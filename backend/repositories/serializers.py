"""JSON shape of one repository on the repository page."""

from datetime import UTC, datetime
from typing import Any

from repositories.brief import (
    INTEREST_WINDOW_DAYS,
    BriefAnswer,
    interest,
    issue_response,
    maintainer_concentration,
    maintenance,
    relative_change,
    release_pace,
)
from repositories.models import Repository, StarWeek
from repositories.services import (
    StarPoint,
    is_star_spike,
    stars_gained,
    stars_gained_previous,
)

REPOSITORY_FIELDS = (
    "description",
    "language",
    "owner_type",
    "archived",
    "stars",
    "forks",
    "open_issues",
    "pushed_at",
)
GAIN_FIELDS = ("stars_gained_7d", "stars_gained_30d", "stars_gained_year")
# Not collected yet: null in the JSON, "N/A" in the UI, never 0.
UNSTORED_FIELDS = ("commit_activity", "contributors", "releases", "issues", "pull_requests")
STATUS_SOURCE = "Computed from pushed_at and releases (F2 status rule)"

Origin = dict[str, Any] | None


def _star_week(week: StarWeek) -> dict[str, Any]:
    return {
        "week_start": week.week_start,
        "stars_gained": week.stars_gained,
        "days": week.days,
        "source": week.source,
        "fetched_at": week.fetched_at,
    }


def _origin(source: str, fetched_at: datetime | None) -> Origin:
    return {"source": source, "fetched_at": fetched_at}


def _origins(repo: Repository, newest_week: StarWeek | None) -> dict[str, Origin]:
    """Where each value came from. Releases are read in the same refresh as the repository."""
    fetched = _origin(repo.source, repo.fetched_at)
    origins: dict[str, Origin] = dict.fromkeys(REPOSITORY_FIELDS, fetched)
    origins["newest_release_at"] = _origin(f"/repos/{repo.full_name}/releases", repo.fetched_at)
    origins["status"] = _origin(STATUS_SOURCE, repo.fetched_at)
    history = None
    if newest_week is not None:
        history = _origin(newest_week.source, repo.star_history_fetched_at)
    origins.update(dict.fromkeys(GAIN_FIELDS, history))
    origins.update(dict.fromkeys(UNSTORED_FIELDS, None))
    return origins


def _provenance(values: dict[str, Any], origins: dict[str, Origin]) -> dict[str, Origin]:
    """A null value has no source, so its provenance is null too (F6 P1)."""
    return {field: None if values[field] is None else origin for field, origin in origins.items()}


def serialize_brief_answer(answer: BriefAnswer | None) -> dict[str, str] | None:
    return None if answer is None else {"tone": answer.tone, "value": answer.value}


def _interest(repo: Repository, weeks: list[StarWeek]) -> dict[str, Any] | None:
    """Stars in the last 15 days against the 15 before, from the day history was fetched."""
    if repo.star_history_fetched_at is None:
        return None
    as_of = repo.star_history_fetched_at.astimezone(UTC).date()
    points = [StarPoint(week.week_start, week.days) for week in weeks]
    spike = is_star_spike(
        repo.stars_gained_7d, repo.forks_count, repo.open_issues_count, repo.stargazers_count
    )
    recent = stars_gained(points, as_of, INTEREST_WINDOW_DAYS)
    previous = stars_gained_previous(points, as_of, INTEREST_WINDOW_DAYS)
    serialized = serialize_brief_answer(interest(recent, previous, repo.stargazers_count, spike))
    if serialized is None or previous is None:
        return None
    return {
        **serialized,
        "window_days": INTEREST_WINDOW_DAYS,
        "recent": recent,
        "previous": previous,
        "change": relative_change(recent, previous),
    }


def _brief(repo: Repository, weeks: list[StarWeek], now: datetime) -> dict[str, Any]:
    """Inputs we don't store yet are passed as None, so those answers stay null."""
    answers = {
        "maintenance": maintenance(None, None),
        "issue_response": issue_response(None, None),
        "release_pace": release_pace(None, now),
        "maintainer_concentration": maintainer_concentration(None),
    }
    serialized = {question: serialize_brief_answer(answer) for question, answer in answers.items()}
    return {"interest": _interest(repo, weeks), **serialized}


def serialize_detail(repo: Repository, now: datetime) -> dict[str, Any]:
    """Keep missing values as null so the page can show N/A, never 0."""
    owner, name = repo.full_name.split("/", 1)
    weeks = list(repo.star_weeks.order_by("week_start"))
    values: dict[str, Any] = {
        "full_name": repo.full_name,
        "owner": owner,
        "name": name,
        "description": repo.description,
        "language": repo.language,
        "owner_type": repo.owner_type,
        "archived": repo.archived,
        "stars": repo.stargazers_count,
        "forks": repo.forks_count,
        "open_issues": repo.open_issues_count,
        "pushed_at": repo.pushed_at,
        "newest_release_at": repo.newest_release_at,
        "status": repo.status,
        "stars_gained_7d": repo.stars_gained_7d,
        "stars_gained_30d": repo.stars_gained_30d,
        "stars_gained_year": repo.stars_gained_year,
        **dict.fromkeys(UNSTORED_FIELDS, None),
    }
    origins = _origins(repo, weeks[-1] if weeks else None)
    return {
        **values,
        "star_history": [_star_week(week) for week in weeks],
        "provenance": _provenance(values, origins),
        "brief": _brief(repo, weeks, now),
    }
