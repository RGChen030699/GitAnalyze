"""Fetch F2 health data when a report opens, and keep it for 24 hours.

The daily ranking refresh doesn't do this: about 4 more requests for each of 1,000 repositories
wouldn't fit in 5,000 requests an hour. A report open costs at most 4 requests, once a day.
"""

from collections.abc import Callable
from datetime import datetime, timedelta
from typing import Any

from github_client import GitHubClient, GitHubError, GitHubResponse
from health.services import PENDING, contributor_commits, contributor_count

from repositories.models import Repository

HEALTH_TTL = timedelta(hours=24)
TAGS_PAGE_SIZE = 100

Part = dict[str, Any]


def health_is_stale(repo: Repository, now: datetime) -> bool:
    """Missing, older than 24 hours, or a part GitHub was still calculating last time."""
    return repo.health_fetched_at is None or now - repo.health_fetched_at >= HEALTH_TTL


def _origin(response: GitHubResponse) -> Part:
    return {"source": response.source, "fetched_at": response.fetched_at.isoformat()}


def _commit_activity(client: GitHubClient, repo: Repository, now: datetime) -> Part:
    response = client.get(f"/repos/{repo.full_name}/stats/commit_activity")
    if response.status == PENDING:
        return {"status": PENDING, "weeks": [], **_origin(response)}
    return {"status": "ok", "weeks": list(response.data or []), **_origin(response)}


def _contributor_commits(client: GitHubClient, repo: Repository, now: datetime) -> Part:
    response = client.get(f"/repos/{repo.full_name}/stats/contributors")
    if response.status == PENDING:
        return {"status": PENDING, "commits": {}, **_origin(response)}
    commits = contributor_commits(list(response.data or []), now)
    return {"status": "ok", "commits": commits, **_origin(response)}


def _contributors(client: GitHubClient, repo: Repository, now: datetime) -> Part:
    params = {"per_page": 1, "anon": 1}
    response = client.get(f"/repos/{repo.full_name}/contributors", params=params)
    listed = len(response.data) if isinstance(response.data, list) else 0
    return {"count": contributor_count(response.last_page, listed), **_origin(response)}


def _tags(client: GitHubClient, repo: Repository, now: datetime) -> Part:
    response = client.get(f"/repos/{repo.full_name}/tags", params={"per_page": TAGS_PAGE_SIZE})
    names = [{"name": tag["name"]} for tag in response.data or []]
    return {"items": names, **_origin(response)}


Fetcher = Callable[[GitHubClient, Repository, datetime], Part]
PARTS: dict[str, Fetcher] = {
    "commit_activity": _commit_activity,
    "contributor_commits": _contributor_commits,
    "contributors": _contributors,
}


def refresh_health(client: GitHubClient, repo: Repository, now: datetime) -> list[str]:
    """Fetch each part; return the names that failed. A failed part keeps its old value.

    Parts still pending leave ``health_fetched_at`` empty, so the next open tries again.
    """
    previous: dict[str, Part] = dict(repo.health or {})
    fetchers = dict(PARTS)
    if not repo.releases:
        fetchers["tags"] = _tags  # F2 V2: tags only matter when there are no releases
    health: dict[str, Part] = {}
    failed: list[str] = []
    for name, fetch in fetchers.items():
        try:
            health[name] = fetch(client, repo, now)
        except GitHubError:
            failed.append(name)
            if name in previous:
                health[name] = previous[name]
    pending = any(part.get("status") == PENDING for part in health.values())
    repo.health = health
    repo.health_fetched_at = None if pending else now
    repo.save(update_fields=["health", "health_fetched_at"])
    return failed
