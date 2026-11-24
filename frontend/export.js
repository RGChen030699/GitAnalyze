/* GitAnalyze export: download a table as CSV or Excel (.xlsx), plus the Download menu.
   No libraries: the .xlsx is a small zip (stored, not compressed) written here. */
(() => {
  'use strict';

  /* ---------- CSV ---------- */
  function toCsv(head, rows, source) {
    const q = (v) => (typeof v === 'number' ? String(v) : '"' + String(v == null ? '' : v).replace(/"/g, '""') + '"');
    const lines = [head, ...rows].map((r) => r.map(q).join(','));
    if (source) lines.push('', q(source));
    return '﻿' + lines.join('\r\n') + '\r\n'; // BOM so Excel reads UTF-8
  }

  /* ---------- XLSX ---------- */
  const xml = (s) => String(s).replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]))
    .replace(/[\u0000-\u0008\u000B\u000C\u000E-\u001F]/g, '');
  const colName = (i) => { let s = ''; i++; while (i) { const m = (i - 1) % 26; s = String.fromCharCode(65 + m) + s; i = Math.floor((i - 1) / 26); } return s; };
  function cell(v, ref, style) {
    const st = style ? ' s="' + style + '"' : '';
    if (v === null || v === undefined || v === '') return '<c r="' + ref + '"' + st + '/>';
    if (typeof v === 'number' && isFinite(v)) return '<c r="' + ref + '"' + st + '><v>' + v + '</v></c>';
    return '<c r="' + ref + '"' + st + ' t="inlineStr"><is><t xml:space="preserve">' + xml(v) + '</t></is></c>';
  }
  function sheetXml(head, rows, source) {
    const all = [head, ...rows];
    const widths = head.map((_, c) => Math.min(60, Math.max(8, ...all.map((r) => String(r[c] == null ? '' : r[c]).length)) + 2));
    let out = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>' +
      '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">' +
      '<sheetViews><sheetView workbookViewId="0"><pane ySplit="1" topLeftCell="A2" activePane="bottomLeft" state="frozen"/></sheetView></sheetViews>' +
      '<cols>' + widths.map((w, i) => '<col min="' + (i + 1) + '" max="' + (i + 1) + '" width="' + w + '" customWidth="1"/>').join('') + '</cols><sheetData>';
    all.forEach((r, ri) => {
      out += '<row r="' + (ri + 1) + '">' + r.map((v, ci) => cell(v, colName(ci) + (ri + 1), ri === 0 ? 1 : 0)).join('') + '</row>';
    });
    if (source) { const rr = all.length + 2; out += '<row r="' + rr + '">' + cell(source, 'A' + rr, 2) + '</row>'; }
    return out + '</sheetData></worksheet>';
  }
  function xlsxFiles(head, rows, source, sheetName) {
    const name = xml(String(sheetName || 'Data').replace(/[\\/?*[\]:]/g, ' ').slice(0, 31));
    return {
      '[Content_Types].xml': '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/><Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/><Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/></Types>',
      '_rels/.rels': '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/></Relationships>',
      'xl/workbook.xml': '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets><sheet name="' + name + '" sheetId="1" r:id="rId1"/></sheets></workbook>',
      'xl/_rels/workbook.xml.rels': '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/><Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/></Relationships>',
      'xl/styles.xml': '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><fonts count="3"><font><sz val="11"/><name val="Calibri"/></font><font><b/><sz val="11"/><name val="Calibri"/></font><font><i/><sz val="10"/><color rgb="FF5E645C"/><name val="Calibri"/></font></fonts><fills count="3"><fill><patternFill patternType="none"/></fill><fill><patternFill patternType="gray125"/></fill><fill><patternFill patternType="solid"><fgColor rgb="FFE3E6FB"/><bgColor indexed="64"/></patternFill></fill></fills><borders count="1"><border><left/><right/><top/><bottom/><diagonal/></border></borders><cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs><cellXfs count="3"><xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0"/><xf numFmtId="0" fontId="1" fillId="2" borderId="0" xfId="0" applyFont="1" applyFill="1"/><xf numFmtId="0" fontId="2" fillId="0" borderId="0" xfId="0" applyFont="1"/></cellXfs><cellStyles count="1"><cellStyle name="Normal" xfId="0" builtinId="0"/></cellStyles></styleSheet>',
      'xl/worksheets/sheet1.xml': sheetXml(head, rows, source)
    };
  }
  /* minimal zip writer (method 0 = stored) */
  const CRC = (() => { const t = new Uint32Array(256); for (let n = 0; n < 256; n++) { let c = n; for (let k = 0; k < 8; k++) c = c & 1 ? 0xEDB88320 ^ (c >>> 1) : c >>> 1; t[n] = c >>> 0; } return t; })();
  const crc32 = (b) => { let c = 0xFFFFFFFF; for (let i = 0; i < b.length; i++) c = CRC[(c ^ b[i]) & 0xFF] ^ (c >>> 8); return (c ^ 0xFFFFFFFF) >>> 0; };
  function zip(files) {
    const enc = new TextEncoder(), parts = [], central = []; let offset = 0;
    const u16 = (v) => [v & 0xFF, (v >>> 8) & 0xFF], u32 = (v) => [v & 0xFF, (v >>> 8) & 0xFF, (v >>> 16) & 0xFF, (v >>> 24) & 0xFF];
    for (const [path, text] of Object.entries(files)) {
      const name = enc.encode(path), data = enc.encode(text), crc = crc32(data);
      const local = new Uint8Array([0x50, 0x4B, 0x03, 0x04, ...u16(20), ...u16(0x0800), ...u16(0), ...u16(0), ...u16(0x21), ...u32(crc), ...u32(data.length), ...u32(data.length), ...u16(name.length), ...u16(0)]);
      parts.push(local, name, data);
      central.push(new Uint8Array([0x50, 0x4B, 0x01, 0x02, ...u16(20), ...u16(20), ...u16(0x0800), ...u16(0), ...u16(0), ...u16(0x21), ...u32(crc), ...u32(data.length), ...u32(data.length), ...u16(name.length), ...u16(0), ...u16(0), ...u16(0), ...u16(0), ...u32(0), ...u32(offset)]), name);
      offset += local.length + name.length + data.length;
    }
    const cdSize = central.reduce((s, p) => s + p.length, 0), count = Object.keys(files).length;
    const end = new Uint8Array([0x50, 0x4B, 0x05, 0x06, ...u16(0), ...u16(0), ...u16(count), ...u16(count), ...u32(cdSize), ...u32(offset), ...u16(0)]);
    return new Blob([...parts, ...central, end], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });
  }

  function save(blob, filename) {
    const a = document.createElement('a'); a.href = URL.createObjectURL(blob); a.download = filename;
    document.body.appendChild(a); a.click(); a.remove(); setTimeout(() => URL.revokeObjectURL(a.href), 4000);
  }
  /** format: 'csv' | 'xlsx'. rows: arrays of numbers/strings. source: one line of provenance (F6). */
  function download({ format, filename, head, rows, source, sheet }) {
    if (format === 'xlsx') save(zip(xlsxFiles(head, rows, source, sheet)), filename + '.xlsx');
    else save(new Blob([toCsv(head, rows, source)], { type: 'text/csv;charset=utf-8' }), filename + '.csv');
  }

  /* ---------- Download menu (menu button pattern) ---------- */
  const ICON_DOWN = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 4v11M7 10l5 5 5-5M5 20h14"/></svg>';
  const CHEV = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M6 9l6 6 6-6"/></svg>';
  const CSS = '.dl{position:relative;display:inline-flex}' +
    '.dl-menu{position:absolute;right:0;top:calc(100% + 6px);min-width:240px;background:var(--surface);border:1px solid var(--line);border-radius:14px;box-shadow:var(--shadow);padding:6px;z-index:45}' +
    '.dl-menu button{display:grid;grid-template-columns:auto 1fr;gap:0 10px;align-items:center;width:100%;min-height:44px;padding:8px 10px;border:none;border-radius:10px;background:transparent;text-align:left;cursor:pointer;color:var(--ink);font:inherit}' +
    '.dl-menu button:hover,.dl-menu button:focus-visible{background:var(--accent-soft)}' +
    '.dl-menu b{font-weight:600;font-size:14px}.dl-menu small{grid-column:2;font-size:12px;color:var(--ink-3)}' +
    '.dl-menu .ext{grid-row:1/3;display:grid;place-items:center;width:36px;height:28px;border-radius:6px;background:var(--surface-2);color:var(--ink-2);font:600 11px/1 var(--mono)}';
  function mount(btn, onPick) {
    if (!document.getElementById('dl-css')) { const st = document.createElement('style'); st.id = 'dl-css'; st.textContent = CSS; document.head.appendChild(st); }
    const wrap = document.createElement('span'); wrap.className = 'dl'; btn.replaceWith(wrap); wrap.appendChild(btn);
    btn.innerHTML = ICON_DOWN + 'Download' + CHEV;
    btn.setAttribute('aria-haspopup', 'menu'); btn.setAttribute('aria-expanded', 'false');
    const menu = document.createElement('div'); menu.className = 'dl-menu'; menu.setAttribute('role', 'menu'); menu.hidden = true;
    menu.setAttribute('aria-label', 'Download as');
    menu.innerHTML = '<button type="button" role="menuitem" data-fmt="csv"><span class="ext">CSV</span><b>Download as CSV</b><small>Plain text, opens anywhere</small></button>' +
      '<button type="button" role="menuitem" data-fmt="xlsx"><span class="ext">XLSX</span><b>Download as Excel</b><small>Header row frozen, columns sized</small></button>';
    wrap.appendChild(menu);
    const items = () => [...menu.querySelectorAll('[role="menuitem"]')];
    const open = (focusIdx) => { menu.hidden = false; btn.setAttribute('aria-expanded', 'true'); if (focusIdx !== undefined) items()[focusIdx].focus(); };
    const close = (refocus) => { if (menu.hidden) return; menu.hidden = true; btn.setAttribute('aria-expanded', 'false'); if (refocus) btn.focus(); };
    btn.addEventListener('click', (e) => { e.stopPropagation(); menu.hidden ? open(0) : close(); });
    btn.addEventListener('keydown', (e) => { if (e.key === 'ArrowDown') { e.preventDefault(); open(0); } else if (e.key === 'ArrowUp') { e.preventDefault(); open(1); } });
    menu.addEventListener('keydown', (e) => {
      const list = items(), i = list.indexOf(document.activeElement);
      if (e.key === 'ArrowDown') { e.preventDefault(); list[(i + 1) % list.length].focus(); }
      else if (e.key === 'ArrowUp') { e.preventDefault(); list[(i - 1 + list.length) % list.length].focus(); }
      else if (e.key === 'Home') { e.preventDefault(); list[0].focus(); }
      else if (e.key === 'End') { e.preventDefault(); list[list.length - 1].focus(); }
      else if (e.key === 'Escape') { e.preventDefault(); e.stopPropagation(); close(true); }
      else if (e.key === 'Tab') close(false);
    });
    menu.addEventListener('click', (e) => { const b = e.target.closest('[data-fmt]'); if (!b) return; e.stopPropagation(); close(true); onPick(b.dataset.fmt); });
    document.addEventListener('click', (e) => { if (!wrap.contains(e.target)) close(false); });
  }

  window.GAExport = { download, mount, toCsv };
})();
