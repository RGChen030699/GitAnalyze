import os
import runpy
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest
from django.conf import settings

REPO_ROOT = Path(__file__).resolve().parents[2]
SETTINGS_FILE = REPO_ROOT / "backend" / "config" / "settings.py"
DATABASE_URL = "postgresql://app:secret@db.example.test:6543/appdb"
DATABASE_ENV_NAMES = (
    "DATABASE_URL",
    "POSTGRES_DB",
    "POSTGRES_USER",
    "POSTGRES_PASSWORD",
    "POSTGRES_HOST",
    "POSTGRES_PORT",
)
POSTGRES_ENGINE = "django.db.backends.postgresql"
SQLITE_ENGINE = "django.db.backends.sqlite3"


@pytest.fixture
def clean_env(monkeypatch: pytest.MonkeyPatch) -> pytest.MonkeyPatch:
    for name in DATABASE_ENV_NAMES:
        monkeypatch.delenv(name, raising=False)
    return monkeypatch


def load_default_database() -> dict[str, Any]:
    database: dict[str, Any] = runpy.run_path(str(SETTINGS_FILE))["DATABASES"]["default"]
    return database


def test_DB1_database_url_configures_postgres(clean_env: pytest.MonkeyPatch) -> None:
    clean_env.setenv("DATABASE_URL", DATABASE_URL)

    database = load_default_database()

    assert database["ENGINE"] == POSTGRES_ENGINE
    assert database["HOST"] == "db.example.test"
    assert database["PORT"] == 6543
    assert database["NAME"] == "appdb"
    assert database["USER"] == "app"


def test_DB1_database_url_wins_over_postgres_vars(clean_env: pytest.MonkeyPatch) -> None:
    clean_env.setenv("DATABASE_URL", DATABASE_URL)
    clean_env.setenv("POSTGRES_DB", "localdb")

    assert load_default_database()["NAME"] == "appdb"


def test_DB2_ssl_required_when_url_has_no_sslmode(clean_env: pytest.MonkeyPatch) -> None:
    clean_env.setenv("DATABASE_URL", DATABASE_URL)

    assert load_default_database()["OPTIONS"]["sslmode"] == "require"


def test_DB2_weak_sslmode_is_upgraded(clean_env: pytest.MonkeyPatch) -> None:
    clean_env.setenv("DATABASE_URL", f"{DATABASE_URL}?sslmode=disable")

    assert load_default_database()["OPTIONS"]["sslmode"] == "require"


def test_DB2_stronger_sslmode_is_kept(clean_env: pytest.MonkeyPatch) -> None:
    clean_env.setenv("DATABASE_URL", f"{DATABASE_URL}?sslmode=verify-full")

    assert load_default_database()["OPTIONS"]["sslmode"] == "verify-full"


def test_DB3_postgres_vars_still_work(clean_env: pytest.MonkeyPatch) -> None:
    clean_env.setenv("POSTGRES_DB", "localdb")
    clean_env.setenv("POSTGRES_HOST", "postgres.local")

    database = load_default_database()

    assert database["ENGINE"] == POSTGRES_ENGINE
    assert database["NAME"] == "localdb"
    assert database["HOST"] == "postgres.local"
    assert "OPTIONS" not in database


def test_DB3_sqlite_is_the_default(clean_env: pytest.MonkeyPatch) -> None:
    assert load_default_database()["ENGINE"] == SQLITE_ENGINE


def test_DB4_active_test_database_is_sqlite() -> None:
    assert settings.DATABASES["default"]["ENGINE"] == SQLITE_ENGINE


@pytest.mark.parametrize(
    ("name", "value"),
    [("DATABASE_URL", DATABASE_URL), ("POSTGRES_DB", "appdb")],
)
def test_DB4_pytest_uses_sqlite_with_database_env(name: str, value: str) -> None:
    env = {**os.environ, name: value, "DJANGO_SETTINGS_MODULE": "config.settings"}
    target = f"{Path(__file__).relative_to(REPO_ROOT)}::test_DB4_active_test_database_is_sqlite"

    result = subprocess.run(
        [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", target],
        cwd=REPO_ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout + result.stderr
