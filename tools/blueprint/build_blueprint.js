const fs = require('fs');
const dir = process.env.PAPEROS_PLAN_DIR || '.';
const plan = JSON.parse(fs.readFileSync(dir + '/plan.json', 'utf8'));
const lin = JSON.parse(fs.readFileSync(dir + '/linear-ids.json', 'utf8'));
const esc = s => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');

const phaseOrder = { P0: 0, P1: 1, P2: 2 };
const projects = [...plan.projects].sort((a, b) => phaseOrder[a.phase] - phaseOrder[b.phase] || plan.projects.indexOf(a) - plan.projects.indexOf(b));
const allIssues = plan.projects.flatMap(p => p.issues.map(i => ({ ...i, project: p.key })));
const nIssues = allIssues.length, nReady = allIssues.filter(i => i.readyNow).length, nProjects = plan.projects.length;
const nMilestones = plan.projects.reduce((a, p) => a + p.milestones.length, 0);
const nLeads = plan.agents.length, nSubs = plan.agents.reduce((a, g) => a + g.subAgents.length, 0);
const daysLeft = Math.round((Date.UTC(2026, 9, 1) - Date.UTC(2026, 8, 17)) / 86400000);

const shortName = {
  'app-shell': 'App shell & template', 'data-layer': 'Data layer', forge: 'Forge independence', identity: 'Identity & audiences',
  'design-system': 'Design system', quality: 'Quality pipeline', 'pm-linear': 'PM & Claude pipeline', agents: 'Agent characters',
  'spec-builder': 'Spec builder', collab: 'Collaboration & knowledge', realtime: 'Multiplayer & realtime', input: 'Multi-input & a11y',
  tables: 'Table & views engine', 'business-core': 'Business core', growth: 'Growth & CRM', migration: 'Migration & import', libraries: 'Library discovery'
};

/* ---------- timeline SVG ---------- */
const dayIdx = d => Math.round((Date.parse(d + 'T00:00:00Z') - Date.UTC(2026, 8, 17)) / 86400000);
const TL = { left: 200, top: 46, rowH: 24, w: 760 / 15, right: 20 };
const tlH = TL.top + projects.length * TL.rowH + 34;
const tlW = TL.left + 760 + TL.right;
const bands = [{ k: 'P0', a: 0, b: 4 }, { k: 'P1', a: 4, b: 10 }, { k: 'P2', a: 10, b: 15 }];
let tl = `<svg class="fig" viewBox="0 0 ${tlW} ${tlH}" role="img" aria-label="Milestone timeline: every project's three milestones plotted by target date across the three phases from 17 September to 1 October 2026">`;
tl += `<defs><clipPath id="tlclip"><rect x="0" y="0" width="${tlW}" height="${tlH}"/></clipPath></defs>`;
for (const b of bands) {
  const x = TL.left + b.a * TL.w, w = (b.b - b.a) * TL.w;
  tl += `<rect x="${x}" y="${TL.top - 8}" width="${w}" height="${projects.length * TL.rowH + 8}" fill="var(--${b.k.toLowerCase()})" opacity="0.13"/>`;
  tl += `<text x="${x + 6}" y="16" class="t-mono t-strong" fill="var(--${b.k.toLowerCase()}-ink)">${b.k} · ${plan.phases.find(p => p.key === b.k).name}</text>`;
}
for (let d = 0; d <= 14; d++) {
  const x = TL.left + d * TL.w;
  const date = new Date(Date.UTC(2026, 8, 17 + d));
  const lab = (date.getUTCMonth() === 8 ? 'Sep ' : 'Oct ') + date.getUTCDate();
  tl += `<line x1="${x}" y1="${TL.top - 8}" x2="${x}" y2="${TL.top + projects.length * TL.rowH}" stroke="currentColor" opacity="${d % 7 === 0 || d === 14 ? 0.35 : 0.12}"/>`;
  if (d % 2 === 0) tl += `<text x="${x + TL.w / 2}" y="${TL.top - 14}" text-anchor="middle" class="t-mono t-mute">${lab}</text>`;
}
tl += `<line x1="${TL.left + 15 * TL.w}" y1="${TL.top - 8}" x2="${TL.left + 15 * TL.w}" y2="${TL.top + projects.length * TL.rowH}" stroke="currentColor" opacity="0.35"/>`;
projects.forEach((p, i) => {
  const y = TL.top + i * TL.rowH + TL.rowH / 2;
  tl += `<text x="${TL.left - 12}" y="${y + 4}" text-anchor="end" class="t-label">${esc(shortName[p.key])}</text>`;
  tl += `<line x1="${TL.left}" y1="${y}" x2="${TL.left + 15 * TL.w}" y2="${y}" stroke="currentColor" opacity="0.08"/>`;
  const xs = p.milestones.map(m => TL.left + (dayIdx(m.targetDate) + 0.5) * TL.w);
  tl += `<line x1="${TL.left + 0.5 * TL.w}" y1="${y}" x2="${xs[xs.length - 1]}" y2="${y}" stroke="var(--accent)" stroke-width="2" opacity="0.55"/>`;
  p.milestones.forEach((m, j) => {
    tl += `<circle cx="${xs[j]}" cy="${y}" r="5" fill="var(--accent)" stroke="var(--card)" stroke-width="2"><title>${esc(p.name)} · ${esc(m.name)} (${m.targetDate}): ${esc(m.goal)}</title></circle>`;
  });
});
tl += `<text x="${TL.left}" y="${tlH - 10}" class="t-mono t-mute">Today: Sep 17</text><text x="${TL.left + 15 * TL.w}" y="${tlH - 10}" text-anchor="end" class="t-mono t-mute">Deadline: Oct 1 · ${daysLeft} days</text>`;
tl += `</svg>`;

