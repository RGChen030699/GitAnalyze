"""F4 rules: which AI capabilities a repository has, and the trust signals for each skill.

Pure functions over the file tree and file texts. They never produce a score, rating or "safe"
label (PRD §6): only what was found, the rule that matched and the file it came from.
"""

import json
import re
import tomllib
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from posixpath import basename, dirname
from typing import Any

import yaml

VENDORED = ("node_modules", "vendor", "dist", "build", ".git", "site-packages", "__pycache__")
SAMPLE_FOLDERS = {"template", "templates", "example", "examples", "test", "tests"}
SCRIPT_EXTENSIONS = (".py", ".sh", ".js", ".ts", ".rb", ".ps1")
SKILL_FILE = "SKILL.md"
AGENT_FILE_NAMES = {"CLAUDE.md", "AGENTS.md", "GEMINI.md", ".cursorrules"}
COPILOT_INSTRUCTIONS = re.compile(r"^\.github/instructions/[^/]+\.instructions\.md$")
PLUGIN_MANIFESTS = (".claude-plugin/marketplace.json", ".claude-plugin/plugin.json", "plugin.json")
DEPENDENCY_FILE = re.compile(
    r"^(package\.json|pyproject\.toml|requirements[^/]*\.txt|server\.json)$"
)
MCP_SCHEMA_HOST = "static.modelcontextprotocol.io/schemas/"
MCP_NODE_SDK = "@modelcontextprotocol/sdk"
MCP_PYTHON_PACKAGES = {"mcp", "fastmcp"}
README_PHRASES = (
    "Claude Code",
    "agent skill",
    "SKILL.md",
    "MCP server",
    "Cursor rules",
    "Codex",
    "Copilot",
    "plugin marketplace",
)
SKILL_NAME = re.compile(r"^[a-z0-9-]{1,64}$")
MAX_DESCRIPTION = 1024
MAX_HEADER_CHARS = 20_000
MAX_SKILL_FILES = 100
MAX_DEPENDENCY_FILES = 20

# The rule behind each finding, shown from its info icon (F4 acceptance: "the rule that matched").
SKILL_RULE = "A file named SKILL.md whose header has a description (Agent Skills format)"
POSSIBLE_RULE = "A SKILL.md that has no valid header or description, or sits in a sample folder"
AGENT_RULE = (
    "A setup file for AI coding agents: CLAUDE.md, AGENTS.md, GEMINI.md, Cursor rules "
    "or Copilot instructions"
)
USES_MCP_RULE = ".mcp.json lists MCP servers this repository uses; it isn't one itself"
README_RULE = "README.md mentions AI tools. A hint, not proof"
MCP_SCHEMA_RULE = "server.json uses the official MCP server schema"
MCP_NODE_RULE = "package.json depends on @modelcontextprotocol/sdk"
MCP_PYTHON_RULE = "Python dependencies include mcp or fastmcp"

NO_HEADER = "No header found"
INVALID_HEADER = "Header isn't valid YAML"
NO_DESCRIPTION = "Header has no description"
SAMPLE_FOLDER = "Inside a template, example or test folder"
LOWER_CASE_NAME = "Named skill.md, not SKILL.md"
UNREADABLE = "Couldn't read the file"

Panel = dict[str, Any]


@dataclass(frozen=True)
class TreeEntry:
    path: str
    type: str  # "blob" or "tree"
    sha: str


# --- Step 2: vendored and generated folders ---


def is_vendored(path: str) -> bool:
    """True when any folder on the path is a vendored or generated one."""
    return any(part in VENDORED for part in path.split("/")[:-1])


def _blobs(entries: Iterable[TreeEntry]) -> list[TreeEntry]:
    return [e for e in entries if e.type == "blob" and not is_vendored(e.path)]


# --- Level 1: SKILL.md files ---


def _skill_groups(blobs: Sequence[TreeEntry]) -> list[list[str]]:
    """SKILL.md paths grouped by blob sha; the first path in each group is the one we read."""
    groups: dict[str, list[str]] = {}
    for entry in blobs:
        if basename(entry.path) == SKILL_FILE:
            groups.setdefault(entry.sha, []).append(entry.path)
    ordered = [sorted(paths, key=lambda p: (len(p), p)) for paths in groups.values()]
    return sorted(ordered, key=lambda paths: paths[0])


