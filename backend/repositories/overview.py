"""What a repository is about, in the owner's own words: the first real paragraph of its README.

Pure text handling. Badges, headings, code, tables, lists, quotes and link definitions are
skipped, and so is any block too short once HTML is removed (logos, link bars) or that only
introduces a list. Links and emphasis keep their text; nothing is rewritten or summarised.
"""

import re

MAX_CHARS = 400
MIN_CHARS = 40  # shorter paragraphs are usually a tagline fragment or a stray link

FRONT_MATTER = re.compile(r"\A---\n.*?\n---\n", re.DOTALL)
FENCE = re.compile(r"^(```|~~~).*?^\1[^\n]*$", re.DOTALL | re.MULTILINE)
IMAGE = re.compile(r"!\[[^\]]*\](\([^)]*\)|\[[^\]]*\])")  # inline or reference style
LINK = re.compile(r"\[([^\]]*)\]\([^)]*\)")
REF_LINK = re.compile(r"\[([^\]]*)\]\[[^\]]*\]")
TAG = re.compile(r"<[^>]+>")
EMPHASIS = re.compile(r"(\*\*|__|\*|_|`)(?=\S)(.+?)(?<=\S)\1")
HEADING = re.compile(r"^(#{1,6}\s|#+$|={3,}$|-{3,}$)")
# quotes, tables, list items and link reference definitions
NOT_PROSE = re.compile(r"^(>|\||[-*+]\s|\d+[.)]\s|\[[^\]]+\]:\s)")
SENTENCE_END = re.compile(r"[.!?](?=\s|$)")


def _blocks(text: str) -> list[str]:
    text = text.lstrip("﻿").replace("\r\n", "\n")
    text = FENCE.sub("", FRONT_MATTER.sub("", text))
    return [block.strip("\n") for block in re.split(r"\n\s*\n", text)]


def _prose(block: str) -> str:
    """The block's opening prose lines: headings above it are dropped, a list or table ends it."""
    lines: list[str] = []
    for raw in block.split("\n"):
        line = raw.strip()
        if not line:
            continue
        if HEADING.match(line):
            if lines:
                break
            continue
        if NOT_PROSE.match(line) or raw.startswith(("    ", "\t")):
            break
        lines.append(line)
    return " ".join(lines)


def _plain(block: str) -> str:
    text = IMAGE.sub("", block)
    text = LINK.sub(r"\1", REF_LINK.sub(r"\1", text))
    text = TAG.sub("", text)
    text = EMPHASIS.sub(r"\2", text)
    return " ".join(text.split())


def _cut(text: str) -> str:
    if len(text) <= MAX_CHARS:
        return text
    ends = [m.end() for m in SENTENCE_END.finditer(text) if m.end() <= MAX_CHARS]
    if ends:
        return text[: ends[-1]]
    return text[:MAX_CHARS].rsplit(" ", 1)[0] + "…"


def readme_summary(text: str) -> str | None:
    """The first paragraph of plain prose, at most about 400 characters; None if there isn't one."""
    for block in _blocks(text):
        plain = _plain(_prose(block))
        if len(plain) >= MIN_CHARS and not plain.endswith(":"):  # "check out:" introduces a list
            return _cut(plain)
    return None
