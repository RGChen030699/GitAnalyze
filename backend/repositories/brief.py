"""Decision brief rules: five questions answered with fixed thresholds (about.html, "Decision
brief rules"). Pure functions with no database or network. Each returns None when an input is
missing, so the page shows N/A instead of guessing."""

from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime, timedelta
from statistics import median
from typing import Literal

Tone = Literal["good", "warn", "bad", "neutral"]

FLAT_SHARE_OF_TOTAL = 0.002
INTEREST_CHANGE = 0.1
COMMITS_DROP = 0.4
COMMITS_RISE = 0.1
KEEPING_UP_RATIO = 0.95
FALLING_BEHIND_RATIO = 0.6
ON_PACE_RATIO = 1.5
USUAL_GAP_WINDOW = 8
SECONDS_PER_DAY = 86_400


@dataclass(frozen=True)
class BriefAnswer:
    tone: Tone
    value: str


def _change(current: int, previous: int) -> float | None:
    """Relative change, or None when there is nothing to compare against."""
    return (current - previous) / previous if previous > 0 else None


def _days(span: timedelta) -> float:
    return span.total_seconds() / SECONDS_PER_DAY


def _days_between(dates: Sequence[datetime]) -> list[float]:
    return [_days(later - earlier) for earlier, later in zip(dates, dates[1:], strict=False)]


def interest(
    gained_30d: int | None,
    gained_prev_30d: int | None,
    total_stars: int | None,
    spike: bool | None,
) -> BriefAnswer | None:
    """Is interest real and growing? Stars in the last 30 days against the 30 days before."""
    if gained_30d is None or gained_prev_30d is None or total_stars is None or spike is None:
        return None
    if spike:
        return BriefAnswer("warn", "Spiky")
    if gained_30d <= 0:
        return BriefAnswer("neutral", "Fading")
    if gained_30d < FLAT_SHARE_OF_TOTAL * total_stars:
        return BriefAnswer("neutral", "Flat")
    change = _change(gained_30d, gained_prev_30d)
    if change is not None and change > INTEREST_CHANGE:
        return BriefAnswer("good", "Growing")
    if change is not None and change < -INTEREST_CHANGE:
        return BriefAnswer("warn", "Cooling")
    return BriefAnswer("neutral", "Steady")


def maintenance(commits_13w: int | None, commits_prev_13w: int | None) -> BriefAnswer | None:
    """Is someone still working on it? Commits in the last 13 weeks against the 13 before."""
    if commits_13w is None or commits_prev_13w is None:
        return None
    if commits_13w == 0:
        return BriefAnswer("bad", "Stopped")
    change = _change(commits_13w, commits_prev_13w)
    if change is not None and change < -COMMITS_DROP:
        return BriefAnswer("warn", "Slowing down")
    if change is not None and change > COMMITS_RISE:
        return BriefAnswer("good", "Speeding up")
    return BriefAnswer("good", "Steady")


def issue_response(opened_6m: int | None, closed_6m: int | None) -> BriefAnswer | None:
    """Will my bug reports get answered? Issues closed for every issue opened, last 6 months."""
    if opened_6m is None or closed_6m is None:
        return None
    if opened_6m == 0:
        return BriefAnswer("neutral", "N/A")
    close_ratio = closed_6m / opened_6m
    if close_ratio >= KEEPING_UP_RATIO:
        return BriefAnswer("good", "Keeping up")
    if close_ratio >= FALLING_BEHIND_RATIO:
        return BriefAnswer("warn", "Falling behind")
    return BriefAnswer("bad", "Not answering")


def release_pace(releases: Sequence[datetime] | None, now: datetime) -> BriefAnswer | None:
    """Does it ship on a rhythm? Days since the last release against its usual gap.

    ``releases`` holds the publish dates of non-draft, non-prerelease releases.
    """
    if releases is None:
        return None
    if not releases:
        return BriefAnswer("neutral", "No releases")
    dates = sorted(releases)
    if len(dates) < 2:
        return None  # no gap yet, so no usual pace to compare against
    usual_gap = median(_days_between(dates)[-USUAL_GAP_WINDOW:])
    ratio = _days(now - dates[-1]) / usual_gap
    if ratio <= ON_PACE_RATIO:
        return BriefAnswer("good", "On its usual pace")
    return BriefAnswer("warn", f"Overdue, {ratio:.1f}× its usual gap")
