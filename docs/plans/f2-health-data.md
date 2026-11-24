# F2 health data: plan

Goal: the report page's health checks stop showing N/A. Commits, contributors, releases, license
and age come from real GitHub data, per `docs/prd/F2-health-summary.md`.

## Request budget

The daily ranking refresh stays at about 3 requests per repository, so it fits under 5,000 an hour
for 1,000 repositories. Health data is fetched **when someone opens a report**, then cached for 24
hours (cache-first, F1 L4). Each report open costs at most 4 requests: commit activity, contributor
stats, contributor count and tags (tags only when there are no releases).

Releases are already fetched in the daily refresh. That step now also stores the release list, at
no extra cost.

## Steps (TDD: red, then green)

1. Pure rules in `health/services.py`:
   - `contributor_commits` and `single_maintainer`: M1–M5
   - `last_release` and `releases_last_12_months`: V1–V4
   - `commit_activity_view`: C1–C3
   - `license_note`: L1–L3
   - `contributor_count`
2. Client changes:
   - `stats_retry_waits=()`: a serverless request can't sleep 62 s on a 202 (C5), so it returns
     "pending" at once and the next page open tries again.
   - `GitHubResponse.last_page`: the page count from the `Link` header, used for the contributor
     count.
3. Store the data:
   - New `Repository.health` JSON field holding each part's data, source and fetch time.
   - New `Repository.health_fetched_at` and `Repository.releases` fields.
   - `refresh_health(client, repo, now)` runs from the detail view when the data is missing, older
     than 24 h or still pending.
4. Serializer:
   - Add the fields: `commit_activity`, `contributors`, `releases`, `last_release`, `releases_12m`,
     `single_maintainer`, `top_contributors`, `license`, `created_at`, each with its provenance.
   - Fill the brief answers: maintenance (13 weeks against the 13 before), release pace and
     maintainer concentration.
5. Frontend: map these fields in `data.js reportModel`, so the commit, heatmap, contributor and
   release charts and the license and maintainer checks render.

Issue and PR trends stay N/A until F9.
