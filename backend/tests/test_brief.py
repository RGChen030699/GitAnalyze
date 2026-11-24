"""Decision brief rules (about.html "Decision brief rules"). Pure functions: no DB, no network."""

from repositories.brief import BriefAnswer, interest


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
