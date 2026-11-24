"""The single module through which all GitHub access goes (PRD F0)."""

from .client import GitHubClient
from .errors import ForbiddenEndpointError, GitHubError, MissingTokenError, RateLimitError
from .search import search_repositories
from .types import GitHubResponse

__all__ = [
    "ForbiddenEndpointError",
    "GitHubClient",
    "GitHubError",
    "GitHubResponse",
    "MissingTokenError",
    "RateLimitError",
    "search_repositories",
]
