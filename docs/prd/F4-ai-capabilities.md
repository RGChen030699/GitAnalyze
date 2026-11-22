# F4: AI Capabilities and Trust Signals

**Priority:** Must · **Size:** M · **Sprint:** 2 · **Job:** J2 · **Proposal story:** 6 ("identify any AI skills it contains")

## 1. User stories

- As someone who was sent an AI skill or tool, I want to see what AI capabilities a repository has, so that I know what I'd be installing.
- As someone deciding whether to install a skill, I want signals of whether it's trustworthy, so that I don't run unsafe code.

## 2. Scope

AI capabilities are checked per repository. There is no GitHub-wide search for skills. F7 can filter lists by "has AI capabilities".

## 3. Detection

**Step 1: list every file.**
- Call `GET /repos/{owner}/{repo}/git/trees/{default_branch}?recursive=1` (1 request).
- If `truncated` is true (more than 100,000 entries or 7 MB), walk the subtrees non-recursively.

**Step 2: ignore vendored and generated folders.**
Skip any path containing `node_modules/`, `vendor/`, `dist/`, `build/`, `.git/`, `site-packages/`, `__pycache__/`.

**Step 3: apply the four levels.**

| Level | Rule | What we show |
|---|---|---|
| **1. AI skill** (high confidence) | A file named exactly `SKILL.md` whose YAML header parses and has a non-empty `description` | "Contains N AI skills", listing each skill's name, description and folder |
| 1b. Skill (medium confidence) | `SKILL.md` without a valid header or description, or inside `template/`, `example/`, `test/` | Listed under "Possible skills", with the reason |
| **2. Set up for AI coding agents** (medium) | Any of: `CLAUDE.md`, `AGENTS.md`, `GEMINI.md`, `.cursor/rules/**`, `.cursorrules`, `.github/copilot-instructions.md`, `.github/instructions/*.instructions.md` | "Set up for AI coding agents", listing which files |
| **3. MCP server** (medium) | `server.json` whose `$schema` points to `static.modelcontextprotocol.io/schemas/`; **or** `@modelcontextprotocol/sdk` in `package.json` dependencies; **or** `mcp` / `fastmcp` in `pyproject.toml` or `requirements*.txt` | "Provides an MCP server: a tool AI apps can connect to" |
| **4. README mentions AI features** (low) | `README.md` (root) contains any of: "Claude Code", "agent skill", "SKILL.md", "MCP server", "Cursor rules", "Codex", "Copilot", "plugin marketplace" (case-insensitive) | "README mentions AI features (a hint, not proof)" |

**Plugins and marketplaces.**
- A `.claude-plugin/marketplace.json` or `plugin.json` that lists skill paths: show those skills under level 1, noting "listed in plugin manifest".
- A `.mcp.json` file means the repository **uses** MCP servers. Show it as a note under level 2, not as level 3.

**Reading files.**
- Fetch `SKILL.md`, `README.md`, `package.json`, `pyproject.toml`, `server.json` from `raw.githubusercontent.com/{owner}/{repo}/{branch}/{path}`. This costs no API quota.
- Parse YAML headers tolerantly: byte-order mark, Windows line endings, folded `>` descriptions.

**Duplicates.**
- The same skill is often copied into several folders (`.claude/skills/`, `.agents/skills/`, `.github/skills/`).
- Count unique skills by the file's `blob_sha` from the tree, and list the extra paths under the skill.

## 4. Trust signals (per skill and per repository)

| Signal | How | Display |
|---|---|---|
| Publisher | `owner.type` | "Published by an organization" / "Published by a personal account" |
| Contains scripts | Any file in the skill folder with `.py`, `.sh`, `.js`, `.ts`, `.rb`, `.ps1`, or a `scripts/` folder | Amber note: "This skill includes scripts that can run on your computer. Read them before installing." |
| Last updated | Repository `pushed_at` [ASSUMPTION: per-skill dates would need one commits call per skill; add later if needed] | "Repository last updated 5 days ago" |
| Standard format | `name` is 1–64 lowercase letters, digits or hyphens, matches the folder name, and `description` is 1–1,024 characters (Agent Skills specification) | "Follows the Agent Skills standard" or "Doesn't fully follow the standard: <reason>" |
| Repository health | Status label from F2 | Reused |

**Never** show a quality score, star rating, or "safe" label.

## 5. Acceptance criteria

- [ ] Given `anthropics/skills`, when I open its page, then the AI panel lists its skills (about 17–20, excluding `template/`), each with name and description.
- [ ] Given a skill folder containing `scripts/fill_form.py`, when the panel loads, then that skill shows the amber "includes scripts" note.
- [ ] Given the same `SKILL.md` content in `.claude/skills/x/` and `.agents/skills/x/`, when the panel loads, then it counts one skill and lists both paths.
- [ ] Given a repository with only `CLAUDE.md` and `AGENTS.md`, when the panel loads, then it shows "Set up for AI coding agents" and no skills.
- [ ] Given a `package.json` depending on `@modelcontextprotocol/sdk`, when the panel loads, then it shows "Provides an MCP server".
- [ ] Given `SKILL.md` files only under `node_modules/`, when the panel loads, then no skills are shown.
- [ ] Given a `SKILL.md` with no YAML header, when the panel loads, then it appears under "Possible skills" with the reason "No header found".
- [ ] Given a repository with no AI signals, when the panel loads, then it says "No AI capabilities found by our rules" and links to the rules (F6).
- [ ] Given any finding, when I open its info icon, then I see the rule that matched and the file path.

## 6. Edge cases

- **Huge monorepos (truncated tree):** walk subtrees, but stop after 50 subtree requests and show "Partial scan".
- **Lower-case `skill.md`:** not counted (the standard uses `SKILL.md`). Listed under "Possible skills".
- **Archived repositories:** scan normally; F2 shows the archived badge.

## 7. Open questions

- Team confirmation of the four-level rule.
- Strength of the "includes scripts" warning (PRD section 9).
