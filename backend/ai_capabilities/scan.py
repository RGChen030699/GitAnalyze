"""Scan one repository for AI capabilities: one tree request, then file texts from raw (F4 §3)."""

from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from typing import Any
from urllib.parse import quote

from github_client import GitHubClient, GitHubError

from ai_capabilities.rules import Panel, TreeEntry, assemble, files_to_read, is_vendored

MAX_SUBTREE_REQUESTS = 50  # F4 §6: huge monorepos stop here and say "Partial scan"
READ_WORKERS = 8


def _entries(items: list[dict[str, Any]], prefix: str = "") -> list[TreeEntry]:
    return [TreeEntry(prefix + item["path"], item["type"], item["sha"]) for item in items]


def _walk_subtrees(
    client: GitHubClient, full_name: str, root: list[TreeEntry]
) -> tuple[list[TreeEntry], bool]:
    """List a truncated tree folder by folder, skipping vendored ones, up to the request cap."""
    entries = list(root)
    folders = [e for e in root if e.type == "tree" and not is_vendored(f"{e.path}/x")]
    partial = len(folders) > MAX_SUBTREE_REQUESTS
    for folder in folders[:MAX_SUBTREE_REQUESTS]:
        sub = client.get(f"/repos/{full_name}/git/trees/{folder.sha}", params={"recursive": 1})
        entries += _entries(sub.data.get("tree", []), prefix=f"{folder.path}/")
        partial = partial or bool(sub.data.get("truncated"))
    return entries, partial


def list_tree(
    client: GitHubClient, full_name: str, branch: str
) -> tuple[list[TreeEntry], bool, datetime]:
    """Every file in the default branch, whether the list is partial, and when it was read."""
    path = f"/repos/{full_name}/git/trees/{quote(branch, safe='')}"
    first = client.get(path, params={"recursive": 1})
    if not first.data.get("truncated"):
        return _entries(first.data.get("tree", [])), False, first.fetched_at
    root = client.get(path)  # more than 100,000 entries or 7 MB: walk the folders instead
    entries, partial = _walk_subtrees(client, full_name, _entries(root.data.get("tree", [])))
    return entries, partial or bool(root.data.get("truncated")), first.fetched_at


def read_files(
    client: GitHubClient, full_name: str, branch: str, paths: list[str]
) -> dict[str, str | None]:
    """File texts via the client's get_raw (no API quota); a file that can't be read is None."""
    owner, name = full_name.split("/", 1)

    def read(path: str) -> str | None:
        try:
            text = client.get_raw(owner, name, branch, path).data
        except GitHubError:
            return None
        return text if isinstance(text, str) else None

    with ThreadPoolExecutor(max_workers=READ_WORKERS) as pool:
        return dict(zip(paths, pool.map(read, paths), strict=True))


def scan_repository(client: GitHubClient, full_name: str, branch: str, owner_type: str) -> Panel:
    """The F4 panel for one repository, with its source and fetch time (F6)."""
    entries, partial, fetched_at = list_tree(client, full_name, branch)
    files = read_files(client, full_name, branch, files_to_read(entries))
    panel = assemble(entries, files, owner_type, partial)
    panel["source"] = f"/repos/{full_name}/git/trees/{branch}?recursive=1"
    panel["fetched_at"] = fetched_at.isoformat()
    return panel
