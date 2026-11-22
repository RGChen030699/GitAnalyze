# F3: Star History Chart

**Priority:** Must · **Size:** M · **Sprint:** 2 · **Jobs:** J1, J4 · **Proposal stories:** 6 (star history), 4 (time range)

## 1. User story

As someone evaluating a repository, I want to see how its stars grew over time, so that I can tell steady growth from a one-off spike or a stall.

## 2. Data

| Item | Detail |
|---|---|
| Endpoint | `GET /repos/{owner}/{repo}/stargazers/history?per_page=30&page=N` |
| Returns | Weekly entries, newest first: `week` (start time), `total` (stars gained that week), `days` (7 numbers, Sunday first) |
| Full history | Fetch pages until the creation week; about weeks ÷ 30 requests (10-year-old repository ≈ 18) |
| Daily refresh | Page 1 only (F0 daily job) |
| Running total | Add the weeks from the oldest forward. Check against `GET /stargazers/count`; if they differ, show the API total and log the difference |
| Meaning | **Net** stars: removed stars disappear from past weeks too, so older weeks can change slightly |
| Caveat | Week and day boundaries are not guaranteed to be UTC |

**Never** build this from the stargazer list or from event datasets (see F0).

## 3. Requirements

| # | Requirement |
|---|---|
| H1 | Line chart of cumulative stars over time, with ranges **1 month / 1 year / All**. Default is All. |
| H2 | The 1-month view uses daily points from `days`; longer views use weekly points. |
| H3 | Tooltip: date, stars gained that week (or day), running total. |
| H4 | Optional second view: bar chart of stars gained per week. |
| H5 | Summary line above the chart: "+N stars in the last 7 days · +N in the last 30 days · N total". |
| H6 | Overlay up to 3 repositories (used by F5), each in a distinct, colour-blind-safe colour with a legend. |
| H7 | Label: "Net stars (current stargazers by the date they starred). Source: GitHub star history API. Updated <date>." |

## 4. Acceptance criteria

- [ ] Given a repository created 3 years ago, when I open it, then the "All" view starts at its creation week and ends at the current week.
- [ ] Given I choose "1 month", when the chart redraws, then it shows about 30 daily points.
- [ ] Given stored weekly data, when I hover a point, then I see the date, stars gained, and running total.
- [ ] Given the summed history differs from `/stargazers/count`, when the page loads, then the headline total uses the API count and the difference is logged.
- [ ] Given a repository with 0 stars, when I open it, then the chart area shows "No stars yet" instead of an empty chart.
- [ ] Given the daily job ran, when it refreshed this repository, then only page 1 was requested.
- [ ] Given three repositories on the comparison page, when the chart loads, then three labelled lines share one time axis.

## 5. Edge cases

- **The endpoint returns 422 ("validation failed or the endpoint has been spammed"):** keep stored data, show "Couldn't refresh star history" with the last update date.
- **Repositories older than 3,000 weeks:** not possible on GitHub; no special handling.

## 6. Out of scope

- 5- and 10-year presets.
