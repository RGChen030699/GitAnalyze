"""Decision brief rules (about.html "Decision brief rules"). Pure functions: no DB, no network."""

from repositories.brief import BriefAnswer, interest, issue_response, maintenance


def test_brief_interest_none_when_inputs_null() -> None:
    assert interest(None, 100, 10_000, False) is None
    assert interest(200, None, 10_000, False) is None
    assert interest(200, 100, None, False) is None
    assert interest(200, 100, 10_000, None) is None


def test_brief_interest_spiky_when_star_pattern_check_fires() -> None:
    assert interest(5_000, 100, 10_000, True) == BriefAnswer("warn", "Spiky")


def test_brief_interest_fading_when_no_net_stars_in_30_days() -> None:
    assert interest(0, 100, 10_000, False) == BriefAnswer("neutral", "Fading")
    assert interest(-5, 100, 10_000, False) == BriefAnswer("neutral", "Fading")


def test_brief_interest_flat_when_gain_under_0_2_percent_of_total() -> None:
    assert interest(19, 19, 10_000, False) == BriefAnswer("neutral", "Flat")
    assert interest(20, 20, 10_000, False) != BriefAnswer("neutral", "Flat")


def test_brief_interest_growing_when_up_more_than_10_percent() -> None:
    assert interest(111, 100, 10_000, False) == BriefAnswer("good", "Growing")
    assert interest(110, 100, 10_000, False) != BriefAnswer("good", "Growing")


def test_brief_interest_cooling_when_down_more_than_10_percent() -> None:
    assert interest(89, 100, 10_000, False) == BriefAnswer("warn", "Cooling")
    assert interest(90, 100, 10_000, False) != BriefAnswer("warn", "Cooling")


def test_brief_interest_steady_within_10_percent_or_without_prior_stars() -> None:
    assert interest(110, 100, 10_000, False) == BriefAnswer("neutral", "Steady")
    assert interest(90, 100, 10_000, False) == BriefAnswer("neutral", "Steady")
    assert interest(50, 0, 10_000, False) == BriefAnswer("neutral", "Steady")


def test_brief_maintenance_none_when_inputs_null() -> None:
    assert maintenance(None, 100) is None
    assert maintenance(100, None) is None


def test_brief_maintenance_stopped_when_no_commits_in_13_weeks() -> None:
    assert maintenance(0, 40) == BriefAnswer("bad", "Stopped")
    assert maintenance(0, 0) == BriefAnswer("bad", "Stopped")


def test_brief_maintenance_slowing_down_when_down_more_than_40_percent() -> None:
    assert maintenance(59, 100) == BriefAnswer("warn", "Slowing down")
    assert maintenance(60, 100) != BriefAnswer("warn", "Slowing down")


def test_brief_maintenance_speeding_up_when_up_more_than_10_percent() -> None:
    assert maintenance(111, 100) == BriefAnswer("good", "Speeding up")
    assert maintenance(110, 100) != BriefAnswer("good", "Speeding up")


def test_brief_maintenance_steady_otherwise() -> None:
    assert maintenance(110, 100) == BriefAnswer("good", "Steady")
    assert maintenance(60, 100) == BriefAnswer("good", "Steady")
    assert maintenance(12, 0) == BriefAnswer("good", "Steady")


def test_brief_issue_response_none_when_inputs_null() -> None:
    assert issue_response(None, 10) is None
    assert issue_response(10, None) is None


def test_brief_issue_response_na_when_no_issues_opened_in_6_months() -> None:
    assert issue_response(0, 0) == BriefAnswer("neutral", "N/A")
    assert issue_response(0, 3) == BriefAnswer("neutral", "N/A")


def test_brief_issue_response_keeping_up_at_95_percent_or_more() -> None:
    assert issue_response(100, 95) == BriefAnswer("good", "Keeping up")
    assert issue_response(100, 120) == BriefAnswer("good", "Keeping up")
    assert issue_response(100, 94) != BriefAnswer("good", "Keeping up")


def test_brief_issue_response_falling_behind_from_60_to_95_percent() -> None:
    assert issue_response(100, 60) == BriefAnswer("warn", "Falling behind")
    assert issue_response(100, 94) == BriefAnswer("warn", "Falling behind")
    assert issue_response(100, 59) != BriefAnswer("warn", "Falling behind")


def test_brief_issue_response_not_answering_under_60_percent() -> None:
    assert issue_response(100, 59) == BriefAnswer("bad", "Not answering")
    assert issue_response(40, 0) == BriefAnswer("bad", "Not answering")
