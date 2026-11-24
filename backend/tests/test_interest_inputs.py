"""Interest inputs derived from stored star weeks and counts (F8 G7, decision brief)."""

from datetime import UTC, date, datetime, timedelta
from typing import Any

import pytest
from django.test import Client
from repositories.models import StarWeek
from repositories.services import StarPoint, is_star_spike, stars_gained_previous

from tests.test_repo_detail_api import HISTORY_SOURCE, NOW, frozen_now, make_repo  # noqa: F401

AS_OF = date(2026, 11, 23)


def weeks_back(count: int, per_day: int) -> list[StarPoint]:
    """``count`` full weeks of ``per_day`` stars a day, ending in the week of AS_OF."""
    current = date(2026, 11, 22)  # the Sunday that starts AS_OF's week
    return [StarPoint(current - timedelta(weeks=n), [per_day] * 7) for n in range(count)]


def test_previous_30_days_sums_the_30_days_before_the_last_30() -> None:
    assert stars_gained_previous(weeks_back(10, 1), AS_OF, 30) == 30


def test_previous_30_days_is_none_when_history_does_not_reach_back() -> None:
    assert stars_gained_previous(weeks_back(4, 1), AS_OF, 30) is None
    assert stars_gained_previous([], AS_OF, 30) is None


@pytest.mark.parametrize(
    ("gained_7d", "forks", "issues", "total", "expected"),
    [
        (3_000, 5, 0, 3_200, True),  # F8 G7 acceptance example
        (999, 5, 0, 3_200, False),
        (3_000, 32, 0, 3_200, False),  # exactly 1% is not under 1%
        (None, 5, 0, 3_200, None),
        (3_000, None, 0, 3_200, None),
    ],
)
def test_G7_star_spike_rule(
    gained_7d: int | None, forks: int | None, issues: int, total: int, expected: bool | None
) -> None:
    assert is_star_spike(gained_7d, forks, issues, total) is expected


FETCHED = datetime(2026, 11, 23, 11, 0, tzinfo=UTC)


def make_repo_with_weeks(week_count: int, **overrides: Any) -> None:
    fields: dict[str, Any] = {
        "stargazers_count": 10_000,
        "forks_count": 2_000,
        "stars_gained_7d": 70,
        "stars_gained_30d": None,  # the interest answer must not depend on the 30-day number
        "star_history_fetched_at": FETCHED,
    }
    repo = make_repo(**{**fields, **overrides})
    for point in weeks_back(week_count, 10):
        StarWeek.objects.create(
            repository=repo,
            week_start=point.week_start,
            stars_gained=70,
            days=list(point.days),
            source=HISTORY_SOURCE,
            fetched_at=FETCHED,
        )


@pytest.mark.django_db
def test_detail_interest_compares_15_days_with_the_15_before(client: Client) -> None:
    make_repo_with_weeks(10)

    brief: dict[str, Any] = client.get("/api/repos/pallets/flask").json()["brief"]

    assert brief["interest"] == {"tone": "neutral", "value": "Steady", "window_days": 15}


@pytest.mark.django_db
def test_detail_interest_is_null_with_under_30_days_of_history(client: Client) -> None:
    make_repo_with_weeks(4)  # 23 days: Sunday 1 Nov to Monday 23 Nov

    brief: dict[str, Any] = client.get("/api/repos/pallets/flask").json()["brief"]

    assert brief["interest"] is None
