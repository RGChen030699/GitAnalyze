"""Pure repository health rules (F2)."""

import re
from collections.abc import Mapping, Sequence
from datetime import datetime, timedelta
from typing import Any

ARCHIVED = "Archived"
ACTIVE = "Active"
SLOWING = "Slowing"
QUIET = "Quiet"
PENDING = "pending"

RECENT_COMMIT = timedelta(days=30)
SIX_MONTHS = timedelta(days=182)  # F2 R3: a fixed day count, not calendar months
TWELVE_MONTHS = timedelta(days=365)
BOT_SUFFIX = "[bot]"
SHARE_NUMERATOR, SHARE_DENOMINATOR = 4, 5  # 80%, compared in integers so 80% exactly counts
VERSION_PATTERN = re.compile(r"^v?(\d+(?:\.\d+)*)")
NOASSERTION = "NOASSERTION"

TAG_NOTE = "tag, not a formal release"
CALCULATING_NOTE = "GitHub is still calculating this, check back in a minute"
NO_COMMITS_NOTE = "No commits in the last year"
NO_LICENSE_WARNING = "No license: others may not legally reuse this code."
CUSTOM_LICENSE = "Custom or unrecognized license"


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


# --- Single maintainer (M1–M5) ---


def contributor_commits(stats: Sequence[dict[str, Any]], now: datetime) -> dict[str, int]:
    """Commits per account in weeks starting within 365 days, bots removed (M1, M2)."""
    cutoff = (now - TWELVE_MONTHS).timestamp()
    commits: dict[str, int] = {}
    for entry in stats:
        login = (entry.get("author") or {}).get("login")
        if not login or login.endswith(BOT_SUFFIX):
            continue
        total = sum(week["c"] for week in entry.get("weeks", []) if week["w"] >= cutoff)
        if total:
            commits[login] = commits.get(login, 0) + total
    return commits


def single_maintainer(stats: Sequence[dict[str, Any]] | None, now: datetime) -> str | None:
    """The login behind 80% or more of last year's commits, PENDING, or None (M3–M5)."""
    if stats is None:
        return PENDING
    return maintainer_of(contributor_commits(stats, now))


def maintainer_of(commits: Mapping[str, int]) -> str | None:
    """The login with 80% or more of these commits, or None (M3, M4)."""
    total = sum(commits.values())
    if total == 0:
        return None
    login, top = max(commits.items(), key=lambda item: item[1])
    return login if top * SHARE_DENOMINATOR >= total * SHARE_NUMERATOR else None


# --- Releases (V1–V4) ---


def _published(releases: Sequence[dict[str, Any]]) -> list[tuple[datetime, dict[str, Any]]]:
    """Non-draft releases with a publish date, newest first (S2)."""
    dated = []
    for item in releases:
        moment = _parse(item.get("published_at"))
        if not item.get("draft") and moment is not None:
            dated.append((moment, item))
    return sorted(dated, key=lambda pair: pair[0], reverse=True)


def _version_key(name: str) -> tuple[int, ...] | None:
    match = VERSION_PATTERN.match(name)
    return tuple(int(part) for part in match.group(1).split(".")) if match else None


def _newest_tag(tags: Sequence[dict[str, Any]]) -> str:
    """Highest version number when every tag looks like a version, else the first listed."""
    names = [str(tag["name"]) for tag in tags]
    keys = [_version_key(name) for name in names]
    if all(key is not None for key in keys):
        return max(zip(keys, names, strict=True), key=lambda pair: pair[0] or ())[1]
    return names[0]


def last_release(
    releases: Sequence[dict[str, Any]], tags: Sequence[dict[str, Any]]
) -> dict[str, Any] | None:
    published = _published(releases)
    if published:
        _, newest = published[0]
        return {
            "tag": newest["tag_name"],
            "published_at": newest["published_at"],
            "kind": "release",
            "prerelease": bool(newest.get("prerelease")),
            "note": None,
        }
    if tags:
        return {
            "tag": _newest_tag(tags),
            "published_at": None,
            "kind": "tag",
            "prerelease": False,
            "note": TAG_NOTE,
        }
    return None


def releases_last_12_months(releases: Sequence[dict[str, Any]], now: datetime) -> int:
    return sum(1 for moment, _ in _published(releases) if now - moment <= TWELVE_MONTHS)


# --- Commits per week (C1–C3) ---


def commit_activity_view(weeks: Sequence[dict[str, Any]] | None) -> dict[str, Any]:
    if weeks is None:
        return {"status": PENDING, "weeks": [], "note": CALCULATING_NOTE}
    ordered = sorted(
        ({"week": w["week"], "total": w["total"], "days": list(w["days"])} for w in weeks),
        key=lambda week: week["week"],
    )
    return {"status": "ok", "weeks": ordered, "note": None if ordered else NO_COMMITS_NOTE}


# --- License (L1–L3) ---


def license_note(spdx_id: str | None) -> dict[str, str | None]:
    if not spdx_id:
        return {"spdx_id": None, "display": "No license", "warning": NO_LICENSE_WARNING}
    if spdx_id == NOASSERTION:
        return {"spdx_id": spdx_id, "display": CUSTOM_LICENSE, "warning": None}
    return {"spdx_id": spdx_id, "display": spdx_id, "warning": None}


def contributor_count(last_page: int | None, listed: int) -> int:
    """With per_page=1, the Link header's last page number is the contributor count."""
    return last_page if last_page is not None else listed


def _parse(value: str | None) -> datetime | None:
    return datetime.fromisoformat(value) if value else None
