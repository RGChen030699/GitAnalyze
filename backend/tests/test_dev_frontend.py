"""Local development only: Django serves frontend/ on the same origin as /api/ (F7 Step 7).

The routes mirror frontend/vercel.json. In production Vercel serves the pages, and these
routes answer 404 because DEBUG is off.
"""

from typing import Any

import pytest
from django.test import Client


@pytest.fixture
def debug_on(settings: Any) -> None:
    settings.DEBUG = True


def body(response: Any) -> str:
    return b"".join(response.streaming_content).decode()


@pytest.mark.parametrize(
    ("url", "title"),
    [
        ("/", "<title>GitAnalyze Dashboard</title>"),
        ("/repo/pallets/flask", 'id="repoTitle"'),
        ("/compare", 'id="dlCmp"'),
        ("/about", 'id="h-brief"'),
        ("/about/brief", 'id="h-brief"'),
    ],
)
def test_dev_serves_page_for_each_vercel_route(
    client: Client, debug_on: None, url: str, title: str
) -> None:
    response = client.get(url)

    assert response.status_code == 200
    assert title in body(response)


def test_dev_serves_frontend_scripts(client: Client, debug_on: None) -> None:
    response = client.get("/compare-list.js")

    assert response.status_code == 200
    assert "GACompare" in body(response)


def test_dev_does_not_serve_files_outside_the_top_level(client: Client, debug_on: None) -> None:
    assert client.get("/%2e%2e/backend/manage.py").status_code == 404
    assert client.get("/tests/anything.js").status_code == 404


def test_dev_frontend_is_off_when_debug_is_off(client: Client, settings: Any) -> None:
    settings.DEBUG = False

    assert client.get("/").status_code == 404
    assert client.get("/compare-list.js").status_code == 404
