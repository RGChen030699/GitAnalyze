# F5: Side-by-Side Comparison and Export

**Priority:** Should · **Size:** M · **Sprint:** 3 · **Job:** J3 · **Proposal story:** 7

## 1. User story

As someone comparing options, I want to view repository metrics side by side and export them, so that I can compare projects with the same measures and show my reasoning to others.

## 2. Requirements

| # | Requirement |
|---|---|
| X1 | Opened from F1 (2–3 links) or by adding repositories to a comparison from any repository page ("Add to compare"). Maximum 3. |
| X2 | Table columns are repositories; rows are the metrics below. The best value in each row gets a subtle highlight; no overall winner is declared. |
| X3 | Overlaid star history chart (F3, H6). |
| X4 | **Export:** copy the table as Markdown, download CSV, download the chart as PNG. |
| X5 | Every export includes a footer: "Source: GitHub API via GitAnalyze · Data fetched <date> · Definitions: <link to F6 page>". |
| X6 | The URL `/compare?repos=a/b,c/d` reproduces the comparison, so it can be shared. |
| X7 | Remove a repository from the comparison with one click; the URL updates. |

### Rows

| Group | Row | From |
|---|---|---|
| Health | Status label · last commit · last release · releases in last 12 months · archived · license · publisher type · contributors · single-maintainer flag | F2 |
| Popularity | Total stars · stars gained in last 30 days · forks | F2, F3 |
| Fair comparison | Average stars per month since creation · releases per year · age | Computed |
| AI | Number of skills · agent setup (yes/no) · MCP server (yes/no) | F4 |
| Later | Issues opened vs closed (last 12 months) · pull requests merged | F9 |

## 3. Acceptance criteria

- [ ] Given I paste two repository links in F1, when the page loads, then I see a two-column table with every row above filled or marked "not available".
- [ ] Given three repositories, when I try to add a fourth, then I see "Compare up to 3 repositories at a time".
- [ ] Given a comparison, when I click "Copy as table", then the clipboard holds a Markdown table that includes the source and date footer.
- [ ] Given a comparison, when I click "Download CSV", then the file has one column per repository and one row per metric, with the footer as a final row.
- [ ] Given a comparison, when I click "Download chart", then a PNG of the overlaid star history downloads with a legend and the source line.
- [ ] Given I open `/compare?repos=vercel/next.js,remix-run/remix` in a new browser, then I see the same comparison.
- [ ] Given a repository 1 year old with 12,000 stars and one 10 years old with 30,000, when I view "Average stars per month", then it shows 1,000 and 250.
- [ ] Given a metric is pending (statistics still computing), when I export, then the cell says "pending" rather than 0.

## 4. Edge cases

- **Comparing a repository with itself:** remove the duplicate silently.
- **One repository fails to load:** show the other columns, plus a retry button in the failed column.

## 5. Out of scope

- Comparing more than 3 at once.
- Weighted scores or a recommended pick.
