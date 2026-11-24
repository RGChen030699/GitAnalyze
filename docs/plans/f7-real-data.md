# F7 Real GitHub Data Implementation Plan

> **Execution:** Native, in the main session, with no subagent-driven development. Do only the step the user names, then stop and wait. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the sample data in `frontend/index.html` with real GitHub data stored in our database, refreshed by hand with a management command.

**Architecture:** `refresh_rankings` builds a small watch list through `github_client` and stores repositories and weekly star points with provenance. `GET /api/rankings` reads only the database. `GET /api/lookup` fetches 1–3 repositories on demand with a 24-hour database cache. The frontend loads every rankings page, then keeps its existing client-side filters, sorting and summary.

**Tech Stack:** Python 3.12, Django 5, DRF, PostgreSQL 16 (SQLite locally), pytest, `responses`, plain JavaScript, Node's built-in test runner. No new dependencies.

**Spec:** `docs/prd/F7-top-repositories.md`, with `F0`, `F1` (L1–L4), `F2` (R1–R4, S1–S5), `F3` §2 and `F8` §2.

**Status:** Steps 1, 2, 3, 3a, 4, 6a, 6b and 8 are done. Step 8 still has limit 10, `/api/lookup` wiring and a browser check open. Step 5 is committed (`a3c892b`–`5fa4648`) but its checkboxes below were not ticked. Steps 6, 7, 9 and 10 have not been implemented. `refresh_rankings` has been tested only with recorded fixtures on in-memory SQLite. It has not run against live GitHub or a real Postgres database.

## Global Constraints

- Work on branch `feat/f7-real-data`, never directly on `main`.
- Page loads never call GitHub (T7). Only `refresh_rankings` and `/api/lookup` may.
- All GitHub traffic goes through `github_client`. Never call `/repos/{owner}/{repo}/stargazers` (C10).
- Tests use recorded fixtures and `responses`. The existing `block_real_http` fixture must stay active.
- Missing data is `null` in the API and "N/A" in the UI, never `0`, "today" or a crash.
- Timestamps are timezone-aware UTC. Pure rules take `now` as an argument (F2 R1).
- Exact copy: "We couldn't find a public repository at owner/name", "Compare up to 3 repositories at a time", "Rankings are being prepared", "No repositories match these filters".
- For each step, write tests one at a time and watch each fail for the right reason. Commit the step's tests as `[red]` and its implementation as `[green]`. Add `[refactor]` only if needed.
- Before each `[green]` commit, run `python -m pytest`, `ruff check . && ruff format --check .`, and `mypy backend`.

**Out of scope:** deployment, daily scheduler, AI topics, bigger watch lists, year-window drift, URL state, tabs.

## Review Focus

1. **Partial star history:** page 1 succeeds and page 2 fails. Week, month and sparkline are kept and year is `null` (Step 4).
2. **Rate limit during a web request:** `/api/lookup` must never sleep until reset. It serves cached data or returns 503 (Steps 2 and 7).
3. **Renamed repository:** the old name updates the same row, matched on `github_id` (Steps 4 and 7).
4. **Null values in every UI path:** sort, summary, sparkline, CSV and status pill all survive `null` (Step 8).
5. **Incomplete input:** `https://github.com/vercel` and `https://gitlab.com` raise `InvalidRepoInput` instead of crashing with `ValueError` (Step 6), and the API returns 400 (Step 7).

## Data shapes shared across steps

**API row** (`serialize_row`): `full_name, owner, name, description, language, owner_type, stars, forks, open_issues, status, pushed_at, stars_gained_7d, stars_gained_30d, stars_gained_year, weeks_12, contributors, ai, spike, trending, source, fetched_at`.

`contributors`, `ai`, `spike` and `trending` are always `null` in this plan. Their data sources are follow-ups.

**Rankings response:** `{prepared, updated_at, tracked, count, page, limit, languages, results}`. `languages` is `[{name, count}]` across all ranked repositories, ignoring the request's filters and page. It is sorted by `count` descending, then `name`, excludes `null`, and has at most 15 entries (T2).

**Lookup response:** `{repos: [row], suggestions: [{full_name, description, stars}]}`. Errors are `{detail}`.

---

### Step 1: Verify star history and record fixtures

**Files:**
- Create: `backend/tests/fixtures/github/stargazers_history.json`, `search_repositories.json`, `repo.json`, `releases.json`
- Modify: this plan, section "Step 1 result"

- [x] Run one live `GitHubClient().get("/repos/pallets/flask/stargazers/history", params={"per_page": 30, "page": 1})` from `python backend/manage.py shell`, with `GITHUB_TOKEN` exported. Never print the token.
- [x] Record the HTTP status, entry keys, newest-first order, and whether `week` values fall on a Sunday.
- [x] Apply the outcome:
  - **200 with `week`, `total`, `days`:** set `STAR_HISTORY_ENABLED = True` in Step 4 and save this response as the fixture.
  - **404:** set `STAR_HISTORY_ENABLED = False`. Stars gained and sparkline stay `null`. Add a follow-up to this plan.
  - **401, 403, 429, 5xx or a network error:** the result is inconclusive. Stop and report it. Do not treat it as "doesn't exist".
  - **200 with a different shape:** stop and update Step 4 before continuing.
- [x] Record the three remaining fixtures with one read-only call each: search (`per_page=3`), `/repos/pallets/flask`, and its releases.
- [x] Commit: `docs(F7): verify star history endpoint and record fixtures [plan]`

