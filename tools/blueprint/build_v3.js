#!/usr/bin/env node
// Builds site/index.html (and site/data.json) from the live Linear snapshot.
//   node tools/blueprint/build_v3.js
// Env: PAPEROS_REPO (repo root, default: two levels up), MODEL_EFFORT (optional path to
// the cost estimate's model-effort.json), PAPEROS_ARTIFACT_OUT (optional path for the
// artifact body without the document wrapper, for publishing with the Artifact tool).
'use strict';
const fs = require('fs');
const path = require('path');

const ROOT = process.env.PAPEROS_REPO || path.resolve(__dirname, '..', '..');
const read = p => fs.readFileSync(p, 'utf8');
const snap = JSON.parse(read(path.join(ROOT, 'plan/linear-snapshot-live.json')));
const plan = JSON.parse(read(path.join(ROOT, 'plan/plan.json')));
const ids = JSON.parse(read(path.join(ROOT, 'plan/linear-ids.json')));
const mePath = process.env.MODEL_EFFORT || path.join(ROOT, 'plan/model-effort.json');
const me = mePath && fs.existsSync(mePath) ? JSON.parse(read(mePath)) : null;
const template = read(path.join(__dirname, 'template.html'));
let archSvg = read(path.join(__dirname, 'architecture.svg'));

const TODAY = snap.takenAt.slice(0, 10);
const DEADLINE = '2026-10-01';
const daysLeft = Math.round((Date.parse(DEADLINE) - Date.parse(TODAY)) / 86400000);
const REPO = 'https://github.com/imagine-os/linear-builder';
const PAGES = 'https://imagine-os.github.io/linear-builder/';

const shortName = {
  'app-shell': 'App shell & template', 'data-layer': 'Data layer', forge: 'Forge independence', identity: 'Identity & audiences',
  'design-system': 'Design system', quality: 'Quality pipeline', 'pm-linear': 'PM & Claude pipeline', agents: 'Agent characters',
  'spec-builder': 'Spec builder', collab: 'Collaboration & knowledge', realtime: 'Multiplayer & realtime', input: 'Multi-input & a11y',
  tables: 'Table & views engine', 'business-core': 'Business core', growth: 'Growth & CRM', migration: 'Migration & import', libraries: 'Library discovery'
};
const phaseOrder = { P0: 0, P1: 1, P2: 2 };
const SIZE_W = { S: 0.5, M: 1, L: 2 };
const stKey = { Backlog: 'backlog', 'Ready for Claude': 'ready', 'In Progress': 'progress', 'In Review': 'review', 'Needs Justin': 'justin', Done: 'done', Duplicate: 'dup', Canceled: 'dup', Todo: 'backlog' };

/* ---------------- issues ---------------- */
const sizeOf = i => { const m = /\*\*Size:?\*\*:?\s*([SML])/.exec(i.description || ''); return m ? m[1] : ''; };
const issues = snap.issues.map(i => ({
  id: i.identifier, n: Number(i.identifier.split('-')[1]), t: i.title, s: i.state, p: i.projectKey, ph: i.phase || '', ty: i.type || '', sz: sizeOf(i),
  pr: i.priority, par: i.parent || null, ch: i.children || [], d: !!i.deferred, ms: i.milestone || '', msd: i.milestoneDate || '', url: i.url,
  _blocks: i.blocks || [], _blockedBy: i.blockedBy || []
}));
const byId = Object.fromEntries(issues.map(i => [i.id, i]));
const countKey = i => (i.d && stKey[i.s] === 'backlog') ? 'deferred' : (stKey[i.s] || 'backlog');

