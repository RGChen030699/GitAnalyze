"""Decision brief rules (about.html "Decision brief rules"). Pure functions: no DB, no network."""

from repositories.brief import BriefAnswer, interest


def test_brief_interest_none_when_inputs_null() -> None:
    assert interest(None, 100, 10_000, False) is None
    assert interest(200, None, 10_000, False) is None
    assert interest(200, 100, None, False) is None
    assert interest(200, 100, 10_000, None) is None
