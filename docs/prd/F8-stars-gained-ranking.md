# F8: Stars-Gained Ranking and GitHub Trending

**Priority:** Should · **Size:** M · **Sprint:** 4 · **Job:** J4 · **Proposal stories:** 2, 4

## 1. User stories

- (Story 2) As a user looking for emerging tools or AI skills, I want to see repositories gaining stars quickly, so that I can identify projects receiving recent attention.
- (Story 4) As a user exploring repository trends, I want to filter by a time range (a week, a month or a year), so that I can compare recent traction with longer-term growth.

## 2. Data

| Need | Source |
|---|---|
| Stars gained per repository | `star_week` table (F3 data). **Week** = last 7 days from the `days` arrays; **month** = last 30 days; **year** = last 52 weeks |
| Fastest-growing repositories across GitHub | GitHub's official Trending page, read through the GitHubTrendingRSS feed (F0, W3). Feed items carry name, link and description, **but no star numbers**, so we compute those ourselves |
| Coverage | Our watch list (F0). Every repository that appears on Trending is added automatically, so viral newcomers are caught |

## 3. Requirements

| # | Requirement |
|---|---|
| G1 | Page section (or tab on `/explore`) **"Gaining stars"** with windows **This week / This month / This year**. Default: this week. |
| G2 | Same filters, limit and scrolling as F7 (language, AI capabilities, 10/25/50/100, keep scrolling). |
| G3 | Each row shows stars gained in the window, total stars, and a small sparkline of the last 12 weeks. |
| G4 | **"On GitHub Trending this week"** block: the repositories from the weekly feed, in GitHub's order, with our computed "+N stars this week", and the credit "From GitHub Trending" linking to github.com/trending. |
| G5 | Repositories that are on Trending get a small "Trending" badge in all lists. |
| G6 | Coverage footer, as in F7 (T9). |
| G7 *(Could)* | **Spike warning:** flag when stars gained in the last 7 days ≥ 1,000 **and** forks + open issues are under 1% of total stars [ASSUMPTION: thresholds]. Text: "Unusual spike: lots of new stars but little other activity." Explained in F6. |

## 4. Acceptance criteria

- [ ] Given "This week", when the list loads, then rows are ordered by stars gained in the last 7 days, highest first.
- [ ] Given "This month", when the list loads, then the stars-gained column covers the last 30 days and the heading says so.
- [ ] Given a repository on today's weekly Trending feed but not yet in our database, when the daily job runs, then it is added to the watch list, its star history is fetched, and it appears in the Trending block with a computed "+N stars this week".
- [ ] Given the Trending block, when it renders, then it shows the credit "From GitHub Trending" with a link.
- [ ] Given the feed is unreachable, when the daily job runs, then the Trending block keeps yesterday's list with "Trending last updated <date>", and the job does not fail.
- [ ] Given the time-range control, when I open it, then the options are week, month and year only.
- [ ] *(Could)* Given a repository gained 3,000 stars this week with 5 forks and 0 issues out of 3,200 total stars, when it appears in a list, then it shows the spike warning.

## 5. Edge cases

- **A repository created this week:** "This year" equals its total; fine.
- **Net stars can make a week negative** (more removals than new stars): show negative values as they are; sort them last.

## 6. Out of scope

- Scraping github.com/trending ourselves (robots.txt disallows the weekly and monthly addresses).
- Paid sources (Trendshift API) unless the team decides otherwise.
- 5- and 10-year windows.

## 7. Open questions

- Team OK on the GitHubTrendingRSS feed (a third-party feed built from the Trending page; GitHub's rules neither clearly allow nor forbid it).
