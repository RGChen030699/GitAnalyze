"""Parse and validate rankings query parameters."""

from collections.abc import Mapping
from dataclasses import dataclass

from health.services import ACTIVE, ARCHIVED, QUIET, SLOWING

SORTS = ("stars", "gained", "pushed", "trending")
WINDOWS = ("7d", "30d", "1y")
FLAGS = ("0", "1")
STATUSES = (ACTIVE, SLOWING, QUIET, ARCHIVED)


class InvalidRankingParams(Exception):
    pass


@dataclass(frozen=True)
class RankingParams:
    sort: str = "stars"
    window: str = "7d"
    trending_only: bool = False
    lang: str | None = None
    status: str | None = None
    archived: bool | None = None


def _choice(query: Mapping[str, str], name: str, choices: tuple[str, ...], default: str) -> str:
    value = query.get(name) or default
    if value not in choices:
        raise InvalidRankingParams(f"{name} must be one of: {', '.join(choices)}")
    return value


def _optional_choice(query: Mapping[str, str], name: str, choices: tuple[str, ...]) -> str | None:
    return _choice(query, name, choices, "") if query.get(name) else None


def parse_params(query: Mapping[str, str]) -> RankingParams:
    archived = _optional_choice(query, "archived", FLAGS)
    return RankingParams(
        sort=_choice(query, "sort", SORTS, "stars"),
        window=_choice(query, "window", WINDOWS, "7d"),
        trending_only=_choice(query, "trending", FLAGS, "0") == "1",
        lang=query.get("lang") or None,
        status=_optional_choice(query, "status", STATUSES),
        archived=None if archived is None else archived == "1",
    )