#### Step 1 result

Run on 2026-11-23 against `pallets/flask`.

- **Outcome:** the endpoint returned a successful response with `week`, `total` and `days`, so `STAR_HISTORY_ENABLED = True`.
- **Shape:** page 1 has 30 entries, newest first. Each has 7 `days` values, and `total` equals their sum in all 30.
- **`week` format:** an integer Unix timestamp in seconds, not a date string. All 30 values are Sunday 00:00 UTC. Step 4 must convert it to `week_start`.
- **Current week:** the newest entry is partial, with zeros for days that have not happened yet (`[22, 17, 0, 0, 0, 0, 0]`). Step 4 must ignore those future days.
- **Fixtures:** recorded in `backend/tests/fixtures/github/`. Search uses `language:Python stars:>1000`, and releases use `per_page=3`. Token-specific `permissions` and `temp_clone_token` fields were removed.
- **Requests:** 5 in total. The search ran twice because the first recording attempt stopped when low search quota paused the next core request. That is the bug Step 2 fixes.

---

### Step 2: Per-resource rate limits (F0 C3, C4)

**Files:**
- Modify: `backend/github_client/client.py`, `backend/github_client/errors.py`
- Test: `backend/tests/test_github_client.py`

**Interfaces produced:**
- `GitHubClient(..., search_rate_limit_margin: int = 2, wait_for_rate_limit: bool = True)`
- `RateLimitError(..., reset_at: int | None = None)`

| Test | Assertion |
|---|---|
| `test_C3_low_search_quota_does_not_pause_core` | Search response with `x-ratelimit-resource: search`, remaining 5: the next core call does not sleep |
| `test_C3_low_core_quota_does_not_pause_search` | Core remaining 150: the next search call does not sleep |
| `test_C3_search_pauses_below_search_margin` | Search remaining 1: the next search call sleeps until its reset + 1 |
| `test_C3_core_still_pauses_below_200` | Core remaining 150: the next core call sleeps until reset + 1 |
| `test_C3_no_wait_mode_raises_instead_of_sleeping` | `wait_for_rate_limit=False`, low quota: raises `RateLimitError` with `reset_at`, sleep not called |
| `test_C4_no_wait_mode_does_not_retry_429` | A 429 raises at once after one request |
| `test_network_error_raises_github_error` | `requests.ConnectionError` becomes `GitHubError` |

- [x] Write tests, confirm red, commit `test(F0): per-resource rate limits [red]`.
- [x] Track quota per resource, keyed by the `x-ratelimit-resource` header. Before a request, treat `/search/` paths as `search` and all others as `core`. Keep `rate_limit_margin` for core.
- [x] Wrap `requests.RequestException` as `GitHubError`.
- [x] Run the checks, commit `feat(F0): track rate limits per resource [green]`.

---

### Step 3: Search helper (F0 W1, F1 L3, C8)

**Files:**
- Create: `backend/github_client/search.py`
- Modify: `backend/github_client/__init__.py`
- Test: `backend/tests/test_github_search.py`

**Interface produced:** `search_repositories(client: GitHubClient, query: str, per_page: int) -> GitHubResponse`, sorted by stars descending, one page, `per_page` between 1 and 100.

| Test | Assertion |
|---|---|
| `test_W1_search_sends_query_sorted_by_stars` | Request has `q`, `sort=stars`, `order=desc`, `per_page` |
| `test_C8_search_source_includes_query` | `source` contains the path and the encoded query |
| `test_W1_search_rejects_per_page_over_100` | `ValueError`, no request sent |
| `test_W1_search_parses_recorded_fixture` | `data["items"][0]` has `full_name` and `stargazers_count` |

- [x] Write tests, confirm red, commit `test(F0): search helper [red]`.
- [x] Implement, using `dataclasses.replace` to put the query in `source`.
- [x] Run the checks, commit `feat(F0): add repository search helper [green]`.

---

### Step 3a: `DATABASE_URL` support and SQLite-only tests

**Files:**
- Create: `backend/config/test_settings.py`
- Modify: `backend/config/settings.py`, `requirements.txt`, `pytest.ini`
- Test: `backend/tests/test_database_settings.py`

**New dependency:** `dj-database-url`. Hosted Postgres such as Neon provides one connection URL, and this library parses its credentials, escaping and query options into Django's format, so we don't maintain our own parser.

**Database order:** `DATABASE_URL`, then `POSTGRES_*`, then SQLite. Pytest always uses in-memory SQLite through `--ds=config.test_settings`, which also overrides an exported `DJANGO_SETTINGS_MODULE`.

| Test | Assertion |
|---|---|
| `test_DB1_database_url_configures_postgres` | Engine, host, port, name and user come from the URL |
| `test_DB1_database_url_wins_over_postgres_vars` | `DATABASE_URL` is used when both are set |
| `test_DB2_ssl_required_when_url_has_no_sslmode` | `sslmode=require` |
| `test_DB2_weak_sslmode_is_upgraded` | `sslmode=disable` becomes `require` |
| `test_DB2_stronger_sslmode_is_kept` | `sslmode=verify-full` is not downgraded |
| `test_DB3_postgres_vars_still_work` | `POSTGRES_*` fallback, with no SSL option added |
| `test_DB3_sqlite_is_the_default` | SQLite with no database variables |
| `test_DB4_pytest_uses_sqlite_with_database_env` | A nested pytest run stays on SQLite with `DATABASE_URL` or `POSTGRES_DB` exported |

