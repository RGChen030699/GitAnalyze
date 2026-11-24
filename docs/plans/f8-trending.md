# F8 trending: plan

Goal: the Trending tab lists GitHub Trending repositories in GitHub's order, with our computed
stars (F0 W3, F8 G4 and G5).

## Source

The GitHubTrendingRSS feed at `https://mshibanami.github.io/GitHubTrendingRSS/{period}/{slug}.xml`.
Each item has a title (`owner/name`), a link and a description, but no star numbers. Language
slugs are lowercase, with spaces replaced by `-` and `#` written as `%23` (for example `c%23`,
`c++`, `jupyter-notebook`). The feed is not the GitHub API, so the request carries no token and
costs nothing from the 5,000-an-hour budget.

The feeds checked on 2026-11-24 listed 281 unique repositories: daily, weekly and monthly `all`,
plus weekly for the 18 languages. Repositories that aren't already tracked cost about 4 GitHub
requests each, roughly 1,100 a day, which still fits the hourly budget.

## Steps (TDD)

1. `github_client/trending.py`, the only code that reads the feed:
   - `feed_slug`, `feed_url` and `parse_feed`: pure functions that return names in feed order.
   - `fetch_trending`: sends no GitHub token and raises `TrendingFeedError` when the feed is
     unreachable.
2. `Repository.trending` (a JSON map from feed key to rank, for example `{"all": 3, "Python": 1}`)
   and `Repository.trending_at`, in migration 0003.
3. `refresh_trending` management command:
   - Reads the feeds.
   - Adds any listed repository not refreshed in the last 20 hours: `GET /repos`, then the
     normal details refresh, ranked.
   - Replaces the weekly ranks only for feeds that answered. When a feed is unreachable, the
     job keeps yesterday's ranks and doesn't fail.
4. Rankings API:
   - `sort=trending` orders by rank in the weekly feed for the chosen language, or `all` when no
     language is chosen. `trending=1` filters to repositories that have a rank.
   - Each row's `trending` is that rank.
   - The response gains `trending_updated_at`.
5. The detail API returns `trending`, the rank in the weekly `all` feed.
6. Frontend: on the Trending tab, the credit "From GitHub Trending" linking to github.com/trending,
   and "Trending last updated <date>".
7. Workflow: run `refresh_trending` after `refresh_rankings`.
