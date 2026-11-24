"""Parse and validate rankings query parameters."""

from collections.abc import Mapping
from dataclasses import dataclass

SORTS = ("stars", "gained")
WINDOWS = ("7d", "30d", "1y")


class InvalidRankingParams(Exception):
    pass


@dataclass(frozen=True)
class RankingParams:
    sort: str = "stars"
    window: str = "7d"


def _choice(query: Mapping[str, str], name: str, choices: tuple[str, ...], default: str) -> str:
    value = query.get(name) or default
    if value not in choices:
        raise InvalidRankingParams(f"{name} must be one of: {', '.join(choices)}")
    return value


def parse_params(query: Mapping[str, str]) -> RankingParams:
    return RankingParams(
        sort=_choice(query, "sort", SORTS, "stars"),
        window=_choice(query, "window", WINDOWS, "7d"),
    )
