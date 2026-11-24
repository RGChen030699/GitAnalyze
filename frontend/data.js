/* GitAnalyze: map API responses to the shapes the pages render (F7 Step 7).
   Pure functions only. Rules live on the backend (CLAUDE.md decision 6); this file never decides
   a status or a brief answer, it only formats them. Missing values stay null and show as "N/A".
   Loaded by the pages as window.GAData, and by Node's test runner as a module. */
(function (root, factory) {
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api; else root.GAData = api;
})(typeof self !== 'undefined' ? self : this, function () {
  'use strict';
  const DAY = 864e5, WEEK = 7 * DAY;
  const MON = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
  const TONES = { Active: 'good', Slowing: 'warn', Quiet: 'neutral', Archived: 'bad' };
  const QUESTIONS = [
    ['interest', 'Is interest real and growing?'],
    ['maintenance', 'Is someone still working on it?'],
    ['issue_response', 'Will my bug reports get answered?'],
    ['release_pace', 'Does it ship on a rhythm?'],
    ['maintainer_concentration', 'What if one person leaves?'],
  ];

  const missing = (v) => v === null || v === undefined || (typeof v === 'number' && !isFinite(v));
  const show = (v, fmt) => (missing(v) ? 'N/A' : fmt ? fmt(v) : String(v));
  function compareNullable(a, b, dir) {
    if (missing(a) && missing(b)) return 0;
    if (missing(a)) return 1;
    if (missing(b)) return -1;
    return dir === 'asc' ? a - b : b - a;
  }
  function sumKnown(values) {
    const known = values.filter((v) => !missing(v));
    return known.length ? known.reduce((s, v) => s + v, 0) : null;
  }
  const daysAgo = (iso, now) => (iso ? (now - Date.parse(iso)) / DAY : null);
  const statusTone = (status) => TONES[status] || 'neutral';

  function rankingsQuery(state, page) {
    const q = new URLSearchParams();
    if (state.view === 'gaining') { q.set('sort', 'gained'); q.set('window', state.win); }
    else if (state.view === 'trending') { q.set('sort', 'trending'); q.set('trending', '1'); }
    else q.set('sort', 'stars');
    if (state.lang && state.lang !== 'Any') q.set('lang', state.lang);
    if (state.status && state.status !== 'any') q.set('status', state.status);
    if (state.hideArch) q.set('archived', '0');
    q.set('limit', '100');
    q.set('page', String(page));
    return q.toString();
  }

  function toRow(r, now) {
    return {
      id: r.full_name.toLowerCase(), full: r.full_name, owner: r.owner, name: r.name,
      desc: r.description || '', lang: r.language, stars: r.stars, status: r.status,
      ai: r.ai, pushed: daysAgo(r.pushed_at, now), contributors: r.contributors, ownerType: r.owner_type,
      gain7: r.stars_gained_7d, gain30: r.stars_gained_30d, gainYear: r.stars_gained_year,
      weeks: r.weeks_12, forks: r.forks, openIssues: r.open_issues, spike: r.spike, trending: r.trending,
      source: r.source, fetchedAt: r.fetched_at,
    };
  }

  const weekStart = (w) => Date.parse(w.week_start + 'T00:00:00Z');
  const byWeek = (history) => (history || []).slice().sort((a, b) => weekStart(a) - weekStart(b));
  /** Weekly points oldest first, with totals counted back from today's star count. */
  function weeksFromHistory(history, stars) {
    const weeks = byWeek(history).map((w) => ({ t: weekStart(w), gained: w.stars_gained, total: null }));
    let running = stars;
    for (let i = weeks.length - 1; i >= 0; i--) { weeks[i].total = running; running -= weeks[i].gained; }
    return weeks;
  }
  /** Daily points for the last 30 days that have happened, with totals. */
  function daysFromHistory(history, stars, now) {
    const today = Math.floor(now / DAY) * DAY;
    const days = byWeek(history).flatMap((w) => w.days.map((gained, k) => ({ t: weekStart(w) + k * DAY, gained, total: null })))
      .filter((x) => x.t <= today).slice(-30);
    let running = stars;
    for (let i = days.length - 1; i >= 0; i--) { days[i].total = running; running -= days[i].gained; }
    return days;
  }

  // Same formats as report-kit.js, which Node tests don't load.
  const sign = (x) => (x > 0 ? '+' : x < 0 ? '−' : '');
  const signed = (x) => sign(x) + Math.abs(Math.round(x)).toLocaleString('en-US');
  const pct = (x) => sign(x) + Math.abs(Math.round(x * 100)) + '%';

  /** Evidence line from the numbers behind the interest answer; other answers carry none. */
  function evidence(a) {
    const w = a.window_days;
    if (!w || missing(a.recent)) return '';
    return `${signed(a.recent)} net stars in ${w} days, ${show(a.change, pct)} on the ${w} days before`;
  }

  function briefFindings(brief) {
    return QUESTIONS.map(([key, question]) => {
      const a = brief && brief[key];
      return [question, a ? { tone: a.tone, v: a.value, e: evidence(a) } : { tone: 'neutral', v: 'N/A', e: '' }];
    });
  }

  function compareRecord(detail, now) {
    return {
      owner: detail.owner, name: detail.name, status: detail.status, lang: detail.language, stars: detail.stars,
      pushed: daysAgo(detail.pushed_at, now), contributors: missing(detail.contributors) ? null : detail.contributors,
      ownerType: detail.owner_type, ai: detail.ai === undefined ? null : detail.ai,
      spike: detail.spike === undefined ? null : detail.spike, trending: detail.trending === undefined ? null : detail.trending,
      desc: detail.description || '',
    };
  }

  const pad = (n) => String(n).padStart(2, '0');
  const dateLabel = (d) => MON[d.getUTCMonth()] + ' ' + d.getUTCDate() + ', ' + d.getUTCFullYear();
  const timeLabel = (d) => pad(d.getUTCHours()) + ':' + pad(d.getUTCMinutes()) + ' UTC';
  function utcStamp(iso) {
    if (!iso) return 'N/A';
    const d = new Date(iso);
    return dateLabel(d) + ', ' + timeLabel(d);
  }
  function updatedLabel(iso, now) {
    if (!iso) return 'N/A';
    const d = new Date(iso);
    const sameDay = Math.floor(d.getTime() / DAY) === Math.floor(now / DAY);
    return (sameDay ? 'today' : dateLabel(d)) + ' at ' + timeLabel(d);
  }
  function busyMinutes(retryAfter) {
    const seconds = parseInt(retryAfter, 10);
    return isFinite(seconds) ? Math.max(1, Math.ceil(seconds / 60)) : null;
  }

  /** Same wording as the report pages' sample helper it replaces. */
  function agoLabel(t, now) {
    if (missing(t)) return 'N/A';
    const days = Math.round((now - t) / DAY);
    if (days <= 0) return 'today';
    if (days === 1) return '1 day ago';
    if (days < 60) return days + ' days ago';
    if (days < 730) return Math.round(days / 30.4) + ' months ago';
    return (days / 365).toFixed(1).replace(/\.0$/, '') + ' years ago';
  }
  const naCheck = (k, label) => ({ tone: 'neutral', t: label + ': N/A', d: '', k, na: true });
  function maintenanceCheck(status, lastCommit, lastRel, relDays, now) {
    const commit = agoLabel(lastCommit, now);
    if (status === 'Active') return { tone: 'good', t: 'Actively maintained', d: 'Last commit ' + commit + ', last release ' + (lastRel ? agoLabel(lastRel.t, now) : 'N/A') + '.', k: 'maintenance' };
    if (status === 'Slowing') return { tone: 'warn', t: 'Maintenance is slowing', d: 'Last commit ' + commit + ', but no release in ' + show(relDays, Math.round) + ' days.', k: 'maintenance' };
    if (status === 'Archived') return { tone: 'bad', t: 'Archived by its owner', d: 'Read-only. No one will fix bugs or answer issues.', k: 'maintenance' };
    if (status === 'Quiet') return { tone: 'bad', t: 'No recent work', d: 'Last commit ' + commit + '.', k: 'maintenance' };
    return naCheck('maintenance', 'Maintenance');
  }
  /** Good-fit and watch-out lines, from results the API gives (status, brief tones, publisher). */
  function fitAndWatch(status, findings, ownerType, owner, lastCommit, now) {
    const [momentum, , support, shipping] = findings.map(([, f]) => f);
    const fit = [], watch = [];
    if (status === 'Active') fit.push('You need something that is maintained today and should be for the next year.');
    if (momentum.tone === 'good') fit.push('You want a growing community, which usually means more answers and examples online.');
    if (ownerType === 'Organization') fit.push('It is published by an organization (' + owner + '), not one personal account.');
    if (status === 'Quiet') fit.push('You only need the current version as it is and can fix problems yourself.');
    if (support.tone === 'warn' || support.tone === 'bad') watch.push('You expect quick help: issues are being opened faster than they are closed.');
    if (shipping.tone === 'warn') watch.push('You need regular fixes: the next release is well past its usual date.');
    if (status === 'Quiet') watch.push('You need security fixes or new features: the last commit was ' + agoLabel(lastCommit, now) + '.');
    if (!watch.length) watch.push('Nothing stood out in the data we have.');
    if (!fit.length) fit.push('You are only evaluating it, and will check again later.');
    return { fit, watch };
  }
  /** The P (profile), D (series) and A (results) shapes the report and compare pages render. */
  function reportModel(det, now) {
    const P = { owner: det.owner, name: det.name, desc: det.description || '', lang: det.language, ownerType: det.owner_type,
      archived: det.archived, openIssues: det.open_issues, openPrs: null, license: null, skills: null, peers: null, trending: null };
    // Commit activity, releases, issues and contributors are not stored yet, so their charts stay null.
    const D = { weeks: weeksFromHistory(det.star_history, det.stars), days: daysFromHistory(det.star_history, det.stars, now),
      commits: null, releases: null, months: null, contrib: null };
    const lastCommit = det.pushed_at ? Date.parse(det.pushed_at) : null;
    const lastRel = det.newest_release_at ? { t: Date.parse(det.newest_release_at), pre: false } : null;
    const relDays = lastRel ? (now - lastRel.t) / DAY : null;
    const findings = briefFindings(det.brief);
    const interest = det.brief && det.brief.interest;
    const interestChange = interest && !missing(interest.change) ? interest.change : null;
    const checks = [maintenanceCheck(det.status, lastCommit, lastRel, relDays, now),
      naCheck('maintainers', 'Maintainers'), naCheck('license', 'License'), naCheck('star_pattern', 'Star pattern')];
    const known = checks.filter((c) => !c.na);
    const A = {
      status: det.status || 'N/A', statusTone: statusTone(det.status), lastCommit, lastRel, relDays,
      g7: det.stars_gained_7d, g30: det.stars_gained_30d, momChange: null, interestChange, commits90: null, commitsPrev90: null, devChange: null,
      spike: null, top: null, for80: null, single: null, closeRatio: null, mergeRate: null, backlog6: null, growStreak: null,
      prO: null, prM: null, rel12: null, medGap: null, scripted: null, checks, findings,
      issuesCount: known.filter((c) => c.tone === 'warn' || c.tone === 'bad').length, unknownChecks: checks.length - known.length,
      ...fitAndWatch(det.status, findings, det.owner_type, det.owner, lastCommit, now),
    };
    return { P, D, A };
  }

  /* F6 P1: the API puts a fetch time on every value, not one for the whole response.
     "Last updated" is the newest of them; null when none has one. */
  function lastFetched(det) {
    const times = [];
    Object.values((det && det.provenance) || {}).forEach((o) => { if (o && o.fetched_at) times.push(o.fetched_at); });
    ((det && det.star_history) || []).forEach((w) => { if (w && w.fetched_at) times.push(w.fetched_at); });
    if (!times.length) return null;
    return times.reduce((a, b) => (Date.parse(b) > Date.parse(a) ? b : a));
  }

  return {
    DAY, WEEK, missing, show, compareNullable, sumKnown, daysAgo, statusTone, rankingsQuery, toRow,
    weeksFromHistory, daysFromHistory, briefFindings, compareRecord, utcStamp, updatedLabel, busyMinutes, lastFetched,
    agoLabel, reportModel,
  };
});