- [x] Write tests, confirm red, commit `test(F7): database URL settings [red]`.
- [x] Add the dependency, the settings branch, `config.test_settings` and the pytest option.
- [x] Run the checks, commit `feat(F7): support DATABASE_URL with required SSL [green]`. Existing ruff lint and format issues in `backend/config/` and `backend/manage.py` were left alone.

---

### Step 4: Models, pure rules and `refresh_rankings`

**Files:**
- Create: `backend/repositories/` (`apps.py`, `models.py`, `services.py`, `ingest.py`, `migrations/`, `management/commands/refresh_rankings.py`), `backend/health/__init__.py`, `backend/health/services.py`
- Modify: `backend/config/settings.py` (`INSTALLED_APPS`, `RANKINGS_LANGUAGES`), `.env.example`
- Test: `backend/tests/test_ranking_services.py`, `test_compute_status.py`, `test_refresh_rankings.py`, `test_rankings_languages_setting.py`

**Models:**
- `Repository`: `github_id` (unique), `full_name` (unique, case-insensitive), `owner_login`, `owner_type`, `description?`, `language?`, `archived`, `pushed_at?`, `stargazers_count`, `forks_count`, `open_issues_count`, `newest_release_at?`, `status?`, `stars_gained_7d?`, `stars_gained_30d?`, `stars_gained_year?`, `weeks_12?` (JSON), `source`, `fetched_at`, `star_history_fetched_at?`, `ranked_at?`, `raw` (JSON).
- `StarWeek`: `repository`, `week_start` (date), `stars_gained`, `days` (JSON, 7 integers), `source`, `fetched_at`. Unique on (`repository`, `week_start`).

**Interfaces produced:**
- `health.services.compute_status(archived: bool, pushed_at: datetime | None, newest_release_at: datetime | None, releases_known: bool, now: datetime) -> str | None`
- `repositories.services.stars_gained(points: Sequence[StarPoint], as_of: date, days: int) -> int`
- `repositories.services.stars_gained_year(points, as_of) -> int`
- `repositories.services.weeks_12(points, as_of) -> list[int]` (exactly 12, oldest first)
- `repositories.services.build_watch_list(overall: list[dict], by_language: list[list[dict]], limit: int | None) -> list[dict]`
- `repositories.ingest.upsert_repository(payload: dict, source: str, fetched_at: datetime) -> Repository`
- `repositories.ingest.refresh_details(client: GitHubClient, repo: Repository, now: datetime) -> list[str]` (names of the parts that failed)

**Setting:** `RANKINGS_LANGUAGES` is read from the environment as a comma-separated list, default `Python,TypeScript,JavaScript`. Entries are trimmed, blanks are dropped, and case-insensitive duplicates keep the first spelling. An unset or blank value uses the default.

**Command option:** `refresh_rankings --language X` is repeatable and replaces `RANKINGS_LANGUAGES` for that run. The overall search still runs. Names with spaces are quoted in the query (`language:"Jupyter Notebook"`). Rows from earlier runs stay ranked, so removing a language does not remove its stored repositories.

**Constants:** `TOP_OVERALL = 100`, `TOP_PER_LANGUAGE = 50`, `STAR_HISTORY_ENABLED = True` (from Step 1).

| Test | Assertion |
|---|---|
| `test_S1_archived_wins` | Archived with a recent commit returns `Archived` |
| `test_S3_active_with_release_on_day_182` | Commit on day 30, release on day 182: `Active` |
| `test_S3_active_with_no_releases_ever` | Commit in 30 days, no releases, `releases_known=True`: `Active` |
| `test_S4_slowing` | Commit on day 31: `Slowing` |
| `test_S5_quiet_when_pushed_at_missing` | `pushed_at=None`: `Quiet` |
| `test_S3_unknown_releases_returns_none` | Recent commit, `releases_known=False`: `None` |
| `test_F8_week_sums_last_7_days_across_week_boundary` | Days spanning two weeks are summed correctly; future days are ignored |
| `test_F8_negative_weeks_kept` | Net-negative days stay negative |
| `test_G3_weeks_12_oldest_first_zero_fills_gaps` | 12 values, last is the current week, missing weeks are 0 |
| `test_W1_watch_list_dedupes_and_applies_limit` | Overlap counted once; `limit` keeps the highest-starred |
| `test_rankings_languages_default` | Unset or blank gives `("Python", "TypeScript", "JavaScript")` |
| `test_rankings_languages_parses_env` | ` Go, rust,,GO ` gives `("Go", "rust")` |
| `test_refresh_uses_configured_languages` | Default setting: one overall search (`per_page=100`), three language searches (`per_page=50`) |
| `test_refresh_language_option_replaces_setting` | `--language Go --language Rust`: one overall search and only those two language searches |
| `test_refresh_quotes_language_with_space` | `--language "Jupyter Notebook"` sends `language:"Jupyter Notebook"` |
| `test_refresh_blank_language_is_error` | `--language " "` raises `CommandError` before any request |
| `test_refresh_stores_source_and_fetched_at` | On both `Repository` and `StarWeek` |
| `test_refresh_is_idempotent` | A second run creates no duplicate rows |
| `test_C7_rename_updates_same_row` | Same `github_id`, new `full_name`: one row |
| `test_history_page_2_failure_keeps_week_and_month` | Year `null`; 7d, 30d and `weeks_12` set |
| `test_history_failure_keeps_previous_values` | Earlier values are not wiped |
| `test_history_disabled_leaves_gains_null` | `STAR_HISTORY_ENABLED=False`: gains `null`, no history request |
| `test_release_failure_gives_null_status` | Status `None` for a recent commit, row still saved |
| `test_one_repo_failure_does_not_stop_run` | Others saved; summary counts one failure |
| `test_search_failure_aborts_without_changes` | `CommandError`, database unchanged |
| `test_limit_must_be_positive` | `--limit 0` raises `CommandError` |
| `test_summary_reports_repos_requests_failures` | Output contains all three (F0 §3.4) |

