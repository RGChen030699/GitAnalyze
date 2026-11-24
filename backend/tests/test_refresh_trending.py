"""refresh_trending: add Trending repositories and store their weekly ranks (F0 W3, F8 G4)."""

from datetime import UTC, datetime, timedelta
from io import StringIO
from itertools import count
from typing import Any

import pytest
import requests
import responses
from django.core.management import call_command
from github_client.client import API_BASE_URL
from github_client.trending import FEED_BASE_URL
from repositories.models import Repository

from tests.test_refresh_rankings import load, mock_details

NOW = datetime(2026, 11, 24, 12, 0, tzinfo=UTC)
DOWN = "down"
_ids = count(10_000)


@pytest.fixture(autouse=True)
def command_setup(settings: Any, monkeypatch: pytest.MonkeyPatch) -> None:
    settings.GITHUB_TOKEN = "test-token"
    settings.RANKINGS_LANGUAGES = ("Python",)
    monkeypatch.setattr("django.utils.timezone.now", lambda: NOW)


def feed_body(names: list[str]) -> str:
    items = "".join(
        f"<item><title>{n}</title><link>https://github.com/{n}</link></item>" for n in names
    )
    return f'<?xml version="1.0"?><rss version="2.0"><channel>{items}</channel></rss>'


def mock_feed(path: str, names: list[str] | str) -> None:
    url = f"{FEED_BASE_URL}/{path}.xml"
    if names == DOWN:
        responses.get(url, body=requests.ConnectionError("feed down"))
    else:
        assert isinstance(names, list)
        responses.get(url, body=feed_body(names))


Feed = list[str] | str | None


def mock_feeds(
    weekly: Feed = None,
    python: Feed = None,
    daily: Feed = None,
    monthly: Feed = None,
    daily_python: Feed = None,
    monthly_python: Feed = None,
) -> None:
    """Each feed lists names, is DOWN, or (None) answers with no items."""
    mock_feed("weekly/all", weekly or [])
    mock_feed("weekly/python", python or [])
    mock_feed("daily/all", daily or [])
    mock_feed("monthly/all", monthly or [])
    mock_feed("daily/python", daily_python or [])
    mock_feed("monthly/python", monthly_python or [])


def mock_new_repo(full_name: str) -> None:
    owner, name = full_name.split("/")
    payload = {
        **load("repo.json"),
        "id": next(_ids),
        "full_name": full_name,
        "name": name,
        "owner": {**load("repo.json")["owner"], "login": owner},
    }
    responses.get(f"{API_BASE_URL}/repos/{full_name}", json=payload)
    mock_details(full_name)


def make_repo(full_name: str, **overrides: Any) -> Repository:
    fields: dict[str, Any] = {
        "github_id": next(_ids),
        "full_name": full_name,
        "owner_login": full_name.split("/")[0],
        "owner_type": "Organization",
        "archived": False,
        "stargazers_count": 100,
        "forks_count": 1,
        "open_issues_count": 1,
        "source": f"/repos/{full_name}",
        "fetched_at": NOW - timedelta(hours=2),
        "ranked_at": NOW - timedelta(hours=2),
        "raw": {},
    }
    return Repository.objects.create(**{**fields, **overrides})


def run() -> tuple[str, str]:
    out, err = StringIO(), StringIO()
    call_command("refresh_trending", stdout=out, stderr=err)
    return out.getvalue(), err.getvalue()


def trending(full_name: str) -> Any:
    return Repository.objects.get(full_name=full_name).trending


def github_calls() -> list[str]:
    urls = [str(call.request.url) for call in responses.calls]
    return [url for url in urls if url.startswith(API_BASE_URL)]


@responses.activate
@pytest.mark.django_db
def test_W3_new_trending_repo_is_added_ranked_with_star_history() -> None:
    mock_feeds(weekly=["new/repo"])
    mock_new_repo("new/repo")

    run()

    repo = Repository.objects.get(full_name="new/repo")
    assert repo.ranked_at == NOW
    assert repo.star_weeks.count() > 0
    assert repo.stars_gained_7d is not None
    assert repo.trending == {"weekly:all": 1}
    assert repo.trending_at == NOW


