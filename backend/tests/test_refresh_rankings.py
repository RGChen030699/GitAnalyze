import json
from collections.abc import Iterator
from datetime import UTC, date, datetime, timedelta
from io import StringIO
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlsplit

import pytest
import responses
from django.core.management import CommandError, call_command
from github_client.client import API_BASE_URL
from repositories.models import Repository, StarWeek
from responses import matchers

NOW = datetime(2026, 11, 23, 12, 0, tzinfo=UTC)
FIXTURES = Path(__file__).parent / "fixtures" / "github"
SEARCH_URL = f"{API_BASE_URL}/search/repositories"
TOP_REPO = "public-apis/public-apis"
REPO_NAMES = (
    TOP_REPO,
    "EbookFoundation/free-programming-books",
    "donnemartin/system-design-primer",
)
DEFAULT_LANGUAGES = ("Python", "TypeScript", "JavaScript")
SECONDS_PER_WEEK = 7 * 24 * 60 * 60


def load(name: str) -> Any:
    return json.loads((FIXTURES / name).read_text())


def history_page_1() -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = load("stargazers_history.json")
    return entries


def history_page_2() -> list[dict[str, Any]]:
    """The recorded page, moved back 30 weeks, because only page 1 was recorded."""
    return [{**entry, "week": entry["week"] - 30 * SECONDS_PER_WEEK} for entry in history_page_1()]


def mock_search(payload: Any = None) -> None:
    responses.get(SEARCH_URL, json=payload or load("search_repositories.json"))


def mock_history_page(full_name: str, page: int, entries: Any, status: int) -> None:
    responses.get(
        f"{API_BASE_URL}/repos/{full_name}/stargazers/history",
        json=entries if status == 200 else {"message": "failed"},
        status=status,
        match=[matchers.query_param_matcher({"per_page": "30", "page": str(page)})],
    )


def mock_details(
    full_name: str,
    releases: Any = None,
    releases_status: int = 200,
    page_1: Any = None,
    page_1_status: int = 200,
    page_2_status: int = 200,
) -> None:
    responses.get(
        f"{API_BASE_URL}/repos/{full_name}/releases",
        json=load("releases.json") if releases is None else releases,
        status=releases_status,
        match=[matchers.query_param_matcher({"per_page": "100"})],
    )
    entries = history_page_1() if page_1 is None else page_1
    mock_history_page(full_name, 1, entries, page_1_status)
    if len(entries) == 30:
        mock_history_page(full_name, 2, history_page_2(), page_2_status)


def mock_all() -> None:
    mock_search()
    for full_name in REPO_NAMES:
        mock_details(full_name)


def run(*args: str) -> tuple[str, str]:
    out, err = StringIO(), StringIO()
    call_command("refresh_rankings", *args, stdout=out, stderr=err)
    return out.getvalue(), err.getvalue()


def request_urls() -> list[str]:
    return [str(call.request.url) for call in responses.calls]


def search_params(name: str) -> list[str]:
    return [parse_qs(urlsplit(url).query)[name][0] for url in request_urls() if "/search/" in url]


def top_repository() -> Repository:
    return Repository.objects.get(full_name=TOP_REPO)


def single_repo_search() -> dict[str, Any]:
    payload: dict[str, Any] = load("search_repositories.json")
    payload["items"] = payload["items"][:1]
    return payload


def dated_days(entries: list[dict[str, Any]]) -> Iterator[tuple[date, int]]:
    for entry in entries:
        week_start = datetime.fromtimestamp(entry["week"], UTC).date()
        for offset, gained in enumerate(entry["days"]):
            yield week_start + timedelta(days=offset), gained


def expected_gain(entries: list[dict[str, Any]], days: int) -> int:
    today = NOW.date()
    first_day = today - timedelta(days=days - 1)
    return sum(gained for day, gained in dated_days(entries) if first_day <= day <= today)


@pytest.fixture(autouse=True)
def command_setup(settings, monkeypatch: pytest.MonkeyPatch) -> None:
    settings.GITHUB_TOKEN = "test-token"
    settings.RANKINGS_LANGUAGES = DEFAULT_LANGUAGES
    monkeypatch.setattr("django.utils.timezone.now", lambda: NOW)