/* ---------------- projects ---------------- */
const projects = [...plan.projects].sort((a, b) => phaseOrder[a.phase] - phaseOrder[b.phase] || plan.projects.indexOf(a) - plan.projects.indexOf(b)).map(p => {
  const mine = issues.filter(i => i.p === p.key);
  const counts = {}; for (const i of mine) counts[countKey(i)] = (counts[countKey(i)] || 0) + 1;
  const msMap = new Map();
  for (const i of mine) if (i.ms) { const m = msMap.get(i.ms) || { name: i.ms, date: i.msd, issues: 0, ready: 0, goal: '' }; m.issues++; if (i.s === 'Ready for Claude') m.ready++; if (i.msd && (!m.date || i.msd < m.date)) m.date = i.msd; msMap.set(i.ms, m); }
  for (const m of msMap.values()) { const pm = p.milestones.find(x => x.name === m.name); m.goal = pm ? pm.goal : ''; if (!m.date && pm) m.date = pm.targetDate; }
  const milestones = [...msMap.values()].sort((a, b) => a.date.localeCompare(b.date) || a.name.localeCompare(b.name));
  return {
    key: p.key, name: p.name, short: shortName[p.key] || p.name, url: (ids.projects[p.key] || {}).url || 'https://linear.app/paperos/team/PAP/projects',
    phase: p.phase, priority: p.priority, dependsOn: p.dependsOn, summary: p.summary, total: mine.length, counts,
    ready: counts.ready || 0, deferred: mine.filter(i => i.d).length, umbrellas: mine.filter(i => i.ch.length).length, milestones
  };
});
const P = Object.fromEntries(projects.map(p => [p.key, p]));

/* ---------------- edges (project to project, from blocks) ---------------- */
const edgeMap = new Map();
let relations = 0;
for (const i of issues) for (const t of i._blocks) { relations++; const to = byId[t]; if (!to || to.p === i.p) continue; const k = i.p + '>' + to.p; edgeMap.set(k, (edgeMap.get(k) || 0) + 1); }
const edges = [...edgeMap.entries()].map(([k, n]) => { const [from, to] = k.split('>'); return { from, to, n }; }).sort((a, b) => b.n - a.n);

/* ---------------- critical path (longest size-weighted chain over blocks) ---------------- */
const active = new Set(issues.filter(i => i.s !== 'Duplicate' && i.s !== 'Canceled' && !i.d).map(i => i.id));
const memo = new Map();
function best(u) {
  if (memo.has(u)) return memo.get(u);
  const w = SIZE_W[byId[u].sz] || 1; let res = { days: w, path: [u] };
  for (const t of byId[u]._blocks) if (active.has(t)) { const b = best(t); if (w + b.days > res.days) res = { days: w + b.days, path: [u, ...b.path] }; }
  memo.set(u, res); return res;
}
let critical = { days: 0, path: [] };
for (const u of active) { const b = best(u); if (b.days > critical.days) critical = b; }
const critProjects = [...new Set(critical.path.map(id => byId[id].p))];

/* ---------------- totals ---------------- */
const byState = {}; for (const i of issues) byState[countKey(i)] = (byState[countKey(i)] || 0) + 1;
const totals = {
  issues: issues.length, ready: issues.filter(i => i.s === 'Ready for Claude').length, umbrellas: issues.filter(i => i.ch.length).length,
  duplicates: issues.filter(i => i.s === 'Duplicate').length, deferred: issues.filter(i => i.d).length, relations,
  milestones: projects.reduce((a, p) => a + p.milestones.length, 0), needsJustin: issues.filter(i => i.s === 'Needs Justin').length, byState
};
const phaseDates = { P0: ['2026-09-17', '2026-09-20'], P1: ['2026-09-21', '2026-09-26'], P2: ['2026-09-27', '2026-10-01'] };
const goalShort = {
  P0: 'Pipeline, orchestrator and roster live; template runs on web and desktop; Postgres, Forgejo, auth, spec schema and gates 1 to 3 exist.',
  P1: 'Spec builder, components, multiplayer, tables and views, collaboration, multi-input and permissions reach a usable v1.',
  P2: 'Payments, ledger, payroll, CRM and importers ship; load, recovery and accessibility drills pass; first release candidate.'
};
const phases = plan.phases.map(ph => ({ key: ph.key, name: ph.name, start: phaseDates[ph.key][0], end: phaseDates[ph.key][1], goal: ph.goal, goalShort: goalShort[ph.key], issues: issues.filter(i => i.ph === ph.key).length }));
const phaseNow = phases.find(p => TODAY >= p.start && TODAY <= p.end) || phases[0];
const milestonesFlat = projects.flatMap(p => p.milestones.map(m => ({ ...m, project: p.key }))).sort((a, b) => a.date.localeCompare(b.date) || projects.findIndex(p => p.key === a.project) - projects.findIndex(p => p.key === b.project));

