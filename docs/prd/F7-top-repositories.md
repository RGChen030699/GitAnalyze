# F7: Top Repositories (Browse, Filter, Limit, Keep Scrolling)

**Priority:** Should · **Size:** M · **Sprint:** 3 · **Job:** J4 · **Proposal stories:** 1, 3

## 1. User stories

- (Story 1) As a developer exploring a technology category, I want to browse top repositories and filter by language and ranking, so that I can find relevant projects.
- (Story 3) As a user browsing repositories, I want to choose a result limit (top 10, 25, 50 or 100) and keep scrolling beyond that list, so that I can control how many projects I explore.

## 2. Requirements

| # | Requirement |
|---|---|
| T1 | Page `/explore` with two category tabs: **All** and **AI tools & skills**. *AI tools & skills* = watch list repositories with any F4 finding at level 1–3, or tagged with an AI topic (F0, W2). |
| T2 | Filters: **language** (top 15 languages in the watch list, plus "Any"), **has AI capabilities** (yes / any), **hide archived** (default on). |
| T3 | Sort options: **Most stars** (total), **Most stars gained** (window from F8: week / month / year), **Recently active** (`pushed_at`). |
| T4 | Result limit selector: **10 / 25 / 50 / 100**. Default 25. |
| T5 | After the chosen number, a "Show more" button and infinite scroll load the next page of the same size, until the watch list runs out. |
| T6 | Each row shows: rank, `owner/name` (links to the F1 page), description (one line), language, total stars, stars gained in the selected window, F2 status label, AI badge if any. |
| T7 | All data comes from our database (daily job). No GitHub call on page load. |
| T8 | Filter, sort and limit are kept in the URL (`/explore?tab=ai&lang=python&sort=stars&limit=50`) so a view can be shared. |
| T9 | Footer: "Rankings cover N repositories we track: top by stars, GitHub Trending, AI topics, and repositories users looked up. Updated <time>." (F6) |

## 3. Acceptance criteria

- [ ] Given I choose language "Python" and sort "Most stars", when the list loads, then every row is a Python repository, in descending total stars.
- [ ] Given limit 10, when the list loads, then exactly 10 rows show, followed by "Show more".
- [ ] Given limit 10, when I scroll to the bottom, then the next 10 rows load (ranks 11–20).
- [ ] Given the "AI tools & skills" tab, when the list loads, then every row has an AI badge or an AI topic.
- [ ] Given "hide archived" is on, when the list loads, then no archived repository appears.
- [ ] Given I copy the URL and open it elsewhere, then the same filters, sort and limit are applied.
- [ ] Given the page loads, when network requests are inspected, then none go to api.github.com.
- [ ] Given a filter combination with no results, when the list loads, then I see "No repositories match these filters" and a reset link.

## 4. Edge cases

- **Ties in stars:** break ties by `full_name` so ordering is stable while scrolling.
- **The daily job hasn't run yet** (new deployment): show "Rankings are being prepared" instead of an empty list.

## 5. Out of scope

- Free-text search inside the list (F1 covers search).
- Topics other than the AI topics listed in F0.
