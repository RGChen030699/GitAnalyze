"""Static checks on frontend/ for the switch from sample data to the API (F7 Step 7, T7)."""

from pathlib import Path

import pytest

FRONTEND = Path(__file__).resolve().parents[2] / "frontend"
REAL_DATA_PAGES = ("index.html", "repo.html", "compare.html")
CALCULATING = "GitHub is still calculating this. Check back in a minute."


def read(name: str) -> str:
    return (FRONTEND / name).read_text()


def frontend_sources() -> list[Path]:
    return [p for p in FRONTEND.iterdir() if p.suffix in {".html", ".js"}]


def test_T7_frontend_never_calls_github_or_an_absolute_api_host() -> None:
    for source in frontend_sources():
        text = source.read_text()
        assert "api.github.com" not in text, source.name
        assert "localhost:8000" not in text, source.name


def test_rankings_page_loads_from_relative_api_path() -> None:
    assert "'/api/rankings?'" in read("index.html")


@pytest.mark.parametrize("page", ["repo.html", "compare.html"])
def test_report_pages_load_each_repo_from_relative_api_path(page: str) -> None:
    assert "'/api/repos/'" in read(page)


@pytest.mark.parametrize("page", REAL_DATA_PAGES)
def test_real_data_pages_use_data_module_not_sample_js(page: str) -> None:
    html = read(page)
    assert '<script src="/data.js"></script>' in html
    assert "sample.js" not in html


@pytest.mark.parametrize("page", REAL_DATA_PAGES)
def test_real_data_pages_drop_sample_data_notes(page: str) -> None:
    html = read(page)
    assert "Sample data" not in html
    assert "sample repositories" not in html


def test_rankings_page_has_no_sample_generator() -> None:
    html = read("index.html")
    for marker in ("makeRepo", "const NAMED", "function generate", "NOW_LABEL"):
        assert marker not in html, marker


@pytest.mark.parametrize("page", ["repo.html", "compare.html"])
def test_report_pages_show_calculating_message_for_null_charts(page: str) -> None:
    assert CALCULATING in read(page)


def test_sample_js_is_gone() -> None:
    assert not (FRONTEND / "sample.js").exists()
