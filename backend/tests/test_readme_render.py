"""The README section: Markdown rendered to safe HTML, links and images pointed at GitHub."""

from repositories.readme_render import MAX_MARKDOWN_CHARS, TRUNCATED_NOTE, render_readme

REPO = "octo/kit"


def render(text: str, path: str = "README.md") -> str:
    return render_readme(text, REPO, "main", path)


def test_readme_headings_lists_code_and_tables_are_rendered() -> None:
    html = render(
        "# Kit\n\nA *tool*.\n\n- one\n- two\n\n```py\nprint(1)\n```\n\n"
        "| a | b |\n|---|---|\n| 1 | ~~2~~ |\n"
    )
    assert "<h1>Kit</h1>" in html
    assert "<em>tool</em>" in html
    assert "<li>one</li>" in html
    assert "<pre><code" in html and "print(1)" in html
    assert "<table>" in html and "<th>a</th>" in html
    assert "<s>2</s>" in html or "<del>2</del>" in html


def test_readme_scripts_styles_and_event_handlers_are_removed() -> None:
    html = render(
        '<script>alert("x")</script>\n\n<style>body{}</style>\n\n'
        '<p onclick="steal()">Hi</p>\n\n[click](javascript:alert(1))\n'
    )
    assert "<script" not in html and "alert(" not in html
    assert "<style" not in html and "body{}" not in html
    assert "onclick" not in html
    assert "javascript:" not in html
    assert "Hi" in html


def test_readme_iframes_forms_and_inputs_are_removed() -> None:
    html = render('<iframe src="https://x.test"></iframe>\n\n<form><input name="q"></form>\n')
    assert "<iframe" not in html and "<form" not in html and "<input" not in html


def test_readme_raw_html_blocks_keep_their_content() -> None:
    html = render(
        '<p align="center"><strong>Fast</strong> builds</p>\n\n'
        "<details><summary>More</summary>Hidden</details>\n"
    )
    assert "<strong>Fast</strong> builds" in html
    assert "<details>" in html and "<summary>More</summary>" in html


def test_readme_links_open_safely() -> None:
    html = render("[Docs](https://docs.example.com)\n")
    assert 'href="https://docs.example.com"' in html
    assert 'rel="noopener noreferrer nofollow"' in html


def test_readme_relative_links_point_at_the_file_on_github() -> None:
    html = render(
        "[Guide](docs/guide.md) and [Top](#install) and [Up](../LICENSE)\n", path="pkg/README.md"
    )
    assert 'href="https://github.com/octo/kit/blob/main/pkg/docs/guide.md"' in html
    assert 'href="#install"' in html
    assert 'href="https://github.com/octo/kit/blob/main/LICENSE"' in html


def test_readme_relative_images_load_from_the_repository() -> None:
    html = render("![Screenshot](./img/shot.png)\n")
    assert (
        '<img src="https://raw.githubusercontent.com/octo/kit/main/img/shot.png" alt="Screenshot"'
        in html
    )


def test_readme_github_hosted_images_are_kept() -> None:
    url = "https://github.com/user-attachments/assets/1234"
    html = render(f'<img src="{url}" alt="Demo" width="600">\n')
    assert f'src="{url}"' in html
    assert 'width="600"' in html


def test_readme_images_from_other_sites_become_their_caption() -> None:
    html = render(
        "[![PyPI](https://img.shields.io/pypi/v/kit.svg)](https://pypi.org/project/kit/) "
        '<img src="https://tracker.example.com/pixel.gif" alt="">\n'
    )
    assert "img.shields.io" not in html and "tracker.example.com" not in html
    assert '<span class="img-alt">PyPI</span>' in html
    assert "<img" not in html


def test_readme_longer_than_the_cap_is_cut_with_a_note() -> None:
    line = "word " * 19 + "\n"
    html = render(line * (MAX_MARKDOWN_CHARS // len(line) + 50))
    assert TRUNCATED_NOTE in html
    assert html.count("word") < (MAX_MARKDOWN_CHARS // 5) + 50


def test_readme_empty_text_renders_nothing() -> None:
    assert render("") == ""
