from typing import Any

from repositories.services import OVERALL_QUERY, build_watch_list, language_query


def item(github_id: int, full_name: str, stars: int) -> dict[str, Any]:
    return {"id": github_id, "full_name": full_name, "stargazers_count": stars}


def names(items: list[dict[str, Any]]) -> list[str]:
    return [entry["full_name"] for entry in items]


def test_W1_watch_list_dedupes_and_applies_limit() -> None:
    overall = [item(1, "a/high", 300), item(2, "b/mid", 200)]
    by_language = [[item(2, "b/mid", 200), item(3, "c/low", 100)]]

    assert names(build_watch_list(overall, by_language, None)) == ["a/high", "b/mid", "c/low"]
    assert names(build_watch_list(overall, by_language, 2)) == ["a/high", "b/mid"]


def test_W1_watch_list_sorts_across_searches() -> None:
    overall = [item(1, "a/low", 100)]
    by_language = [[item(2, "b/high", 900)]]

    assert names(build_watch_list(overall, by_language, 1)) == ["b/high"]


def test_W1_watch_list_breaks_star_ties_by_name() -> None:
    overall = [item(1, "z/tied", 100), item(2, "A/tied", 100)]

    assert names(build_watch_list(overall, [], None)) == ["A/tied", "z/tied"]


def test_W1_overall_query_uses_star_floor() -> None:
    assert OVERALL_QUERY == "stars:>1000"


def test_W1_language_query() -> None:
    assert language_query("Python") == "language:Python stars:>1000"


def test_W1_language_query_quotes_spaces() -> None:
    assert language_query("Jupyter Notebook") == 'language:"Jupyter Notebook" stars:>1000'
