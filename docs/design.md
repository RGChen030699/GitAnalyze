# GitAnalyze — Design Specification

**Version:** 1.0 · **Date:** 2026-11-22 · **Status:** Matches the working demo
**Companion to:** `PRD.md`, `F0`–`F9` feature PRDs
**Reference builds:** working demo (published artifact) and the wireframe canvas

This document describes how GitAnalyze looks, behaves and reads. It is the source of truth for the frontend build. When this file and the demo disagree, fix whichever is wrong and update the other.

---

## Contents

1. Design direction
2. Principles
3. Design tokens
4. Typography
5. Layout and spacing
6. Iconography and status language
7. Components
8. Screens
9. States: loading, empty, error, pending
10. Data visualization
11. Interaction and motion
12. Content and voice
13. Accessibility
14. Responsive behaviour
15. Feature coverage map
16. Implementation notes
17. Open design questions

---

## 1. Design direction

**Concept: the inspection report.**

People come to GitAnalyze with one question: *is this repository alive, maintained and safe to depend on?* The design answers that question first and puts evidence underneath. Every repository page opens on a **verdict band**: a large status word, one sentence that says how many things need attention, and a short checklist marked pass, caution or stop.

The verdict band is the one bold element in the product. Everything around it is quiet, flat and scannable, so the verdict reads instantly and the evidence feels like a reliable appendix rather than a dashboard.

**What we deliberately avoid**

| Avoided default | Why | What we do instead |
|---|---|---|
| Score out of 100, star ratings, "safe" badges | PRD non-goal; implies a judgment we can't make | Pass / caution / stop checks with the rule shown |
| A grid of identical stat cards | Hides what matters; every number looks equally important | A definition list of facts, with warnings coloured in place |
| Cream background, serif display, clay accent | Common generated look; wrong tone for a developer tool | Cool stone ground, cobalt accent, grotesque display |
| Dark background with neon accent | Reads as "hacker aesthetic", lowers trust for team leads (P2) | Light by default, carefully tuned dark theme |
| Gradients, glass, decorative shadows | Decoration without information | Flat surfaces; one soft shadow reserved for floating layers and the verdict |

---

## 2. Principles

1. **Answer first, evidence second.** Every page leads with the conclusion a person came for, then the supporting detail.
2. **Show the rule, never a verdict we can't defend.** Each status and check links to how it was worked out (F6).
3. **One accent, used only for action.** Cobalt means "you can click this" or "this is selected". It never decorates.
4. **Colour never works alone.** Every status pairs colour with an icon and a word.
5. **Plain language beats jargon.** "Mostly one person" instead of "bus factor"; "Open issues and pull requests" because GitHub counts them together.
6. **Never show a fake zero.** Unknown, pending or not-yet-created values say so in words.
7. **Fast to scan, slow to mislead.** Large type for the answer, small but readable type for caveats, and caveats always visible rather than hidden behind hover.

---

## 3. Design tokens

All colours are CSS custom properties on `:root`. Dark values apply under `@media (prefers-color-scheme: dark)` (guarded by `:root:not([data-theme="light"])`) and under `:root[data-theme="dark"]`, so the user toggle overrides the system setting.

### 3.1 Colour — neutrals

| Token | Light | Dark | Use |
|---|---|---|---|
| `--bg` | `#F3F4F0` | `#121512` | Page background ("stone") |
| `--surface` | `#FFFFFF` | `#1A1E1A` | Panels, header, popovers |
| `--surface-2` | `#ECEEE8` | `#232823` | Chips, segmented track, hover fill |
| `--line` | `#D8DBD2` | `#343A33` | Panel borders, section dividers |
| `--line-2` | `#E6E8E1` | `#2A2F2A` | Row dividers inside panels, chart gridlines |
| `--ink` | `#181C18` | `#ECEEE9` | Primary text |
| `--ink-2` | `#454B44` | `#BCC2B9` | Secondary text, labels |
| `--ink-3` | `#5E645C` | `#9DA49A` | Notes, captions, axis labels |

### 3.2 Colour — accent

| Token | Light | Dark | Use |
|---|---|---|---|
| `--accent` | `#3446D9` | `#8D9CFF` | Primary buttons, focus ring, selected tab underline |
| `--accent-ink` | `#FFFFFF` | `#0F1433` | Text on `--accent` |
| `--accent-soft` | `#E3E6FB` | `#262C55` | Parsed-entry chips, best-value cells, hover rows |
| `--accent-text` | `#2A38B0` | `#B3BCFF` | Links and accent text on light surfaces |

### 3.3 Colour — status

Each status has a strong tone (icons, text) and a soft tone (backgrounds). Pairs are tuned so strong-on-soft passes 4.5:1.

