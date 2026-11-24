"""Database queries for the rankings API. These never call GitHub (F7 T7)."""

from django.db.models import F, QuerySet
from django.db.models.functions import Lower
from repositories.models import Repository

from rankings.params import RankingParams

GAIN_FIELDS = {
    "7d": "stars_gained_7d",
    "30d": "stars_gained_30d",
    "1y": "stars_gained_year",
}


def ranked_repositories() -> QuerySet[Repository]:
    return Repository.objects.filter(ranked_at__isnull=False)


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
