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
    assert (readme_summary(text) or "").startswith("Plannotator is the workspace")


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


# --- Shapes found in real READMEs (checked 2026-11-24) ---


def test_overview_heading_directly_above_its_paragraph_anthropics_skills() -> None:
    text = (
        "> **Note:** This repository contains Anthropic's implementation of skills for Claude.\n\n"
        "[![skills.sh](https://skills.sh/b/anthropics/skills)](https://skills.sh/anthropics/skills)\n\n"
        "# Skills\n"
        "Skills are folders of instructions, scripts, and resources that Claude loads dynamically "
        "to improve performance on specialized tasks.\n\n"
        "For more information, check out:\n"
        "- [What are skills?](https://support.claude.com/x)\n"
        "- [Using skills in Claude](https://support.claude.com/y)\n"
    )
    assert readme_summary(text) == (
        "Skills are folders of instructions, scripts, and resources that Claude loads dynamically "
        "to improve performance on specialized tasks."
    )


def test_overview_a_line_that_introduces_a_list_is_not_a_summary() -> None:
    text = (
        "For more information about this project, check out:\n- [Docs](x)\n- [Blog](y)\n\n"
        "Widget draws charts in the terminal using plain text characters only.\n"
    )
    assert (
        readme_summary(text)
        == "Widget draws charts in the terminal using plain text characters only."
    )


def test_overview_paragraph_stops_where_a_list_starts() -> None:
    text = "Widget draws charts in the terminal using plain text characters.\n- fast\n- small\n"
    assert (
        readme_summary(text) == "Widget draws charts in the terminal using plain text characters."
    )


def test_overview_reference_style_badges_and_definitions_are_skipped_denoland_deno() -> None:
    text = (
        "# Deno\n\n"
        "![Twitter badge][Twitter link] ![Bluesky badge][Bluesky link] ![Discord badge][Discord link]\n\n"
        "[Twitter link]: https://twitter.com/deno_land\n[Discord link]: https://discord.gg/deno\n\n"
        "Deno is a JavaScript, TypeScript, and WebAssembly runtime with secure defaults and a "
        "great developer experience.\n"
    )
    assert readme_summary(text) == (
        "Deno is a JavaScript, TypeScript, and WebAssembly runtime with secure defaults and a "
        "great developer experience."
    )
