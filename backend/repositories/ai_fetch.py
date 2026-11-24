"""Keep each repository's F4 AI capabilities scan fresh."""

from datetime import datetime, timedelta

from ai_capabilities.scan import scan_repository
from github_client import GitHubClient, GitHubError

from repositories.models import Repository

REPORT_TTL = timedelta(hours=24)  # opening a report rescans after a day
DAILY_JOB_TTL = timedelta(days=7)  # the daily job rescans weekly: skills change slowly


def ai_is_stale(repo: Repository, now: datetime, ttl: timedelta = REPORT_TTL) -> bool:
    return repo.ai_fetched_at is None or now - repo.ai_fetched_at >= ttl


def refresh_ai(client: GitHubClient, repo: Repository, now: datetime) -> None:
    """Scan and store the panel. Raises GitHubError; the old panel stays if the scan fails."""
    branch = repo.raw.get("default_branch") or "main"
    repo.ai = scan_repository(client, repo.full_name, branch, repo.owner_type)
    repo.ai_fetched_at = now
    repo.save(update_fields=["ai", "ai_fetched_at"])


def refresh_ai_quietly(client: GitHubClient, repo: Repository, now: datetime) -> bool:
    """For a web request: a failed scan leaves the page working. Returns whether it worked."""
    try:
        refresh_ai(client, repo, now)
    except GitHubError:
        return False
    return True
