"""Pure repository health rules (F2)."""

from datetime import datetime, timedelta

ARCHIVED = "Archived"
ACTIVE = "Active"
SLOWING = "Slowing"
QUIET = "Quiet"

RECENT_COMMIT = timedelta(days=30)
SIX_MONTHS = timedelta(days=182)  # F2 R3: a fixed day count, not calendar months


def compute_status(
    archived: bool,
    pushed_at: datetime | None,
    newest_release_at: datetime | None,
    releases_known: bool,
    now: datetime,
) -> str | None:
    """Return the F2 label, or None when unknown releases could change it."""
    if archived:
        return ARCHIVED
    if pushed_at is None or now - pushed_at > SIX_MONTHS:
        return QUIET
    if now - pushed_at > RECENT_COMMIT:
        return SLOWING
    if not releases_known:
        return None
    if newest_release_at is None or now - newest_release_at <= SIX_MONTHS:
        return ACTIVE
    return SLOWING