/* ---------- budget SVG ---------- */
const B = { left: 300, top: 14, rowH: 40, barW: 520, right: 130 };
const bW = B.left + B.barW + B.right, bH = B.top + plan.budget.length * B.rowH + 30;
let bg = `<svg class="fig" viewBox="0 0 ${bW} ${bH}" role="img" aria-label="Credit budget split: building 45 percent, automated review and QA 30, planning and specs 12, docs 8, research 5">`;
[0, 10, 20, 30, 40, 50].forEach(v => {
  const x = B.left + v / 50 * B.barW;
  bg += `<line x1="${x}" y1="${B.top}" x2="${x}" y2="${B.top + plan.budget.length * B.rowH}" stroke="currentColor" opacity="0.12"/><text x="${x}" y="${bH - 8}" text-anchor="middle" class="t-mono t-mute">${v}%</text>`;
});
plan.budget.forEach((b, i) => {
  const y = B.top + i * B.rowH, h = 22, w = b.share_pct / 50 * B.barW;
  const hot = b.area.startsWith('Automated');
  bg += `<text x="${B.left - 14}" y="${y + h / 2 + 4}" text-anchor="end" class="t-label${hot ? ' t-strong' : ''}">${esc(b.area)}</text>`;
  bg += `<rect x="${B.left}" y="${y}" width="${w}" height="${h}" rx="3" fill="var(--accent)" opacity="${hot ? 1 : 0.42}"><title>${esc(b.area)}: ${b.share_pct}% ≈ $${(b.share_pct * 100).toLocaleString()}</title></rect>`;
  bg += `<text x="${B.left + w + 10}" y="${y + h / 2 + 4}" class="t-mono${hot ? ' t-strong' : ''}">${b.share_pct}% · ≈$${(b.share_pct * 100).toLocaleString()}</text>`;
});
bg += `</svg>`;

