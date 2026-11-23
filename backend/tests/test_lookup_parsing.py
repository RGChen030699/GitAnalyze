from lookup.parsing import ParsedInput, RepoRef, parse_repo_input


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


def test_L1_accepts_git_ssh_url() -> None:
    parsed = parse_repo_input("git@github.com:vercel/next.js.git")

    assert parsed.repos == [RepoRef("vercel", "next.js")]


def test_L3_treats_bare_name_as_search() -> None:
    parsed = parse_repo_input("zustand")

    assert parsed == ParsedInput(repos=[], search="zustand")


def test_L2_accepts_space_separated_entries() -> None:
    parsed = parse_repo_input("vercel/next.js facebook/react")

    assert parsed.repos == [RepoRef("vercel", "next.js"), RepoRef("facebook", "react")]


def test_L2_accepts_comma_separated_entries() -> None:
    parsed = parse_repo_input("vercel/next.js,facebook/react")

    assert parsed.repos == [RepoRef("vercel", "next.js"), RepoRef("facebook", "react")]


def test_L2_accepts_newline_separated_entries() -> None:
    parsed = parse_repo_input("vercel/next.js\nfacebook/react")

    assert parsed.repos == [RepoRef("vercel", "next.js"), RepoRef("facebook", "react")]
