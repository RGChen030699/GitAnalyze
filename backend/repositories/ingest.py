"""Fetch repository details through the GitHub client and store them."""

from dataclasses import dataclass
from datetime import UTC, date, datetime
from typing import Any

from django.db import transaction
from django.utils.dateparse import parse_datetime
from github_client import GitHubClient, GitHubError, GitHubResponse
from health.services import compute_status

from repositories.models import Repository, StarWeek
from repositories.services import (
    StarPoint,
    cap_gain,
    stars_gained,
    stars_gained_year,
    weeks_12,
)

STAR_HISTORY_ENABLED = True  # F7 Step 1: verified live on 2026-11-23
HISTORY_PAGE_SIZE = 30
RELEASES_PAGE_SIZE = 100
DAYS_PER_WEEK = 7
GAIN_FIELDS = ("stars_gained_7d", "stars_gained_30d", "stars_gained_year")


@dataclass(frozen=True)
class _History:
    entries: list[dict[str, Any]]
    source: str
    fetched_at: datetime
    complete: bool


def _parse_optional_datetime(value: str | None) -> datetime | None:
    return parse_datetime(value) if value else None


def _cap_gains(repo: Repository) -> bool:
    """Cap stored gains at total stars and return whether any value changed."""
    changed = False
    for field in GAIN_FIELDS:
        gained = getattr(repo, field)
        capped = cap_gain(gained, repo.stargazers_count)
        if capped != gained:
            setattr(repo, field, capped)
            changed = True
    return changed


def upsert_repository(payload: dict[str, Any], source: str, fetched_at: datetime) -> Repository:
    """Save basic fields, matched on GitHub id so a renamed repository keeps its row (C7)."""
    repository, _ = Repository.objects.update_or_create(
        github_id=payload["id"],
        defaults={
            "full_name": payload["full_name"],
            "owner_login": payload["owner"]["login"],
            "owner_type": payload["owner"]["type"],
            "description": payload.get("description"),
            "language": payload.get("language"),
            "archived": payload["archived"],
            "pushed_at": _parse_optional_datetime(payload.get("pushed_at")),
            "stargazers_count": payload["stargazers_count"],
            "forks_count": payload["forks_count"],
            "open_issues_count": payload["open_issues_count"],
            "source": source,
            "fetched_at": fetched_at,
            "raw": payload,
        },
    )
    if _cap_gains(repository):
        repository.save(update_fields=GAIN_FIELDS)
    return repository


def _fetch_list(client: GitHubClient, path: str, params: dict[str, int]) -> GitHubResponse:
    response = client.get(path, params=params)
    if response.status != "ok" or not isinstance(response.data, list):
        raise GitHubError(f"GitHub returned no list for {path}")
    return response


def _fetch_newest_release(client: GitHubClient, full_name: str) -> datetime | None:
    response = _fetch_list(client, f"/repos/{full_name}/releases", {"per_page": RELEASES_PAGE_SIZE})
    published = [
        parse_datetime(release["published_at"])
        for release in response.data
        if not release.get("draft") and release.get("published_at")
    ]
    return max((moment for moment in published if moment is not None), default=None)


def _fetch_history_page(client: GitHubClient, full_name: str, page: int) -> GitHubResponse:
    params = {"per_page": HISTORY_PAGE_SIZE, "page": page}
    return _fetch_list(client, f"/repos/{full_name}/stargazers/history", params)


def _fetch_history(client: GitHubClient, full_name: str) -> _History:
    first = _fetch_history_page(client, full_name, 1)
    entries = list(first.data)
    complete = len(entries) < HISTORY_PAGE_SIZE
    if not complete:
        try:
            entries += _fetch_history_page(client, full_name, 2).data
            complete = True
        except GitHubError:
            pass
    return _History(entries, first.source, first.fetched_at, complete)


def _week_start(timestamp: int) -> date:
    return datetime.fromtimestamp(timestamp, UTC).date()


def _star_week(repo: Repository, entry: dict[str, Any], history: _History) -> StarWeek:
    if len(entry["days"]) != DAYS_PER_WEEK:
        raise ValueError(f"Expected {DAYS_PER_WEEK} days in star history for {repo.full_name}")
    return StarWeek(
        repository=repo,
        week_start=_week_start(entry["week"]),
        stars_gained=entry["total"],
        days=entry["days"],
        source=history.source,
        fetched_at=history.fetched_at,
    )


def _store_history(repo: Repository, history: _History, now: datetime) -> None:
    StarWeek.objects.bulk_create(
        [_star_week(repo, entry, history) for entry in history.entries],
        update_conflicts=True,
        unique_fields=["repository", "week_start"],
        update_fields=["stars_gained", "days", "source", "fetched_at"],
    )
    points = [StarPoint(week.week_start, week.days) for week in repo.star_weeks.all()]
    as_of = now.astimezone(UTC).date()
    repo.stars_gained_7d = stars_gained(points, as_of, 7)
    repo.stars_gained_30d = stars_gained(points, as_of, 30)
    repo.weeks_12 = weeks_12(points, as_of)
    repo.star_history_fetched_at = history.fetched_at
    if history.complete:
        repo.stars_gained_year = stars_gained_year(points, as_of)
    _cap_gains(repo)


def refresh_details(client: GitHubClient, repo: Repository, now: datetime) -> list[str]:
    """Refresh releases and star history, and return the names of the parts that failed."""
    failed: list[str] = []
    releases_known = True
    newest_release_at = repo.newest_release_at
    try:
        newest_release_at = _fetch_newest_release(client, repo.full_name)
    except GitHubError:
        releases_known = False
        failed.append("releases")

    history: _History | None = None
    if STAR_HISTORY_ENABLED:
        try:
            history = _fetch_history(client, repo.full_name)
        except GitHubError:
            failed.append("star history")
        if history is not None and not history.complete:
            failed.append("star history page 2")

    with transaction.atomic():
        if history is not None:
            _store_history(repo, history, now)
        repo.newest_release_at = newest_release_at
        repo.status = compute_status(
            repo.archived, repo.pushed_at, newest_release_at, releases_known, now
        )
        repo.ranked_at = now
        repo.save()
    return failed