/* ---------------- hand-written content ---------------- */
const lede = 'PaperOS Core Platform is the reusable foundation every future PaperOS app is generated from: one spec-driven TypeScript monorepo that ships to web, desktop and mobile with the data layer, design system, multiplayer, tables, identity and business plumbing already wired. It is built and reviewed by <b>nine Claude agent characters</b> working from Linear behind four automated quality gates, so that by <b>1 October 2026</b> a new app goes from blank screen to running product in hours, and Justin only reviews release candidates.';
const meta = [
  `<a href="https://linear.app/paperos/team/PAP/all">Linear team PAP</a>`, `<a href="${REPO}">imagine-os/linear-builder</a>`, `<a href="${PAGES}previous/index-v2.html">previous version of this page</a>`,
  `${projects.length} projects`, `${totals.issues} issues`, `${relations} blocking relations`, `${totals.milestones} milestones`, `$10,000 credits`
];
const nj = [
  { id: 'NJ-1', when: 'Sep 17 12:50Z', done: true, show: true, text: 'Linear: upgrade the workspace plan so the remaining specified issues can be created (PAP-91).', resolved: 'Justin upgraded to Basic; all 153 pending issues were created as PAP-280 to PAP-432 and PAP-91 is back in Ready for Claude.' },
  { id: 'NJ-2', when: 'Sep 17', show: true, text: 'Infra credential batch on PAP-25: Hetzner account, registrar or Cloudflare token, Resend, sops recovery key. Every infra issue waits on these.' },
  { id: 'NJ-3', when: 'Sep 17', show: true, text: 'GitHub App on the imagine-os org with repo and workflow scope (PAP-47).' },
  { id: 'NJ-4', when: 'Sep 17', show: true, text: 'Anthropic Console: orchestrator API key, $10K hard limit, usage export (PAP-98).' },
  { id: 'NJ-5', when: 'Sep 18', show: true, text: 'Linear: orchestrator API key and webhook signing secret (PAP-92, PAP-97).' },
  { id: 'NJ-6', when: 'Sep 19', show: true, text: 'Code signing (PAP-256): Apple Developer Program and Windows signing, or accept unsigned v0.1.0 installers. Default after 48 h: unsigned.' },
  { id: 'NJ-7', when: 'Sep 20', text: 'Licence of the template code (PAP-211); default Apache-2.0.' },
  { id: 'NJ-8', when: 'Sep 20', text: 'Approve the Justin queue format (PAP-94) and the issue contract (PAP-93).' },
  { id: 'NJ-9', when: 'Sep 21', text: 'Hire the roster (PAP-104, PAP-210). RC0.' },
  { id: 'NJ-10', when: 'Sep 22', text: 'Stripe test-mode account (PAP-177); Google OAuth consent screen (PAP-224, PAP-200).' },
  { id: 'NJ-11', when: 'Sep 24', text: 'Domain: set PAPEROS_DOMAIN or keep sslip.io for v0.1.0. RC1.' },
  { id: 'NJ-12', when: 'Sep 25', text: 'Payroll provider (PAP-176): Check sandbox (default) or Gusto Embedded.' },
  { id: 'NJ-13', when: 'Sep 25', text: 'Airtable demo base and token (PAP-202); Slack incoming webhook (PAP-136).' },
  { id: 'NJ-14', when: 'Sep 27', text: 'Stop-loss checkpoint: go or no-go on the deferred stretch pool.' },
  { id: 'NJ-15', when: 'Sep 28', text: 'Release candidate v0.1.0-rc.2 (PAP-254): /approve or /reject. RC2.' },
  { id: 'NJ-16', when: 'Sep 29', text: 'Approve the content agent (PAP-192) and migration agent (PAP-208).' },
  { id: 'NJ-17', when: 'Sep 29', text: 'Accessibility statement wording (PAP-160).' },
  { id: 'NJ-18', when: 'Sep 30', text: 'Industry list and terminology defaults (PAP-126).' },
  { id: 'NJ-19', when: 'Sep 30', text: 'Scope freeze: the deferred list becomes milestone v0.2.' },
  { id: 'NJ-20', when: 'Oct 1', text: 'Release candidate v0.1.0: /approve promotes and tags. RC3.' },
  { id: 'NJ-21', when: 'Oct 1', text: 'PAP-5: close or keep as scoreboard (PAP-95 vs PAP-29).' }
];
const docs = [
  { key: 'blueprint', title: 'Blueprint', line: 'Vision, the fifteen decisions, phases, budget and the project index. This page is its visual form.', linear: 'https://linear.app/paperos/document/paperos-core-platform-blueprint-0c2115fe48f1', github: `${REPO}/blob/main/docs/blueprint.md` },
  { key: 'contracts', title: 'Interface & Data Contracts', line: 'The shapes every project codes against (ids, tenancy, Principal, Money, FilterTree, events). Changing one needs an ADR.', linear: 'https://linear.app/paperos/document/paperos-interface-and-data-contracts-d40e6a4d227c', github: `${REPO}/blob/main/docs/interface-and-data-contracts.md` },
  { key: 'project-contracts', title: 'Project Contract sections', line: 'Each Linear project carries what it provides to and consumes from the others.', linear: 'https://linear.app/paperos/team/PAP/projects', github: '' },
  { key: 'roster', title: 'Agent Roster', line: 'The org chart above, the routing rules that decide who picks up an issue, and links to every character sheet.', linear: 'https://linear.app/paperos/document/paperos-agent-roster-org-chart-and-character-index-fc7ea7f41ff3', github: `${REPO}/blob/main/docs/agent-roster.md` },
  { key: 'security', title: 'Security & Threat Model', line: 'Assets, trust boundaries, the Linear deny list and which issue owns each control.', linear: 'https://linear.app/paperos/document/paperos-security-and-threat-model-51fd5fd8929c', github: `${REPO}/blob/main/docs/security-and-threat-model.md` },
  { key: 'schedule', title: 'Execution Schedule', line: 'Day by day to 1 October: starts, capacity, the Needs Justin table, credit burn and stop-loss rules.', linear: 'https://linear.app/paperos/document/paperos-execution-schedule-1fa3d38d6795', github: `${REPO}/blob/main/docs/execution-schedule.md` },
  { key: 'golden', title: 'New App in Ten Minutes', line: 'The golden path the whole platform serves: one command, one paragraph, a deployed multi-device app.', linear: '', github: `${REPO}/blob/main/docs/new-app-in-ten-minutes.md` }
];
const risks = [
  { title: 'P0 is serial: scaffold, local stack, Drizzle, entities, RLS, API, auth, Yjs cannot run in parallel.', body: 'The schedule already moved the first milestones of data-layer, identity, design-system and pm-linear to Sep 20 to 23. The branch-start rule (start against a blocker\'s open PR) is what makes the rest fit before Oct 1; if sessions wait for merges instead, add two days to every P1 milestone.' },
  { title: 'Human account setup is on the critical path.', body: 'Hetzner, a domain or Cloudflare, Resend, the Apple developer program, Stripe test keys, a payroll sandbox. PAP-25 batches the infra credentials into NJ-2 on day one; answer it the same day or every infra issue waits. Issues whose credential is late start in sandbox or dry-run mode.' },
  { title: 'The orchestrator and the Coolify host hold every credential.', body: 'A compromised session prompt or leaked token there is a total compromise. Tool scopes, security scans and the destructive-action deny list are the mitigations; they must not slip to P1.' },
  { title: 'Automated review replaces human review, but nobody has calibrated it yet.', body: 'Thirty percent of credits go to reviewer agents, vision inspection and edge-case hunting. Until the eval harness produces a false-negative rate, treat the first release candidate as a smoke test and spot-check five Gate 2 verdicts in week one.' },
  { title: 'P2 carries the business layer, growth, migration and hardening in five days.', body: 'Stripe Connect, ledger, payroll adapter, CRM, social scheduler and importers are each large. Something will not ship by Oct 1. Decide now what the release candidate must contain (suggested: template, spec builder, tables, collaboration, identity, billing) and let the rest land after the deadline.' },
  { title: 'Scope creep by design.', body: 'The brief says go deep and the plan obliges, but 400-plus issues with generous specs will burn credits on research and docs. Enforce the time boxes in research issues (one session each, ADR or stop) and let credit metering post the daily burn so the trade-off is visible by day three.' },
  { title: 'Linear\'s issue cap shaped the plan once and can again.', body: 'The Basic plan stopped issue creation at 275; the round-2 set was created after the upgrade question was filed as NJ-1 on PAP-91. If the cap returns, umbrella parents run as single large sessions using their children\'s specs inline, which means coarser sessions and a thinner Ready queue, not lost scope.' }
];
const decisions = plan.decisions.map(d => ({ title: d.title, decision: d.decision, why: d.why }));

