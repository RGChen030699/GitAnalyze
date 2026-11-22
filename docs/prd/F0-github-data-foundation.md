# F0: GitHub Data Foundation

**Priority:** Must · **Size:** L · **Sprint:** 0 (client, schema), 3 (daily job) · **Serves:** every feature

## 1. Scope

**In:**
- one GitHub client module;
- the PostgreSQL schema;
- the daily refresh job;
- the watch list;
- an on-demand fetch for a single repository (used by F1).

**Out:**
- user accounts;
- dependency alerts (J5);
- any data source other than the GitHub REST/GraphQL API, raw.githubusercontent.com, and the GitHubTrendingRSS feed.

## 2. Requirements

### 3.1 GitHub client (one module, for example `github_client/`)

| # | Requirement |
|---|---|
| C1 | Reads the token from the `GITHUB_TOKEN` environment variable. Fails with a clear error if it is missing. |
| C2 | Sends `Accept: application/vnd.github+json` and a fixed API version header. |
| C3 | After every response, records `x-ratelimit-remaining` and `x-ratelimit-reset`. When `remaining` falls below a safety margin (default 200), pauses until the reset time. |
| C4 | On a 403 or 429 with `retry-after`, waits that many seconds. Without the header, waits 60 seconds, then backs off exponentially. Gives up after 5 tries and logs the failure. |
| C5 | On **202 Accepted** (statistics still computing), retries up to 5 times with a growing wait (2, 4, 8, 16, 32 seconds), then marks the metric "pending" rather than failing the page. |
| C6 | Stores the `ETag` for each URL and sends `If-None-Match` next time. A **304** reuses the stored data and does not count against the limit. |
| C7 | Follows redirects, because renamed repositories return 301. Stores the canonical `full_name`. |
| C8 | Every call returns the data **plus** `source` (the endpoint), `fetched_at`, and the request cost, so F6 can store provenance. |
| C9 | Raw file contents (for F4) come from `raw.githubusercontent.com`, which does not use API quota. |
| C10 | **Forbidden:** `GET /repos/{owner}/{repo}/stargazers`, which has been restricted to repository admins since July 2026. The client must not expose a method for it. |

### 3.2 Database schema (first version) [ASSUMPTION: names can change]

| Table | Key fields |
|---|---|
| `repository` | id, full_name, owner_login, owner_type (User or Organization), description, language, topics, license_spdx, archived, fork, default_branch, created_at, pushed_at, stargazers_count, forks_count, open_issues_count, last_fetched_at, raw (JSONB) |
| `star_week` | repository, week_start, stars_gained, days (7 integers), fetched_at. Unique on (repository, week_start) |
| `metric_value` | repository, metric_key, value (numeric or JSONB), source, method_key, fetched_at. History is kept, not overwritten |
| `release` | repository, tag, name, published_at, prerelease |
| `ai_finding` | repository, level, path, name, description, rule_matched, blob_sha, details (JSONB), fetched_at |
| `watch_list_entry` | repository, reason (top_stars, trending, user_lookup, ai_topic), added_at, last_seen_in_source_at |
| `fetch_log` | url, status, etag, cost, fetched_at, error |

### 3.3 Watch list

| # | Requirement |
|---|---|
| W1 | **Top by stars:** the top N repositories by stars from the Search API, overall and per language (N pending team decision: 1,000 or 3,000). Each search returns at most 1,000 results, so split the query by star bands (for example `stars:10000..*`, `stars:5000..9999`). |
| W2 | **AI topics:** repositories with topics `agent-skills`, `claude-skills`, `claude-code-plugin`, `claude-code-skills`, `mcp-server`, sorted by stars. Top 500 per topic [ASSUMPTION]. |
| W3 | **GitHub Trending:** daily, read the GitHubTrendingRSS feeds (`daily/all.xml`, `weekly/all.xml`, `monthly/all.xml`, plus per-language feeds for the languages we offer) and add every listed repository. *Pending team OK on using this third-party feed.* |
| W4 | **User lookups:** any repository looked up in F1 joins the list. |
| W5 | A repository leaves the list if no source has listed it for 90 days and nobody has looked it up [ASSUMPTION]. |

### 3.4 Daily job

- Runs as a Django management command, for example `python manage.py refresh_daily`. The scheduler (cron or Celery beat) depends on where we host, which the team has not decided yet.
- **Steps:**
  1. refresh the watch list (W1–W4);
  2. for each repository: refresh the basic fields (1 request, usually a 304) and the newest page of star history (1 request);
  3. recompute F7 and F8 rankings;
  4. write a run summary (repositories refreshed, requests used, failures).
- **Budget:** a 3,000-repository list needs about 6,000 requests, about 1.2 hours with one token.
- **One-off backfill:** full star history for every watch list repository is about 18–33 requests each, roughly 10 hours for 3,000. Run it once, overnight.

### 3.5 On-demand fetch (used by F1)

The full fetch for one repository uses about 20–45 requests: basic fields, all star history pages, statistics, releases, contributors, and the file tree. Results are cached; a repository fetched within the last 24 hours is served from the database.

## 3. Acceptance criteria

- [ ] Given `GITHUB_TOKEN` is missing, when the app starts a fetch, then it fails with the message "GITHUB_TOKEN is not set" and makes no request.
- [ ] Given a response with `x-ratelimit-remaining: 150`, when the next call is made, then the client waits until `x-ratelimit-reset` before sending it.
- [ ] Given a 403 with `retry-after: 30`, when the client retries, then it waits at least 30 seconds and retries at most 5 times.
- [ ] Given a statistics endpoint returns 202 five times, when the fetch finishes, then the metric is stored as "pending" and the rest of the repository data is saved.
- [ ] Given a stored ETag, when GitHub returns 304, then the stored data is reused and no new row is written.
- [ ] Given a renamed repository (301), when it is fetched, then `full_name` is stored as the new name.
- [ ] Given any fetched value, when it is saved, then `source` and `fetched_at` are stored with it.
- [ ] Given the codebase, when searched, then no code calls `/stargazers` without `/history` or `/count` after it (a test enforces this).
- [ ] Given the daily job runs, when it finishes, then a run summary records the repositories refreshed, requests used, and failures.
- [ ] Given CI runs, when tests execute, then no request reaches api.github.com (recorded fixtures only).

## 4. Constraints

1. All GitHub access goes through the client module; no direct `requests.get("https://api.github.com/...")` elsewhere.
2. Never use the stargazer list endpoint, GH Archive, BigQuery `githubarchive`, ClickHouse playgrounds, or OSS Insight. Their star data is restricted, broken, or shutting down.
3. Web pages read from the database; only the daily job and the F1 on-demand fetch call GitHub.

## 5. Open questions

- Hosting, and therefore the scheduler (cron or Celery).
- Watch list size N.
- Team OK on the GitHubTrendingRSS feed.
