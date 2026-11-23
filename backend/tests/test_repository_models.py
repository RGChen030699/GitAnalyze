from datetime import UTC, date, datetime
from io import StringIO
from typing import Any

import pytest
from django.core.management import call_command
from django.db import IntegrityError
from repositories.models import Repository, StarWeek

FETCHED_AT = datetime(2026, 11, 23, 12, 0, tzinfo=UTC)
REPO_SOURCE = "/repos/pallets/flask"
HISTORY_SOURCE = "/repos/pallets/flask/stargazers/history"
WEEK_START = date(2026, 11, 22)
OPTIONAL_FIELDS = (
    "description",
    "language",
    "pushed_at",
    "newest_release_at",
    "status",
    "stars_gained_7d",
    "stars_gained_30d",
    "stars_gained_year",
    "weeks_12",
    "star_history_fetched_at",
    "ranked_at",
)


def make_repository(**overrides: Any) -> Repository:
    fields: dict[str, Any] = {
        "github_id": 596892,
        "full_name": "pallets/flask",
        "owner_login": "pallets",
        "owner_type": "Organization",
        "archived": False,
        "stargazers_count": 75193,
        "forks_count": 16000,
        "open_issues_count": 5,
        "source": REPO_SOURCE,
        "fetched_at": FETCHED_AT,
        "raw": {"full_name": "pallets/flask"},
    }
    return Repository.objects.create(**{**fields, **overrides})


def make_star_week(repository: Repository, **overrides: Any) -> StarWeek:
    fields: dict[str, Any] = {
        "repository": repository,
        "week_start": WEEK_START,
        "stars_gained": 39,
        "days": [22, 17, 0, 0, 0, 0, 0],
        "source": HISTORY_SOURCE,
        "fetched_at": FETCHED_AT,
    }
    return StarWeek.objects.create(**{**fields, **overrides})


@pytest.mark.django_db
def test_C8_repository_stores_source_and_fetched_at() -> None:
    repository = make_repository()

    repository.refresh_from_db()

    assert repository.source == REPO_SOURCE
    assert repository.fetched_at == FETCHED_AT
    assert repository.raw == {"full_name": "pallets/flask"}


@pytest.mark.django_db
def test_missing_repository_data_stays_null() -> None:
    repository = make_repository()

    repository.refresh_from_db()

    assert {name: getattr(repository, name) for name in OPTIONAL_FIELDS} == dict.fromkeys(
        OPTIONAL_FIELDS
    )


@pytest.mark.django_db
def test_C7_github_id_is_unique() -> None:
    make_repository()

    with pytest.raises(IntegrityError):
        make_repository(full_name="pallets/renamed")


@pytest.mark.django_db
def test_L4_full_name_is_unique_ignoring_case() -> None:
    make_repository()

    with pytest.raises(IntegrityError):
        make_repository(github_id=2, full_name="Pallets/FLASK")


@pytest.mark.django_db
def test_C8_star_week_stores_source_and_fetched_at() -> None:
    star_week = make_star_week(make_repository())

    star_week.refresh_from_db()

    assert star_week.source == HISTORY_SOURCE
    assert star_week.fetched_at == FETCHED_AT
    assert star_week.week_start == WEEK_START
    assert star_week.days == [22, 17, 0, 0, 0, 0, 0]


@pytest.mark.django_db
def test_F3_star_week_keeps_net_negative_values() -> None:
    star_week = make_star_week(make_repository(), stars_gained=-2, days=[-2, 0, 0, 0, 0, 0, 0])

    star_week.refresh_from_db()

    assert star_week.stars_gained == -2
    assert star_week.days[0] == -2


@pytest.mark.django_db
def test_F0_star_week_is_unique_per_repository_and_week() -> None:
    repository = make_repository()
    make_star_week(repository)

    with pytest.raises(IntegrityError):
        make_star_week(repository)


@pytest.mark.django_db
def test_F0_same_week_is_allowed_for_another_repository() -> None:
    make_star_week(make_repository())
    make_star_week(make_repository(github_id=2, full_name="psf/requests"))

    assert StarWeek.objects.filter(week_start=WEEK_START).count() == 2


@pytest.mark.django_db
def test_deleting_repository_deletes_its_star_weeks() -> None:
    repository = make_repository()
    make_star_week(repository)

    repository.delete()

    assert StarWeek.objects.count() == 0


@pytest.mark.django_db
def test_models_match_committed_migrations() -> None:
    call_command("makemigrations", "--check", "--dry-run", stdout=StringIO())
