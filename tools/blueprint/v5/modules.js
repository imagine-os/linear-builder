/* ===== v4 modules and plug points ===== */
(() => {
  const M = D.modules; if (!M || !M.length) return;
  const byKey = Object.fromEntries(M.map(m => [m.key, m]));
  const kernel = byKey['module-system'];
  const ring = M.filter(m => m.key !== 'module-system');
  const RISK = { critical: 0, high: 1, medium: 2, low: 3 };
  const PHO = { P0: 0, P1: 1, P2: 2 };
  const S = { sort: 'phase', risk: '', kind: '', kern: false };
  $('#nMod').textContent = M.length; $('#nContracts').textContent = ring.length;
  $('#modProjLink').href = kernel.url || '#';
  const tools = $('#modTools');
  const opt = (v, l, c) => `<option value="${v}"${v === c ? ' selected' : ''}>${l}</option>`;
  const kinds = [...new Set(M.map(m => m.kind))];
  function renderTools() {
    tools.innerHTML = `<label class="small">Order around the ring <select id="md-sort">${opt('phase', 'phase, then plan order', S.sort)}${opt('req', 'most requires first', S.sort)}${opt('dep', 'most depended-on first', S.sort)}${opt('risk', 'swap risk', S.sort)}${opt('alpha', 'alphabetical', S.sort)}</select></label>
      <label class="small">Swap risk <select id="md-risk">${opt('', 'all', S.risk)}${['critical', 'high', 'medium', 'low'].map(r => opt(r, r, S.risk)).join('')}</select></label>
      <label class="small">Kind <select id="md-kind">${opt('', 'all', S.kind)}${kinds.map(k => opt(k, k, S.kind)).join('')}</select></label>
      <label class="ck small"><input type="checkbox" id="md-kern"${S.kern ? ' checked' : ''}> show kernel bindings</label><span class="sp"></span><span class="small mute">${ring.length} contract packages · ${ring.reduce((a, m) => a + m.requires.length, 0)} requires edges · ${M.filter(m => m.risk === 'critical').length} critical modules</span>`;
    $('#md-sort').addEventListener('change', ev => { S.sort = ev.target.value; draw(); });
    $('#md-risk').addEventListener('change', ev => { S.risk = ev.target.value; draw(); });
    $('#md-kind').addEventListener('change', ev => { S.kind = ev.target.value; draw(); });
    $('#md-kern').addEventListener('change', ev => { S.kern = ev.target.checked; draw(); });
  }
  const sorters = {
    phase: (a, b) => PHO[a.phase] - PHO[b.phase] || D.projects.findIndex(p => p.key === a.key) - D.projects.findIndex(p => p.key === b.key),
    req: (a, b) => b.requires.length - a.requires.length || a.short.localeCompare(b.short),
    dep: (a, b) => b.dependents.length - a.dependents.length || a.short.localeCompare(b.short),
    risk: (a, b) => RISK[a.risk] - RISK[b.risk] || a.short.localeCompare(b.short),
    alpha: (a, b) => a.short.localeCompare(b.short)
  };
  const svg = $('#modsvg'); const W = 1080, H = 800; svg.setAttribute('viewBox', `0 0 ${W} ${H}`);
  let selected = null, els = {}, edgeEls = [];
  const contractShort = m => m.contract.replace('@paperos/', '');
  const splitName = s => { if (s.length <= 15) return [s]; const words = s.split(' '); let a = '', b = ''; for (const w of words) { if ((a + ' ' + w).trim().length <= Math.ceil(s.length / 2) + 2 && !b) a = (a + ' ' + w).trim(); else b = (b + ' ' + w).trim(); } return b ? [a, b] : [a]; };
  function draw() {
    svg.innerHTML = ''; els = {}; edgeEls = [];
    const shown = ring.filter(m => (!S.risk || m.risk === S.risk) && (!S.kind || m.kind === S.kind)).sort(sorters[S.sort]);
    const defs = svgEl('defs', {}, svg);
    for (const [id, cls] of [['mah', ''], ['mah-out', 'm-out'], ['mah-in', 'm-in']]) { const mk = svgEl('marker', { id, class: cls, viewBox: '0 0 10 10', refX: 9, refY: 5, markerWidth: 6, markerHeight: 6, orient: 'auto', markerUnits: 'userSpaceOnUse' }, defs); svgEl('path', { d: 'M0 1L9 5L0 9z' }, mk); }
    const cx = W / 2, cy = H / 2 + 6, rx = 430, ry = 318, bw = 134, bh = 54, pw = 84, ph = 14;
    svgEl('ellipse', { class: 'ring', cx, cy, rx, ry }, svg);
    const gE = svgEl('g', {}, svg), gN = svgEl('g', {}, svg);
    const pos = {};
    shown.forEach((m, i) => { const a = -Math.PI / 2 + 2 * Math.PI * i / shown.length; pos[m.key] = { x: cx + rx * Math.cos(a), y: cy + ry * Math.sin(a), a }; });
    // kernel
    pos['module-system'] = { x: cx, y: cy, a: 0 };
    const plugPos = k => { const p = pos[k]; if (k === 'module-system') return { x: cx, y: cy + 44 }; const ux = (cx - p.x), uy = (cy - p.y), L = Math.hypot(ux, uy), dx = ux / L, dy = uy / L; const t = Math.min(Math.abs(dx) > 1e-6 ? (bw / 2) / Math.abs(dx) : 1e9, Math.abs(dy) > 1e-6 ? (bh / 2) / Math.abs(dy) : 1e9); const d = t + 10 + ph / 2; return { x: p.x + dx * d, y: p.y + dy * d, ux: dx, uy: dy, t }; };
    const edge = (fromKey, toKey, cls) => {
      const a = pos[fromKey], b = plugPos(toKey); if (!a || !b) return null;
      const mx = (a.x + b.x) / 2, my = (a.y + b.y) / 2; const px = cx + (mx - cx) * 0.45, py = cy + (my - cy) * 0.45;
      const ax = a.x + (b.x - a.x) * 0.12, ay = a.y + (b.y - a.y) * 0.12;
      const p = svgEl('path', { class: 'req ' + cls, d: `M${ax.toFixed(1)},${ay.toFixed(1)} Q${px.toFixed(1)},${py.toFixed(1)} ${(b.x - (b.ux || 0) * 10).toFixed(1)},${(b.y - (b.uy || 0) * 10).toFixed(1)}`, 'marker-end': cls ? '' : 'url(#mah)' }, gE);
      return p;
    };
    for (const m of shown) {
      for (const r of m.requires) { if (!pos[r]) continue; const p = edge(m.key, r, ''); if (p) { edgeEls.push({ from: m.key, to: r, el: p }); bindTip(p, `<b>${esc(m.short)} requires ${esc(contractShort(byKey[r]))}</b><div class="mu">${esc(byKey[r].short)} owns the contract (${esc(byKey[r].owner)}); ${esc(m.short)} may import only that package, never the implementation.</div>`); } }
      if (S.kern) edge(m.key, 'module-system', 'kern');
    }
    const drawModule = (m, isK) => {
      const p = pos[m.key]; const g = svgEl('g', { class: `mod risk-${m.risk}${isK ? ' kern' : ''}`, tabindex: 0, role: 'button', 'aria-label': `${m.short}: ${m.kind}, swap risk ${m.risk}` }, gN);
      const w = isK ? 170 : bw, h = isK ? 64 : bh;
      svgEl('rect', { class: 'box', x: p.x - w / 2, y: p.y - h / 2, width: w, height: h, rx: 8, stroke: m.color }, g);
      svgEl('rect', { x: p.x - w / 2, y: p.y - h / 2, width: 6, height: h, rx: 3, fill: m.color }, g);
      const lines = isK ? ['@paperos/kernel'] : splitName(m.short);
      lines.forEach((ln, li) => { const nm = svgEl('text', { class: 'nm', x: p.x + 3, y: p.y - (isK ? 8 : (lines.length === 2 ? 9 : 3)) + li * 13 }, g); nm.textContent = ln; });
      const kd = svgEl('text', { class: 'kd', x: p.x + 3, y: p.y + (isK ? 8 : 18) }, g); kd.textContent = isK ? 'the middle tooling' : `${m.kind} · ${m.risk}`;
      // plug: the contract package, on the inner side
      const q = plugPos(m.key);
      const plug = svgEl('rect', { class: 'plug', x: q.x - pw / 2, y: q.y - ph / 2, width: pw, height: ph, rx: 3, stroke: m.color }, g);
      if (!isK) { svgEl('line', { x1: p.x + q.ux * q.t, y1: p.y + q.uy * q.t, x2: q.x - q.ux * (ph / 2), y2: q.y - q.uy * (ph / 2), stroke: m.color, 'stroke-width': 2 }, g); }
      svgEl('circle', { class: 'pin', cx: q.x, cy: q.y, r: 3.2, fill: m.color }, g);
      const pl = svgEl('text', { class: 'plug-l', x: q.x, y: q.y + ph / 2 + 10 }, g); pl.textContent = isK ? 'kernel' : contractShort(m).replace('contract-', 'contract-');
      bindTip(plug, `<b>${esc(m.contract)}</b><div class="mu">plug point: types, Zod schemas, event topics, route signatures, slot definitions, port interfaces, conformance suite, golden fixtures. No runtime, no React, no database. ${m.dependents.length} module${m.dependents.length === 1 ? '' : 's'} plug in.</div>`);
      bindTip(g, () => `<b>${esc(m.short)}</b> · ${esc(m.kind)}<div class="mu">owner ${esc(m.owner)} · swap risk ${m.risk} · requires ${m.requires.length} · required by ${m.dependents.length}</div><div class="mu">${P[m.key] ? P[m.key].total + ' issues in Linear · ' : ''}click for ports and the contract issues</div>`);
      g.addEventListener('click', () => select(selected === m.key ? null : m.key));
      g.addEventListener('keydown', ev => { if (ev.key === 'Enter' || ev.key === ' ') { ev.preventDefault(); select(selected === m.key ? null : m.key); } });
      els[m.key] = g;
    };
    for (const m of shown) drawModule(m, false);
    drawModule(kernel, true);
    svg.addEventListener('click', ev => { if (ev.target === svg || ev.target.classList.contains('ring')) select(null); });
    select(selected && (els[selected] ? selected : null));
    $('#modCap').textContent = `${shown.length} modules on the ring, ordered by ${$('#md-sort').selectedOptions[0].textContent}; ${edgeEls.length} requires edges drawn from a module to the contract package it depends on. Every module also binds into the kernel (toggle above). Layout after the graph-gallery radial demos; data from docs/module-system.md table 1.1 and the live Linear issues.`;
  }
  function select(key) {
    selected = key; svg.classList.toggle('has-sel', !!key);
    for (const k in els) els[k].classList.remove('sel', 'nb', 'out', 'in');
    for (const e of edgeEls) { e.el.classList.remove('on', 'out', 'in'); e.el.setAttribute('marker-end', 'url(#mah)'); }
    if (key && els[key]) {
      els[key].classList.add('sel');
      for (const e of edgeEls) { if (e.from === key) { e.el.classList.add('on', 'out'); e.el.setAttribute('marker-end', 'url(#mah-out)'); if (els[e.to]) els[e.to].classList.add('nb', 'out'); } else if (e.to === key) { e.el.classList.add('on', 'in'); e.el.setAttribute('marker-end', 'url(#mah-in)'); if (els[e.from]) els[e.from].classList.add('nb', 'in'); } }
      for (const e of edgeEls) if (e.el.classList.contains('on')) e.el.parentNode.appendChild(e.el);
    }
    renderSide(key);
  }
  const pill = id => { const i = byId[id]; if (!i) return '<span class="mute">not yet created</span>'; return `<a href="${esc(i.url)}" title="${esc(i.t)}">${id}</a><span class="pill${i.s === 'Ready for Claude' ? ' ready' : ''}">${esc(i.s)}</span>`; };
  function renderSide(key) {
    const s = $('#modSide');
    if (!key) { s.innerHTML = `<div class="k">How to read this</div><p>Each box is a module (one Linear project). The small socket on its inner side is its <b>contract package</b>, the only thing other modules may import. An arrow from a module to a socket is a <span class="mono">requires</span> entry in its manifest. The kernel in the middle resolves every arrow at boot and can swap the implementation behind any socket with a flag.</p><p>Blue arrows: what the selected module waits on. Orange: who plugs into it. Border weight is swap risk: solid heavy for <span class="risk critical">critical</span>, dashed for <span class="risk low">low</span>.</p><p class="mute small">Click a module, or press Enter on it, for its ports, owner and the three Linear issues that publish, prove and wire its contract.</p>`; return; }
    const m = byKey[key]; const pr = P[key];
    const reqLinks = m.requires.map(r => `<li class="up"><b><a href="#modules" data-mod="${r}">${esc(byKey[r].short)}</a></b><span class="n mono">${esc(contractShort(byKey[r]))}</span></li>`).join('') || '<li class="mute">contract-zero only (@paperos/core)</li>';
    const depLinks = m.dependents.map(r => `<li class="down"><b><a href="#modules" data-mod="${r}">${esc(byKey[r].short)}</a></b><span class="n">${byKey[r].risk}</span></li>`).join('') || '<li class="mute">nothing requires it yet</li>';
    const trio = m.trio ? `<div class="row"><div class="k">Linear: publish, prove, wire</div><div class="trio"><div><span class="k">contract v0.1</span><span>${pill(m.trio.contract)}</span></div><div><span class="k">conformance</span><span>${pill(m.trio.conformance)}</span></div><div><span class="k">wire + flag</span><span>${pill(m.trio.wire)}</span></div></div></div>` : `<div class="row"><div class="k">Linear: the fourteen kernel pieces</div><p class="small">${D.kernelPieces.map(k => `<a href="${esc(k.url)}" title="${esc(k.piece)}">${k.id.replace('PAP-', '')}</a>`).join(' · ')} — listed below.</p></div>`;
    s.innerHTML = `<div><div class="k">${esc(m.kind)} · owner ${esc(m.owner)} · <span class="risk ${m.risk}">${m.risk}</span></div><h3>${esc(pr ? pr.name : m.short)}</h3><div class="mono small">${esc(m.contract)}</div></div>
      <div class="stats"><div class="stat"><span class="v">${m.provides.length}</span><span class="l">ports provided</span></div><div class="stat"><span class="v">${m.requires.length}</span><span class="l">contracts required</span></div><div class="stat"><span class="v">${m.dependents.length}</span><span class="l">modules plug in</span></div></div>
      <div class="row"><div class="k">Provides (the plug)</div><div class="ports">${m.provides.map(p => `<span class="chip">${esc(p)}</span>`).join('')}</div></div>
      <div class="row"><div class="k">Requires · waits on</div><ul>${reqLinks}</ul></div>
      <div class="row"><div class="k">Required by · unblocks</div><ul>${depLinks}</ul></div>
      ${trio}
      <div class="row"><div class="k">In the Linear blocks graph</div><p class="small mute">${m.linearOut} issues elsewhere wait on ${esc(m.short)}; ${m.linearIn} of its issues wait on other projects. ${m.risk === 'critical' ? 'A breaking change to this contract is a Needs Justin card (NJ-22).' : m.risk === 'high' ? 'A swap needs conformance plus a canary flip.' : m.risk === 'medium' ? 'A swap needs the conformance suite only.' : 'A swap is a version bump and a green CI.'}</p></div>
      <div class="small">${pr ? `<a href="${esc(pr.url)}">Project in Linear</a> · ` : ''}<a href="#views" data-view="${key}">See its issues in the views ↓</a></div>`;
    s.querySelectorAll('[data-mod]').forEach(a => a.addEventListener('click', ev => { ev.preventDefault(); select(a.dataset.mod); }));
    const v = s.querySelector('[data-view]'); if (v) v.addEventListener('click', ev => { ev.preventDefault(); V.setFilter('p', key); V.show('objects-map', true); });
  }
  /* kernel pieces and playbook */
  $('#kpieces').innerHTML = D.kernelPieces.map(k => `<div class="kpiece"><div class="hd"><b>${esc(k.piece)}</b><a href="${esc(k.url)}">${k.id}</a></div><div class="sv">serves ${esc(k.serves)} · <span class="pill${k.state === 'Ready for Claude' ? ' ready' : ''}">${esc(k.state)}</span></div><p>${linkify(k.behaviour)}</p></div>`).join('');
  $('#playbook').innerHTML = D.playbook.map((p, i) => `<div class="pstep${i >= 3 && i <= 5 ? ' rb' : ''}"><b>${esc(p.step)}</b><span>${esc(p.gate)}</span></div>`).join('');
  renderTools(); draw();
})();