@responses.activate
@pytest.mark.django_db
def test_refresh_uses_configured_languages() -> None:
    mock_all()

    run()

    assert search_params("q") == [
        "stars:>1000",
        "language:Python stars:>1000",
        "language:TypeScript stars:>1000",
        "language:JavaScript stars:>1000",
    ]
    assert search_params("per_page") == ["100", "50", "50", "50"]


@responses.activate
@pytest.mark.django_db
def test_refresh_language_option_replaces_setting() -> None:
    mock_all()

    run("--language", "Go", "--language", "Rust")

    assert search_params("q") == [
        "stars:>1000",
        "language:Go stars:>1000",
        "language:Rust stars:>1000",
    ]


@responses.activate
@pytest.mark.django_db
def test_refresh_language_option_ignores_duplicates() -> None:
    mock_all()

    run("--language", "Go", "--language", " go ")

    assert search_params("q") == ["stars:>1000", "language:Go stars:>1000"]


@responses.activate
@pytest.mark.django_db
def test_refresh_quotes_language_with_space() -> None:
    mock_all()

    run("--language", "Jupyter Notebook")

    assert search_params("q")[1] == 'language:"Jupyter Notebook" stars:>1000'


@responses.activate
@pytest.mark.django_db
def test_refresh_blank_language_is_error() -> None:
    with pytest.raises(CommandError, match="--language"):
        run("--language", " ")

    assert len(responses.calls) == 0


@responses.activate
@pytest.mark.django_db
@pytest.mark.parametrize("limit", ["0", "-1"])
def test_limit_must_be_positive(limit: str) -> None:
    with pytest.raises(CommandError, match="--limit"):
        run("--limit", limit)

    assert len(responses.calls) == 0


@responses.activate
@pytest.mark.django_db
def test_limit_keeps_highest_starred() -> None:
    mock_all()

    out, _ = run("--limit", "1")

    assert list(Repository.objects.values_list("full_name", flat=True)) == [TOP_REPO]
    assert "7 requests" in out


@responses.activate
@pytest.mark.django_db
def test_refresh_stores_source_and_fetched_at() -> None:
    mock_all()

    run()

    repository = top_repository()
    star_week = repository.star_weeks.first()
    assert repository.source.startswith("/search/repositories?q=stars%3A%3E1000")
    assert repository.fetched_at == NOW
    assert repository.ranked_at == NOW
    assert star_week.source == f"/repos/{TOP_REPO}/stargazers/history"
    assert star_week.fetched_at == NOW


@responses.activate
@pytest.mark.django_db
def test_refresh_saves_basic_fields_from_search() -> None:
    mock_all()

    run()

    repository = top_repository()
    assert repository.github_id == 54346799
    assert repository.owner_login == "public-apis"
    assert repository.owner_type == "Organization"
    assert repository.language == "Python"
    assert repository.stargazers_count == 501041
    assert repository.raw["full_name"] == TOP_REPO


@responses.activate
@pytest.mark.django_db
def test_F8_refresh_computes_gains_from_recorded_history() -> None:
    mock_all()

    run()

    repository = top_repository()
    entries = history_page_1() + history_page_2()
    assert repository.stars_gained_7d == expected_gain(entries, 7)
    assert repository.stars_gained_30d == expected_gain(entries, 30)
    assert repository.stars_gained_year == expected_gain(entries, 364)
    assert repository.star_history_fetched_at == NOW


@responses.activate
@pytest.mark.django_db
def test_G3_refresh_stores_12_weeks_oldest_first() -> None:
    mock_all()

    run()

    expected = [entry["total"] for entry in reversed(history_page_1()[:12])]
    assert top_repository().weeks_12 == expected


@responses.activate
@pytest.mark.django_db
def test_refresh_stores_week_start_as_sunday_date() -> None:
    mock_all()

    run()

    newest = top_repository().star_weeks.order_by("-week_start").first()
    assert newest.week_start == date(2026, 11, 22)
    assert newest.days == [22, 17, 0, 0, 0, 0, 0]
    assert top_repository().star_weeks.count() == 60


@responses.activate
@pytest.mark.django_db
def test_refresh_is_idempotent() -> None:
    mock_all()

    run()
    run()

    assert Repository.objects.count() == 3
    assert StarWeek.objects.count() == 180