| Status | Strong (light / dark) | Soft (light / dark) | Meaning |
|---|---|---|---|
| Good | `#1D7550` / `#62CB98` | `#DCEFE4` / `#173628` | Pass |
| Warn | `#955200` / `#F1AD52` | `#FAEAD2` / `#3B2B13` | Caution, look before you adopt |
| Bad | `#AE3127` / `#F2867B` | `#F8E0DC` / `#3F1E1B` | Stop, a serious problem |
| Neutral | `--ink-2` | `--surface-2` | No signal either way (e.g. Quiet) |

### 3.4 Colour — data series

Used for chart lines and bars. The three differ in lightness as well as hue, and comparison lines also differ in dash pattern.

| Token | Light | Dark | Dash (compare) |
|---|---|---|---|
| `--c1` | `#3446D9` | `#8D9CFF` | Solid |
| `--c2` | `#D07A1F` | `#F1AD52` | `9 6` (dashed) |
| `--c3` | `#5B615A` | `#BCC2B9` | `2 6` (dotted) |

Two-series charts (issues opened vs closed) use `--c1` and `--c2` only.

### 3.5 Elevation

| Token | Value | Use |
|---|---|---|
| `--shadow` (light) | `0 1px 2px rgba(24,28,24,.06), 0 8px 24px rgba(24,28,24,.06)` | Verdict band, lookup box, popovers, suggestions, demo panel |
| `--shadow` (dark) | `0 1px 2px rgba(0,0,0,.3), 0 8px 24px rgba(0,0,0,.25)` | Same |
| Tray shadow | `0 10px 30px rgba(0,0,0,.25)` | Floating compare tray only |

Ordinary panels have a 1px border and **no** shadow.

### 3.6 Radius (by hierarchy, not one value everywhere)

| Element | Radius |
|---|---|
| Verdict band | 20px |
| Lookup box, modal | 18px |
| Tray | 16px |
| Panels, popovers, suggestions | 14px |
| Segmented track | 12px |
| Buttons, inputs, selects, tabs' items | 10px |
| Segmented items | 9px |
| Small icon buttons, info buttons | 8px |
| Confidence tags | 6px |
| Chips, counts | 999px (pill) |
| Bars in charts | 2px top corners |

### 3.7 Z-index scale

| Layer | z-index |
|---|---|
| Sticky report tabs | 5 |
| Safe-area cover (`body::before`) | 10 |
| Header | 20 |
| Tray, suggestions | 30 |
| Demo panel | 40 |
| Popover | 60 |
| Toast | 70 |
| Modal | 80 |

---

## 4. Typography

### 4.1 Families

| Role | Family | Weights | Notes |
|---|---|---|---|
| Display | **Bricolage Grotesque** (optical size 12–96) | 500, 650, 750 | Headlines, status word, numbers in summaries. Carries the personality. |
| Text | **IBM Plex Sans** | 400, 500, 600 | Body, UI, tables. `font-variant-numeric: tabular-nums` site-wide. |
| Code | **IBM Plex Mono** | 400, 500 | Only for things that *are* code: `owner/repo`, file paths, endpoints, exported Markdown. Never for ordinary labels. |

Fallback stacks: `'IBM Plex Sans', system-ui, -apple-system, 'Segoe UI', sans-serif` and `ui-monospace, SFMono-Regular, Menlo, monospace`.

### 4.2 Scale

| Style | Family | Size | Weight | Line height | Tracking | Used for |
|---|---|---|---|---|---|---|
| Hero | Display | `clamp(40px, 6.4vw, 76px)` | 750 | 1.02 | −0.025em | Home headline (max 15ch) |
| Verdict word | Display | `clamp(48px, 6vw, 68px)` | 750 | 1.0 | −0.03em | "Active", "Slowing"… |
| Page title | Display | `clamp(32px, 4.4vw, 48px)` | 750 | 1.02 | −0.025em | Compare, Explore, How it works |
| Repo title | Display | `clamp(28px, 4vw, 40px)` | 650 | 1.1 | −0.015em | `owner / name` (owner in `--ink-3`, weight 500) |
| H2 | Display | 24px (20px in compact panels) | 650 | 1.2 | −0.01em | Section titles |
| Summary number | Display | 22px | 650 | — | — | "+310 in the last 7 days" |
| H3 | Text | 17px | 600 | 1.4 | 0 | Sub-sections, skill counts |
| Lead | Text | 19px (17px on Compare) | 400 | 1.55 | 0 | Intro paragraphs, max 62ch |
| Body | Text | 16px | 400 | 1.55 | 0 | Default |
| UI | Text | 15px | 500 | — | 0 | Tabs, selects, nav |
| Small | Text | 14px | 400 | 1.5 | 0 | Descriptions, check details |
| Note | Text | 13px | 400 | 1.5 | 0 | Captions, sources, footers |
| Micro | Text | 12px / 11px | 400–600 | — | 0 | Axis labels, chip tags, month labels |

### 4.3 Rules

- Sentence case everywhere. No all-caps labels, no eyebrow labels above headings.
- No single-word emphasis inside headlines.
- Line length under 80 characters for prose.
- Typographic punctuation in UI copy: ’ “ ” and the en dash for ranges. Straight quotes only in code.

