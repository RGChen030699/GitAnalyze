import re
from datetime import UTC, datetime
from pathlib import Path

import pytest
import responses
from github_client import (
    ForbiddenEndpointError,
    GitHubClient,
    GitHubError,
    MissingTokenError,
    RateLimitError,
)
from github_client.client import API_BASE_URL, API_VERSION, RAW_BASE_URL

FIXED_NOW = datetime(2026, 11, 22, 12, 0, tzinfo=UTC)
REPO_PATH = "/repos/octo/widget"
REPO_URL = f"{API_BASE_URL}{REPO_PATH}"


@pytest.fixture(autouse=True)
def github_token(settings) -> None:
    settings.GITHUB_TOKEN = "test-token"


@pytest.fixture
def client() -> GitHubClient:
    return GitHubClient(clock=lambda: FIXED_NOW)


@responses.activate
def test_missing_token_fails_without_request(settings, client: GitHubClient) -> None:
    settings.GITHUB_TOKEN = ""
    with pytest.raises(MissingTokenError, match="^GITHUB_TOKEN is not set$"):
        client.get(REPO_PATH)
    assert len(responses.calls) == 0


@responses.activate
def test_sends_required_headers(client: GitHubClient) -> None:
    responses.get(REPO_URL, json={"full_name": "octo/widget"})
    client.get(REPO_PATH)
    headers = responses.calls[0].request.headers
    assert headers["Accept"] == "application/vnd.github+json"
    assert headers["X-GitHub-Api-Version"] == API_VERSION
    assert headers["Authorization"] == "Bearer test-token"


@responses.activate
def test_returns_data_with_provenance(client: GitHubClient) -> None:
    responses.get(REPO_URL, json={"full_name": "octo/widget"})
    result = client.get(REPO_PATH)
    assert result.data == {"full_name": "octo/widget"}
    assert result.source == REPO_PATH
    assert result.fetched_at == FIXED_NOW
    assert result.cost == 1
    assert result.status == "ok"


@responses.activate
def test_follows_rename_redirect(client: GitHubClient) -> None:
    new_url = f"{API_BASE_URL}/repositories/42"
    responses.get(REPO_URL, status=301, headers={"Location": new_url})
    responses.get(new_url, json={"full_name": "octo/renamed"})
    result = client.get(REPO_PATH)
    assert result.data["full_name"] == "octo/renamed"
    assert result.final_url == new_url
    assert result.cost == 2


@responses.activate
def test_error_status_raises(client: GitHubClient) -> None:
    responses.get(REPO_URL, status=404, json={"message": "Not Found"})
    with pytest.raises(GitHubError) as excinfo:
        client.get(REPO_PATH)
    assert excinfo.value.status_code == 404


@responses.activate
@pytest.mark.parametrize(
    "path",
    [
        "/repos/octo/widget/stargazers",
        "/repos/octo/widget/stargazers/",
        "/repos/octo/widget/stargazers?per_page=100",
        "/repos/octo/widget/STARGAZERS",
        "/repos/octo/widget/%73targazers",
    ],
)
def test_stargazer_list_is_forbidden(client: GitHubClient, path: str) -> None:
    with pytest.raises(ForbiddenEndpointError):
        client.get(path)
    assert len(responses.calls) == 0


@responses.activate
@pytest.mark.parametrize("suffix", ["history", "count"])
def test_stargazer_history_and_count_are_allowed(client: GitHubClient, suffix: str) -> None:
    path = f"{REPO_PATH}/stargazers/{suffix}"
    responses.get(f"{API_BASE_URL}{path}", json={})
    assert client.get(path).status == "ok"


@pytest.mark.parametrize("path", ["https://evil.example/x", "//evil.example/x", "repos/a/b"])
def test_rejects_non_api_paths(client: GitHubClient, path: str) -> None:
    with pytest.raises(GitHubError):
        client.get(path)


@pytest.fixture
def sleeps() -> list[float]:
    return []


@pytest.fixture
def timed_client(sleeps: list[float]) -> GitHubClient:
    return GitHubClient(clock=lambda: FIXED_NOW, sleep=sleeps.append)


@responses.activate
def test_low_quota_waits_until_reset(timed_client: GitHubClient, sleeps: list[float]) -> None:
    reset_at = int(FIXED_NOW.timestamp()) + 100
    quota = {"x-ratelimit-remaining": "150", "x-ratelimit-reset": str(reset_at)}
    responses.get(REPO_URL, json={}, headers=quota)
    responses.get(REPO_URL, json={})
    timed_client.get(REPO_PATH)
    assert sleeps == []
    timed_client.get(REPO_PATH)
    assert sleeps == [101]


@responses.activate
def test_healthy_quota_does_not_wait(timed_client: GitHubClient, sleeps: list[float]) -> None:
    reset_at = int(FIXED_NOW.timestamp()) + 100
    quota = {"x-ratelimit-remaining": "200", "x-ratelimit-reset": str(reset_at)}
    responses.get(REPO_URL, json={}, headers=quota)
    timed_client.get(REPO_PATH)
    timed_client.get(REPO_PATH)
    assert sleeps == []


@responses.activate
def test_403_with_retry_after_waits(timed_client: GitHubClient, sleeps: list[float]) -> None:
    responses.get(REPO_URL, status=403, headers={"retry-after": "30"})
    responses.get(REPO_URL, json={"ok": True})
    result = timed_client.get(REPO_PATH)
    assert result.data == {"ok": True}
    assert result.cost == 2
    assert sleeps == [30]


