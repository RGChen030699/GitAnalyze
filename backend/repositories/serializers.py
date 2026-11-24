"""JSON shape of one repository on the repository page."""

from typing import Any

from repositories.models import Repository, StarWeek


def _star_week(week: StarWeek) -> dict[str, Any]:
    return {
        "week_start": week.week_start,
        "stars_gained": week.stars_gained,
        "days": week.days,
        "source": week.source,
        "fetched_at": week.fetched_at,
    }


def serialize_detail(repo: Repository) -> dict[str, Any]:
    """Keep missing values as null so the page can show N/A, never 0."""
    owner, name = repo.full_name.split("/", 1)
    return {
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
        "star_history": [_star_week(week) for week in repo.star_weeks.order_by("week_start")],
    }
