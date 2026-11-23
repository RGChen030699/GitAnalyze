"""Repository search through the GitHub client."""

from dataclasses import replace
from urllib.parse import urlencode

from .client import GitHubClient
from .types import GitHubResponse

SEARCH_PATH = "/search/repositories"
MAX_PER_PAGE = 100


def search_repositories(client: GitHubClient, query: str, per_page: int) -> GitHubResponse:
    """Fetch one page of repositories, most stars first, with the query in ``source`` (C8)."""
    if not 1 <= per_page <= MAX_PER_PAGE:
        raise ValueError(f"per_page must be between 1 and {MAX_PER_PAGE}")
    params = {"q": query, "sort": "stars", "order": "desc", "per_page": per_page}
    response = client.get(SEARCH_PATH, params=params)
    return replace(response, source=f"{SEARCH_PATH}?{urlencode(params)}")
