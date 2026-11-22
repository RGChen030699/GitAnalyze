"""Storage for ETags and the responses they validate (C6)."""

from dataclasses import dataclass
from typing import Any, Protocol


@dataclass(frozen=True)
class CachedResponse:
    etag: str
    data: Any
    final_url: str


class ETagStore(Protocol):
    def get(self, url: str) -> CachedResponse | None: ...

    def set(self, url: str, cached: CachedResponse) -> None: ...


class InMemoryETagStore:
    """Per-process store, to be replaced by a database-backed one with the F0 schema."""

    def __init__(self) -> None:
        self._entries: dict[str, CachedResponse] = {}

    def get(self, url: str) -> CachedResponse | None:
        return self._entries.get(url)

    def set(self, url: str, cached: CachedResponse) -> None:
        self._entries[url] = cached