- [x] Write tests, confirm red, and commit in three parts: models (`718f564`), pure rules (`faf87df`), and the command (`46d5e7e`).
- [x] Implement the models and create the migration with `makemigrations` (`b021399`). Implement the pure rules (`d198781`).
- [x] Implement the command (`8894362`). Per repository, fetch up to 2 history pages (`per_page=30`, enough for 52 weeks) and `GET /repos/{owner}/{repo}/releases?per_page=100`. Basic fields come from the search result. Save each repository's details in one transaction.
- [x] Add `RANKINGS_LANGUAGES=Python,TypeScript,JavaScript` to `.env.example` (`8264f09`, committed by the user).
- [x] Budget check, for `L` languages: at most `1 + L` searches + `(100 + 50L) × 3` core requests, or `301 + 151L` per run. The default (`L = 3`) is 4 searches + 250 × 3 = **754 requests**. Each extra language adds up to 151. With `--limit N`, the total is at most `1 + L + 3N`. These are calculated limits, because no full live run has happened.

#### Step 4 implementation choices

- **Star floor:** every search uses `stars:>1000`, alone for the overall search and with `language:<name>` for language searches. The earlier plan did not specify a query, and this matches the recorded search fixture.
- **`refresh_details` return value:** it returns a list of failed parts (`releases`, `star history`, `star history page 2`) instead of `None`, so the command can log them and count that repository as one failure.
- **Request counting:** `GitHubClient.requests_sent` counts HTTP responses received, including retries and redirects. The run summary reports it. Requests that end in a network error are not counted.
- **Reused names:** rows are matched on `github_id`. If a new repository takes a name still stored on another row, the unique-name constraint rejects it. The run counts one failure, leaves the existing row unchanged, and continues.
- [x] Run the checks, commit `feat(F7): store rankings via refresh_rankings [green]`.

---

### Step 5: `GET /api/rankings` and CORS

**Files:**
- Create: `backend/rankings/__init__.py`, `views.py`, `serializers.py`, `backend/config/cors.py`
- Modify: `backend/config/urls.py`, `backend/config/settings.py`
- Test: `backend/tests/test_rankings_api.py`, `test_cors.py`

**Interfaces produced:** `rankings.serializers.serialize_row(repo: Repository) -> dict`. Setting `FRONTEND_ORIGIN`, default `http://localhost:8080`.

**Query parameters:**
- `sort=stars` is the default: total lifetime stars descending, ties by `full_name`. Stars gained is never the default.
- `sort=gained&window=7d|30d|1y` powers "Gaining stars". `window` defaults to `7d`. Missing gains sort last.
- `sort=pushed` is "Recently active" (T3). Missing dates sort last.
- `sort=trending` orders by trending rank ascending, and `trending=1` keeps only trending repositories. Both return an empty list until trending data exists.
- Filters: `lang` (case-insensitive), `status` (`Active`, `Slowing`, `Quiet`, `Archived`), `archived=0|1`.
- Paging: `limit=10|25|50|100` (default 25) and `page` (default 1). Invalid values return 400 with `{detail}`.

| Test | Assertion |
|---|---|
| `test_T7_rankings_makes_no_github_call` | `responses.calls` is empty |
| `test_F7_python_sorted_by_stars` | Every row is Python, descending stars |
| `test_F7_limit_10_returns_10` | 10 rows, `count` is the full total |
| `test_T5_page_2_continues_ranks` | Page 2 holds items 11–20 with no overlap |
| `test_F7_ties_break_by_full_name` | Stable order across pages |
| `test_T3_null_gains_sort_last` | After negative values |
| `test_T4_invalid_limit_returns_400` | `limit=7`; same for bad `sort` and `page=0` |
| `test_nulls_stay_null_in_json` | Never coerced to `0` |
| `test_F7_empty_database_not_prepared` | `prepared=false`, `results=[]` |
| `test_F7_lookup_only_rows_still_not_prepared` | Rows with `ranked_at=None` do not count as prepared |
| `test_T2_languages_sorted_by_repository_count` | Count descending, ties by name, `null` excluded |
| `test_T2_languages_ignore_request_filters` | `language=Python` and `page=2` return the same list |
| `test_T2_languages_exclude_lookup_only_rows` | Rows with `ranked_at=None` are not counted |
| `test_T2_languages_capped_at_15` | 16 languages return the top 15 |
| `test_cors_allows_frontend_origin` | Exact `Access-Control-Allow-Origin` and `Vary: Origin` |
| `test_cors_rejects_other_origin` | Header absent |
| `test_cors_only_on_api_paths` | `/admin/` gets no header |

- [ ] Write tests, confirm red, commit `test(F7): rankings API and CORS [red]`.
- [ ] Implement a thin DRF view with `F(...).desc(nulls_last=True)`. Implement a small GET/OPTIONS CORS middleware rather than adding `django-cors-headers`.
- [ ] Run the checks, commit `feat(F7): add database-only rankings API [green]`.

