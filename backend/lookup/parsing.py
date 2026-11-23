from dataclasses import dataclass


@dataclass(frozen=True)
class RepoRef:
    owner: str
    name: str


@dataclass(frozen=True)
class ParsedInput:
    repos: list[RepoRef]
    search: str | None


def parse_repo_input(text: str) -> ParsedInput:
    owner, name = text.removeprefix("https://").removeprefix("github.com/").split("/")
    return ParsedInput(repos=[RepoRef(owner, name)], search=None)
