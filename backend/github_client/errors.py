"""Errors raised by the GitHub client."""


class GitHubError(Exception):
    """A GitHub request failed."""

    def __init__(self, message: str, status_code: int | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code


class MissingTokenError(GitHubError):
    """GITHUB_TOKEN is not configured (C1)."""

    def __init__(self) -> None:
        super().__init__("GITHUB_TOKEN is not set")


class RateLimitError(GitHubError):
    """GitHub kept rate limiting the request after all attempts (C4)."""


class ForbiddenEndpointError(GitHubError):
    """The path targets an endpoint the client must never call (C10)."""
