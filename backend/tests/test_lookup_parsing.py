from lookup.parsing import RepoRef, parse_repo_input


def test_L1_accepts_https_url() -> None:
    parsed = parse_repo_input("https://github.com/vercel/next.js")

    assert parsed.repos == [RepoRef("vercel", "next.js")]
