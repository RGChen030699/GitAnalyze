from dataclasses import dataclass

URL_PREFIXES = ("https://", "http://", "www.", "github.com/", "git@github.com:")
MAX_REPOS = 3


class TooManyRepos(Exception):
    pass


class InvalidRepoInput(Exception):
    pass


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
    if "." in owner:
        raise InvalidRepoInput("GitAnalyze only checks GitHub repositories")
    return RepoRef(owner, name.removesuffix(".git"))


def _unique_repos(repos: list[RepoRef]) -> list[RepoRef]:
    unique: dict[tuple[str, str], RepoRef] = {}
    for repo in repos:
        unique.setdefault((repo.owner.lower(), repo.name.lower()), repo)
    return list(unique.values())


def _split_entries(text: str) -> list[str]:
    return text.replace(",", " ").split()


def _parse_repos(text: str) -> list[RepoRef]:
    repos = _unique_repos([_parse_entry(entry) for entry in _split_entries(text)])
    if len(repos) > MAX_REPOS:
        raise TooManyRepos("Compare up to 3 repositories at a time")
    return repos


def parse_repo_input(text: str) -> ParsedInput:
    if "/" not in text:
        return ParsedInput(repos=[], search=text)
    return ParsedInput(repos=_parse_repos(text), search=None)
