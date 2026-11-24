import runpy
from pathlib import Path

import pytest
from django.test import Client

URL = "/api/rankings"
ORIGIN = "http://localhost:8080"
SETTINGS_FILE = Path(__file__).resolve().parents[1] / "config" / "settings.py"
ALLOW_ORIGIN = "Access-Control-Allow-Origin"


@pytest.fixture(autouse=True)
def frontend_origin(settings) -> None:
    settings.FRONTEND_ORIGIN = ORIGIN


def load_frontend_origin() -> str:
    origin: str = runpy.run_path(str(SETTINGS_FILE))["FRONTEND_ORIGIN"]
    return origin


def test_cors_origin_defaults_to_local_frontend(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("FRONTEND_ORIGIN", raising=False)

    assert load_frontend_origin() == "http://localhost:8080"


def test_cors_origin_reads_env_without_trailing_slash(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("FRONTEND_ORIGIN", "https://app.example.test/")

    assert load_frontend_origin() == "https://app.example.test"


@pytest.mark.django_db
def test_cors_allows_frontend_origin(client: Client) -> None:
    response = client.get(URL, headers={"Origin": ORIGIN})

    assert response[ALLOW_ORIGIN] == ORIGIN
    assert "Origin" in response["Vary"]
    assert "Access-Control-Allow-Credentials" not in response


@pytest.mark.django_db
@pytest.mark.parametrize(
    "origin",
    ["https://evil.example", "http://localhost:8080.evil.example", "http://localhost:5173"],
)
def test_cors_rejects_other_origin(client: Client, origin: str) -> None:
    response = client.get(URL, headers={"Origin": origin})

    assert ALLOW_ORIGIN not in response
    assert "Origin" in response["Vary"]


@pytest.mark.django_db
def test_cors_adds_header_to_error_responses(client: Client) -> None:
    response = client.get(URL, {"limit": "7"}, headers={"Origin": ORIGIN})

    assert response.status_code == 400
    assert response[ALLOW_ORIGIN] == ORIGIN


@pytest.mark.django_db
def test_cors_only_on_api_paths(client: Client) -> None:
    response = client.get("/admin/login/", headers={"Origin": ORIGIN})

    assert ALLOW_ORIGIN not in response


def test_cors_preflight_allows_frontend_origin(client: Client) -> None:
    response = client.options(
        URL, headers={"Origin": ORIGIN, "Access-Control-Request-Method": "GET"}
    )

    assert response.status_code == 204
    assert response[ALLOW_ORIGIN] == ORIGIN
    assert response["Access-Control-Allow-Methods"] == "GET, OPTIONS"
    assert "Origin" in response["Vary"]


def test_cors_preflight_rejects_other_origin(client: Client) -> None:
    response = client.options(
        URL, headers={"Origin": "https://evil.example", "Access-Control-Request-Method": "GET"}
    )

    assert ALLOW_ORIGIN not in response
