// Pure API-to-page mapping (F7 Step 7). Run: node --test frontend/tests/
'use strict';
const test = require('node:test');
const assert = require('node:assert/strict');
const D = require('../data.js');

const NOW = Date.UTC(2026, 10, 23, 12, 0);
const DAY = 864e5;
const WEEK = 7 * DAY;

test('show gives N/A for null but keeps a real 0', () => {
  assert.equal(D.show(null), 'N/A');
  assert.equal(D.show(undefined), 'N/A');
  assert.equal(D.show(NaN), 'N/A');
  assert.equal(D.show(0), '0');
  assert.equal(D.show(1234, (n) => n.toLocaleString('en-US')), '1,234');
});

test('compareNullable puts null last in both directions', () => {
  assert.deepEqual([3, null, 1, 2].sort((a, b) => D.compareNullable(a, b, 'desc')), [3, 2, 1, null]);
  assert.deepEqual([3, null, 1, 2].sort((a, b) => D.compareNullable(a, b, 'asc')), [1, 2, 3, null]);
});

test('sumKnown ignores null and returns null when every value is null', () => {
  assert.equal(D.sumKnown([1, null, -3]), -2);
  assert.equal(D.sumKnown([null, null]), null);
  assert.equal(D.sumKnown([]), null);
});

test('rankingsQuery maps Rank by, window and filters to API parameters', () => {
  const base = { view: 'stars', win: '7d', lang: 'Any', status: 'any', hideArch: false };
  assert.equal(D.rankingsQuery(base, 1), 'sort=stars&limit=100&page=1');
  assert.equal(D.rankingsQuery({ ...base, view: 'gaining', win: '30d' }, 2), 'sort=gained&window=30d&limit=100&page=2');
  assert.equal(D.rankingsQuery({ ...base, view: 'trending' }, 1), 'sort=trending&trending=1&limit=100&page=1');
  assert.equal(D.rankingsQuery({ ...base, lang: 'Jupyter Notebook', status: 'Active', hideArch: true }, 1),
    'sort=stars&lang=Jupyter+Notebook&status=Active&archived=0&limit=100&page=1');
});

const apiRow = {
  full_name: 'pallets/flask', owner: 'pallets', name: 'flask', description: 'Micro framework', language: 'Python',
  owner_type: 'Organization', stars: 70000, forks: 16000, open_issues: 5, status: 'Active',
  pushed_at: '2026-11-20T12:00:00Z', stars_gained_7d: 12, stars_gained_30d: null, stars_gained_year: 0,
  weeks_12: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], contributors: null, ai: null, spike: null, trending: null,
  source: '/search/repositories', fetched_at: '2026-11-23T04:10:00Z',
};

test('toRow keeps nulls, converts pushed_at to days ago and keeps weeks oldest first', () => {
  const r = D.toRow(apiRow, NOW);
  assert.equal(r.id, 'pallets/flask');
  assert.equal(r.full, 'pallets/flask');
  assert.equal(r.desc, 'Micro framework');
  assert.equal(r.lang, 'Python');
  assert.equal(r.pushed, 3);
  assert.equal(r.gain7, 12);
  assert.equal(r.gain30, null);
  assert.equal(r.gainYear, 0);
  assert.equal(r.contributors, null);
  assert.equal(r.ai, null);
  assert.deepEqual(r.weeks, apiRow.weeks_12);
  assert.equal(D.toRow({ ...apiRow, pushed_at: null, description: null }, NOW).pushed, null);
  assert.equal(D.toRow({ ...apiRow, description: null }, NOW).desc, '');
});

const history = [
  { week_start: '2026-11-08', stars_gained: 10, days: [1, 1, 2, 2, 2, 1, 1] },
  { week_start: '2026-11-15', stars_gained: 7, days: [1, 1, 1, 1, 1, 1, 1] },
  { week_start: '2026-11-22', stars_gained: 3, days: [2, 1, 0, 0, 0, 0, 0] },
];

test('weeksFromHistory rebuilds weekly totals that end at the current star count', () => {
  const w = D.weeksFromHistory(history, 100);
  assert.deepEqual(w.map((x) => x.gained), [10, 7, 3]);
  assert.deepEqual(w.map((x) => x.total), [90, 97, 100]);
  assert.equal(w[0].t, Date.UTC(2026, 10, 8));
  assert.deepEqual(D.weeksFromHistory([], 100), []);
});