---

## 5. Layout and spacing

### 5.1 Grid

- Content container `.wrap`: `max-width: 1180px`, `padding: 0 24px`, centred.
- Content is **left-aligned** throughout, including the hero. Nothing is centred except empty and error states.
- Main area padding: 36px top, 72px bottom. Footer bottom padding 90px so the tray never covers content.

### 5.2 Spacing scale

Base unit 4px. Common steps: 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 36, 40, 48, 56, 72.

| Context | Value |
|---|---|
| Gap between panels on a page | 20–22px |
| Panel inner padding | 22px 24px (verdict status area 28px 30px) |
| Gap between home sections | 56px |
| Row height in lists and fact tables | min 44–56px |
| Chip padding | 3px 10px |
| Button height | 44px (36px small, 56px in lookup) |

### 5.3 Page skeleton

```
┌──────────────────────────────────────────────────────────────┐
│ Header (sticky, 64px): logo · nav · Demo · theme             │
├──────────────────────────────────────────────────────────────┤
│ main .wrap (max 1180, left aligned)                          │
│   page content                                                │
├──────────────────────────────────────────────────────────────┤
│ Footer: data note · source · definitions link                │
└──────────────────────────────────────────────────────────────┘
                    [ Compare tray, floating, bottom centre ]
```

---

## 6. Iconography and status language

### 6.1 Icon style

- 24×24 viewBox, stroke icons, `stroke-width` 2–2.4, round caps and joins, `currentColor`.
- Rendered at 16–18px in UI, 30px in the verdict status tile.
- Decorative icons get `aria-hidden="true"`; icon-only buttons carry `aria-label`.
- No emoji in the interface.

### 6.2 Status mapping (single source)

| Status | Tone | Icon | Word |
|---|---|---|---|
| Active | Good | Check | "Active" |
| Slowing | Warn | Triangle with ! | "Slowing" |
| Quiet | Neutral | Minus | "Quiet" |
| Archived | Bad | X | "Archived" |
| Pending (any metric) | Neutral | Clock | "Pending" |

The status rule itself (from F2) is:

| Status | Rule |
|---|---|
| Archived | `archived = true` (wins over everything) |
| Active | Commit within 30 days **and** (release within 182 days **or** no releases ever) |
| Slowing | Commit within 182 days, but not Active |
| Quiet | No commit within 182 days, or none at all |

### 6.3 Verdict checks

The verdict band shows four or five checks, always in this order.

| # | Check | Pass | Caution | Stop |
|---|---|---|---|---|
| 1 | Maintenance | "Actively maintained" (Active) | "Maintenance is slowing" (Slowing) | "No recent work" (Quiet) or "Archived by its owner" |
| 2 | Maintainers | "Shared maintenance" | "Mostly one person" (≥ 80% of last-year commits by one non-bot account) | — |
| 3 | License | "MIT license" (any SPDX id) | "Custom or unrecognized license" (`NOASSERTION`) | "No license" |
| 4 | Star pattern | "Steady interest" | "Unusual star spike" (F8 G7 rule) | — (neutral "No new attention" when gain ≤ 0) |
| 5 | Scripts in skills (only if skills exist) | — | "N of M skills run scripts" | — |

Pending statistics replace check 2 with a neutral clock: "Maintainer check pending".

**Verdict sentence**, based on the count of caution + stop checks:
- 0 → "Nothing stood out. The usual signals look healthy."
- 1 → "1 thing to look at before you adopt it."
- n → "n things to look at before you adopt it."

Below the sentence: "We show evidence, never a score. Each check links to how it’s worked out."

---

## 7. Components

Each component lists anatomy, variants, states and rules.

### 7.1 Header

- Sticky, `--surface` background, 1px bottom border, min-height 64px.
- Anatomy: logo (28px cobalt rounded square with a check, wordmark in Display 750 21px) · nav (Check, Explore, Compare + count badge, How it works) · Demo menu · theme toggle.
- Nav items: 44px tall, 10px radius, `--ink-2`; hover `--surface-2`; current page uses `aria-current="page"` with `--surface-2` fill and `--ink` text.
- Compare count badge: cobalt pill, appears only when the compare list has items.
- A `body::before` strip in `--surface` covers the top safe-area inset on phones.

### 7.2 Buttons

| Variant | Look | Use |
|---|---|---|
| Primary | `--accent` fill, `--accent-ink` text, 600 weight | One per view: Check, Add to compare, Try another |
| Secondary | `--surface` fill, `--line` border | Exports, GitHub link, Reset |
| Ghost | Transparent, `--ink-2` | Low-emphasis actions (Copy link) |
| Small | 36px tall, 14px text | Inside tray, table headers |
| Icon | 44×44 (36×36 for info buttons) | Theme, remove, info |

States: hover (primary brightens 8%, secondary border darkens to `--ink-3`), focus (3px `--accent` ring, 2px offset), disabled (55% opacity, `not-allowed` cursor). Labels are verbs that say what happens and stay the same through the flow ("Add to compare" → toast "Added … to compare").

