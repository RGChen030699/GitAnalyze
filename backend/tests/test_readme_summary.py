"""What a repository is about: its README's first real paragraph (pure, no network)."""

from repositories.overview import readme_summary


def test_overview_first_plain_paragraph_after_title_and_badges() -> None:
    text = (
        "# Click\n\n"
        "[![PyPI](https://img.shields.io/pypi/v/click.svg)](https://pypi.org/project/click/) "
        "![CI](https://github.com/pallets/click/badge.svg)\n\n"
        "Click is a Python package for creating beautiful command line interfaces in a "
        "composable way with as little code as necessary.\n\n"
        "## Installing\n\npip install click\n"
    )
    assert readme_summary(text) == (
        "Click is a Python package for creating beautiful command line interfaces in a "
        "composable way with as little code as necessary."
    )


def test_overview_links_and_emphasis_keep_only_their_text() -> None:
    text = (
        "A **fast** `toml` parser for [Rust](https://rust-lang.org), with _no_ unsafe code at all."
    )
    assert readme_summary(text) == "A fast toml parser for Rust, with no unsafe code at all."


def test_overview_html_blocks_and_centered_logos_are_skipped() -> None:
    text = (
        '<p align="center"><img src="logo.png" width="200"></p>\n\n'
        '<div align="center">\n<a href="x">Docs</a> | <a href="y">Blog</a>\n</div>\n\n'
        "Plannotator is the workspace to stay in the loop with your coding agents and review "
        "what they produce.\n"
    )
    assert readme_summary(text).startswith("Plannotator is the workspace")


def test_overview_inline_html_tags_are_removed_from_the_paragraph() -> None:
    text = (
        "<b>Deno</b> is a modern runtime for JavaScript and TypeScript that is secure by default."
    )
    assert readme_summary(text) == (
        "Deno is a modern runtime for JavaScript and TypeScript that is secure by default."
    )


def test_overview_code_blocks_tables_and_quotes_are_skipped() -> None:
    text = (
        "```bash\nnpm install widget and some other words here to be long\n```\n\n"
        "| a | b |\n|---|---|\n| 1 | 2 |\n\n"
        "> Note: this is a fork of something else that we maintain separately.\n\n"
        "Widget draws charts in the terminal using plain text characters only.\n"
    )
    assert (
        readme_summary(text)
        == "Widget draws charts in the terminal using plain text characters only."
    )


def test_overview_lines_of_one_paragraph_are_joined() -> None:
    text = "Widget draws charts\nin the terminal using\nplain text characters.\n"
    assert (
        readme_summary(text) == "Widget draws charts in the terminal using plain text characters."
    )


def test_overview_long_paragraph_is_cut_at_a_sentence_within_400_characters() -> None:
    sentence = "This sentence is exactly about sixty characters long, okay. "
    summary = readme_summary(sentence * 10)
    assert summary is not None
    assert len(summary) <= 400
    assert summary.endswith("okay.")


def test_overview_long_paragraph_without_sentences_is_cut_at_a_word() -> None:
    summary = readme_summary("word " * 200)
    assert summary is not None
    assert len(summary) <= 401
    assert summary.endswith("word…")


def test_overview_no_usable_paragraph_returns_none() -> None:
    assert readme_summary("# Title\n\n![logo](x.png)\n\n## Usage\n") is None
    assert readme_summary("") is None
    assert readme_summary("Too short.") is None


def test_overview_front_matter_and_bom_are_ignored() -> None:
    text = "﻿---\ntitle: x\n---\r\n\r\nWidget draws charts in the terminal using plain text.\r\n"
    assert readme_summary(text) == "Widget draws charts in the terminal using plain text."
