# F9: Issue and Pull Request Trends

**Priority:** Should (later sprint) · **Size:** M · **Sprint:** 4 · **Job:** J1 · **Proposal story:** 6 ("issues, and pull request trends")

## 1. User story

As someone evaluating a repository, I want to see whether issues and pull requests are being opened and handled over time, so that I can tell if the maintainers keep up.

## 2. Approach

Build after F1–F8. First test on a few large "foundation" repositories to see real numbers, then decide the presentation.

**Test set [ASSUMPTION]:** `microsoft/vscode` (very busy), `facebook/react`, `vercel/next.js`, `anthropics/skills` (young), plus one small, quiet repository.

## 3. Data

- **Method:** count-only searches, one number per month, batched into **one GraphQL query** with aliases:
  ```graphql
  query {
    jan_opened: search(type: ISSUE, query: "repo:o/r is:issue created:2026-01-01..2026-01-31", first: 0) { issueCount }
    jan_closed: search(type: ISSUE, query: "repo:o/r is:issue closed:2026-01-01..2026-01-31", first: 0) { issueCount }
    jan_pr_opened: search(type: ISSUE, query: "repo:o/r is:pr created:2026-01-01..2026-01-31", first: 0) { issueCount }
    jan_pr_merged: search(type: ISSUE, query: "repo:o/r is:pr merged:2026-01-01..2026-01-31", first: 0) { issueCount }
    # … 12 months × 4 series = 48 aliases, possibly split into 2 queries
  }
  ```
- **Why GraphQL:** plain REST search allows only 30 requests per minute, so 48 numbers would take about 2 minutes per repository.

**To verify in the test (spike tasks):**

| # | Question | Pass condition |
|---|---|---|
| V1 | Is `issueCount` exact above 1,000? | Compare one busy month on `microsoft/vscode` with GitHub's web search count |
| V2 | Do `closed:` and `merged:` date ranges work as expected? | Counts match the web UI for 2 sample months |
| V3 | GraphQL point cost of the 48-alias query | Read `rateLimit { cost }`; must fit the hourly budget for the watch list |
| V4 | *(Exploratory)* Cost of "median time to first reply" | Estimate requests per repository; decide whether it's feasible |

## 4. Requirements (draft, to finalise after the test)

| # | Requirement |
|---|---|
| I1 | Two small charts on the repository page: **Issues** (opened vs closed per month) and **Pull requests** (opened vs merged per month), last 12 months. |
| I2 | One-line summary: "Last 12 months: N issues opened, M closed. K pull requests merged." |
| I3 | Refreshed weekly, not daily, for watch list repositories [ASSUMPTION]; fetched on demand for looked-up repositories. |
| I4 | Numbers carry provenance (F6). If V1 fails, months above 1,000 show "1,000+". |
| I5 | Adds rows to the F5 comparison table. |

## 5. Acceptance criteria (draft)

- [ ] Given a repository, when its page loads, then both charts show 12 months with opened and closed (or merged) bars.
- [ ] Given a month where the count may be inexact (V1 failed), when it displays, then it shows "1,000+" with an explanation.
- [ ] Given the 48-alias query, when run for one repository, then its cost is recorded and within the budget set after V3.
- [ ] Given a repository with issues disabled, when the page loads, then the issue chart says "Issues are turned off for this repository".

## 6. Out of scope (for now)

- Per-issue analysis (labels, response times) unless V4 shows it's affordable.
