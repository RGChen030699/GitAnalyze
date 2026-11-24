# CLAUDE.md — GitAnalyze

GitAnalyze shows real GitHub data about open-source repositories and AI skills: whether each one is alive, maintained, and trustworthy. Users can look up repos, compare them side by side, and browse rankings. Every number is shown with its source and the time it was fetched.

## Product context

@docs/prd/PRD.md

Feature specs are in `docs/prd/F*.md`. **Read the spec for a feature before planning or coding it.** These files are deliberately not imported here; load only the one you need.

| Feature | Spec |
|---|---|
| F0 GitHub client, DB schema, daily job | `docs/prd/F0-github-data-foundation.md` |
| F1 Repository lookup (paste/search) | `docs/prd/F1-repository-lookup.md` |
| F2 Health summary | `docs/prd/F2-health-summary.md` |
| F3 Star history | `docs/prd/F3-star-history.md` |
| F4 AI capabilities & trust signals | `docs/prd/F4-ai-capabilities.md` |
| F5 Compare & export | `docs/prd/F5-compare-and-export.md` |
| F6 Metric provenance | `docs/prd/F6-metric-provenance.md` |
| F7 Top repositories | `docs/prd/F7-top-repositories.md` |
| F8 Stars-gained ranking | `docs/prd/F8-stars-gained-ranking.md` |
| F9 Issue & PR trends | `docs/prd/F9-issue-pr-trends.md` |

Requirement IDs (e.g. `L1`, `C5`) and acceptance criteria in those files are the source of truth. Reference them in tests, plans, and commit messages.

Other reference docs, also not imported. Read them only when the task needs them:

| Doc | Read when |
|---|---|
| `docs/design.md` | Any frontend/UI work: tokens, components, screens, states, copy, accessibility |
| `docs/research/mom-test-transcripts.md` | Product questions: why a feature exists or who it's for. Don't load it for coding tasks |
## Tech stack

- **Backend:** Python 3.12, Django 5, Django REST Framework
- **Database:** PostgreSQL 16 (raw GitHub payloads stored in `JSONB`)
- **Frontend:** TypeScript (framework TBD; see PRD §8), in `frontend/`
- **Testing:** pytest + pytest-django; `responses` (or recorded fixtures) for HTTP mocking
- **Lint/format:** ruff (lint + format), mypy for type checks
- **Data sources:** GitHub REST/GraphQL API, `raw.githubusercontent.com`, GitHubTrendingRSS feed (only these)

## Commands

Run everything from the repo root.

```bash
# setup (requirements-dev.txt includes requirements.txt)
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt

# run (manage.py lives in backend/)
python backend/manage.py migrate
python backend/manage.py runserver
python backend/manage.py makemigrations

# test (run before every commit); use `python -m pytest` so the venv's pytest is used
python -m pytest                                                  # all tests
python -m pytest backend/tests/test_smoke.py::test_project_settings_load  # one test
python -m pytest -k parse_repo_input                              # by name

# quality
ruff check . && ruff format --check .
mypy backend
```

### Environment gotchas (found by `/init`)

- `backend/` is the Python import root (`pythonpath` in `pytest.ini`; `manage.py` lives there). Import `config.settings`, **not** `backend.config.settings`.
- All settings live in `backend/config/settings.py` and come from environment variables listed in `.env.example`.
- **`.env` is not loaded automatically.** There is no dotenv dependency, so export variables in the shell.
- `POSTGRES_DB` selects the database: PostgreSQL when set, otherwise SQLite at `backend/db.sqlite3`. **This applies to pytest too.** An exported `POSTGRES_DB` makes tests hit Postgres.
- DRF renders JSON only (`DEFAULT_RENDERER_CLASSES`), so the browsable API is off.
- Tooling targets Python 3.12 with 100-character lines (`ruff.toml`, `mypy.ini`). There is no `pyproject.toml`: Vercel's Python builder would install from it instead of `requirements.txt`.

## Architecture

```
backend/
  config/            # Django settings, urls
  github_client/     # F0: the ONLY module that talks to GitHub
  repositories/      # models (repository, snapshots), on-demand fetch
  lookup/            # F1: input parsing + search endpoint
  health/            # F2
  ...                # one Django app per feature
  tests/fixtures/    # recorded GitHub JSON responses
frontend/
docs/prd/
```

