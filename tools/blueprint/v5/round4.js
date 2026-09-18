/* ===== v5 round 4: initiatives, cycles, estimates, what changed ===== */
(() => {
  const ORDER = ['triage', 'backlog', 'ready', 'progress', 'review', 'justin', 'done', 'deferred'];
  const NAMES = { triage: 'Triage', backlog: 'Backlog', ready: 'Ready for Claude', progress: 'In Progress', review: 'In Review', justin: 'Needs Justin', done: 'Done', deferred: 'Deferred (v0.2)' };
  const pts = n => `${fmt(n)} pt`;
  const projChip = k => { const p = P[k]; return p ? `<span class="chip" data-k="${k}" title="${esc(p.name)}"><i style="background:${p.color}"></i>${esc(p.short)}</span>` : ''; };
  const bindChips = root => root.querySelectorAll('.chip[data-k]').forEach(c => c.addEventListener('click', () => { if (typeof V !== 'undefined' && V.setFilter) { V.setFilter('p', c.dataset.k); V.show('objects-map', true); } }));
  const bar = (counts, total, label) => { const d = el('div', 'sbar'); for (const k of ORDER) { const n = counts[k] || 0; if (!n) continue; const i = el('i', 'f-' + k); i.style.flex = `${n} ${n} 0`; bindTip(i, `<b>${NAMES[k]}</b> · ${fmt(n)} of ${fmt(total)}${label ? `<div class="mu">${label}</div>` : ''}`); d.appendChild(i); } return d; };

  /* ---- initiatives ---- */
  { const wrap = $('#iniCards'); const I = D.initiatives || [];
    $('#nIni').textContent = I.length;
    for (const x of I) {
      const c = el('div', 'inicard' + (x.r4 ? ' r4' : ''));
      const pct = Math.round(100 * x.progress);
      c.innerHTML = `<div class="hd"><h3><a href="${esc(x.url)}">${esc(x.name)}</a></h3><span class="tag${x.r4 ? ' new' : ''}">${x.r4 ? 'new in round 4' : esc(x.status || 'Active')}</span></div>
        <p>${esc(x.description)}</p>
        <div class="projs">${x.projects.map(projChip).join('')}</div>
        <div class="facts"><div class="fact"><span class="v">${x.projects.length}</span><span class="l">projects</span></div><div class="fact"><span class="v">${fmt(x.issues)}</span><span class="l">issues · ${x.leaves} leaves</span></div><div class="fact"><span class="v">${fmt(x.points)}</span><span class="l">points</span></div><div class="fact"><span class="v">${x.ready}</span><span class="l">ready now</span></div></div>
        <div class="prog"><div class="track"><i style="width:${Math.max(0, Math.min(100, pct))}%"></i></div><div class="lbl"><span>${pts(x.pointsDone)} done</span><span>${pct}% of ${pts(x.points)}</span></div></div>
        <div class="sb"></div>
        <div class="foot"><span>${x.deferred} deferred to v0.2 · ${x.newRound4} issues added in round 4</span><span>target ${x.targetDate ? fdate(x.targetDate) : '—'} · owner ${esc(x.owner || 'Justin')}</span></div>`;
      $('.sb', c).appendChild(bar(x.byState, x.issues, x.name));
      wrap.appendChild(c);
    }
    bindChips(wrap);
    const owned = new Set(I.flatMap(x => x.projects));
    const orphan = D.projects.filter(p => !owned.has(p.key));
    $('#iniNote').innerHTML = `${I.length} initiatives cover ${owned.size} of ${D.projects.length} projects${orphan.length ? ` (not in an initiative: ${orphan.map(p => esc(p.short)).join(', ')})` : ''}. Initiatives are workspace-level on the Basic plan (team initiatives need Business); each carries an outcome, why, done criteria and a reading list as its content. Progress counts points in Done only: nothing has merged yet, so every bar reads 0.`;
  }

  /* ---- cycles strip ---- */
  { const C = D.cycles || { list: [] }; const strip = $('#cyStrip'); $('#nCy').textContent = C.list.length;
    const maxPts = Math.max(1, ...C.list.flatMap(c => [c.points, c.plannedPoints]), C.noCycle.points);
    const row = (k, v, cls, label) => `<div class="row"><span class="k">${k}</span><div class="bar"><i class="${cls}" style="width:${(100 * v / maxPts).toFixed(1)}%"></i></div><span class="v" title="${esc(label)}">${fmt(v)} pt</span></div>`;
    for (const c of C.list) {
      const card = el('div', 'cycard' + (c.active ? ' active' : ''));
      card.innerHTML = `<div class="hd"><b>${c.short}</b><span class="tag${c.active ? ' on' : ''}">${c.active ? 'active' : c.endsAt < D.today ? 'closed' : 'upcoming'}</span></div>
        <div class="nm">${esc(c.name.replace(/^C\d\s*/, ''))}</div>
        <div class="dates">${fdate(c.startsAt)} → ${fdate(c.endsAt)}${c.chunks.length && c.chunks.length <= 3 ? ` · chunk${c.chunks.length > 1 ? 's' : ''} ${c.chunks.join(', ')}` : c.chunks.length ? ' · all chunks' : ''}</div>
        <div class="pair">${row('assigned', c.points, 'asg', `${c.issues} issues carry this cycle in Linear`)}${row('due inside', c.plannedPoints, 'pln', `${c.plannedIssues} leaf issues have a due date inside the window`)}</div>
        <div class="sb"></div>
        <div class="small mute">${c.issues} issues assigned · ${c.plannedIssues} due in the window</div>`;
      $('.sb', card).appendChild(bar(c.byState, c.issues || 1, `${c.short} assigned issues by state`));
      bindTip($('.dates', card), `<b>${esc(c.name)}</b><div class="mu">${esc(c.description || '')}</div>`);
      strip.appendChild(card);
    }
    const nc = el('div', 'cycard muted');
    nc.innerHTML = `<div class="hd"><b>No cycle</b><span class="tag">backlog</span></div><div class="nm">Specified, not yet claimed</div><div class="dates">joins a cycle on claim</div><div class="pair">${row('leaves', C.noCycle.points, 'pln', `${C.noCycle.issues} non-deferred leaves without a cycle`)}</div><div class="small mute">${fmt(C.noCycle.issues)} leaves · ${pts(C.noCycle.points)}</div><div class="small mute">Deferred (v0.2): ${fmt(C.deferred.issues)} leaves · ${pts(C.deferred.points)}, no cycle by design; they move into C3 or a v0.2 project at the NJ-19 scope freeze.</div>`;
    strip.appendChild(nc);
    const S = C.settings || {};
    const dayName = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'][S.cycleStartDay] || '';
    $('#cyRule').innerHTML = `<span class="k">rule</span><div>${esc(C.rule)}<div class="set">${[
      `estimation ${esc(S.issueEstimationType || 'fibonacci')}`, `cycles ${S.cyclesEnabled ? 'on' : 'off'} · ${S.cycleDuration || 1} week · start ${dayName}`, `auto-assign started issues ${S.cycleIssueAutoAssignStarted ? 'on' : 'off'}`,
      `triage ${S.triageEnabled ? 'on' : 'off'}${S.triageIssueState ? ' · state ' + esc(S.triageIssueState.name) : ''}`, `active cycle ${S.activeCycle ? 'C' + S.activeCycle.number : 'none'}`
    ].map(t => `<span class="chip">${t}</span>`).join('')}</div></div>`;
    const c1 = C.list.find(c => c.active) || C.list[0];
    $('#cyNote').innerHTML = c1 ? `Cycle boundaries are midnight America/Los_Angeles (07:00Z). ${c1.short} holds ${c1.issues} issues (${pts(c1.points)}) today against ${pts(c1.plannedPoints)} due inside its window; the gap is work that is specified and unblocked but not yet claimed. Views: ${(D.round4.views || []).filter(v => /cycle|chunk/i.test(v.name)).map(v => `<a href="${esc(v.url)}">${esc(v.name)}</a>`).join(', ')}.` : 'No cycles in the snapshot.';
  }

  /* ---- estimates ---- */
  { const E = D.estimates || { perProject: [], totals: {}, byDue: [], burnup: { points: [] } }; const T = E.totals;
    $('#nPts').textContent = fmt(T.points);
    $('#estKpis').innerHTML = [
      { v: `${fmt(T.points)}<small>pts</small>`, l: 'planned across the team', s: `${fmt(T.estimated)} estimated issues · ${E.type} scale, S 2 / M 3 / L 5` },
      { v: `${fmt(T.done)}<small>done</small>`, l: 'points merged and verified', s: 'nothing has merged yet; the burn-up starts here' },
      { v: `${fmt(T.ready)}<small>pts</small>`, l: 'claimable today (Ready for Claude)', s: `${fmt(T.points - T.deferred)} pts in the v0.1 scope, ${fmt(T.deferred)} deferred to v0.2`, cls: 'ready' },
      { v: `${fmt(T.unestimatedLeaves)}<small>leaves</small>`, l: 'without an estimate', s: 'mostly Triage intake; umbrellas roll up their children' }
    ].map(k => `<div class="kpi ${k.cls || ''}"><div class="v">${k.v}</div><div class="l">${k.l}</div><div class="s">${k.s}</div></div>`).join('');
    const S = { sort: 'points' };
    $('#estTools').innerHTML = `<label class="small">Sort <select id="est-sort"><option value="points">by points</option><option value="phase">plan order</option><option value="new">round-4 projects first</option></select></label>`;
    $('#estLegend').innerHTML = ORDER.map(k => `<span><i class="f-${k}"></i>${NAMES[k]}</span>`).join('');
    function renderBars() {
      const rows = E.perProject.slice();
      if (S.sort === 'points') rows.sort((a, b) => b.total - a.total); else if (S.sort === 'new') rows.sort((a, b) => (P[b.key].isNew ? 1 : 0) - (P[a.key].isNew ? 1 : 0) || b.total - a.total);
      const max = Math.max(1, ...rows.map(r => r.total));
      const wrap = $('#estChart'); wrap.innerHTML = '';
      for (const r of rows) {
        const row = el('div', 'row');
        row.innerHTML = `<div class="nm"><i style="background:${r.color}"></i><a href="#issues" data-k="${r.key}" title="${esc(P[r.key].name)}">${esc(r.short)}</a>${P[r.key].isNew ? '<span class="new">new</span>' : ''}</div><div class="bar" style="width:${(100 * r.total / max).toFixed(1)}%"></div><div class="tot"><b>${fmt(r.total)}</b> · ${r.estimated}/${r.issues}</div>`;
        const b = $('.bar', row);
        for (const k of ORDER) { const n = r.byState[k] || 0; if (!n) continue; const i = el('i', 'f-' + k); i.style.flex = `${n} ${n} 0`; bindTip(i, `<b>${esc(r.short)}</b> · ${NAMES[k]}: ${fmt(n)} pt of ${fmt(r.total)}`); b.appendChild(i); }
        $('a', row).addEventListener('click', () => openProject(r.key));
        wrap.appendChild(row);
      }
      const ax = el('div', 'axis'); ax.innerHTML = `<span>0</span><span>${fmt(Math.round(max / 2))}</span><span>${fmt(max)} pt</span>`; wrap.appendChild(ax);
    }
    $('#est-sort').addEventListener('change', ev => { S.sort = ev.target.value; renderBars(); });
    renderBars();
    /* burn-up */
    const svg = $('#estBurn'); const W = 520, H = 260, L = 54, R = 16, top = 18, bot = 34;
    svg.setAttribute('viewBox', `0 0 ${W} ${H}`);
    const start = E.burnup.start || D.today, last = E.byDue.length ? E.byDue[E.byDue.length - 1].date : D.deadline, end = last > D.deadline ? last : D.deadline;
    const span = Math.max(1, dayIdx(end) - dayIdx(start));
    const x = d => L + (W - L - R) * (dayIdx(d) - dayIdx(start)) / span;
    const maxY = Math.max(T.points, 1); const y = v => top + (H - top - bot) * (1 - v / maxY);
    for (let k = 0; k <= 4; k++) { const v = maxY * k / 4; svgEl('line', { class: 'grid', x1: L, y1: y(v), x2: W - R, y2: y(v) }, svg); const t = svgEl('text', { class: 'axis', x: L - 6, y: y(v) + 3.5, 'text-anchor': 'end' }, svg); t.textContent = fmt(Math.round(v)); }
    let cum = 0; const plan = [{ date: start, v: 0 }]; for (const d of E.byDue) { if (d.date < start) { cum += d.pts; plan[0].v = cum; continue; } cum += d.pts; plan.push({ date: d.date, v: cum }); }
    if (cum < T.points) plan.push({ date: end, v: T.points });
    const pathD = plan.map((p, i) => `${i ? 'L' : 'M'}${x(p.date).toFixed(1)},${y(p.v).toFixed(1)}`).join('');
    svgEl('path', { class: 'plan-a', d: pathD + `L${x(plan[plan.length - 1].date).toFixed(1)},${y(0)}L${x(start).toFixed(1)},${y(0)}Z` }, svg);
    const planPath = svgEl('path', { class: 'plan', d: pathD }, svg);
    for (const d of [start, D.deadline, end].filter((v, i, a) => a.indexOf(v) === i)) { const t = svgEl('text', { class: 'axis', x: x(d), y: H - bot + 16, 'text-anchor': d === start ? 'start' : 'end' }, svg); t.textContent = fdate(d); }
    svgEl('line', { class: 'dead', x1: x(D.deadline), y1: top, x2: x(D.deadline), y2: H - bot }, svg);
    const td = svgEl('text', { class: 'lbl', x: x(D.deadline) - 4, y: top + 10, 'text-anchor': 'end' }, svg); td.textContent = 'v0.1.0';
    svgEl('line', { class: 'today', x1: x(D.today), y1: top, x2: x(D.today), y2: H - bot }, svg);
    const done = E.burnup.points || [];
    if (done.length) { svgEl('path', { class: 'done', d: `M${x(start).toFixed(1)},${y(0)}` + done.map(p => `L${x(p.date).toFixed(1)},${y(p.done).toFixed(1)}`).join('') }, svg); const lastP = done[done.length - 1]; const dot = svgEl('circle', { class: 'done-dot', cx: x(lastP.date), cy: y(lastP.done), r: 5 }, svg); bindTip(dot, `<b>${fdate(lastP.date)}</b> · ${pts(lastP.done)} done of ${pts(lastP.scope)} in scope`); }
    const lp = svgEl('text', { class: 'lbl', x: x(plan[Math.max(1, Math.floor(plan.length * 0.55))].date), y: y(plan[Math.max(1, Math.floor(plan.length * 0.55))].v) - 8, 'text-anchor': 'middle' }, svg); lp.textContent = 'points due by date';
    const ld = svgEl('text', { class: 'lbl', x: x(D.today) + 6, y: y(0) - 8 }, svg); ld.textContent = `done: ${fmt(T.done)} pt`;
    bindTip(planPath, `<b>Plan line</b><div class="mu">cumulative points of leaf issues by due date; ${fmt(cum)} pt carry a due date${T.points > cum ? `, ${fmt(T.points - cum)} pt (Deferred, Triage) have none and step in at the end` : ''}</div>`);
    $('#burnNote').textContent = `${fmt(T.done)} of ${fmt(T.points)} pt`;
    $('#burnCap').textContent = E.burnup.note;
    /* table view */
    const tbl = `<table><thead><tr><th>Project</th>${ORDER.map(k => `<th>${NAMES[k].split(' ')[0]}</th>`).join('')}<th>Total</th><th>Estimated</th></tr></thead><tbody>${E.perProject.slice().sort((a, b) => b.total - a.total).map(r => `<tr><td>${esc(r.short)}</td>${ORDER.map(k => `<td>${r.byState[k] || ''}</td>`).join('')}<td><b>${fmt(r.total)}</b></td><td>${r.estimated} / ${r.issues}</td></tr>`).join('')}</tbody></table>`;
    $('#estTable').insertAdjacentHTML('beforeend', tbl);
  }

  /* ---- round 4 ---- */
  { const R = D.round4; $('#r4Date').textContent = fdate(R.date); $('#nR4Proj').textContent = R.projects.length;
    const delta = (a, b, unit) => `<span class="was">${fmt(a)}</span><span class="arr">→</span>${fmt(b)}${unit ? `<small>${unit}</small>` : ''}`;
    $('#r4Kpis').innerHTML = [
      { v: delta(R.before.issues, R.after.issues), l: 'issues in team PAP', s: `${fmt(R.newIssues)} created in round 4 · ${R.newChildren} children of umbrellas · ${R.newDeferred} deferred to v0.2`, cls: 'r4' },
      { v: delta(R.before.projects, R.after.projects), l: 'projects (modules)', s: `new: ${R.newProjects.map(k => P[k] ? P[k].short : k).join(', ')}`, cls: 'r4' },
      { v: delta(R.before.relations, R.after.relations), l: 'blocking relations', s: `${fmt(R.newRelations)} added after inversion checks; graph acyclic` },
      { v: `${fmt(R.amendments)}<small>amendments</small>`, l: 'edits to existing specs', s: `${R.digestFiles} digests · ${R.suggestions} cross-project suggestions filed or noted` },
      { v: `${fmt(R.after.estimated)}<small>estimated</small>`, l: `issues carry ${fmt(R.after.points)} Fibonacci points`, s: `${R.after.cycles} cycles · ${R.after.initiatives} initiatives · ${R.after.views} views · ${R.after.templates} templates · ${R.after.updates} project updates · ${R.after.links} project links` }
    ].map(k => `<div class="kpi ${k.cls || ''}"><div class="v">${k.v}</div><div class="l">${k.l}</div><div class="s">${k.s}</div></div>`).join('');
    /* projects with new-issue counts */
    const wrap = $('#r4Projects'); const rows = R.projects.slice().sort((a, b) => b.r4New - a.r4New || b.total - a.total); const max = Math.max(1, ...rows.map(r => r.total));
    wrap.innerHTML = `<div class="hdr"><span>project</span><span>issues before round 4 · new · new deferred</span><span>new</span></div>`;
    for (const r of rows) {
      const old = r.total - r.r4New, nw = r.r4New - r.r4Deferred;
      const row = el('div', 'row');
      row.innerHTML = `<div class="nm"><i style="background:${P[r.key].color}"></i><a href="#issues" data-k="${r.key}" title="${esc(r.name)}">${esc(r.short)}</a>${r.isNew ? '<span class="new">new</span>' : ''}</div><div class="bar">${old ? `<i class="old" style="flex:${old} ${old} 0"></i>` : ''}${nw ? `<i class="new" style="flex:${nw} ${nw} 0"></i>` : ''}${r.r4Deferred ? `<i class="def" style="flex:${r.r4Deferred} ${r.r4Deferred} 0"></i>` : ''}<i style="flex:${max - r.total} ${max - r.total} 0;background:transparent"></i></div><div class="n"><b>+${r.r4New}</b></div>`;
      bindTip(row, `<b>${esc(r.name)}</b><div class="mu">${r.total} issues · ${r.r4New} new in round 4 (${r.r4Children} children, ${r.r4Deferred} deferred) · ${fmt(r.points)} pt${r.ini ? ` · ${esc(r.ini)}` : ''}</div>`);
      $('a', row).addEventListener('click', () => openProject(r.key));
      wrap.appendChild(row);
    }
    wrap.insertAdjacentHTML('beforeend', `<div class="lg"><span><i style="background:var(--card-3)"></i>before round 4</span><span><i style="background:var(--sel)"></i>new, v0.1 scope</span><span><i style="background:var(--sel);opacity:.4"></i>new, deferred to v0.2</span></div>`);
    /* gaps */
    $('#r4Gaps').innerHTML = R.gaps.map(g => `<li><div><b>${esc(g.area)}</b>${esc(g.gap)}<div class="fix">${linkify(g.fix).replace(/`([^`]+)`/g, '<span class="mono">$1</span>')}</div><div class="pj">${g.projects.map(projChip).join('')}</div></div></li>`).join('');
    bindChips($('#r4Gaps'));
    /* features table */
    const cls = u => /^yes/i.test(u) ? 'yes' : /not on basic/i.test(u) ? 'na' : /not yet/i.test(u) ? 'no' : 'part';
    $('#r4Features').innerHTML = R.features.length ? `<table><thead><tr><th>Feature</th><th>Used</th><th>Since</th><th>How PaperOS uses it</th></tr></thead><tbody>${R.features.map(f => `<tr><td class="f">${esc(f.feature)}</td><td class="u"><span class="pill ${cls(f.used)}"><i></i>${esc(f.used)}</span></td><td class="h">${esc(f.since)}</td><td class="h">${linkify(f.how).replace(/`([^`]+)`/g, '<span class="mono">$1</span>')}</td></tr>`).join('')}</tbody></table>` : '<p class="note">docs/linear-features.md was not available at build time.</p>';
    $('#r4Docs').innerHTML = R.docs.map(d => `<a href="${esc(d.url)}">${esc(d.title)} <span class="mono">${esc(d.path)}</span></a>`).join('');
  }
})();
