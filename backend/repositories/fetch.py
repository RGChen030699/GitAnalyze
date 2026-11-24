"""Serve a repository from the database, fetching it through the GitHub client when needed."""

from datetime import datetime, timedelta

from github_client import GitHubClient, GitHubError

from repositories.ingest import refresh_details, upsert_repository
from repositories.models import Repository

CACHE_TTL = timedelta(hours=24)


class RepoNotFound(Exception):
    """GitHub has no public repository at this owner/name."""

    def __init__(self, owner: str, name: str) -> None:
        super().__init__(f"We couldn't find a public repository at {owner}/{name}")


def get_or_fetch(client: GitHubClient, owner: str, name: str, now: datetime) -> Repository:
    cached = Repository.objects.filter(full_name__iexact=f"{owner}/{name}").first()
    if cached is not None and now - cached.fetched_at < CACHE_TTL:
        return cached
    try:
        response = client.get(f"/repos/{owner}/{name}")
    except GitHubError as error:
        if error.status_code == 404:
            raise RepoNotFound(owner, name) from error
        raise
    repo = upsert_repository(response.data, response.source, response.fetched_at)
    refresh_details(client, repo, now, ranked=False)
    return repo
