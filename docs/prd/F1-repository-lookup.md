# F1: Repository Lookup

**Priority:** Must · **Size:** S · **Sprint:** 1 · **Job:** J1 · **Proposal story:** 5

## 1. User story

As someone with candidate tools in mind, I want to paste one or more repository links or search by name, so that I can review those projects directly.

## 2. Requirements

| # | Requirement |
|---|---|
| L1 | One input box on the home page accepts any of: `https://github.com/owner/repo`, the same with extra path (`/tree/main/...`, `/issues/12`), `github.com/owner/repo`, `owner/repo`, `https://github.com/owner/repo.git`, `git@github.com:owner/repo.git`. |
| L2 | Accepts **up to 3** entries, separated by spaces, commas, or new lines. One entry opens the repository page; two or three open the comparison page (F5). |
| L3 | Text that is not a link or `owner/repo` is treated as a name search: `GET /search/repositories?q=<text> in:name&sort=stars&per_page=5`, shown as suggestions with stars and description. |
| L4 | If the repository is in the database and was fetched less than 24 hours ago, show it immediately. Otherwise run the F0 on-demand fetch and show a loading state that names each step ("Reading releases…"). |
| L5 | Show sections as soon as their data arrives; don't wait for the slowest one (statistics can take several retries). |
| L6 | Every looked-up repository joins the watch list (F0, W4). |
| L7 | Repository pages have stable URLs: `/repo/{owner}/{name}`. Comparison pages: `/compare?repos=a/b,c/d`. |

## 3. Acceptance criteria

- [ ] Given I paste `https://github.com/anthropics/skills/tree/main/skills`, when I submit, then I land on `/repo/anthropics/skills`.
- [ ] Given I paste `git@github.com:vercel/next.js.git`, when I submit, then I land on `/repo/vercel/next.js`.
- [ ] Given I paste two links, when I submit, then I land on `/compare` with both repositories.
- [ ] Given I paste four links, when I submit, then I see "Compare up to 3 repositories at a time" and nothing is fetched.
- [ ] Given I type `zustand`, when I pause typing, then I see up to 5 suggestions with stars and descriptions.
- [ ] Given a repository that doesn't exist or is private, when I submit, then I see "We couldn't find a public repository at owner/name" and no error page.
- [ ] Given a repository fetched 2 hours ago, when I open it, then it loads from the database without calling GitHub, and shows "Last updated 2 hours ago".
- [ ] Given a renamed repository, when I paste its old name, then I land on the new name's page.

## 4. Edge cases

- **Forks:** show a "This is a fork of X" link.
- **Archived:** load normally; F2 shows the archived badge.
- **Very large repositories:** the first fetch may take 10+ seconds; keep the step-by-step loading text.
- **GitHub rate limit reached:** show cached data if we have it, otherwise "GitHub is busy, try again in N minutes" with the reset time.

## 5. Open questions

- A "Refresh now" button for a single repository.