### 7.3 Lookup box

- Container: `--surface`, 2px `--line` border, 18px radius, shadow; border turns `--accent` on focus-within.
- Textarea: Plex Mono 16px, auto-grows from 1 line to 160px, no visible border.
- Button: primary, 56px tall. Label changes with input: **Check** (one repo) → **Compare 2 / Compare 3** → **Search** (free text). Disabled when empty or more than 3 entries.
- Below: "We read this as" + accent chips showing each normalized `owner/repo`.
- Warning (more than 3): warn alert "Compare up to 3 repositories at a time." Nothing is fetched.
- Suggestions: dropdown panel after a 220ms pause, header "Top matches by stars", up to 5 rows (name in mono accent, description, stars). Arrow keys move the highlight, Enter opens. No match: "No public repositories match “x”. Try a different name, or paste a link."
- "Try" row: pill buttons that fill the box with an example (one link, compare two, search, archived project, suspicious spike).

### 7.4 Chips and tags

| Variant | Colours | Use |
|---|---|---|
| Default | `--surface-2` / `--ink-2` | Publisher, language, age |
| Accent | `--accent-soft` / `--accent-text` | AI capabilities, parsed entries |
| Warn | `--warn-soft` / `--warn` | Trending, prerelease, scripts |
| Good / Bad | soft / strong | Format checks, status in lists |
| Confidence tag | 6px radius, 12px 600 | High / Medium / Low in AI panel |

### 7.5 Segmented control

- Track `--surface-2`, 12px radius, 3px padding; items 38px tall, 9px radius.
- Selected item: `--surface` fill, `--ink` text, tiny shadow, `aria-pressed="true"`.
- Used for star range (1 month / 1 year / All), chart type (Total / Gained), time window (This week / This month / This year), result limit (10 / 25 / 50 / 100).

### 7.6 Select and toggle

- Select: 44px, 10px radius, `--line` border, custom chevron drawn with CSS gradients, always paired with a visible label above.
- Toggle: native checkbox 20px with `accent-color: --accent`, label text to the right, whole row clickable, 44px tall.

### 7.7 Tabs (report sections)

- Underline tabs, 50px tall, 600 weight, 3px `--accent` underline on the selected tab.
- Full ARIA tab pattern: `role="tablist"`, `role="tab"`, `aria-selected`, roving `tabindex`, Left/Right arrows move between tabs.
- Sticky under the header on wide screens; static below 860px.
- The AI tab shows a count badge when skills exist.

### 7.8 Info button and provenance popover (F6)

- Info button: 36×36, circle-i icon in `--ink-3`, `aria-label="About <metric>"`, `aria-expanded`.
- Popover: 360px max, `--surface`, 14px radius, shadow. Opens below the button, flips above when there is no room, clamps to the viewport.
- Content, always in this order: title · one-sentence meaning · **How** · **Source** (mono endpoint) · **Updated** · **Can’t tell you**.
- Closes on outside click, Escape, or clicking the same button again.
- Text comes from the single definitions object (`metrics.yaml` in production), the same one that generates `/about`.

### 7.9 Verdict band

```
┌────────────────────────────┬──────────────────────────────────────┐
│ Status ⓘ                   │ ✓ Actively maintained            ⓘ  │
│ [✓]  Active                │   Last commit 2 days ago, …          │
│ 1 thing to look at before  │ ✓ Shared maintenance             ⓘ  │
│ you adopt it.              │ ✓ MIT license                    ⓘ  │
│ We show evidence, never a  │ ✓ Steady interest                ⓘ  │
│ score…                     │ ! 3 of 6 skills run scripts      ⓘ  │
├────────────────────────────┴──────────────────────────────────────┤
│ Commits, last 52 weeks  ╱╲__╱╲╱‾‾╲__╱‾‾╲╱╲_____________________   │
└───────────────────────────────────────────────────────────────────┘
```

- Two columns at 5fr / 7fr; stacks below 860px.
- Status tile: 56px rounded square in the status soft colour with a 30px icon, followed by the status word in the strong colour.
- Each check row: 28px circular mark (soft background, strong icon) · title (600) · info button · detail line (14px, `--ink-2`).
- Pulse strip: polyline of 52 weekly commit totals in the status tone, baseline in `--line`. When statistics are pending it shows "GitHub is still calculating this. Check back in a minute."

### 7.10 Fact list

- A `<dl>` in a responsive grid (columns of min 260px), not cards.
- Row: label (14px `--ink-2`) · value (600, right-aligned, optional small grey sub-line) · info button.
- Warnings colour the value in place (e.g. "No license" in `--warn` with "Others may not legally reuse this code." underneath).

### 7.11 Tables

