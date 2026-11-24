"""F2 health rules: single maintainer (M1–M5), releases (V1–V4), commit chart (C1–C3),
license (L1–L3) and contributor count. Pure functions, so no database or network."""

from datetime import UTC, datetime, timedelta
from typing import Any

from health.services import (
    PENDING,
    commit_activity_view,
    contributor_commits,
    contributor_count,
    last_release,
    license_note,
    releases_last_12_months,
    single_maintainer,
)

NOW = datetime(2026, 11, 23, 12, 0, tzinfo=UTC)


def ts(days_ago: float) -> int:
    return int((NOW - timedelta(days=days_ago)).timestamp())


def iso(days_ago: float) -> str:
    return (NOW - timedelta(days=days_ago)).strftime("%Y-%m-%dT%H:%M:%SZ")


def account(login: str, weeks: list[tuple[float, int]]) -> dict[str, Any]:
    return {"author": {"login": login}, "weeks": [{"w": ts(d), "c": c} for d, c in weeks]}


def release(tag: str, days_ago: float, draft: bool = False, pre: bool = False) -> dict[str, Any]:
    return {"tag_name": tag, "published_at": iso(days_ago), "draft": draft, "prerelease": pre}


# --- M1–M5: single maintainer ---


def test_F2_M1_only_weeks_within_365_days_count() -> None:
    stats = [account("old", [(400, 100), (10, 1)]), account("new", [(10, 9)])]
    assert contributor_commits(stats, NOW) == {"old": 1, "new": 9}


def test_F2_M1_week_starting_exactly_365_days_ago_counts() -> None:
    assert contributor_commits([account("a", [(365, 3)])], NOW) == {"a": 3}


def test_F2_M2_bot_accounts_are_removed() -> None:
    stats = [account("dependabot[bot]", [(5, 90)]), account("alice", [(5, 10)])]
    assert contributor_commits(stats, NOW) == {"alice": 10}
    assert single_maintainer(stats, NOW) == "alice"


def test_F2_M2_account_without_author_is_skipped() -> None:
    stats = [{"author": None, "weeks": [{"w": ts(5), "c": 50}]}, account("bob", [(5, 1)])]
    assert contributor_commits(stats, NOW) == {"bob": 1}


def test_F2_M3_90_percent_names_that_person() -> None:
    stats = [account("alice", [(5, 90)]), account("bob", [(5, 10)])]
    assert single_maintainer(stats, NOW) == "alice"


def test_F2_M3_exactly_80_percent_counts() -> None:
    stats = [account("alice", [(5, 80)]), account("bob", [(5, 20)])]
    assert single_maintainer(stats, NOW) == "alice"


def test_F2_M3_below_80_percent_returns_nothing() -> None:
    stats = [account("alice", [(5, 79)]), account("bob", [(5, 21)])]
    assert single_maintainer(stats, NOW) is None


def test_F2_M4_no_commits_last_year_returns_nothing() -> None:
    assert single_maintainer([account("alice", [(400, 50)])], NOW) is None


def test_F2_M4_only_bots_returns_nothing() -> None:
    assert single_maintainer([account("renovate[bot]", [(5, 50)])], NOW) is None


def test_F2_M5_pending_stats_return_pending() -> None:
    assert single_maintainer(None, NOW) == PENDING


# --- V1–V4: last release and count ---


def test_F2_V1_newest_non_draft_release_by_published_at() -> None:
    releases = [release("v2", 1, draft=True), release("v1.1", 10), release("v1.0", 40)]
    assert last_release(releases, []) == {
        "tag": "v1.1",
        "published_at": iso(10),
        "kind": "release",
        "prerelease": False,
        "note": None,
    }


def test_F2_V1_prerelease_is_returned_and_marked() -> None:
    result = last_release([release("v2.0-rc1", 3, pre=True), release("v1.0", 40)], [])
    assert result is not None
    assert result["tag"] == "v2.0-rc1"
    assert result["prerelease"] is True


def test_F2_V2_tags_only_returns_highest_version_with_note() -> None:
    tags = [{"name": "v1.9.2"}, {"name": "v1.10.0"}, {"name": "v1.2.0"}]
    assert last_release([], tags) == {
        "tag": "v1.10.0",
        "published_at": None,
        "kind": "tag",
        "prerelease": False,
        "note": "tag, not a formal release",
    }


def test_F2_V2_non_version_tags_take_the_first_listed() -> None:
    result = last_release([], [{"name": "stable"}, {"name": "latest"}])
    assert result is not None
    assert result["tag"] == "stable"


def test_F2_V2_only_drafts_counts_as_no_releases() -> None:
    result = last_release([release("v3", 1, draft=True)], [{"name": "v0.1"}])
    assert result is not None
    assert result["kind"] == "tag"


def test_F2_V3_no_releases_and_no_tags_returns_nothing() -> None:
    assert last_release([], []) is None


def test_F2_V4_counts_non_draft_releases_within_365_days() -> None:
    releases = [
        release("a", 10),
        release("b", 200, pre=True),
        release("c", 365),
        release("d", 366),
        release("e", 5, draft=True),
    ]
    assert releases_last_12_months(releases, NOW) == 3


# --- C1–C3: commits per week ---


def test_F2_C1_pending_stats_show_calculating_message() -> None:
    assert commit_activity_view(None) == {
        "status": "pending",
        "weeks": [],
        "note": "GitHub is still calculating this, check back in a minute",
    }


def test_F2_C2_weeks_oldest_first() -> None:
    weeks = [
        {"week": ts(7), "total": 2, "days": [0, 1, 1, 0, 0, 0, 0]},
        {"week": ts(14), "total": 5, "days": [1, 1, 1, 1, 1, 0, 0]},
    ]
    view = commit_activity_view(weeks)
    assert view["status"] == "ok"
    assert [w["total"] for w in view["weeks"]] == [5, 2]
    assert view["weeks"][0] == {"week": ts(14), "total": 5, "days": [1, 1, 1, 1, 1, 0, 0]}
    assert view["note"] is None


def test_F2_C3_empty_list_says_no_commits() -> None:
    assert commit_activity_view([]) == {
        "status": "ok",
        "weeks": [],
        "note": "No commits in the last year",
    }


# --- L1–L3: license ---


def test_F2_L1_no_license_warns() -> None:
    assert license_note(None) == {
        "spdx_id": None,
        "display": "No license",
        "warning": "No license: others may not legally reuse this code.",
    }


def test_F2_L2_noassertion_is_custom_without_warning() -> None:
    assert license_note("NOASSERTION") == {
        "spdx_id": "NOASSERTION",
        "display": "Custom or unrecognized license",
        "warning": None,
    }


def test_F2_L3_known_license_is_shown_as_is() -> None:
    assert license_note("MIT") == {"spdx_id": "MIT", "display": "MIT", "warning": None}


# --- Contributor count from the Link header ---


def test_F2_contributor_count_reads_last_page() -> None:
    assert contributor_count(last_page=412, listed=1) == 412


def test_F2_contributor_count_without_link_is_the_listed_count() -> None:
    assert contributor_count(last_page=None, listed=1) == 1
    assert contributor_count(last_page=None, listed=0) == 0
