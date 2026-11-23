"""HTTP client for the GitHub REST API."""

import logging
import time
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any, Literal
from urllib.parse import quote, unquote, urlsplit

import requests
from django.conf import settings

from .errors import ForbiddenEndpointError, GitHubError, MissingTokenError, RateLimitError
from .etag_store import CachedResponse, ETagStore, InMemoryETagStore
from .types import GitHubResponse

logger = logging.getLogger(__name__)

API_BASE_URL = "https://api.github.com"
RAW_BASE_URL = "https://raw.githubusercontent.com"
API_VERSION = "2022-11-28"
REQUEST_TIMEOUT = (5, 30)  # connect, read (seconds)

DEFAULT_RATE_LIMIT_MARGIN = 200
DEFAULT_SEARCH_RATE_LIMIT_MARGIN = 2
CORE_RESOURCE = "core"
SEARCH_RESOURCE = "search"
MAX_RATE_LIMIT_ATTEMPTS = 5
DEFAULT_RETRY_SECONDS = 60
STATS_RETRY_WAITS = (2, 4, 8, 16, 32)

_ALLOWED_AFTER_STARGAZERS = {"history", "count"}


@dataclass(frozen=True)
class _Quota:
    remaining: int
    reset_at: int


def _utc_now() -> datetime:
    return datetime.now(UTC)


def _resource_for(path: str) -> str:
    return SEARCH_RESOURCE if urlsplit(path).path.startswith("/search/") else CORE_RESOURCE


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


def _skip_netrc(request: requests.PreparedRequest) -> requests.PreparedRequest:
    """Passed as ``auth`` so a ~/.netrc entry cannot replace or add credentials."""
    return request


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
        etag_store: ETagStore | None = None,
        search_rate_limit_margin: int = DEFAULT_SEARCH_RATE_LIMIT_MARGIN,
        wait_for_rate_limit: bool = True,
    ) -> None:
        self._etag_store: ETagStore = etag_store or InMemoryETagStore()
        self._session = session or requests.Session()
        self._clock = clock
        self._sleep = sleep
        self._rate_limit_margin = rate_limit_margin
        self._search_rate_limit_margin = search_rate_limit_margin
        self._wait_for_rate_limit = wait_for_rate_limit
        self._quotas: dict[str, _Quota] = {}

    def get(self, path: str, params: Mapping[str, Any] | None = None) -> GitHubResponse:
        """GET an API path such as ``/repos/owner/name``."""
        _check_path(path)
        token: str = settings.GITHUB_TOKEN
        if not token:
            raise MissingTokenError()

        url = f"{API_BASE_URL}{path}"
        cache_key = requests.Request("GET", url, params=params).prepare().url or url
        cached = self._etag_store.get(cache_key)
        headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": API_VERSION,
            "Authorization": f"Bearer {token}",
        }
        if cached is not None:
            headers["If-None-Match"] = cached.etag

        resource = _resource_for(path)
        cost = 0
        rate_limit_attempts = 0
        stats_retries = 0
        while True:
            self._pause_if_near_limit(resource, path)
            response = self._send(url, params=params, headers=headers)
            self._record_rate_limit(response, resource)

            if response.status_code == 304 and cached is not None:
                return GitHubResponse(
                    data=cached.data,
                    source=path,
                    fetched_at=self._clock(),
                    cost=cost + len(response.history),  # the 304 itself is free
                    final_url=cached.final_url,
                    from_cache=True,
                )
            cost += 1 + len(response.history)

            if response.status_code == 202:
                if stats_retries == len(STATS_RETRY_WAITS):
                    return self._result(None, path, cost, response, status="pending")
                self._sleep(STATS_RETRY_WAITS[stats_retries])
                stats_retries += 1
                continue

            if _is_rate_limited(response):
                if not self._wait_for_rate_limit:
                    raise RateLimitError(
                        f"GitHub rate limited {path}",
                        status_code=response.status_code,
                        reset_at=self._reset_time(response),
                    )
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
                delay = self._retry_delay(response, rate_limit_attempts, resource)
                if delay > 0:
                    self._sleep(delay)
                continue

            if not response.ok:
                raise GitHubError(
                    f"GitHub returned {response.status_code} for {path}",
                    status_code=response.status_code,
                )
            data = response.json() if response.content else None
            etag = response.headers.get("ETag")
            if etag:
                self._etag_store.set(cache_key, CachedResponse(etag, data, response.url))
            return self._result(data, path, cost, response)

    def get_raw(self, owner: str, repo: str, ref: str, path: str) -> GitHubResponse:
        """Fetch a public file's text. Uses no API quota and sends no token (C9)."""
        parts = [owner, repo, *ref.split("/"), *path.split("/")]
        if any(part in {"", ".", ".."} for part in parts):
            raise GitHubError(f"Invalid raw file location: {owner}/{repo}@{ref}:{path}")
        url = f"{RAW_BASE_URL}/{'/'.join(quote(part, safe='') for part in parts)}"

        response = self._send(url)
        if not response.ok:
            raise GitHubError(
                f"GitHub returned {response.status_code} for {url}",
                status_code=response.status_code,
            )
        return self._result(response.text, url, 0, response)

    def _send(self, url: str, **kwargs: Any) -> requests.Response:
        try:
            return self._session.get(
                url, timeout=REQUEST_TIMEOUT, allow_redirects=True, auth=_skip_netrc, **kwargs
            )
        except requests.RequestException as error:
            raise GitHubError(f"Could not reach GitHub for {url}") from error

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

    def _record_rate_limit(self, response: requests.Response, resource: str) -> None:
        """Remember the latest quota headers for the response's resource (C3)."""
        remaining = _int_header(response, "x-ratelimit-remaining")
        reset_at = _int_header(response, "x-ratelimit-reset")
        if remaining is not None and reset_at is not None:
            key = response.headers.get("x-ratelimit-resource", resource)
            self._quotas[key] = _Quota(remaining, reset_at)

    def _margin(self, resource: str) -> int:
        if resource == SEARCH_RESOURCE:
            return self._search_rate_limit_margin
        return self._rate_limit_margin

    def _pause_if_near_limit(self, resource: str, path: str) -> None:
        """Wait for the quota reset when below the resource's safety margin (C3)."""
        quota = self._quotas.get(resource)
        if quota is None or quota.remaining >= self._margin(resource):
            return
        wait = quota.reset_at - self._clock().timestamp()
        if wait > 0 and not self._wait_for_rate_limit:
            raise RateLimitError(
                f"GitHub {resource} quota is too low for {path}", reset_at=quota.reset_at
            )
        del self._quotas[resource]
        if wait > 0:
            self._sleep(wait + 1)  # one extra second covers clock skew

    def _reset_time(self, response: requests.Response) -> int | None:
        retry_after = _int_header(response, "retry-after")
        if retry_after is not None:
            return int(self._clock().timestamp()) + max(retry_after, 0)
        return _int_header(response, "x-ratelimit-reset")

    def _retry_delay(self, response: requests.Response, attempt: int, resource: str) -> float:
        """Seconds to wait before retrying a rate-limited request (C4)."""
        retry_after = _int_header(response, "retry-after")
        if retry_after is not None:
            return max(retry_after, 0)
        quota = self._quotas.get(resource)
        if (
            quota is not None
            and quota.remaining < self._margin(resource)
            and quota.reset_at > self._clock().timestamp()
        ):
            return 0  # the pause before the next request already waits for the reset
        return DEFAULT_RETRY_SECONDS * 2 ** (attempt - 1)