**Comparison table**
- Sticky header row and sticky first column; horizontal scroll inside the panel below 720px.
- Group header rows (Health, Popularity, Fair comparison, AI, Issues and pull requests) in Display 650 16px.
- Column header: line-style legend (solid / dashed / dotted) · repo name link · remove button.
- Best value per numeric row: `--accent-soft` fill, `--accent-text`, 600. No highlight when all values tie. Never an overall winner.
- Warning values (no license, single maintainer, archived) in `--warn`, 600.
- "Pending" shown as text, never 0.

**Skill table (AI tab)**
- Columns: Skill (mono name, folder path, duplicate paths, "listed in plugin manifest") · What it does · Scripts (warn chip with count and file list, or "None") · Format (good chip "Follows the standard" or warn chip "Partly" + reason).

### 7.12 Lists (Explore rows)

Columns on wide screens: rank · name + status chip + AI / Trending chips + one-line description (+ spike warning) · language · 12-week sparkline · stars gained (window) · total stars · add-to-compare button. Collapses to rank · details · add button below 900px. Negative gains show in `--bad` with a minus sign.

### 7.13 Compare tray

- Floating pill-shaped bar, bottom centre, `--ink` background with `--bg` text.
- Contains: "Compare" label · one chip per repo with a remove × · primary action ("Compare 2", or "Add one more to compare" with a single repo).
- Hidden on the Compare page and when empty. Respects the bottom safe-area inset.
- Adding a fourth repo anywhere shows the toast "Compare up to 3 repositories at a time."

### 7.14 Toast

- Bottom centre above the tray, `--ink` / `--bg`, 12px radius, `role="status"`.
- Slides up 12px and fades in over 200ms, disappears after 3.2s.
- Copy confirms the action in the same words as the button ("Copied a Markdown table with the source and date.").

### 7.15 Modal

- Used only as a fallback when the clipboard or downloads are blocked: shows the content in a read-only textarea with the text pre-selected.
- 640px max, 18px radius, dimmed backdrop `rgba(10,12,10,.45)`; closes on backdrop click, Close button or Escape.

### 7.16 Progress strip (loading)

- Accent-soft bar with a spinner, the current step in bold ("Reading releases…") and the full step list, finished steps marked with a check.

---

## 8. Screens

### 8.1 Home — Check (F1)

```
Check a repository before you depend on it.            ← Hero, max 15ch
Paste up to three GitHub repositories…                  ← Lead
┌──────────────────────────────────────────────┬───────┐
│ github.com/owner/repo, owner/repo, or a name │ Check │ ← Lookup box
└──────────────────────────────────────────────┴───────┘
We read this as [lumen-labs/agent-kit]
Separate entries with spaces, commas or new lines…
Try (One link) (Compare two) (Search “agent”) (Archived project) (Suspicious spike)

┌ Recently checked ─────────────┐ ┌ Gaining stars this week ─ See all ┐
│ ✓ lumen-labs/agent-kit Active │ │ 1 newwave/hype-agent      +3,000  │
└───────────────────────────────┘ └───────────────────────────────────┘
──────────────────────────────────────────────────────────────────────
Is it maintained?   Is the attention real?   What would I be installing?
```

Behaviour: accepts all F1 input formats; one entry → report, two or three → comparison, free text → suggestions; unknown repository → Not found screen.

### 8.2 Repository report (F2, F3, F4, F6, F9)

```
lumen-labs / agent-kit                      [+ Add to compare] [GitHub ↗]
Agent skills for document work…              Data last updated 2 hours ago
(Organization) (Python) (3 years old) (On GitHub Trending) (AI capabilities)

[ Progress strip — only while loading ]

[ VERDICT BAND — see 7.9 ]

Overview | Star history | AI & trust (6) | Issues & pull requests
──────────────────────────────────────────────────────────────────
```

**Overview tab**: Key facts list (last commit, last release, releases in 12 months, contributors, single maintainer, license, publisher, stars, forks, open issues and pull requests, created), then two panels side by side: Commits per week (52 bars) and Releases (latest six, prereleases tagged; tag-only repositories list tags with "no date on tags").

**Star history tab**: range and chart-type controls; summary line "+N in the last 7 days · +N in the last 30 days · N total" with numbers in Display; spike alert when the G7 rule fires; interactive chart; caption with the net-stars explanation, source and update date.

**AI & trust tab**: trust chips (publisher, repository updated, health status); "Contains N AI skills" with High confidence tag; scripts warning; skill table; collapsible "Possible skills" (Medium); "Other AI signals" panel listing agent setup files (with `.mcp.json` note), MCP server, README mentions (Low, "a hint, not proof"); footer "We never show a quality score or a ‘safe’ label." Repositories with nothing found show "No AI capabilities found by our rules" with a link to the rules.

**Issues & pull requests tab**: summary sentence, two grouped bar charts for 12 months (Issues: opened vs closed; Pull requests: opened vs merged), note "Refreshed weekly from GitHub search counts."

Fork repositories show "This is a fork of X" beneath the description (production; not in demo data). Archived repositories keep the page but the verdict band leads with "Archived".

### 8.3 Compare (F5)