@responses.activate
@pytest.mark.django_db
def test_C7_rename_updates_same_row() -> None:
    mock_search(single_repo_search())
    mock_details(TOP_REPO)
    run()
    responses.reset()
    renamed = single_repo_search()
    renamed["items"][0]["full_name"] = "public-apis/renamed"
    mock_search(renamed)
    mock_details("public-apis/renamed")

    run()

    assert list(Repository.objects.values_list("full_name", flat=True)) == ["public-apis/renamed"]


@responses.activate
@pytest.mark.django_db
def test_short_history_skips_page_2() -> None:
    mock_search(single_repo_search())
    mock_details(TOP_REPO, page_1=history_page_1()[:5])

    run()

    assert not [url for url in request_urls() if "history" in url and "page=2" in url]
    assert top_repository().stars_gained_year == expected_gain(history_page_1()[:5], 364)


@responses.activate
@pytest.mark.django_db
def test_history_page_2_failure_keeps_week_and_month() -> None:
    mock_search(single_repo_search())
    mock_details(TOP_REPO, page_2_status=500)

    out, err = run()

    repository = top_repository()
    assert repository.stars_gained_year is None
    assert repository.stars_gained_7d == expected_gain(history_page_1(), 7)
    assert repository.stars_gained_30d == expected_gain(history_page_1(), 30)
    assert len(repository.weeks_12) == 12
    assert "1 failures" in out
    assert "star history" in err


@responses.activate
@pytest.mark.django_db
def test_history_page_2_failure_keeps_previous_year() -> None:
    mock_search(single_repo_search())
    mock_details(TOP_REPO)
    run()
    previous_year = top_repository().stars_gained_year
    responses.reset()
    mock_search(single_repo_search())
    mock_details(TOP_REPO, page_2_status=500)

    run()

    assert previous_year is not None
    assert top_repository().stars_gained_year == previous_year


@responses.activate
@pytest.mark.django_db
def test_history_failure_keeps_previous_values() -> None:
    mock_search(single_repo_search())
    mock_details(TOP_REPO)
    run()
    before = top_repository()
    responses.reset()
    mock_search(single_repo_search())
    mock_details(TOP_REPO, page_1_status=500)

    out, _ = run()

    after = top_repository()
    assert after.stars_gained_7d == before.stars_gained_7d
    assert after.stars_gained_30d == before.stars_gained_30d
    assert after.stars_gained_year == before.stars_gained_year
    assert after.weeks_12 == before.weeks_12
    assert after.star_weeks.count() == 60
    assert "1 failures" in out


@responses.activate
@pytest.mark.django_db
def test_first_history_failure_leaves_gains_null() -> None:
    mock_search(single_repo_search())
    mock_details(TOP_REPO, page_1_status=500)

    run()

    repository = top_repository()
    assert repository.stars_gained_7d is None
    assert repository.stars_gained_30d is None
    assert repository.stars_gained_year is None
    assert repository.weeks_12 is None
    assert repository.star_history_fetched_at is None


