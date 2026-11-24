"""GET /api/repos/{owner}/{name} (F7 Step 6a; F1 L4, F0 C8, F6 P1)."""

from datetime import UTC, datetime, timedelta
from typing import Any

import pytest
import responses
from django.test import Client
from repositories.models import Repository

NOW = datetime(2026, 11, 23, 12, 0, tzinfo=UTC)
REPO_SOURCE = "/repos/pallets/flask"


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
