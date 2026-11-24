"""Read GitHub Trending through the GitHubTrendingRSS feed (F0 W3).

The feed is a third-party mirror of github.com/trending, not GitHub's API, so the request carries
no token and doesn't count against the API budget. We never scrape github.com itself (F8 §6).
"""

import re
import xml.etree.ElementTree as ET
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime
from email.utils import parsedate_to_datetime

import requests

FEED_BASE_URL = "https://mshibanami.github.io/GitHubTrendingRSS"
PERIODS = ("daily", "weekly", "monthly")
ALL_LANGUAGES = "all"
REQUEST_TIMEOUT = 20
REPO_LINK = re.compile(r"^https://github\.com/([A-Za-z0-9-]+/[A-Za-z0-9._-]+)/?$")


class TrendingFeedError(Exception):
    """The feed could not be read: unreachable, an error status, or not valid XML."""


@dataclass(frozen=True)
class TrendingFeed:
    names: list[str]  # owner/name, in GitHub's Trending order
    source: str
    fetched_at: datetime
    published_at: datetime | None


def feed_slug(language: str | None) -> str:
    """The feed's name for a language: lowercase, spaces as "-", "#" as "%23"."""
    if language is None:
        return ALL_LANGUAGES
    return language.lower().replace(" ", "-").replace("#", "%23")


def feed_url(period: str, language: str | None) -> str:
    if period not in PERIODS:
        raise ValueError(f"period must be one of: {', '.join(PERIODS)}")
    return f"{FEED_BASE_URL}/{period}/{feed_slug(language)}.xml"


def _published_at(channel: ET.Element) -> datetime | None:
    text = channel.findtext("pubDate")
    if not text:
        return None
    try:
        return parsedate_to_datetime(text).astimezone(UTC)
    except (TypeError, ValueError):
        return None


def parse_feed(text: str) -> tuple[list[str], datetime | None]:
    """Repository names in feed order, read from each item's GitHub link, and the publish time."""
    try:
        root = ET.fromstring(text)
    except ET.ParseError as error:
        raise TrendingFeedError(f"Trending feed is not valid XML: {error}") from error
    channel = root.find("channel")
    if channel is None:
        raise TrendingFeedError("Trending feed has no channel")
    names: list[str] = []
    for item in channel.iter("item"):
        match = REPO_LINK.match((item.findtext("link") or "").strip())
        if match and match.group(1) not in names:
            names.append(match.group(1))
    return names, _published_at(channel)


def _utc_now() -> datetime:
    return datetime.now(UTC)


def fetch_trending(
    period: str,
    language: str | None,
    session: requests.Session | None = None,
    clock: Callable[[], datetime] = _utc_now,
) -> TrendingFeed:
    url = feed_url(period, language)
    try:
        response = (session or requests).get(url, timeout=REQUEST_TIMEOUT)
    except requests.RequestException as error:
        raise TrendingFeedError(f"Could not reach {url}") from error
    if not response.ok:
        raise TrendingFeedError(f"{url} returned {response.status_code}")
    names, published_at = parse_feed(response.text)
    return TrendingFeed(names, url, clock(), published_at)
