"""Serve a repository from the database, fetching it through the GitHub client when needed."""

from datetime import datetime, timedelta

from github_client import GitHubClient

from repositories.ingest import refresh_details, upsert_repository
from repositories.models import Repository

CACHE_TTL = timedelta(hours=24)


def get_or_fetch(client: GitHubClient, owner: str, name: str, now: datetime) -> Repository:
    cached = Repository.objects.filter(full_name__iexact=f"{owner}/{name}").first()
    if cached is not None and now - cached.fetched_at < CACHE_TTL:
        return cached
    response = client.get(f"/repos/{owner}/{name}")
    repo = upsert_repository(response.data, response.source, response.fetched_at)
    refresh_details(client, repo, now, ranked=False)
    return repo