@responses.activate
@pytest.mark.django_db
def test_history_disabled_leaves_gains_null(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("repositories.ingest.STAR_HISTORY_ENABLED", False)
    mock_search(single_repo_search())
    responses.get(f"{API_BASE_URL}/repos/{TOP_REPO}/releases", json=load("releases.json"))

    out, _ = run()

    assert top_repository().stars_gained_7d is None
    assert not [url for url in request_urls() if "history" in url]
    assert "0 failures" in out


@responses.activate
@pytest.mark.django_db
def test_S2_recorded_release_sets_status() -> None:
    mock_search(single_repo_search())
    mock_details(TOP_REPO)

    run()

    repository = top_repository()
    assert repository.newest_release_at == datetime(2026, 2, 19, 5, 1, 30, tzinfo=UTC)
    assert repository.status == "Slowing"


@responses.activate
@pytest.mark.django_db
def test_S2_draft_release_is_ignored() -> None:
    releases = load("releases.json")
    releases[0] = {**releases[0], "draft": True, "published_at": "2026-11-20T00:00:00Z"}
    mock_search(single_repo_search())
    mock_details(TOP_REPO, releases=releases)

    run()

    repository = top_repository()
    assert repository.newest_release_at == datetime(2025, 8, 19, 21, 3, 31, tzinfo=UTC)
    assert repository.status == "Slowing"


@responses.activate
@pytest.mark.django_db
def test_S3_no_releases_ever_is_active() -> None:
    mock_search(single_repo_search())
    mock_details(TOP_REPO, releases=[])

    run()

    assert top_repository().newest_release_at is None
    assert top_repository().status == "Active"


@responses.activate
@pytest.mark.django_db
def test_release_failure_gives_null_status() -> None:
    mock_search(single_repo_search())
    mock_details(TOP_REPO, releases_status=500)

    out, err = run()

    repository = top_repository()
    assert repository.status is None
    assert repository.ranked_at == NOW
    assert "1 failures" in out
    assert "releases" in err


@responses.activate
@pytest.mark.django_db
def test_one_repo_failure_does_not_stop_run() -> None:
    mock_search()
    mock_details(REPO_NAMES[0])
    mock_details(REPO_NAMES[1], releases_status=500, page_1_status=500)
    mock_details(REPO_NAMES[2])

    out, _ = run()

    assert Repository.objects.count() == 3
    assert Repository.objects.get(full_name=REPO_NAMES[2]).stars_gained_7d is not None
    assert "1 failures" in out


@responses.activate
@pytest.mark.django_db
def test_malformed_repo_does_not_stop_run() -> None:
    payload = load("search_repositories.json")
    del payload["items"][0]["owner"]
    mock_search(payload)
    mock_details(REPO_NAMES[1])
    mock_details(REPO_NAMES[2])

    out, err = run()

    assert Repository.objects.count() == 2
    assert "Refreshed 2 repositories" in out
    assert "1 failures" in out
    assert TOP_REPO in err


@responses.activate
@pytest.mark.django_db
def test_name_collision_counts_as_failure() -> None:
    mock_search(single_repo_search())
    mock_details(TOP_REPO)
    run()
    responses.reset()
    reused_name = single_repo_search()
    reused_name["items"][0]["id"] = 999
    reused_name["items"][0]["full_name"] = TOP_REPO.upper()
    mock_search(reused_name)

    out, _ = run()

    assert Repository.objects.count() == 1
    assert top_repository().github_id == 54346799
    assert "1 failures" in out


@responses.activate
@pytest.mark.django_db
def test_search_failure_aborts_without_changes() -> None:
    responses.get(
        SEARCH_URL,
        json=load("search_repositories.json"),
        match=[matchers.query_param_matcher({"per_page": "100"}, strict_match=False)],
    )
    responses.get(
        SEARCH_URL,
        status=500,
        json={"message": "failed"},
        match=[matchers.query_param_matcher({"per_page": "50"}, strict_match=False)],
    )

    with pytest.raises(CommandError, match="Search failed"):
        run()

    assert Repository.objects.count() == 0
    assert not [url for url in request_urls() if "/repos/" in url]


@responses.activate
@pytest.mark.django_db
def test_C1_missing_token_is_command_error(settings) -> None:
    settings.GITHUB_TOKEN = ""

    with pytest.raises(CommandError, match="GITHUB_TOKEN is not set"):
        run()

    assert len(responses.calls) == 0


@responses.activate
@pytest.mark.django_db
def test_summary_reports_repos_requests_failures() -> None:
    mock_all()

    out, err = run()

    assert "Refreshed 3 repositories, 13 requests used, 0 failures" in out
    assert err == ""


def low_total_search() -> dict[str, Any]:
    payload = single_repo_search()
    payload["items"][0]["stargazers_count"] = 10
    return payload


@responses.activate
@pytest.mark.django_db
def test_F8_new_gains_never_exceed_total_stars() -> None:
    mock_search(low_total_search())
    mock_details(TOP_REPO)

    run()

    repository = top_repository()
    assert repository.stars_gained_7d == 10
    assert repository.stars_gained_30d == 10
    assert repository.stars_gained_year == 10
    assert repository.weeks_12 == [entry["total"] for entry in reversed(history_page_1()[:12])]


@responses.activate
@pytest.mark.django_db
def test_F8_kept_gains_never_exceed_lower_total_after_history_failure() -> None:
    mock_search(single_repo_search())
    mock_details(TOP_REPO)
    run()
    responses.reset()
    mock_search(low_total_search())
    mock_details(TOP_REPO, page_1_status=500)

    run()

    repository = top_repository()
    assert repository.stars_gained_7d == 10
    assert repository.stars_gained_30d == 10
    assert repository.stars_gained_year == 10
