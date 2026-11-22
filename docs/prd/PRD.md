# PRD: GitAnalyze

**Version:** 0.1 · **Date:** 2026-11-22 · **Owners:** Yue, Richard Chen

**Conventions:** [HYPOTHESIS] = based on preliminary interview findings, to be validated in user interviews (section 9). [ASSUMPTION] = team assumption without evidence.

---

## 1. Problem

Before adopting an open-source library, tool, or AI skill, people need to know whether it is **alive, maintained, and trustworthy**. The evidence is scattered across many GitHub tabs, and some of it is easy to misread. For example, high stars don't mean a project is alive, and a star spike can be bought. AI skills are newer still: there is almost no history to judge them by, yet they can run code on your machine.

GitAnalyze gathers real GitHub data into one place, explains each number in plain language, and makes the evidence easy to compare and to share with a team.

---

## 2. Personas

**P1: The candidate checker (main persona).** A developer or student with 2–3 named options in mind: a library, a tool, or an AI skill someone sent them. The names come from an AI assistant, a teammate, a forum thread, or a list. They want a quick, trustworthy check of whether each option is alive and safe before they commit. Many don't compare at all today; they take the first suggestion and sometimes get burned when it turns out to be abandoned. [HYPOTHESIS]

**P2: The team justifier.** A tech lead, product manager, or analyst who must recommend a tool to a team or defend a choice to a manager or client. They need a clear comparison and plain explanations they can paste into a slide, document, or report. They are often not GitHub experts themselves; words like "fork" or "release" may need explaining. [HYPOTHESIS]

*Secondary (from the proposal, served by the ranking features): an explorer who wants to see what is gaining attention in an area, especially AI tools and skills.*

---

## 3. Jobs to be done

Format: *When [situation], I want to [motivation], so I can [outcome].*

| Id | Job | Persona | Proposal stories | Priority |
|---|---|---|---|---|
| **J1** | When I already have a few candidate tools or skills in mind, I want to check whether each one is alive and maintained, so I can pick one without getting burned later. | P1 | 5, 6 | **Primary** |
| **J2** | When someone sends me an AI skill or tool, I want to see what AI capabilities it has and signals of whether it's safe to install, so I can decide whether to trust it. | P1 | 6 | **Primary** |
| **J3** | When I have to recommend or defend a choice, I want a side-by-side comparison with plain explanations I can export, so my team or manager can follow my reasoning. | P2 | 7, 8 | Secondary |
| **J4** | When I want to know what's new in an area, I want to see the top projects and those gaining attention fastest, so I can spot options I didn't know about. | Explorer | 1, 2, 3, 4 | Secondary |
| *J5* | *When a project my team already depends on starts going quiet, I want to be told, so we can plan a switch before it breaks.* | P2 | *(new, not in proposal)* | *Candidate only: add if 2+ interviewees describe this pain* [HYPOTHESIS] |

---

## 4. Features

Priority uses MoSCoW: **Must**, **Should**, **Could**, **Won't**.

| Id | Feature | Jobs | Proposal stories | Priority | Size | PRD |
|---|---|---|---|---|---|---|
| **F0** | GitHub data foundation: API client, database, daily job, watch list | all | (enables all) | **Must** | L | `F0-github-data-foundation.md` |
| **F1** | Repository lookup: paste links or search by name, 1–3 at once | J1 | 5 | **Must** | S | `F1-repository-lookup.md` |
| **F2** | Repository health summary: activity, releases, maintainers, license, archived status | J1 | 6 | **Must** | M | `F2-health-summary.md` |
| **F3** | Star history chart | J1, J4 | 6, 4 | **Must** | M | `F3-star-history.md` |
| **F4** | AI capabilities and trust signals | J2 | 6 | **Must** | M | `F4-ai-capabilities.md` |
| **F6** | Metric source, method, and plain-language explanations | J3 | 8 | **Must** (data) / **Should** (glossary page) | S | `F6-metric-provenance.md` |
| **F5** | Side-by-side comparison and export | J3 | 7 | **Should** | M | `F5-compare-and-export.md` |
| **F7** | Top repositories: browse, filter, result limit, keep scrolling | J4 | 1, 3 | **Should** | M | `F7-top-repositories.md` |
| **F8** | Stars-gained ranking and GitHub Trending | J4 | 2, 4 | **Should** | M | `F8-stars-gained-ranking.md` |
| **F9** | Issue and pull request trends | J1 | 6 | **Should** (later sprint) | M | `F9-issue-pr-trends.md` |
| — | Dependency watch alerts (J5) | J5 | — | **Won't for now**; revisit after user interviews | — | — |

