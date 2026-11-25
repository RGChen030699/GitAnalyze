"""F2 health data fetched when a report opens, cached 24 hours, and served with provenance."""

import base64
from datetime import UTC, datetime, timedelta
from typing import Any

import pytest
import responses
from django.test import Client
from github_client import GitHubClient
from github_client.client import API_BASE_URL
from repositories.ingest import refresh_details
from repositories.models import Repository

from tests.test_refresh_rankings import load, mock_details

NOW = datetime(2026, 11, 23, 12, 0, tzinfo=UTC)
FULL_NAME = "pallets/flask"
BASE = f"{API_BASE_URL}/repos/{FULL_NAME}"
DETAIL_URL = f"/api/repos/{FULL_NAME}"
WEEK = 7 * 86_400
CONTRIBUTORS_PAGE = f"{API_BASE_URL}/repositories/596892/contributors?per_page=1&anon=1"
LINK_LAST_412 = f'<{CONTRIBUTORS_PAGE}&page=412>; rel="last"'
STAMP = "%Y-%m-%dT%H:%M:%SZ"


@pytest.fixture(autouse=True)
def frozen_now(monkeypatch: pytest.MonkeyPatch, settings: Any) -> None:
    settings.GITHUB_TOKEN = "test-token"
    monkeypatch.setattr("django.utils.timezone.now", lambda: NOW)


def week_ts(weeks_ago: int) -> int:
    return int((NOW - timedelta(weeks=weeks_ago)).timestamp())


def commit_weeks(recent: int = 4, earlier: int = 2) -> list[dict[str, Any]]:
    """52 weeks oldest first: `earlier` commits a week, then `recent` a week for the last 13."""
    weeks = []
    for age in range(51, -1, -1):
        total = recent if age < 13 else earlier
        weeks.append({"week": week_ts(age), "total": total, "days": [0, total, 0, 0, 0, 0, 0]})
    return weeks


def stats_contributors(shares: dict[str, int]) -> list[dict[str, Any]]:
    return [
        {"author": {"login": login}, "total": c, "weeks": [{"w": week_ts(3), "c": c}]}
        for login, c in shares.items()
    ]


def releases_payload() -> list[dict[str, Any]]:
    """Four releases 30 days apart, the newest 10 days ago."""
    return [
        {
            "tag_name": f"v1.{n}",
            "published_at": (NOW - timedelta(days=10 + 30 * (3 - n))).strftime(STAMP),
            "draft": False,
            "prerelease": False,
        }
        for n in (3, 2, 1, 0)
    ]


def make_repo(**overrides: Any) -> Repository:
    fields: dict[str, Any] = {
        "github_id": 596892,
        "full_name": FULL_NAME,
        "owner_login": "pallets",
        "owner_type": "Organization",
        "archived": False,
        "stargazers_count": 100,
        "forks_count": 10,
        "open_issues_count": 5,
        "source": f"/repos/{FULL_NAME}",
        "fetched_at": NOW - timedelta(hours=2),
        "raw": load("repo.json"),
        "releases": releases_payload(),
        "ai_fetched_at": NOW - timedelta(hours=2),  # F4 scan is fresh; these tests are about F2
    }
    return Repository.objects.create(**{**fields, **overrides})


def mock_health(
    activity: Any = None,
    activity_status: int = 200,
    contributors: Any = None,
    contributors_count_status: int = 200,
    readme_status: int = 200,
) -> None:
    responses.get(
        f"{BASE}/stats/commit_activity",
        json=commit_weeks() if activity is None else activity,
        status=activity_status,
    )
    responses.get(
        f"{BASE}/stats/contributors",
        json=stats_contributors({"alice": 90, "bob": 10}) if contributors is None else contributors,
    )
    responses.get(
        f"{BASE}/contributors",
        json=[{"login": "alice"}],
        headers={"Link": LINK_LAST_412},
        status=contributors_count_status,
    )
    responses.get(f"{BASE}/tags", json=[{"name": "v0.9.0"}, {"name": "v0.10.0"}])
    mock_readme(readme_status)


