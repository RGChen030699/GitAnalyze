from datetime import date, timedelta

from repositories.services import StarPoint, stars_gained, stars_gained_year, weeks_12

TUESDAY = date(2026, 11, 24)
CURRENT_WEEK = date(2026, 11, 22)
PREVIOUS_WEEK = date(2026, 11, 15)


def steady_weeks(count: int) -> list[StarPoint]:
    return [
        StarPoint(CURRENT_WEEK - timedelta(weeks=offset), (1, 1, 1, 1, 1, 1, 1))
        for offset in range(count)
    ]


def test_F8_week_sums_last_7_days_across_week_boundary() -> None:
    points = [
        StarPoint(CURRENT_WEEK, (22, 17, 5, 900, 900, 900, 900)),
        StarPoint(PREVIOUS_WEEK, (100, 100, 100, 4, 5, 6, 7)),
    ]

    assert stars_gained(points, TUESDAY, 7) == 66


def test_F8_future_days_in_current_week_are_ignored() -> None:
    points = [StarPoint(CURRENT_WEEK, (1, 2, 3, 100, 100, 100, 100))]

    assert stars_gained(points, TUESDAY, 7) == 6


def test_F8_future_week_is_ignored() -> None:
    points = [StarPoint(CURRENT_WEEK + timedelta(weeks=1), (9, 9, 9, 9, 9, 9, 9))]

    assert stars_gained(points, TUESDAY, 7) == 0


def test_F8_month_sums_last_30_days() -> None:
    assert stars_gained(steady_weeks(8), TUESDAY, 30) == 30


def test_F8_negative_weeks_kept() -> None:
    points = [StarPoint(CURRENT_WEEK, (-3, 1, 0, 0, 0, 0, 0))]

    assert stars_gained(points, TUESDAY, 7) == -2


def test_F8_no_history_gains_zero() -> None:
    assert stars_gained([], TUESDAY, 7) == 0


def test_F8_year_sums_last_52_weeks() -> None:
    assert stars_gained_year(steady_weeks(60), TUESDAY) == 364


def test_F8_year_excludes_day_365() -> None:
    oldest_week = date(2025, 11, 23)
    points = [StarPoint(oldest_week, (0, 0, 1000, 1, 0, 0, 0))]

    assert stars_gained_year(points, TUESDAY) == 1


def test_F8_year_ignores_future_days() -> None:
    points = [StarPoint(CURRENT_WEEK, (1, 2, 3, 100, 100, 100, 100))]

    assert stars_gained_year(points, TUESDAY) == 6


def test_G3_weeks_12_oldest_first_zero_fills_gaps() -> None:
    points = [
        StarPoint(CURRENT_WEEK, (1, 2, 3, 900, 900, 900, 900)),
        StarPoint(date(2026, 11, 8), (1, 1, 1, 1, 1, 1, 1)),
        StarPoint(CURRENT_WEEK - timedelta(weeks=12), (999, 0, 0, 0, 0, 0, 0)),
    ]

    assert weeks_12(points, TUESDAY) == [0, 0, 0, 0, 0, 0, 0, 0, 0, 7, 0, 6]


def test_G3_weeks_12_on_sunday_counts_only_that_day() -> None:
    points = [StarPoint(CURRENT_WEEK, (4, 900, 900, 900, 900, 900, 900))]

    assert weeks_12(points, CURRENT_WEEK)[-1] == 4


def test_G3_weeks_12_on_saturday_stays_in_same_week() -> None:
    saturday = CURRENT_WEEK + timedelta(days=6)
    points = [StarPoint(CURRENT_WEEK, (1, 1, 1, 1, 1, 1, 1))]

    assert weeks_12(points, saturday)[-1] == 7


def test_G3_weeks_12_keeps_negative_weeks() -> None:
    points = [StarPoint(PREVIOUS_WEEK, (-2, -1, 0, 0, 0, 0, 0))]

    assert weeks_12(points, TUESDAY)[-2] == -3


def test_G3_weeks_12_ignores_future_week() -> None:
    points = [StarPoint(CURRENT_WEEK + timedelta(weeks=1), (9, 9, 9, 9, 9, 9, 9))]

    assert weeks_12(points, TUESDAY) == [0] * 12
