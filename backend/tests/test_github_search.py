import json
from datetime import UTC, datetime
from pathlib import Path

import pytest
import responses
from github_client import GitHubClient, search_repositories
from github_client.client import API_BASE_URL
from responses import matchers

FIXED_NOW = datetime(2026, 11, 23, 12, 0, tzinfo=UTC)
SEARCH_URL = f"{API_BASE_URL}/search/repositories"
QUERY = "language:Python stars:>1000"
FIXTURE = Path(__file__).parent / "fixtures" / "github" / "search_repositories.json"


@pytest.fixture(autouse=True)
def github_token(settings) -> None:
    settings.GITHUB_TOKEN = "test-token"


@pytest.fixture
def client() -> GitHubClient:
    return GitHubClient(clock=lambda: FIXED_NOW)


@responses.activate
def test_W1_search_sends_query_sorted_by_stars(client: GitHubClient) -> None:
    expected = {"q": QUERY, "sort": "stars", "order": "desc", "per_page": "3"}
    responses.get(
        SEARCH_URL,
        json={"items": []},
        match=[matchers.query_param_matcher(expected)],
    )

    search_repositories(client, QUERY, per_page=3)

    assert len(responses.calls) == 1


@responses.activate
def test_C8_search_source_includes_query(client: GitHubClient) -> None:
    responses.get(SEARCH_URL, json={"items": []})

    result = search_repositories(client, QUERY, per_page=3)

    assert result.source == (
        "/search/repositories?q=language%3APython+stars%3A%3E1000&sort=stars&order=desc&per_page=3"
    )
    assert result.fetched_at == FIXED_NOW
    assert result.cost == 1


@responses.activate
@pytest.mark.parametrize("per_page", [0, 101])
def test_W1_search_rejects_per_page_out_of_range(client: GitHubClient, per_page: int) -> None:
    with pytest.raises(ValueError, match="per_page"):
        search_repositories(client, QUERY, per_page=per_page)

    assert len(responses.calls) == 0


@responses.activate
@pytest.mark.parametrize("per_page", [1, 100])
def test_W1_search_accepts_per_page_limits(client: GitHubClient, per_page: int) -> None:
    responses.get(SEARCH_URL, json={"items": []})

    assert search_repositories(client, QUERY, per_page=per_page).status == "ok"


@responses.activate
def test_W1_search_parses_recorded_fixture(client: GitHubClient) -> None:
    responses.get(SEARCH_URL, json=json.loads(FIXTURE.read_text()))

    first = search_repositories(client, QUERY, per_page=3).data["items"][0]

    assert first["full_name"] == "public-apis/public-apis"
    assert first["stargazers_count"] == 501041
