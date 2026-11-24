"""F4 detection rules: pure functions, no network or database."""

from pathlib import Path
from typing import Any

import pytest
from ai_capabilities.rules import (
    AGENT_RULE,
    NO_DESCRIPTION,
    NO_HEADER,
    SKILL_RULE,
    TreeEntry,
    assemble,
    files_to_read,
    is_vendored,
    manifest_skill_folders,
    mcp_server_rule,
    parse_skill_header,
    readme_mentions,
    skill_scripts,
    standard_problems,
)

FIXTURE = Path(__file__).parent / "fixtures" / "github" / "ai_anthropics_skills.txt"
SHA_A = "a" * 40
SHA_B = "b" * 40


def blob(path: str, sha: str = "0" * 40) -> TreeEntry:
    return TreeEntry(path=path, type="blob", sha=sha)


def skill_md(name: str, description: str = "Does a thing.") -> str:
    return f"---\nname: {name}\ndescription: {description}\n---\n\n# Body\n"


def load_fixture() -> tuple[list[TreeEntry], dict[str, str]]:
    """Parse the recorded anthropics/skills tree and SKILL.md headers."""
    entries: list[TreeEntry] = []
    files: dict[str, str] = {}
    section, current = "", ""
    for line in FIXTURE.read_text().splitlines():
        if line.startswith("#") and section != "[files]":
            continue
        if line in ("[tree]", "[files]"):
            section = line
        elif section == "[tree]":
            kind, sha, path = line.split(" ", 2)
            entries.append(TreeEntry(path, "blob" if kind == "b" else "tree", sha))
        elif line.startswith("=== "):
            current = line[4:]
            files[current] = ""
        else:
            files[current] += line + "\n"
    return entries, files


def panel(entries: list[TreeEntry], files: dict[str, str], **kwargs: Any) -> dict[str, Any]:
    return assemble(entries, files, owner_type=kwargs.get("owner_type", "Organization"))


# --- Recorded repository: anthropics/skills ---


def test_F4_anthropics_skills_lists_19_skills_and_puts_template_under_possible() -> None:
    entries, files = load_fixture()
    result = panel(entries, files)

    names = [skill["name"] for skill in result["skills"]]
    assert len(names) == 19
    assert "pdf" in names and "skill-creator" in names and "claude-api" in names
    assert "template-skill" not in names
    assert result["possible_skills"] == [
        {
            "path": "template/SKILL.md",
            "reason": "Inside a template, example or test folder",
            "rule": result["possible_skills"][0]["rule"],
        }
    ]
    assert result["has_ai"] is True
    assert result["publisher"] == "organization"


def test_F4_anthropics_skills_each_skill_has_name_description_and_folder() -> None:
    entries, files = load_fixture()
    pdf = next(s for s in panel(entries, files)["skills"] if s["name"] == "pdf")

    assert pdf["description"].startswith("Use this skill whenever the user wants to do anything")
    assert pdf["folder"] == "skills/pdf"
    assert pdf["path"] == "skills/pdf/SKILL.md"
    assert pdf["rule"] == SKILL_RULE
    assert pdf["scripts"] == ["scripts/check_bounding_boxes.py", "scripts/check_fillable_fields.py"]


def test_F4_folded_and_literal_descriptions_are_read() -> None:
    entries, files = load_fixture()
    skills = {s["name"]: s for s in panel(entries, files)["skills"]}

    assert skills["academy-guide"]["description"].startswith("Stop and check this skill before")
    assert "\n" not in skills["academy-guide"]["description"]  # folded ">" joins lines
    assert skills["claude-api"]["description"].startswith("Reference for the Claude API")


def test_F4_skills_without_script_files_have_no_scripts() -> None:
    entries, files = load_fixture()
    skills = {s["name"]: s for s in panel(entries, files)["skills"]}

    assert skills["brand-guidelines"]["scripts"] == []
    assert len([s for s in skills.values() if s["scripts"]]) == 11


# --- Step 2: vendored folders ---


