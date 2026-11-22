# F6: Metric Source, Method, and Plain-Language Explanations

**Priority:** Must (data on every metric, info icons) / Should (glossary and limits page) · **Size:** S · **Sprints:** 1 (data), 4 (page) · **Job:** J3 · **Proposal story:** 8

## 1. User story

As someone interpreting a metric or AI finding, I want to see its source, how it was identified or calculated, and when it was last updated, explained in plain language, so that I can understand the result and its limits and explain it to others.

## 2. Requirements

| # | Requirement |
|---|---|
| P1 | Every stored value has `source`, `method_key` and `fetched_at` (F0, C8). This is a data rule, enforced in Sprint 1. |
| P2 | Every displayed metric has an info icon. Clicking it shows: what it means (one sentence), how it's calculated, the source endpoint, last updated, and what it can't tell you. |
| P3 | Each page shows "Data last updated <time>" for the repository, or "Rankings updated <time>" for lists. |
| P4 | A **metric dictionary** at `/about/metrics`, generated from one definitions file (for example `metrics.yaml`) that P2 also uses, so the two never disagree. |
| P5 | A **glossary** at `/about/terms`: star, fork, release, tag, issue, pull request, contributor, archived, license, maintainer, AI skill, MCP server, agent setup file. |
| P6 | A **known limits** section on `/about/metrics` (list below). |
| P7 | AI findings show the rule that matched and the file path (F4). |

### Definitions file format (example)

```yaml
stars_gained_30d:
  label: Stars gained in the last 30 days
  means: How many people starred the repository in the last 30 days, minus those who later removed their star.
  method: Sum of daily counts from GitHub's star history for the last 30 days.
  source: GET /repos/{owner}/{repo}/stargazers/history
  cannot_tell_you: Whether people use it, or whether the stars are genuine.
```

### Known limits (shown to users)

1. **Stars are not usage.** GitHub has no data on how many people use a project.
2. **Net stars.** Removed stars disappear from past weeks too, so history can shift slightly.
3. **Rankings cover our watch list:** top repositories by stars, GitHub Trending, AI topics, and repositories users have looked up. Not every repository on GitHub.
4. **Contributor details** cover the top 100 contributors only.
5. **AI capabilities** are found by file rules; a skill in a non-standard format may be missed. We do not judge quality.
6. **Updated daily**, not in real time.
7. **Not covered:** company backing, security advisories, paid support, documentation quality.

## 3. Acceptance criteria

- [ ] Given any metric on a repository page, when I click its info icon, then I see meaning, method, source, last updated, and what it can't tell you.
- [ ] Given `metrics.yaml` changes, when the site rebuilds, then both the info popups and `/about/metrics` show the new text.
- [ ] Given a metric stored without `source` or `fetched_at`, when the save is attempted, then a test fails (data rule).
- [ ] Given the word "fork" in the compare table, when I hover it, then I see the glossary definition.
- [ ] Given the rankings page, when it loads, then it shows "Rankings updated <time>" and a link to the watch list explanation.
- [ ] Given a screen reader, when it reaches an info icon, then it announces "About <metric name>".

## 4. Out of scope

- Translating the site into other languages.