def parse_skill_header(text: str) -> dict[str, str] | str:
    """The header's name and description, or the reason it can't be read."""
    text = text.lstrip("﻿").replace("\r\n", "\n")[:MAX_HEADER_CHARS]
    match = re.match(r"---\n(.*?)\n---(\n|$)", text, re.DOTALL)
    if not match:
        return NO_HEADER
    try:
        header = yaml.safe_load(match.group(1))
    except yaml.YAMLError:
        return INVALID_HEADER
    if not isinstance(header, dict):
        return INVALID_HEADER
    description = header.get("description")
    if not isinstance(description, str) or not description.strip():
        return NO_DESCRIPTION
    name = header.get("name")
    return {"name": str(name) if name is not None else "", "description": description.strip()}


def standard_problems(name: str, description: str, folder: str) -> list[str]:
    """Where a skill departs from the Agent Skills specification; empty when it follows it."""
    problems = []
    if not SKILL_NAME.match(name):
        problems.append("name must be 1–64 lowercase letters, digits or hyphens")
    if folder and name != basename(folder):
        problems.append("name doesn't match the folder name")
    if len(description) > MAX_DESCRIPTION:
        problems.append("description is over 1,024 characters")
    return problems


def skill_scripts(folder: str, paths: Iterable[str]) -> list[str]:
    """Files in the skill's folder that can run: script extensions, or anything under scripts/."""
    prefix = f"{folder}/" if folder else ""
    found = []
    for path in paths:
        if not path.startswith(prefix):
            continue
        relative = path[len(prefix) :]
        if not folder and "/" in relative and not relative.startswith("scripts/"):
            continue  # a skill at the repository root: only its own top level and scripts/
        if relative.endswith(SCRIPT_EXTENSIONS) or _extensionless_script(relative):
            found.append(relative)
    return sorted(found)


def _extensionless_script(relative: str) -> bool:
    """A file with no extension in scripts/ is likely an executable; data files are not."""
    return relative.startswith("scripts/") and "." not in basename(relative)


def manifest_skill_folders(text: str) -> set[str]:
    """Skill paths listed under any "skills" key of a plugin or marketplace manifest."""
    try:
        data = json.loads(text)
    except ValueError:
        return set()
    folders: set[str] = set()

    def walk(node: Any) -> None:
        if isinstance(node, dict):
            for key, value in node.items():
                if key == "skills" and isinstance(value, list):
                    folders.update(_clean(v) for v in value if isinstance(v, str))
                walk(value)
        elif isinstance(node, list):
            for item in node:
                walk(item)

    walk(data)
    return folders - {""}


def _clean(path: str) -> str:
    return path.removeprefix("./").strip("/")


def _in_manifest(folder: str, listed: set[str]) -> bool:
    return any(folder == entry or folder.startswith(f"{entry}/") for entry in listed)


def _possible(path: str, reason: str) -> dict[str, str]:
    return {"path": path, "reason": reason, "rule": POSSIBLE_RULE}


def _in_sample_folder(path: str) -> bool:
    return any(part in SAMPLE_FOLDERS for part in path.split("/")[:-1])


def _skills(
    blobs: Sequence[TreeEntry], files: Mapping[str, str | None], listed: set[str]
) -> tuple[list[Panel], list[dict[str, str]]]:
    paths = [entry.path for entry in blobs]
    skills: list[Panel] = []
    possible: list[dict[str, str]] = []
    for group in _skill_groups(blobs):
        path, others = group[0], group[1:]
        if _in_sample_folder(path):
            possible.append(_possible(path, SAMPLE_FOLDER))
            continue
        text = files.get(path)
        header = UNREADABLE if text is None else parse_skill_header(text)
        if isinstance(header, str):
            possible.append(_possible(path, header))
            continue
        folder = dirname(path)
        name = header["name"] or basename(folder)
        problems = standard_problems(name, header["description"], folder)
        skills.append(
            {
                "name": name,
                "description": header["description"],
                "folder": folder,
                "path": path,
                "other_paths": others,
                "scripts": skill_scripts(folder, paths),
                "standard": "; ".join(problems) or None,
                "in_manifest": _in_manifest(folder, listed),
                "rule": SKILL_RULE,
            }
        )
    lower_case = [p for p in paths if basename(p) == "skill.md"]
    possible += [_possible(p, LOWER_CASE_NAME) for p in lower_case]
    return skills, possible


# --- Level 2: agent setup files ---


def _is_agent_file(path: str) -> bool:
    return (
        basename(path) in AGENT_FILE_NAMES
        or path.startswith(".cursor/rules/")
        or path == ".github/copilot-instructions.md"
        or bool(COPILOT_INSTRUCTIONS.match(path))
    )


# --- Level 3: MCP server ---


def _python_name(requirement: str) -> str:
    match = re.match(r"\s*([A-Za-z0-9][A-Za-z0-9._-]*)", requirement)
    return match.group(1).lower().replace("_", "-") if match else ""


