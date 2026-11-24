"""F4 in the API: scanned on report open (cached 24h), with provenance, flagged in rankings."""

from datetime import UTC, datetime, timedelta
from io import StringIO
from typing import Any

import pytest
import responses
from django.core.management import call_command
from django.test import Client
from github_client.client import API_BASE_URL, RAW_BASE_URL
from repositories.models import Repository

NOW = datetime(2026, 11, 24, 12, 0, tzinfo=UTC)
FULL_NAME = "octo/kit"
DETAIL_URL = f"/api/repos/{FULL_NAME}"
TREE_URL = f"{API_BASE_URL}/repos/{FULL_NAME}/git/trees/main"
RAW = f"{RAW_BASE_URL}/{FULL_NAME}/main"
SKILL = "---\nname: forms\ndescription: Fills PDF forms.\n---\nBody\n"
PANEL = {"has_ai": True, "skills": [], "source": "/repos/x/git/trees/main?recursive=1"}


@pytest.fixture(autouse=True)
def frozen_now(monkeypatch: pytest.MonkeyPatch, settings: Any) -> None:
    settings.GITHUB_TOKEN = "test-token"
    monkeypatch.setattr("django.utils.timezone.now", lambda: NOW)


def make_repo(full_name: str = FULL_NAME, **overrides: Any) -> Repository:
    fields: dict[str, Any] = {
        "github_id": abs(hash(full_name)) % 10_000_000,
        "full_name": full_name,
        "owner_login": full_name.split("/")[0],
        "owner_type": "Organization",
        "archived": False,
        "stargazers_count": 100,
        "forks_count": 1,
        "open_issues_count": 1,
        "source": f"/repos/{full_name}",
        "fetched_at": NOW - timedelta(hours=2),
        "health_fetched_at": NOW - timedelta(hours=2),
        "ranked_at": NOW - timedelta(hours=2),
        "raw": {"default_branch": "main"},
    }
    return Repository.objects.create(**{**fields, **overrides})


def mock_scan(tree: list[dict[str, str]] | None = None) -> None:
    tree = tree or [
        {"path": "skills/forms/SKILL.md", "type": "blob", "sha": "a" * 40},
        {"path": "skills/forms/scripts/fill_form.py", "type": "blob", "sha": "b" * 40},
    ]
    responses.get(TREE_URL, json={"truncated": False, "tree": tree})
    responses.get(f"{RAW}/skills/forms/SKILL.md", body=SKILL)


@responses.activate
@pytest.mark.django_db
def test_F4_report_open_scans_once_then_serves_the_cache(client: Client) -> None:
    make_repo()
    mock_scan()

    body = client.get(DETAIL_URL).json()

    assert body["ai"] is True
    panel = body["ai_capabilities"]
    assert [s["name"] for s in panel["skills"]] == ["forms"]
    assert panel["skills"][0]["scripts"] == ["scripts/fill_form.py"]
    assert panel["publisher"] == "organization"
    assert Repository.objects.get().ai_fetched_at == NOW

    responses.calls.reset()
    client.get(DETAIL_URL)
    assert len(responses.calls) == 0


@responses.activate
@pytest.mark.django_db
def test_F4_scan_older_than_24_hours_runs_again(client: Client) -> None:
    make_repo(ai=PANEL, ai_fetched_at=NOW - timedelta(hours=24))
    mock_scan()

    client.get(DETAIL_URL)

    assert any(str(c.request.url).startswith(TREE_URL) for c in responses.calls)


@responses.activate
@pytest.mark.django_db
def test_F4_no_ai_signals_returns_false_and_an_empty_panel(client: Client) -> None:
    make_repo()
    mock_scan([{"path": "main.go", "type": "blob", "sha": "c" * 40}])

    body = client.get(DETAIL_URL).json()

    assert body["ai"] is False
    assert body["ai_capabilities"]["has_ai"] is False
    assert body["ai_capabilities"]["skills"] == []


@responses.activate
@pytest.mark.django_db
def test_F4_failed_scan_keeps_the_page_working_with_ai_null(client: Client) -> None:
    make_repo()
    responses.get(TREE_URL, status=404)

    response = client.get(DETAIL_URL)

    assert response.status_code == 200
    assert response.json()["ai"] is None
    assert response.json()["ai_capabilities"] is None


@responses.activate
@pytest.mark.django_db
def test_F6_P1_ai_panel_carries_its_source_and_fetch_time(client: Client) -> None:
    make_repo()
    mock_scan()

    provenance = client.get(DETAIL_URL).json()["provenance"]

    expected = {
        "source": f"/repos/{FULL_NAME}/git/trees/main?recursive=1",
        "fetched_at": "2026-11-24T12:00:00Z",
    }
    assert provenance["ai_capabilities"] == expected
    assert provenance["ai"] == expected


@pytest.mark.django_db
def test_F4_rankings_rows_carry_the_ai_flag(client: Client) -> None:
    make_repo("a/skills", stargazers_count=300, ai=PANEL, ai_fetched_at=NOW)
    make_repo("b/plain", stargazers_count=200, ai={**PANEL, "has_ai": False}, ai_fetched_at=NOW)
    make_repo("c/unscanned", stargazers_count=100)

    rows = client.get("/api/rankings").json()["results"]

    assert [(r["full_name"], r["ai"]) for r in rows] == [
        ("a/skills", True),
        ("b/plain", False),
        ("c/unscanned", None),
    ]


@responses.activate
@pytest.mark.django_db
def test_F4_refresh_ai_scans_ranked_repositories_not_scanned_for_7_days() -> None:
    make_repo("octo/kit", ai_fetched_at=NOW - timedelta(days=8))
    make_repo("octo/fresh", ai=PANEL, ai_fetched_at=NOW - timedelta(days=6))
    make_repo("octo/unranked", ranked_at=None)
    mock_scan()

    out = StringIO()
    call_command("refresh_ai", stdout=out, stderr=StringIO())

    assert Repository.objects.get(full_name="octo/kit").ai_fetched_at == NOW
    assert Repository.objects.get(full_name="octo/fresh").ai_fetched_at == NOW - timedelta(days=6)
    assert Repository.objects.get(full_name="octo/unranked").ai is None
    # 1 API request for the tree; raw file reads cost no API quota but are counted too
    assert "AI scan: 1 repositories scanned, 2 requests sent, 0 failures" in out.getvalue()


@responses.activate
@pytest.mark.django_db
def test_F4_refresh_ai_reports_a_failure_and_carries_on() -> None:
    make_repo("octo/kit")
    make_repo("octo/other", raw={"default_branch": "main"})
    mock_scan()
    responses.get(f"{API_BASE_URL}/repos/octo/other/git/trees/main", status=404)

    out, err = StringIO(), StringIO()
    call_command("refresh_ai", stdout=out, stderr=err)

    assert Repository.objects.get(full_name="octo/kit").ai is not None
    assert "octo/other" in err.getvalue()
    assert "1 failures" in out.getvalue()
