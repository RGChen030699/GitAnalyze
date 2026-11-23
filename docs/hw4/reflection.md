# HW4 Reflection: Claude Code Workflow & TDD

GitAnalyze team · November 2026

We built two GitAnalyze features with Claude Code: the F0 GitHub client through Explore → Plan → Implement → Commit (Part 2), and the F1 repository-input parser through strict TDD (Part 3). The main lesson: planning and test-first work paid off most when each phase left evidence another person could check.

## Q1: How the workflow compared to our previous approach

Our earlier process was already document-first: a proposal, a team discussion, then a PRD and one spec per feature before any code. What was new was applying the same discipline inside each Claude Code session, with every phase ending in a commit.

**What was better.** Problems surfaced before code existed. The F0 plan went through a pushback round that changed six design points. Two examples:

- A plain 403 is usually a permissions error, so it now fails fast instead of being retried for minutes, as a literal reading of F0 C4 would suggest.
- The token is never sent to `raw.githubusercontent.com`, because raw files are public and use no API quota.

Both would have been costly to change after the client and its 26 tests existed. Exploring before editing also caught conflicts between our own documents:

1. Our first task split grouped TDD cycles by feature area, while CLAUDE.md says "one criterion at a time".
2. F1 and F2 both number their rules L1–L3, so tests named `test_L1_...` would collide.
3. F0 marks slow statistics as "pending" and F2 consumes that state, but neither spec said how. F0 settled it as `status == "pending"` with `data=None`.

**What was harder.** The workflow is slower to start, and it only helps if the phases are visible. Our F0 history shows this unevenly:

- There is a `[plan]` commit, but exploration happened only inside the session, so it has no commit of its own.
- The commit scope is `github`, not `F0` as CLAUDE.md asks.
- The plan's pushback was Claude critiquing its own draft rather than one of us reviewing it.

TDD worked more cleanly. The F1 history has four red → green cycles (https URL, no scheme, `www.`, extra `/tree/...` path), a guard test honestly labelled "already passes, not a red cycle", and two refactors, merged with a merge commit so none of it was squashed away. Writing the test first kept each step small: the first green was a one-line `removeprefix`, and later cycles forced the general prefix handling that the refactors then cleaned up.

## Q2: Context management strategies that worked best

What worked best was keeping stable facts in files that Claude loads when needed, instead of repeating them in chat.

1. **Specs on demand.** CLAUDE.md imports only `@docs/prd/PRD.md` and lists the ten feature specs in a table marked "load only the one you need". Sessions read one spec, not eleven documents.
2. **Rules in CLAUDE.md, not in prompts.** Claude already knew that tests must not be changed to pass, the full suite must pass before a commit, and how to tag commits. Prompts only had to name the next step.
3. **Restart after changing CLAUDE.md or subagents.** Our F0 session started before the `codebase-explorer` subagent was committed, so Claude fell back to the built-in Explore agent. Exiting and restarting loaded the new CLAUDE.md, subagents and permissions.
4. **`/clear` between tasks, `/compact` within one.** We cleared between Part 2 and Part 3, compacted with a focus during the TDD cycles, and resumed with `claude --continue` after a break.
5. **A shared document between sessions.** Each of us worked in separate Claude Code sessions, whose context is not shared. A shared HW4 plan (scope, commit format, checklist) let either of us start a fresh session without re-explaining the history.

## Annotated session log

Full logs are in `docs/hw4/logs/`. Excerpts below; our annotations in brackets.

**Part 2, F0: explore and plan**

```text
There's no codebase-explorer agent in this session, so I'll use the
built-in Explore agent instead ...
Entered plan mode
```

- `[EXPLORE]` Read-only survey of the skeleton and the F0 spec before any code. The custom subagent was missing because the session predated it (see Q2, point 3).
- `[PLAN MODE]` The plan defined scope (C1–C10 in, database and daily job out), injectable `sleep` and `clock` so retry tests never wait, and three implementation commits.

**Part 2, F0: result**

```text
All 35 tests pass ... It has only run against mocked responses,
never the live GitHub API, and nothing is pushed.
403 handling differs from the PRD ...
```

- `[IMPLEMENT]` Three commits, each with its tests. An autouse fixture blocks real HTTP, so CI can never call GitHub.
- `[HONEST GAP]` Claude flagged where the code departs from the spec instead of hiding it.

**Part 3, F1: push rejected during the refactor**

```text
The push was rejected and I haven't changed anything yet. While I was
refactoring, 9 new commits landed on origin/feat/f1-parser, and one of
them changes the same code as mine ...
```

- `[CONFLICT]` Two of us were on the same branch, and two refactors overlapped. Claude stopped, explained the overlap and asked before discarding anything.
- `[PERMISSIONS]` `git reset --hard` is denied in `.claude/settings.json`, so we used `git reset --keep`, which refuses to discard uncommitted work.

**Part 3, F1: refactor checked before commit**

```text
Diff (backend/lookup/parsing.py only; no test files touched)
+def _parse_entry(entry: str) -> RepoRef: ...
Before the refactor: 40 passed.  After: 40 passed.
```

- `[REFACTOR]` Behaviour unchanged, tests untouched, suite green before and after. We reviewed the diff before approving the commit.

## What we'd do differently

- Commit the explore notes, so the history shows all four phases.
- Have a teammate review the plan, not only Claude's self-critique.
- Use the feature as the commit scope (`F0`), as our own CLAUDE.md says.
- One writer per branch at a time: say so before starting, and pull right before working.
