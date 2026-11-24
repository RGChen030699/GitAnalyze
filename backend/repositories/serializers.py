"""JSON shape of one repository on the repository page."""

from typing import Any

from repositories.models import Repository


def serialize_detail(repo: Repository) -> dict[str, Any]:
    return {"full_name": repo.full_name}
