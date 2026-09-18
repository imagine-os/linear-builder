/* ===== v4 views (v5: cycle, points, initiative and round-4 filters): shared filters + objects map, lanes skill tree, radial tree, images, icons, objects 3D, radial 3D ===== */
const V = (() => {
  const canon = D.issues.filter(i => i.n >= 13 && i.s !== 'Duplicate');
  const projOrder = D.projects.map(p => p.key);
  const pIdx = Object.fromEntries(projOrder.map((k, i) => [k, i]));
  const SK = { Backlog: 'backlog', 'Ready for Claude': 'ready', 'In Progress': 'progress', 'In Review': 'review', 'Needs Justin': 'justin', Done: 'done', Triage: 'triage' };
  const skey = i => (i.d && i.s === 'Backlog') ? 'deferred' : (SK[i.s] || 'backlog');
  const stName = { triage: 'Triage', backlog: 'Backlog', ready: 'Ready for Claude', progress: 'In Progress', review: 'In Review', justin: 'Needs Justin', done: 'Done', deferred: 'Deferred (Backlog, v0.2)' };
  const CYCLES = (D.cycles && D.cycles.list) || [];
  const ESTS = Object.keys((D.estimates && D.estimates.histogram) || {}).filter(k => k !== 'none').map(Number).sort((a, b) => a - b);
  const INIS = (D.initiatives || []).map(x => x.short);
  const TYPES = ['Research', 'Spec', 'Build', 'Review', 'Infra', 'Docs'];
  const MODELS = ['Fable 5.1', 'Opus 5', 'Sonnet 5', 'Haiku 4.5'];
  const EFFS = ['low', 'medium', 'high', 'max'];
  const PH = { P0: 0, P1: 1, P2: 2 };
  const hue = k => (P[k] && P[k].color) || '#8A95A8';
  const short = k => (P[k] && P[k].short) || k;
  const blockersOf = Object.fromEntries(canon.map(i => [i.id, i.bb.filter(b => byId[b] && byId[b].s !== 'Duplicate')]));
  const blocksOf = {}; for (const i of canon) for (const b of blockersOf[i.id]) (blocksOf[b] = blocksOf[b] || []).push(i.id);
  const hash = s => { let h = 2166136261; for (let k = 0; k < s.length; k++) { h ^= s.charCodeAt(k); h = Math.imul(h, 16777619); } return h >>> 0; };
  const rng = seed => { let a = seed || 1; return () => { a = (a * 1664525 + 1013904223) >>> 0; return a / 4294967296; }; };

  /* ---- glyphs (type -> shape) and icons (type, model) ---- */
  const shape = (ty, r) => {
    const h = r * 0.866;
    switch (ty) {
      case 'Build': return `M${-r},${-r}h${2 * r}v${2 * r}h${-2 * r}z`;
      case 'Spec': return `M0,${-r * 1.15}L${r * 1.15},0L0,${r * 1.15}L${-r * 1.15},0z`;
      case 'Review': return `M0,${-r * 1.2}L${r * 1.1},${r * 0.75}L${-r * 1.1},${r * 0.75}z`;
      case 'Infra': return `M${r},0L${r / 2},${h}L${-r / 2},${h}L${-r},0L${-r / 2},${-h}L${r / 2},${-h}z`;
      case 'Docs': return `M${-r * 1.25},${-r * 0.7}h${2.5 * r}v${1.4 * r}h${-2.5 * r}z`;
      default: return `M${-r},0a${r},${r} 0 1,0 ${2 * r},0a${r},${r} 0 1,0 ${-2 * r},0z`;
    }
  };
  const ICON = {
    Research: '<circle cx="10.5" cy="10.5" r="6"/><path d="M15 15l5.5 5.5"/>',
    Spec: '<path d="M6 3h8l4 4v14H6z"/><path d="M14 3v4h4M9 12h6M9 16h6"/>',
    Build: '<path d="M8 8L3 12l5 4M16 8l5 4-5 4M14 5l-4 14"/>',
    Review: '<path d="M2 12s3.5-6 10-6 10 6 10 6-3.5 6-10 6S2 12 2 12z"/><circle cx="12" cy="12" r="2.6"/>',
    Infra: '<rect x="3" y="4" width="18" height="6" rx="1.5"/><rect x="3" y="14" width="18" height="6" rx="1.5"/><path d="M7 7h.01M7 17h.01"/>',
    Docs: '<path d="M4 5.5A2.5 2.5 0 0 1 6.5 3H20v16H6.5A2.5 2.5 0 0 0 4 21z"/><path d="M4 18.5A2.5 2.5 0 0 1 6.5 16H20"/>'
  };
  const MICON = {
    'Fable 5.1': '<path d="M12 2c.6 5.5 4.5 9.4 10 10-5.5.6-9.4 4.5-10 10-.6-5.5-4.5-9.4-10-10 5.5-.6 9.4-4.5 10-10z"/>',
    'Opus 5': '<path d="M12 2.5l8.2 4.75v9.5L12 21.5l-8.2-4.75v-9.5z"/><circle cx="12" cy="12" r="2.2"/>',
    'Sonnet 5': '<path d="M12 3l9.5 17h-19z"/>',
    'Haiku 4.5': '<circle cx="12" cy="12" r="6"/>'
  };
  const icon = (paths, cls) => `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"${cls ? ` class="${cls}"` : ''}>${paths || ''}</svg>`;
  const typeIcon = ty => icon(ICON[ty] || ICON.Research);
  const modelIcon = m => icon(MICON[m] || '<path d="M6 12h12"/>');
  const effDots = e => { const n = { low: 1, medium: 2, high: 3, max: 4 }[e] || 0; return `<span class="eff" title="effort ${esc(e || 'n/a')}">${[1, 2, 3].map(k => `<i class="${k <= n ? 'on' : ''}"></i>`).join('')}</span>`; };

  /* ---- filter state ---- */
  const F = { p: '', ph: '', s: '', ty: '', m: '', e: '', sz: '', cy: '', est: '', ini: '', flag: '', sort: 'priority', q: '' };
  const sorters = {
    priority: (a, b) => (a.pr || 9) - (b.pr || 9) || a.n - b.n,
    milestone: (a, b) => (a.msd || '9').localeCompare(b.msd || '9') || a.n - b.n,
    blockers: (a, b) => blockersOf[b.id].length - blockersOf[a.id].length || a.n - b.n,
    blocks: (a, b) => (blocksOf[b.id] || []).length - (blocksOf[a.id] || []).length || a.n - b.n,
    title: (a, b) => a.t.localeCompare(b.t),
    id: (a, b) => a.n - b.n,
    points: (a, b) => (b.est || 0) - (a.est || 0) || a.n - b.n,
    due: (a, b) => (a.due || '9').localeCompare(b.due || '9') || a.n - b.n
  };
  function filtered() {
    const q = F.q.toLowerCase();
    return canon.filter(i => (!F.p || i.p === F.p) && (!F.ph || i.ph === F.ph) && (!F.s || skey(i) === F.s) && (!F.ty || i.ty === F.ty) && (!F.m || i.m === F.m) && (!F.e || i.e === F.e) && (!F.sz || i.sz === F.sz)
      && (!F.cy || (F.cy === 'none' ? !i.cy : String(i.cy) === F.cy)) && (!F.est || (F.est === 'none' ? i.est == null : String(i.est) === F.est)) && (!F.ini || i.ini === F.ini)
      && (!F.flag || (F.flag === 'ready' ? i.s === 'Ready for Claude' : F.flag === 'nodef' ? !i.d : F.flag === 'def' ? i.d : F.flag === 'leaf' ? !i.ch.length : F.flag === 'umb' ? !!i.ch.length : F.flag === 'new' ? (i.n >= 433 && !i.r4) : F.flag === 'r4' ? i.r4 : F.flag === 'triage' ? i.s === 'Triage' : F.flag === 'blocked' ? blockersOf[i.id].length > 0 : F.flag === 'free' ? blockersOf[i.id].length === 0 : true))
      && (!q || (i.id + ' ' + i.t).toLowerCase().includes(q))).sort(sorters[F.sort] || sorters.priority);
  }
  const fbar = $('#fbar');
  const opt = (v, l, cur) => `<option value="${esc(v)}"${v === cur ? ' selected' : ''}>${esc(l)}</option>`;
  function renderFbar() {
    fbar.innerHTML = `
      <label>Project <select id="f-p">${opt('', 'all', F.p)}${D.projects.map(p => opt(p.key, p.short, F.p)).join('')}</select></label>
      <label>Phase <select id="f-ph">${opt('', 'all', F.ph)}${['P0', 'P1', 'P2'].map(x => opt(x, x, F.ph)).join('')}</select></label>
      <label>State <select id="f-s">${opt('', 'all', F.s)}${Object.keys(stName).map(k => opt(k, stName[k], F.s)).join('')}</select></label>
      <label>Type <select id="f-ty">${opt('', 'all', F.ty)}${TYPES.map(x => opt(x, x, F.ty)).join('')}</select></label>
      <label>Model <select id="f-m">${opt('', 'all', F.m)}${MODELS.map(x => opt(x, x, F.m)).join('')}</select></label>
      <label>Effort <select id="f-e">${opt('', 'all', F.e)}${EFFS.map(x => opt(x, x, F.e)).join('')}</select></label>
      <label>Size <select id="f-sz">${opt('', 'all', F.sz)}${['S', 'M', 'L'].map(x => opt(x, x, F.sz)).join('')}</select></label>
      <label>Points <select id="f-est">${opt('', 'all', F.est)}${ESTS.map(x => opt(String(x), String(x), F.est)).join('')}${opt('none', 'no estimate', F.est)}</select></label>
      <label>Cycle <select id="f-cy">${opt('', 'all', F.cy)}${CYCLES.map(c => opt(String(c.number), `${c.short} · ${c.name.replace(/^C\d\s*/, '')}`, F.cy)).join('')}${opt('none', 'no cycle', F.cy)}</select></label>
      <label>Initiative <select id="f-ini">${opt('', 'all', F.ini)}${INIS.map(x => opt(x, x, F.ini)).join('')}</select></label>
      <label>Only <select id="f-flag">${opt('', 'everything', F.flag)}${opt('ready', 'Ready for Claude', F.flag)}${opt('r4', 'new in round 4', F.flag)}${opt('triage', 'in Triage', F.flag)}${opt('nodef', 'not deferred', F.flag)}${opt('def', 'Deferred', F.flag)}${opt('leaf', 'leaves (claimable)', F.flag)}${opt('umb', 'umbrellas', F.flag)}${opt('free', 'no open blockers', F.flag)}${opt('blocked', 'has blockers', F.flag)}${opt('new', 'round-3 module issues', F.flag)}</select></label>
      <span class="sep"></span>
      <label>Sort <select id="f-sort">${opt('priority', 'priority', F.sort)}${opt('milestone', 'milestone date', F.sort)}${opt('due', 'due date', F.sort)}${opt('points', 'points', F.sort)}${opt('blockers', 'blockers count', F.sort)}${opt('blocks', 'issues it unblocks', F.sort)}${opt('title', 'title', F.sort)}${opt('id', 'identifier', F.sort)}</select></label>
      <input type="search" id="f-q" placeholder="Search id or title" aria-label="Search issues in the views" value="${esc(F.q)}">
      <button class="btn" id="f-reset" type="button">Reset</button>
      <span class="cnt" id="f-cnt"></span>`;
    for (const k of ['p', 'ph', 's', 'ty', 'm', 'e', 'sz', 'est', 'cy', 'ini', 'flag', 'sort']) $('#f-' + k).addEventListener('change', ev => { F[k] = ev.target.value; refresh(); });
    let qt; $('#f-q').addEventListener('input', ev => { clearTimeout(qt); qt = setTimeout(() => { F.q = ev.target.value.trim(); refresh(); }, 140); });
    $('#f-reset').addEventListener('click', () => { for (const k in F) F[k] = k === 'sort' ? 'priority' : ''; renderFbar(); refresh(); });
  }
  const setFilter = (k, v) => { F[k] = v; renderFbar(); refresh(); };

  /* ---- shared tooltip / detail ---- */
  const tipFor = i => `<b>${i.id}</b> ${esc(i.t)}<div class="mu">${esc(short(i.p))} · ${i.ph} · ${esc(i.ty)}${i.sz ? ' · ' + i.sz : ''} · ${esc(i.d ? 'Deferred' : i.s)}${i.m ? ` · ${esc(i.m)} / ${esc(i.e)}` : ''}${i.msd ? ` · ${fdate(i.msd)}` : ''}</div><div class="mu">${i.est ? `${i.est} pt` : 'no estimate'}${i.due ? ` · due ${fdate(i.due)}` : ''}${i.cy ? ` · C${i.cy}` : ''}${i.ini ? ` · ${esc(i.ini)}` : ''}${i.r4 ? ' · new in round 4' : ''}</div><div class="mu">waits on ${blockersOf[i.id].length} · unblocks ${(blocksOf[i.id] || []).length}${i.ch.length ? ` · umbrella of ${i.ch.length}` : ''}</div>`;
  let pinned = null;
  const detail = $('#vdetail');
  function pin(id) {
    pinned = pinned === id ? null : id;
    detail.hidden = !pinned;
    if (!pinned) { document.querySelectorAll('.pin').forEach(e => e.classList.remove('pin')); return; }
    const i = byId[pinned];
    const rel = (ids, lab) => ids.length ? `<div><b>${lab}</b> ${ids.slice(0, 12).map(x => `<a href="${esc(byId[x].url)}" title="${esc(byId[x].t)}">${x}</a>`).join(', ')}${ids.length > 12 ? ` and ${ids.length - 12} more` : ''}</div>` : '';
    detail.innerHTML = `<div><div class="h"><a href="${esc(i.url)}">${i.id}</a><b>${esc(i.t)}</b></div>
      <div class="chips"><span class="chip">${esc(short(i.p))}</span><span class="chip">${i.ph}</span><span class="chip">${esc(i.ty)}${i.sz ? ' · ' + i.sz : ''}</span><span class="chip">${esc(i.d ? 'Deferred' : i.s)}</span>${i.m ? `<span class="chip">${esc(i.m)} / ${esc(i.e)}</span>` : ''}${i.ms ? `<span class="chip">${esc(i.ms)} · ${fdate(i.msd)}</span>` : ''}${i.sf.length ? `<span class="chip">${i.sf.map(esc).join(', ')}</span>` : ''}${i.ch.length ? `<span class="chip">umbrella · ${i.ch.length} children</span>` : ''}${i.est ? `<span class="chip">${i.est} pt</span>` : ''}${i.due ? `<span class="chip">due ${fdate(i.due)}</span>` : ''}${i.cy ? `<span class="chip">C${i.cy}</span>` : ''}${i.ini ? `<span class="chip">${esc(i.ini)}</span>` : ''}${i.r4 ? '<span class="chip">round 4</span>' : ''}</div>
      <div class="rel">${rel(blockersOf[i.id], 'Waits on')}${rel(blocksOf[i.id] || [], 'Unblocks')}${i.par ? `<div><b>Child of</b> ${issLink(i.par)}</div>` : ''}</div></div>
      <div style="display:grid;gap:6px;justify-items:end"><button class="x" id="vd-x" type="button">Unpin</button><a class="small" href="${esc(i.url)}">Open in Linear</a></div>`;
    $('#vd-x').addEventListener('click', () => pin(pinned));
    document.querySelectorAll('.pin').forEach(e => e.classList.remove('pin'));
    document.querySelectorAll(`[data-id="${pinned}"]`).forEach(e => e.classList.add('pin'));
  }
  const bindIssue = (node, i) => { node.dataset.id = i.id; bindTip(node, () => tipFor(i)); node.addEventListener('click', ev => { ev.stopPropagation(); pin(i.id); }); if (pinned === i.id) node.classList.add('pin'); };

  /* ---- legend ---- */
  function legend(extra) {
    const g = (ty) => `<span class="it"><svg viewBox="-8 -8 16 16"><path d="${shape(ty, 5)}" fill="currentColor" opacity=".7"/></svg>${ty}</span>`;
    $('#vlegend').innerHTML = `<span class="grp"><span class="k">shape = type</span>${TYPES.map(g).join('')}</span><span class="grp"><span class="k">fill = state</span>${['triage', 'backlog', 'ready', 'progress', 'review', 'justin', 'done', 'deferred'].map(k => `<span class="it"><svg viewBox="-8 -8 16 16"><circle r="5.5" class="g ${k}"/></svg>${stName[k].replace(' (Backlog, v0.2)', '')}</span>`).join('')}</span><span class="grp"><span class="k">hue = project</span>${extra || ''}</span>`;
  }

  /* ---- highlight helpers (ancestors / descendants within a visible set) ---- */
  function closure(id, map, vis) { const out = new Set(); const st = [id]; while (st.length) { const u = st.pop(); for (const v of (map[u] || [])) if (vis.has(v) && !out.has(v)) { out.add(v); st.push(v); } } return out; }
  function graphHover(svg, nodes, edges, vis) {
    return (id) => {
      svg.classList.toggle('dim', !!id);
      for (const k in nodes) nodes[k].classList.remove('on', 'up', 'down', 'self');
      for (const e of edges) e.el.classList.remove('on', 'up', 'down');
      if (!id) return;
      const up = closure(id, blockersOf, vis), down = closure(id, blocksOf, vis);
      nodes[id].classList.add('on', 'self');
      for (const u of up) nodes[u].classList.add('on', 'up');
      for (const d of down) nodes[d].classList.add('on', 'down');
      for (const e of edges) { if ((up.has(e.from) || e.from === id) && (up.has(e.to) || e.to === id)) e.el.classList.add('on', 'up'); else if ((down.has(e.from) || e.from === id) && (down.has(e.to) || e.to === id)) e.el.classList.add('on', 'down'); }
    };
  }

  /* ---- 1. objects map ---- */
  function squarify(items, x, y, w, h) {
    // items: [{key, v}], returns rects; simple slice-and-dice by rows (Bruls et al. squarified)
    const total = items.reduce((a, it) => a + it.v, 0) || 1, out = [];
    let rest = items.slice(), rx = x, ry = y, rw = w, rh = h;
    while (rest.length) {
      const horiz = rw >= rh; const side = horiz ? rh : rw; const area = (rw * rh) / rest.reduce((a, it) => a + it.v, 0);
      let row = [], best = Infinity;
      for (let k = 0; k < rest.length; k++) {
        const cand = rest.slice(0, k + 1), s = cand.reduce((a, it) => a + it.v * area, 0), len = s / side;
        const worst = Math.max(...cand.map(it => { const l2 = (it.v * area) / len; return Math.max(len / l2, l2 / len); }));
        if (worst > best) break; best = worst; row = cand;
      }
      const s = row.reduce((a, it) => a + it.v * area, 0), len = s / side; let off = 0;
      for (const it of row) { const l2 = (it.v * area) / len; out.push(horiz ? { key: it.key, x: rx, y: ry + off, w: len, h: l2 } : { key: it.key, x: rx + off, y: ry, w: l2, h: len }); off += l2; }
      if (horiz) { rx += len; rw -= len; } else { ry += len; rh -= len; }
      rest = rest.slice(row.length);
    }
    return out;
  }
  function viewObjectsMap(list, mount) {
    legend();
    const W = 1120, H = 660, top = 30;
    const byP = {}; for (const i of list) (byP[i.p] = byP[i.p] || []).push(i);
    const phases = ['P0', 'P1', 'P2'].map(ph => ({ ph, keys: projOrder.filter(k => (P[k].phase === ph) && byP[k]), n: 0 })).map(b => ({ ...b, n: b.keys.reduce((a, k) => a + byP[k].length, 0) })).filter(b => b.n);
    if (!phases.length) { mount.innerHTML = '<div class="empty">No issues match these filters.</div>'; return; }
    const tot = phases.reduce((a, b) => a + b.n, 0);
    const svg = svgEl('svg', { class: 'vfig omap', viewBox: `0 0 ${W} ${H}`, width: W, height: H, role: 'img', 'aria-label': 'Objects map: each project is a region sized by its issue count, grouped into phase bands; issues sit inside as glyphs; curved roads carry the blocking relations between projects' });
    const gB = svgEl('g', {}, svg), gR = svgEl('g', {}, svg), gRoad = svgEl('g', {}, svg), gG = svgEl('g', {}, svg);
    let x = 8; const rects = [], center = {}, regionEl = {};
    for (const b of phases) {
      const w = Math.max(120, (W - 16) * b.n / tot - 6);
      svgEl('rect', { class: `ph-band ${b.ph.toLowerCase()}`, x, y: 4, width: w, height: H - 8, rx: 12 }, gB);
      const t = svgEl('text', { class: 'ph-l', x: x + 12, y: 20 }, gB); const pname = D.phases.find(p => p.key === b.ph).name.toUpperCase(); t.textContent = w > 300 ? `${b.ph} · ${pname} · ${b.n}` : w > 170 ? `${b.ph} · ${pname.split(' ')[0]} · ${b.n}` : `${b.ph} · ${b.n}`;
      const rs = squarify(b.keys.map(k => ({ key: k, v: Math.max(2, byP[k].length) })).sort((a, c) => c.v - a.v), x + 6, top, w - 12, H - top - 8);
      for (const r of rs) rects.push(r);
      x += w + 8;
    }
    for (const r of rects) {
      const p = P[r.key], items = byP[r.key], pad = 5, ix = r.x + pad, iy = r.y + pad, iw = r.w - 2 * pad, ih = r.h - 2 * pad;
      const reg = svgEl('rect', { class: 'region', x: ix, y: iy, width: Math.max(0, iw), height: Math.max(0, ih), rx: 8, fill: p.color, stroke: p.color }, gR);
      regionEl[r.key] = reg; center[r.key] = { x: ix + iw / 2, y: iy + ih / 2 };
      const labelH = ih > 40 ? 26 : 0;
      if (labelH) { const nm = svgEl('text', { class: 'rname lbl', x: ix + 7, y: iy + 14 }, gR); nm.textContent = iw > 110 ? p.short : p.short.split(' ')[0]; const c = svgEl('text', { class: 'rcnt lbl', x: ix + 7, y: iy + 24 }, gR); c.textContent = `${items.length} issues · ${items.filter(i => i.s === 'Ready for Claude').length} ready`; }
      const gx = ix + 6, gy = iy + labelH + 4, gw = Math.max(8, iw - 12), gh = Math.max(8, ih - labelH - 8);
      let c = Math.max(6, Math.min(20, Math.floor(Math.sqrt(gw * gh / items.length)))); let cols = Math.max(1, Math.floor(gw / c)); let rows = Math.ceil(items.length / cols);
      while (rows * c > gh && c > 6) { c--; cols = Math.max(1, Math.floor(gw / c)); rows = Math.ceil(items.length / cols); }
      const r0 = Math.max(2.4, c * 0.34);
      items.forEach((i, k) => { const cx = gx + (k % cols) * c + c / 2, cy = gy + Math.floor(k / cols) * c + c / 2; const g = svgEl('path', { class: `g ${skey(i)}${i.ch.length ? ' umb' : ''}`, d: shape(i.ty, r0), transform: `translate(${cx.toFixed(1)},${cy.toFixed(1)})` }, gG); bindIssue(g, i); });
      bindTip(reg, `<b>${esc(p.name)}</b><div class="mu">${items.length} issues shown · ${p.total} in Linear · ${p.ready} ready · ${p.milestones.length} milestones</div><div class="mu">click to highlight its roads · double-click to filter to it</div>`);
      reg.addEventListener('click', () => selectRegion(r.key === selReg ? null : r.key));
      reg.addEventListener('dblclick', () => setFilter('p', r.key));
    }
    const roads = [];
    for (const e of D.edges) { if (!center[e.from] || !center[e.to] || e.n < 2) continue; const a = center[e.from], b = center[e.to]; const mx = (a.x + b.x) / 2, my = (a.y + b.y) / 2 - Math.min(90, Math.abs(b.x - a.x) * 0.25); const pth = svgEl('path', { class: 'road', d: `M${a.x},${a.y} Q${mx},${my} ${b.x},${b.y}`, 'stroke-width': (0.6 + Math.sqrt(e.n) * 0.8).toFixed(2) }, gRoad); bindTip(pth, `<b>${esc(short(e.from))} → ${esc(short(e.to))}</b><div class="mu">${e.n} issues in ${esc(short(e.to))} wait on ${esc(short(e.from))}</div>`); roads.push({ e, el: pth }); }
    let selReg = null;
    function selectRegion(k) {
      selReg = k; svg.classList.toggle('dim', !!k);
      for (const key in regionEl) regionEl[key].classList.remove('sel', 'nb');
      for (const r of roads) r.el.classList.remove('on', 'up');
      if (!k) return; regionEl[k].classList.add('sel');
      for (const r of roads) { if (r.e.from === k) { r.el.classList.add('on'); regionEl[r.e.to].classList.add('nb'); } else if (r.e.to === k) { r.el.classList.add('on', 'up'); regionEl[r.e.from].classList.add('nb'); } }
    }
    svg.addEventListener('click', ev => { if (ev.target === svg || ev.target.classList.contains('ph-band')) selectRegion(null); });
    mount.innerHTML = `<div class="vtools"><span>Region area = issues shown · roads = 2+ blocking relations between projects (orange: the selected project unblocks, blue: it waits on) · glyph grid follows the sort order</span></div>`;
    const sc = el('div', 'scroller'); sc.appendChild(svg); mount.appendChild(sc); fitWidth(svg, sc, W, H);
  }
  function fitWidth(svg, sc, W, H) { const avail = sc.clientWidth - 24; const k = Math.min(1, avail / W); svg.setAttribute('width', Math.round(W * Math.max(k, 0.55))); svg.setAttribute('height', Math.round(H * Math.max(k, 0.55))); }

  /* ---- 2. lanes skill tree ---- */
  function viewLanes(list, mount) {
    legend();
    const vis = new Set(list.map(i => i.id));
    const lanesDef = ['P0', 'P1', 'P2'].map(ph => ({ ph, items: list.filter(i => i.ph === ph) })).filter(l => l.items.length);
    if (!lanesDef.length) { mount.innerHTML = '<div class="empty">No issues match these filters.</div>'; return; }
    const maxLv = Math.max(...list.map(i => i.lv || 0));
    const padL = 215, colW = 128, rowH = 15, top = 34; const W = padL + (maxLv + 1) * colW + 40;
    let y = top; const pos = {};
    for (const l of lanesDef) {
      const byLv = {}; for (const i of l.items) (byLv[i.lv || 0] = byLv[i.lv || 0] || []).push(i);
      let maxN = 0; for (const k in byLv) { byLv[k].sort((a, b) => pIdx[a.p] - pIdx[b.p] || sorters[F.sort](a, b)); maxN = Math.max(maxN, byLv[k].length); }
      l.top = y; l.h = Math.max(64, 30 + maxN * rowH); l.byLv = byLv;
      for (const k in byLv) byLv[k].forEach((i, j) => { pos[i.id] = { x: padL + k * colW + 20, y: y + 26 + j * rowH }; });
      y += l.h + 10;
    }
    const H = y + 10;
    const svg = svgEl('svg', { class: 'vfig lanes', viewBox: `0 0 ${W} ${H}`, width: W, height: H, role: 'img', 'aria-label': 'Lanes skill tree: one lane per phase, issues placed left to right by how many blockers precede them, with the blocking relations drawn as branches' });
    const gL = svgEl('g', {}, svg), gE = svgEl('g', {}, svg), gN = svgEl('g', {}, svg);
    for (let k = 0; k <= maxLv; k++) { const x = padL + k * colW + 20; svgEl('line', { class: 'col', x1: x, y1: top - 6, x2: x, y2: H - 6 }, gL); const t = svgEl('text', { class: 'col-l', x, y: top - 12 }, gL); t.textContent = k === 0 ? 'no blockers' : `step ${k}`; }
    for (const l of lanesDef) { svgEl('rect', { class: `lane ${l.ph.toLowerCase()}`, x: 6, y: l.top, width: W - 12, height: l.h, rx: 8 }, gL); const t = svgEl('text', { class: `lane-l ${l.ph.toLowerCase()}`, x: 16, y: l.top + 18 }, gL); t.textContent = `${l.ph} · ${D.phases.find(p => p.key === l.ph).name.toUpperCase()}`; const s = svgEl('text', { class: 'lane-s', x: 16, y: l.top + 32 }, gL); s.textContent = `${l.items.length} issues · ${l.items.filter(i => i.s === 'Ready for Claude').length} ready`; }
    const edges = [], nodes = {};
    for (const i of list) for (const b of blockersOf[i.id]) { if (!vis.has(b)) continue; const a = pos[b], c = pos[i.id]; const dx = Math.max(24, (c.x - a.x) * 0.45); const d = c.x > a.x ? `M${a.x + 6},${a.y} C${a.x + dx},${a.y} ${c.x - dx},${c.y} ${c.x - 6},${c.y}` : `M${a.x},${a.y + 6} C${a.x},${(a.y + c.y) / 2} ${c.x},${(a.y + c.y) / 2} ${c.x},${c.y - 6}`; const e = svgEl('path', { class: 'e', d }, gE); edges.push({ from: b, to: i.id, el: e }); }
    for (const i of list) { const q = pos[i.id]; const g = svgEl('g', { class: 'nd' }, gN); svgEl('rect', { x: q.x - 11, y: q.y - 4, width: 3, height: 8, rx: 1, fill: hue(i.p) }, g); const p = svgEl('path', { class: `g ${skey(i)}${i.ch.length ? ' umb' : ''}`, d: shape(i.ty, 4.6), transform: `translate(${q.x},${q.y})` }, g); const t = svgEl('text', { class: 'lb', x: q.x + 8, y: q.y + 3 }, g); t.textContent = i.n; nodes[i.id] = p; bindIssue(p, i); }
    const hov = graphHover(svg, nodes, edges, vis);
    for (const i of list) { nodes[i.id].addEventListener('pointerenter', () => hov(i.id)); nodes[i.id].addEventListener('pointerleave', () => hov(null)); }
    mount.innerHTML = `<div class="vtools"><span>Column = dependency depth (longest chain of blockers before it) · hover an issue to light its blockers (blue) and what it unblocks (orange) · tick colour = project</span><span class="sp"></span><label class="ck small"><input type="checkbox" id="ln-edges" checked> draw all edges</label><span class="seg"><button class="btn" id="ln-out" type="button">−</button><button class="btn" id="ln-in" type="button">+</button></span></div>`;
    const sc = el('div', 'scroller'); sc.appendChild(svg); mount.appendChild(sc);
    let z = Math.min(1, (sc.clientWidth - 24) / W); z = Math.max(z, 0.6); const apply = () => { svg.setAttribute('width', Math.round(W * z)); svg.setAttribute('height', Math.round(H * z)); }; apply();
    $('#ln-out', mount).addEventListener('click', () => { z = Math.max(0.35, z - 0.15); apply(); }); $('#ln-in', mount).addEventListener('click', () => { z = Math.min(2, z + 0.15); apply(); });
    $('#ln-edges', mount).addEventListener('change', ev => { gE.style.opacity = ev.target.checked ? '' : '0'; svg.classList.toggle('edges-off', !ev.target.checked); });
    svg.classList.add('edges-hover');
  }

  /* ---- 3. radial tree ---- */
  const polar = (a, r) => [r * Math.sin(a), -r * Math.cos(a)];
  const radialLink = (a0, r0, a1, r1) => { const rm = (r0 + r1) / 2; const [x0, y0] = polar(a0, r0), [c0x, c0y] = polar(a0, rm), [c1x, c1y] = polar(a1, rm), [x1, y1] = polar(a1, r1); return `M${x0.toFixed(1)},${y0.toFixed(1)}C${c0x.toFixed(1)},${c0y.toFixed(1)} ${c1x.toFixed(1)},${c1y.toFixed(1)} ${x1.toFixed(1)},${y1.toFixed(1)}`; };
  function viewRadial(list, mount) {
    legend();
    if (!list.length) { mount.innerHTML = '<div class="empty">No issues match these filters.</div>'; return; }
    const R = 430, S = 2 * (R + 70);
    const svg = svgEl('svg', { class: 'vfig radial', viewBox: `${-S / 2} ${-S / 2} ${S} ${S}`, width: S, height: S, role: 'img', 'aria-label': 'Radial tree: PaperOS at the centre, one sector per project, milestones on the middle ring and issues on the outer ring' });
    const gS = svgEl('g', {}, svg), gL = svgEl('g', {}, svg), gN = svgEl('g', {}, svg), gT = svgEl('g', {}, svg);
    const defs = svgEl('defs', {}, svg);
    const tree = projOrder.filter(k => list.some(i => i.p === k)).map(k => { const items = list.filter(i => i.p === k); const ms = {}; for (const i of items) (ms[i.ms || '(no milestone)'] = ms[i.ms || '(no milestone)'] || []).push(i); const msList = Object.keys(ms).map(n => ({ name: n, date: (P[k].milestones.find(m => m.name === n) || {}).date || '', items: ms[n] })).sort((a, b) => a.date.localeCompare(b.date)); return { key: k, items, ms: msList, w: Math.max(4, items.length) }; });
    const gap = (tree.length > 1 ? 5 : 0) * Math.PI / 180, avail = 2 * Math.PI - tree.length * gap, tot = tree.reduce((a, t) => a + t.w, 0);
    let a = gap / 2; const links = [], leafEls = {}, msEls = [];
    const showLeafLabels = list.length <= 160;
    for (const t of tree) {
      const span = avail * t.w / tot, a0 = a, a1 = a + span, am = (a0 + a1) / 2, col = hue(t.key);
      const sec = svgEl('path', { class: 'sector', fill: col, stroke: col, d: `M${polar(a0, R * 0.16).join(',')}L${polar(a0, R + 14).join(',')}A${R + 14},${R + 14} 0 ${span > Math.PI ? 1 : 0},1 ${polar(a1, R + 14).join(',')}L${polar(a1, R * 0.16).join(',')}A${R * 0.16},${R * 0.16} 0 ${span > Math.PI ? 1 : 0},0 ${polar(a0, R * 0.16).join(',')}z` }, gS);
      bindTip(sec, `<b>${esc(P[t.key].name)}</b><div class="mu">${t.items.length} issues shown · ${t.ms.length} milestones · double-click to filter</div>`); sec.addEventListener('dblclick', () => setFilter('p', t.key));
      // project node
      const [px, py] = polar(am, R * 0.3);
      links.push(svgEl('path', { class: 'link', d: radialLink(am, 0, am, R * 0.3), stroke: col, 'stroke-width': 2.6, 'stroke-opacity': .7 }, gL));
      const pn = svgEl('path', { d: shape('Infra', 10), fill: col, stroke: 'var(--card)', 'stroke-width': 2, transform: `translate(${px.toFixed(1)},${py.toFixed(1)})`, style: 'cursor:pointer' }, gN);
      bindTip(pn, `<b>${esc(P[t.key].name)}</b><div class="mu">${t.items.length} issues shown · ${P[t.key].total} in Linear · ${P[t.key].ready} ready</div>`); pn.addEventListener('dblclick', () => setFilter('p', t.key));
      // arc label
      const flip = Math.cos(am) < 0, rl = flip ? R + 44 : R + 30, [s, e] = flip ? [a1, a0] : [a0, a1]; const id = 'arc-' + t.key;
      svgEl('path', { id, d: `M${polar(s, rl).join(',')}A${rl},${rl} 0 ${span > Math.PI ? 1 : 0} ${flip ? 0 : 1} ${polar(e, rl).join(',')}`, fill: 'none' }, defs);
      const tx = svgEl('text', { class: 'arc-l', fill: col, 'text-anchor': 'middle' }, gT); const tp = svgEl('textPath', { href: '#' + id, startOffset: '50%' }, tx); const arcLen = span * rl, full = P[t.key].short.toUpperCase(), first = full.split(' ')[0]; tp.textContent = arcLen > full.length * 8.5 ? full : arcLen > first.length * 8.5 ? first : first.slice(0, Math.max(3, Math.floor(arcLen / 8.5)));
      // milestones
      const mtot = t.ms.reduce((x, m) => x + Math.max(1, m.items.length), 0); let ma = a0;
      for (const m of t.ms) {
        const mspan = span * Math.max(1, m.items.length) / mtot, mam = ma + mspan / 2; const [mx, my] = polar(mam, R * 0.62);
        const l = svgEl('path', { class: 'link', d: radialLink(am, R * 0.3, mam, R * 0.62), stroke: col, 'stroke-width': 1.6, 'stroke-opacity': .55 }, gL);
        const mn = svgEl('circle', { class: 'msn', cx: mx.toFixed(1), cy: my.toFixed(1), r: 4.5, stroke: col }, gN);
        bindTip(mn, `<b>${esc(P[t.key].short)} · ${esc(m.name)}</b><div class="mu">${m.date ? fdate(m.date) + ' · ' : ''}${m.items.length} issues shown · ${m.items.filter(i => i.s === 'Ready for Claude').length} ready</div>`);
        if (mspan * R * 0.62 > 14) { const deg = mam * 180 / Math.PI - 90, fl = mam > Math.PI; const tl = svgEl('text', { class: 'ms-l lbl', transform: `rotate(${deg.toFixed(1)}) translate(${R * 0.62 + 8},0) rotate(${fl ? 180 : 0}) translate(0,3)`, 'text-anchor': fl ? 'end' : 'start' }, gT); tl.textContent = m.name.length > 26 ? m.name.slice(0, 25) + '…' : m.name; msEls.push({ el: tl, ids: m.items.map(i => i.id) }); }
        const n = m.items.length; m.items.forEach((i, j) => { const la = ma + mspan * (j + 0.5) / n, lr = R - (j % 2) * 13; const [lx, ly] = polar(la, lr); links.push(Object.assign(svgEl('path', { class: 'link lf', d: radialLink(mam, R * 0.62, la, lr), stroke: col, 'stroke-width': .8, 'stroke-opacity': .4 }, gL), { _id: i.id })); const g = svgEl('path', { class: `g ${skey(i)}${i.ch.length ? ' umb' : ''}`, d: shape(i.ty, 3.4), transform: `translate(${lx.toFixed(1)},${ly.toFixed(1)})` }, gN); leafEls[i.id] = { el: g, link: links[links.length - 1], ms: m }; bindIssue(g, i); if (showLeafLabels) { const deg = la * 180 / Math.PI - 90, fl = la > Math.PI; const tl = svgEl('text', { class: 'leaf-l', transform: `rotate(${deg.toFixed(1)}) translate(${lr + 6},0) rotate(${fl ? 180 : 0}) translate(0,2.5)`, 'text-anchor': fl ? 'end' : 'start' }, gT); tl.textContent = i.n; } });
        ma += mspan;
      }
      a += span + gap;
    }
    svgEl('circle', { class: 'core', r: 26 }, gN); const ct = svgEl('text', { class: 'core-l', y: 4 }, gN); ct.textContent = 'PAPEROS';
    for (const id in leafEls) { const { el: g, link } = leafEls[id]; g.addEventListener('pointerenter', () => { svg.classList.add('dim'); link.classList.add('on'); }); g.addEventListener('pointerleave', () => { svg.classList.remove('dim'); link.classList.remove('on'); }); }
    mount.innerHTML = `<div class="vtools"><span>Sector = project (size by issues shown) · middle ring = milestones in date order · outer ring = issues${showLeafLabels ? ', numbered' : ' (labels appear under 160 issues)'} · double-click a sector to filter to it</span><span class="sp"></span><span class="seg"><button class="btn" id="rd-out" type="button">−</button><button class="btn" id="rd-in" type="button">+</button></span></div>`;
    const sc = el('div', 'scroller'); sc.appendChild(svg); mount.appendChild(sc);
    let z = Math.min(1, (sc.clientWidth - 24) / S); z = Math.max(z, 0.7); const apply = () => { svg.setAttribute('width', Math.round(S * z)); svg.setAttribute('height', Math.round(S * z)); }; apply();
    $('#rd-out', mount).addEventListener('click', () => { z = Math.max(0.5, z - 0.15); apply(); }); $('#rd-in', mount).addEventListener('click', () => { z = Math.min(2.2, z + 0.15); apply(); });
  }

  /* ---- 4. images: project tiles with generated glyphs + issue cards with generated covers ---- */
  function projectGlyph(key, size) {
    const r = rng(hash(key)); const c = hue(key); let cells = '';
    for (let y = 0; y < 5; y++) for (let x = 0; x < 3; x++) if (r() > 0.5) { const o = 0.35 + r() * 0.65; cells += `<rect x="${x * 8}" y="${y * 8}" width="8" height="8" fill="${c}" opacity="${o.toFixed(2)}"/>`; if (x < 2) cells += `<rect x="${(4 - x) * 8}" y="${y * 8}" width="8" height="8" fill="${c}" opacity="${o.toFixed(2)}"/>`; }
    return `<svg viewBox="-2 -2 44 44" width="${size}" height="${size}" aria-hidden="true"><rect x="-2" y="-2" width="44" height="44" rx="8" fill="${c}" opacity=".12"/>${cells}</svg>`;
  }
  function cover(i) {
    const r = rng(i.n * 7919 + 17), c = hue(i.p); let sh = '';
    for (let k = 0; k < 4; k++) { const x = 20 + r() * 120, y = 12 + r() * 66, s = 10 + r() * 26, rot = r() * 360; sh += `<path d="${shape(i.ty, s)}" transform="translate(${x.toFixed(0)},${y.toFixed(0)}) rotate(${rot.toFixed(0)})" fill="${c}" opacity="${(0.18 + r() * 0.35).toFixed(2)}"/>`; }
    return `<svg class="cover" viewBox="0 0 160 90" aria-hidden="true"><rect width="160" height="90" fill="${c}" opacity=".10"/>${sh}<path d="${shape(i.ty, 9)}" transform="translate(140,18)" fill="${c}" opacity=".9"/><rect x="0" y="84" width="160" height="6" class="g ${skey(i)}" style="stroke:none"/><text x="8" y="16" font-family="ui-monospace,Menlo,monospace" font-size="10" fill="currentColor" opacity=".7">${i.id}</text></svg>`;
  }
  function viewImages(list, mount) {
    legend();
    const counts = {}; for (const i of list) counts[i.p] = (counts[i.p] || 0) + 1;
    const tiles = D.projects.filter(p => counts[p.key] || F.p === p.key).map(p => `<button class="ptile${F.p === p.key ? ' on' : ''}" type="button" data-k="${p.key}">${projectGlyph(p.key, 44)}<div><b>${esc(p.short)}</b><span>${p.phase} · ${counts[p.key] || 0} of ${p.total}</span></div></button>`).join('');
    mount.innerHTML = `<div class="vtools"><span>Project tiles carry a glyph generated from the project key; each issue card's cover is generated from its number, type and project. Click a tile to filter; click a card to pin it.</span></div><div class="scroller"><div class="ptiles">${tiles}</div><div class="icards" id="icards"></div><div class="more" id="imore"></div></div>`;
    mount.querySelectorAll('.ptile').forEach(b => b.addEventListener('click', () => setFilter('p', F.p === b.dataset.k ? '' : b.dataset.k)));
    const wrap = $('#icards', mount), more = $('#imore', mount); let shown = 0; const PAGE = 48;
    const page = () => { const slice = list.slice(shown, shown + PAGE); for (const i of slice) { const card = el('div', `icard st-${skey(i)}`); card.innerHTML = `${cover(i)}<div class="body"><div class="hd"><a class="id" href="${esc(i.url)}">${i.id}</a><span class="pill">${esc(i.d ? 'Deferred' : i.s)}</span></div><div class="t" title="${esc(i.t)}">${esc(i.t)}</div><div class="m"><span title="${esc(i.ty)}">${typeIcon(i.ty)} ${esc(i.ty)}${i.sz ? ' · ' + i.sz : ''}</span>${i.m ? `<span title="${esc(i.m)} / ${esc(i.e)}">${modelIcon(i.m)} ${esc(i.m.replace(' 5.1', '').replace(' 5', '').replace(' 4.5', ''))} · ${esc(i.e)}</span>` : ''}${i.msd ? `<span>${fdate(i.msd)}</span>` : ''}<span title="blockers">⇠ ${blockersOf[i.id].length} · ⇢ ${(blocksOf[i.id] || []).length}</span></div></div>`; bindIssue(card, i); wrap.appendChild(card); } shown += slice.length; more.innerHTML = shown < list.length ? `<button class="btn" type="button">Show ${Math.min(PAGE, list.length - shown)} more (${list.length - shown} left)</button>` : `<span class="small mute">${list.length} issues shown</span>`; const b = more.querySelector('button'); if (b) b.addEventListener('click', page); };
    if (!list.length) wrap.innerHTML = '<div class="empty">No issues match these filters.</div>'; else page();
  }

  /* ---- 5. icons ---- */
  function viewIcons(list, mount) {
    legend(`<span class="it">${TYPES.map(t => `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" style="width:15px;height:15px">${ICON[t]}</svg>`).join('')} type icons</span><span class="it">${MODELS.map(m => `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" style="width:13px;height:13px">${MICON[m]}</svg>`).join('')} model marks (Fable, Opus, Sonnet, Haiku)</span><span class="it">● ● ○ effort dots</span>`);
    const byP = {}; for (const i of list) (byP[i.p] = byP[i.p] || []).push(i);
    const groups = projOrder.filter(k => byP[k]).map(k => `<div class="igroup"><div class="ghd"><i style="background:${hue(k)}"></i><b>${esc(short(k))}</b><span>${P[k].phase} · ${byP[k].length} shown · ${byP[k].filter(i => i.s === 'Ready for Claude').length} ready</span></div><div class="igrid">${byP[k].map(i => `<button class="itile st-${skey(i)}${i.ch.length ? ' umb' : ''}" type="button" data-id="${i.id}" aria-label="${i.id} ${esc(i.t)}">${typeIcon(i.ty)}${i.m ? `<span class="mk">${modelIcon(i.m)}</span>` : ''}${i.e ? effDots(i.e) : ''}</button>`).join('')}</div></div>`).join('');
    mount.innerHTML = `<div class="vtools"><span>One tile per issue, grouped by project in sort order: the big icon is the type, the small mark bottom-right is the model, the dots bottom-left are effort, the tint is the state; a bold border marks an umbrella.</span></div><div class="scroller"><div class="itiles">${groups || '<div class="empty">No issues match these filters.</div>'}</div></div>`;
    mount.querySelectorAll('.itile').forEach(b => bindIssue(b, byId[b.dataset.id]));
  }

  /* ---- 3D: shared projection for the static previews ---- */
  function project3d(pts, yaw, pitch, W, H, scale) {
    const cy = Math.cos(yaw), sy = Math.sin(yaw), cp = Math.cos(pitch), sp = Math.sin(pitch);
    return pts.map(p => { const x1 = p.x * cy - p.z * sy, z1 = p.x * sy + p.z * cy; const y2 = p.y * cp - z1 * sp, z2 = p.y * sp + z1 * cp; const f = 900 / (900 + z2); return { ...p, sx: W / 2 + x1 * f * scale, sy: H / 2 + y2 * f * scale, f, z: z2 }; });
  }
  function previewSvg(pts, links, W, H, label) {
    const sorted = [...pts].sort((a, b) => a.z - b.z);
    const idx = Object.fromEntries(pts.map(p => [p.id, p]));
    const ls = links.slice(0, 700).map(l => { const a = idx[l.s], b = idx[l.t]; if (!a || !b) return ''; return `<line x1="${a.sx.toFixed(1)}" y1="${a.sy.toFixed(1)}" x2="${b.sx.toFixed(1)}" y2="${b.sy.toFixed(1)}" stroke="${l.c || '#ffffff'}" stroke-opacity="${(l.o || 0.12).toFixed(2)}" stroke-width="${(l.w || 0.6).toFixed(1)}"/>`; }).join('');
    const ns = sorted.map(p => `<circle cx="${p.sx.toFixed(1)}" cy="${p.sy.toFixed(1)}" r="${(p.r * p.f).toFixed(1)}" fill="${p.c}" fill-opacity="${(0.45 + 0.55 * Math.min(1, Math.max(0, (p.z + 500) / 1000))).toFixed(2)}"/>${p.glow ? `<circle cx="${p.sx.toFixed(1)}" cy="${p.sy.toFixed(1)}" r="${(p.r * p.f * 2.4).toFixed(1)}" fill="${p.c}" fill-opacity=".12"/>` : ''}`).join('');
    return `<svg viewBox="0 0 ${W} ${H}" role="img" aria-label="${esc(label)}"><rect width="${W}" height="${H}" fill="#070a12"/>${ls}${ns}<text x="14" y="${H - 12}" font-family="ui-monospace,Menlo,monospace" font-size="11" fill="#98a4b9">static preview · ${pts.length} objects</text></svg>`;
  }
  function fallback(mount, kind, list) {
    const W = 760, H = 480; let svg;
    const jit = rng(hash(kind) + list.length);
    if (kind === 'objects-3d') {
      const pts = list.map(i => ({ id: i.id, x: (PH[i.ph] - 1) * 240 + (jit() - 0.5) * 150, y: (pIdx[i.p] - projOrder.length / 2) * 26 + (jit() - 0.5) * 20, z: ({ low: -1, medium: 0, high: 1, max: 1.6 }[i.e] || 0) * 150 + (jit() - 0.5) * 80, r: { S: 2.6, M: 3.4, L: 4.6 }[i.sz] || 3, c: hue(i.p) }));
      const links = []; const vis = new Set(list.map(i => i.id)); for (const i of list) for (const b of blockersOf[i.id]) if (vis.has(b)) links.push({ s: b, t: i.id, c: '#9ec5f4' });
      svg = previewSvg(project3d(pts, 0.55, 0.35, W, H, 0.95), links, W, H, 'Static preview of the objects 3D scene: issues placed by phase, project and effort, joined by their blocking relations');
    } else {
      const pts = [{ id: 'root', x: 0, y: 0, z: 0, r: 12, c: '#ffffff', glow: true }], links = [];
      const tree = projOrder.filter(k => list.some(i => i.p === k)); const N = tree.length, ga = Math.PI * (3 - Math.sqrt(5));
      tree.forEach((k, n) => { const yv = 1 - (n / Math.max(1, N - 1)) * 2, rr = Math.sqrt(1 - yv * yv), th = ga * n; const d = { x: Math.cos(th) * rr, y: yv, z: Math.sin(th) * rr }; const pp = { id: 'p:' + k, x: d.x * 150, y: d.y * 150, z: d.z * 150, r: 7, c: hue(k), glow: true }; pts.push(pp); links.push({ s: 'root', t: pp.id, c: hue(k), o: .55, w: 2.2 });
        const items = list.filter(i => i.p === k); const ms = {}; for (const i of items) (ms[i.ms || '-'] = ms[i.ms || '-'] || []).push(i); const mks = Object.keys(ms);
        const u = { x: -d.z, y: 0, z: d.x }; const ul = Math.hypot(u.x, u.z) || 1; u.x /= ul; u.z /= ul; const v = { x: d.y * u.z - d.z * u.y, y: d.z * u.x - d.x * u.z, z: d.x * u.y - d.y * u.x };
        mks.forEach((mk, j) => { const phi = 2 * Math.PI * (j + 0.5) / mks.length + n, L = 85, th2 = 0.5; const mp = { id: `m:${k}:${j}`, x: pp.x + d.x * L * Math.cos(th2) + (u.x * Math.cos(phi) + v.x * Math.sin(phi)) * L * Math.sin(th2), y: pp.y + d.y * L * Math.cos(th2) + (u.y * Math.cos(phi) + v.y * Math.sin(phi)) * L * Math.sin(th2), z: pp.z + d.z * L * Math.cos(th2) + (u.z * Math.cos(phi) + v.z * Math.sin(phi)) * L * Math.sin(th2), r: 4, c: hue(k) }; pts.push(mp); links.push({ s: pp.id, t: mp.id, c: hue(k), o: .4, w: 1.2 });
          const dm = { x: mp.x - pp.x, y: mp.y - pp.y, z: mp.z - pp.z }; const dl = Math.hypot(dm.x, dm.y, dm.z) || 1; dm.x /= dl; dm.y /= dl; dm.z /= dl;
          ms[mk].forEach((i, q) => { const ph2 = 2 * Math.PI * (q + 0.5) / ms[mk].length, L2 = 50, t2 = 0.42; const lp = { id: i.id, x: mp.x + dm.x * L2 * Math.cos(t2) + (u.x * Math.cos(ph2) + v.x * Math.sin(ph2)) * L2 * Math.sin(t2), y: mp.y + dm.y * L2 * Math.cos(t2) + (u.y * Math.cos(ph2) + v.y * Math.sin(ph2)) * L2 * Math.sin(t2), z: mp.z + dm.z * L2 * Math.cos(t2) + (u.z * Math.cos(ph2) + v.z * Math.sin(ph2)) * L2 * Math.sin(t2), r: 2.3, c: hue(k) }; pts.push(lp); links.push({ s: mp.id, t: lp.id, c: hue(k), o: .25, w: .7 }); }); }); });
      svg = previewSvg(project3d(pts, 0.6, 0.42, W, H, 1.05), links, W, H, 'Static preview of the radial 3D scene: PaperOS at the centre, project limbs, milestone cones and issue leaves');
    }
    const live = MODE === 'pages';
    mount.innerHTML = `<div class="fallback"><div class="prev">${svg}</div><div class="why"><h4>${kind === 'objects-3d' ? 'Objects 3D: issues as objects in space' : 'Radial 3D: the project tree in three dimensions'}</h4><p>${live ? 'The live scene needs 3d-force-graph from jsDelivr, which did not load here (offline, blocked, or still loading). The picture on the left is a static projection of the same data.' : 'This copy of the Blueprint is self-contained, so it shows a static projection of the same data. The interactive WebGL scene runs on the GitHub Pages copy, where the library may load from a CDN.'}</p><a class="btn on" href="${esc(D.pages)}#${kind}">Open the live 3D view on GitHub Pages</a><ul>${kind === 'objects-3d' ? '<li>Force-directed graph of every <span class="mono">blockedBy</span> relation among the filtered issues, or a scatter by phase, project and effort.</li><li>Node colour is the project, size is S / M / L; arrows point at the issue that waits.</li><li>Drag to orbit, hover for the issue, click to fly to it and pin it below.</li>' : '<li>PaperOS at the centre, one limb per project, milestones in a cone around each limb, issues as leaves (radial DAG layout).</li><li>Node colour is the project; the same filters and sort apply.</li><li>Drag to orbit, hover for the issue, click to fly to it and pin it below.</li>'}</ul><p class="small mute">Library: 3d-force-graph 1.80.0 (bundles three.js), as used by the graph-gallery Constellation demo.</p></div></div>`;
  }
  const fg = { objects: null, radial: null };
  function view3d(kind, list, mount) {
    legend();
    if (MODE !== 'pages' || window.__fg3dFailed) return fallback(mount, kind, list);
    if (!window.ForceGraph3D) {
      mount.innerHTML = `<div class="threed"><div class="load">Loading 3d-force-graph from jsDelivr…</div></div>`;
      let tries = 0; const iv = setInterval(() => { tries++; if (window.ForceGraph3D) { clearInterval(iv); if (active === kind) view3d(kind, list, mount); } else if (tries > 40 || window.__fg3dFailed) { clearInterval(iv); window.__fg3dFailed = true; if (active === kind) fallback(mount, kind, list); } }, 250);
      return;
    }
    const isObj = kind === 'objects-3d'; const st = state3d[kind];
    mount.innerHTML = `<div class="vtools">${isObj ? `<label>Layout <select id="fg-mode"><option value="force"${st.mode === 'force' ? ' selected' : ''}>force graph of blocks</option><option value="scatter"${st.mode === 'scatter' ? ' selected' : ''}>scatter: phase × project × effort</option></select></label>` : ''}<label>Colour <select id="fg-col"><option value="project"${st.col === 'project' ? ' selected' : ''}>project</option><option value="state"${st.col === 'state' ? ' selected' : ''}>state</option><option value="phase"${st.col === 'phase' ? ' selected' : ''}>phase</option></select></label><label class="ck small"><input type="checkbox" id="fg-spin"${st.spin ? ' checked' : ''}> auto-orbit</label><span class="sp"></span><button class="btn" id="fg-fit" type="button">Fit</button></div><div class="threed"><div class="fg" id="fg-${kind}"></div><div class="hint">drag to orbit · scroll to zoom · hover for the issue · click to fly in and pin</div></div>`;
    const box = $('#fg-' + kind, mount); const w = box.clientWidth || mount.clientWidth || 900, h = 560;
    const cssVar = n => getComputedStyle(document.documentElement).getPropertyValue(n).trim() || '#888';
    const colorOf = i => st.col === 'state' ? cssVar('--st-' + skey(i)) : st.col === 'phase' ? cssVar('--' + i.ph.toLowerCase()) : hue(i.p);
    const vis = new Set(list.map(i => i.id));
    let nodes, links;
    if (isObj) {
      nodes = list.map(i => ({ id: i.id, i, val: { S: 1, M: 2.2, L: 4.5 }[i.sz] || 2 }));
      links = []; for (const i of list) for (const b of blockersOf[i.id]) if (vis.has(b)) links.push({ source: b, target: i.id });
      if (st.mode === 'scatter') { const j = rng(42); for (const n of nodes) { n.fx = (PH[n.i.ph] - 1) * 220 + (j() - 0.5) * 120; n.fy = (pIdx[n.i.p] - projOrder.length / 2) * 22 + (j() - 0.5) * 14; n.fz = ({ low: -1, medium: 0, high: 1, max: 1.6 }[n.i.e] || 0) * 140 + (j() - 0.5) * 60; } }
    } else {
      nodes = [{ id: 'root', name: 'PaperOS', val: 30, color: '#ffffff' }]; links = [];
      for (const k of projOrder) { const items = list.filter(i => i.p === k); if (!items.length) continue; nodes.push({ id: 'p:' + k, name: P[k].name, val: 12, color: hue(k) }); links.push({ source: 'root', target: 'p:' + k }); const ms = {}; for (const i of items) (ms[i.ms || '(no milestone)'] = ms[i.ms || '(no milestone)'] || []).push(i); for (const mk in ms) { const mid = `m:${k}:${mk}`; nodes.push({ id: mid, name: `${P[k].short} · ${mk}`, val: 4, color: hue(k) }); links.push({ source: 'p:' + k, target: mid }); for (const i of ms[mk]) { nodes.push({ id: i.id, i, val: { S: 1, M: 1.6, L: 2.6 }[i.sz] || 1.5 }); links.push({ source: mid, target: i.id }); } } }
    }
    const G = fg[kind] || (fg[kind] = ForceGraph3D()(box));
    G.width(w).height(h).backgroundColor('#070a12').showNavInfo(false)
      .nodeVal(n => n.val).nodeRelSize(2.2).nodeResolution(12).nodeOpacity(0.92)
      .nodeColor(n => n.i ? colorOf(n.i) : n.color)
      .nodeLabel(n => n.i ? `<div style="font:12px/1.4 system-ui;max-width:260px;background:#141a26;color:#e6ebf4;padding:6px 8px;border-radius:6px"><b>${n.i.id}</b> ${esc(n.i.t)}<div style="opacity:.7">${esc(short(n.i.p))} · ${esc(n.i.ty)} · ${esc(n.i.d ? 'Deferred' : n.i.s)}${n.i.m ? ' · ' + esc(n.i.m) + ' / ' + esc(n.i.e) : ''}</div></div>` : `<div style="font:12px system-ui;background:#141a26;color:#e6ebf4;padding:4px 8px;border-radius:6px">${esc(n.name)}</div>`)
      .linkColor(() => 'rgba(158,197,244,0.35)').linkOpacity(0.35).linkWidth(0).linkDirectionalArrowLength(isObj ? 2.5 : 0).linkDirectionalArrowRelPos(1)
      .dagMode(isObj ? null : 'radialout').dagLevelDistance(isObj ? null : 65)
      .onNodeClick(n => { const d = Math.hypot(n.x, n.y, n.z), dist = 60, ratio = d > 1 ? 1 + dist / d : 0; G.cameraPosition(d > 1 ? { x: n.x * ratio, y: n.y * ratio, z: n.z * ratio } : { x: n.x, y: n.y, z: n.z + dist }, { x: n.x, y: n.y, z: n.z }, 900); if (n.i) pin(n.i.id); })
      .graphData({ nodes, links });
    if (isObj && st.mode === 'force') G.d3Force('charge').strength(-40);
    const controls = G.controls(); controls.autoRotate = st.spin; controls.autoRotateSpeed = 0.6;
    box.addEventListener('pointerdown', () => { controls.autoRotate = false; const c = $('#fg-spin', mount); if (c) c.checked = false; }, { once: true });
    setTimeout(() => G.zoomToFit(600, 20), 1600);
    $('#fg-fit', mount).addEventListener('click', () => G.zoomToFit(600, 20));
    $('#fg-spin', mount).addEventListener('change', ev => { st.spin = ev.target.checked; controls.autoRotate = st.spin; });
    $('#fg-col', mount).addEventListener('change', ev => { st.col = ev.target.value; G.nodeColor(G.nodeColor()); });
    if (isObj) $('#fg-mode', mount).addEventListener('change', ev => { st.mode = ev.target.value; refresh(); });
  }
  const state3d = { 'objects-3d': { mode: 'force', col: 'project', spin: true }, 'radial-3d': { mode: 'tree', col: 'project', spin: true } };

  /* ---- registry, tabs, hash routing ---- */
  const views = { 'objects-map': viewObjectsMap, lanes: viewLanes, radial: viewRadial, images: viewImages, icons: viewIcons, 'objects-3d': (l, m) => view3d('objects-3d', l, m), 'radial-3d': (l, m) => view3d('radial-3d', l, m) };
  let active = 'objects-map';
  const pane = $('#vpane');
  function refresh() {
    const list = filtered();
    $('#f-cnt').innerHTML = `<b>${fmt(list.length)}</b> of ${fmt(canon.length)} issues · ${list.filter(i => i.s === 'Ready for Claude').length} ready`;
    if (fg[active === 'objects-3d' ? 'objects' : 'radial'] && !active.endsWith('-3d')) { /* leave WebGL contexts alone */ }
    pane.innerHTML = '';
    views[active](list, pane);
    if (pinned) document.querySelectorAll(`[data-id="${pinned}"]`).forEach(e => e.classList.add('pin'));
  }
  function show(v, scroll) {
    if (!views[v]) return; active = v;
    document.querySelectorAll('#vtabs .vtab').forEach(b => { const on = b.dataset.v === v; b.classList.toggle('on', on); b.setAttribute('aria-selected', on); });
    refresh();
    if (scroll) setTimeout(() => $('#views').scrollIntoView({ behavior: 'smooth', block: 'start' }), 30);
  }
  document.querySelectorAll('#vtabs .vtab').forEach(b => { if (b.dataset.v.endsWith('-3d')) b.insertAdjacentHTML('beforeend', `<span class="p3d">${MODE === 'pages' ? 'webgl' : 'preview'}</span>`); b.addEventListener('click', () => { show(b.dataset.v); history.replaceState(null, '', '#' + b.dataset.v); }); });
  renderFbar();
  const fromHash = () => { const h = location.hash.slice(1); if (views[h]) show(h, true); };
  addEventListener('hashchange', fromHash);
  if (views[location.hash.slice(1)]) fromHash(); else refresh();
  addEventListener('resize', () => { clearTimeout(V._rt); V._rt = setTimeout(() => { if (!active.endsWith('-3d')) refresh(); }, 200); });
  return { F, filtered, refresh, show, pin, skey, hue, shape, typeIcon, modelIcon, projectGlyph, blockersOf, blocksOf, setFilter };
})();
