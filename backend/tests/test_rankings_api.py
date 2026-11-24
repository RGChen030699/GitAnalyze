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