test('daysFromHistory gives the last 30 days, ignoring days that have not happened', () => {
  const days = D.daysFromHistory(history, 100, NOW);
  assert.equal(days.length, 16); // only 16 days of history exist before today
  assert.equal(days[days.length - 1].t, Date.UTC(2026, 10, 23));
  assert.equal(days[days.length - 1].gained, 1);
  assert.equal(days[days.length - 1].total, 100);
  assert.equal(days[days.length - 2].total, 99);
});

test('briefFindings keeps the five questions in order and shows N/A for a null answer', () => {
  const f = D.briefFindings({ interest: { tone: 'good', value: 'Growing' }, maintenance: null, issue_response: null, release_pace: null, maintainer_concentration: null });
  assert.deepEqual(f.map(([q]) => q), ['Is interest real and growing?', 'Is someone still working on it?', 'Will my bug reports get answered?', 'Does it ship on a rhythm?', 'What if one person leaves?']);
  assert.deepEqual(f[0][1], { tone: 'good', v: 'Growing', e: '' });
  assert.deepEqual(f[1][1], { tone: 'neutral', v: 'N/A', e: '' });
  assert.equal(D.briefFindings(null).every(([, a]) => a.v === 'N/A'), true);
});


test('statusTone maps status to its tone and null to neutral', () => {
  assert.equal(D.statusTone('Active'), 'good');
  assert.equal(D.statusTone('Slowing'), 'warn');
  assert.equal(D.statusTone('Quiet'), 'neutral');
  assert.equal(D.statusTone('Archived'), 'bad');
  assert.equal(D.statusTone(null), 'neutral');
});

test('compareRecord keeps the fields the compare list stores, with nulls', () => {
  const rec = D.compareRecord({ ...apiRow, star_history: [] }, NOW);
  assert.deepEqual(rec, { owner: 'pallets', name: 'flask', status: 'Active', lang: 'Python', stars: 70000, pushed: 3, contributors: null, ownerType: 'Organization', ai: null, spike: null, trending: null, desc: 'Micro framework' });
});

test('utcStamp formats a fetch time and gives N/A without one', () => {
  assert.equal(D.utcStamp('2026-11-23T12:04:00Z'), 'Nov 23, 2026, 12:04 UTC');
  assert.equal(D.utcStamp(null), 'N/A');
});

test('updatedLabel says today for the same UTC day', () => {
  assert.equal(D.updatedLabel('2026-11-23T04:10:00Z', NOW), 'today at 04:10 UTC');
  assert.equal(D.updatedLabel('2026-11-22T04:10:00Z', NOW), 'Nov 22, 2026 at 04:10 UTC');
  assert.equal(D.updatedLabel(null, NOW), 'N/A');
});

test('busyMinutes reads Retry-After in seconds, rounded up, at least 1', () => {
  assert.equal(D.busyMinutes('840'), 14);
  assert.equal(D.busyMinutes('30'), 1);
  assert.equal(D.busyMinutes(null), null);
});

test('WEEK constant used by callers is one week in ms', () => {
  assert.equal(D.WEEK, WEEK);
});

const detail = {
  ...apiRow, archived: false, newest_release_at: '2026-10-24T12:00:00Z', star_history: history,
  commit_activity: null, releases: null, issues: null, pull_requests: null,
  brief: { interest: { tone: 'good', value: 'Growing' }, maintenance: null, issue_response: null, release_pace: null, maintainer_concentration: null },
};

test('agoLabel matches the report wording and gives N/A without a time', () => {
  assert.equal(D.agoLabel(NOW, NOW), 'today');
  assert.equal(D.agoLabel(NOW - DAY, NOW), '1 day ago');
  assert.equal(D.agoLabel(NOW - 3 * DAY, NOW), '3 days ago');
  assert.equal(D.agoLabel(NOW - 90 * DAY, NOW), '3 months ago');
  assert.equal(D.agoLabel(null, NOW), 'N/A');
});

const GROWING = { tone: 'good', value: 'Growing', window_days: 15, recent: 1200, previous: 600, change: 1 };

