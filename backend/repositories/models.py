"""Stored GitHub repositories and weekly star history, with provenance (F0 §3.2, C8)."""

from django.db import models
from django.db.models.functions import Lower


class Repository(models.Model):
    github_id = models.BigIntegerField(unique=True)
    full_name = models.CharField(max_length=140)
    owner_login = models.CharField(max_length=100)
    owner_type = models.CharField(max_length=20)
    description = models.TextField(null=True, blank=True)
    language = models.CharField(max_length=100, null=True, blank=True)
    archived = models.BooleanField()
    pushed_at = models.DateTimeField(null=True, blank=True)
    stargazers_count = models.IntegerField()
    forks_count = models.IntegerField()
    open_issues_count = models.IntegerField()
    newest_release_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, null=True, blank=True)
    stars_gained_7d = models.IntegerField(null=True, blank=True)
    stars_gained_30d = models.IntegerField(null=True, blank=True)
    stars_gained_year = models.IntegerField(null=True, blank=True)
    weeks_12 = models.JSONField(null=True, blank=True)
    source = models.TextField()
    fetched_at = models.DateTimeField()
    star_history_fetched_at = models.DateTimeField(null=True, blank=True)
    ranked_at = models.DateTimeField(null=True, blank=True)
    raw = models.JSONField()
    # Non-draft releases from the newest 100, read in the same refresh as the repository.
    releases = models.JSONField(null=True, blank=True)
    # F2 parts fetched when a report opens: each holds its data, source and fetched_at.
    health = models.JSONField(null=True, blank=True)
    health_fetched_at = models.DateTimeField(null=True, blank=True)
    # F8 G4: rank in each Trending list, e.g. {"weekly:all": 3, "daily:Python": 1}; null on none.
    trending = models.JSONField(null=True, blank=True)
    trending_at = models.DateTimeField(
        null=True, blank=True
    )  # last read of the weekly overall list

    class Meta:
        db_table = "repository"
        constraints = [
            models.UniqueConstraint(Lower("full_name"), name="repository_full_name_ci_unique"),
        ]

    def __str__(self) -> str:
        return self.full_name


class StarWeek(models.Model):
    repository = models.ForeignKey(Repository, on_delete=models.CASCADE, related_name="star_weeks")
    week_start = models.DateField()
    stars_gained = models.IntegerField()
    days = models.JSONField()
    source = models.TextField()
    fetched_at = models.DateTimeField()

    class Meta:
        db_table = "star_week"
        constraints = [
            models.UniqueConstraint(
                fields=["repository", "week_start"], name="star_week_repository_week_unique"
            ),
        ]

    def __str__(self) -> str:
        return f"{self.repository_id} {self.week_start}"