---

### Step 6: Fix parser crashes on incomplete input (F1 L1–L3)

**Files:**
- Modify: `backend/lookup/parsing.py`
- Test: `backend/tests/test_lookup_parsing.py`

| Test | Assertion |
|---|---|
| `test_L1_incomplete_link_raises_invalid` | `https://github.com/vercel` raises `InvalidRepoInput` with the incomplete-link message |
| `test_L1_trailing_slash_link_raises_invalid` | `https://github.com/vercel/` raises the same error instead of returning an empty repository name |
| `test_L1_other_host_without_path_raises_invalid` | `https://gitlab.com` raises `InvalidRepoInput("GitAnalyze only checks GitHub repositories")` |
| `test_L2_mixed_input_raises_invalid` | `vercel/next.js zustand` raises `InvalidRepoInput("Enter up to 3 repositories, or one search, not both")` |
| `test_L3_plain_words_stay_one_search` | `state management` gives one search. This guard already passes, so it is not expected to go red |

- [ ] Write tests one at a time, confirm each new behavior fails for the right reason, commit `test(F1): parser handles incomplete input [red]`.
- [ ] Fix only `parsing.py`, covering the cases in `docs/plans/f1-followups.md`. The incomplete-link message is "That doesn't look like a GitHub repository. Use owner/repo or a github.com link."
- [ ] Run the checks, commit `feat(F1): reject incomplete repository input [green]`.

---

### Step 6a: `GET /api/repos/{owner}/{name}` (F1 L4, F0 C8, F6 P1)

**Files:**
- Create: `backend/repositories/fetch.py`, `serializers.py`, `views.py`
- Modify: `backend/config/urls.py`, `backend/repositories/ingest.py`
- Test: `backend/tests/test_repo_detail_api.py`

**Interfaces produced:**
- `repositories.fetch.get_or_fetch(client, owner, name, now) -> Repository`. Raises `RepoNotFound` on a GitHub 404.
- `repositories.serializers.serialize_detail(repo) -> dict`
- `refresh_details(..., ranked: bool = True)`. Lookups pass `ranked=False`, so they never set `ranked_at` and never join the rankings (Step 5 "lookup-only rows").

**Response:** `full_name, owner, name, description, language, owner_type, archived, stars, forks, open_issues, pushed_at, newest_release_at, status, stars_gained_7d, stars_gained_30d, stars_gained_year, commit_activity, contributors, releases, issues, pull_requests, star_history, provenance`.
- `star_history` is `[{week_start, stars_gained, days, source, fetched_at}]`, oldest first, read from `star_week`.
- `provenance` maps each value field to `{source, fetched_at}`, or `null` when the value is `null`. Repository fields use the repository's own `source`/`fetched_at`. Gains use the newest star week's `source` and `star_history_fetched_at`. `newest_release_at` uses `/repos/{full_name}/releases` and `status` uses "Computed from pushed_at and releases (F2 status rule)". Both take the repository's `fetched_at`, because releases are read in the same refresh and no separate release timestamp is stored.
- `commit_activity`, `contributors`, `releases`, `issues` and `pull_requests` are always `null` for now. `open_issues` is GitHub's combined issue and pull request count.

| Test | Assertion |
|---|---|
| `test_L4_fresh_repo_served_from_database_without_github_call` | Fetched 2 hours ago: 200, no request |
| `test_L4_cache_lookup_is_case_insensitive` | `Pallets/FLASK` hits the cached row |
| `test_L4_missing_repo_is_fetched_and_saved` | `/repos/pallets/flask` called first; row saved with its `source` and `fetched_at` |
| `test_L4_repo_fetched_24_hours_ago_is_refetched` | Exactly 24 hours old: fetched and updated |
| `test_lookup_fetch_does_not_mark_repo_ranked` | `ranked_at` stays `None` |
| `test_lookup_refetch_keeps_existing_ranked_at` | A ranked row keeps its `ranked_at` |
| `test_F2_detail_returns_repository_fields_status_and_gains` | All value fields, negative gains kept |
| `test_F3_detail_returns_star_weeks_oldest_first_with_provenance` | Rows oldest first, each with `source` and `fetched_at` |
| `test_C8_detail_gives_source_and_fetched_at_for_each_value` | Provenance per field; `null` value gives `null` provenance |
| `test_detail_unstored_data_is_null_not_zero` | Unstored fields and their provenance are `null` |
| `test_F1_unknown_repo_returns_404_with_message` | 404 with "We couldn't find a public repository at nobody/missing", no row saved |

- [x] One red/green pair per rule, `a2cfd3a`–`f00b334`.
- [x] Checks run before each green commit: `python -m pytest`, ruff on the changed files, `mypy backend`.

**Not covered in 6a:** a rate limit or other GitHub error while fetching still gives a 500, and the client never sleeps because `wait_for_rate_limit=False`. Step 7's stale-cache and 503 rules should apply here too. A renamed repository's old name works, because GitHub redirects and the row is matched on `github_id`, but there is no test for it yet and every request for the old name refetches.

---

### Step 6b: Decision brief rules on the backend (CLAUDE.md decision 6)

The five decision brief answers move from `frontend/sample.js` (`analyse`) to Django, with the thresholds in `sample.js` and in `frontend/about.html` under "Decision brief rules". The frontend only renders the results.

