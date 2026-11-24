"""Database queries for the rankings API. These never call GitHub (F7 T7)."""

from typing import Any

from django.db.models import Count, F, Max, QuerySet
from django.db.models.functions import Lower
from repositories.models import Repository

from rankings.params import RankingParams

MAX_LANGUAGES = 15
GAIN_FIELDS = {
    "7d": "stars_gained_7d",
    "30d": "stars_gained_30d",
    "1y": "stars_gained_year",
}


def ranked_repositories() -> QuerySet[Repository]:
    return Repository.objects.filter(ranked_at__isnull=False)


def coverage() -> dict[str, Any]:
    totals = ranked_repositories().aggregate(tracked=Count("id"), updated_at=Max("ranked_at"))
    return {"prepared": totals["tracked"] > 0, **totals}


def language_counts() -> list[dict[str, Any]]:
    rows = (
        ranked_repositories()
        .filter(language__isnull=False)
        .values("language")
        .annotate(count=Count("id"))
        .order_by("-count", "language")[:MAX_LANGUAGES]
    )
    return [{"name": row["language"], "count": row["count"]} for row in rows]


def _filtered(params: RankingParams) -> QuerySet[Repository]:
    repositories = ranked_repositories()
    if params.lang is not None:
        repositories = repositories.filter(language__iexact=params.lang)
    if params.status is not None:
        repositories = repositories.filter(status=params.status)
    if params.archived is not None:
        repositories = repositories.filter(archived=params.archived)
    return repositories


def _sort_field(params: RankingParams) -> str:
    if params.sort == "gained":
        return GAIN_FIELDS[params.window]
    if params.sort == "pushed":
        return "pushed_at"
    return "stargazers_count"


def ordered_repositories(params: RankingParams) -> QuerySet[Repository]:
    if params.sort == "trending" or params.trending_only:
        return Repository.objects.none()  # F8: no trending data is stored yet
    field = _sort_field(params)
    return _filtered(params).order_by(F(field).desc(nulls_last=True), Lower("full_name"))
