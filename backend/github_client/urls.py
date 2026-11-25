"""Links to files on GitHub, for pages that show a repository's own content (the README section).

Kept in github_client, the only module that names GitHub hosts.
"""

from urllib.parse import quote, urlsplit

from github_client.client import RAW_BASE_URL

WEB_BASE_URL = "https://github.com"
# GitHub's own image hosts; images from anywhere else are not loaded (they can track visitors).
GITHUB_IMAGE_HOSTS = frozenset(
    {
        "github.com",
        "raw.githubusercontent.com",
        "user-images.githubusercontent.com",
        "private-user-images.githubusercontent.com",
        "avatars.githubusercontent.com",
        "camo.githubusercontent.com",
    }
)


def _quoted(path: str) -> str:
    return quote(path, safe="/")


def blob_url(full_name: str, ref: str, path: str) -> str:
    """The file's page on github.com."""
    return f"{WEB_BASE_URL}/{full_name}/blob/{quote(ref, safe='')}/{_quoted(path)}"


def raw_file_url(full_name: str, ref: str, path: str) -> str:
    """The file's bytes, for images inside the repository."""
    return f"{RAW_BASE_URL}/{full_name}/{quote(ref, safe='')}/{_quoted(path)}"


def is_github_image(url: str) -> bool:
    parts = urlsplit(url)
    return parts.scheme == "https" and parts.hostname in GITHUB_IMAGE_HOSTS