def urls() -> list[str]:
    return [str(call.request.url).split("?")[0] for call in responses.calls]


@responses.activate
@pytest.mark.django_db
def test_F2_refresh_details_stores_the_release_list() -> None:
    repo = make_repo(releases=None)
    mock_details(FULL_NAME)

    refresh_details(GitHubClient(clock=lambda: NOW), repo, NOW)

    repo.refresh_from_db()
    assert [r["tag_name"] for r in repo.releases] == ["3.1.3", "3.1.2", "3.1.1"]


@responses.activate
@pytest.mark.django_db
def test_F2_report_open_fetches_health_once_then_serves_cache(client: Client) -> None:
    make_repo()
    mock_health()

    body = client.get(DETAIL_URL).json()

    assert sorted(urls()) == sorted(
        [
            f"{BASE}/stats/commit_activity",
            f"{BASE}/stats/contributors",
            f"{BASE}/contributors",
            f"{BASE}/readme",  # the report's overview: what the repository is about
        ]
    )
    assert body["commit_activity"]["status"] == "ok"
    assert len(body["commit_activity"]["weeks"]) == 52
    assert body["contributors"] == 412
    assert body["single_maintainer"] == "alice"
    assert body["top_contributors"] == [
        {"login": "alice", "commits": 90},
        {"login": "bob", "commits": 10},
    ]
    assert body["contributors_last_year"] == 2
    assert body["commits_last_year"] == 100
    assert body["people_for_80"] == 1
    assert Repository.objects.get().health_fetched_at == NOW

    responses.calls.reset()
    client.get(DETAIL_URL)
    assert len(responses.calls) == 0


@responses.activate
@pytest.mark.django_db
def test_F2_health_older_than_24_hours_is_refetched(client: Client) -> None:
    make_repo(health={}, health_fetched_at=NOW - timedelta(hours=24))
    mock_health()

    client.get(DETAIL_URL)

    assert f"{BASE}/stats/commit_activity" in urls()


@responses.activate
@pytest.mark.django_db
def test_F2_C1_pending_stats_show_message_and_retry_on_next_open(client: Client) -> None:
    make_repo()
    mock_health(activity_status=202)

    body = client.get(DETAIL_URL).json()

    assert body["commit_activity"] == {
        "status": "pending",
        "weeks": [],
        "note": "GitHub is still calculating this, check back in a minute",
    }
    assert body["contributors"] == 412
    assert body["stars"] == 100
    assert Repository.objects.get().health_fetched_at is None
    assert urls().count(f"{BASE}/stats/commit_activity") == 1  # no waiting inside a web request


@responses.activate
@pytest.mark.django_db
def test_F2_one_failed_part_keeps_the_page_working(client: Client) -> None:
    make_repo()
    mock_health(contributors_count_status=500)

    response = client.get(DETAIL_URL)

    assert response.status_code == 200
    body = response.json()
    assert body["contributors"] is None
    assert body["provenance"]["contributors"] is None
    assert body["commit_activity"]["status"] == "ok"


@responses.activate
@pytest.mark.django_db
def test_F2_V2_tags_are_fetched_only_when_there_are_no_releases(client: Client) -> None:
    make_repo(releases=[])
    mock_health()

    body = client.get(DETAIL_URL).json()

    assert f"{BASE}/tags" in urls()
    assert body["last_release"] == {
        "tag": "v0.10.0",
        "published_at": None,
        "kind": "tag",
        "prerelease": False,
        "note": "tag, not a formal release",
    }
    assert body["releases_12m"] == 0


@responses.activate
@pytest.mark.django_db
def test_F2_V1_V4_last_release_and_count_from_stored_releases(client: Client) -> None:
    make_repo()
    mock_health()

    body = client.get(DETAIL_URL).json()

    assert f"{BASE}/tags" not in urls()
    assert body["last_release"]["tag"] == "v1.3"
    assert body["releases_12m"] == 4
    assert [r["tag"] for r in body["releases"]] == ["v1.0", "v1.1", "v1.2", "v1.3"]
    assert body["releases"][0] == {
        "tag": "v1.0",
        "published_at": "2026-08-15T12:00:00Z",
        "prerelease": False,
    }