@pytest.mark.parametrize(
    "path",
    [
        "node_modules/x/SKILL.md",
        "web/node_modules/x/SKILL.md",
        "vendor/a.py",
        "dist/SKILL.md",
        "pkg/build/SKILL.md",
        ".git/config",
        "lib/site-packages/x/SKILL.md",
        "x/__pycache__/a.pyc",
    ],
)
def test_F4_vendored_paths_are_skipped(path: str) -> None:
    assert is_vendored(path)


@pytest.mark.parametrize("path", ["skills/build-tools/SKILL.md", "vendors.md", "distance/x.py"])
def test_F4_similar_names_are_not_vendored(path: str) -> None:
    assert not is_vendored(path)


def test_F4_skill_md_only_under_node_modules_shows_no_skills() -> None:
    entries = [blob("node_modules/pkg/skills/x/SKILL.md", SHA_A)]
    result = panel(entries, {"node_modules/pkg/skills/x/SKILL.md": skill_md("x")})

    assert result["skills"] == []
    assert result["possible_skills"] == []
    assert result["has_ai"] is False


# --- Level 1: skills, headers, duplicates ---


def test_F4_parse_header_tolerates_bom_and_windows_line_endings() -> None:
    text = "﻿---\r\nname: x\r\ndescription: Does x.\r\n---\r\nBody\r\n"
    assert parse_skill_header(text) == {"name": "x", "description": "Does x."}


def test_F4_parse_header_without_front_matter_reports_no_header() -> None:
    assert parse_skill_header("# Just a heading\n") == NO_HEADER


def test_F4_parse_header_without_description_reports_it() -> None:
    assert parse_skill_header("---\nname: x\n---\n") == NO_DESCRIPTION
    assert parse_skill_header("---\nname: x\ndescription: '  '\n---\n") == NO_DESCRIPTION


def test_F4_parse_header_with_broken_yaml_reports_it() -> None:
    assert parse_skill_header("---\nname: [x\n---\n") == "Header isn't valid YAML"


def test_F4_skill_without_header_is_a_possible_skill_with_reason() -> None:
    entries = [blob("skills/x/SKILL.md", SHA_A)]
    result = panel(entries, {"skills/x/SKILL.md": "# x\n"})

    assert result["skills"] == []
    assert [(p["path"], p["reason"]) for p in result["possible_skills"]] == [
        ("skills/x/SKILL.md", "No header found")
    ]
    assert result["has_ai"] is False


def test_F4_lower_case_skill_md_is_only_a_possible_skill() -> None:
    entries = [blob("skills/x/skill.md", SHA_A)]
    result = panel(entries, {"skills/x/skill.md": skill_md("x")})

    assert result["skills"] == []
    assert result["possible_skills"][0]["reason"] == "Named skill.md, not SKILL.md"


def test_F4_unreadable_skill_file_is_a_possible_skill() -> None:
    result = panel([blob("skills/x/SKILL.md", SHA_A)], {})
    assert result["possible_skills"][0]["reason"] == "Couldn't read the file"


def test_F4_same_skill_in_two_folders_counts_once_and_lists_both_paths() -> None:
    entries = [blob(".claude/skills/x/SKILL.md", SHA_A), blob(".agents/skills/x/SKILL.md", SHA_A)]
    files = {".agents/skills/x/SKILL.md": skill_md("x")}

    skills = panel(entries, files)["skills"]

    assert len(skills) == 1
    assert skills[0]["path"] == ".agents/skills/x/SKILL.md"
    assert skills[0]["other_paths"] == [".claude/skills/x/SKILL.md"]


def test_F4_files_to_read_fetches_one_copy_of_each_skill() -> None:
    entries = [
        blob(".claude/skills/x/SKILL.md", SHA_A),
        blob(".agents/skills/x/SKILL.md", SHA_A),
        blob("skills/y/SKILL.md", SHA_B),
        blob("node_modules/z/SKILL.md", "c" * 40),
        blob("README.md"),
        blob("package.json"),
        blob("docs/readme.md"),
    ]
    assert files_to_read(entries) == [
        ".agents/skills/x/SKILL.md",
        "skills/y/SKILL.md",
        "README.md",
        "package.json",
    ]


# --- Trust signals ---


def test_F4_skill_folder_with_a_script_shows_it() -> None:
    paths = ["skills/forms/SKILL.md", "skills/forms/scripts/fill_form.py", "skills/forms/a.md"]
    assert skill_scripts("skills/forms", paths) == ["scripts/fill_form.py"]