def _python_dependencies(path: str, text: str) -> list[str]:
    if basename(path) != "pyproject.toml":
        lines = (line.strip() for line in text.splitlines())
        return [line for line in lines if line and not line.startswith(("#", "-"))]
    try:
        data = tomllib.loads(text)
    except tomllib.TOMLDecodeError:
        return []
    project = data.get("project", {})
    optional = project.get("optional-dependencies", {})
    poetry = data.get("tool", {}).get("poetry", {}).get("dependencies", {})
    return [
        *project.get("dependencies", []),
        *(dep for group in optional.values() for dep in group),
        *poetry.keys(),
    ]


def mcp_server_rule(path: str, text: str) -> str | None:
    """The rule that makes this file evidence of an MCP server, or None."""
    name = basename(path)
    if name in ("server.json", "package.json"):
        try:
            data = json.loads(text)
        except ValueError:
            return None
        if not isinstance(data, dict):
            return None
        if name == "server.json":
            return MCP_SCHEMA_RULE if MCP_SCHEMA_HOST in str(data.get("$schema", "")) else None
        return MCP_NODE_RULE if MCP_NODE_SDK in (data.get("dependencies") or {}) else None
    names = {_python_name(dep) for dep in _python_dependencies(path, text)}
    return MCP_PYTHON_RULE if names & MCP_PYTHON_PACKAGES else None


# --- Level 4: README hint ---


def readme_mentions(text: str) -> list[str]:
    lowered = text.lower()
    return [phrase for phrase in README_PHRASES if phrase.lower() in lowered]


def _root_readme(blobs: Sequence[TreeEntry]) -> str | None:
    return next((e.path for e in blobs if e.path.lower() == "readme.md"), None)


def _skill_folders(blobs: Sequence[TreeEntry]) -> set[str]:
    return {dirname(e.path) for e in blobs if basename(e.path) == SKILL_FILE}


def _inside(path: str, folders: set[str]) -> bool:
    return any(f and (path == f or path.startswith(f"{f}/")) for f in folders)


def _dependency_files(blobs: Sequence[TreeEntry]) -> list[str]:
    """Shallowest first. A skill's own helper dependencies don't make the repo an MCP server."""
    skills = _skill_folders(blobs)
    found = [
        e.path
        for e in blobs
        if DEPENDENCY_FILE.match(basename(e.path)) and not _inside(e.path, skills)
    ]
    return sorted(found, key=lambda p: (p.count("/"), p))[:MAX_DEPENDENCY_FILES]


def files_to_read(entries: Iterable[TreeEntry]) -> list[str]:
    """Files whose text the rules need: one copy of each SKILL.md, the README and manifests."""
    blobs = _blobs(entries)
    skill_files = [group[0] for group in _skill_groups(blobs) if not _in_sample_folder(group[0])]
    readme = _root_readme(blobs)
    manifests = [e.path for e in blobs if e.path in PLUGIN_MANIFESTS]
    return [
        *skill_files[:MAX_SKILL_FILES],
        *([readme] if readme else []),
        *_dependency_files(blobs),
        *manifests,
    ]


# --- The panel ---


def assemble(
    entries: Iterable[TreeEntry],
    files: Mapping[str, str | None],
    owner_type: str,
    partial: bool = False,
) -> Panel:
    blobs = _blobs(entries)
    listed: set[str] = set()
    for path in PLUGIN_MANIFESTS:
        listed |= manifest_skill_folders(files.get(path) or "")
    skills, possible = _skills(blobs, files, listed)
    agent_files = [{"path": e.path, "rule": AGENT_RULE} for e in blobs if _is_agent_file(e.path)]
    uses_mcp = [
        {"path": e.path, "rule": USES_MCP_RULE} for e in blobs if basename(e.path) == ".mcp.json"
    ]
    mcp_server = []
    for path in _dependency_files(blobs):
        rule = mcp_server_rule(path, files.get(path) or "")
        if rule:
            mcp_server.append({"path": path, "rule": rule})
    readme = _root_readme(blobs)
    phrases = readme_mentions(files.get(readme) or "") if readme else []
    return {
        "has_ai": bool(skills or agent_files or mcp_server),
        "partial": partial or len(_skill_groups(blobs)) > MAX_SKILL_FILES,
        "skills": skills,
        "possible_skills": possible,
        "agent_files": sorted(agent_files, key=lambda a: a["path"]),
        "uses_mcp": uses_mcp,
        "mcp_server": mcp_server,
        "readme_mentions": (
            {"path": readme, "phrases": phrases, "rule": README_RULE} if phrases else None
        ),
        "publisher": "organization" if owner_type == "Organization" else "personal",
    }
