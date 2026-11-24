"""Refresh the stored rankings from GitHub (F0 §3.4, F7)."""

from argparse import ArgumentParser
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from config.languages import normalize_languages
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import IntegrityError
from django.utils import timezone
from github_client import GitHubClient, GitHubError, search_repositories

from repositories.ingest import refresh_details, upsert_repository
from repositories.services import OVERALL_QUERY, build_watch_list, language_query

TOP_OVERALL = 100
TOP_PER_LANGUAGE = 50
REPOSITORY_ERRORS = (GitHubError, IntegrityError, KeyError, TypeError, ValueError)


@dataclass(frozen=True)
class _SearchPage:
    items: list[dict[str, Any]]
    source: str
    fetched_at: datetime


def _selected_languages(values: list[str] | None) -> tuple[str, ...]:
    if values is None:
        return tuple(settings.RANKINGS_LANGUAGES)
    if any(not value.strip() for value in values):
        raise CommandError("--language cannot be blank")
    return normalize_languages(values)


def _checked_limit(limit: int | None) -> int | None:
    if limit is not None and limit < 1:
        raise CommandError("--limit must be a positive number")
    return limit


def _search_page(client: GitHubClient, query: str, per_page: int) -> _SearchPage:
    response = search_repositories(client, query, per_page)
    return _SearchPage(response.data["items"], response.source, response.fetched_at)


def _search_all(
    client: GitHubClient, languages: tuple[str, ...]
) -> tuple[_SearchPage, list[_SearchPage]]:
    try:
        overall = _search_page(client, OVERALL_QUERY, TOP_OVERALL)
        by_language = [
            _search_page(client, language_query(language), TOP_PER_LANGUAGE)
            for language in languages
        ]
    except (GitHubError, KeyError, TypeError) as error:
        raise CommandError(f"Search failed, no changes were saved: {error}") from error
    return overall, by_language


def _first_page_by_id(pages: list[_SearchPage]) -> dict[int, _SearchPage]:
    origins: dict[int, _SearchPage] = {}
    for page in pages:
        for item in page.items:
            origins.setdefault(item["id"], page)
    return origins


class Command(BaseCommand):
    help = "Refresh stored repositories, star history, and status from GitHub."

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument(
            "--language",
            action="append",
            dest="languages",
            metavar="NAME",
            help="Language to search. Repeat it to replace RANKINGS_LANGUAGES for this run.",
        )
        parser.add_argument("--limit", type=int, help="Keep only the N most-starred repositories.")

    def handle(self, *args: Any, **options: Any) -> None:
        languages = _selected_languages(options["languages"])
        limit = _checked_limit(options["limit"])
        client = GitHubClient(clock=timezone.now)
        now = timezone.now()
        overall, by_language = _search_all(client, languages)
        origins = _first_page_by_id([overall, *by_language])
        watch_list = build_watch_list(overall.items, [page.items for page in by_language], limit)

        saved = failures = 0
        for item in watch_list:
            was_saved, failed = self._refresh_one(client, item, origins[item["id"]], now)
            saved += was_saved
            failures += failed
        self.stdout.write(
            f"Refreshed {saved} repositories, {client.requests_sent} requests used, "
            f"{failures} failures"
        )

    def _refresh_one(
        self, client: GitHubClient, item: dict[str, Any], page: _SearchPage, now: datetime
    ) -> tuple[bool, bool]:
        """Return whether the row was saved and whether any part failed."""
        saved = False
        try:
            repository = upsert_repository(item, page.source, page.fetched_at)
            saved = True
            failed_parts = refresh_details(client, repository, now)
        except REPOSITORY_ERRORS as error:
            self.stderr.write(f"{item.get('full_name')}: {error}")
            return saved, True
        if failed_parts:
            self.stderr.write(f"{repository.full_name}: could not fetch {', '.join(failed_parts)}")
        return saved, bool(failed_parts)