@responses.activate
def test_rate_limit_backs_off_then_gives_up(
    timed_client: GitHubClient, sleeps: list[float], caplog: pytest.LogCaptureFixture
) -> None:
    responses.get(REPO_URL, status=429)
    with pytest.raises(RateLimitError):
        timed_client.get(REPO_PATH)
    assert len(responses.calls) == 5
    assert sleeps == [60, 120, 240, 480]
    assert "giving up" in caplog.text


@responses.activate
def test_exhausted_quota_403_waits_once_for_reset(
    timed_client: GitHubClient, sleeps: list[float]
) -> None:
    reset_at = int(FIXED_NOW.timestamp()) + 100
    quota = {"x-ratelimit-remaining": "0", "x-ratelimit-reset": str(reset_at)}
    responses.get(REPO_URL, status=403, headers=quota, json={"message": "API rate limit exceeded"})
    responses.get(REPO_URL, json={"ok": True})
    assert timed_client.get(REPO_PATH).data == {"ok": True}
    assert sleeps == [101]


@responses.activate
def test_plain_403_fails_fast(timed_client: GitHubClient, sleeps: list[float]) -> None:
    responses.get(REPO_URL, status=403, json={"message": "Resource not accessible"})
    with pytest.raises(GitHubError) as excinfo:
        timed_client.get(REPO_PATH)
    assert not isinstance(excinfo.value, RateLimitError)
    assert len(responses.calls) == 1
    assert sleeps == []


@responses.activate
def test_stats_202_becomes_pending(timed_client: GitHubClient, sleeps: list[float]) -> None:
    path = f"{REPO_PATH}/stats/commit_activity"
    responses.get(f"{API_BASE_URL}{path}", status=202)
    result = timed_client.get(path)
    assert result.status == "pending"
    assert result.data is None
    assert len(responses.calls) == 6
    assert sleeps == [2, 4, 8, 16, 32]


@responses.activate
def test_stats_202_then_ready(timed_client: GitHubClient, sleeps: list[float]) -> None:
    path = f"{REPO_PATH}/stats/commit_activity"
    responses.get(f"{API_BASE_URL}{path}", status=202)
    responses.get(f"{API_BASE_URL}{path}", json=[{"total": 3}])
    result = timed_client.get(path)
    assert result.status == "ok"
    assert result.data == [{"total": 3}]
    assert sleeps == [2]


@responses.activate
def test_304_reuses_stored_data_at_no_cost(client: GitHubClient) -> None:
    responses.get(REPO_URL, json={"stars": 5}, headers={"ETag": '"abc"'})
    responses.get(REPO_URL, status=304)
    first = client.get(REPO_PATH)
    second = client.get(REPO_PATH)
    assert "If-None-Match" not in responses.calls[0].request.headers
    assert responses.calls[1].request.headers["If-None-Match"] == '"abc"'
    assert first.from_cache is False
    assert second.from_cache is True
    assert second.data == {"stars": 5}
    assert second.cost == 0


@responses.activate
def test_etags_are_separate_per_query(client: GitHubClient) -> None:
    responses.get(REPO_URL, json=[1], headers={"ETag": '"page1"'})
    client.get(REPO_PATH, params={"page": 1})
    client.get(REPO_PATH, params={"page": 2})
    assert "If-None-Match" not in responses.calls[1].request.headers


@responses.activate
def test_raw_fetch_sends_no_token_and_costs_nothing(client: GitHubClient) -> None:
    url = f"{RAW_BASE_URL}/octo/widget/feature/x/docs/my%20file.md"
    responses.get(url, body="# Hello")
    result = client.get_raw("octo", "widget", "feature/x", "docs/my file.md")
    assert result.data == "# Hello"
    assert result.cost == 0
    assert result.source == url
    assert "Authorization" not in responses.calls[0].request.headers


@responses.activate
def test_raw_fetch_works_without_token(settings, client: GitHubClient) -> None:
    settings.GITHUB_TOKEN = ""
    responses.get(f"{RAW_BASE_URL}/octo/widget/main/README.md", body="ok")
    assert client.get_raw("octo", "widget", "main", "README.md").data == "ok"


@pytest.mark.parametrize("path", ["../other/file", "a/./b", "a//b", ""])
def test_raw_fetch_rejects_unsafe_paths(client: GitHubClient, path: str) -> None:
    with pytest.raises(GitHubError):
        client.get_raw("octo", "widget", "main", path)


def test_real_network_is_blocked_in_tests(client: GitHubClient) -> None:
    with pytest.raises(RuntimeError, match="Real network access"):
        client.get(REPO_PATH)


def _production_sources() -> list[Path]:
    backend = Path(__file__).resolve().parent.parent
    return [p for p in backend.rglob("*.py") if "tests" not in p.relative_to(backend).parts]


def test_no_code_calls_the_stargazer_list() -> None:
    pattern = re.compile(r"/stargazers(?!/(?:history|count)\b)", re.IGNORECASE)
    offenders = [str(p) for p in _production_sources() if pattern.search(p.read_text())]
    assert offenders == []


def test_only_the_client_names_github_hosts() -> None:
    pattern = re.compile(r"(?:api\.github\.com|raw\.githubusercontent\.com)")
    offenders = [
        str(p)
        for p in _production_sources()
        if "github_client" not in p.parts and pattern.search(p.read_text())
    ]
    assert offenders == []
