"""F4 scanning: the file tree from the API, file contents from raw.githubusercontent.com.

Reading raw files without a token is the F0 client's get_raw (C9), tested there."""

from datetime import UTC, datetime
from typing import Any

import pytest
import responses
from ai_capabilities.scan import MAX_SUBTREE_REQUESTS, scan_repository
from github_client import GitHubClient
from github_client.client import API_BASE_URL, RAW_BASE_URL

NOW = datetime(2026, 11, 24, 12, 0, tzinfo=UTC)
REPO = "octo/kit"
TREES = f"{API_BASE_URL}/repos/{REPO}/git/trees"
RAW = f"{RAW_BASE_URL}/{REPO}/main"
SKILL = "---\nname: forms\ndescription: Fills PDF forms.\n---\nBody\n"


@pytest.fixture(autouse=True)
def token(settings: Any) -> None:
    settings.GITHUB_TOKEN = "test-token"


def client() -> GitHubClient:
    return GitHubClient(clock=lambda: NOW, sleep=lambda _: None)


def entry(path: str, kind: str = "blob", sha: str = "0" * 40) -> dict[str, str]:
    return {"path": path, "type": kind, "sha": sha, "mode": "100644"}


@responses.activate
def test_F4_scan_lists_the_tree_once_and_reads_files_from_raw() -> None:
    tree = [
        entry("skills/forms/SKILL.md", sha="a" * 40),
        entry("skills/forms/scripts/fill_form.py"),
        entry("README.md"),
    ]
    responses.get(f"{TREES}/main", json={"sha": "t", "truncated": False, "tree": tree})
    responses.get(f"{RAW}/skills/forms/SKILL.md", body=SKILL)
    responses.get(f"{RAW}/README.md", body="A toolkit.")

    result = scan_repository(client(), REPO, "main", "Organization")

    assert result["skills"][0]["name"] == "forms"
    assert result["skills"][0]["scripts"] == ["scripts/fill_form.py"]
    assert result["partial"] is False
    assert "Authorization" not in responses.calls[1].request.headers
    assert result["source"] == f"/repos/{REPO}/git/trees/main?recursive=1"
    assert result["fetched_at"] == NOW.isoformat()
    api_calls = [c for c in responses.calls if c.request.url.startswith(API_BASE_URL)]
    assert len(api_calls) == 1
    assert "recursive=1" in api_calls[0].request.url


@responses.activate
def test_F4_truncated_tree_is_walked_by_subtree_skipping_vendored_folders() -> None:
    root = [
        entry("skills", "tree", "s" * 40),
        entry("node_modules", "tree", "n" * 40),
        entry("AGENTS.md"),
    ]
    responses.get(f"{TREES}/main", json={"truncated": True, "tree": []})
    responses.get(f"{TREES}/main", json={"truncated": False, "tree": root})
    sub = [entry("forms", "tree"), entry("forms/SKILL.md", sha="a" * 40)]
    responses.get(f"{TREES}/{'s' * 40}", json={"truncated": False, "tree": sub})
    responses.get(f"{RAW}/skills/forms/SKILL.md", body=SKILL)

    result = scan_repository(client(), REPO, "main", "User")

    assert [s["path"] for s in result["skills"]] == ["skills/forms/SKILL.md"]
    assert [a["path"] for a in result["agent_files"]] == ["AGENTS.md"]
    assert result["partial"] is False
    assert not any("n" * 40 in str(c.request.url) for c in responses.calls)


@responses.activate
def test_F4_huge_monorepo_stops_after_50_subtrees_and_says_partial() -> None:
    root = [entry(f"pkg{i:02d}", "tree", f"{i:040d}") for i in range(60)]
    responses.get(f"{TREES}/main", json={"truncated": True, "tree": []})
    responses.get(f"{TREES}/main", json={"truncated": False, "tree": root})
    for i in range(60):
        responses.get(f"{TREES}/{i:040d}", json={"truncated": False, "tree": []})

    result = scan_repository(client(), REPO, "main", "Organization")

    subtree_calls = [c for c in responses.calls if "/git/trees/0" in str(c.request.url)]
    assert len(subtree_calls) == MAX_SUBTREE_REQUESTS
    assert result["partial"] is True


@responses.activate
def test_F4_unreadable_raw_file_does_not_stop_the_scan() -> None:
    tree = [entry("skills/forms/SKILL.md", sha="a" * 40), entry("CLAUDE.md")]
    responses.get(f"{TREES}/main", json={"truncated": False, "tree": tree})
    responses.get(f"{RAW}/skills/forms/SKILL.md", status=500)

    result = scan_repository(client(), REPO, "main", "Organization")

    assert result["possible_skills"][0]["reason"] == "Couldn't read the file"
    assert result["has_ai"] is True