test('briefFindings gives interest evidence from recent, previous and change', () => {
  const f = D.briefFindings({ interest: GROWING });
  assert.deepEqual(f[0][1], { tone: 'good', v: 'Growing', e: '+1,200 net stars in 15 days, +100% on the 15 days before' });
});

test('interest evidence shows N/A only for a null change', () => {
  const steady = { tone: 'neutral', value: 'Steady', window_days: 15, recent: 150, previous: 0, change: null };
  assert.equal(D.briefFindings({ interest: steady })[0][1].e, '+150 net stars in 15 days, N/A on the 15 days before');
  const cooling = { ...steady, value: 'Cooling', recent: -40, previous: 200, change: -1.2 };
  assert.equal(D.briefFindings({ interest: cooling })[0][1].e, '−40 net stars in 15 days, −120% on the 15 days before');
});

test('reportModel takes the 15-day interest change from the API and keeps the 30-day one null', () => {
  const { A } = D.reportModel({ ...detail, brief: { ...detail.brief, interest: GROWING } }, NOW);
  assert.equal(A.interestChange, 1);
  assert.equal(A.momChange, null);
  assert.equal(D.reportModel({ ...detail, brief: null }, NOW).A.interestChange, null);
});

test('reportModel keeps data we do not store as null, never 0', () => {
  const { P, D: data, A } = D.reportModel(detail, NOW);
  assert.equal(P.license, null);
  assert.equal(P.skills, null);
  assert.equal(P.peers, null);
  assert.equal(P.openIssues, 5);
  assert.equal(data.commits, null);
  assert.equal(data.releases, null);
  assert.equal(data.months, null);
  assert.equal(data.contrib, null);
  assert.deepEqual(data.weeks.map((w) => w.total), [69990, 69997, 70000]);
  assert.equal(data.days.length, 16);
  for (const key of ['commits90', 'devChange', 'momChange', 'closeRatio', 'mergeRate', 'rel12', 'medGap', 'top', 'for80', 'single', 'scripted', 'g30']) {
    assert.equal(A[key], null, key);
  }
  assert.equal(A.g7, 12);
  assert.equal(A.spike, null);
  assert.equal(A.lastCommit, Date.parse('2026-11-20T12:00:00Z'));
  assert.equal(A.relDays, 30);
});

test('reportModel takes status and brief answers from the API', () => {
  const { A } = D.reportModel(detail, NOW);
  assert.equal(A.status, 'Active');
  assert.equal(A.statusTone, 'good');
  assert.deepEqual(A.findings[0][1], { tone: 'good', v: 'Growing', e: '' });
  assert.equal(A.findings[1][1].v, 'N/A');
});

test('reportModel checks show N/A where the data is not collected', () => {
  const { A } = D.reportModel(detail, NOW);
  assert.deepEqual(A.checks.map((c) => c.k), ['maintenance', 'maintainers', 'license', 'star_pattern']);
  assert.equal(A.checks[0].t, 'Actively maintained');
  assert.equal(A.checks[0].d, 'Last commit 3 days ago, last release 30 days ago.');
  assert.deepEqual(A.checks.slice(1).map((c) => [c.tone, c.na]), [['neutral', true], ['neutral', true], ['neutral', true]]);
  assert.equal(A.issuesCount, 0);
  assert.equal(A.unknownChecks, 3);
});

test('reportModel shows N/A status when the API has none', () => {
  const { A } = D.reportModel({ ...detail, status: null }, NOW);
  assert.equal(A.status, 'N/A');
  assert.equal(A.statusTone, 'neutral');
  assert.equal(A.checks[0].na, true);
});

test('reportModel lists good-fit and watch-out lines only from known results', () => {
  const active = D.reportModel(detail, NOW).A;
  assert.deepEqual(active.fit, [
    'You need something that is maintained today and should be for the next year.',
    'You want a growing community, which usually means more answers and examples online.',
    'It is published by an organization (pallets), not one personal account.',
  ]);
  assert.deepEqual(active.watch, ['Nothing stood out in the data we have.']);
  const quiet = D.reportModel({ ...detail, status: 'Quiet', owner_type: 'User', brief: null }, NOW).A;
  assert.deepEqual(quiet.fit, ['You only need the current version as it is and can fix problems yourself.']);
  assert.deepEqual(quiet.watch, ['You need security fixes or new features: the last commit was 3 days ago.']);
});
