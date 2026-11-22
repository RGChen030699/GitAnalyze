"""Value types returned by the GitHub client."""

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Literal


@dataclass(frozen=True)
class GitHubResponse:
    """Response data plus the provenance F6 stores with it (C8)."""

    data: Any
    source: str
    fetched_at: datetime
    cost: int
    final_url: str
    status: Literal["ok", "pending"] = "ok"
    from_cache: bool = False
