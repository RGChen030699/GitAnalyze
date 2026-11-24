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

  function briefFindings(brief) {
    return QUESTIONS.map(([key, question]) => {
      const a = brief && brief[key];
      return [question, a ? { tone: a.tone, v: a.value, e: '' } : { tone: 'neutral', v: 'N/A', e: '' }];
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

  return {
    DAY, WEEK, missing, show, compareNullable, sumKnown, daysAgo, statusTone, rankingsQuery, toRow,
    weeksFromHistory, daysFromHistory, briefFindings, compareRecord, utcStamp, updatedLabel, busyMinutes,
  };
});
