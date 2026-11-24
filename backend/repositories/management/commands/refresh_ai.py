"""Scan ranked repositories for AI capabilities (F4), so rankings can filter by them.

Runs daily after refresh_trending. A repository is rescanned when its last scan is older than
7 days: about 170 a day for 1,200 ranked repositories, one API request each. File texts come
through the client's get_raw, which costs no API quota.
"""

from typing import Any

from django.core.management.base import BaseCommand
from django.db.models import Q
from django.utils import timezone
from github_client import GitHubClient, GitHubError

from repositories.ai_fetch import DAILY_JOB_TTL, refresh_ai
from repositories.models import Repository


class Command(BaseCommand):
    help = "Scan ranked repositories not scanned in the last 7 days for AI capabilities."

    def handle(self, *args: Any, **options: Any) -> None:
        client = GitHubClient(clock=timezone.now)
        now = timezone.now()
        stale = Q(ai_fetched_at__isnull=True) | Q(ai_fetched_at__lte=now - DAILY_JOB_TTL)
        repositories = Repository.objects.filter(stale, ranked_at__isnull=False)
        scanned = failures = 0
        for repo in repositories.order_by("ai_fetched_at", "id"):
            try:
                refresh_ai(client, repo, now)
            except GitHubError as error:
                failures += 1
                self.stderr.write(f"{repo.full_name}: {error}")
                continue
            scanned += 1
        self.stdout.write(
            f"AI scan: {scanned} repositories scanned, {client.requests_sent} requests sent, "
            f"{failures} failures"
        )
