"""The README section: the repository's README as safe HTML.

READMEs are written by strangers, so the HTML is cleaned with nh3 (an allow-list sanitizer):
no scripts, styles, frames, forms or event handlers. Relative links point at the file on
github.com, relative images load from the repository, and images hosted anywhere other than
GitHub are replaced by their caption so third-party sites can't track visitors.
"""

import posixpath
import re
from urllib.parse import urlsplit

import nh3
from github_client.urls import blob_url, is_github_image, raw_file_url
from markdown_it import MarkdownIt

MAX_MARKDOWN_CHARS = 200_000
TRUNCATED_NOTE = "The README is longer than we show here. Read the rest on GitHub."

TAGS = {
    *(f"h{level}" for level in range(1, 7)),
    "p", "br", "hr", "a", "img", "ul", "ol", "li", "blockquote", "pre", "code",
    "em", "strong", "b", "i", "del", "s", "kbd", "sub", "sup", "mark",
    "table", "thead", "tbody", "tr", "th", "td", "details", "summary", "div", "span",
}  # fmt: skip
ATTRIBUTES = {
    "a": {"href", "title"},
    "img": {"src", "alt", "title", "width", "height"},
    "th": {"align"},
    "td": {"align"},
    "ol": {"start"},
    "span": {"class"},
}
IMAGE_TAG = re.compile(r"<img\b[^>]*>")
SRC = re.compile(r'\ssrc="')
ALT = re.compile(r'\salt="([^"]*)"')

_markdown = MarkdownIt("commonmark", {"html": True}).enable(["table", "strikethrough"])


def _resolve(target: str, readme_path: str) -> str | None:
    """A repository path for a relative URL, or None when it points outside the repository."""
    joined = posixpath.normpath(posixpath.join(posixpath.dirname(readme_path), target))
    if joined.startswith("..") or joined == ".":
        return None
    return joined.lstrip("/")


def _link(href: str, full_name: str, ref: str, readme_path: str) -> str | None:
    if href.startswith("#"):
        return href
    if urlsplit(href).scheme:
        return href if urlsplit(href).scheme in ("http", "https", "mailto") else None
    path = _resolve(href.split("#")[0], readme_path)
    return blob_url(full_name, ref, path) if path else None


def _image(src: str, full_name: str, ref: str, readme_path: str) -> str | None:
    if urlsplit(src).scheme:
        return src if is_github_image(src) else None
    path = _resolve(src, readme_path)
    return raw_file_url(full_name, ref, path) if path else None


def _captions_for_dropped_images(html: str) -> str:
    """An image whose source was dropped shows its caption instead (or nothing)."""

    def caption(match: re.Match[str]) -> str:
        tag = match.group(0)
        if SRC.search(tag):
            return tag
        alt = ALT.search(tag)
        return f'<span class="img-alt">{alt.group(1)}</span>' if alt and alt.group(1) else ""

    return IMAGE_TAG.sub(caption, html)


def _capped(markdown: str) -> tuple[str, bool]:
    if len(markdown) <= MAX_MARKDOWN_CHARS:
        return markdown, False
    return markdown[:MAX_MARKDOWN_CHARS].rsplit("\n", 1)[0], True


def render_readme(markdown: str, full_name: str, ref: str, readme_path: str) -> str:
    text, cut = _capped(markdown.lstrip("﻿").replace("\r\n", "\n"))
    if not text.strip():
        return ""

    def rewrite(tag: str, attribute: str, value: str) -> str | None:
        if tag == "a" and attribute == "href":
            return _link(value, full_name, ref, readme_path)
        if tag == "img" and attribute == "src":
            return _image(value, full_name, ref, readme_path)
        if tag == "span" and attribute == "class":
            return None  # only our own caption spans carry a class, added after cleaning
        return value

    html = nh3.clean(
        _markdown.render(text),
        tags=TAGS,
        attributes=ATTRIBUTES,
        attribute_filter=rewrite,
        link_rel="noopener noreferrer nofollow",
        url_schemes={"http", "https", "mailto"},
    )
    html = _captions_for_dropped_images(html).strip()
    return html + (f'\n<p class="readme-cut">{TRUNCATED_NOTE}</p>' if cut else "")