**Files:**
- Create: `backend/repositories/brief.py`
- Modify: `backend/repositories/serializers.py`, `backend/repositories/views.py`
- Test: `backend/tests/test_brief.py` (pure, no DB), `backend/tests/test_repo_detail_api.py`

**Interfaces produced** (`repositories.brief`, pure functions with no database or network; each returns `None` when an input is `None`):
- `BriefAnswer(tone: "good" | "warn" | "bad" | "neutral", value: str)`, a frozen dataclass.
- `interest(gained_30d, gained_prev_30d, total_stars, spike) -> BriefAnswer | None`. In order: Spiky (warn) when `spike`, Fading (neutral) at 0 or fewer net stars, Flat (neutral) under 0.2% of total stars, Growing (good) above +10%, Cooling (warn) below −10%, else Steady (neutral). Steady also covers a previous 30 days with no stars.
- `maintenance(commits_13w, commits_prev_13w) -> BriefAnswer | None`. Stopped (bad) at 0 commits, Slowing down (warn) below −40%, Speeding up (good) above +10%, else Steady (good).
- `issue_response(opened_6m, closed_6m) -> BriefAnswer | None`. "N/A" (neutral) when no issues were opened, Keeping up (good) at 95% or more, Falling behind (warn) from 60% to under 95%, Not answering (bad) under 60%.
- `release_pace(releases, now) -> BriefAnswer | None`. `releases` holds the publish dates of non-draft, non-prerelease releases. No releases (neutral) when empty, `None` with only one release, and otherwise the days since the newest release against the median of the last 8 gaps: On its usual pace (good) up to 1.5×, or "Overdue, X.X× its usual gap" (warn).
- `maintainer_concentration(commits_per_person) -> BriefAnswer | None`. The input is commits per person over the last 365 days, with bots already removed (F2 M2). `None` with no commits (F2 M4). Depends on one person (warn) when the top person made 80% or more. Otherwise "Shared by N people" (good), where N is the fewest people who together made 80%. Integer comparisons keep the 80% boundary exact.
- `repositories.serializers.serialize_brief_answer(answer) -> {tone, value} | None`.
- `serialize_detail(repo, now)` now takes `now`, which the view passes from `timezone.now()`, so release pace can measure days since the last release.

**Response:** `GET /api/repos/{owner}/{name}` adds `brief: {interest, maintenance, issue_response, release_pace, maintainer_concentration}`, each `{tone, value}` or `null`. All five are `null` for now. Interest needs the previous 30 days' stars and the F8 G7 spike check. The other four need commit, issue, release-list and contributor data that is not stored yet.

**Differences from `sample.js`:**
- **One release:** `sample.js` shows "On its usual pace" through JavaScript's `null <= 1.5` coercion. With no gap to compare against, the backend returns `None`.
- **Unknown spike check:** interest is `None` when `spike` is unknown. It is not treated as "no spike".
- **Only prereleases:** the input excludes prereleases, so a repository with only prereleases gives "No releases". `sample.js` would use the newest prerelease.

| Test | Assertion |
|---|---|
| `test_brief_interest_none_when_inputs_null` | Any `None` input gives `None` |
| `test_brief_interest_spiky_when_star_pattern_check_fires` | warn, Spiky |
| `test_brief_interest_fading_when_no_net_stars_in_30_days` | 0 and negative give neutral, Fading |
| `test_brief_interest_flat_when_gain_under_0_2_percent_of_total` | 19 of 10,000 is Flat, 20 is not |
| `test_brief_interest_growing_when_up_more_than_10_percent` | +11% is Growing, +10% is not |
| `test_brief_interest_cooling_when_down_more_than_10_percent` | −11% is Cooling, −10% is not |
| `test_brief_interest_steady_within_10_percent_or_without_prior_stars` | ±10% and a previous 0 give neutral, Steady |
| `test_brief_maintenance_none_when_inputs_null` | Any `None` input gives `None` |
| `test_brief_maintenance_stopped_when_no_commits_in_13_weeks` | bad, Stopped |
| `test_brief_maintenance_slowing_down_when_down_more_than_40_percent` | −41% is Slowing down, −40% is not |
| `test_brief_maintenance_speeding_up_when_up_more_than_10_percent` | +11% is Speeding up, +10% is not |
| `test_brief_maintenance_steady_otherwise` | good, Steady, including a previous 0 |
| `test_brief_issue_response_none_when_inputs_null` | Any `None` input gives `None` |
| `test_brief_issue_response_na_when_no_issues_opened_in_6_months` | neutral, N/A |
| `test_brief_issue_response_keeping_up_at_95_percent_or_more` | 95% and above give Keeping up, 94% does not |
| `test_brief_issue_response_falling_behind_from_60_to_95_percent` | 60% and 94% give Falling behind, 59% does not |
| `test_brief_issue_response_not_answering_under_60_percent` | bad, Not answering |
| `test_brief_release_pace_none_when_releases_unknown` | `None` input gives `None` |
| `test_brief_release_pace_no_releases_when_none_published` | neutral, No releases |
| `test_brief_release_pace_on_usual_pace_up_to_1_5x_its_gap` | Exactly 1.5× is on pace |
| `test_brief_release_pace_overdue_beyond_1_5x_its_gap` | "Overdue, 2.0× its usual gap" |
| `test_brief_release_pace_usual_gap_is_median_of_last_8_gaps` | Older gaps are ignored |
| `test_brief_release_pace_none_with_a_single_release` | One release gives `None` |
| `test_brief_maintainer_concentration_none_without_commits` | `None`, empty and all-zero give `None` |
| `test_brief_maintainer_concentration_depends_on_one_person_at_80_percent_or_more` | Exactly 80% is one person, 79% is not |
| `test_brief_maintainer_concentration_shared_by_people_who_made_80_percent` | Counts the fewest people who reach 80% |
| `test_detail_brief_has_five_answers_null_until_inputs_are_stored` | API `brief` has five keys, all `null` |
| `test_brief_answer_serializes_tone_and_value` | `{tone, value}`, or `null` |