def test_F4_scripts_folder_counts_whatever_the_extension() -> None:
    paths = ["skills/x/SKILL.md", "skills/x/scripts/run", "skills/x/lib/tool.ps1"]
    assert skill_scripts("skills/x", paths) == ["lib/tool.ps1", "scripts/run"]


def test_F4_root_skill_only_counts_root_level_scripts() -> None:
    paths = ["SKILL.md", "install.sh", "src/app.ts", "scripts/setup"]
    assert skill_scripts("", paths) == ["install.sh", "scripts/setup"]


def test_F4_panel_marks_the_skill_whose_folder_has_scripts() -> None:
    entries = [blob("skills/forms/SKILL.md", SHA_A), blob("skills/forms/scripts/fill_form.py")]
    skills = panel(entries, {"skills/forms/SKILL.md": skill_md("forms")})["skills"]
    assert skills[0]["scripts"] == ["scripts/fill_form.py"]


def test_F4_standard_format_passes_for_a_matching_name() -> None:
    assert standard_problems("pdf-tools", "Does PDFs.", "skills/pdf-tools") == []


def test_F4_standard_format_lists_each_problem() -> None:
    assert standard_problems("PDF Tools", "x" * 1025, "skills/pdf") == [
        "name must be 1–64 lowercase letters, digits or hyphens",
        "name doesn't match the folder name",
        "description is over 1,024 characters",
    ]


def test_F4_personal_account_publisher() -> None:
    assert panel([], {}, owner_type="User")["publisher"] == "personal"


# --- Level 2: agent files ---


def test_F4_only_claude_and_agents_md_is_set_up_for_agents_with_no_skills() -> None:
    entries = [blob("CLAUDE.md"), blob("AGENTS.md"), blob("src/main.py")]
    result = panel(entries, {})

    assert result["skills"] == []
    assert [a["path"] for a in result["agent_files"]] == ["AGENTS.md", "CLAUDE.md"]
    assert result["agent_files"][0]["rule"] == AGENT_RULE
    assert result["has_ai"] is True


@pytest.mark.parametrize(
    "path",
    [
        "GEMINI.md",
        ".cursorrules",
        ".cursor/rules/style.mdc",
        ".github/copilot-instructions.md",
        ".github/instructions/python.instructions.md",
        "packages/api/AGENTS.md",
    ],
)
def test_F4_agent_setup_files(path: str) -> None:
    assert [a["path"] for a in panel([blob(path)], {})["agent_files"]] == [path]


def test_F4_mcp_json_means_the_repository_uses_mcp_not_that_it_is_a_server() -> None:
    result = panel([blob(".mcp.json")], {})

    assert [u["path"] for u in result["uses_mcp"]] == [".mcp.json"]
    assert result["mcp_server"] == []
    assert result["has_ai"] is False


# --- Level 3: MCP server ---


def test_F4_package_json_depending_on_the_mcp_sdk_is_an_mcp_server() -> None:
    text = '{"dependencies": {"@modelcontextprotocol/sdk": "^1.0.0", "zod": "^3"}}'
    result = panel([blob("package.json")], {"package.json": text})

    assert [(m["path"], m["rule"]) for m in result["mcp_server"]] == [
        ("package.json", "package.json depends on @modelcontextprotocol/sdk")
    ]
    assert result["has_ai"] is True


def test_F4_server_json_with_the_official_schema() -> None:
    text = '{"$schema": "https://static.modelcontextprotocol.io/schemas/2025-07-09/server.schema.json"}'
    assert mcp_server_rule("server.json", text) == "server.json uses the official MCP server schema"


@pytest.mark.parametrize(
    ("path", "text"),
    [
        ("pyproject.toml", '[project]\ndependencies = ["fastmcp>=2.0", "httpx"]\n'),
        ("pyproject.toml", '[tool.poetry.dependencies]\npython = "^3.11"\nmcp = {version = "1"}\n'),
        ("requirements.txt", "# tools\nhttpx==0.27\nmcp[cli]>=1.2\n"),
        ("requirements-dev.txt", "-r requirements.txt\nFastMCP==2.3\n"),
    ],
)
def test_F4_python_dependencies_on_mcp_or_fastmcp(path: str, text: str) -> None:
    assert mcp_server_rule(path, text) == "Python dependencies include mcp or fastmcp"


