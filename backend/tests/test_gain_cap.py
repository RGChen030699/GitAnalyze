import pytest
from repositories.services import cap_gain


@pytest.mark.parametrize(
    ("gained", "total", "expected"),
    [
        (50, 10, 10),
        (10, 10, 10),
        (9, 10, 9),
        (-3, 10, -3),
        (5, 0, 0),
    ],
)
def test_F8_gain_is_capped_at_total(gained: int, total: int, expected: int) -> None:
    assert cap_gain(gained, total) == expected


def test_F8_missing_gain_stays_null() -> None:
    assert cap_gain(None, 10) is None