- [x] One red/green pair per rule, `3b1e040`–`6f00b8d`.
- [x] Checks run before each green commit: `python -m pytest`, ruff on the changed files, `mypy backend`. Commit `148a0fa` slipped through with an unused import in `test_brief.py`, which the next commit fixed.

**Follow-ups:** compute the previous 30 days of stars from `star_week` and add the F8 G7 spike check so interest can be answered. Store commit activity, issue counts, the release list and contributor counts, then pass them into the other four rules. Replace `analyse` in `sample.js` with the API's `brief` in Step 8.

---

### Step 7: `GET /api/lookup` (F1 L1–L4)

**Files:**
- Create: `backend/lookup/services.py`, `backend/lookup/views.py`
- Modify: `backend/config/urls.py`
- Test: `backend/tests/test_lookup_api.py`

**Interface produced:** `lookup.services.lookup_repos(client: GitHubClient, refs: list[RepoRef], now: datetime) -> list[Repository]`. The view builds its client with `wait_for_rate_limit=False`.

| Test | Assertion |
|---|---|
| `test_L2_lookup_returns_three_repos` | 3 rows, saved to the database |
| `test_L4_fresh_repo_makes_no_github_call` | Fetched 2 hours ago: no request |
| `test_L4_repo_at_24_hours_refetches` | Exactly 24 hours old: fetched |
| `test_L4_lookup_is_case_insensitive` | `Pallets/FLASK` hits the cached row |
| `test_F1_404_message` | HTTP 404 with the exact message and the real owner/name |
| `test_F1_too_many_repos_is_400` | Exact message, no GitHub request |
| `test_F1_invalid_input_is_400` | Includes empty `q`, no GitHub request |
| `test_F1_renamed_repo_returns_new_name` | Old name resolves to the canonical `full_name` |
| `test_L3_name_search_returns_5_suggestions` | Uses `q=<text> in:name`, writes no rows |
| `test_F1_rate_limit_serves_stale_cache` | Stale row returned, no sleep |
| `test_F1_rate_limit_without_cache_is_503` | "GitHub is busy, try again in N minutes" with `Retry-After` |

- [ ] Write tests, confirm red, commit `test(F1): lookup API [red]`.
- [ ] Implement the service and a thin view. Fetch `/repos/{owner}/{name}`, then reuse `upsert_repository` and `refresh_details`.
- [ ] Run the checks, commit `feat(F1): add on-demand lookup API [green]`.

---

### Step 8: Connect the frontend

Done as one piece of work (`bb0c8a2`–`87c3169`), briefed as "Step 7: connect the frontend to the API". It covers `index.html`, `repo.html` and `compare.html`, not only the rankings table. The design changed from the first draft below: one mapping module, `data.js`, replaces `rows.js`. Pages use relative `/api/` paths, not a `<meta>` base URL, and a DEBUG-only Django route replaces `python -m http.server`.

**Files:**
- Create: `frontend/data.js`, `frontend/report-kit.js`, `frontend/tests/data.test.js`, `backend/config/dev_frontend.py`
- Modify: `frontend/index.html`, `frontend/repo.html`, `frontend/compare.html`, `backend/config/urls.py`
- Delete: `frontend/sample.js`. Its chart and formatting helpers moved unchanged to `report-kit.js`. Its sample profiles, `build()` and `analyse()` are gone.
- Test: `backend/tests/test_dev_frontend.py`, `backend/tests/test_frontend_static.py`

**Same origin in development:** `config.dev_frontend` serves `frontend/` from Django when `DEBUG` is on, mirroring `frontend/vercel.json`. That covers `/`, `/repo/{owner}/{name}`, `/compare`, `/about`, `/about/{section}` and top-level `.js`/`.css` files. Every route answers 404 when `DEBUG` is off. In production Vercel serves the pages and forwards `/api/` to the backend.

**Interfaces produced** (`data.js`, pure, loaded as `window.GAData` and as a Node module):
- `show(value, fmt)`, `compareNullable(a, b, dir)` and `sumKnown(values)`: `null` shows as "N/A", sorts last, and is left out of sums.
- `rankingsQuery(state, page)`. Rank by Total stars gives `sort=stars`. Gaining stars gives `sort=gained&window=7d|30d|1y`. Trending gives `sort=trending&trending=1`. The filters map to `lang`, `status` and `archived=0`, with `limit=100`.
- `toRow(apiRow, now)`, `weeksFromHistory(history, stars)`, `daysFromHistory(history, stars, now)` and `compareRecord(detail, now)`.
- `briefFindings(brief)`, `statusTone(status)`, `reportModel(detail, now)`. The report model takes status and brief answers from the API and shows N/A for unknowns. Good-fit and watch-out lines come only from known results.
- `utcStamp(iso)`, `updatedLabel(iso, now)`, `agoLabel(t, now)` and `busyMinutes(retryAfter)`.

