"""GET /api/repos/{owner}/{name} (F7 Step 6a; F1 L4, F0 C8, F6 P1)."""

from datetime import UTC, date, datetime, timedelta
from typing import Any

import pytest
import responses
from django.test import Client
from github_client.client import API_BASE_URL
from repositories.models import Repository, StarWeek

from tests.test_refresh_rankings import load, mock_details

NOW = datetime(2026, 11, 23, 12, 0, tzinfo=UTC)
REPO_SOURCE = "/repos/pallets/flask"
REPO_URL = f"{API_BASE_URL}{REPO_SOURCE}"
HISTORY_SOURCE = "/repos/pallets/flask/stargazers/history"
UNSTORED_FIELDS = ("commit_activity", "contributors", "releases", "issues", "pull_requests")
DETAIL_FIELDS = (
    "full_name",
    "owner",
    "name",
    "description",
    "language",
    "owner_type",
    "archived",
    "stars",
    "forks",
    "open_issues",
    "pushed_at",
    "newest_release_at",
    "status",
    "stars_gained_7d",
    "stars_gained_30d",
    "stars_gained_year",
)


@pytest.fixture(autouse=True)
def frozen_now(monkeypatch: pytest.MonkeyPatch, settings: Any) -> None:
    settings.GITHUB_TOKEN = "test-token"
    monkeypatch.setattr("django.utils.timezone.now", lambda: NOW)


def make_repo(full_name: str = "pallets/flask", **overrides: Any) -> Repository:
    fields: dict[str, Any] = {
        "github_id": 596892,
        "full_name": full_name,
        "owner_login": full_name.split("/")[0],
        "owner_type": "Organization",
        "archived": False,
        "stargazers_count": 100,
        "forks_count": 10,
        "open_issues_count": 5,
        "source": REPO_SOURCE,
        "fetched_at": NOW - timedelta(hours=2),
        "raw": {},
    }
    return Repository.objects.create(**{**fields, **overrides})


def mock_flask() -> None:
    responses.get(REPO_URL, json=load("repo.json"))
    mock_details("pallets/flask")


@responses.activate
@pytest.mark.django_db
def test_L4_fresh_repo_served_from_database_without_github_call(client: Client) -> None:
    make_repo()

    response = client.get("/api/repos/pallets/flask")

    assert response.status_code == 200
    assert response.json()["full_name"] == "pallets/flask"
    assert len(responses.calls) == 0


@responses.activate
@pytest.mark.django_db
def test_L4_cache_lookup_is_case_insensitive(client: Client) -> None:
    make_repo()

    response = client.get("/api/repos/Pallets/FLASK")

    assert response.status_code == 200
    assert response.json()["full_name"] == "pallets/flask"
    assert len(responses.calls) == 0


@responses.activate
@pytest.mark.django_db
def test_L4_missing_repo_is_fetched_and_saved(client: Client) -> None:
    mock_flask()

    response = client.get("/api/repos/pallets/flask")

    assert response.status_code == 200
    assert response.json()["full_name"] == "pallets/flask"
    saved = Repository.objects.get()
    assert saved.source == REPO_SOURCE
    assert saved.fetched_at == NOW
    assert responses.calls[0].request.url == REPO_URL


@responses.activate
@pytest.mark.django_db
def test_L4_repo_fetched_24_hours_ago_is_refetched(client: Client) -> None:
    make_repo(fetched_at=NOW - timedelta(hours=24), stargazers_count=1)
    mock_flask()

    response = client.get("/api/repos/pallets/flask")

    assert response.status_code == 200
    saved = Repository.objects.get()
    assert saved.fetched_at == NOW
    assert saved.stargazers_count == load("repo.json")["stargazers_count"]


@responses.activate
@pytest.mark.django_db
def test_lookup_fetch_does_not_mark_repo_ranked(client: Client) -> None:
    mock_flask()

    client.get("/api/repos/pallets/flask")

    assert Repository.objects.get().ranked_at is None


@responses.activate
@pytest.mark.django_db
def test_lookup_refetch_keeps_existing_ranked_at(client: Client) -> None:
    ranked_at = NOW - timedelta(days=1)
    make_repo(fetched_at=NOW - timedelta(hours=24), ranked_at=ranked_at)
    mock_flask()

    client.get("/api/repos/pallets/flask")

    assert Repository.objects.get().ranked_at == ranked_at


