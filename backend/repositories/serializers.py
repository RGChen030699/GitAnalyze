"""JSON shape of one repository on the repository page."""

from datetime import UTC, datetime
from typing import Any

from django.utils.dateparse import parse_datetime
from github_client.trending import feed_url
from health.services import (
    PENDING,
    commit_activity_view,
    last_release,
    license_note,
    maintainer_of,
    releases_last_12_months,
)

from repositories.brief import (
    INTEREST_WINDOW_DAYS,
    BriefAnswer,
    interest,
    issue_response,
    maintainer_concentration,
    maintenance,
    people_for_share,
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
from repositories.trending import WEEKLY_ALL

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
# Not collected yet (F9): null in the JSON, "N/A" in the UI, never 0.
UNSTORED_FIELDS = ("issues", "pull_requests")
STATUS_SOURCE = "Computed from pushed_at and releases (F2 status rule)"
TOP_CONTRIBUTORS = 10
COMMIT_WINDOW_WEEKS = 13  # brief "maintenance": 13 weeks against the 13 before

Origin = dict[str, Any] | None
Part = dict[str, Any] | None
CONTRIBUTOR_FIELDS = (
    "single_maintainer",
    "top_contributors",
    "contributors_last_year",
    "commits_last_year",
    "people_for_80",
)


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


def _part_origin(part: Part) -> Origin:
    if part is None:
        return None
    return _origin(part["source"], parse_datetime(part["fetched_at"]))


def _health_origins(repo: Repository) -> dict[str, Origin]:
    health = repo.health or {}
    commits = _part_origin(health.get("contributor_commits"))
    releases = _origin(f"/repos/{repo.full_name}/releases", repo.fetched_at)
    repository = _origin(repo.source, repo.fetched_at)
    return {
        "commit_activity": _part_origin(health.get("commit_activity")),
        "contributors": _part_origin(health.get("contributors")),
        **dict.fromkeys(CONTRIBUTOR_FIELDS, commits),
        **dict.fromkeys(("releases", "last_release", "releases_12m"), releases),
        **dict.fromkeys(("license", "created_at"), repository),
    }


def _origins(repo: Repository, newest_week: StarWeek | None) -> dict[str, Origin]:
    """Where each value came from. Releases are read in the same refresh as the repository."""
    fetched = _origin(repo.source, repo.fetched_at)
    origins: dict[str, Origin] = dict.fromkeys(REPOSITORY_FIELDS, fetched)
    origins["newest_release_at"] = _origin(f"/repos/{repo.full_name}/releases", repo.fetched_at)
    origins.update(_health_origins(repo))
    origins["trending"] = _origin(feed_url("weekly", None), repo.trending_at)
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


def _ready(part: Part) -> bool:
    return part is not None and part.get("status") != PENDING


def _commit_activity(part: Part) -> dict[str, Any] | None:
    if part is None:
        return None
    return commit_activity_view(part["weeks"] if _ready(part) else None)


def _contributor_values(part: Part) -> dict[str, Any]:
    if part is None:
        return dict.fromkeys(CONTRIBUTOR_FIELDS)
    if not _ready(part):
        return {**dict.fromkeys(CONTRIBUTOR_FIELDS), "single_maintainer": PENDING}
    commits: dict[str, int] = part["commits"]
    ranked = sorted(commits.items(), key=lambda item: (-item[1], item[0]))[:TOP_CONTRIBUTORS]
    return {
        "single_maintainer": maintainer_of(commits),
        "top_contributors": [{"login": login, "commits": n} for login, n in ranked],
        "contributors_last_year": len(commits),
        "commits_last_year": sum(commits.values()),
        "people_for_80": people_for_share(list(commits.values())) if commits else None,
    }


def _release_values(repo: Repository, now: datetime) -> dict[str, Any]:
    if repo.releases is None:
        return dict.fromkeys(("releases", "last_release", "releases_12m"))
    tags = ((repo.health or {}).get("tags") or {}).get("items", [])
    listed = sorted(repo.releases, key=lambda release: release["published_at"])
    return {
        "releases": [
            {
                "tag": release["tag_name"],
                "published_at": release["published_at"],
                "prerelease": bool(release.get("prerelease")),
            }
            for release in listed
        ],
        "last_release": last_release(repo.releases, tags),
        "releases_12m": releases_last_12_months(repo.releases, now),
    }


def _license(repo: Repository) -> dict[str, str | None] | None:
    if "license" not in repo.raw:
        return None
    return license_note((repo.raw["license"] or {}).get("spdx_id"))


def _health_values(repo: Repository, now: datetime) -> dict[str, Any]:
    """Health fields are null until fetched, so the page shows N/A, never 0."""
    health = repo.health or {}
    count = health.get("contributors")
    created = repo.raw.get("created_at")
    return {
        "commit_activity": _commit_activity(health.get("commit_activity")),
        "contributors": None if count is None else count["count"],
        **_contributor_values(health.get("contributor_commits")),
        **_release_values(repo, now),
        "license": _license(repo),
        "created_at": parse_datetime(created) if created else None,
    }


def _commit_windows(part: Part) -> tuple[int | None, int | None]:
    if not _ready(part) or part is None or len(part["weeks"]) < 2 * COMMIT_WINDOW_WEEKS:
        return None, None
    totals = [week["total"] for week in sorted(part["weeks"], key=lambda week: week["week"])]
    recent = totals[-COMMIT_WINDOW_WEEKS:]
    previous = totals[-2 * COMMIT_WINDOW_WEEKS : -COMMIT_WINDOW_WEEKS]
    return sum(recent), sum(previous)


def _release_dates(repo: Repository) -> list[datetime] | None:
    """Publish dates of formal releases, prereleases left out (brief "release pace")."""
    if repo.releases is None:
        return None
    dates = [parse_datetime(r["published_at"]) for r in repo.releases if not r.get("prerelease")]
    return [moment for moment in dates if moment is not None]


def _commits_per_person(part: Part) -> list[int] | None:
    return list(part["commits"].values()) if _ready(part) and part is not None else None


def _brief(repo: Repository, weeks: list[StarWeek], now: datetime) -> dict[str, Any]:
    """Inputs we don't store yet are passed as None, so those answers stay null."""
    health = repo.health or {}
    answers = {
        "maintenance": maintenance(*_commit_windows(health.get("commit_activity"))),
        "issue_response": issue_response(None, None),
        "release_pace": release_pace(_release_dates(repo), now),
        "maintainer_concentration": maintainer_concentration(
            _commits_per_person(health.get("contributor_commits"))
        ),
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
        "trending": (repo.trending or {}).get(WEEKLY_ALL),  # F8 G5: weekly overall Trending rank
        **_health_values(repo, now),
        **dict.fromkeys(UNSTORED_FIELDS, None),
    }
    origins = _origins(repo, weeks[-1] if weeks else None)
    return {
        **values,
        "star_history": [_star_week(week) for week in weeks],
        "provenance": _provenance(values, origins),
        "brief": _brief(repo, weeks, now),
    }
