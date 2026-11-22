# Plan: F0 GitHub client

## Context

Sprint 0 needs the single module all GitHub access goes through. The source is `~/Downloads/1. prd/F0-github-data-foundation.md`, section 3.1 (C1–C10) and its client-related acceptance criteria. The repo has only a Django skeleton, with `settings.GITHUB_TOKEN` already defined at `backend/config/settings.py:90`.

**In scope:** C1–C10. **Out of scope:** database schema, watch list, daily job, on-demand fetch, and any endpoint-specific wrappers for F1–F9. Acceptance criteria that need the database ("stored as pending", "no new row written", "`full_name` is stored") are covered here only at the client boundary: the client returns the state, and persistence tests arrive with the schema.

## Design

A plain package at `backend/github_client/`. It has no models, so it is not added to `INSTALLED_APPS`.

- `client.py`: `GitHubClient` with `get(path, params=None) -> GitHubResponse` and `get_raw(owner, repo, ref, path) -> GitHubResponse`.
- `types.py`: frozen `GitHubResponse` with `data`, `status` (`ok` or `pending`), `source`, `fetched_at`, `cost`, `from_cache`, `final_url`.
- `errors.py`: `GitHubError`, `MissingTokenError`, `RateLimitError`, `ForbiddenEndpointError`.
- `etag_store.py`: `ETagStore` Protocol plus `InMemoryETagStore`, so a database-backed store can replace it when the schema lands.
- `sleep` and `clock` are constructor arguments, so tests never really wait.
- Every request sets an explicit timeout, because `requests` has no default and the enabled ruff rules do not flag this.
- The token check treats an empty value as missing, because `settings.GITHUB_TOKEN` defaults to `""`.
- Tests live in `backend/tests/test_github_client.py`, use `responses`, and set the token through pytest-django's `settings` fixture so a token exported in the shell cannot affect results. No new dependencies are needed.

## Pushback round (changes made to the first draft)

1. **A plain 403 is not always a rate limit.** C4 read literally would spend minutes retrying a permissions error. Retry a 403 only with `retry-after`, `x-ratelimit-remaining: 0`, or a rate-limit message in the body. Otherwise raise immediately. A 429 always retries.
2. **"5 tries" vs "retries at most 5 times".** Use 5 total attempts, which satisfies both C4 and the acceptance criterion.
3. **202 handling.** The wait list 2, 4, 8, 16, 32 means 1 initial request plus 5 retries, then `status="pending"` with no exception.
4. **Token check happens at fetch time, not import time,** so the app and tests can start without a token. The message is exactly `GITHUB_TOKEN is not set`, and no request is sent.
5. **Do not send the token to `raw.githubusercontent.com`.** C9 content is public and uses no API quota, so the credential stays off that host.
6. **Cost is defined explicitly.** It counts quota-charged requests in a call, including retries. A 304 and raw fetches cost 0.

## Steps (one commit each)

First, on a new branch `feat/f0-github-client`, save this plan to `docs/plans/f0-github-client.md` and commit it as `[plan] F0 GitHub client`.

1. **`feat(github): client core with auth, headers, provenance`** covers C1, C2, C7, C8, C10. Tests: missing token sends no request, headers, 301 returns the canonical URL and data, provenance fields, `/stargazers` rejected while `/stargazers/history` and `/count` style paths are not.
2. **`feat(github): rate limits, retries, and 202 handling`** covers C3, C4, C5. Tests: `remaining: 150` waits until reset, `retry-after: 30`, 60-second default then exponential backoff, gives up after 5 tries and logs, plain 403 fails fast, 202 five times returns pending.
3. **`feat(github): ETag caching, raw files, and guard tests`** covers C6, C9, and the constraints. Tests: 304 reuses stored data at cost 0, raw fetch has no `Authorization` header, a source scan finds no forbidden `/stargazers` call or direct `api.github.com` use outside the client, and an autouse fixture blocks real network access in tests.

## Verification

Run after each step, and in full at the end:

```sh
.venv/bin/ruff check .
.venv/bin/ruff format --check backend/github_client backend/tests
.venv/bin/mypy backend
.venv/bin/python -m pytest
```

The repo already has one ruff error, one mypy error (both in `settings.py`), and 5 unformatted files. These stay untouched and will be reported as existing failures, and all new code must be clean. Nothing is pushed unless requested.