### Proposal story coverage

| Story | Feature(s) | Note |
|---|---|---|
| 1 | F7 | |
| 2 | F8 | |
| 3 | F7 | |
| 4 | F8, F3 | Week, month, year only |
| 5 | F1 | |
| 6 | F2, F3, F4, F9 | |
| 7 | F5 | |
| 8 | F6 | |

---

## 5. Build order

[ASSUMPTION: 1-week sprints.]

| Sprint | Goal | Features | Done when |
|---|---|---|---|
| **0** | Foundation | Repo setup, CLAUDE.md, CI, empty app deployed; F0 client + database schema | A test calls a mocked GitHub response through the client and saves it |
| **1** | "Check one repository" | F1, F2, F6 (data fields) | Paste a link → see a health summary with source and date on every number |
| **2** | "History and AI" | F3, F4 | Star history chart and AI capability panel work on any public repository |
| **3** | "Compare and browse" | F5, F7, F0 daily job | Compare 2–3 repositories and export; browse top repositories with filters |
| **4** | "Trending and polish" | F8, F6 glossary page, F9 | Stars-gained ranking + Trending; issue and pull request trends tested on large repositories |

---

## 6. Non-goals

- **No "how many people use it" number.** GitHub has no usage data. We show adoption signals we do have (forks, contributors). Package downloads (npm or PyPI) are a possible later add-on.
- **No quality score or ranking for AI skills.** We show trust signals, never a verdict.
- **No real-time data.** Rankings refresh daily; a looked-up repository is fetched on demand.
- **No 5- or 10-year ranking windows.**
- **No search of all of GitHub for AI skills.** AI capabilities are checked per repository.
- **No company-backing, security-advisory, paid-support, or documentation-quality judgments.** These are outside GitHub data; we say so in F6.
- **No scraping of github.com pages.** We read GitHub Trending only through the GitHubTrendingRSS feed, pending team OK.
- **No use of the restricted stargazer list endpoint, or of GH Archive, BigQuery, ClickHouse, or OSS Insight star data.** See F0.

---

## 7. Technical goals

- **Stack [ASSUMPTION]:** Django with Django REST Framework, PostgreSQL, TypeScript frontend (framework to be decided).
- **Deployed** and reachable by URL by the end of Sprint 0 (empty app first).
- **Responsive** layout; meets WCAG AA contrast and keyboard navigation.
- **Tests:** every acceptance criterion becomes a test. GitHub responses are recorded fixtures; CI never calls the live GitHub API.
- **Secrets:** the GitHub token lives in an environment variable, never in the repository.
- **Request budget:** stay within 5,000 GitHub requests per hour per token (details in F0).

---

## 8. Open questions for the team

1. Downloads: drop, add later for packaged repositories, or show adoption signals only?
2. Does the four-level AI capability rule (F4) meet the team's definition of an AI tool?
3. PostgreSQL confirmed?
4. Where do the database and daily job run (cron or Celery)?
5. Watch list size (1,000 or 3,000), and OK to use the GitHubTrendingRSS feed?

---

## 9. Validation plan

| Check | If confirmed | If not |
|---|---|---|
| Did real people start from names they already had, or from a ranking? | Keep J1 first | Move F7/F8 earlier |
| Did they copy comparisons into slides, docs, or reports? | Keep F5 export as Should | Drop export to Could |
| How did they learn the last time a dependency died? | 2+ "by accident" → consider J5 (watch alerts; also gives user accounts a real purpose) | Keep J5 out |
| When asked "is it widely used?", what satisfied the asker? | Numbers → consider downloads | Logos or names → adoption signals only |
| Before installing their last skill, what did they look at? | Publisher → make publisher prominent in F4 | Nothing → consider a stronger warning when a skill contains scripts |