@pytest.mark.parametrize(
    ("path", "text"),
    [
        ("package.json", '{"devDependencies": {"@modelcontextprotocol/sdk": "1"}}'),
        ("package.json", "not json"),
        ("requirements.txt", "mcpx==1\nmy-mcp-tool==2\n"),
        ("pyproject.toml", "not = [toml"),
        ("server.json", '{"$schema": "https://example.com/schema.json"}'),
    ],
)
def test_F4_near_misses_are_not_mcp_servers(path: str, text: str) -> None:
    assert mcp_server_rule(path, text) is None


# --- Level 4: README hint ---


def test_F4_readme_mentions_are_found_case_insensitively() -> None:
    text = "Works with claude code and any mcp SERVER. Not about codecs."
    assert readme_mentions(text) == ["Claude Code", "MCP server"]


def test_F4_readme_hint_alone_does_not_count_as_ai_capabilities() -> None:
    result = panel([blob("README.md")], {"README.md": "An agent skill for Copilot."})

    assert result["readme_mentions"] == {
        "path": "README.md",
        "phrases": ["agent skill", "Copilot"],
        "rule": result["readme_mentions"]["rule"],
    }
    assert result["has_ai"] is False


# --- Plugins ---


def test_F4_plugin_manifest_skill_paths() -> None:
    text = '{"plugins": [{"skills": ["./skills/xlsx", "./skills/pdf/"]}]}'
    assert manifest_skill_folders(text) == {"skills/xlsx", "skills/pdf"}


def test_F4_skills_listed_in_a_plugin_manifest_are_noted() -> None:
    entries = [
        blob(".claude-plugin/marketplace.json"),
        blob("skills/pdf/SKILL.md", SHA_A),
        blob("skills/other/SKILL.md", SHA_B),
    ]
    files = {
        ".claude-plugin/marketplace.json": '{"plugins": [{"skills": ["./skills/pdf"]}]}',
        "skills/pdf/SKILL.md": skill_md("pdf"),
        "skills/other/SKILL.md": skill_md("other"),
    }
    skills = {s["name"]: s for s in panel(entries, files)["skills"]}

    assert skills["pdf"]["in_manifest"] is True
    assert skills["other"]["in_manifest"] is False


# --- Nothing found ---


def test_F4_repository_with_no_ai_signals() -> None:
    result = panel([blob("README.md"), blob("src/main.go")], {"README.md": "A web server."})

    assert result["has_ai"] is False
    assert result["skills"] == result["agent_files"] == result["mcp_server"] == []
    assert result["readme_mentions"] is None


def test_F4_panel_never_contains_a_score_or_safe_label() -> None:
    entries, files = load_fixture()
    text = str(panel(entries, files)).lower()
    for word in ("score", "rating", "safe", "verdict"):
        assert word not in text


# --- Found on the live anthropics/skills scan ---


def test_F4_data_files_in_a_scripts_folder_are_not_scripts() -> None:
    paths = [
        "skills/docx/scripts/office/validate.py",
        "skills/docx/scripts/office/schemas/wml.xsd",
        "skills/docx/scripts/templates/people.xml",
        "skills/docx/scripts/requirements.txt",
        "skills/docx/scripts/bundle.tar.gz",
        "skills/docx/scripts/run",
    ]
    assert skill_scripts("skills/docx", paths) == ["scripts/office/validate.py", "scripts/run"]


def test_F4_a_skills_own_dependency_files_do_not_make_the_repo_an_mcp_server() -> None:
    entries = [
        blob("skills/mcp-builder/SKILL.md", SHA_A),
        blob("skills/mcp-builder/scripts/requirements.txt"),
    ]
    files = {
        "skills/mcp-builder/SKILL.md": skill_md("mcp-builder"),
        "skills/mcp-builder/scripts/requirements.txt": "mcp>=1.0\n",
    }
    assert panel(entries, files)["mcp_server"] == []
