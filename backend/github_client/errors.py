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
    """GitHub rate limited the request, or the client chose not to wait (C3, C4)."""

    def __init__(
        self, message: str, status_code: int | None = None, reset_at: int | None = None
    ) -> None:
        super().__init__(message, status_code=status_code)
        self.reset_at = reset_at


class ForbiddenEndpointError(GitHubError):
    """The path targets an endpoint the client must never call (C10)."""
