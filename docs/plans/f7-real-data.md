# F7 Real GitHub Data Implementation Plan

> **Execution:** Native, in the main session, with no subagent-driven development. Do only the step the user names, then stop and wait. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the sample data in `frontend/index.html` with real GitHub data stored in our database, refreshed by hand with a management command.

**Architecture:** `refresh_rankings` builds a small watch list through `github_client` and stores repositories and weekly star points with provenance. `GET /api/rankings` reads only the database. `GET /api/lookup` fetches 1–3 repositories on demand with a 24-hour database cache. The frontend loads every rankings page, then keeps its existing client-side filters, sorting and summary.

**Tech Stack:** Python 3.12, Django 5, DRF, PostgreSQL 16 (SQLite locally), pytest, `responses`, plain JavaScript, Node's built-in test runner. No new dependencies.

**Spec:** `docs/prd/F7-top-repositories.md`, with `F0`, `F1` (L1–L4), `F2` (R1–R4, S1–S5), `F3` §2 and `F8` §2.

**Status:** Steps 1 and 3a are done. Steps 2, 3 and 4–8 have not been implemented.

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

- [ ] Write tests, confirm red, commit `test(F0): per-resource rate limits [red]`.
- [ ] Track quota per resource, keyed by the `x-ratelimit-resource` header. Before a request, treat `/search/` paths as `search` and all others as `core`. Keep `rate_limit_margin` for core.
- [ ] Wrap `requests.RequestException` as `GitHubError`.
- [ ] Run the checks, commit `feat(F0): track rate limits per resource [green]`.

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

- [ ] Write tests, confirm red, commit `test(F0): search helper [red]`.
- [ ] Implement, using `dataclasses.replace` to put the query in `source`.
- [ ] Run the checks, commit `feat(F0): add repository search helper [green]`.

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
- `repositories.ingest.refresh_details(client: GitHubClient, repo: Repository, now: datetime) -> None`

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

- [ ] Write tests, confirm red, commit `test(F7): models, rules and refresh command [red]`.
- [ ] Implement the models and create the migration with `makemigrations`.
- [ ] Implement the command. Per repository, fetch 2 history pages (`per_page=30`, enough for 52 weeks) and `GET /repos/{owner}/{repo}/releases?per_page=100`. Basic fields come from the search result. Save each repository in its own transaction.
- [ ] Add `RANKINGS_LANGUAGES=Python,TypeScript,JavaScript` to `.env.example`. Claude's permissions block that file, so the user runs this edit.
- [ ] Budget check, for `L` languages: at most `1 + L` searches + `(100 + 50L) × 3` core requests, or `301 + 151L` per run. The default (`L = 3`) is 4 searches + 250 × 3 = **754 requests**. Each extra language adds up to 151. With `--limit N`, the total is at most `1 + L + 3N`.
- [ ] Run the checks, commit `feat(F7): store rankings via refresh_rankings [green]`.

---

### Step 5: `GET /api/rankings` and CORS

**Files:**
- Create: `backend/rankings/__init__.py`, `views.py`, `serializers.py`, `backend/config/cors.py`
- Modify: `backend/config/urls.py`, `backend/config/settings.py`
- Test: `backend/tests/test_rankings_api.py`, `test_cors.py`

**Interfaces produced:** `rankings.serializers.serialize_row(repo: Repository) -> dict`. Setting `FRONTEND_ORIGIN`, default `http://localhost:8080`. Sort values: `stars` (default), `gained_7d`, `gained_30d`, `gained_year`, `pushed`.

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

**Files:**
- Create: `frontend/rows.js`, `frontend/tests/rows.test.js`
- Modify: `frontend/index.html`
- Test: `backend/tests/test_frontend_static.py`

**Interfaces produced** (`rows.js`, classic script that also exports for Node):
- `toRow(apiRow, now: Date) -> Row` maps to the existing shape: `pushed` as days ago, `weeks` oldest first, `null` preserved.
- `display(value, format) -> string` returns "N/A" for `null`.
- `compareNullable(a, b, dir) -> number` puts `null` last in both directions.
- `sumKnown(values) -> number | null` returns `null` when every value is `null`.
- `languageOptions(languages) -> string[]` returns `"Any"` followed by the API's language names, in API order.

| Test | Assertion |
|---|---|
| `toRow converts pushed_at to days ago` | Fixed `now`; `null` stays `null` |
| `toRow keeps weeks oldest first` | Same order as the API |
| `display shows N/A for null but keeps real 0` | `0` stays `0` |
| `compareNullable sorts null last both ways` | Ascending and descending |
| `sumKnown ignores null and returns null if all null` | Both cases |
| `languageOptions keeps API order after Any` | Not re-sorted alphabetically; an empty list gives only `Any` |
| `test_T7_frontend_never_calls_github_api` | `index.html` and `rows.js` contain no `api.github.com` |
| `test_frontend_has_no_sample_data` | No `makeRepo`, `generate`, `NAMED`, "Sample data" or demo panel |

- [ ] Write tests, confirm red, commit `test(F7): frontend row mapping [red]`.
- [ ] Read the API base URL from `<meta name="gitanalyze-api-base">`, default `http://localhost:8000`.
- [ ] Load all rankings pages at `limit=100` until `count` is reached. The existing controls need window, status and archived filters that the API does not take.
- [ ] Remove the sample generator, demo panel, sample-data notes and hard-coded "Today at 04:10 UTC". Use real `fetched_at` and `updated_at`.
- [ ] Handle `null` in `rowHtml`, `spark`, `ago`, `statusPill`, `renderSummary`, status counts, sorting and CSV.
- [ ] Disable the AI filter and show "N/A" for the AI summary, because AI data is not collected yet.
- [ ] Apply the small F7 fixes: add limit 10 (T4), "Show more" (T5), "Updated <time>" (T9).
- [ ] Build the Language filter from the API's `languages` with `languageOptions`, so it lists only languages present in the database, sorted by repository count (T2). Remove any hard-coded language list.
- [ ] Wire lookup to `/api/lookup`, merge returned rows into the list, and show API error text. Debounce suggestions to 400 ms and abort stale requests. Picking a suggestion runs a lookup.
- [ ] Show "Rankings are being prepared" only when `prepared=false`. If the API is unreachable, show "Couldn't load rankings" with a retry button.
- [ ] Run `node --test frontend/tests/`, plus the backend checks.
- [ ] Manual check: serve with `python -m http.server 8080 --directory frontend`, then verify empty database, `refresh_rankings --limit 10`, filters, a 404 lookup, and no browser requests to `api.github.com`.
- [ ] Commit `feat(F7): load rankings and lookup from the API [green]`.

---

## Follow-ups (not in this plan)

- Contributors, AI capabilities, Trending and spike warnings stay "N/A" or hidden until their data is collected.
- Repository names do not link anywhere until the F1 repository page exists (T6).
- `/api/lookup` spends our token's quota and has no per-client throttle. Add one before deployment.