/* ---------- architecture SVG ---------- */
const box = (x, y, w, h, title, sub, opt = {}) => {
  const cls = opt.cls || '';
  let s = `<g class="node ${cls}"><rect x="${x}" y="${y}" width="${w}" height="${h}" rx="6" fill="${opt.fill || 'var(--card)'}" stroke="${opt.stroke || 'currentColor'}" stroke-width="${opt.sw || 1.2}" ${opt.dash ? 'stroke-dasharray="5 4"' : ''}/>`;
  s += `<text x="${x + 12}" y="${y + 20}" class="t-strong">${esc(title)}</text>`;
  (sub || []).forEach((line, i) => { s += `<text x="${x + 12}" y="${y + 38 + i * 15}" class="t-small t-mute">${esc(line)}</text>`; });
  return s + `</g>`;
};
const arrow = (d, label, lx, ly, opt = {}) => `<path d="${d}" fill="none" stroke="${opt.stroke || 'currentColor'}" stroke-width="1.4" ${opt.dash ? 'stroke-dasharray="4 4"' : ''} marker-end="url(#ah)"${opt.start ? ' marker-start="url(#ahs)"' : ''}/>` + (label ? `<text x="${lx}" y="${ly}" text-anchor="${opt.anchor || 'middle'}" class="t-small t-mute lbl">${esc(label)}</text>` : '');
let ar = `<svg class="fig" viewBox="0 0 1000 780" role="img" aria-label="System architecture: Linear issues flow to Claude sessions and through the quality pipeline back to Linear; specs are the contract that drives codegen, component IDs, view specs and conformance tests; the app shell hosts the design system, table and views engine, identity and realtime; business core, growth and migration are removable modules; everything rests on the Postgres data layer.">`;
ar += `<defs><marker id="ah" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0L10 5L0 10z" fill="currentColor"/></marker><marker id="ahs" viewBox="0 0 10 10" refX="1" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M10 0L0 5L10 10z" fill="currentColor"/></marker></defs>`;
// band labels
ar += `<text x="0" y="14" class="t-mono t-mute">BUILD LOOP</text>`;
ar += box(0, 24, 300, 96, 'Linear pipeline', ['Backlog → Ready for Claude → In Progress', '→ In Review → Needs Justin → Done', '206 issues · 284 blocking relations']);
ar += box(350, 24, 300, 96, 'Claude Code sessions', ['Orchestrator spawns one session per issue', 'in its own git worktree, as a character', 'with scoped tools, MCPs and budget']);
ar += box(700, 24, 300, 96, 'Quality pipeline', ['Gate 1 static · Gate 2 three reviewer agents', 'Gate 3 screenshots + video, 7 widths', 'Gate 4 edge-case hunter · weekly RC digest'], { cls: 'hot' });
ar += arrow('M300 60 L348 60', 'claims Ready for Claude', 324, 50);
ar += arrow('M650 60 L698 60', 'opens PR on Forgejo (GitHub mirror)', 674, 50);
ar += arrow('M850 120 L850 150 L150 150 L150 122', 'gates pass → In Review → merge; release candidate → Needs Justin', 500, 144);
// specs band
ar += `<text x="0" y="200" class="t-mono t-mute">THE CONTRACT</text>`;
ar += box(0, 210, 1000, 62, 'Spec builder', ['app.spec.yaml + page.spec.yaml per page: purpose, logic, access, data, integrations, layout, components, states, edge cases · validator blocks PRs without a spec'], { fill: 'var(--accent-soft)', stroke: 'var(--accent)', sw: 1.6 });
ar += arrow('M500 120 L500 208', 'writes and validates specs', 560, 172, { anchor: 'start' });
ar += arrow('M930 210 L930 122', 'conformance, permission and edge-case tests derive from specs', 920, 172, { anchor: 'end' });
// product layer
ar += `<text x="0" y="316" class="t-mono t-mute">PRODUCT LAYER</text>`;
ar += box(0, 326, 250, 112, 'Design system', ['DTCG tokens → CSS variables', 'Base UI/Radix + Tailwind v4', 'Storybook · per-tenant themes']);
ar += box(300, 326, 400, 112, 'Universal app shell', ['One React 19 + Vite bundle: web/PWA,', 'Tauri 2 desktop (Linux/macOS/Windows)', 'and mobile · multi-window · kiosk', 'Business, growth, migration as removable modules']);
ar += box(750, 326, 250, 112, 'Table & views engine', ['View model ⊇ Airtable/Notion/ClickUp', 'compiled to SQL · grid, kanban, calendar,', 'Gantt, gallery, form, map, chart']);
ar += arrow('M125 272 L125 324', 'component IDs', 132, 302, { anchor: 'start' });
ar += arrow('M500 272 L500 324', 'codegen scaffolds pages', 508, 302, { anchor: 'start' });
ar += arrow('M875 272 L875 324', 'view + dashboard specs', 882, 302, { anchor: 'start' });
ar += arrow('M250 382 L298 382', 'tokens, components', 274, 372);
ar += arrow('M750 382 L702 382', 'views in pages', 726, 372);
// platform services
ar += `<text x="0" y="482" class="t-mono t-mute">PLATFORM SERVICES</text>`;
ar += box(0, 492, 300, 96, 'Identity & audiences', ['Better Auth: passkeys, magic link, OAuth, orgs', 'can(actor, action, resource) from spec access', 'customers · staff · partners · admins · agents']);
ar += box(350, 492, 300, 96, 'Realtime & multiplayer', ['Yjs via Hocuspocus: docs, canvas, presence', 'Electric shapes: live records', 'one WebSocket · offline queue · multi-window']);
ar += box(700, 492, 300, 96, 'Business modules', ['Business core: Stripe, own ledger, payroll adapter', 'Growth: CRM, outreach, social, landing pages', 'Migration: importers, dry runs, business templates'], { dash: true });
ar += arrow('M150 490 L150 440', 'who may see and do what, per page', 158, 470, { anchor: 'start' });
ar += arrow('M500 490 L500 440', 'presence, CRDT docs, live rows', 508, 470, { anchor: 'start', start: true });
ar += arrow('M850 490 L850 440', 'hosted; toggled per app / tenant', 858, 470, { anchor: 'start' });
ar += arrow('M700 540 L652 540', 'built on tables + identity', 676, 530);
// data layer
ar += `<text x="0" y="640" class="t-mono t-mute">SOURCE OF TRUTH</text>`;
ar += box(0, 650, 1000, 80, 'Data layer', ['Postgres 17 with row-level security per tenant · Drizzle schema-as-code · oRPC typed API · ElectricSQL + PGlite local-first · MinIO files · pg-boss jobs · audit log · tsvector + pgvector search', 'Self-hosted on a Hetzner VPS via Coolify next to Forgejo (mirrored to GitHub imagine-os), Hocuspocus and the orchestrator'], { sw: 1.6 });
ar += arrow('M150 650 L150 590', 'RLS policies enforce tenancy', 158, 628, { anchor: 'start' });
ar += arrow('M500 650 L500 590', 'Yjs persistence · change streams', 508, 628, { anchor: 'start' });
ar += arrow('M850 650 L850 590', 'ledger, CRM, import tables', 858, 628, { anchor: 'start' });
ar += `<text x="0" y="768" class="t-small t-mute">Solid arrows: data or control flow, labelled with what moves. Dashed box: optional modules an app can ship without. Tinted band: the spec contract every other box reads.</text>`;
ar += `</svg>`;

/* ---------- org chart ---------- */
const chips = (arr, cls) => arr.map(a => `<span class="chip ${cls}">${esc(a)}</span>`).join('');
const agentCard = (g, lead) => `<article class="agent${lead ? ' lead' : ''}">
  <header><h4>${esc(g.name)}</h4><span class="t-mono t-mute">reports to ${esc(g.reportsTo)}</span></header>
  <p class="role">${esc(g.role)}</p>
  <div class="sub"><span class="k">Sub-characters</span><ul>${g.subAgents.map(s => `<li><b>${esc(s.name)}</b> <span>${esc(s.role)}</span></li>`).join('')}</ul></div>
  <div class="sub"><span class="k">Tools</span><div class="chips">${chips(g.tools, 'tool')}</div></div>
  <div class="sub"><span class="k">Access</span><div class="chips">${chips(g.access, 'acc')}</div></div>
</article>`;
const atlas = plan.agents.find(a => a.reportsTo === 'Justin');
const leads = plan.agents.filter(a => a !== atlas);

