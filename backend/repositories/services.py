"""Pure star history calculations (F3, F8)."""

from collections.abc import Iterator, Sequence
from dataclasses import dataclass
from datetime import date, timedelta

YEAR_DAYS = 52 * 7
SPARKLINE_WEEKS = 12


@dataclass(frozen=True)
class StarPoint:
    """One week of net stars; ``days`` starts on the Sunday ``week_start``."""

    week_start: date
    days: Sequence[int]


def _elapsed_days(point: StarPoint, as_of: date) -> Iterator[tuple[date, int]]:
    for offset, gained in enumerate(point.days):
        day = point.week_start + timedelta(days=offset)
        if day <= as_of:
            yield day, gained


def stars_gained(points: Sequence[StarPoint], as_of: date, days: int) -> int:
    """Sum net stars for the ``days`` ending on ``as_of``, ignoring future days."""
    first_day = as_of - timedelta(days=days - 1)
    return sum(
        gained
        for point in points
        for day, gained in _elapsed_days(point, as_of)
        if day >= first_day
    )


def stars_gained_year(points: Sequence[StarPoint], as_of: date) -> int:
    return stars_gained(points, as_of, YEAR_DAYS)


def weeks_12(points: Sequence[StarPoint], as_of: date) -> list[int]:
    """Return 12 weekly totals, oldest first, ending with the current partial week."""
    current_week = as_of - timedelta(days=(as_of.weekday() + 1) % 7)
    totals = {
        point.week_start: sum(gained for _, gained in _elapsed_days(point, as_of))
        for point in points
    }
    return [
        totals.get(current_week - timedelta(weeks=offset), 0)
        for offset in range(SPARKLINE_WEEKS - 1, -1, -1)
    ]