let modelEffort = null;
if (me) {
  const all = me.counts_by_model_effort || {}, act = me.counts_active_non_deferred || {};
  const rowsDef = [['claude-fable-5-1', 'Fable 5.1'], ['claude-opus-5', 'Opus 5'], ['claude-sonnet-5', 'Sonnet 5']];
  const rows = rowsDef.map(([k, label]) => { const r = { label }; let tot = 0; for (const e of ['low', 'medium', 'high']) { r[e] = (all[k] || {})[e] || 0; tot += r[e]; } r.total = tot; return r; });
  const assigned = rows.reduce((a, r) => a + r.total, 0);
  const activeN = Object.values(act).reduce((a, n) => a + n, 0);
  const umbrellas = (all.null || {})['-'] || totals.umbrellas;
  modelEffort = { rows, assigned, umbrellas, note: `Scenario E of the cost estimate (${me.takenAt.slice(0, 10)} snapshot): Fable 5.1 on the eight keystone specs every other spec reads, Opus 5 on the scaffold, orchestrator, security-titled and P0 data, identity, pipeline and realtime work, Sonnet 5 elsewhere; deferred leaves sit in Sonnet 5 / low (${assigned - activeN} of the ${assigned}). Effort scales output tokens (low ×0.6, medium ×1, high ×1.4). Estimated <b>$3,490</b> for the ${activeN} issues in the 1 October scope, about a third of the $10,000 budget; the deferred set would add about $295.` };
}