```
Compare                                     [Copy as table] [Download CSV]
Same measures, side by side…                [Download chart] [Copy link]

┌ Metric ─────────────┬ ─── lumen-labs/agent-kit × ┬ - - orbit-ui/skills-pack × ┬ + Add ┐
│ Health              │                             │                           │       │
│ Status          ⓘ   │ ✓ Active                    │ ! Slowing                 │       │
│ …                   │                             │                           │       │
└─────────────────────┴─────────────────────────────┴───────────────────────────┴───────┘
"Pending" means GitHub is still calculating… Source: GitHub API via GitAnalyze…

┌ Star history, overlaid ─────────── legend ┐
│ chart                                       │
└─────────────────────────────────────────────┘
```

- URL `#compare-<id>--<id>` reproduces the view (production: `/compare?repos=a/b,c/d`).
- Fewer than two repositories: empty state "Add one more repository to compare" with one-click suggestions.
- Every export carries the footer "Source: GitHub API via GitAnalyze. Data fetched <date>. Definitions: <link>".

### 8.4 Explore (F7, F8)

```
Explore
Rankings updated today at 04:10 UTC… What we track

All repositories | AI tools & skills | Gaining stars
┌ Language [Any ▾]  Sort by [Most stars ▾]  Time range (week|month|year)
│ Show (10|25|50|100)   ☐ Has AI capabilities   ☑ Hide archived
└──────────────────────────────────────────────────────────────────────
[ On GitHub Trending this week — only on Gaining stars tab ]
┌ Showing 25 of 30                         Stars gained: last 7 days ┐
│ 1  quarry/dataframe-x (Active)  …   Rust  ╱╲╱  +180   48.2k   [+]  │
│ …                                                                  │
│                [ Show 5 more ]  More load automatically as you scroll
│ Rankings cover the N repositories in our watch list…               │
└────────────────────────────────────────────────────────────────────┘
```

- Gaining stars tab forces sort by stars gained and shows the Trending strip with credit "From GitHub Trending" linking to github.com/trending.
- Ties break by `full_name` so order is stable while scrolling.
- No results: "No repositories match these filters" + Reset filters.
- Production: filters persist in the URL (`/explore?tab=ai&lang=python&sort=stars&limit=50`).

### 8.5 How it works (F6)

Left table of contents (sticky on wide screens), then: intro, Known limits (numbered, since order is fixed), Metric dictionary (label + meaning on the left, How / Source / Can’t tell you on the right), Finding AI capabilities (confidence levels), What rankings cover, Glossary (13 terms).

### 8.6 Not found and rate-limited

Centred empty-state panel: 52px warn circle icon, H2 title, one explanatory paragraph, primary + secondary action. See section 9.

---

## 9. States: loading, empty, error, pending

| Situation | Where | What the user sees |
|---|---|---|
| First fetch of a repository | Report | Header info immediately; progress strip with six named steps (Reading repository details → star history → releases → contributors → Scanning files for AI skills → Collecting GitHub statistics); skeleton blocks replaced section by section as data arrives (F1 L5). |
| Cached (< 24 h) | Report | Instant load, "Data last updated 2 hours ago". |
| Statistics still computing (202) | Verdict, Overview, Compare | "GitHub is still calculating this. Check back in a minute." in place of the chart; maintainer check shows a clock and "pending"; Compare cell says "Pending". Rest of the page works. |
| Repository not found or private | Not found screen | "We couldn’t find a public repository at owner/name" + check spelling or privacy; actions: Try another, Browse. No error page. |
| GitHub rate limit, not cached | Report | "GitHub is busy. Try again in 14 minutes." with the reset time; action to open a stored repository. Cached repositories still open. |
| Star history fetch failed (422) | Star tab | Keep stored data, note "Couldn’t refresh star history. Last updated <date>." (production) |
| Zero stars | Star tab | "No stars yet." instead of an empty chart. |
| No commits in a year | Overview | "No commits in the last year." |
| No releases | Overview | "No releases", or latest tag marked "tag, not a formal release". |
| No AI signals | AI tab | "No AI capabilities found by our rules" + link to rules. |
| Partial AI scan (truncated tree) | AI tab | "Partial scan" note (production). |
| Compare with < 2 repos | Compare | Empty state with suggestions. |
| More than 3 repos | Lookup, tray | "Compare up to 3 repositories at a time." |
| Filters return nothing | Explore | "No repositories match these filters" + Reset. |
| Rankings not built yet | Explore | "Rankings are being prepared" (production, new deployment). |
| Trending feed unreachable | Explore | Keep yesterday’s list, "Trending last updated <date>". |
| Clipboard or download blocked | Compare | Modal with the content selected for manual copy. |
| Download declined | Compare | Toast "Download cancelled." |

---

## 10. Data visualization

### 10.1 General rules

