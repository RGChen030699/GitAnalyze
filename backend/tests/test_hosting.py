"""Hosting the backend as a Vercel Python project, and the daily refresh (F7 Step 10)."""

import json
import runpy
from pathlib import Path
from typing import Any

import pytest
from django.core.exceptions import ImproperlyConfigured

REPO_ROOT = Path(__file__).resolve().parents[2]
SETTINGS_FILE = REPO_ROOT / "backend" / "config" / "settings.py"
ENTRY_POINT = REPO_ROOT / "api" / "index.py"
ROOT_VERCEL = REPO_ROOT / "vercel.json"
FRONTEND_VERCEL = REPO_ROOT / "frontend" / "vercel.json"
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "refresh-rankings.yml"
VERCELIGNORE = REPO_ROOT / ".vercelignore"
HOSTING_ENV = (
    "VERCEL",
    "VERCEL_URL",
    "DJANGO_DEBUG",
    "DJANGO_SECRET_KEY",
    "DJANGO_ALLOWED_HOSTS",
    "FRONTEND_ORIGIN",
    "DATABASE_URL",
    "POSTGRES_DB",
)
PAGE_REWRITES = [
    {"source": "/repo/:owner/:name", "destination": "/repo.html"},
    {"source": "/compare", "destination": "/compare.html"},
    {"source": "/about", "destination": "/about.html"},
    {"source": "/about/:section", "destination": "/about.html"},
]


@pytest.fixture
def env(monkeypatch: pytest.MonkeyPatch) -> pytest.MonkeyPatch:
    for name in HOSTING_ENV:
        monkeypatch.delenv(name, raising=False)
    return monkeypatch


def load_settings() -> dict[str, Any]:
    return runpy.run_path(str(SETTINGS_FILE))


def test_H1_debug_defaults_on_for_local_runs(env: pytest.MonkeyPatch) -> None:
    assert load_settings()["DEBUG"] is True


def test_H1_debug_defaults_off_on_vercel(env: pytest.MonkeyPatch) -> None:
    env.setenv("VERCEL", "1")
    env.setenv("DJANGO_SECRET_KEY", "test-only-key")

    assert load_settings()["DEBUG"] is False


@pytest.mark.parametrize(("value", "expected"), [("0", False), ("1", True)])
def test_H1_debug_comes_from_env(env: pytest.MonkeyPatch, value: str, expected: bool) -> None:
    env.setenv("DJANGO_DEBUG", value)
    env.setenv("DJANGO_SECRET_KEY", "test-only-key")

    assert load_settings()["DEBUG"] is expected


def test_H2_secret_key_required_when_debug_is_off(env: pytest.MonkeyPatch) -> None:
    env.setenv("DJANGO_DEBUG", "0")

    with pytest.raises(ImproperlyConfigured, match="DJANGO_SECRET_KEY"):
        load_settings()


def test_H3_allowed_hosts_come_from_env_trimmed(env: pytest.MonkeyPatch) -> None:
    env.setenv("DJANGO_ALLOWED_HOSTS", " api.example.test, ,other.example.test ")

    assert load_settings()["ALLOWED_HOSTS"] == ["api.example.test", "other.example.test"]


def test_H3_allowed_hosts_include_the_vercel_deployment_host(env: pytest.MonkeyPatch) -> None:
    env.setenv("DJANGO_ALLOWED_HOSTS", "api.example.test")
    env.setenv("VERCEL_URL", "gitanalyze-api-abc123.vercel.app")

    assert load_settings()["ALLOWED_HOSTS"] == [
        "api.example.test",
        "gitanalyze-api-abc123.vercel.app",
    ]


def test_H4_csrf_trusts_the_frontend_origin(env: pytest.MonkeyPatch) -> None:
    env.setenv("FRONTEND_ORIGIN", "https://app.example.test/")

    assert load_settings()["CSRF_TRUSTED_ORIGINS"] == ["https://app.example.test"]


def test_H5_database_url_opens_a_fresh_connection_per_request(env: pytest.MonkeyPatch) -> None:
    env.setenv("DATABASE_URL", "postgresql://app:secret@db.example.test:5432/appdb")

    database = load_settings()["DATABASES"]["default"]

    assert database["CONN_MAX_AGE"] == 0
    assert database["OPTIONS"]["sslmode"] == "require"


def test_H6_entry_point_exposes_the_django_wsgi_app() -> None:
    app = runpy.run_path(str(ENTRY_POINT))["app"]

    assert type(app).__name__ == "WSGIHandler"


def test_H7_root_vercel_json_routes_api_to_the_entry_point_only() -> None:
    config = json.loads(ROOT_VERCEL.read_text())

    assert config["builds"] == [
        {"src": "api/index.py", "use": "@vercel/python", "config": config["builds"][0]["config"]}
    ]
    assert config["routes"] == [{"src": "/api/(.*)", "dest": "api/index.py"}]


def test_H7_nothing_runs_migrations_at_build_or_refresh_time() -> None:
    for path in (ROOT_VERCEL, ENTRY_POINT, WORKFLOW):
        assert "migrate" not in path.read_text(), path.name


def test_H8_frontend_forwards_api_to_the_backend_and_keeps_page_routes() -> None:
    rewrites = json.loads(FRONTEND_VERCEL.read_text())["rewrites"]

    assert rewrites[0] == {
        "source": "/api/:path*",
        "destination": "https://BACKEND_URL_PLACEHOLDER/api/:path*",
    }
    assert rewrites[1:] == PAGE_REWRITES


def test_H9_daily_refresh_workflow_uses_repository_secrets() -> None:
    text = WORKFLOW.read_text()

    assert "schedule:" in text and "cron:" in text
    assert "python backend/manage.py refresh_rankings --limit 100" in text
    assert "DATABASE_URL: ${{ secrets.DATABASE_URL }}" in text
    assert "GITHUB_TOKEN: ${{ secrets.GH_API_TOKEN }}" in text


def test_H10_vercel_deployment_leaves_out_frontend_docs_and_tests() -> None:
    ignored = VERCELIGNORE.read_text().split()

    for entry in ("frontend/", "docs/", "backend/tests/", ".claude/", "*.html"):
        assert entry in ignored, entry


@pytest.mark.parametrize("path", [ROOT_VERCEL, FRONTEND_VERCEL, ENTRY_POINT, WORKFLOW])
def test_H11_hosting_files_hold_no_secrets(path: Path) -> None:
    text = path.read_text()

    for marker in ("postgres://", "postgresql://", "ghp_", "github_pat_", "npg_"):
        assert marker not in text, marker