| Test | Assertion |
|---|---|
| `test_dev_serves_page_for_each_vercel_route` | All five routes serve their page in DEBUG |
| `test_dev_serves_frontend_scripts` | Top-level `.js` is served |
| `test_dev_does_not_serve_files_outside_the_top_level` | Path traversal and subfolders give 404 |
| `test_dev_frontend_is_off_when_debug_is_off` | 404 without DEBUG |
| `data.test.js` (20 tests) | Each `data.js` function, including null cases and the report model |
| `test_T7_frontend_never_calls_github_or_an_absolute_api_host` | No `api.github.com` or `localhost:8000` in `frontend/` |
| `test_rankings_page_loads_from_relative_api_path` | `index.html` calls `/api/rankings?` |
| `test_report_pages_load_each_repo_from_relative_api_path` | `repo.html` and `compare.html` call `/api/repos/` |
| `test_real_data_pages_use_data_module_not_sample_js` | All three pages load `data.js`, none load `sample.js` |
| `test_real_data_pages_drop_sample_data_notes` | No "Sample data" or "sample repositories" |
| `test_rankings_page_has_no_sample_generator` | No `makeRepo`, `NAMED`, `generate` or `NOW_LABEL` |
| `test_report_pages_show_calculating_message_for_null_charts` | The exact calculating message is present |
| `test_sample_js_is_gone` | `frontend/sample.js` does not exist |

- [x] Write tests, confirm red, commit (`bb0c8a2`, `f967996`, `14c73b0`, `2e65a2d`).
- [x] Serve `frontend/` from Django in DEBUG on the API origin (`e40018c`).
- [x] Load every rankings page at `limit=100` until `count` is reached, for the current Rank by and filters. Column-header sorting, focus, search and paging stay client-side.
- [x] Remove the sample generator, sample-data notes and hard-coded times. Use the real `updated_at` and `fetched_at`.
- [x] Handle `null` in rows, sparklines, last commit, status pill, summary, status counts, sorting and download.
- [x] Disable the AI filter and show "N/A" for the AI summary, because AI data is not collected yet.
- [x] Build the Language filter from the API's `languages`, in API order (T2).
- [x] "Updated <time>" from `updated_at` (T9). "Show more" already existed (T5).
- [ ] Add limit 10 to the Show control (T4). It still offers 25, 50 and 100.
- [x] Report and compare pages load `/api/repos/{owner}/{name}` and render its `brief` instead of `analyse()`. Null values show "N/A". Null charts show "GitHub is still calculating this. Check back in a minute." A 404 shows the API's message.
- [x] Report links, the compare list, Download and the GitHub button use the real repository.
- [x] Lookup on the main page opens `/repo/{owner}/{name}` or `/compare` directly, and the report fetches on demand. Suggestions search the loaded rankings only.
- [ ] Wire lookup and suggestions to `/api/lookup` once Step 7 exists.
- [x] Show "Rankings are being prepared" when `prepared=false` or the API can't be reached. Show the "GitHub is busy" message on 429 or 503.
- [x] Run `node --test 'frontend/tests/*.test.js'` and the backend checks. Node 22 needs a file pattern, not a directory.
- [ ] Manual browser check. The local server ran against Neon: every route answered 200, the API returned 10 ranked repositories, and `data.js` mapped the real responses correctly. No browser was connected, so the rendered pages were not looked at.
- [x] Commit `feat(F7): load rankings, reports and compare from the API [green]` (`87c3169`).

**Known gap:** most report charts show the calculating message, because commit, contributor, issue and release data is not collected (Step 9). The wording stays until then.

**Process note:** `b9e794c` is a `[green]` commit made while the `14c73b0` static tests were still red.

---

### Step 9: Collect activity data (commits, contributors, releases, issue and pull request counts)

- [ ] Fetch and store commit activity, contributor statistics, the release list, and issue and pull request counts through `github_client`, with provenance (F2, F9).
- [ ] Return them from `GET /api/repos/{owner}/{name}` and pass them into the Step 6b brief rules.
- [ ] Compute the previous 30 days of stars and the F8 G7 spike check so the interest answer can be given.
- [ ] Draw the report and compare charts from this data in place of the calculating message.

---

### Step 10: Host the backend on Vercel and refresh daily

- [ ] Deploy the Django backend as its own Vercel project, using `DATABASE_URL` for Neon and `GITHUB_TOKEN` from the environment, with `DEBUG=0`. Code is ready (`api/index.py`, root `vercel.json`, settings from `DEBUG`, `ALLOWED_HOSTS`, `FRONTEND_ORIGIN`). Not yet deployed or checked live.
- [x] Forward the frontend's `/api/` requests to the backend (`https://gitanalyze-backend.vercel.app`).
- [x] Run `refresh_rankings` once a day on a schedule (`.github/workflows/refresh-rankings.yml`). Not yet run for real.
- [ ] Add a per-client throttle to on-demand fetches before going public.

---

## Follow-ups (not in this plan)

- Contributors, AI capabilities, Trending and spike warnings stay "N/A" or hidden until their data is collected.
- **Trending (F8):** the `trending` field is `null` on every row for now, so `sort=trending` and `trending=1` return an empty list. A later step fills it from the GitHubTrendingRSS feed, pending the team's OK on that feed (F0 W3).
- Repository names do not link anywhere until the F1 repository page exists (T6).
- `/api/lookup` spends our token's quota and has no per-client throttle. Add one before deployment.
