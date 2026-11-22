"""HTTP client for the GitHub REST API."""

import logging
import time
from collections.abc import Callable, Mapping
from datetime import UTC, datetime
from typing import Any, Literal
from urllib.parse import unquote, urlsplit

import requests
from django.conf import settings

from .errors import ForbiddenEndpointError, GitHubError, MissingTokenError, RateLimitError
from .types import GitHubResponse

logger = logging.getLogger(__name__)

API_BASE_URL = "https://api.github.com"
API_VERSION = "2022-11-28"
REQUEST_TIMEOUT = (5, 30)  # connect, read (seconds)

DEFAULT_RATE_LIMIT_MARGIN = 200
MAX_RATE_LIMIT_ATTEMPTS = 5
DEFAULT_RETRY_SECONDS = 60
STATS_RETRY_WAITS = (2, 4, 8, 16, 32)

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


def _int_header(response: requests.Response, name: str) -> int | None:
    try:
        return int(response.headers[name])
    except (KeyError, ValueError):
        return None


def _is_rate_limited(response: requests.Response) -> bool:
    """A 429 always is; a 403 only with a rate-limit signal, else it is a permissions error."""
    if response.status_code == 429:
        return True
    if response.status_code != 403:
        return False
    return (
        "retry-after" in response.headers
        or _int_header(response, "x-ratelimit-remaining") == 0
        or "rate limit" in response.text.lower()
    )


class GitHubClient:
    """Reads from GitHub and returns data with its provenance."""

    def __init__(
        self,
        session: requests.Session | None = None,
        clock: Callable[[], datetime] = _utc_now,
        sleep: Callable[[float], None] = time.sleep,
        rate_limit_margin: int = DEFAULT_RATE_LIMIT_MARGIN,
    ) -> None:
        self._session = session or requests.Session()
        self._clock = clock
        self._sleep = sleep
        self._rate_limit_margin = rate_limit_margin
        self._remaining: int | None = None
        self._reset_at: int | None = None

    def get(self, path: str, params: Mapping[str, Any] | None = None) -> GitHubResponse:
        """GET an API path such as ``/repos/owner/name``."""
        _check_path(path)
        token: str = settings.GITHUB_TOKEN
        if not token:
            raise MissingTokenError()

        cost = 0
        rate_limit_attempts = 0
        stats_retries = 0
        while True:
            self._pause_if_near_limit()
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
            cost += 1 + len(response.history)
            self._record_rate_limit(response)

            if response.status_code == 202:
                if stats_retries == len(STATS_RETRY_WAITS):
                    return self._result(None, path, cost, response, status="pending")
                self._sleep(STATS_RETRY_WAITS[stats_retries])
                stats_retries += 1
                continue

            if _is_rate_limited(response):
                rate_limit_attempts += 1
                if rate_limit_attempts >= MAX_RATE_LIMIT_ATTEMPTS:
                    logger.error(
                        "GitHub rate limit: giving up on %s after %d tries",
                        path,
                        rate_limit_attempts,
                    )
                    raise RateLimitError(
                        f"GitHub kept rate limiting {path} after {rate_limit_attempts} tries",
                        status_code=response.status_code,
                    )
                delay = self._retry_delay(response, rate_limit_attempts)
                if delay > 0:
                    self._sleep(delay)
                continue

            if not response.ok:
                raise GitHubError(
                    f"GitHub returned {response.status_code} for {path}",
                    status_code=response.status_code,
                )
            data = response.json() if response.content else None
            return self._result(data, path, cost, response)

    def _result(
        self,
        data: Any,
        path: str,
        cost: int,
        response: requests.Response,
        status: Literal["ok", "pending"] = "ok",
    ) -> GitHubResponse:
        return GitHubResponse(
            data=data,
            source=path,
            fetched_at=self._clock(),
            cost=cost,
            final_url=response.url,
            status=status,
        )

    def _record_rate_limit(self, response: requests.Response) -> None:
        """Remember the latest quota headers (C3)."""
        remaining = _int_header(response, "x-ratelimit-remaining")
        reset_at = _int_header(response, "x-ratelimit-reset")
        if remaining is not None and reset_at is not None:
            self._remaining = remaining
            self._reset_at = reset_at

    def _pause_if_near_limit(self) -> None:
        """Wait for the quota reset when below the safety margin (C3)."""
        if self._remaining is None or self._reset_at is None:
            return
        if self._remaining >= self._rate_limit_margin:
            return
        wait = self._reset_at - self._clock().timestamp()
        self._remaining = None
        self._reset_at = None
        if wait > 0:
            self._sleep(wait + 1)  # one extra second covers clock skew

    def _retry_delay(self, response: requests.Response, attempt: int) -> float:
        """Seconds to wait before retrying a rate-limited request (C4)."""
        retry_after = _int_header(response, "retry-after")
        if retry_after is not None:
            return max(retry_after, 0)
        if (
            self._remaining is not None
            and self._reset_at is not None
            and self._remaining < self._rate_limit_margin
            and self._reset_at > self._clock().timestamp()
        ):
            return 0  # the pause before the next request already waits for the reset
        return DEFAULT_RETRY_SECONDS * 2 ** (attempt - 1)
