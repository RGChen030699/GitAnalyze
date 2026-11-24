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


def ordered_repositories(params: RankingParams) -> QuerySet[Repository]:
    if params.sort == "trending" or params.trending_only:
        return Repository.objects.none()  # F8: no trending data is stored yet
    field = GAIN_FIELDS[params.window] if params.sort == "gained" else "stargazers_count"
    return ranked_repositories().order_by(F(field).desc(nulls_last=True), Lower("full_name"))