@responses.activate
@pytest.mark.django_db
def test_F2_license_and_created_come_from_the_repository_payload(client: Client) -> None:
    make_repo()
    mock_health()

    body = client.get(DETAIL_URL).json()

    bsd = "BSD-3-Clause"
    assert body["license"] == {"spdx_id": bsd, "display": bsd, "warning": None}
    assert body["created_at"] == "2010-04-06T11:11:59Z"
    assert body["provenance"]["license"]["source"] == f"/repos/{FULL_NAME}"


@responses.activate
@pytest.mark.django_db
def test_F2_L1_no_license_in_payload_warns(client: Client) -> None:
    make_repo(raw={**load("repo.json"), "license": None})
    mock_health()

    body = client.get(DETAIL_URL).json()

    assert body["license"]["display"] == "No license"
    assert body["license"]["warning"] == "No license: others may not legally reuse this code."


@responses.activate
@pytest.mark.django_db
def test_F2_brief_answers_use_health_data(client: Client) -> None:
    make_repo()
    mock_health()

    brief = client.get(DETAIL_URL).json()["brief"]

    assert brief["maintenance"] == {"tone": "good", "value": "Speeding up"}  # 52 against 26
    assert brief["release_pace"] == {"tone": "good", "value": "On its usual pace"}
    assert brief["maintainer_concentration"] == {"tone": "warn", "value": "Depends on one person"}
    assert brief["issue_response"] is None  # F9


@responses.activate
@pytest.mark.django_db
def test_F6_P1_health_values_carry_source_and_fetch_time(client: Client) -> None:
    make_repo()
    mock_health()

    provenance = client.get(DETAIL_URL).json()["provenance"]

    fetched = "2026-11-23T12:00:00Z"
    assert provenance["commit_activity"] == {
        "source": f"/repos/{FULL_NAME}/stats/commit_activity",
        "fetched_at": fetched,
    }
    assert provenance["single_maintainer"] == {
        "source": f"/repos/{FULL_NAME}/stats/contributors",
        "fetched_at": fetched,
    }
    assert provenance["contributors"] == {
        "source": f"/repos/{FULL_NAME}/contributors",
        "fetched_at": fetched,
    }
    assert provenance["releases"]["source"] == f"/repos/{FULL_NAME}/releases"


README_TEXT = (
    "# Flask\n\n![badge](https://x/y.svg)\n\n"
    "Flask is a lightweight WSGI web application framework for Python.\n"
)


def mock_readme(status: int = 200) -> None:
    payload = {"encoding": "base64", "content": base64.b64encode(README_TEXT.encode()).decode()}
    responses.get(f"{BASE}/readme", json=payload, status=status)


@responses.activate
@pytest.mark.django_db
def test_overview_readme_summary_and_topics_are_served(client: Client) -> None:
    make_repo(raw={**load("repo.json"), "topics": ["flask", "python", "wsgi"]})
    mock_health()

    body = client.get(DETAIL_URL).json()

    assert body["readme_summary"] == (
        "Flask is a lightweight WSGI web application framework for Python."
    )
    assert body["topics"] == ["flask", "python", "wsgi"]
    assert body["provenance"]["readme_summary"] == {
        "source": f"/repos/{FULL_NAME}/readme",
        "fetched_at": "2026-11-23T12:00:00Z",
    }
    assert body["provenance"]["topics"]["source"] == f"/repos/{FULL_NAME}"


@responses.activate
@pytest.mark.django_db
def test_overview_missing_readme_and_topics_are_null(client: Client) -> None:
    raw = {k: v for k, v in load("repo.json").items() if k != "topics"}
    make_repo(raw=raw)
    mock_health(readme_status=404)

    body = client.get(DETAIL_URL).json()

    assert body["readme_summary"] is None
    assert body["topics"] is None
    assert body["commit_activity"]["status"] == "ok"
