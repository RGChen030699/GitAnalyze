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


def test_about_page_describes_15_day_interest_rule() -> None:
    about = read("about.html")

    assert "Stars in the last 15 days against the 15 days before" in about
    assert "Flat (under 0.1% of its total stars in 15 days)" in about
    assert "Stars in the last 30 days against the 30 days before" not in about
    assert "0.2%" not in about


def test_report_interest_text_compares_with_the_15_days_before() -> None:
    repo = read("repo.html")

    assert "more stars than the 15 days before." in repo
    assert "Interest is cooling compared with the 15 days before." in repo
    assert "the 30 days before" not in repo
    assert "Stars gained, 30 days" in repo  # 30-day numbers stay


def test_compare_interest_row_uses_the_15_days_before() -> None:
    compare = read("compare.html")

    assert "Change on the 15 days before" in compare
    assert "Change on the 30 days before" not in compare
    assert "Stars gained, 30 days" in compare  # 30-day numbers stay


def test_compare_interest_row_reads_the_api_change() -> None:
    row = "{ l:'Change on the 15 days before', v: it => it.A.interestChange,"

    assert row in read("compare.html")


def test_report_interest_text_reads_the_api_change() -> None:
    repo = read("repo.html")

    assert "${pct(A.interestChange)} more stars than the 15 days before." in repo
    assert "A.momChange === null ? 'Interest is growing.'" not in repo


def test_G4_trending_tab_credits_github_trending_with_a_link() -> None:
    text = read("index.html")
    assert '<a href="https://github.com/trending"' in text
    assert "From GitHub Trending</a>" in text
    assert "'Trending last updated '" in text


def test_home_dropdowns_open_below_on_computers_and_stay_native_on_touch() -> None:
    script = read("select.js")
    assert '<script src="/select.js"></script>' in read("index.html")
    assert "(hover: hover) and (pointer: fine)" in script  # touch devices keep the native picker
    assert "r.bottom + 6" in script  # the list starts below the box, never on top of it


def test_report_page_shows_a_spinner_while_it_loads() -> None:
    text = read("repo.html")
    assert 'id="pageLoading"' in text and 'class="spinner"' in text
    assert "Loading report" in text
    assert "Fetching from GitHub. A first look can take a few seconds." in text


def test_readme_tab_sits_right_after_summary_and_loads_more() -> None:
    text = read("repo.html")
    summary = text.index('<a href="#s-summary">Summary</a>')
    readme = text.index('<a href="#s-readme">README</a>')
    momentum = text.index('<a href="#s-momentum">Momentum</a>')
    assert summary < readme < momentum
    assert 'id="s-readme"' in text
    assert "Load more" in text
    assert "Show less" in text  # collapses back to the first screen