Key decisions:
1. **One GitHub client.** All GitHub traffic goes through `github_client/`. It handles auth, rate limits, retries on 202/403/429, ETags, and redirects (F0 C1–C9). Views and other apps never call `requests`/`httpx` directly.
2. **Provenance travels with data.** Every client call returns `data`, `source` (the endpoint), `fetched_at`, and the request cost (F0 C8). Stored metrics keep these fields so F6 can display them.
3. **Pure logic stays separate from I/O.** Parsing, metric calculations, and ranking are pure functions in `services.py`/`parsing.py` modules that are unit-tested without the DB or network. Views stay thin.
4. **Cache-first.** Repos fetched less than 24h ago are served from Postgres (F1 L4). Rankings refresh daily, never in real time.
5. **Stable URLs.** `/repo/{owner}/{name}` and `/compare?repos=a/b,c/d` (F1 L7).
6. **Rules live on the backend.** `compute_status`, `single_maintainer`, `license_note`, and the star-spike rule are implemented in Django exactly per F2 and F8 G7. The frontend only renders their results and tones (design.md §16).
7. **One definitions file.** `metrics.yaml` drives info popovers, the `/about` dictionary, and verdict check explanations (F6). Don't hard-code metric descriptions anywhere else.
8. **PostgreSQL, not NoSQL.** The data is relational (repo → snapshots, releases, contributors) and queried as time series (window functions for stars gained). Raw GitHub payloads go in `JSONB` for flexibility.

## Coding conventions

- Type hints on all functions; `mypy` clean.
- Use `@dataclass(frozen=True)` for value objects (e.g. `RepoRef(owner, name)`).
- Names: modules `snake_case`, classes `PascalCase`, constants `UPPER_SNAKE`.
- Raise specific exceptions (`InvalidRepoInput`, `RepoNotFound`, `RateLimited`). Never use bare `except:`.
- User-facing messages must match the wording in the spec exactly (e.g. "Compare up to 3 repositories at a time").
- Timestamps are timezone-aware UTC (`django.utils.timezone.now()`).
- Keep functions small. If a function needs a comment explaining what it does, split it.

**Frontend (from `docs/design.md`):**
- Components use CSS tokens from `tokens.css` only. Never use raw hex values.
- Status always shows icon + word + colour. Never rely on colour alone.
- Use sentence case, no exclamation marks, and never apologise in errors. Button labels are verbs that name the result ("Check", "Compare 3").
- Every interactive element is at least 44×44px, has a visible 3px focus ring, and respects `prefers-reduced-motion`.
- Fixed strings from design.md §12 must appear verbatim.

## Testing strategy (TDD)

- **Every acceptance criterion becomes at least one test.** Name tests after the requirement: `test_L1_accepts_git_ssh_url`.
- **Red → green → refactor, one criterion at a time:**
  1. Write the failing test. Run it and **confirm it fails for the right reason**. Commit: `test(F1): ... [red]`
  2. Write the **minimum** code to pass. Run the whole suite. Commit: `feat(F1): ... [green]`
  3. Clean up with all tests still green. Commit: `refactor(F1): ... [refactor]`
- **Never** modify a test to make it pass unless the test itself is wrong. If it is, say so explicitly first.
- **Never** write implementation code before its test exists.
- **CI never calls the live GitHub API.** Use recorded fixtures in `tests/fixtures/` and mock HTTP with `responses`.
- Unit tests for pure logic need no DB. Use `@pytest.mark.django_db` only where required.

## Git & commits

- Conventional commits: `type(scope): summary`, where type is `feat|fix|test|refactor|docs|chore` and scope is the feature (`F0`, `F1`, …).
- Tag TDD commits with `[red]`, `[green]`, or `[refactor]`.
- Tag workflow commits with the phase when useful: `docs(F0): implementation plan [plan]`.
- One logical change per commit. Run `python -m pytest` before committing; never commit a red suite except on a `[red]` commit.
- Never force-push or rewrite shared history.

## Do's

- **Explore before changing code:** use Glob/Grep/Read to find existing patterns and reuse them.
- **Plan before non-trivial work:** use Plan mode, and save the plan to `docs/plans/<feature>.md`.
- Cite requirement IDs in code comments only where the reason isn't obvious (`# F0 C10: stargazers endpoint is forbidden`).
- Show "N/A" for missing data, never `0`.
- Ask when a spec is ambiguous instead of guessing; specs mark guesses with `[ASSUMPTION]`.

## Don'ts

- **Don't** call `GET /repos/{owner}/{repo}/stargazers`, and don't add a client method for it (F0 C10).
- **Don't** scrape github.com HTML. Don't use GH Archive, BigQuery, ClickHouse, or OSS Insight data.
- **Don't** commit secrets. `GITHUB_TOKEN` comes from the environment; `.env` is git-ignored.
- **Don't** compute a "quality score" or verdict for AI skills. Show trust signals only (PRD §6).
- **Don't** add 5- or 10-year ranking windows, or claim to measure usage/downloads.
- **Don't** add dependencies without saying why.
- **Don't** edit migrations that are already committed; create new ones instead.

## Context management

- Run `/clear` between unrelated features or tasks.
- Run `/compact` during long sessions, with a focus such as `/compact keep F1 test list and current failing test`.
- Use `claude --continue` to resume the last session after a break; use `claude --resume` to pick an older one.
- Load only the F-spec you're working on; don't read every spec "just in case."
