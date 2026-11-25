/* A dropdown that always opens below its box, on computers with a mouse or trackpad.
   macOS draws native <select> menus on top of the box; this replaces them there. Touch devices
   keep the native picker, which suits a thumb. The real <select> stays in the page, hidden, and
   holds the value: picking an option sets it and fires "change", so page code is unchanged.
   Keyboard: Enter, Space or arrows open; arrows, Home and End move; Enter picks; Escape closes;
   typing a letter jumps to the next option starting with it. */
(function () {
  const finePointer = () => window.matchMedia('(hover: hover) and (pointer: fine)').matches;
  let uid = 0;

  function enhance(select) {
    if (!select || select.dataset.gaSelect || !finePointer()) return;
    select.dataset.gaSelect = '1';
    const id = 'dd' + (++uid);
    const wrap = document.createElement('div');
    wrap.className = 'dd';
    const button = document.createElement('button');
    button.type = 'button';
    button.className = 'dd-btn';
    button.id = id + '-btn';
    button.setAttribute('aria-haspopup', 'listbox');
    button.setAttribute('aria-expanded', 'false');
    const labelId = select.getAttribute('aria-labelledby');
    if (labelId) button.setAttribute('aria-labelledby', labelId + ' ' + button.id);
    const list = document.createElement('ul');
    list.className = 'dd-list';
    list.id = id + '-list';
    list.setAttribute('role', 'listbox');
    list.tabIndex = -1;
    list.hidden = true;
    if (labelId) list.setAttribute('aria-labelledby', labelId);
    button.setAttribute('aria-controls', list.id);
    select.after(wrap);
    wrap.append(button, list);
    select.hidden = true;
    select.tabIndex = -1;
    let active = 0;

    const options = () => Array.from(list.children);
    function sync() {
      list.innerHTML = Array.from(select.options).map((o, i) =>
        '<li role="option" id="' + id + '-' + i + '" data-value="' + o.value.replace(/"/g, '&quot;') + '" aria-selected="' + (o.selected) + '">' +
        o.textContent.replace(/[&<>]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;' }[c])) + '</li>').join('');
      const chosen = select.options[select.selectedIndex];
      button.textContent = chosen ? chosen.textContent : '';
      fitWidth();
    }
    /* The box is as wide as its longest option, and the menu matches the box exactly. */
    const ruler = document.createElement('canvas').getContext('2d');
    function fitWidth() {
      const style = getComputedStyle(button);
      ruler.font = style.fontWeight + ' ' + style.fontSize + ' ' + style.fontFamily;
      const longest = Math.max(0, ...Array.from(select.options).map((o) => ruler.measureText(o.textContent).width));
      // the box's text is centred between 12px on the left and the arrow (34px); the menu's text
      // sits 30px in (room for the check) and 12px from the right, inside 6px padding; plus borders
      button.style.minWidth = Math.ceil(longest + Math.max(12 + 34, 30 + 12 + 6 * 2) + 2) + 'px';
    }
    function highlight(i) {
      const items = options();
      if (!items.length) return;
      active = Math.max(0, Math.min(items.length - 1, i));
      items.forEach((li, j) => li.classList.toggle('active', j === active));
      list.setAttribute('aria-activedescendant', items[active].id);
      items[active].scrollIntoView({ block: 'nearest' });
    }
    /* Fixed to the window, so panels with overflow:hidden can't clip it; always below the box. */
    function place() {
      const r = button.getBoundingClientRect();
      const top = r.bottom + 6;
      list.style.top = top + 'px';
      list.style.left = r.left + 'px';
      list.style.width = r.width + 'px';
      list.style.maxHeight = Math.max(160, Math.min(320, window.innerHeight - top - 12)) + 'px';
    }
    function open() {
      if (!list.hidden) return;
      sync();
      place();
      list.hidden = false;
      button.setAttribute('aria-expanded', 'true');
      highlight(Math.max(0, select.selectedIndex));
      list.focus();
    }
    function close(refocus) {
      if (list.hidden) return;
      list.hidden = true;
      button.setAttribute('aria-expanded', 'false');
      if (refocus) button.focus();
    }
    function pick(i) {
      const item = options()[i];
      if (!item) return;
      const changed = select.value !== item.dataset.value;
      select.value = item.dataset.value;
      sync();
      close(true);
      if (changed) select.dispatchEvent(new Event('change', { bubbles: true }));
    }

    button.addEventListener('click', () => (list.hidden ? open() : close(true)));
    button.addEventListener('keydown', (e) => {
      if (['ArrowDown', 'ArrowUp', 'Enter', ' '].includes(e.key)) { e.preventDefault(); open(); }
    });
    list.addEventListener('click', (e) => {
      const li = e.target.closest('li');
      if (li) pick(options().indexOf(li));
    });
    list.addEventListener('mousemove', (e) => {
      const li = e.target.closest('li');
      if (li) highlight(options().indexOf(li));
    });
    list.addEventListener('keydown', (e) => {
      const n = options().length;
      if (e.key === 'ArrowDown') { e.preventDefault(); highlight(active + 1); }
      else if (e.key === 'ArrowUp') { e.preventDefault(); highlight(active - 1); }
      else if (e.key === 'Home') { e.preventDefault(); highlight(0); }
      else if (e.key === 'End') { e.preventDefault(); highlight(n - 1); }
      else if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); pick(active); }
      else if (e.key === 'Escape') { e.preventDefault(); close(true); }
      else if (e.key === 'Tab') { close(false); }
      else if (e.key.length === 1 && /\S/.test(e.key)) {
        const items = options(), k = e.key.toLowerCase();
        for (let step = 1; step <= n; step++) {
          const j = (active + step) % n;
          if (items[j].textContent.toLowerCase().startsWith(k)) { highlight(j); break; }
        }
      }
    });
    const label = select.id && document.querySelector('label[for="' + select.id + '"]');
    if (label) label.addEventListener('click', (e) => { e.preventDefault(); button.focus(); open(); });
    window.addEventListener('scroll', () => { if (!list.hidden) place(); }, true);
    window.addEventListener('resize', () => { if (!list.hidden) place(); });
    document.addEventListener('click', (e) => { if (!wrap.contains(e.target) && !(label && label.contains(e.target))) close(false); });
    // Page code rewrites the options or sets .value directly; keep the button in step.
    new MutationObserver(sync).observe(select, { childList: true, subtree: true, characterData: true });
    select._gaSync = sync;
    sync();
  }

  /** Call after setting select.value in code, so the button shows the new choice. */
  function refresh(select) { if (select && select._gaSync) select._gaSync(); }

  window.GASelect = { enhance, refresh };
})();
