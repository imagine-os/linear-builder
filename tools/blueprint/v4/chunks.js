/* ===== v4 $2,500 chunks ===== */
(() => {
  const C = D.chunks;
  const sec = $('#chunks');
  if (!C) { sec.querySelector('header p').insertAdjacentHTML('afterend', '<p class="note">No chunk plan file (plan/chunks.json) was available when this page was built.</p>'); return; }
  const S = { mix: C.recommended || 'B', def: true };
  const money = n => '$' + Number(n).toLocaleString('en-US', { maximumFractionDigits: 0 });
  const money2 = n => '$' + Number(n).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  const MON = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
  const parse = s => Date.parse(s.length === 17 ? s.replace('Z', ':00Z') : s);
  const ft = s => { const d = new Date(parse(s)); return `${MON[d.getUTCMonth()]} ${d.getUTCDate()} ${String(d.getUTCHours()).padStart(2, '0')}:${String(d.getUTCMinutes()).padStart(2, '0')}Z`; };
  const t0 = parse(C.terms.start);
  const hrs = s => (parse(s) - t0) / 3600000;
  const short = k => (P[k] && P[k].short) || k;
  const tools = $('#chTools');
  const opt = (v, l, c) => `<option value="${v}"${v === c ? ' selected' : ''}>${l}</option>`;
  function renderTools() {
    tools.innerHTML = `<label class="small">Model mix <select id="ch-mix">${Object.keys(C.mixes).map(k => opt(k, `mix ${k}: ${C.mixes[k].description}${k === C.recommended ? ' (recommended)' : ''}`, S.mix)).join('')}</select></label><label class="ck small"><input type="checkbox" id="ch-def"${S.def ? ' checked' : ''}> include the optional deferred chunk</label><span class="sp"></span><span class="small mute">$${C.terms.chunkListUsd.toLocaleString('en-US')} list = $${C.terms.discountedPerChunkUsd} to Justin · ${C.terms.builders} builders · ${C.terms.hoursPerDay} h/day</span>`;
    $('#ch-mix').addEventListener('change', ev => { S.mix = ev.target.value; render(); });
    $('#ch-def').addEventListener('change', ev => { S.def = ev.target.checked; render(); });
  }
  function render() {
    const mix = C.mixes[S.mix], T = mix.totals, chunks = mix.chunks, def = S.def ? mix.deferred : null;
    const endH = hrs(def ? def.end : T.end);
    /* KPIs */
    $('#chKpis').innerHTML = [
      { v: `${money2(T.discountedCost)}`, l: 'to Justin for the 1 October scope', s: `${money(T.listCost)} list · ${T.wholeChunksBilled} chunks billed whole = ${money(T.wholeChunksBilledUsd)}`, cls: 'cost' },
      { v: `${T.chunks}<small>chunks</small>`, l: `of $2,500 list each`, s: `${T.issues} buildable issues + 4 RC reviews` },
      { v: `${T.wallClockHours}<small>hours</small>`, l: `${T.wallClockDays24h} days at ${C.terms.builders} builders, 24/7`, s: `ends ${ft(T.end)} if every answer is in hand` },
      def ? { v: `+${money2(def.discountedCost)}`, l: `for the ${def.count} deferred issues after NJ-14`, s: `${money(def.listCost)} list · +${def.hours} h · ${def.equivalentChunks} of a chunk` } : { v: `${money(T.byPhase.P0)}<small>P0</small>`, l: `list cost of the foundation phase`, s: `P1 ${money(T.byPhase.P1)} · P2 ${money(T.byPhase.P2)}` }
    ].map(k => `<div class="kpi ${k.cls || ''}"><div class="v">${k.v}</div><div class="l">${k.l}</div><div class="s">${k.s}</div></div>`).join('');
    /* timeline */
    const svg = $('#chsvg'); svg.innerHTML = '';
    const W = 1000, L = 20, R = 20, top = 84, bh = 54, H = top + bh + 62; svg.setAttribute('viewBox', `0 0 ${W} ${H}`);
    const defs = svgEl('defs', {}, svg); const pat = svgEl('pattern', { id: 'hatch', width: 6, height: 6, patternUnits: 'userSpaceOnUse', patternTransform: 'rotate(45)' }, defs); svgEl('rect', { width: 6, height: 6, fill: 'var(--card-2)' }, pat); svgEl('rect', { width: 2.5, height: 6, fill: 'var(--st-deferred)' }, pat);
    const x = h => L + (W - L - R) * h / Math.max(1, endH);
    svgEl('line', { class: 'axis', x1: L, y1: top + bh + 14, x2: W - R, y2: top + bh + 14 }, svg);
    for (let h = 0; h <= endH; h += 6) { const t = svgEl('text', { class: 'tick', x: x(h), y: top + bh + 30 }, svg); t.textContent = h === 0 ? 'start' : `+${h} h`; svgEl('line', { class: 'axis', x1: x(h), y1: top + bh + 10, x2: x(h), y2: top + bh + 18 }, svg); }
    // midnight lines
    for (let d = new Date(t0); d.getTime() < t0 + endH * 3600000; d = new Date(d.getTime() + 86400000)) { const m = new Date(Date.UTC(d.getUTCFullYear(), d.getUTCMonth(), d.getUTCDate() + 1)); const h = (m - t0) / 3600000; if (h > endH) break; svgEl('line', { class: 'day', x1: x(h), y1: top - 6, x2: x(h), y2: top + bh + 8 }, svg); const t = svgEl('text', { class: 'day-l', x: x(h) + 4, y: top - 10 }, svg); t.textContent = `${MON[m.getUTCMonth()]} ${m.getUTCDate()} 00:00Z`; }
    const rcXs = []; const bars = chunks.map(c => ({ ...c, cls: 'c' + Math.min(5, c.n) }));
    if (def) bars.push({ ...def, n: 'optional', cls: 'def', discountedCost: def.discountedCost, count: def.count, isDef: true });
    for (const c of bars) {
      const x0 = x(hrs(c.start)), x1 = x(hrs(c.end)), w = Math.max(2, x1 - x0);
      const r = svgEl('rect', { class: `bar ${c.cls}`, x: x0, y: top, width: w, height: bh, rx: 6 }, svg);
      const light = c.cls === 'c1' || c.cls === 'c2' || c.cls === 'c3';
      if (w > 56) { const t = svgEl('text', { class: 'bar-l' + (light ? ' light' : ''), x: x0 + w / 2, y: top + (w > 150 ? 22 : 31) }, svg); t.textContent = c.isDef ? `+${money2(c.discountedCost)}` : money2(c.discountedCost); if (w > 150) { const s = svgEl('text', { class: 'bar-s' + (light ? ' light' : ''), x: x0 + w / 2, y: top + 38 }, svg); s.textContent = c.isDef ? `deferred · ${c.count} issues · ${c.hours} h` : `chunk ${c.n} · ${c.count} issues · ${c.hours} h`; } }
      bindTip(r, `<b>${c.isDef ? 'Optional deferred chunk' : 'Chunk ' + c.n}</b> · ${money2(c.discountedCost)} to Justin (${money(c.listCost)} list)<div class="mu">${ft(c.start)} → ${ft(c.end)} · ${c.hours} h · ${c.count} issues</div>${c.isDef ? '' : `<div class="mu">${c.milestones.length} milestones done · ${c.rcs.map(r => r.rc).join(', ') || 'no RC'} · ${c.nj.length} Needs Justin first</div>`}`);
      r.addEventListener('click', () => { const card = $(`#chunk-${c.isDef ? 'def' : c.n}`); if (card) card.scrollIntoView({ behavior: 'smooth', block: 'center' }); });
      if (!c.isDef) {
        for (const rc of c.rcs) { const rx = x(hrs(rc.at)); const lift = rcXs.some(px => Math.abs(px - rx) < 26) ? 22 : 0; rcXs.push(rx); const d = svgEl('path', { class: 'rc', d: `M${rx},${top - 22 - lift}l7,7l-7,7l-7,-7z` }, svg); bindTip(d, `<b>${esc(rc.rc)} review · ${ft(rc.at)}</b><div class="mu">${esc(rc.label)}</div><div class="mu">gate issues: ${rc.gates.map(g => g.replace('PAP-', '')).join(', ')}</div>`); const t = svgEl('text', { class: 'rc-l', x: rx, y: top - 28 - lift }, svg); t.textContent = rc.rc; }
        if (c.nj.length) { const nx = x(hrs(c.start)) + 2; const g = svgEl('g', {}, svg); const open = c.nj.filter(n => n.status !== 'resolved').length; svgEl('circle', { class: 'nj', cx: nx + 7, cy: top + bh + 46, r: 7 }, g); const t = svgEl('text', { class: 'nj-l', x: nx + 7, y: top + bh + 49, fill: '#fff', style: 'fill:#fff;font-weight:700' }, g); t.textContent = open; const l = svgEl('text', { class: 'nj-l', x: nx + 19, y: top + bh + 49, style: 'text-anchor:start' }, g); l.textContent = 'Needs Justin first'; bindTip(g, `<b>${open} decision${open === 1 ? '' : 's'} before chunk ${c.n} starts</b><div class="mu">${c.nj.map(n => esc(n.id)).join(', ')}</div>`); }
      }
    }
    $('#chCap').textContent = `Mix ${S.mix}: ${T.chunks} chunks over ${T.wallClockHours} hours of session time from ${ft(C.terms.start)}, ${money(T.listCost)} list, ${money2(T.discountedCost)} to Justin${def ? `, plus the optional deferred chunk (${money2(def.discountedCost)}, ${def.hours} h) after the stop-loss go` : ''}. Orange diamonds are the four release-candidate reviews; the red count under a chunk is the Needs Justin decisions it needs answered before it starts. Chunks overlap at their edges: sixteen builders are mid-issue when a dollar boundary passes.`;
    /* cards */
    const phaseBar = bp => { const tot = Object.values(bp).reduce((a, n) => a + n, 0) || 1; return `<div class="pbar">${['P0', 'P1', 'P2'].map(k => bp[k] ? `<i class="${k.toLowerCase()}" style="flex:${bp[k]} ${bp[k]} 0" title="${k}: ${bp[k]}"></i>` : '').join('')}</div><div class="plg">${['P0', 'P1', 'P2'].map(k => `<span>${k} ${bp[k] || 0}</span>`).join('')}</div>`; };
    const njItem = n => `<li><span class="tag${n.status === 'resolved' ? ' ok' : ''}">${esc(n.id)}</span><span>${linkify(n.text.replace(/^NJ-\d+[^:]*:\s*/, ''))}</span></li>`;
    const card = c => {
      const projs = Object.entries(c.byProject).sort((a, b) => b[1].n - a[1].n);
      const types = Object.entries(c.byType).sort((a, b) => b[1] - a[1]).map(([k, n]) => `${k} ${n}`).join(' · ');
      const models = Object.entries(c.byBuilderModel).map(([k, n]) => `${k.replace('claude-', '').replace('-5-1', ' 5.1').replace('-5', ' 5')} ${n}`).join(' · ');
      return `<div class="chunk c${Math.min(5, c.n)}" id="chunk-${c.n}"><div class="hd"><h3>Chunk ${c.n}</h3><span class="mono small mute">${ft(c.start)} → ${ft(c.end)}</span></div>
        <div class="cost">${money2(c.discountedCost)}<small>${money(c.listCost)} list</small></div>
        <div class="facts"><div class="fact"><span class="v">${c.count}</span><span class="l">issues</span></div><div class="fact"><span class="v">${c.hours} h</span><span class="l">session time</span></div><div class="fact"><span class="v">${c.milestones.length}</span><span class="l">milestones done</span></div></div>
        <div><div class="k">By phase</div>${phaseBar(c.byPhase)}</div>
        <div><div class="k">Delivers</div><ul>${c.rcs.map(r => `<li><span class="tag rc">${esc(r.rc)}</span><span><b>${esc(r.label.replace(/^RC\d\s*/, ''))}</b> · review at ${ft(r.at)}</span></li>`).join('')}${c.milestones.length ? `<li><span class="tag rc" style="background:var(--card-2);color:var(--ink-2)">${c.milestones.length} ms</span><span><details><summary>${c.milestones.slice(0, 2).map(m => `<b>${esc(short(m.project))}</b> · ${esc(m.name)}`).join('; ')}${c.milestones.length > 2 ? ` and ${c.milestones.length - 2} more` : ''}</summary><ul style="margin-top:6px">${c.milestones.map(m => `<li><span class="mono small">${fdate(m.date)}</span><span><b>${esc(short(m.project))}</b> · ${esc(m.name)} <span class="mute">· ${m.issues} issues${m.excluded ? `, ${m.excluded} deferred excluded` : ''} · done ${ft(m.at)}</span></span></li>`).join('')}</ul></details></span></li>` : ''}${!c.rcs.length && !c.milestones.length ? '<li><span class="mute">no milestone closes in this chunk</span></li>' : ''}</ul></div>
        <div><div class="k">Needs Justin before it starts</div><ul>${c.nj.length ? c.nj.map(njItem).join('') : '<li><span class="mute">nothing new; earlier answers carry over</span></li>'}</ul></div>
        <div><div class="k">Projects · ${types}</div><div class="chips">${projs.slice(0, 8).map(([k, v]) => `<span class="chip" title="${esc(P[k] ? P[k].name : k)}">${esc(short(k))} <b>${v.n}</b>${v.umbrellas.length ? ` · closes ${v.umbrellas.map(u => u.replace('PAP-', '')).join(', ')}` : ''}</span>`).join('')}${projs.length > 8 ? `<span class="chip">+${projs.length - 8} more</span>` : ''}</div><p class="small mute" style="margin-top:6px">builders: ${models}</p></div>
      </div>`;
    };
    const defCard = d => d ? `<div class="chunk def" id="chunk-def"><div class="hd"><h3>Optional: the deferred set</h3><span class="mono small mute">${ft(d.start)} → ${ft(d.end)}</span></div>
        <div class="cost">+${money2(d.discountedCost)}<small>${money(d.listCost)} list · ${d.equivalentChunks} of a chunk</small></div>
        <div class="facts"><div class="fact"><span class="v">${d.count}</span><span class="l">deferred leaves</span></div><div class="fact"><span class="v">${d.hours} h</span><span class="l">after RC3</span></div><div class="fact"><span class="v">v0.2</span><span class="l">milestone after NJ-19</span></div></div>
        <div><div class="k">Needs Justin before it starts</div><ul>${d.nj.map(n => njItem(typeof n === 'string' ? { id: n.split(':')[0], text: n, status: 'open' } : n)).join('') || '<li><span class="tag">NJ-14</span><span>Stop-loss checkpoint: go or no-go on the stretch pool.</span></li>'}</ul></div>
        <div><div class="k">Projects</div><div class="chips">${Object.entries(d.byProject).sort((a, b) => b[1] - a[1]).map(([k, n]) => `<span class="chip">${esc(short(k))} <b>${n}</b></span>`).join('')}</div><p class="small mute" style="margin-top:6px">${esc(d.note)}</p></div></div>` : '';
    $('#chList').innerHTML = chunks.map(card).join('') + defCard(def);
    $('#chTerms').innerHTML = `<b>Terms.</b> ${esc(C.terms.scheduler)}. ${esc(C.terms.costModel)}. Prices per MTok: Fable 5.1 $${C.terms.prices.fable.inp} in / $${C.terms.prices.fable.out} out, Opus 5 $${C.terms.prices.opus.inp} / $${C.terms.prices.opus.out}, Sonnet 5 $${C.terms.prices.sonnet.inp} / $${C.terms.prices.sonnet.out}. Generated ${esc(C.generatedAt)} from the ${esc(C.snapshotTakenAt)} snapshot (326 buildable issues before the 65 round-3 module issues were created; the module issues add roughly one more chunk at list price and are priced in the next regeneration). Full tables: <a href="${D.repo}/blob/main/docs/build-chunks.md">docs/build-chunks.md</a>.`;
  }
  /* discount strip in the budget section */
  { const d = $('#disc'); if (d) { const B = C.mixes[C.recommended]; d.innerHTML = `<div><span class="v">$50</span><span class="l">per $2,500 of list spend (×0.02)</span></div><div><span class="v">$200</span><span class="l">the whole $10,000 budget, to Justin</span></div><div><span class="v">${money2(B.totals.discountedCost)}</span><span class="l">mix ${C.recommended}, 1 October scope</span></div><div><span class="v">${money2(C.mixes.A.totals.discountedCost)}</span><span class="l">mix A, Fable 5.1 everywhere</span></div>`; } }
  renderTools(); render();
})();
