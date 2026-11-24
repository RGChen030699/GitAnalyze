"""JSON shape of one repository in the rankings API."""

from typing import Any

from repositories.models import Repository


def serialize_row(repo: Repository) -> dict[str, Any]:
    return {"full_name": repo.full_name}
