"""Decision brief rules: five questions answered with fixed thresholds (about.html, "Decision
brief rules"). Pure functions with no database or network. Each returns None when an input is
missing, so the page shows N/A instead of guessing."""

from dataclasses import dataclass
from typing import Literal

Tone = Literal["good", "warn", "bad", "neutral"]

FLAT_SHARE_OF_TOTAL = 0.002
INTEREST_CHANGE = 0.1
COMMITS_DROP = 0.4
COMMITS_RISE = 0.1


@dataclass(frozen=True)
class BriefAnswer:
    tone: Tone
    value: str


def _change(current: int, previous: int) -> float | None:
    """Relative change, or None when there is nothing to compare against."""
    return (current - previous) / previous if previous > 0 else None


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
    return None
