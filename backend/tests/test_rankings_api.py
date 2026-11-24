from datetime import UTC, datetime
from typing import Any

import pytest
import responses
from django.test import Client
from repositories.models import Repository

NOW = datetime(2026, 11, 23, 12, 0, tzinfo=UTC)
URL = "/api/rankings"
_next_id = iter(range(1, 100_000))


def make_repo(full_name: str, stars: int = 100, **overrides: Any) -> Repository:
    owner = full_name.split("/")[0]
    fields: dict[str, Any] = {
        "github_id": next(_next_id),
        "full_name": full_name,
        "owner_login": owner,
        "owner_type": "Organization",
        "archived": False,
        "stargazers_count": stars,
        "forks_count": 1,
        "open_issues_count": 1,
        "source": "/search/repositories?q=stars%3A%3E1000",
        "fetched_at": NOW,
        "ranked_at": NOW,
        "raw": {},
    }
    return Repository.objects.create(**{**fields, **overrides})


def names(client: Client, **params: Any) -> list[str]:
    response = client.get(URL, params)
    assert response.status_code == 200
    return [row["full_name"] for row in response.json()["results"]]


@responses.activate
@pytest.mark.django_db
def test_T7_rankings_makes_no_github_call(client: Client) -> None:
    make_repo("a/one")

    assert client.get(URL).status_code == 200
    assert len(responses.calls) == 0


@pytest.mark.django_db
def test_T3_default_sort_is_total_stars_descending(client: Client) -> None:
    make_repo("a/low", stars=10, stars_gained_7d=900)
    make_repo("b/high", stars=300, stars_gained_7d=1)
    make_repo("c/mid", stars=200, stars_gained_7d=50)

    assert names(client) == ["b/high", "c/mid", "a/low"]


@pytest.mark.django_db
def test_F7_star_ties_break_by_full_name(client: Client) -> None:
    make_repo("z/tied", stars=100)
    make_repo("A/tied", stars=100)
    make_repo("m/tied", stars=100)

    assert names(client) == ["A/tied", "m/tied", "z/tied"]


@pytest.mark.django_db
def test_F7_lookup_only_rows_are_not_ranked(client: Client) -> None:
    make_repo("a/ranked")
    make_repo("b/lookup", stars=999, ranked_at=None)

    assert names(client) == ["a/ranked"]


def first_row(client: Client) -> dict[str, Any]:
    row: dict[str, Any] = client.get(URL).json()["results"][0]
    return row


@pytest.mark.django_db
def test_nulls_stay_null_in_json(client: Client) -> None:
    make_repo("a/sparse")

    row = first_row(client)

    missing = (
        "description",
        "language",
        "status",
        "pushed_at",
        "stars_gained_7d",
        "stars_gained_30d",
        "stars_gained_year",
        "weeks_12",
        "contributors",
        "ai",
        "spike",
        "trending",
    )
    assert {name: row[name] for name in missing} == dict.fromkeys(missing)


@pytest.mark.django_db
def test_real_zero_gain_stays_zero(client: Client) -> None:
    make_repo("a/flat", stars_gained_7d=0)

    assert first_row(client)["stars_gained_7d"] == 0


@pytest.mark.django_db
def test_C8_row_includes_fields_and_provenance(client: Client) -> None:
    make_repo(
        "pallets/flask",
        stars=75193,
        forks_count=17292,
        open_issues_count=4,
        language="Python",
        status="Active",
        weeks_12=[1] * 12,
    )

    row = first_row(client)

    assert row["owner"] == "pallets"
    assert row["name"] == "flask"
    assert row["owner_type"] == "Organization"
    assert row["language"] == "Python"
    assert row["status"] == "Active"
    assert (row["stars"], row["forks"], row["open_issues"]) == (75193, 17292, 4)
    assert row["weeks_12"] == [1] * 12
    assert row["source"] == "/search/repositories?q=stars%3A%3E1000"
    assert row["fetched_at"] == "2026-11-23T12:00:00Z"


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("params", "expected"),
    [
        ({"sort": "gained"}, ["a/week", "b/month", "c/year"]),
        ({"sort": "gained", "window": "7d"}, ["a/week", "b/month", "c/year"]),
        ({"sort": "gained", "window": "30d"}, ["b/month", "c/year", "a/week"]),
        ({"sort": "gained", "window": "1y"}, ["c/year", "a/week", "b/month"]),
    ],
)
def test_G1_sort_gained_uses_window(
    client: Client, params: dict[str, str], expected: list[str]
) -> None:
    make_repo("a/week", stars_gained_7d=30, stars_gained_30d=1, stars_gained_year=20)
    make_repo("b/month", stars_gained_7d=20, stars_gained_30d=30, stars_gained_year=10)
    make_repo("c/year", stars_gained_7d=10, stars_gained_30d=20, stars_gained_year=30)

    assert names(client, **params) == expected


@pytest.mark.django_db
def test_T3_gained_sorts_negative_then_null_last(client: Client) -> None:
    make_repo("a/missing", stars=999)
    make_repo("b/negative", stars_gained_7d=-5)
    make_repo("c/zero", stars_gained_7d=0)

    assert names(client, sort="gained") == ["c/zero", "b/negative", "a/missing"]


@pytest.mark.django_db
def test_F7_gained_ties_break_by_full_name(client: Client) -> None:
    make_repo("z/tied", stars_gained_7d=5)
    make_repo("A/tied", stars_gained_7d=5)

    assert names(client, sort="gained") == ["A/tied", "z/tied"]


@pytest.mark.django_db
@pytest.mark.parametrize(
    "params",
    [{"sort": "nope"}, {"sort": "gained", "window": "5y"}, {"window": "1w"}],
)
def test_T4_invalid_sort_or_window_returns_400(client: Client, params: dict[str, str]) -> None:
    response = client.get(URL, params)

    assert response.status_code == 400
    assert response.json()["detail"]


@pytest.mark.django_db
@pytest.mark.parametrize("params", [{"sort": "trending"}, {"trending": "1"}])
def test_G5_trending_is_empty_until_data_exists(client: Client, params: dict[str, str]) -> None:
    make_repo("a/one")

    response = client.get(URL, params)

    assert response.status_code == 200
    assert response.json()["results"] == []


@pytest.mark.django_db
def test_G5_trending_0_does_not_filter(client: Client) -> None:
    make_repo("a/one")

    assert names(client, trending="0") == ["a/one"]


@pytest.mark.django_db
def test_T4_invalid_trending_returns_400(client: Client) -> None:
    assert client.get(URL, {"trending": "yes"}).status_code == 400
