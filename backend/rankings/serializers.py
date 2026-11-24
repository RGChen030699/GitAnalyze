"""JSON shape of one repository in the rankings API."""

from typing import Any

from repositories.models import Repository
from repositories.trending import WEEKLY_ALL


def trending_rank(repo: Repository, key: str | None = None) -> int | None:
    """Rank in the Trending list being viewed; elsewhere, the weekly overall rank (F8 G5 badge)."""
    ranks: dict[str, int] = repo.trending or {}
    return ranks.get(key) if key is not None else ranks.get(WEEKLY_ALL)


def serialize_row(repo: Repository, trending_key: str | None = None) -> dict[str, Any]:
    """Keep missing values as null so the page can show N/A, never 0."""
    owner, name = repo.full_name.split("/", 1)
    return {
        "full_name": repo.full_name,
        "owner": owner,
        "name": name,
        "description": repo.description,
        "language": repo.language,
        "owner_type": repo.owner_type,
        "stars": repo.stargazers_count,
        "forks": repo.forks_count,
        "open_issues": repo.open_issues_count,
        "status": repo.status,
        "pushed_at": repo.pushed_at,
        "stars_gained_7d": repo.stars_gained_7d,
        "stars_gained_30d": repo.stars_gained_30d,
        "stars_gained_year": repo.stars_gained_year,
        "weeks_12": repo.weeks_12,
        "contributors": None,
        "ai": repo.ai["has_ai"] if repo.ai else None,  # F4: null until scanned
        "spike": None,
        "trending": trending_rank(repo, trending_key),
        "source": repo.source,
        "fetched_at": repo.fetched_at,
    }
