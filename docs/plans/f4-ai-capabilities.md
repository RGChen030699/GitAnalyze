# F4 AI capabilities: plan

Goal: each report shows which AI capabilities a repository has, with trust signals and the rule
and file behind every finding. Rankings rows carry an `ai` flag, so "Has AI capabilities" works.

## Where the code lives

- `ai_capabilities/rules.py`: pure rules, tested without network or database.
  - Drop vendored paths; group SKILL.md files by blob sha (duplicates).
  - Parse SKILL.md headers tolerantly (BOM, CRLF, folded `>` and `|-`).
  - Level 1 skills, 1b possible skills with a reason, 2 agent files (with `.mcp.json` as a
    "uses MCP" note), 3 MCP server, 4 README hint.
  - Trust signals: publisher, scripts in the skill folder, Agent Skills standard.
  - `assemble()` builds the panel; it never produces a score or a "safe" label.
- Files are read with the F0 client's `get_raw` (C9): raw.githubusercontent.com, no token, no API quota.
- `ai_capabilities/scan.py`: one tree request. A truncated tree is walked subtree by subtree, at
  most 50 requests, then "Partial scan". Needed files are read 8 at a time, at most 100 SKILL.md
  files and 20 dependency manifests.

## When scans run

- On report open, when the stored scan is missing or older than 24 hours, like F2 health data.
- In the daily job, `refresh_ai` scans ranked repositories whose scan is older than 7 days, about
  170 a day, about 170 GitHub requests. Skills change slowly, and this keeps the daily job inside
  the request budget.

## Storage and API

- `Repository.ai` (JSON panel, including its source) and `Repository.ai_fetched_at`, in
  migration 0005.
- Detail API: `ai` (true or false; null when not scanned) and `ai_capabilities` (the panel),
  each with provenance.
- Rankings rows: `ai`.

## Dependency

PyYAML, for SKILL.md headers. YAML has folded and literal blocks, quoting and escapes, and real
skills use all of them (`description: >`, `description: |-`). `yaml.safe_load` only.

## Test fixture

`tests/fixtures/github/ai_anthropics_skills.txt`, recorded from anthropics/skills on
2026-11-24. It has 20 SKILL.md files: 19 skills plus `template/`.
