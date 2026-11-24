"""Parse the languages that the rankings refresh searches."""

from collections.abc import Iterable

DEFAULT_RANKINGS_LANGUAGES = ("Python", "TypeScript", "JavaScript")


def normalize_languages(values: Iterable[str]) -> tuple[str, ...]:
    """Trim names, drop blanks, and keep the first spelling of each language."""
    unique: dict[str, str] = {}
    for value in values:
        name = value.strip()
        if name:
            unique.setdefault(name.lower(), name)
    return tuple(unique.values())


def parse_rankings_languages(raw: str | None) -> tuple[str, ...]:
    return normalize_languages((raw or "").split(",")) or DEFAULT_RANKINGS_LANGUAGES