/* ---------- index ---------- */
const typeCls = { Build: 'build', Research: 'research', Spec: 'spec', Review: 'review', Infra: 'infra', Docs: 'docs' };
const projectCard = p => {
  const L = lin.projects[p.key];
  const ready = p.issues.filter(i => i.readyNow).length;
  return `<article class="proj" id="proj-${p.key}" data-phase="${p.phase}">
  <header>
    <div class="ph"><span class="phase ${p.phase.toLowerCase()}">${p.phase}</span><span class="t-mono t-mute">${p.issues.length} issues · ${p.milestones.length} milestones · target ${p.milestones[p.milestones.length - 1].targetDate}${ready ? ` · <b class="ready-n">${ready} ready now</b>` : ''}</span></div>
    <h3><a href="${L.url}" target="_blank" rel="noopener">${esc(p.name)}</a></h3>
    <p>${esc(p.summary)}</p>
  </header>
  <ol class="ms">${p.milestones.map(m => `<li><span class="t-mono">${m.targetDate}</span> ${esc(m.name)}</li>`).join('')}</ol>
  <ul class="issues">${p.issues.map(i => {
    const li = lin.issues[i.key];
    return `<li data-ready="${i.readyNow}"><a href="${li.url}" target="_blank" rel="noopener"><span class="id">${li.identifier}</span><span class="tt">${esc(i.title)}</span></a><span class="tags"><span class="type ${typeCls[i.type]}">${i.type}</span>${i.readyNow ? '<span class="ready">Ready for Claude</span>' : ''}</span></li>`;
  }).join('')}</ul>
</article>`;
};

/* ---------- risks (from critique.md) ---------- */
const risks = [
  ['P0 is 68 issues in four days (Sep 17 to 20).', 'Even with parallel sessions, the chain scaffold → local stack → Drizzle → core entities → RLS → API → Better Auth → Yjs server is serial and each step is M-size. Expect P0 to spill into Sep 22 or 23; treat phase dates as targets for the ready set, not for the whole phase.'],
  ['Human account setup is on the critical path.', 'Hetzner (may need identity verification), a domain or Cloudflare, Resend, Apple developer program for signed macOS builds, Stripe live keys, a payroll sandbox. PAP-25 batches the first four into one Needs Justin item on day one; answer it the same day or every infra issue waits.'],
  ['The orchestrator and the Coolify host hold every credential.', 'The orchestrator runs with Linear, forge, Coolify and sops access on one VPS. A compromised session prompt or leaked token there is a total compromise. Tool scopes, security scans and the destructive-action deny list are the mitigations; do not let those slip to P1.'],
  ['Automated review replaces human review, but nobody has calibrated it yet.', 'Thirty percent of credits go to reviewer agents, vision inspection and edge-case hunting. Until the eval harness and review rubrics produce a false-negative rate, treat the first release candidate as a smoke test. Plan a manual spot-check of gate 2 verdicts on five PRs in week one.'],
  ['P2 carries the business layer, growth, migration and hardening in five days.', 'Stripe Connect, ledger, payroll adapter, CRM, social scheduler and importers are each L-size. Something will not ship by Oct 1. Decide now what the release candidate must contain (suggested: template + spec builder + tables + collab + identity + billing) and let the rest land after the deadline with remaining credits.'],
  ['Scope creep by design.', 'The brief says go deep and the plan obliges, but 206 issues with generous specs will burn credits on research and docs (17 percent of budget). Enforce the time boxes in research issues (one session each, ADR or stop) and let credit metering post the daily burn so the trade-off is visible by day three, not day ten.']
];

const readyList = allIssues.filter(i => i.readyNow).map(i => lin.issues[i.key]);