const footer = `<span>Built from <span class="mono">plan/linear-snapshot-live.json</span> taken ${snap.takenAt} by <span class="mono">tools/blueprint/build_v3.js</span>.</span><span>Linear is the system of record; where this page and an issue disagree, the issue wins.</span><span><a href="${PAGES}previous/index-v2.html">Previous version</a> · <a href="${REPO}">Source</a></span>`;

const data = {
  takenAt: snap.takenAt, today: TODAY, deadline: DEADLINE, daysLeft, phaseNow: phaseNow.key, lede, meta, totals, phases, projects, edges,
  topEdges: edges.slice(0, 3), critical: { days: critical.days, ids: critical.path, projects: critProjects }, milestonesFlat,
  issues: issues.map(({ _blocks, _blockedBy, ...i }) => i), agents: plan.agents, budget: plan.budget, decisions, modelEffort, nj, docs, risks, footer
};

/* ---------------- render ---------------- */
archSvg = archSvg.replace(/267 issues · 534 blocking relations/, `${totals.issues} issues · ${relations} blocking relations`).replace(/class="fig"/, 'class="fig arch-fig"');
const json = JSON.stringify(data).replace(/<\/script/gi, '<\\/script').replace(/<!--/g, '<\\!--');
const body = template.replace('__ARCH_SVG__', () => archSvg).replace('__DATA__', () => json);
const doc = `<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n</head>\n<body>\n${body}\n</body>\n</html>\n`;

const siteDir = path.join(ROOT, 'site');
fs.mkdirSync(siteDir, { recursive: true });
fs.writeFileSync(path.join(siteDir, 'index.html'), doc);
fs.writeFileSync(path.join(siteDir, 'data.json'), JSON.stringify(data, null, 1));
if (process.env.PAPEROS_ARTIFACT_OUT) fs.writeFileSync(process.env.PAPEROS_ARTIFACT_OUT, body);
console.log(`issues ${totals.issues} · ready ${totals.ready} · deferred ${totals.deferred} · relations ${relations} · edges ${edges.length} · milestones ${totals.milestones} · critical ${critical.path.length} issues / ${critical.days} days · html ${(doc.length / 1024).toFixed(0)} KB${modelEffort ? ' · model-effort included' : ' · no model-effort file'}`);
