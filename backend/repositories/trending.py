"""Store GitHub Trending ranks on repositories (F8 G4)."""

from collections.abc import Mapping
from datetime import datetime

from django.db import transaction
from django.db.models import Q

from repositories.models import Repository

ALL_KEY = "all"

Ranks = Mapping[str, Mapping[int, int]]  # feed key ("all" or a language) -> repository id -> rank


def _merged(current: dict[str, int] | None, repo_id: int, ranks: Ranks) -> dict[str, int] | None:
    """Replace the ranks of the feeds that answered; keep the others as they were."""
    kept = {key: rank for key, rank in (current or {}).items() if key not in ranks}
    for key, listed in ranks.items():
        if repo_id in listed:
            kept[key] = listed[repo_id]
    return kept or None


def apply_weekly_ranks(ranks: Ranks, now: datetime) -> None:
    """Pass only the feeds that were read: an unreachable feed keeps yesterday's ranks."""
    listed_ids = {repo_id for listed in ranks.values() for repo_id in listed}
    candidates = Repository.objects.filter(Q(trending__isnull=False) | Q(id__in=listed_ids))
    with transaction.atomic():
        for repo in candidates:
            repo.trending = _merged(repo.trending, repo.id, ranks)
            if repo.id in ranks.get(ALL_KEY, {}):
                repo.trending_at = now
            repo.save(update_fields=["trending", "trending_at"])
