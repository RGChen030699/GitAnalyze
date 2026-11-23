from datetime import UTC, datetime, timedelta
from typing import Any

import pytest
from health.services import compute_status

NOW = datetime(2026, 11, 23, 12, 0, tzinfo=UTC)
ONE_SECOND = timedelta(seconds=1)


def days_ago(days: int) -> datetime:
    return NOW - timedelta(days=days)


def status(**overrides: Any) -> str | None:
    fields: dict[str, Any] = {
        "archived": False,
        "pushed_at": days_ago(1),
        "newest_release_at": days_ago(10),
        "releases_known": True,
        "now": NOW,
    }
    return compute_status(**{**fields, **overrides})


def test_S1_archived_wins() -> None:
    assert status(archived=True) == "Archived"


def test_S1_archived_wins_when_releases_unknown() -> None:
    assert status(archived=True, newest_release_at=None, releases_known=False) == "Archived"


def test_F2_recent_commit_and_release_is_active() -> None:
    assert status(pushed_at=days_ago(10), newest_release_at=days_ago(60)) == "Active"


def test_S3_active_with_release_on_day_182() -> None:
    assert status(pushed_at=days_ago(30), newest_release_at=days_ago(182)) == "Active"


def test_S3_active_with_no_releases_ever() -> None:
    assert status(pushed_at=days_ago(30), newest_release_at=None) == "Active"


def test_S3_unknown_releases_returns_none() -> None:
    assert status(newest_release_at=None, releases_known=False) is None


def test_S4_slowing() -> None:
    assert status(pushed_at=days_ago(31)) == "Slowing"


def test_S4_commit_just_past_30_days_is_slowing() -> None:
    assert status(pushed_at=days_ago(30) - ONE_SECOND) == "Slowing"


def test_S4_recent_commit_with_old_release_is_slowing() -> None:
    assert status(newest_release_at=days_ago(182) - ONE_SECOND) == "Slowing"


def test_S4_commit_on_day_182_is_slowing() -> None:
    assert status(pushed_at=days_ago(182)) == "Slowing"


def test_S4_older_commit_is_slowing_when_releases_unknown() -> None:
    assert status(pushed_at=days_ago(31), releases_known=False) == "Slowing"


def test_S5_commit_past_182_days_is_quiet() -> None:
    assert status(pushed_at=days_ago(182) - ONE_SECOND) == "Quiet"


def test_F2_commit_8_months_ago_is_quiet() -> None:
    assert status(pushed_at=days_ago(243)) == "Quiet"


@pytest.mark.parametrize("releases_known", [True, False])
def test_S5_quiet_when_pushed_at_missing(releases_known: bool) -> None:
    assert status(pushed_at=None, releases_known=releases_known) == "Quiet"
