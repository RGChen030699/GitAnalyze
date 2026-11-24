"""Reading the GitHubTrendingRSS feed (F0 W3). The feed is not GitHub's API: no token goes to it."""

from datetime import UTC, datetime
from pathlib import Path

import pytest
import requests
import responses
from github_client.trending import (
    FEED_BASE_URL,
    TrendingFeedError,
    feed_slug,
    feed_url,
    fetch_trending,
    parse_feed,
)

FIXTURE = Path(__file__).parent / "fixtures" / "github" / "trending_weekly_all.xml"
NOW = datetime(2026, 11, 24, 12, 0, tzinfo=UTC)
WEEKLY_ALL = f"{FEED_BASE_URL}/weekly/all.xml"
RECORDED = [
    "backnotprop/plannotator",
    "google-labs-code/stitch-skills",
    "GoogleChrome/modern-web-guidance-src",
    "alibaba/open-code-review",
    "mvanhorn/last30days-skill",
]


def item(title: str, link: str) -> str:
    return f"<item><title>{title}</title><link>{link}</link></item>"


def feed(*items: str) -> str:
    return f'<?xml version="1.0"?><rss version="2.0"><channel>{"".join(items)}</channel></rss>'


@pytest.mark.parametrize(
    ("language", "slug"),
    [
        (None, "all"),
        ("Python", "python"),
        ("C#", "c%23"),
        ("C++", "c++"),
        ("Jupyter Notebook", "jupyter-notebook"),
    ],
)
def test_W3_feed_slug(language: str | None, slug: str) -> None:
    assert feed_slug(language) == slug


def test_W3_feed_url() -> None:
    assert feed_url("weekly", "C#") == f"{FEED_BASE_URL}/weekly/c%23.xml"
    assert feed_url("daily", None) == f"{FEED_BASE_URL}/daily/all.xml"


def test_W3_parse_recorded_feed_keeps_github_order_and_publish_time() -> None:
    names, published_at = parse_feed(FIXTURE.read_text())
    assert names == RECORDED
    assert published_at == datetime(2026, 11, 24, 10, 35, 1, tzinfo=UTC)


def test_W3_parse_reads_the_name_from_the_github_link() -> None:
    text = feed(item("Display title", "https://github.com/octo/widget"))
    assert parse_feed(text) == (["octo/widget"], None)


def test_W3_parse_skips_items_that_are_not_github_repositories() -> None:
    text = feed(
        item("x", "https://example.com/octo/widget"),
        item("y", "https://github.com/octo"),
        item("z", "https://github.com/octo/widget/issues"),
        item("ok", "https://github.com/a/b.c-d_e"),
        item("dupe", "https://github.com/a/b.c-d_e"),
    )
    assert parse_feed(text)[0] == ["a/b.c-d_e"]


def test_W3_parse_bad_xml_raises() -> None:
    with pytest.raises(TrendingFeedError):
        parse_feed("<rss><channel>")


@responses.activate
def test_W3_fetch_sends_no_github_token() -> None:
    responses.get(WEEKLY_ALL, body=FIXTURE.read_text())

    result = fetch_trending("weekly", None, clock=lambda: NOW)

    assert result.names == RECORDED
    assert result.source == WEEKLY_ALL
    assert result.fetched_at == NOW
    assert "Authorization" not in responses.calls[0].request.headers


@responses.activate
def test_G4_unreachable_feed_raises_feed_error() -> None:
    responses.get(WEEKLY_ALL, body=requests.ConnectionError("down"))
    with pytest.raises(TrendingFeedError):
        fetch_trending("weekly", None, clock=lambda: NOW)


@responses.activate
def test_G4_feed_error_status_raises_feed_error() -> None:
    responses.get(WEEKLY_ALL, status=503)
    with pytest.raises(TrendingFeedError):
        fetch_trending("weekly", None, clock=lambda: NOW)
