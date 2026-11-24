"""Decision brief rules: five questions answered with fixed thresholds (about.html, "Decision
brief rules"). Pure functions with no database or network. Each returns None when an input is
missing, so the page shows N/A instead of guessing."""

from dataclasses import dataclass
from typing import Literal

Tone = Literal["good", "warn", "bad", "neutral"]


@dataclass(frozen=True)
class BriefAnswer:
    tone: Tone
    value: str


def interest(
    gained_30d: int | None,
    gained_prev_30d: int | None,
    total_stars: int | None,
    spike: bool | None,
) -> BriefAnswer | None:
    """Is interest real and growing? Stars in the last 30 days against the 30 days before."""
    if gained_30d is None or gained_prev_30d is None or total_stars is None or spike is None:
        return None
    return None
