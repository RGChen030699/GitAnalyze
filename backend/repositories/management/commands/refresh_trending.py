"""Add GitHub Trending repositories to the watch list and store their ranks (F0 W3, F8 G4).

Runs daily after refresh_rankings. A repository that refresh_rankings already refreshed costs
nothing here; a new one costs about 4 GitHub requests.
"""

from datetime import datetime, timedelta
from typing import Any

import requests
from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import IntegrityError
from django.utils import timezone
from github_client import GitHubClient, GitHubError
from github_client.trending import (
    PERIODS,
    TrendingFeed,
    TrendingFeedError,
    feed_url,
    fetch_trending,
)

from repositories.ingest import refresh_details, upsert_repository
from repositories.models import Repository
from repositories.trending import apply_ranks, rank_key

FRESH_FOR = timedelta(hours=20)  # refreshed by today's refresh_rankings run
REPOSITORY_ERRORS = (GitHubError, IntegrityError, KeyError, TypeError, ValueError)

FeedKey = tuple[str, str | None]  # (period, language or None for all)
Feeds = dict[FeedKey, TrendingFeed]


def _feed_keys(languages: tuple[str, ...]) -> list[FeedKey]:
    """Today, this week and this month, overall and for each ranked language."""
    return [(period, language) for period in PERIODS for language in (None, *languages)]


def _unique_names(feeds: Feeds) -> list[str]:
    seen: dict[str, str] = {}
    for feed in feeds.values():
        for name in feed.names:
            seen.setdefault(name.lower(), name)
    return list(seen.values())


def _ranks(feeds: Feeds, ids: dict[str, int]) -> dict[str, dict[int, int]]:
    """GitHub's order, gaps included: a listed repository we couldn't fetch keeps its place."""
    ranks: dict[str, dict[int, int]] = {}
    for (period, language), feed in feeds.items():
        listed = [(rank, name.lower()) for rank, name in enumerate(feed.names, start=1)]
        ranks[rank_key(period, language)] = {ids[n]: rank for rank, n in listed if n in ids}
    return ranks


class Command(BaseCommand):
    help = "Add GitHub Trending repositories to the watch list and store their ranks."

    def handle(self, *args: Any, **options: Any) -> None:
        client = GitHubClient(clock=timezone.now)
        now = timezone.now()
        feeds = self._read_feeds(tuple(settings.RANKINGS_LANGUAGES))
        names = _unique_names(feeds)
        ids: dict[str, int] = {}
        refreshed = failures = 0
        for name in names:
            repo, fetched, failed = self._ensure(client, name, now)
            if repo is not None:
                ids[name.lower()] = repo.id
            refreshed += fetched
            failures += failed
        apply_ranks(_ranks(feeds, ids), now)
        unreachable = len(_feed_keys(tuple(settings.RANKINGS_LANGUAGES))) - len(feeds)
        self.stdout.write(
            f"Trending: {len(names)} repositories from {len(feeds)} feeds, "
            f"{refreshed} added or refreshed, {client.requests_sent} requests used, "
            f"{failures} failures, {unreachable} feeds unreachable"
        )

    def _read_feeds(self, languages: tuple[str, ...]) -> Feeds:
        session = requests.Session()
        feeds: Feeds = {}
        for period, language in _feed_keys(languages):
            try:
                feeds[(period, language)] = fetch_trending(period, language, session, timezone.now)
            except TrendingFeedError:
                self.stderr.write(f"Trending feed unreachable: {feed_url(period, language)}")
        return feeds

    def _ensure(
        self, client: GitHubClient, name: str, now: datetime
    ) -> tuple[Repository | None, bool, bool]:
        """Return the stored repository, whether it was fetched now, and whether anything failed."""
        existing = Repository.objects.filter(full_name__iexact=name).first()
        if existing is not None and existing.ranked_at and now - existing.ranked_at < FRESH_FOR:
            return existing, False, False
        try:
            response = client.get(f"/repos/{name}")
            repo = upsert_repository(response.data, response.source, response.fetched_at)
            failed_parts = refresh_details(client, repo, now)
        except REPOSITORY_ERRORS as error:
            self.stderr.write(f"{name}: {error}")
            return existing, False, True
        if failed_parts:
            self.stderr.write(f"{repo.full_name}: could not fetch {', '.join(failed_parts)}")
        return repo, True, bool(failed_parts)