- Charts are SVG drawn at the container’s real pixel width (re-drawn on resize) so text never stretches.
- Y axis: 4–5 "nice" ticks (1, 2, 5 × 10ⁿ) labelled with compact numbers (12.4k); gridlines in `--line-2`.
- X axis: 5 date labels; month view uses "Nov 3", longer views use "Nov 2025".
- Cumulative totals start at zero for the All range; 1 month and 1 year start just below the minimum so change is visible.
- Every chart has a text alternative (`role="img"` with an `aria-label` that states the range and total) and a caption with source and update date.

### 10.2 Star history (F3)

| Aspect | Spec |
|---|---|
| Views | Total (line + 10% area fill) or Gained (bars, 70% of slot width) |
| Ranges | 1 month (daily points), 1 year (52 weekly points), All (from creation week) |
| Hover / touch | Dashed vertical cursor, dot on the line, tooltip: date (or "Week of …"), "+N stars that week/day", "N total". Tooltip clamps inside the chart. |
| Keyboard | Chart is focusable; Left/Right step, Home/End jump to ends |
| Negative weeks | Bars below zero, shown as they are |
| Compare overlay | Up to 3 lines (`--c1/c2/c3`, solid/dashed/dotted), shared time axis, one tooltip listing each repo; repos not yet created at that date say "not created yet" |

### 10.3 Other charts

| Chart | Spec |
|---|---|
| Commit pulse (verdict) | 52-point polyline, status tone, no axes, 44px tall |
| Commits per week | 52 bars in `--c1` at 85% opacity, 110px tall, axis labels "<date one year ago>" and "This week"; each bar has a title with its count |
| Issues / PRs | 12 monthly groups of two bars (`--c1`, `--c2`), legend above, month labels below |
| Sparkline (Explore) | 92×28, last 12 weeks of stars gained, `--c1`, no axes |

### 10.4 Exported chart (PNG)

1200×680 at 2× resolution: title "Net star history", legend with line styles and repo names, chart, and the source footer. Background uses the current theme surface.

---

## 11. Interaction and motion

| Interaction | Behaviour |
|---|---|
| Typing in lookup | Live parsing chips; suggestions after 220ms pause |
| Enter in lookup | Opens highlighted suggestion, otherwise submits; Shift+Enter adds a new line |
| Add to compare | Toggles; button becomes "In compare" with a check; tray updates; toast confirms |
| Tabs | Click or arrow keys; focus moves to the selected tab |
| Info button | Opens popover; second click, Escape or outside click closes |
| Explore "Show more" | Loads next page of the chosen size; infinite scroll arms after 600ms to avoid runaway loading; scroll position kept |
| Theme toggle | Switches light/dark, remembered in local storage, charts redraw in new colours |
| Escape | Closes popover, modal, demo panel and suggestions |

**Motion budget** — motion only answers an action or signals waiting:
- Skeleton shimmer 1.3s linear loop; spinner 0.8s rotation.
- Toast 200ms fade and 12px rise.
- Lookup border colour 150ms.
- No entrance animations on sections or cards.
- `prefers-reduced-motion: reduce` disables all animation and transitions.

---

## 12. Content and voice

**Voice:** plain, direct, calm. Speaks like a careful colleague, not a marketer or an alarm.

| Do | Don’t |
|---|---|
| "Mostly one person" | "Bus factor: 1" |
| "Open issues and pull requests" | "Open issues" (GitHub counts both) |
| "Stars are bookmarks, not usage." | Implying stars mean adoption |
| "This skill includes scripts that can run on your computer. Read them before installing." | "Dangerous", "Unsafe", or a safety score |
| "GitHub is still calculating this. Check back in a minute." | "Error" or a blank chart |
| "We couldn’t find a public repository at owner/name" | "Oops! Something went wrong" |

**Rules**
- Sentence case; active voice; no exclamation marks.
- Buttons are verbs naming the result: Check, Compare 3, Add to compare, Copy as table, Download CSV, Reset filters.
- The same action keeps the same name in the button, the toast and the help text.
- Errors say what happened and what to do next; they never apologise.
- Empty states invite an action.
- Every number that could be misread carries its caveat nearby (net stars, combined issue count, tags without dates).

**Fixed strings from the PRDs** (must appear verbatim): "Compare up to 3 repositories at a time", "We couldn’t find a public repository at …", "GitHub is still calculating this…", "Archived by its owner…", "No license: others may not legally reuse this code", "tag, not a formal release", "Unusual spike: lots of new stars but little other activity", "From GitHub Trending", "No AI capabilities found by our rules", "No repositories match these filters".

---

## 13. Accessibility

Target: **WCAG 2.2 AA**.

