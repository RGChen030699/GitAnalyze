from typing import Any

import pytest
from requests.adapters import HTTPAdapter


@pytest.fixture(autouse=True)
def block_real_http(monkeypatch: pytest.MonkeyPatch) -> None:
    """Fail any HTTP request that a `responses` mock does not intercept."""

    def blocked(self: HTTPAdapter, request: Any, **kwargs: Any) -> None:
        raise RuntimeError(f"Real network access in tests: {request.url}")

    monkeypatch.setattr(HTTPAdapter, "send", blocked)
