from dataclasses import dataclass

URL_PREFIXES = ("https://", "www.", "github.com/", "git@github.com:")


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


def _parse_entry(entry: str) -> RepoRef:
    owner, name = _strip_url_prefixes(entry).split("/")[:2]
    return RepoRef(owner, name.removesuffix(".git"))


def _unique_repos(repos: list[RepoRef]) -> list[RepoRef]:
    unique: dict[tuple[str, str], RepoRef] = {}
    for repo in repos:
        unique.setdefault((repo.owner.lower(), repo.name.lower()), repo)
    return list(unique.values())


def parse_repo_input(text: str) -> ParsedInput:
    if "/" not in text:
        return ParsedInput(repos=[], search=text)
    entries = text.replace(",", " ").split()
    repos = _unique_repos([_parse_entry(entry) for entry in entries])
    return ParsedInput(repos=repos, search=None)
