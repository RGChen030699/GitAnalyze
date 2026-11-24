/* GitAnalyze compare list: up to 3 repositories, kept in this browser so it follows you
   from the rankings to a report to /compare (F5). Each entry is the row record the report needs. */
(() => {
  'use strict';
  const KEY = 'ga-compare', MAX = 3;
  const FIELDS = ['owner', 'name', 'status', 'lang', 'stars', 'pushed', 'contributors', 'ownerType', 'ai', 'spike', 'trending', 'desc'];
  let mem = [];
  const id = (r) => (r.owner + '/' + r.name).toLowerCase();
  function load() { try { const v = JSON.parse(localStorage.getItem(KEY) || '[]'); if (Array.isArray(v)) mem = v.filter((r) => r && r.owner && r.name).slice(0, MAX); } catch (_) {} return mem; }
  function save(list) { mem = list.slice(0, MAX); try { localStorage.setItem(KEY, JSON.stringify(mem)); } catch (_) {} listeners.forEach((f) => f(mem)); }
  const listeners = [];
  const pick = (r) => { const o = {}; FIELDS.forEach((k) => { if (r[k] !== undefined) o[k] = r[k]; }); return o; };

  const api = {
    MAX,
    list: () => load().slice(),
    ids: () => load().map(id),
    has: (full) => load().some((r) => id(r) === full.toLowerCase()),
    /** returns 'added' | 'full' | 'exists' */
    add(rec) { const l = load(); if (l.some((r) => id(r) === id(rec))) return 'exists'; if (l.length >= MAX) return 'full'; save([...l, pick(rec)]); return 'added'; },
    remove(full) { save(load().filter((r) => id(r) !== full.toLowerCase())); },
    set(recs) { save(recs.map(pick)); },
    find: (full) => load().find((r) => id(r) === full.toLowerCase()) || null,
    url: (list) => '/compare?repos=' + (list || load()).map((r) => encodeURIComponent(r.owner) + '/' + encodeURIComponent(r.name)).join(','),
    onChange(f) { listeners.push(f); },

    /** Floating compare bar (design.md 7.13) for pages that don't draw their own. */
    mountTray(toast) {
      if (!document.getElementById('cmp-css')) {
        const st = document.createElement('style'); st.id = 'cmp-css';
        st.textContent = '.cmp-tray{position:fixed;left:50%;transform:translateX(-50%);bottom:16px;z-index:30;display:flex;flex-wrap:wrap;align-items:center;gap:10px 12px;padding:8px 8px 8px 18px;border-radius:16px;background:var(--ink);color:var(--bg);box-shadow:0 10px 30px rgba(0,0,0,.25);max-width:calc(100% - 32px);padding-bottom:max(8px,env(safe-area-inset-bottom))}' +
          '.cmp-tray[hidden]{display:none}.cmp-tray>b{font-size:14px;font-weight:600}' +
          '.cmp-tray .c{display:inline-flex;align-items:center;gap:4px;padding:3px 4px 3px 10px;border-radius:999px;background:rgba(255,255,255,.14);font-family:var(--mono);font-size:12px}' +
          '.cmp-tray .c button{border:none;background:transparent;color:inherit;cursor:pointer;width:28px;height:28px;display:grid;place-items:center;border-radius:50%}' +
          '.cmp-tray .c button:hover{background:rgba(255,255,255,.18)}' +
          '.cmp-tray .go{display:inline-flex;align-items:center;min-height:36px;padding:0 14px;border-radius:10px;background:var(--bg);color:var(--ink);font-weight:600;font-size:14px;text-decoration:none;border:none}' +
          '.cmp-tray .go[aria-disabled="true"]{opacity:.6;pointer-events:none}' +
          '.cmp-tray .more{color:var(--bg);font-size:13px;opacity:.85}';
        document.head.appendChild(st);
      }
      const tray = document.createElement('div'); tray.className = 'cmp-tray'; tray.setAttribute('role', 'region'); tray.setAttribute('aria-label', 'Compare list');
      document.body.appendChild(tray);
      const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
      const X = '<svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" aria-hidden="true"><path d="M6 6l12 12M18 6L6 18"/></svg>';
      function render(list) {
        tray.hidden = !list.length;
        if (!list.length) return;
        tray.innerHTML = '<b>Compare</b>' + list.map((r) => '<span class="c">' + esc(r.name) + '<button type="button" data-rm="' + esc(r.owner + '/' + r.name) + '" aria-label="Remove ' + esc(r.owner + '/' + r.name) + ' from compare">' + X + '</button></span>').join('') +
          (list.length > 1 ? '<a class="go" href="' + api.url(list) + '">Compare ' + list.length + '</a>' : '<a class="more" href="/">Add one more from the rankings</a>');
      }
      tray.addEventListener('click', (e) => { const b = e.target.closest('[data-rm]'); if (!b) return; api.remove(b.dataset.rm); if (toast) toast('Removed ' + b.dataset.rm + ' from compare.'); });
      api.onChange(render);
      window.addEventListener('storage', (e) => { if (e.key === KEY) render(load()); });
      render(load());
      return { render };
    }
  };
  window.GACompare = api;
})();
