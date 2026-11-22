# F2: Repository Health Summary

**Priority:** Must · **Size:** M · **Sprint:** 1 · **Job:** J1 · **Proposal story:** 6 (contributors, releases)

## 1. User story

As someone checking a candidate, I want to see at a glance whether the project is still active and who maintains it, so that I don't adopt something that is about to be abandoned.

## 2. What the summary shows

| Field | Source (GitHub) | Notes |
|---|---|---|
| Status label | Computed (rule below) | Active / Slowing / Quiet / Archived |
| Last commit | `pushed_at` on the repository | Shown as "3 days ago", with the full date on hover |
| Last release | `GET /releases?per_page=100` (falls back to `/tags`) | "No releases" if none; prereleases marked |
| Releases in the last 12 months | Same | Count |
| Commits per week, last 52 weeks | `GET /stats/commit_activity` | Small bar chart; may be "pending" (F0, C5) |
| Contributors | `GET /contributors?per_page=1&anon=1`, count read from the `Link` header's last page | "About N contributors" |
| Single-maintainer flag | `GET /stats/contributors` | Flag if one person made ≥ 80% of commits in the last 12 months [ASSUMPTION: threshold] |
| Archived | `archived` | Red badge: "Archived by its owner: read-only, no further updates" |
| License | `license.spdx_id` | "No license" shown in amber: legally, others may not reuse it |
| Publisher | `owner.type` | "Organization" or "Personal account" |
| Stars, forks | `stargazers_count`, `forks_count` | Plain-language tooltip (F6) |
| Open issues and pull requests | `open_issues_count` | GitHub counts both together; label it that way |
| Created | `created_at` | Age, for example "4 years old" |
| Fork of | `fork`, `parent` | Link to the original |

### Status rule [ASSUMPTION: thresholds to tune with real data]

| Label | Rule |
|---|---|
| **Archived** | `archived = true` |
| **Active** | Commit in the last 30 days **and** (a release in the last 6 months **or** no releases ever) |
| **Slowing** | Commit in the last 6 months, but not Active |
| **Quiet** | No commit in the last 6 months |

The rule is displayed next to the label (F6).

### Exact rules

**General**

| # | Rule |
|---|---|
| R1 | All dates are compared in UTC. Every rule takes `now` as an argument, so tests never depend on today's date. |
| R2 | "Within N days" includes day N: a commit exactly 30 days ago counts as within 30 days. |
| R3 | "6 months" = 182 days, "12 months" = 365 days [DEFAULT]. Fixed day counts, not calendar months, so the rule is the same on every date. |
| R4 | "Last commit" = the repository's `pushed_at`. This counts a push to any branch, not only the main one; the F6 tooltip says so. If `pushed_at` is missing, the repository is treated as having no commit (status "Quiet"). |

**Status label** (`compute_status`)

| # | Rule |
|---|---|
| S1 | Archived wins over everything else. |
| S2 | Only published releases count: drafts are ignored, prereleases count [DEFAULT]. Plain tags do **not** count as releases here; a repository with tags but no releases counts as "no releases ever". |
| S3 | Active = last commit within 30 days **and** (newest release within 182 days **or** no releases ever). |
| S4 | Slowing = last commit within 182 days, but not Active. |
| S5 | Quiet = last commit more than 182 days ago, or no commit at all. |

**Single-maintainer flag** (`single_maintainer`)

| # | Rule |
|---|---|
| M1 | Input is `/stats/contributors`: per account, a list of weeks with a commit count. Only weeks starting within the last 365 days are counted. |
| M2 | Accounts whose login ends in `[bot]` are removed before calculating, from both the account's own count and the total. |
| M3 | If one account made **80% or more** of the remaining commits (80% exactly counts), return that login. Otherwise return nothing. |
| M4 | If no commits remain (none in the last year, or only bots), return nothing. |
| M5 | If the statistics are still "pending" (F0, C5), return "pending", not "no single maintainer". |

**License** (`license_note`)

| # | Rule |
|---|---|
| L1 | No license → amber warning: "No license: others may not legally reuse this code." |
| L2 | `spdx_id` = "NOASSERTION" → display "Custom or unrecognized license", no amber warning (a license file exists, GitHub just couldn't name it). |
| L3 | Any other `spdx_id` → display it (for example "MIT"), no warning. |

**Last release and release count** (`last_release`, `releases_last_12_months`)

| # | Rule |
|---|---|
| V1 | Last release = the newest non-draft release by `published_at`. If it is a prerelease, it is still returned, marked as a prerelease. |
| V2 | No releases but tags exist → return the newest tag, marked as a tag with the note "tag, not a formal release". GitHub's tag list has **no dates**, so "newest" = highest version number when the tag names look like versions (`v1.10.0` is newer than `v1.9.2`); if they don't, take the first tag GitHub lists [DEFAULT]. |
| V3 | No releases and no tags → return nothing ("No releases"). |
| V4 | Releases in the last 12 months = number of non-draft releases (prereleases included) with `published_at` within 365 days. |

**Commits-per-week chart** (`commit_activity_view`)

| # | Rule |
|---|---|
| C1 | If F0 marked the statistics as "pending" → status "pending", message "GitHub is still calculating this, check back in a minute". The rest of the summary still displays. |
| C2 | Otherwise → status "ok" and the 52 weekly totals, oldest first. |
| C3 | An empty list (a brand-new repository) → status "ok" with no bars and the note "No commits in the last year". |

## 3. Acceptance criteria

- [ ] Given a repository with `archived = true`, when I open it, then the status shows "Archived" in red with the explanation, whatever else is true.
- [ ] Given the last commit 10 days ago and a release 2 months ago, when I open it, then the status shows "Active".
- [ ] Given the last commit 8 months ago, when I open it, then the status shows "Quiet".
- [ ] Given a repository with no license, when I open it, then "No license" shows in amber with a one-line explanation.
- [ ] Given one contributor made 90% of last year's commits, when I open it, then the single-maintainer flag shows, naming that person's account.
- [ ] Given `/stats/commit_activity` is still computing, when I open the page, then the chart shows "GitHub is still calculating this, check back in a minute" and every other field displays.
- [ ] Given a repository with no releases but recent tags, when I open it, then "Last release" shows the latest tag with the note "tag, not a formal release".
- [ ] Given any field, when I hover the info icon, then I see its source and fetch time (F6).

## 4. Edge cases

- **Monorepos with 10,000+ commits:** contributor statistics lose line counts; we only use commit counts, so this is fine.
- **Repositories with only bots committing** (for example dependabot): exclude accounts ending in `[bot]` from the single-maintainer calculation.
- **Mirrors:** treat as normal repositories.
- **More than 100 releases a year:** we read only the newest 100 releases, so the 12-month count would show "100+".
- **Busy bot branches:** `pushed_at` also moves when a bot pushes to a side branch, so a dead project with an active bot can look "Active". Known limit, listed in F6.

## 5. Out of scope

- Security advisories (later, to verify).
- Company backing.
- Documentation quality.
- Median time to first issue reply (F9 may explore it).
