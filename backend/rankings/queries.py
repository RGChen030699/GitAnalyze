"""Database queries for the rankings API. These never call GitHub (F7 T7)."""

from django.db.models import F, QuerySet
from django.db.models.functions import Lower
from repositories.models import Repository


def ranked_repositories() -> QuerySet[Repository]:
    return Repository.objects.filter(ranked_at__isnull=False)


def ordered_repositories() -> QuerySet[Repository]:
    return ranked_repositories().order_by(F("stargazers_count").desc(), Lower("full_name"))