@responses.activate
@pytest.mark.django_db
def test_G4_weekly_ranks_follow_feed_order_per_language() -> None:
    make_repo("a/one")
    make_repo("b/two")
    mock_feeds(weekly=["a/one", "b/two"], python=["b/two"])

    run()

    assert trending("a/one") == {"weekly:all": 1}
    assert trending("b/two") == {"weekly:all": 2, "weekly:Python": 1}


@responses.activate
@pytest.mark.django_db
def test_W3_repo_refreshed_in_the_last_20_hours_is_not_fetched_again() -> None:
    make_repo("a/one", ranked_at=NOW - timedelta(hours=19))
    mock_feeds(weekly=["a/one"])

    run()

    assert github_calls() == []


@responses.activate
@pytest.mark.django_db
def test_W3_repo_not_refreshed_today_is_refreshed_and_ranked() -> None:
    make_repo("old/one", github_id=77, ranked_at=None, fetched_at=NOW - timedelta(days=3))
    mock_feeds(weekly=["old/one"])
    payload = {**load("repo.json"), "id": 77, "full_name": "old/one"}
    responses.get(f"{API_BASE_URL}/repos/old/one", json=payload)
    mock_details("old/one")

    run()

    assert Repository.objects.filter(ranked_at=NOW).count() == 1


@responses.activate
@pytest.mark.django_db
def test_G4_daily_and_monthly_lists_are_ranked_too() -> None:
    mock_feeds(daily=["d/one"], monthly=["m/one", "d/one"], monthly_python=["m/one"])
    mock_new_repo("d/one")
    mock_new_repo("m/one")

    run()

    assert trending("d/one") == {"daily:all": 1, "monthly:all": 2}
    assert trending("m/one") == {"monthly:all": 1, "monthly:Python": 1}
    assert Repository.objects.filter(ranked_at=NOW).count() == 2


@responses.activate
@pytest.mark.django_db
def test_G4_repo_dropped_from_the_feeds_loses_its_rank() -> None:
    make_repo(
        "c/old",
        trending={"weekly:all": 1, "weekly:Python": 3},
        trending_at=NOW - timedelta(days=1),
    )
    make_repo("a/one")
    mock_feeds(weekly=["a/one"], python=[])

    run()

    assert trending("c/old") is None
    assert trending("a/one") == {"weekly:all": 1}


@responses.activate
@pytest.mark.django_db
def test_G4_unreachable_feed_keeps_yesterdays_ranks_and_the_job_succeeds() -> None:
    yesterday = NOW - timedelta(days=1)
    make_repo("c/old", trending={"weekly:all": 1, "weekly:Python": 2}, trending_at=yesterday)
    mock_feeds(weekly=DOWN, python=[])

    out, err = run()

    repo = Repository.objects.get(full_name="c/old")
    assert repo.trending == {"weekly:all": 1}  # weekly Python answered empty; weekly all was down
    assert repo.trending_at == yesterday
    assert f"Trending feed unreachable: {FEED_BASE_URL}/weekly/all.xml" in err
    assert "1 feeds unreachable" in out


@responses.activate
@pytest.mark.django_db
def test_W3_listed_repo_github_cannot_find_is_skipped() -> None:
    mock_feeds(weekly=["gone/repo", "a/one"])
    make_repo("a/one")
    responses.get(f"{API_BASE_URL}/repos/gone/repo", json={"message": "Not Found"}, status=404)

    out, err = run()

    assert not Repository.objects.filter(full_name="gone/repo").exists()
    assert "gone/repo" in err
    assert trending("a/one") == {"weekly:all": 2}  # GitHub's order is kept, gaps included


@responses.activate
@pytest.mark.django_db
def test_W3_summary_reports_feeds_added_repositories_and_requests() -> None:
    mock_feeds(weekly=["new/repo"], daily=["new/repo"])
    mock_new_repo("new/repo")

    out, err = run()

    assert "Trending: 1 repositories from 6 feeds, 1 added or refreshed" in out
    assert "0 feeds unreachable" in out
    assert err == ""


def test_G4_stored_weekly_ranks_move_to_period_keys() -> None:
    from repositories.trending import with_period_keys

    assert with_period_keys({"all": 1, "Python": 2}) == {"weekly:all": 1, "weekly:Python": 2}
    assert with_period_keys({"weekly:all": 1, "daily:all": 3}) == {"weekly:all": 1, "daily:all": 3}
    assert with_period_keys(None) is None