| Area | Requirement |
|---|---|
| Contrast | Body and small text ≥ 4.5:1 in both themes (including `--ink-3` notes and strong-on-soft status pairs); large text and UI parts ≥ 3:1 |
| Colour independence | Status = icon + word + colour; chart series differ in lightness and dash pattern |
| Keyboard | Everything reachable by Tab; visible 3px focus ring; tabs and charts support arrow keys; Escape closes overlays |
| Targets | Minimum 44×44px for all interactive elements (info buttons 36px with surrounding padding) |
| Semantics | Real `<button>`, `<a href>`, `<label>`, `<select>`, `<table>`, `<dl>`; ARIA tab pattern; `aria-pressed` on toggles and segments; `aria-expanded` on info buttons and the demo menu |
| Announcements | Toasts and lookup status use `aria-live="polite"`; loading strip uses `role="status"`; warnings use `role="alert"` |
| Screen readers | Info buttons announce "About <metric>"; charts have descriptive labels; decorative icons hidden |
| Motion | Respect `prefers-reduced-motion` |
| Zoom | Layout works at 200% zoom and 320px width without horizontal page scroll |

---

## 14. Responsive behaviour

| Breakpoint | Change |
|---|---|
| ≤ 900px | Explore rows collapse to rank · details · add button; language, sparkline and numbers wrap under the name |
| ≤ 860px | Verdict band stacks (status above checks); report tabs stop being sticky; How it works TOC becomes a horizontal row |
| ≤ 720px | Comparison table scrolls horizontally inside its panel with the metric column pinned |
| ≤ 700px | Metric dictionary entries become single-column |
| All sizes | Header nav wraps; panels use `auto-fit` grids (min 240–340px); viewport uses `viewport-fit=cover` with safe-area padding; one-screen layouts avoid `100vh` |

Phones: the tray sits above the home indicator; toasts sit above the tray; touch drag scrubs charts while vertical page scroll still works (`touch-action: pan-y`).

---

## 15. Feature coverage map

| Feature | Where it lives | Key design elements |
|---|---|---|
| F0 Data foundation | Behind the scenes | "Data last updated", "Rankings updated", pending and rate-limit states |
| F1 Lookup | Home, header nav | Lookup box, parsing chips, suggestions, Try row, Not found |
| F2 Health | Report verdict + Overview | Status rule, checks, fact list, commits chart, releases |
| F3 Star history | Report Star history tab, Compare | Interactive chart, ranges, summary line, overlay |
| F4 AI & trust | Report AI tab, Explore AI tab | Confidence levels, skill table, scripts warning, no scores |
| F5 Compare & export | Compare page, tray | Best-value shading, line legend, exports with footer, share link |
| F6 Provenance | Every ⓘ, How it works | Popover anatomy, dictionary, limits, glossary |
| F7 Top repositories | Explore All / AI tabs | Filters, sort, limit, show more + infinite scroll, coverage footer |
| F8 Gaining stars | Explore Gaining tab, Home panel | Time window, Trending strip with credit, Trending chip, spike warning |
| F9 Issues & PRs | Report Issues tab, Compare rows | Grouped monthly bars, 12-month summary |

---

## 16. Implementation notes

- **Tokens:** ship the tables in section 3 as a single `tokens.css` (and optionally `tokens.json` for the TypeScript frontend). Components reference tokens only, never raw hex values.
- **Definitions file:** one `metrics.yaml` drives the info popovers, the dictionary page and the verdict check explanations (F6 P4). The demo’s `M` object mirrors its shape: `label`, `means`, `method`, `source`, `cannot`.
- **Status and checks:** implement `compute_status`, `single_maintainer`, `license_note` and the spike rule on the backend (Django) exactly per F2 rules R1–V4 and F8 G7; the frontend only renders their results and tones.
- **Fonts:** load from Google Fonts with `display=swap`, or self-host the three families for production.
- **Charts:** a small in-house SVG chart module (as in the demo) is enough; if a library is adopted, it must support custom tooltips, keyboard stepping and dash patterns.
- **Routing:** production URLs follow F1 L7: `/repo/{owner}/{name}`, `/compare?repos=a/b,c/d`, `/explore?…`, `/about/metrics`, `/about/terms`. The demo uses hash names only because of its hosting.
- **Exports:** CSV and PNG are generated client-side; every export appends the source footer (F5 X5).
- **Theme:** respect the system setting by default; store an explicit choice; set `color-scheme` so native controls match.
- **Testing:** add visual regression snapshots for the verdict band in each status, both themes, and the 375px and 1280px widths; add axe checks to CI.

---

## 17. Open design questions

1. **Scripts warning strength** (PRD §9): keep the amber caution, or escalate to stop when a skill’s scripts touch the network or file system? Depends on interview findings.
2. **Publisher prominence** (PRD §9): if interviewees check the publisher first, move it into the verdict checklist.
3. **Verdict wording:** test "things to look at" against "things to check" with P2 users who must justify a choice.
4. **Downloads (adoption signal):** if added, where in the verdict? Proposal: a sixth check "Package downloads", only for packaged repositories.
5. **Refresh now:** F1 open question; if added, a ghost button beside "Data last updated", disabled while rate-limited.
6. **J5 watch alerts:** if validated, needs accounts; the compare tray could evolve into a saved "watch list".
7. **Mobile verdict density:** five checks on a 375px screen push the tabs below the fold; consider collapsing passing checks into "3 checks passed" on phones.
