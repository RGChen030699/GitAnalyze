/* GitAnalyze report helpers: formatting, icons and chart primitives shared by the report and
   compare pages. Moved unchanged from the former sample.js; the sample data and the rules it held
   are gone (rules now come from the API, CLAUDE.md decision 6). Needs data.js loaded first. */
(() => {
'use strict';
/* ---------- helpers ---------- */
const $ = (s, r = document) => r.querySelector(s);
const DAY = 864e5;
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
const ago = (t) => window.GAData.agoLabel(t, Date.now());
const esc = (s) => String(s).replace(/[&<>"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
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
window.GA = { $, DAY, MON, d, fDay, fDayY, fMonY, n0, compact, signed, pct, sum, median, ago, esc, niceMax, niceTicks, ICON, TONE_ICON, toneIcon, css, frame, yAxis, xLabels, tipper, hover };
})();