const html = `<title>PaperOS Core Platform Blueprint</title>
<style>
:root{
  --bg:#F2F5FA; --card:#FFFFFF; --card-2:#E9EEF6; --ink:#141B2D; --ink-2:#55627A; --line:#CFD8E6;
  --accent:#1F5BD6; --accent-soft:#E3ECFC; --accent-ink:#FFFFFF;
  --p0:#E0474C; --p0-ink:#A9272C; --p1:#E8873A; --p1-ink:#9C4F0E; --p2:#D9A92E; --p2-ink:#7A5A05;
  --ready:#B45309; --ready-soft:#FDEBD3;
  --justin:#A9272C; --justin-soft:#FBE3E4;
  --mono:ui-monospace,"SF Mono",Menlo,Consolas,"Liberation Mono",monospace;
  --sans:system-ui,-apple-system,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
  color-scheme:light;
}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){
  --bg:#0C111C; --card:#151C2B; --card-2:#1C2536; --ink:#E7ECF5; --ink-2:#9AA6BD; --line:#2B3648;
  --accent:#6FA0FF; --accent-soft:#1A2A4A; --accent-ink:#0C111C;
  --p0:#F07178; --p0-ink:#F5A0A5; --p1:#F2994A; --p1-ink:#F7B87E; --p2:#F2C94C; --p2-ink:#F6DA85;
  --ready:#F5B04C; --ready-soft:#3A2A10;
  --justin:#F07178; --justin-soft:#3A1A1E;
  color-scheme:dark;
}}
:root[data-theme="dark"]{
  --bg:#0C111C; --card:#151C2B; --card-2:#1C2536; --ink:#E7ECF5; --ink-2:#9AA6BD; --line:#2B3648;
  --accent:#6FA0FF; --accent-soft:#1A2A4A; --accent-ink:#0C111C;
  --p0:#F07178; --p0-ink:#F5A0A5; --p1:#F2994A; --p1-ink:#F7B87E; --p2:#F2C94C; --p2-ink:#F6DA85;
  --ready:#F5B04C; --ready-soft:#3A2A10;
  --justin:#F07178; --justin-soft:#3A1A1E;
  color-scheme:dark;
}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.55 var(--sans);-webkit-font-smoothing:antialiased}
.wrap{max-width:1080px;margin:0 auto;padding-block:32px 80px;padding-inline:20px}
a{color:var(--accent);text-decoration:none}a:hover{text-decoration:underline}
:focus-visible{outline:2px solid var(--accent);outline-offset:2px;border-radius:3px}
h1,h2,h3,h4{text-wrap:balance;margin:0;letter-spacing:-0.01em}
h1{font-size:clamp(30px,5vw,46px);line-height:1.05;font-weight:700}
h2{font-size:26px;font-weight:650;line-height:1.15}
h3{font-size:18px;font-weight:650}
h4{font-size:16px;font-weight:650}
p{margin:0}
.t-mono,.chip,.id,.type,.phase,.ready,.kicker,.ms span,.stat .n,.stat .l{font-family:var(--mono)}
.kicker{font-size:12px;letter-spacing:.08em;text-transform:uppercase;color:var(--ink-2)}
.lede{max-width:68ch;font-size:17px;line-height:1.6;color:var(--ink)}
.prose{max-width:68ch}
.mute{color:var(--ink-2)}

/* masthead */
.mast{display:grid;gap:18px;padding-bottom:28px;border-bottom:1px solid var(--line)}
.mast .meta{display:flex;flex-wrap:wrap;gap:8px 20px;font-family:var(--mono);font-size:12px;color:var(--ink-2)}
.toc{display:flex;flex-wrap:wrap;gap:6px 14px;font-size:13px;margin-top:6px}
.toc a{padding:3px 0;color:var(--ink-2)}.toc a b{color:var(--accent);font-family:var(--mono);font-weight:500;margin-right:4px}

section{padding-top:56px}
section>header{display:grid;gap:6px;margin-bottom:22px}
section>header .kicker b{color:var(--accent)}

/* stats */
.stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px;margin-top:26px}
.stat{background:var(--card);border:1px solid var(--line);border-radius:8px;padding:14px 16px;display:grid;gap:2px}
.stat .n{font-size:32px;font-weight:600;line-height:1;font-variant-numeric:tabular-nums}
.stat .l{font-size:12px;color:var(--ink-2)}
.stat.hot{border-color:var(--ready);background:var(--ready-soft)}.stat.hot .n{color:var(--ready)}
.summary{margin-top:22px;max-width:68ch;display:grid;gap:10px}
.summary li{margin-left:1.1em}

/* figures */
figure{margin:0;display:grid;gap:10px}
.figwrap{overflow-x:auto;background:var(--card);border:1px solid var(--line);border-radius:10px;padding:18px}
.fig{display:block;width:100%;height:auto;max-width:100%;min-width:640px;font-family:var(--sans);font-size:13px;fill:currentColor;color:var(--ink)}
.fig text{fill:currentColor}
.fig .t-strong{font-weight:650}.fig .t-small{font-size:11.5px}.fig .t-mute{fill:var(--ink-2)}.fig .t-mono{font-family:var(--mono);font-size:11.5px}.fig .t-label{font-size:12.5px}
.fig .lbl{paint-order:stroke;stroke:var(--card);stroke-width:4px;stroke-linejoin:round}
.fig .hot rect{stroke:var(--accent);stroke-width:1.8}
figcaption{font-size:13px;color:var(--ink-2);max-width:78ch}

/* org chart */
.org{display:grid;gap:0;justify-items:center}
.person{background:var(--card);border:1px solid var(--line);border-radius:8px;padding:10px 18px;text-align:center;display:grid;gap:2px}
.person.justin{border-color:var(--justin);background:var(--justin-soft)}
.person .t-mono{font-size:12px;color:var(--ink-2)}
.vline{width:1px;height:26px;background:var(--line)}
.rail{width:100%;position:relative;height:26px}
.rail::before{content:"";position:absolute;left:12.5%;right:12.5%;top:0;border-top:1px solid var(--line)}
.rail::after{content:"";position:absolute;left:50%;top:-26px;height:26px;border-left:1px solid var(--line)}
.agents{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;width:100%}
.agent{background:var(--card);border:1px solid var(--line);border-radius:8px;padding:14px;display:grid;gap:10px;align-content:start;font-size:13px;position:relative}
.agents .agent::before{content:"";position:absolute;left:50%;top:-14px;height:14px;border-left:1px solid var(--line)}
.agent.lead{max-width:560px;width:100%;border-color:var(--accent)}
.agent header{display:flex;justify-content:space-between;gap:8px;align-items:baseline;flex-wrap:wrap}
.agent header .t-mono{font-size:11px}
.agent .role{color:var(--ink-2);line-height:1.45}
.agent .sub{display:grid;gap:5px}
.agent .k{font-family:var(--mono);font-size:10.5px;letter-spacing:.06em;text-transform:uppercase;color:var(--ink-2)}
.agent ul{margin:0;padding:0;list-style:none;display:grid;gap:4px}
.agent li{line-height:1.4}.agent li span{color:var(--ink-2)}
.chips{display:flex;flex-wrap:wrap;gap:4px}
.chip{font-size:11px;padding:2px 7px;border-radius:4px;background:var(--card-2);border:1px solid var(--line);line-height:1.5}
.chip.acc{background:transparent;border-style:dashed}

/* phases */
.phases{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;margin-top:16px}
.phasecard{border-top:4px solid var(--line);padding-top:10px;display:grid;gap:6px;font-size:14px}
.phasecard.p0{border-color:var(--p0)}.phasecard.p1{border-color:var(--p1)}.phasecard.p2{border-color:var(--p2)}
.phasecard .t-mono{font-size:12px;color:var(--ink-2)}
.phasecard p{color:var(--ink-2);line-height:1.5}

/* budget reasons */
.reasons{display:grid;gap:10px;margin-top:16px;max-width:78ch}
.reasons li{display:grid;grid-template-columns:64px 1fr;gap:12px;align-items:baseline}
.reasons .t-mono{font-size:13px;font-weight:600;font-variant-numeric:tabular-nums}
.reasons b{display:block}.reasons span{color:var(--ink-2)}

/* decisions */
.decisions{display:grid;grid-template-columns:repeat(2,1fr);gap:14px}
.dec{background:var(--card);border:1px solid var(--line);border-radius:8px;padding:16px;display:grid;gap:8px;font-size:14px}
.dec h3{font-size:15px}
.dec .k{font-family:var(--mono);font-size:10.5px;letter-spacing:.06em;text-transform:uppercase;color:var(--accent)}
.dec p{line-height:1.5}.dec .why{color:var(--ink-2)}

/* index */
.legend{display:flex;flex-wrap:wrap;gap:8px 14px;font-size:12px;color:var(--ink-2);align-items:center;margin-bottom:16px}
.index{display:grid;gap:16px}
.proj{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:18px 20px;display:grid;gap:14px}
.proj header{display:grid;gap:6px}.proj header p{color:var(--ink-2);font-size:14px;max-width:80ch}
.proj .ph{display:flex;flex-wrap:wrap;gap:10px;align-items:center;font-size:12px}
.ready-n{color:var(--ready);font-weight:600}
.phase{font-size:11px;padding:1px 7px;border-radius:4px;color:var(--accent-ink);font-weight:600}
.phase.p0{background:var(--p0)}.phase.p1{background:var(--p1)}.phase.p2{background:var(--p2);color:#141B2D}
.ms{margin:0;padding:0;list-style:none;display:flex;flex-wrap:wrap;gap:4px 18px;font-size:12.5px;color:var(--ink-2)}
.ms span{margin-right:6px;color:var(--ink)}
.issues{margin:0;padding:0;list-style:none;columns:2;column-gap:28px;font-size:13.5px}
.issues li{break-inside:avoid;padding:5px 0;border-top:1px solid var(--line);display:grid;gap:3px}
.issues li a{display:grid;grid-template-columns:62px 1fr;gap:8px;color:var(--ink);align-items:baseline}
.issues li a:hover .tt{color:var(--accent)}
.issues .id{font-size:12px;color:var(--accent);font-variant-numeric:tabular-nums}
.issues .tags{display:flex;gap:6px;margin-left:70px;flex-wrap:wrap}
.type{font-size:10.5px;letter-spacing:.03em;color:var(--ink-2)}
.ready{font-size:10.5px;padding:0 6px;border-radius:3px;background:var(--ready-soft);color:var(--ready);font-weight:600}
.issues li[data-ready="true"]{background:linear-gradient(90deg,var(--ready-soft),transparent 55%);border-radius:4px}

/* risks */
.risks{margin:0;padding:0;list-style:none;display:grid;gap:14px;counter-reset:r}
.risks li{display:grid;grid-template-columns:44px 1fr;gap:12px;max-width:80ch}
.risks li::before{counter-increment:r;content:counter(r,decimal-leading-zero);font-family:var(--mono);font-size:22px;color:var(--p0);line-height:1.1;font-variant-numeric:tabular-nums}
.risks b{display:block;margin-bottom:3px}.risks p{color:var(--ink-2);font-size:14px}

/* pipeline */
.pipe{display:grid;grid-template-columns:repeat(6,1fr);gap:8px;margin-bottom:22px}
.state{background:var(--card);border:1px solid var(--line);border-radius:8px;padding:12px;display:grid;gap:6px;font-size:13px;position:relative}
.state h4{font-size:14px}.state .who{font-family:var(--mono);font-size:11px;color:var(--ink-2)}
.state p{color:var(--ink-2);line-height:1.45}
.state:not(:last-child)::after{content:"→";position:absolute;right:-11px;top:12px;color:var(--ink-2);font-size:14px;z-index:1}
.state.justin{border-color:var(--justin);background:var(--justin-soft)}
.state.claude{border-color:var(--ready)}
.todo{background:var(--card);border:1px solid var(--line);border-left:4px solid var(--justin);border-radius:8px;padding:18px 20px;display:grid;gap:12px;max-width:80ch}
.todo ul{margin:0;padding-left:1.2em;display:grid;gap:6px;font-size:14px}
.readynow{margin-top:24px;display:grid;gap:8px}
.readynow ul{margin:0;padding:0;list-style:none;columns:2;column-gap:24px;font-size:13px}
.readynow li{break-inside:avoid;padding:3px 0}
.readynow .id{font-family:var(--mono);font-size:12px;margin-right:8px;color:var(--accent)}

footer{margin-top:60px;padding-top:18px;border-top:1px solid var(--line);font-size:12.5px;color:var(--ink-2);font-family:var(--mono)}

@media (max-width:900px){
  .agents{grid-template-columns:repeat(2,1fr)}
  .decisions{grid-template-columns:1fr}
  .pipe{grid-template-columns:repeat(3,1fr)}
  .state:nth-child(3)::after{display:none}
}
@media (max-width:640px){
  .wrap{padding-inline:16px}
  .agents{grid-template-columns:1fr}
  .phases{grid-template-columns:1fr}
  .issues,.readynow ul{columns:1}
  .pipe{grid-template-columns:1fr 1fr}
  .state::after{display:none}
  .state:nth-child(3)::after{display:none}
  .rail::before{left:50%;right:50%}
}
@media (prefers-reduced-motion:no-preference){a{transition:color .15s}}
</style>
<div class="wrap">
<header class="mast">
  <div class="kicker">PaperOS · Core Platform · Blueprint rev 1 · Sep 17, 2026</div>
  <h1>PaperOS Core Platform Blueprint</h1>
  <p class="lede">The reusable foundation every future PaperOS app is generated from: one spec-driven TypeScript monorepo template that ships to web, desktop and mobile with a shared data layer, design system, multiplayer, table and views engine, identity for every audience, and business plumbing already wired. Built and reviewed by a roster of Claude agent characters working from Linear behind four automated quality gates, so that by October 1 a new app goes from blank screen to running product in hours, and Justin reviews release candidates, not pull requests.</p>
  <div class="meta"><span>Workspace linear.app/paperos · team PAP</span><span>GitHub org imagine-os · Forgejo mirror</span><span>Budget ≈ $10,000 Claude credits</span><span>Deadline 2026-10-01</span></div>
  <nav class="toc" aria-label="Sections">
    <a href="#s1"><b>1</b>Ten-second summary</a><a href="#s2"><b>2</b>Architecture</a><a href="#s3"><b>3</b>Agent organisation</a><a href="#s4"><b>4</b>Two-week plan</a><a href="#s5"><b>5</b>Credit budget</a><a href="#s6"><b>6</b>Decisions</a><a href="#s7"><b>7</b>Project index</a><a href="#s8"><b>8</b>Risks</a><a href="#s9"><b>9</b>How the pipeline runs</a>
  </nav>
</header>

<section id="s1">
  <header><div class="kicker"><b>01</b> Vision and the ten-second summary</div><h2>What is being built, and how much of it exists as work already</h2></header>
  <p class="prose">${esc(plan.vision)}</p>
  <div class="stats">
    <div class="stat"><span class="n">${nProjects}</span><span class="l">Linear projects</span></div>
    <div class="stat"><span class="n">${nIssues}</span><span class="l">issues with full specs</span></div>
    <div class="stat hot"><span class="n">${nReady}</span><span class="l">Ready for Claude right now</span></div>
    <div class="stat"><span class="n">${daysLeft}</span><span class="l">days to Oct 1 deadline</span></div>
    <div class="stat"><span class="n">${nMilestones}</span><span class="l">dated milestones</span></div>
    <div class="stat"><span class="n">${nLeads}+${nSubs}</span><span class="l">lead characters + sub-characters</span></div>
  </div>
  <ul class="summary">
    <li><b>The template is the product; apps are instances.</b> <code>paperos create &lt;app&gt;</code> clones one monorepo into a pre-provisioned imagine-os repo and wires forge mirror, CI, Pages demo and a Linear project.</li>
    <li><b>Specs are the contract.</b> Every page has a <code>page.spec.yaml</code> (logic, access, data, integrations, layout, components, edge cases). Agents build from it; gates test against it.</li>
    <li><b>Linear is the queue.</b> Ready for Claude issues become parallel Claude Code sessions; only weekly release candidates and a dozen one-off decisions reach Justin.</li>
    <li><b>30% of credits go to machines reviewing machines</b>, because unreviewed agent code is the fastest way to waste the other 70%.</li>
  </ul>
</section>

<section id="s2">
  <header><div class="kicker"><b>02</b> System architecture</div><h2>Twelve core systems and what moves between them</h2></header>
  <figure>
    <div class="figwrap">${ar}</div>
    <figcaption>Read top to bottom: Linear feeds Claude sessions, whose PRs pass four automated gates before the issue moves on. The spec band in the middle is what everything else reads: codegen scaffolds pages from it, the design system's component IDs are referenced by it, view specs drive the tables engine, and conformance and permission tests are derived from it. The app shell is the one bundle that reaches every device; identity and realtime serve it; business, growth and migration are modules an app can remove; Postgres with row-level security is the single source of truth underneath.</figcaption>
  </figure>
</section>

<section id="s3">
  <header><div class="kicker"><b>03</b> Agent organisation</div><h2>Nine lead characters, ${nSubs} sub-characters, every one with explicit tools and access</h2></header>
  <p class="prose mute" style="margin-bottom:22px">Each character is a <code>.claude/agents</code> definition with its own skills, MCP allowlist, scoped forge bot account and credit budget. Sub-characters are the sub-agents a lead dispatches; access chips are the scopes the orchestrator grants and nothing more. Justin is the only human in the chart.</p>
  <div class="org">
    <div class="person justin"><h4>Justin Massion</h4><span class="t-mono">founder · only reviewer · owns Needs Justin</span></div>
    <div class="vline"></div>
    ${agentCard(atlas, true)}
    <div class="rail"></div>
    <div class="agents">${leads.map(g => agentCard(g, false)).join('')}</div>
  </div>
</section>

<section id="s4">
  <header><div class="kicker"><b>04</b> The two-week plan</div><h2>Three phases, ${nMilestones} milestones, one deadline</h2></header>
  <div class="phases">${plan.phases.map(ph => `<div class="phasecard ${ph.key.toLowerCase()}"><span class="t-mono">${ph.key} · ${ph.dates.replace(' to ', ' → ')}</span><h3>${esc(ph.name)}</h3><p>${esc(ph.goal)}</p></div>`).join('')}</div>
  <figure style="margin-top:22px">
    <div class="figwrap">${tl}</div>
    <figcaption>Each row is a Linear project; each dot is one of its three milestones at its target date (hover a dot for the milestone and its goal). Bands are the phases. The P0 rows all land their first milestone by Sep 19 or 20, which is the serial chain the risks section warns about; P2 projects do not start until their P0 and P1 dependencies exist.</figcaption>
  </figure>
</section>

<section id="s5">
  <header><div class="kicker"><b>05</b> Credit budget</div><h2>Where roughly $10,000 of Claude credits goes</h2></header>
  <figure>
    <div class="figwrap">${bg}</div>
    <figcaption>Share of credit spend by activity, with the dollar equivalent at a $10,000 total. Review and QA is emphasised because it is the number that makes the plan work: it buys the human review Justin cannot supply. Per-character budgets and a kill switch in the orchestrator enforce the split; credit metering posts the daily burn to Linear.</figcaption>
  </figure>
  <ul class="reasons">${plan.budget.map(b => `<li><span class="t-mono">${b.share_pct}%</span><div><b>${esc(b.area)}</b><span>${esc(b.why)}</span></div></li>`).join('')}</ul>
</section>

<section id="s6">
  <header><div class="kicker"><b>06</b> Key architecture decisions</div><h2>${plan.decisions.length} decisions, each with the reason it was taken</h2></header>
  <div class="decisions">${plan.decisions.map(d => `<article class="dec"><h3>${esc(d.title)}</h3><div><span class="k">Decision</span><p>${esc(d.decision)}</p></div><div><span class="k">Why</span><p class="why">${esc(d.why)}</p></div></article>`).join('')}</div>
</section>

<section id="s7">
  <header><div class="kicker"><b>07</b> Full index</div><h2>${nProjects} projects, ${nIssues} issues, every one linked to Linear</h2></header>
  <div class="legend"><span class="phase p0">P0</span><span>Foundation, Sep 17–20</span><span class="phase p1">P1</span><span>Core systems, Sep 21–26</span><span class="phase p2">P2</span><span>Business layer and hardening, Sep 27–Oct 1</span><span class="ready">Ready for Claude</span><span>unblocked now; the orchestrator may claim it</span></div>
  <div class="index">${projects.map(projectCard).join('')}</div>
</section>

<section id="s8">
  <header><div class="kicker"><b>08</b> Risks</div><h2>Six things that can break the plan, from the completeness review</h2></header>
  <ol class="risks">${risks.map(([t, b]) => `<li><div><b>${esc(t)}</b><p>${esc(b)}</p></div></li>`).join('')}</ol>
</section>

<section id="s9">
  <header><div class="kicker"><b>09</b> How the pipeline runs</div><h2>Six states, one human column</h2></header>
  <div class="pipe">
    <div class="state"><h4>Backlog</h4><span class="who">Atlas · Decomposer</span><p>Issue exists with a full spec but is blocked by a dependency or not yet scheduled.</p></div>
    <div class="state claude"><h4>Ready for Claude</h4><span class="who">Dispatcher</span><p>Spec-complete and unblocked. The orchestrator claims it and spawns a Claude Code session in its own worktree as the owning character.</p></div>
    <div class="state"><h4>In Progress</h4><span class="who">the character</span><p>Session builds against the spec, logs every prompt and tool call, opens a PR with spec, screenshots and gate checklist.</p></div>
    <div class="state"><h4>In Review</h4><span class="who">Sentinel · 4 gates</span><p>Static checks, three reviewer agents, screenshots and video across 7 widths, edge-case hunter. Merger merges green PRs.</p></div>
    <div class="state justin"><h4>Needs Justin</h4><span class="who">Justin</span><p>Only human decisions land here: weekly release candidate, credentials, spend increases, roster changes. Kept under five open items.</p></div>
    <div class="state"><h4>Done</h4><span class="who">Merger · Changelog Scribe</span><p>Merged and tagged; changelog written; Linear closed automatically; dependents unblock into Ready for Claude.</p></div>
  </div>
  <div class="todo">
    <h3>What Justin has to do</h3>
    <p class="mute" style="font-size:14px">Watch one column. Everything else is the agents' job, and a stale item in Needs Justin stalls every issue behind it.</p>
    <ul>
      <li><b>Day one:</b> answer the single credentials item from PAP-25 (Hetzner, domain or Cloudflare, Resend, Apple developer program). Every infra issue waits on it.</li>
      <li><b>Weekly:</b> approve or reject one release candidate from its one-page digest (what changed, risks, screenshots, open questions). Treat the first one as a smoke test.</li>
      <li><b>Week one, once:</b> spot-check five gate 2 verdicts against the PRs so the reviewer agents have a calibration point.</li>
      <li><b>As they arrive (about 12 over two weeks):</b> new character or roster approvals, spend increases past a character's budget, Stripe live keys and payroll sandbox, licence of our own code, flipping outreach out of sandbox, S0 security waivers.</li>
      <li><b>Now:</b> decide what the Oct 1 release candidate must contain. Suggested: template + spec builder + tables + collab + identity + billing; let the rest land after the deadline with remaining credits.</li>
    </ul>
  </div>
  <div class="readynow">
    <h3>The ${nReady} issues the orchestrator can start on today</h3>
    <ul>${readyList.map(i => `<li><a href="${i.url}" target="_blank" rel="noopener"><span class="id">${i.identifier}</span>${esc(i.title)}</a></li>`).join('')}</ul>
  </div>
</section>

<footer>Generated 2026-09-17 from plan.json, critique.md and the Linear build log · origin issue <a href="https://linear.app/paperos/issue/PAP-5">PAP-5</a> · team <a href="https://linear.app/paperos/team/PAP/all">PAP</a></footer>
</div>
`;
fs.writeFileSync(dir + '/blueprint.html', html);
console.log('wrote', (html.length / 1024).toFixed(0), 'KB', { nIssues, nReady, nProjects, nMilestones, nLeads, nSubs, daysLeft });
