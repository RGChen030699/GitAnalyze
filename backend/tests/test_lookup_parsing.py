from lookup.parsing import RepoRef, parse_repo_input


def test_L1_accepts_https_url() -> None:
    parsed = parse_repo_input("https://github.com/vercel/next.js")

    assert parsed.repos == [RepoRef("vercel", "next.js")]


def test_L1_accepts_owner_repo_name() -> None:
    parsed = parse_repo_input("vercel/next.js")

    assert parsed.repos == [RepoRef("vercel", "next.js")]


def test_L1_accepts_url_without_scheme() -> None:
    parsed = parse_repo_input("github.com/vercel/next.js")

    assert parsed.repos == [RepoRef("vercel", "next.js")]


def test_L1_accepts_www_url() -> None:
    parsed = parse_repo_input("www.github.com/vercel/next.js")

    assert parsed.repos == [RepoRef("vercel", "next.js")]


def test_L1_ignores_tree_path() -> None:
    parsed = parse_repo_input("https://github.com/anthropics/skills/tree/main/skills")

    assert parsed.repos == [RepoRef("anthropics", "skills")]


def test_L1_strips_git_suffix() -> None:
    parsed = parse_repo_input("https://github.com/vercel/next.js.git")

    assert parsed.repos == [RepoRef("vercel", "next.js")]
