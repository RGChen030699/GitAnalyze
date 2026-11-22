"""HTTP client for the GitHub REST API."""

from collections.abc import Callable, Mapping
from datetime import UTC, datetime
from typing import Any
from urllib.parse import unquote, urlsplit

import requests
from django.conf import settings

from .errors import ForbiddenEndpointError, GitHubError, MissingTokenError
from .types import GitHubResponse

API_BASE_URL = "https://api.github.com"
API_VERSION = "2022-11-28"
REQUEST_TIMEOUT = (5, 30)  # connect, read (seconds)

_ALLOWED_AFTER_STARGAZERS = {"history", "count"}


def _utc_now() -> datetime:
    return datetime.now(UTC)


def _check_path(path: str) -> None:
    """Allow only API-relative paths, and never the stargazer list (C10)."""
    if not path.startswith("/") or path.startswith("//"):
        raise GitHubError(f"Expected a path relative to the API root: {path!r}")
    segments = [s.lower() for s in unquote(urlsplit(path).path).split("/") if s]
    for index, segment in enumerate(segments):
        if segment != "stargazers":
            continue
        following = segments[index + 1] if index + 1 < len(segments) else None
        if following not in _ALLOWED_AFTER_STARGAZERS:
            raise ForbiddenEndpointError(f"The stargazer list endpoint is forbidden: {path}")


class GitHubClient:
    """Reads from GitHub and returns data with its provenance."""

    def __init__(
        self,
        session: requests.Session | None = None,
        clock: Callable[[], datetime] = _utc_now,
    ) -> None:
        self._session = session or requests.Session()
        self._clock = clock

    def get(self, path: str, params: Mapping[str, Any] | None = None) -> GitHubResponse:
        """GET an API path such as ``/repos/owner/name``."""
        _check_path(path)
        token: str = settings.GITHUB_TOKEN
        if not token:
            raise MissingTokenError()

        response = self._session.get(
            f"{API_BASE_URL}{path}",
            params=params,
            headers={
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": API_VERSION,
                "Authorization": f"Bearer {token}",
            },
            timeout=REQUEST_TIMEOUT,
            allow_redirects=True,
        )
        cost = 1 + len(response.history)

        if not response.ok:
            raise GitHubError(
                f"GitHub returned {response.status_code} for {path}",
                status_code=response.status_code,
            )
        return GitHubResponse(
            data=response.json() if response.content else None,
            source=path,
            fetched_at=self._clock(),
            cost=cost,
            final_url=response.url,
        )
