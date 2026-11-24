/* GitAnalyze shared sample data, rules and chart helpers, used by the report and compare pages.
   Sample numbers until the API is connected (F7 Step 7); the rules move to Django with it (CLAUDE.md decision 6). */
(() => {
'use strict';
/* ---------- helpers ---------- */
const $ = (s, r = document) => r.querySelector(s);
const DAY = 864e5;
const NOW = Date.UTC(2026, 10, 23, 14, 0);           // sample "today"
const LAST_SUN = Date.UTC(2026, 10, 22);
const MON = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
const d = (t) => new Date(t);
const fDay = (t) => `${MON[d(t).getUTCMonth()]} ${d(t).getUTCDate()}`;
const fDayY = (t) => `${fDay(t)}, ${d(t).getUTCFullYear()}`;
const fMonY = (t) => `${MON[d(t).getUTCMonth()]} ${d(t).getUTCFullYear()}`;
const n0 = (x) => Math.round(x).toLocaleString('en-US');
const compact = (x) => { const a = Math.abs(x); return a >= 1e6 ? (x/1e6).toFixed(1).replace(/\.0$/,'')+'M' : a >= 1e4 ? Math.round(x/1e3)+'k' : a >= 1e3 ? (x/1e3).toFixed(1).replace(/\.0$/,'')+'k' : String(Math.round(x)); };
const signed = (x) => (x > 0 ? '+' : x < 0 ? '−' : '') + n0(Math.abs(x));
const pct = (x) => (x > 0 ? '+' : x < 0 ? '−' : '') + Math.abs(Math.round(x*100)) + '%';
const sum = (a) => a.reduce((s, v) => s + v, 0);
const median = (a) => { if (!a.length) return null; const s = [...a].sort((x,y)=>x-y), m = s.length >> 1; return s.length % 2 ? s[m] : (s[m-1]+s[m])/2; };
const ago = (t) => { const days = Math.round((NOW - t)/DAY); return days <= 0 ? 'today' : days === 1 ? '1 day ago' : days < 60 ? `${days} days ago` : days < 730 ? `${Math.round(days/30.4)} months ago` : `${(days/365).toFixed(1).replace(/\.0$/,'')} years ago`; };
const esc = (s) => String(s).replace(/[&<>"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
function rng(seed){ return () => { seed |= 0; seed = seed + 0x6D2B79F5 | 0; let t = Math.imul(seed ^ seed >>> 15, 1 | seed); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; }; }
function niceMax(v){ if (v <= 0) return 1; const p = Math.pow(10, Math.floor(Math.log10(v))); for (const m of [1,2,2.5,5,10]) if (m*p >= v) return m*p; return 10*p; }
function niceTicks(lo, hi){ const span = hi - lo || 1; const step0 = span/4, p = Math.pow(10, Math.floor(Math.log10(step0))); let step = p; for (const m of [1,2,2.5,5,10]) { if (m*p >= step0) { step = m*p; break; } } const a = Math.floor(lo/step)*step, out = []; for (let v = a; v <= hi + step*0.001; v += step) out.push(+v.toFixed(6)); if (out[out.length-1] < hi) out.push(out[out.length-1]+step); return out; }

const ICON = {
  check:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12.5l4.5 4.5L19 7.5"/></svg>',
  warn:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 3.5L2.5 20h19z"/><path d="M12 10v4.5M12 17.3v.2"/></svg>',
  stop:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" aria-hidden="true"><path d="M6.5 6.5l11 11M17.5 6.5l-11 11"/></svg>',
  minus:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" aria-hidden="true"><path d="M6 12h12"/></svg>',
  clock:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" aria-hidden="true"><circle cx="12" cy="12" r="8.5"/><path d="M12 7.5V12l3 2"/></svg>',
  up:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 19V5M6 11l6-6 6 6"/></svg>',
  down:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 5v14M6 13l6 6 6-6"/></svg>',
  flat:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14M14 7l5 5-5 5"/></svg>',
  info:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M12 11v5.5M12 7.6v.2"/></svg>'
};
const TONE_ICON = { good:'check', warn:'warn', bad:'stop', neutral:'minus' };
const toneIcon = (tone) => ICON[TONE_ICON[tone]];

/* ---------- sample repositories ---------- */
const PROFILES = [
  { id:'agent-kit', owner:'lumen-labs', name:'agent-kit', ownerType:'Organization', lang:'Python', license:'MIT',
    desc:'Agent skills for document work: PDFs, spreadsheets and slide decks, packaged for AI assistants.',
    blurb:'Healthy, growing, one thing to check', seed:11, ageWeeks:156, lastCommitDays:2,
    star:(i, n, r) => (40 + 300*Math.pow(i/n, 1.7)) * (0.8 + 0.4*r()) * (i > n-5 ? 1.4 : 1),
    commits:(i, r) => Math.max(0, Math.round(24 + 6*Math.sin(i/5) + (i > 38 ? 7 : 0) + 10*r())),
    releaseEvery:34, lastReleaseDays:12, firstVersion:[1,0,0], prereleaseEvery:4,
    contrib:[41,14,9,7,5,4,3,3,2,2,2,1.5,1.5,1,1,1,1,0.5,0.5,0.5,0.5], contribOther:26,
    issues:(m, r) => ({ opened: Math.round(58 + m*3.4 + 8*r()), closed: Math.round(m < 6 ? 60 + m*2 + 8*r() : 66 + 6*r()) }),
    prs:(m, r) => { const o = Math.round(42 + m*1.2 + 8*r()); return { opened:o, merged:Math.round(o*(0.8 + 0.08*r())) }; },
    openIssues:214, openPrs:31, spikeWeeks:0,
    skills:[['pdf-tools','Reads, fills and merges PDF files',2],['sheet-builder','Builds spreadsheets with formulas',1],['deck-maker','Creates slide decks from an outline',0],['doc-review','Reviews a document and suggests edits',0],['table-extract','Pulls tables out of PDFs and images',3],['style-guide','Applies a house writing style',0]],
    peers:{ group:'Python', n:312, rows:[['Total stars',78,18400,'stars'],['Stars gained, last 30 days',91,2210,'stars'],['Commits, last 90 days',84,412,'commits'],['Active contributors, last 90 days',80,17,'people'],['Issues closed per issue opened',38,0.86,'ratio'],['Releases, last 12 months',72,11,'releases']] } },
  { id:'hype-agent', owner:'newwave', name:'hype-agent', ownerType:'User', lang:'TypeScript', license:'NOASSERTION',
    desc:'An autonomous agent that writes, tests and ships your code for you.',
    blurb:'Sudden star spike, one maintainer', seed:23, ageWeeks:34, lastCommitDays:20,
    star:(i, n, r) => (i === n-2 ? 1380 : i === n-1 ? 1620 : 12 + 30*r()),
    commits:(i, r) => i > 44 ? (i === 48 ? 3 : 0) : i < 18 ? 0 : Math.round(2 + 6*r()),
    releaseEvery:30, lastReleaseDays:208, releaseCount:3, firstVersion:[0,1,0], prereleaseEvery:2,
    contrib:[92,5,3], contribOther:0,
    issues:(m, r) => ({ opened: m < 5 ? 0 : Math.round(m === 11 ? 46 : 4 + 6*r()), closed: m < 5 ? 0 : Math.round(1 + 3*r()) }),
    prs:(m, r) => { const o = m < 5 ? 0 : Math.round(m === 11 ? 18 : 1 + 4*r()); return { opened:o, merged:Math.round(o*0.35) }; },
    openIssues:71, openPrs:19, spikeWeeks:2,
    skills:[['auto-ship','Commits and pushes code on your behalf',4],['shell-runner','Runs shell commands it decides on',2],['dep-install','Installs packages it thinks you need',1],['env-reader','Reads environment files for settings',1]],
    peers:{ group:'TypeScript', n:280, rows:[['Total stars',41,4920,'stars'],['Stars gained, last 30 days',99,3410,'stars'],['Commits, last 90 days',6,3,'commits'],['Active contributors, last 90 days',4,1,'people'],['Issues closed per issue opened',9,0.22,'ratio'],['Releases, last 12 months',14,3,'releases']] } },
  { id:'tablekit', owner:'oldframe', name:'tablekit', ownerType:'Organization', lang:'JavaScript', license:'Apache-2.0',
    desc:'A data grid component for the browser with sorting, filtering and virtual scrolling.',
    blurb:'Famous but quiet for 8 months', seed:37, ageWeeks:400, lastCommitDays:241,
    star:(i, n, r) => { const t = i/n; return Math.max(-14, (t < 0.55 ? 60 + 420*t : 290*Math.exp(-(t-0.55)*9)) * (0.75 + 0.5*r()) - (t > 0.93 ? 9*r() : 0)); },
    commits:(i, r) => i < 18 ? Math.round(3*r()) : 0,
    releaseEvery:88, lastReleaseDays:412, releaseCount:14, firstVersion:[3,0,0], prereleaseEvery:0,
    contrib:[58,27,15], contribOther:0,
    issues:(m, r) => ({ opened: Math.round(14 + 9*r()), closed: Math.round(m < 3 ? 6*r() : r()*1.4) }),
    prs:(m, r) => { const o = Math.round(5 + 5*r()); return { opened:o, merged: m < 3 ? Math.round(o*0.3) : 0 }; },
    openIssues:388, openPrs:64, spikeWeeks:0,
    skills:[],
    peers:{ group:'JavaScript', n:290, rows:[['Total stars',96,41200,'stars'],['Stars gained, last 30 days',7,18,'stars'],['Commits, last 90 days',1,0,'commits'],['Active contributors, last 90 days',2,0,'people'],['Issues closed per issue opened',3,0.04,'ratio'],['Releases, last 12 months',4,0,'releases']] } }
];

PROFILES.push({ id:'slowing', owner:'', name:'', ownerType:'Organization', lang:'', license:'MIT', desc:'', blurb:'', seed:51, ageWeeks:220, lastCommitDays:60,
  star:(i, n, r) => (30 + 160*Math.sin(Math.min(1, i/n)*Math.PI*0.85)) * (0.75 + 0.5*r()),
  commits:(i, r) => Math.max(0, Math.round((i < 26 ? 18 - i*0.4 : 5 - (i-26)*0.2) + 4*r())),
  releaseEvery:45, lastReleaseDays:210, firstVersion:[2,0,0], prereleaseEvery:5,
  contrib:[48,18,11,7,5,4,3,2,2], contribOther:20,
  issues:(m, r) => ({ opened: Math.round(30 + 8*r()), closed: Math.round(m < 6 ? 28 + 6*r() : 14 + 6*r()) }),
  prs:(m, r) => { const o = Math.round(14 + 6*r()); return { opened:o, merged:Math.round(o*(m < 6 ? 0.75 : 0.4)) }; },
  openIssues:160, openPrs:22, spikeWeeks:0, skills:[],
  peers:{ group:'', n:300, rows:[['Total stars',70,0,'stars'],['Stars gained, last 30 days',35,0,'stars'],['Commits, last 90 days',30,0,'commits'],['Active contributors, last 90 days',33,0,'people'],['Issues closed per issue opened',28,0.5,'ratio'],['Releases, last 12 months',20,1,'releases']] } });
const TEMPLATE = (id) => PROFILES.find(p => p.id === id);
const hashStr = (str) => { let h = 2166136261; for (const ch of str) { h ^= ch.charCodeAt(0); h = Math.imul(h, 16777619); } return h >>> 0; };
/* The dashboard passes its row in the URL (/repo/{owner}/{name}?s=…). Sample data until the API is wired (F7 Step 7). */
const KNOWN = {
  'lumen-labs/agent-kit': { status:'Active', lang:'Python', stars:18455, pushed:2, contributors:64, ownerType:'Organization', ai:true, spike:false, trending:0, desc:'Agent skills for document work: PDF, slides, spreadsheets.' },
  'newwave/hype-agent': { status:'Active', lang:'Python', stars:3200, pushed:1, contributors:2, ownerType:'User', ai:true, spike:true, trending:1, desc:'An autonomous agent that promises to do everything.' },
  'oldframe/tablekit': { status:'Quiet', lang:'JavaScript', stars:41200, pushed:241, contributors:3, ownerType:'Organization', ai:false, spike:false, trending:0, desc:'A data grid component for the browser with sorting, filtering and virtual scrolling.' }
};
/* A record for a repository we have no row for (a shared link): sample values seeded by its name. */
function recordFor(full){
  const [owner, name] = full.split('/');
  const k = KNOWN[full.toLowerCase()]; if (k) return Object.assign({ owner, name }, k);
  const r = rng(hashStr(full.toLowerCase()));
  const status = ['Active','Active','Active','Slowing','Quiet'][Math.floor(r()*5)];
  return { owner, name, status, lang: ['Python','TypeScript','Go','Rust','JavaScript'][Math.floor(r()*5)], stars: Math.round(800 + r()*40000),
    pushed: status === 'Active' ? 1 + Math.floor(r()*20) : status === 'Slowing' ? 40 + Math.floor(r()*120) : 200 + Math.floor(r()*400),
    contributors: 3 + Math.floor(r()*120), ownerType: r() < 0.6 ? 'Organization' : 'User', ai: r() < 0.4, spike:false, trending:0, desc:'' };
}
function readRecord(){
  const q = new URLSearchParams(location.search);
  const m = location.pathname.match(/\/repo\/([^/]+)\/([^/?#]+)/);
  const full = m ? decodeURIComponent(m[1]) + '/' + decodeURIComponent(m[2]) : (q.get('repo') || 'lumen-labs/agent-kit');
  const [owner, name] = full.split('/');
  const num = (k, dflt) => { const v = parseFloat(q.get(k)); return isFinite(v) ? v : dflt; };
  if (!q.has('s')) return (window.GACompare && window.GACompare.find(full)) || recordFor(full);
  return { owner, name, status: q.get('s') || 'Active', lang: q.get('l') || 'N/A', stars: num('st', 0), pushed: num('p', 2), contributors: num('c', 10),
    ownerType: q.get('o') === 'User' ? 'User' : 'Organization', ai: q.get('ai') === '1', spike: q.get('sp') === '1', trending: num('t', 0), desc: q.get('d') || '' };
}
function profileFor(rec){
  const base = rec.spike ? TEMPLATE('hype-agent') : rec.status === 'Active' ? TEMPLATE('agent-kit') : rec.status === 'Slowing' ? TEMPLATE('slowing') : TEMPLATE('tablekit');
  const p = Object.assign({}, base, { id: (rec.owner + '/' + rec.name).toLowerCase(), owner: rec.owner, name: rec.name, desc: rec.desc, lang: rec.lang, ownerType: rec.ownerType,
    seed: hashStr(rec.owner + '/' + rec.name), targetStars: rec.stars || null, trending: rec.trending, archived: rec.status === 'Archived', contribOther: Math.max(rec.contributors, base.contrib.length) });
  if (rec.status === 'Active') { p.lastCommitDays = Math.min(Math.max(1, rec.pushed), 30); p.lastReleaseDays = Math.min(base.lastReleaseDays, 40); if (rec.spike) p.releaseCount = 3; }
  else if (rec.status === 'Slowing') { p.lastCommitDays = Math.min(Math.max(31, rec.pushed), 182); }
  else { p.lastCommitDays = Math.max(183, rec.pushed); }
  if (rec.contributors <= 3 && !rec.spike) p.contrib = [62, 26, 12].slice(0, Math.max(1, rec.contributors));
  p.skills = rec.ai ? (base.skills.length ? base.skills : TEMPLATE('agent-kit').skills) : [];
  p.peers = Object.assign({}, base.peers, { group: rec.lang });
  return p;
}
function build(p){
  const r = rng(p.seed);
  /* weekly net stars, oldest first */
  const weeks = [];
  for (let i = 0; i < p.ageWeeks; i++) weeks.push({ t: LAST_SUN - (p.ageWeeks-1-i)*7*DAY, gained: Math.round(p.star(i, p.ageWeeks-1, r)) });
  weeks[weeks.length-1].gained = Math.round(weeks[weeks.length-1].gained * 2/7);   // current week is partial (Sun + Mon)
  let tot = 0; weeks.forEach(w => { tot += w.gained; w.total = Math.max(0, tot); });
  if (p.targetStars && tot > 0) { const f = p.targetStars / tot; tot = 0; weeks.forEach(w => { w.gained = Math.round(w.gained * f); tot += w.gained; w.total = Math.max(0, tot); }); weeks[weeks.length-1].total += p.targetStars - tot; weeks[weeks.length-1].gained += p.targetStars - tot; }
  /* daily, last 30 days, split from weekly */
  const days = [];
  for (let k = 29; k >= 0; k--) {
    const t = Date.UTC(2026,10,23) - k*DAY;
    const wk = weeks.find(w => t >= w.t && t < w.t + 7*DAY) || weeks[weeks.length-1];
    const per = wk === weeks[weeks.length-1] ? wk.gained/2 : wk.gained/7;
    days.push({ t, gained: Math.round(per * (0.7 + 0.6*r())) });
  }
  let dt = weeks[weeks.length-1].total - sum(days.map(x => x.gained));
  days.forEach(x => { dt += x.gained; x.total = dt; });
  /* commits, 52 weeks with days */
  const commits = [];
  for (let i = 0; i < 52; i++) {
    const total = p.commits(i, r);
    const w = [0.25,1.2,1.3,1.25,1.15,1,0.35].map(f => f*(0.6 + 0.8*r()));
    const ws = sum(w); const daysArr = w.map(f => Math.round(total*f/ws));
    commits.push({ t: LAST_SUN - (51-i)*7*DAY, total: sum(daysArr), days: daysArr });
  }
  if (p.lastCommitDays > 2) { const lim = NOW - p.lastCommitDays*DAY; commits.forEach(c => c.days.forEach((v, k) => { if (c.t + k*DAY > lim) c.days[k] = 0; })); commits.forEach(c => c.total = sum(c.days)); }
  if (p.lastCommitDays <= 30) { const t0 = NOW - p.lastCommitDays*DAY; const c = commits.find(c => t0 >= c.t && t0 < c.t+7*DAY); if (c) { const k = Math.floor((t0-c.t)/DAY); c.days[k] = Math.max(1, c.days[k]); c.total = sum(c.days); } }
  /* releases */
  const releases = [];
  const count = p.releaseCount || Math.floor((p.ageWeeks*7 - 40) / p.releaseEvery);
  let t = NOW - p.lastReleaseDays*DAY, v = [...p.firstVersion];
  const stamps = [];
  for (let i = 0; i < count; i++) { stamps.push(t); t -= (p.releaseEvery + (r()-0.5)*p.releaseEvery*0.5)*DAY; }
  stamps.reverse().forEach((ts, i) => {
    if (i) { if (i % 6 === 0) { v = [v[0]+1, 0, 0]; } else if (i % 2 === 0) { v = [v[0], v[1]+1, 0]; } else { v = [v[0], v[1], v[2]+1]; } }
    const pre = p.prereleaseEvery && i % p.prereleaseEvery === p.prereleaseEvery-1 && i !== stamps.length-1;
    releases.push({ t: ts, tag: 'v' + v.join('.') + (pre ? '-rc.1' : ''), pre });
  });
  /* issues & PRs, 12 months oldest first */
  const months = [];
  for (let m = 0; m < 12; m++) {
    const mt = Date.UTC(2025, 11 + m, 1);
    months.push({ t: mt, ...p.issues(m, r), pr: p.prs(m, r) });
  }
  /* contributors */
  const contrib = p.contrib.map((s, i) => ({ login: i === 0 ? p.owner === 'newwave' ? 'nw-dev' : p.owner + '-' + ['ada','ben','cy'][0] : 'person-' + (i+1), share: s/100 }));
  const names = { 'agent-kit':['mira-k','jtan','oboyle','sasha-r','devlin','priya-n','kofi','lena-w','tomasz','ruiz'], 'hype-agent':['nw-dev','kai-x','j0e'], 'tablekit':['hgrant','mvoss','elle-b'] }[p.id] || [];
  contrib.forEach((c, i) => { if (names[i]) c.login = names[i]; });
  return { weeks, days, commits, releases, months, contrib };
}

/* ---------- rules (mirror backend F2 / F8 G7; the frontend only renders results) ---------- */
function analyse(p, D){
  const lastCommit = NOW - p.lastCommitDays*DAY;
  const lastRel = D.releases.length ? D.releases.filter(x => !x.pre).slice(-1)[0] || D.releases.slice(-1)[0] : null;
  const relDays = lastRel ? (NOW - lastRel.t)/DAY : null;
  let status;
  if (p.archived) status = 'Archived';
  else if (p.lastCommitDays <= 30 && (relDays === null || relDays <= 182)) status = 'Active';
  else if (p.lastCommitDays <= 182) status = 'Slowing';
  else status = 'Quiet';
  const statusTone = { Active:'good', Slowing:'warn', Quiet:'neutral', Archived:'bad' }[status];

  const W = D.weeks, n = W.length;
  const g7 = W[n-1].gained + W[n-2].gained * 5/7;
  const g30 = sum(D.days.map(x => x.gained));
  const prev30 = sum(W.slice(Math.max(0, n-10), n-5).map(w => w.gained)) * 30/35;
  const base12 = median(W.slice(Math.max(0, n-15), n-3).map(w => w.gained)) || 1;
  const commits90 = sum(D.commits.slice(-13).map(c => c.total));
  const commitsPrev90 = sum(D.commits.slice(-26, -13).map(c => c.total));
  const spike = p.spikeWeeks > 0 && W.slice(-3).some(w => w.gained > 8*Math.max(base12, 10)) && commits90 < 40;

  const top = D.contrib[0].share;
  let cum = 0, for80 = 0; for (const c of D.contrib) { cum += c.share; for80++; if (cum >= 0.8) break; }
  const single = top >= 0.8;

  const last6 = D.months.slice(-6);
  const opened6 = sum(last6.map(m => m.opened)), closed6 = sum(last6.map(m => m.closed));
  const closeRatio = opened6 ? closed6/opened6 : null;
  const backlog6 = opened6 - closed6;
  let growStreak = 0; for (let i = D.months.length-1; i >= 0 && D.months[i].opened > D.months[i].closed; i--) growStreak++;
  const prO = sum(D.months.map(m => m.pr.opened)), prM = sum(D.months.map(m => m.pr.merged));
  const mergeRate = prO ? prM/prO : null;

  const relTimes = D.releases.filter(x => !x.pre).map(x => x.t);
  const gaps = relTimes.slice(1).map((t, i) => (t - relTimes[i])/DAY);
  const medGap = median(gaps.slice(-8));
  const rel12 = D.releases.filter(x => !x.pre && x.t > NOW - 365*DAY).length;

  const checks = [];
  checks.push(status === 'Active' ? { tone:'good', t:'Actively maintained', d:`Last commit ${ago(lastCommit)}, last release ${lastRel ? ago(lastRel.t) : 'never'}.`, k:'maintenance' }
    : status === 'Slowing' ? { tone:'warn', t:'Maintenance is slowing', d:`Last commit ${ago(lastCommit)}, but no release in ${Math.round(relDays)} days.`, k:'maintenance' }
    : status === 'Archived' ? { tone:'bad', t:'Archived by its owner', d:'Read-only. No one will fix bugs or answer issues.', k:'maintenance' }
    : { tone:'bad', t:'No recent work', d:`Last commit ${ago(lastCommit)}.`, k:'maintenance' });
  checks.push(single ? { tone:'warn', t:'Mostly one person', d:`${D.contrib[0].login} made ${Math.round(top*100)}% of last year’s commits.`, k:'maintainers' }
    : { tone:'good', t:'Shared maintenance', d:`${for80} people made 80% of last year’s commits. The top person made ${Math.round(top*100)}%.`, k:'maintainers' });
  checks.push(p.license === 'NOASSERTION' ? { tone:'warn', t:'Custom or unrecognized license', d:'GitHub couldn’t match it to a standard license. Read it before you reuse the code.', k:'license' }
    : !p.license ? { tone:'bad', t:'No license', d:'No license: others may not legally reuse this code.', k:'license' }
    : { tone:'good', t:`${p.license} license`, d:'A standard open-source license.', k:'license' });
  checks.push(spike ? { tone:'warn', t:'Unusual star spike', d:'Unusual spike: lots of new stars but little other activity.', k:'star_pattern' }
    : g7 <= 0 ? { tone:'neutral', t:'No new attention', d:`Net ${signed(Math.round(g7))} stars in the last 7 days.`, k:'star_pattern' }
    : { tone:'good', t:'Steady interest', d:`+${n0(g7)} stars in the last 7 days, in line with recent weeks.`, k:'star_pattern' });
  const scripted = p.skills.filter(s => s[2] > 0).length;
  if (p.skills.length) checks.push(scripted ? { tone:'warn', t:`${scripted} of ${p.skills.length} skills run scripts`, d:'This skill includes scripts that can run on your computer. Read them before installing.', k:'scripts' }
    : { tone:'good', t:'No skills run scripts', d:`${p.skills.length} skills, all instructions only.`, k:'scripts' });
  const issuesCount = checks.filter(c => c.tone === 'warn' || c.tone === 'bad').length;

  /* decision brief findings */
  const momChange = prev30 > 0 ? (g30 - prev30)/prev30 : null;
  const momentum = spike ? { tone:'warn', v:'Spiky', e:`${Math.round(100*(W[n-1].gained+W[n-2].gained)/Math.max(1,g30))}% of the last 30 days’ stars arrived in 2 weeks.` }
    : g30 <= 0 ? { tone:'neutral', v:'Fading', e:`Net ${signed(g30)} stars in 30 days.` }
    : g30 < 0.002 * W[n-1].total ? { tone:'neutral', v:'Flat', e:`+${n0(g30)} stars in 30 days, under 0.2% of its ${n0(W[n-1].total)} total.` }
    : momChange !== null && momChange > 0.1 ? { tone:'good', v:'Growing', e:`+${n0(g30)} stars in 30 days, ${pct(momChange)} on the 30 days before.` }
    : momChange !== null && momChange < -0.1 ? { tone:'warn', v:'Cooling', e:`+${n0(g30)} stars in 30 days, ${pct(momChange)} on the 30 days before.` }
    : { tone:'neutral', v:'Steady', e:`+${n0(g30)} stars in 30 days, about the same as before.` };
  const devChange = commitsPrev90 ? (commits90 - commitsPrev90)/commitsPrev90 : null;
  const maintenance = commits90 === 0 ? { tone:'bad', v:'Stopped', e:`No commits in 13 weeks. Last commit ${ago(lastCommit)}.` }
    : devChange !== null && devChange < -0.4 ? { tone:'warn', v:'Slowing down', e:`${n0(commits90)} commits in 13 weeks, ${pct(devChange)} on the 13 before.` }
    : devChange !== null && devChange > 0.1 ? { tone:'good', v:'Speeding up', e:`${n0(commits90)} commits in 13 weeks, ${pct(devChange)} on the 13 before.` }
    : { tone:'good', v:'Steady', e:`${n0(commits90)} commits in 13 weeks, similar to the 13 before.` };
  const support = closeRatio === null ? { tone:'neutral', v:'N/A', e:'No issues in the last 6 months.' }
    : closeRatio >= 0.95 ? { tone:'good', v:'Keeping up', e:`Closed ${n0(closed6)} of ${n0(opened6)} new issues in 6 months.` }
    : closeRatio >= 0.6 ? { tone:'warn', v:'Falling behind', e:`Closed ${n0(closed6)} for every ${n0(opened6)} opened in 6 months. Backlog ${signed(backlog6)}.` }
    : { tone:'bad', v:'Not answering', e:`Closed ${n0(closed6)} of ${n0(opened6)} new issues in 6 months. Backlog ${signed(backlog6)}.` };
  const relRatio = relDays !== null && medGap ? relDays/medGap : null;
  const shipping = !lastRel ? { tone:'neutral', v:'No releases', e:'Uses the default branch only.' }
    : relRatio <= 1.5 ? { tone:'good', v:'On its usual pace', e:`Last release ${ago(lastRel.t)}. Usually every ${Math.round(medGap)} days.` }
    : { tone:'warn', v:`Overdue, ${relRatio.toFixed(1)}× its usual gap`, e:`Last release ${ago(lastRel.t)}. Usually every ${Math.round(medGap)} days.` };
  const people = single ? { tone:'warn', v:'Depends on one person', e:`${Math.round(top*100)}% of last year’s commits came from ${D.contrib[0].login}.` }
    : { tone:'good', v:`Shared by ${for80} people`, e:`${for80} people made 80% of last year’s commits.` };
  const findings = [['Is interest real and growing?', momentum], ['Is someone still working on it?', maintenance], ['Will my bug reports get answered?', support], ['Does it ship on a rhythm?', shipping], ['What if one person leaves?', people]];

  const fit = [], watch = [];
  if (status === 'Active') fit.push('You need something that is maintained today and should be for the next year.');
  if (!single) fit.push('You want work spread across several people, not one.');
  if (shipping.tone === 'good') fit.push(`You like predictable upgrades: a release about every ${Math.round(medGap)} days.`);
  if (momentum.tone === 'good') fit.push('You want a growing community, which usually means more answers and examples online.');
  if (p.ownerType === 'Organization') fit.push(`It is published by an organization (${p.owner}), not one personal account.`);
  if (status === 'Quiet') fit.push('You only need the current version as it is and can fix problems yourself.');
  if (support.tone !== 'good' && support.tone !== 'neutral') watch.push(`You expect quick help: issues are being opened faster than they are closed (${growStreak} months in a row).`);
  if (single) watch.push('Your team can’t take over if the main maintainer stops.');
  if (spike) watch.push('You are choosing it for its star count: most recent stars arrived in a sudden burst with little other activity.');
  if (p.license === 'NOASSERTION') watch.push('You need legal clarity: the license is not a standard one.');
  if (scripted) watch.push(`You install skills without reading them: ${scripted} of ${p.skills.length} skills run scripts on your computer.`);
  if (shipping.tone === 'warn') watch.push('You need regular fixes: the next release is well past its usual date.');
  if (status === 'Quiet') watch.push(`You need security fixes or new features: the last commit was ${ago(lastCommit)}.`);
  if (!watch.length) watch.push('Nothing stood out in the data we have.');
  if (!fit.length) fit.push('You are only evaluating it, and will check again later.');

  return { status, statusTone, lastCommit, lastRel, relDays, g7, g30, prev30, momChange, commits90, commitsPrev90, devChange, spike, base12,
    top, for80, single, opened6, closed6, closeRatio, backlog6, growStreak, prO, prM, mergeRate, medGap, rel12, gaps,
    checks, issuesCount, findings, fit, watch, scripted };
}

/* ---------- chart primitives ---------- */
const css = (name) => getComputedStyle(document.documentElement).getPropertyValue(name).trim();
function frame(el, pad){ const w = Math.max(240, el.clientWidth), h = el.clientHeight || 200; return { w, h, x0: pad.l, x1: w - pad.r, y0: pad.t, y1: h - pad.b }; }
function yAxis(F, ticks, sy, fmt = compact){ return ticks.map(v => `<line x1="${F.x0}" x2="${F.x1}" y1="${sy(v)}" y2="${sy(v)}" style="stroke:var(--line-2)"/><text x="${F.x0-8}" y="${sy(v)+4}" text-anchor="end" style="fill:var(--ink-3);font-size:11px">${fmt(v)}</text>`).join(''); }
function xLabels(F, items, sx, fmt, k = 5){ if (!items.length) return ''; const idx = new Set(); for (let j = 0; j < k; j++) idx.add(Math.round(j*(items.length-1)/(k-1))); return [...idx].map(i => `<text x="${sx(i)}" y="${F.y1+18}" text-anchor="${i === 0 ? 'start' : i === items.length-1 ? 'end' : 'middle'}" style="fill:var(--ink-3);font-size:11px">${fmt(items[i], i)}</text>`).join(''); }
function tipper(el){ let tip = el.querySelector('.tip'); if (!tip) { tip = document.createElement('div'); tip.className = 'tip'; tip.hidden = true; el.appendChild(tip); } return tip; }
function hover(el, F, count, sx, render){
  const tip = tipper(el); let cur = -1;
  const show = (i) => { cur = Math.max(0, Math.min(count-1, i)); const o = render(cur); tip.innerHTML = o.html; tip.hidden = false;
    const tw = tip.offsetWidth; let x = sx(cur); x = Math.max(tw/2, Math.min(F.w - tw/2, x)); tip.style.left = x + 'px'; tip.style.top = Math.max(o.y, 40) + 'px';
    const c = el.querySelector('.cursor'); if (c) { c.setAttribute('x1', sx(cur)); c.setAttribute('x2', sx(cur)); c.style.display = ''; }
    const dot = el.querySelector('.cdot'); if (dot && o.dy !== undefined) { dot.setAttribute('cx', sx(cur)); dot.setAttribute('cy', o.dy); dot.style.display = ''; } };
  const hide = () => { tip.hidden = true; const c = el.querySelector('.cursor'); if (c) c.style.display = 'none'; const dot = el.querySelector('.cdot'); if (dot) dot.style.display = 'none'; };
  const pick = (cx) => { const rect = el.getBoundingClientRect(); const x = cx - rect.left; let best = 0, bd = Infinity; for (let i = 0; i < count; i++) { const dd = Math.abs(sx(i) - x); if (dd < bd) { bd = dd; best = i; } } return best; };
  el.onmousemove = (e) => show(pick(e.clientX));
  el.onmouseleave = hide;
  el.ontouchstart = (e) => show(pick(e.touches[0].clientX));
  el.onkeydown = (e) => { if (e.key === 'ArrowRight') { show(cur < 0 ? count-1 : cur+1); e.preventDefault(); } else if (e.key === 'ArrowLeft') { show(cur < 0 ? count-1 : cur-1); e.preventDefault(); } else if (e.key === 'Home') { show(0); e.preventDefault(); } else if (e.key === 'End') { show(count-1); e.preventDefault(); } else if (e.key === 'Escape') hide(); };
  el.onblur = hide;
}


window.GA = { $, KNOWN, recordFor, DAY, NOW, LAST_SUN, MON, d, fDay, fDayY, fMonY, n0, compact, signed, pct, sum, median, ago, esc, rng, niceMax, niceTicks, ICON, TONE_ICON, toneIcon, PROFILES, TEMPLATE, hashStr, readRecord, profileFor, build, analyse, css, frame, yAxis, xLabels, tipper, hover };
})();
