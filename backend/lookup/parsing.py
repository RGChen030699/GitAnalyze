from dataclasses import dataclass

URL_PREFIXES = ("https://", "www.", "github.com/")


@dataclass(frozen=True)
class RepoRef:
    owner: str
    name: str


@dataclass(frozen=True)
class ParsedInput:
    repos: list[RepoRef]
    search: str | None


def _strip_url_prefixes(text: str) -> str:
    for prefix in URL_PREFIXES:
        text = text.removeprefix(prefix)
    return text


def parse_repo_input(text: str) -> ParsedInput:
    owner, name = _strip_url_prefixes(text).split("/")[:2]
    return ParsedInput(repos=[RepoRef(owner, name)], search=None)