@pytest.mark.django_db
def test_F2_detail_returns_repository_fields_status_and_gains(client: Client) -> None:
    make_repo(
        description="A micro framework",
        language="Python",
        pushed_at=NOW - timedelta(days=3),
        newest_release_at=NOW - timedelta(days=40),
        status="Active",
        stars_gained_7d=12,
        stars_gained_30d=-2,
        stars_gained_year=400,
    )

    body = client.get("/api/repos/pallets/flask").json()

    assert {key: body[key] for key in DETAIL_FIELDS} == {
        "full_name": "pallets/flask",
        "owner": "pallets",
        "name": "flask",
        "description": "A micro framework",
        "language": "Python",
        "owner_type": "Organization",
        "archived": False,
        "stars": 100,
        "forks": 10,
        "open_issues": 5,
        "pushed_at": "2026-11-20T12:00:00Z",
        "newest_release_at": "2026-10-14T12:00:00Z",
        "status": "Active",
        "stars_gained_7d": 12,
        "stars_gained_30d": -2,
        "stars_gained_year": 400,
    }


@pytest.mark.django_db
def test_F3_detail_returns_star_weeks_oldest_first_with_provenance(client: Client) -> None:
    repo = make_repo()
    for week_start, total in ((date(2026, 11, 22), 3), (date(2026, 11, 15), 9)):
        StarWeek.objects.create(
            repository=repo,
            week_start=week_start,
            stars_gained=total,
            days=[total, 0, 0, 0, 0, 0, 0],
            source=HISTORY_SOURCE,
            fetched_at=NOW - timedelta(hours=2),
        )

    body = client.get("/api/repos/pallets/flask").json()

    assert body["star_history"] == [
        {
            "week_start": "2026-11-15",
            "stars_gained": 9,
            "days": [9, 0, 0, 0, 0, 0, 0],
            "source": HISTORY_SOURCE,
            "fetched_at": "2026-11-23T10:00:00Z",
        },
        {
            "week_start": "2026-11-22",
            "stars_gained": 3,
            "days": [3, 0, 0, 0, 0, 0, 0],
            "source": HISTORY_SOURCE,
            "fetched_at": "2026-11-23T10:00:00Z",
        },
    ]


@pytest.mark.django_db
def test_C8_detail_gives_source_and_fetched_at_for_each_value(client: Client) -> None:
    repo = make_repo(
        language="Python",
        pushed_at=NOW - timedelta(days=3),
        newest_release_at=NOW - timedelta(days=40),
        status="Active",
        stars_gained_7d=12,
        stars_gained_30d=30,
        star_history_fetched_at=NOW - timedelta(hours=1),
    )
    StarWeek.objects.create(
        repository=repo,
        week_start=date(2026, 11, 22),
        stars_gained=3,
        days=[3, 0, 0, 0, 0, 0, 0],
        source=HISTORY_SOURCE,
        fetched_at=NOW - timedelta(hours=1),
    )

    provenance = client.get("/api/repos/pallets/flask").json()["provenance"]

    repo_origin = {"source": REPO_SOURCE, "fetched_at": "2026-11-23T10:00:00Z"}
    history_origin = {"source": HISTORY_SOURCE, "fetched_at": "2026-11-23T11:00:00Z"}
    for field in ("owner_type", "archived", "stars", "forks", "open_issues", "pushed_at"):
        assert provenance[field] == repo_origin, field
    assert provenance["language"] == repo_origin
    assert provenance["newest_release_at"] == {
        "source": "/repos/pallets/flask/releases",
        "fetched_at": "2026-11-23T10:00:00Z",
    }
    assert provenance["status"] == {
        "source": "Computed from pushed_at and releases (F2 status rule)",
        "fetched_at": "2026-11-23T10:00:00Z",
    }
    assert provenance["stars_gained_7d"] == history_origin
    assert provenance["stars_gained_30d"] == history_origin
    assert provenance["stars_gained_year"] is None
    assert provenance["description"] is None


@pytest.mark.django_db
def test_detail_unstored_data_is_null_not_zero(client: Client) -> None:
    make_repo()

    body = client.get("/api/repos/pallets/flask").json()

    for field in UNSTORED_FIELDS:
        assert field in body, field
        assert body[field] is None, field
        assert body["provenance"][field] is None, field


@responses.activate
@pytest.mark.django_db
def test_F1_unknown_repo_returns_404_with_message(client: Client) -> None:
    responses.get(f"{API_BASE_URL}/repos/nobody/missing", json={"message": "Not Found"}, status=404)

    response = client.get("/api/repos/nobody/missing")

    assert response.status_code == 404
    assert response.json() == {"detail": "We couldn't find a public repository at nobody/missing"}
    assert Repository.objects.count() == 0
