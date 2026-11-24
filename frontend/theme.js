/* Theme button label: shows the mode a click switches to ("Dark mode" / "Light mode").
   The pages toggle data-theme on <html>; this keeps the words and the screen-reader label in step. */
(() => {
  'use strict';
  const btn = document.getElementById('themeBtn'); if (!btn) return;
  const st = document.createElement('style');
  st.textContent = '#themeBtn{width:auto;gap:8px;padding:0 12px;font-size:14px;font-weight:500;white-space:nowrap;border:1px solid var(--line)}' +
    '.nav a{gap:8px}.nav .nav-count{display:inline-grid;place-items:center;min-width:22px;height:22px;padding:0 6px;border-radius:999px;background:var(--accent);color:var(--accent-ink);font-size:12px;font-weight:600}.nav .nav-count[hidden]{display:none}' +
    '#themeBtn svg{width:18px;height:18px;flex:none}@media (max-width:420px){#themeBtn .tl{display:none}#themeBtn{width:44px;padding:0}}';
  document.head.appendChild(st);
  btn.style.display = 'inline-flex'; btn.style.alignItems = 'center';
  const label = document.createElement('span'); label.className = 'tl'; btn.appendChild(label);
  const mq = window.matchMedia('(prefers-color-scheme: dark)');
  const isDark = () => { const t = document.documentElement.dataset.theme; return t ? t === 'dark' : mq.matches; };
  function sync() { const next = isDark() ? 'Light mode' : 'Dark mode'; label.textContent = next; btn.setAttribute('aria-label', 'Switch to ' + next.toLowerCase()); }
  new MutationObserver(sync).observe(document.documentElement, { attributes: true, attributeFilter: ['data-theme'] });
  if (mq.addEventListener) mq.addEventListener('change', sync);
  sync();
})();
