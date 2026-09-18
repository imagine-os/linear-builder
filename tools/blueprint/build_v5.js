#!/usr/bin/env node
// Builds site/index.html (GitHub Pages, may load 3d-force-graph from jsDelivr) and site/data.json from the live
// Linear snapshot, plus an artifact body (self-contained, no external scripts) when PAPEROS_ARTIFACT_OUT is set.
//   node tools/blueprint/build_v4.js
// Env: PAPEROS_REPO (repo root, default: two levels up), MODEL_EFFORT (path to model-effort.json), CHUNKS (path to
// the chunk plan, default plan/round4/chunks-v2.json, the round-4 plan; plan/chunks.json is the round-3 plan), PAPEROS_ARTIFACT_OUT (artifact body path).
// Blueprint v4: adds the graph-gallery views (objects map, lanes skill tree, radial tree, images, icons, objects 3D,
// radial 3D) with shared filters and sorting, the Modules & plug points map and the $2,500 chunk plan.
// Blueprint v5 (round 4): the five initiatives, the C1/C2/C3 cycle strip, the estimates view (points per project by
// state, burn-up placeholder), the Round 4 section (what changed, 23 projects, top gaps, Linear features table),
// Triage and Needs Justin tiles, cycle / estimate / initiative / new-in-round-4 filters and estimate, due date and
// cycle in the issue index. Reads the round-4 snapshot from tools/linear/round4/snapshot4.py.
'use strict';
const fs = require('fs');
const path = require('path');

const ROOT = process.env.PAPEROS_REPO || path.resolve(__dirname, '..', '..');
const read = p => fs.readFileSync(p, 'utf8');
const snap = JSON.parse(read(path.join(ROOT, 'plan/linear-snapshot-live.json')));
const plan = JSON.parse(read(path.join(ROOT, 'plan/plan.json')));
const ids = JSON.parse(read(path.join(ROOT, 'plan/linear-ids.json')));
const mePath = process.env.MODEL_EFFORT || path.join(ROOT, 'plan/model-effort.json');
const me = fs.existsSync(mePath) ? JSON.parse(read(mePath)) : null;
const chunksPath = process.env.CHUNKS || path.join(ROOT, 'plan/round4/chunks-v2.json');
const chunksRaw = fs.existsSync(chunksPath) ? JSON.parse(read(chunksPath)) : null;
const template = read(path.join(__dirname, 'template_v5.html'));
const v4 = name => read(path.join(__dirname, 'v5', name));
const readOpt = p => fs.existsSync(p) ? read(p) : '';
const mergeReport = readOpt(path.join(ROOT, 'plan/round4/merge-report.md'));
const verifyMd = readOpt(path.join(ROOT, 'plan/round4/verify.md'));
const featuresMd = readOpt(path.join(ROOT, 'docs/linear-features.md'));
const crossCut = fs.existsSync(path.join(ROOT, 'plan/round4/gaps/cross-cutting.json')) ? JSON.parse(read(path.join(ROOT, 'plan/round4/gaps/cross-cutting.json'))) : { newProjects: [] };
const R4_FIRST = 498; // PAP-497 closed round 3; every identifier from PAP-498 was created in round 4
let archSvg = read(path.join(__dirname, 'architecture.svg'));

const TODAY = snap.takenAt.slice(0, 10);
const DEADLINE = '2026-10-01';
const daysLeft = Math.round((Date.parse(DEADLINE) - Date.parse(TODAY)) / 86400000);
const REPO = 'https://github.com/imagine-os/linear-builder';
const PAGES = 'https://imagine-os.github.io/linear-builder/';

const shortName = {
  'module-system': 'Module system', 'app-shell': 'App shell & template', 'data-layer': 'Data layer', forge: 'Forge independence', identity: 'Identity & audiences',
  'design-system': 'Design system', quality: 'Quality pipeline', 'pm-linear': 'PM & Claude pipeline', agents: 'Agent characters',
  'spec-builder': 'Spec builder', collab: 'Collaboration & knowledge', realtime: 'Multiplayer & realtime', input: 'Multi-input & a11y',
  tables: 'Table & views engine', 'business-core': 'Business core', growth: 'Growth & CRM', migration: 'Migration & import', libraries: 'Library discovery',
  assistant: 'Tenant AI assistant', workflows: 'Workflows & documents', engagement: 'Scheduling & engagement', commerce: 'Commerce & operations', 'platform-ops': 'Platform operations'
};
// Round-4 project hues: validated with the dataviz palette validator (adjacent CVD dE >= 9, normal-vision dE >= 22; names are always printed beside the hue)
const NEW_PROJECT_STYLE = {
  assistant: { color: '#E87BA4', icon: 'Sparkles' }, workflows: { color: '#4A3AA7', icon: 'Workflow' }, engagement: { color: '#1BAF7A', icon: 'Calendar' },
  commerce: { color: '#EDA100', icon: 'ShoppingCart' }, 'platform-ops': { color: '#EB6834', icon: 'Activity' }
};
const phaseOrder = { P0: 0, P1: 1, P2: 2 };
const SIZE_W = { S: 0.5, M: 1, L: 2 };
const stKey = { Backlog: 'backlog', 'Ready for Claude': 'ready', 'In Progress': 'progress', 'In Review': 'review', 'Needs Justin': 'justin', Done: 'done', Duplicate: 'dup', Canceled: 'dup', Todo: 'backlog', Triage: 'triage' };
const modelShort = l => l ? String(l).replace('Model: ', '') : '';
const effortShort = l => l ? String(l).replace('Effort: ', '') : '';

/* ---------------- issues ---------------- */
const sizeOf = i => { const m = /\*\*Size:?\*\*:?\s*([SML])/.exec(i.description || ''); return m ? m[1] : ''; };
const issues = snap.issues.map(i => ({
  id: i.identifier, n: Number(i.identifier.split('-')[1]), t: i.title, s: i.state, p: i.projectKey, ph: i.phase || '', ty: i.type || '', sz: sizeOf(i),
  pr: i.priority, par: i.parent || null, ch: i.children || [], d: !!i.deferred, ms: i.milestone || '', msd: i.milestoneDate || '', url: i.url,
  m: modelShort((i.model || [])[0]), e: effortShort((i.effort || [])[0]), sf: i.surfaces || [],
  bb: (i.blockedBy || []).slice(), nb: (i.blocks || []).length,
  est: i.estimate == null ? null : i.estimate, due: i.dueDate || '', cy: i.cycle ? i.cycle.number : 0, r4: Number(i.identifier.split('-')[1]) >= R4_FIRST,
  att: (i.attachments || []).length, cc: i.commentCount || 0, chunk: i.chunk ? Number(String(i.chunk).replace('Chunk ', '')) : 0, sty: i.stateType || '',
  _blocks: i.blocks || [], _blockedBy: i.blockedBy || []
}));
const byId = Object.fromEntries(issues.map(i => [i.id, i]));
const countKey = i => (i.d && stKey[i.s] === 'backlog') ? 'deferred' : (stKey[i.s] || 'backlog');
const canonical = issues.filter(i => i.n >= 13 && i.s !== 'Duplicate');

/* ---------------- projects (17 from plan.json + module-system from the snapshot) ---------------- */
const snapProj = Object.fromEntries(snap.projects.map(p => [p.key, p]));
const planProjects = [...plan.projects];
if (!planProjects.some(p => p.key === 'module-system') && snapProj['module-system']) {
  const sp = snapProj['module-system'];
  planProjects.unshift({
    key: 'module-system', name: sp.name, color: '#0EA5E9', icon: 'Puzzle', phase: 'P0', priority: 1, dependsOn: ['app-shell', 'data-layer'],
    summary: 'The kernel that makes every PaperOS module plug-and-play: manifest schema, registry and DI container, flag-driven swaps with shadow-run, event schema registry, gateway routing by contract, UI slots, dependency lint and map, compatibility matrix, conformance runner, swap CLI, migration adapter kit, config and secrets port, module docs and the shell swap drill.',
    milestones: sp.milestones.map(m => ({ name: m.name, targetDate: m.targetDate, goal: { 'Kernel and lint live': 'Manifest schema, registry, DI, lint rules R7 to R11 and the committed dependency map', 'Contracts and conformance wired': 'Every module publishes contract v0.1, passes conformance and binds behind a flag', 'Shell swap drill passes': 'A minimal second shell provides the same contract, is flipped for the demo tenant and rolled back' }[m.name] || '' }))
  });
}
const newProjMeta = Object.fromEntries((crossCut.newProjects || []).map(p => [p.key, p]));
for (const sp of snap.projects) {
  if (!sp.key || planProjects.some(p => p.key === sp.key)) continue;
  const meta = newProjMeta[sp.key] || {};
  planProjects.push({
    key: sp.key, name: sp.name, color: (NEW_PROJECT_STYLE[sp.key] || {}).color || sp.color || '#8A95A8', icon: (NEW_PROJECT_STYLE[sp.key] || {}).icon || 'Box',
    phase: meta.phase || 'P2', priority: sp.priority || 2, dependsOn: [], summary: (sp.description || meta.description || '').split(/(?<=\.)\s/)[0],
    milestones: (sp.milestones || []).map(m => ({ name: m.name, targetDate: m.targetDate, goal: m.description || '' })), isNew: true
  });
}
const projects = planProjects.sort((a, b) => phaseOrder[a.phase] - phaseOrder[b.phase] || planProjects.indexOf(a) - planProjects.indexOf(b)).map(p => {
  const mine = issues.filter(i => i.p === p.key);
  const counts = {}; for (const i of mine) counts[countKey(i)] = (counts[countKey(i)] || 0) + 1;
  const msMap = new Map();
  for (const i of mine) if (i.ms) { const m = msMap.get(i.ms) || { name: i.ms, date: i.msd, issues: 0, ready: 0, goal: '' }; m.issues++; if (i.s === 'Ready for Claude') m.ready++; if (i.msd && (!m.date || i.msd < m.date)) m.date = i.msd; msMap.set(i.ms, m); }
  for (const m of msMap.values()) { const pm = (p.milestones || []).find(x => x.name === m.name); m.goal = pm ? pm.goal : ''; if (!m.date && pm) m.date = pm.targetDate; }
  for (const sm of (snapProj[p.key] || { milestones: [] }).milestones) if (!msMap.has(sm.name)) msMap.set(sm.name, { name: sm.name, date: sm.targetDate, issues: 0, ready: 0, goal: ((p.milestones || []).find(x => x.name === sm.name) || {}).goal || '' });
  const milestones = [...msMap.values()].sort((a, b) => (a.date || '').localeCompare(b.date || '') || a.name.localeCompare(b.name));
  const url = (snapProj[p.key] || {}).url || (ids.projects[p.key] || {}).url || 'https://linear.app/paperos/team/PAP/projects';
  const sp = snapProj[p.key] || {};
  const pts = {}; for (const i of mine) if (i.est) pts[countKey(i)] = (pts[countKey(i)] || 0) + i.est;
  return {
    key: p.key, name: p.name, short: shortName[p.key] || p.name, url, color: p.color, icon: p.icon,
    phase: p.phase, priority: p.priority, dependsOn: p.dependsOn, summary: p.summary, total: mine.length, counts,
    ready: counts.ready || 0, deferred: mine.filter(i => i.d).length, umbrellas: mine.filter(i => i.ch.length).length, milestones,
    isNew: !!p.isNew, lead: sp.lead || null, health: sp.health || null, status: sp.status || null, startDate: sp.startDate || null, targetDate: sp.targetDate || null,
    linearPriority: sp.priority == null ? null : sp.priority, links: sp.links || [], initiatives: (sp.initiatives || []).map(x => x.name),
    update: sp.latestUpdate ? { at: sp.latestUpdate.createdAt, health: sp.latestUpdate.health, url: sp.latestUpdate.url, excerpt: String(sp.latestUpdate.body || '').replace(/\s+/g, ' ').slice(0, 220) } : null,
    points: Object.values(pts).reduce((a, n) => a + n, 0), pointsByState: pts, estimated: mine.filter(i => i.est).length,
    r4New: mine.filter(i => i.r4 && i.s !== 'Duplicate').length, r4Deferred: mine.filter(i => i.r4 && i.d).length, r4Children: mine.filter(i => i.r4 && i.par).length
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

/* ---------------- dependency levels (longest path from a source over blockedBy, canonical set) ---------------- */
const lvlMemo = new Map();
const canonSet = new Set(canonical.map(i => i.id));
function level(id) {
  if (lvlMemo.has(id)) return lvlMemo.get(id);
  lvlMemo.set(id, 0);
  let v = 0; for (const b of byId[id]._blockedBy) if (canonSet.has(b)) v = Math.max(v, level(b) + 1);
  lvlMemo.set(id, v); return v;
}
for (const i of canonical) i.lv = level(i.id);

/* ---------------- totals ---------------- */
const byState = {}; for (const i of issues) byState[countKey(i)] = (byState[countKey(i)] || 0) + 1;
const totals = {
  issues: issues.length, canonical: canonical.length, leaves: canonical.filter(i => !i.ch.length).length, ready: issues.filter(i => i.s === 'Ready for Claude').length, umbrellas: issues.filter(i => i.ch.length).length,
  duplicates: issues.filter(i => i.s === 'Duplicate').length, deferred: issues.filter(i => i.d).length, relations,
  milestones: projects.reduce((a, p) => a + p.milestones.length, 0), needsJustin: issues.filter(i => i.s === 'Needs Justin').length, byState,
  newRound3: issues.filter(i => i.n >= 433 && i.n < R4_FIRST).length, newRound4: issues.filter(i => i.r4).length,
  triage: issues.filter(i => i.s === 'Triage' || i.sty === 'triage').length,
  points: canonical.reduce((a, i) => a + (i.est || 0), 0), pointsDone: canonical.filter(i => i.s === 'Done').reduce((a, i) => a + (i.est || 0), 0),
  estimated: canonical.filter(i => i.est).length, unestimatedLeaves: canonical.filter(i => !i.ch.length && !i.est).length,
  withDue: canonical.filter(i => i.due).length, inCycle: canonical.filter(i => i.cy).length, comments: issues.reduce((a, i) => a + i.cc, 0), attachments: issues.reduce((a, i) => a + i.att, 0)
};
const phaseDates = { P0: ['2026-09-17', '2026-09-20'], P1: ['2026-09-21', '2026-09-26'], P2: ['2026-09-27', '2026-10-01'] };
const goalShort = {
  P0: 'Pipeline, orchestrator and roster live; template runs on web and desktop; Postgres, Forgejo, auth, spec schema, kernel and gates 1 to 3 exist.',
  P1: 'Spec builder, components, multiplayer, tables and views, collaboration, multi-input and permissions reach a usable v1; every module publishes its contract.',
  P2: 'Payments, ledger, payroll, CRM and importers ship; load, recovery and accessibility drills pass; the shell swap drill and the first release candidate.'
};
const phases = plan.phases.map(ph => ({ key: ph.key, name: ph.name, start: phaseDates[ph.key][0], end: phaseDates[ph.key][1], goal: ph.goal, goalShort: goalShort[ph.key], issues: issues.filter(i => i.ph === ph.key).length }));
const phaseNow = phases.find(p => TODAY >= p.start && TODAY <= p.end) || phases[0];
const milestonesFlat = projects.flatMap(p => p.milestones.map(m => ({ ...m, project: p.key }))).sort((a, b) => (a.date || '9').localeCompare(b.date || '9') || projects.findIndex(p => p.key === a.project) - projects.findIndex(p => p.key === b.project));

/* ---------------- modules and plug points (docs/module-system.md table 1.1) ---------------- */
const MODULES = [
  { key: 'module-system', kind: 'kernel', owner: 'Atlas / Forge', contract: '@paperos/kernel', provides: ['registry', 'DI container', 'flag swap', 'gateway', 'slots runtime', 'conformance runner', 'swap CLI', 'migration adapter kit'], requires: [], risk: 'critical' },
  { key: 'app-shell', kind: 'runtime host', owner: 'Forge', provides: ['shell slots', 'route contribution', 'layout', 'window manager', 'config and secrets', 'flags', 'i18n', 'native capability ports'], requires: ['identity', 'design-system', 'spec-builder'], risk: 'critical' },
  { key: 'data-layer', kind: 'runtime core', owner: 'Forge', provides: ['tenant context', 'repository and unit-of-work ports', 'event bus', 'jobs', 'files', 'search', 'audit', 'sync', 'email', 'idempotency', 'API conventions', 'pins @paperos/core types, filter, events'], requires: ['identity'], risk: 'critical' },
  { key: 'forge', kind: 'service', owner: 'Forge', provides: ['ForgePort (repos, trees, commits, PRs, mirror status)', 'webhook envelopes', 'bootstrap spec', 'CI runner artefact contract'], requires: ['identity', 'quality'], risk: 'medium' },
  { key: 'identity', kind: 'runtime core', owner: 'Forge (Sentinel reviews)', provides: ['Principal', 'auth', 'permission (can, explain, SQL predicate)', 'tenant and membership', 'audiences', 'impersonation ports'], requires: ['data-layer'], risk: 'critical' },
  { key: 'design-system', kind: 'runtime', owner: 'Iris', provides: ['component id registry with props schemas', 'DTCG token set', 'theme port', 'icon port', 'motion tokens', 'state component ids'], requires: [], risk: 'high' },
  { key: 'quality', kind: 'tooling', owner: 'Sentinel', provides: ['gate artefact schemas (gate1, security, visual, review, edge, conformance)', 'finding and severity taxonomy', 'gate runner port', 'RC manifest'], requires: ['forge', 'pm-linear'], risk: 'medium' },
  { key: 'pm-linear', kind: 'service + runtime', owner: 'Atlas', provides: ['issue contract and states', 'PM entities', 'PmSourcePort (list, claim, transition, comment)', 'queue port', 'webhook envelope'], requires: ['data-layer', 'tables', 'collab'], risk: 'high' },
  { key: 'agents', kind: 'tooling', owner: 'Atlas', provides: ['character schema', 'handoff artefact', 'session status', 'agent runtime port', 'budget port', 'prompt-log sink', 'skill manifest', 'MCP allowlist'], requires: ['identity', 'pm-linear', 'collab'], risk: 'medium' },
  { key: 'spec-builder', kind: 'tooling + runtime', owner: 'Quill', provides: ['PageSpec', 'AppSpec', 'validator port', 'generator plugin interface', 'flow graph', 'component refs'], requires: ['design-system', 'identity', 'data-layer', 'app-shell'], risk: 'high' },
  { key: 'collab', kind: 'runtime', owner: 'Nova (Quill consults)', provides: ['comment anchors and port', 'docs port', 'prompt-log port', 'changelog port', 'notification kinds and port', 'ADR record'], requires: ['data-layer', 'identity', 'realtime', 'design-system'], risk: 'medium' },
  { key: 'realtime', kind: 'runtime + service', owner: 'Nova', provides: ['collab doc rooms', 'presence', 'live records', 'reconciler and conflict events', 'push transport', 'window bus'], requires: ['data-layer', 'identity'], risk: 'high' },
  { key: 'input', kind: 'runtime', owner: 'Nova', provides: ['input event abstraction', 'command registry', 'keymap presets', 'focus', 'drag-and-drop sensors', 'voice routing'], requires: ['app-shell', 'design-system'], risk: 'low' },
  { key: 'tables', kind: 'runtime', owner: 'Nova', provides: ['ViewSpec', 'FieldDef', 'dataset registration', 'view query port', 'view renderer registry', 'field type plugin', 'formula and automation trigger ports'], requires: ['data-layer', 'identity', 'design-system', 'input'], risk: 'high' },
  { key: 'business-core', kind: 'runtime', owner: 'Ledger', provides: ['finance model', 'ledger port', 'posting rules', 'billing', 'payments', 'tax and payroll provider ports', 'document port', 'entitlements'], requires: ['data-layer', 'identity', 'tables'], risk: 'high' },
  { key: 'growth', kind: 'runtime', owner: 'Beacon', provides: ['CRM entities', 'social adapter', 'outreach provider', 'landing page publisher', 'attribution events', 'segment and support channel ports'], requires: ['tables', 'data-layer', 'business-core', 'collab', 'agents'], risk: 'medium' },
  { key: 'migration', kind: 'runtime', owner: 'Scout', provides: ['SourceConnector', 'mapping model', 'import run states', 'external id map', 'export archive v1', 'template pack schema'], requires: ['tables', 'data-layer', 'collab', 'business-core', 'pm-linear'], risk: 'low' },
  { key: 'libraries', kind: 'process', owner: 'Scout', provides: ['library record', 'rubric scores', 'ADR frontmatter', 'license policy', 'MCP connector record', 'Renovate groups'], requires: ['collab', 'quality'], risk: 'low' }
];
const findIssue = (pk, re) => (issues.find(i => i.p === pk && re.test(i.t)) || {}).id || null;
const modules = MODULES.map(m => {
  const contract = m.contract || `@paperos/contract-${m.key}`;
  const trio = m.key === 'module-system' ? null : {
    contract: findIssue(m.key, /^Publish @paperos\/contract-/), conformance: findIssue(m.key, /^Conformance test suite/), wire: findIssue(m.key, /^Wire .* behind the module registry/)
  };
  const dependents = MODULES.filter(x => x.requires.includes(m.key)).map(x => x.key);
  const linearOut = edges.filter(e => e.from === m.key).reduce((a, e) => a + e.n, 0), linearIn = edges.filter(e => e.to === m.key).reduce((a, e) => a + e.n, 0);
  return { ...m, contract, trio, dependents, linearOut, linearIn, short: shortName[m.key], phase: P[m.key] ? P[m.key].phase : 'P0', total: P[m.key] ? P[m.key].total : 0, color: P[m.key] ? P[m.key].color : '#0EA5E9', url: P[m.key] ? P[m.key].url : '' };
});
const kernelPieces = [
  { id: 'PAP-433', piece: 'Manifest schema and validator', serves: 'every module', behaviour: 'provides, requires with semver ranges, capabilities, slots, events, owner, swap risk on top of PAP-264; validated at boot and in CI.' },
  { id: 'PAP-434', piece: 'Registry and DI container', serves: 'every manifest', behaviour: 'createKernel() resolves requires topologically, refuses cycles and version conflicts; kernel.resolve(port) with singleton, request and transient scopes; two implementations bind side by side.' },
  { id: 'PAP-435', piece: 'Flag-driven swap', serves: 'PAP-366 flags', behaviour: 'module.<id>.impl variant flag read per request; flip in under 5 s per tenant or globally; shadow: true runs both and diffs the secondary.' },
  { id: 'PAP-436', piece: 'Event bus and schema registry', serves: 'PAP-303 envelope', behaviour: 'topics.json aggregated from every contract; defineUpcaster() for v1 readers during a window; dualPublish() during a swap; undeclared topics fail at boot.' },
  { id: 'PAP-437', piece: 'API gateway routing by contract', serves: 'PAP-267, PAP-268', behaviour: 'mountContract() routes by contract name to the bound implementation per request; X-PaperOS-Impl forces and echoes the implementation for canaries.' },
  { id: 'PAP-438', piece: 'UI slot and extension system', serves: 'contract-app-shell', behaviour: 'shell.nav, shell.sidebar, shell.inspector, shell.commandBar and eight more named slots with Zod props; modules fill them from their manifest; a new shell only exposes the same slot ids.' },
  { id: 'PAP-439', piece: 'Dependency lint and map', serves: 'rules R7 to R11', behaviour: 'no package imports another module\'s implementation; pnpm gen:dep-map writes the committed dependency-map.json Gate 1 checks; the Blueprint renders the same graph.' },
  { id: 'PAP-440', piece: 'Compatibility matrix', serves: 'every requires range', behaviour: 'CI job compat resolves requires against provides.version; cells ok, ahead (fails), behind (warns, then fails).' },
  { id: 'PAP-441', piece: 'Conformance runner and fixtures', serves: 'every contract', behaviour: 'defineConformanceSuite() parametrised by an implementation factory; golden fixtures are the shared truth for shadow-run diffs; conformance.json is a gate artefact.' },
  { id: 'PAP-442', piece: 'Swap CLI', serves: 'the playbook', behaviour: 'paperos module swap <id> --to <impl> walks propose, fork, conformance, shadow, canary, flip, remove and refuses a step whose gate is red.' },
  { id: 'PAP-443', piece: 'Migration adapter kit', serves: 'data shapes', behaviour: 'defineMigrationAdapter() covers event payloads, API responses, tables (expand-contract) and Yjs documents; generates the checklist the CLI enforces.' },
  { id: 'PAP-444', piece: 'Config and secrets port', serves: 'ConfigPort, SecretsPort', behaviour: 'manifests declare settingsSchema and secret names; the kernel validates config at boot and hands out secrets.get(); no module reads process.env.' },
  { id: 'PAP-445', piece: 'Module docs generator', serves: 'every manifest', behaviour: 'one page per module from manifest, contract exports, slots, events and owner.' },
  { id: 'PAP-446', piece: 'Shell swap drill', serves: 'the claim itself', behaviour: 'a deliberately minimal second shell provides contract-app-shell, passes conformance, is flipped for the demo tenant and rolled back with zero edits in module packages.' }
].map(k => ({ ...k, state: (byId[k.id] || {}).s || '', title: (byId[k.id] || {}).t || '', url: (byId[k.id] || {}).url || '' }));
const playbook = [
  { step: 'Propose', gate: 'ADR naming the contract version, swap risk and rollback; one Linear issue per step for critical risk.' },
  { step: 'Fork behind flag', gate: 'New package declares provides with impl v2; flag module.<id>.impl exists, default v1; CI builds both.' },
  { step: 'Pass conformance', gate: 'conformance.json green for v2 on every port and fixture; compatibility matrix unchanged or every consumer bumped.' },
  { step: 'Shadow-run', gate: 'shadow: true on staging for a nightly gate run; diff count under threshold; events dual-published.' },
  { step: 'Canary flip', gate: 'Flag rule for the demo tenant, then staff tenants, one release train each; Gate 3 screenshots carry X-PaperOS-Impl.' },
  { step: 'Flip default', gate: 'Flag default v2; v1 stays bound; 30-day deprecation window starts.' },
  { step: 'Remove', gate: 'Unbind v1, delete the package, knip clean, matrix regenerated, ADR superseded.' }
];

/* ---------------- $2,500 chunks ---------------- */
let chunks = null;
if (chunksRaw) {
  const slim = ch => ({
    n: ch.chunk, issues: ch.issues, count: ch.issueCount || ch.issues.length, listCost: ch.listCost, discountedCost: ch.discountedCost, hours: ch.hours, cumulativeHours: ch.cumulativeHours,
    start: ch.start, end: ch.end, firstIssueStart: ch.firstIssueStart, byPhase: ch.byPhase || {}, byType: ch.byType || {}, bySize: ch.bySize || {}, byBuilderModel: ch.byBuilderModel || {},
    byProject: Object.fromEntries(Object.entries(ch.byProject || {}).map(([k, v]) => [k, { n: (v.issues || []).length, umbrellas: v.umbrellasCompleted || [] }])),
    milestones: (ch.milestonesCompleted || []).map(m => ({ project: m.project, name: m.milestone, date: m.targetDate, issues: m.issues, excluded: m.deferredIssuesExcluded || 0, at: m.completedAt })),
    rcs: (ch.releaseCandidatesReached || []).map(r => ({ rc: r.rc, label: r.label, at: r.reviewAt, gates: r.gateIssues || [] })),
    nj: (ch.needsJustinBeforeStart || []).map(n => ({ id: n.id, text: n.text, status: n.status, mappedTo: n.mappedTo || [] }))
  });
  const mixes = {};
  for (const [k, m] of Object.entries(chunksRaw.mixes)) {
    const d = m.deferredChunk;
    mixes[k] = {
      description: m.description, builderModels: m.builderModels, reviewerModel: m.reviewerModel, qaModel: m.qaModel, totals: m.totals, chunks: m.chunks.map(slim),
      deferred: d ? { label: d.label, count: d.issueCount, listCost: d.listCost, discountedCost: d.discountedCost, equivalentChunks: d.equivalentChunks, start: d.start, end: d.end, hours: d.hours, issues: Object.values(d.byProject || {}).flatMap(v => v.issues || []), byProject: Object.fromEntries(Object.entries(d.byProject || {}).map(([k2, v]) => [k2, (v.issues || []).length])), byBuilderModel: d.byBuilderModel || {}, nj: d.needsJustinBeforeStart || [], note: d.effortNote || '' } : null
    };
  }
  chunks = { generatedAt: chunksRaw.generatedAt, snapshotTakenAt: chunksRaw.snapshotTakenAt, terms: chunksRaw.terms, recommended: chunksRaw.canonicalMix || 'B', round: chunksRaw.round || 3, counts: chunksRaw.counts || null, wallClock: chunksRaw.wallClock || null, round3: chunksRaw.round3 || null, mixes };
}

/* ---------------- round 4: initiatives, cycles, estimates, what changed ---------------- */
const INI_ORDER = ['A new app in ten minutes', 'The agent org runs the build', 'Product surfaces for every audience', 'Business-ready for any business', 'Operate, measure and comply'];
const INI_SHORT = { 'A new app in ten minutes': 'Golden path', 'The agent org runs the build': 'Agent org', 'Product surfaces for every audience': 'Product surfaces', 'Business-ready for any business': 'Business-ready', 'Operate, measure and comply': 'Operate & comply' };
const iniRank = n => { const k = INI_ORDER.findIndex(x => n.startsWith(x)); return k < 0 ? 99 : k; };
const initiatives = (snap.initiatives || []).slice().sort((a, b) => iniRank(a.name) - iniRank(b.name) || a.name.localeCompare(b.name)).map(x => {
  const keys = x.projects.map(p => p.key || (projects.find(q => q.name === p.name) || {}).key).filter(Boolean);
  const mine = canonical.filter(i => keys.includes(i.p));
  const byState = {}, ptsByState = {}; for (const i of mine) { const k = countKey(i); byState[k] = (byState[k] || 0) + 1; if (i.est) ptsByState[k] = (ptsByState[k] || 0) + i.est; }
  const points = mine.reduce((a, i) => a + (i.est || 0), 0), done = mine.filter(i => i.s === 'Done').reduce((a, i) => a + (i.est || 0), 0);
  return { id: x.id, name: x.name, short: INI_SHORT[INI_ORDER.find(k => x.name.startsWith(k))] || x.name, description: x.description || '', url: x.url, status: x.status, targetDate: x.targetDate, owner: x.owner,
    projects: keys, issues: mine.length, leaves: mine.filter(i => !i.ch.length).length, ready: mine.filter(i => i.s === 'Ready for Claude').length, deferred: mine.filter(i => i.d).length,
    newRound4: mine.filter(i => i.r4).length, points, pointsDone: done, progress: points ? done / points : 0, byState, ptsByState, r4: x.name.startsWith('Operate') };
});
const iniOfProject = {}; for (const x of initiatives) for (const k of x.projects) iniOfProject[k] = x.short;
for (const i of issues) i.ini = iniOfProject[i.p] || '';
const inWindow = (d, c) => d && d >= c.startsAt.slice(0, 10) && d < c.endsAt.slice(0, 10);
const cycles = (snap.cycles || []).slice().sort((a, b) => a.number - b.number).map(c => {
  const assigned = canonical.filter(i => i.cy === c.number), planned = canonical.filter(i => !i.d && !i.ch.length && inWindow(i.due, c));
  const byState = {}; for (const i of assigned) byState[countKey(i)] = (byState[countKey(i)] || 0) + 1;
  return { number: c.number, name: c.name, short: 'C' + c.number, description: c.description || '', startsAt: c.startsAt.slice(0, 10), endsAt: c.endsAt.slice(0, 10), active: !!c.active, progress: c.progress || 0,
    issues: assigned.length, points: assigned.reduce((a, i) => a + (i.est || 0), 0), byState, plannedIssues: planned.length, plannedPoints: planned.reduce((a, i) => a + (i.est || 0), 0),
    chunks: [...new Set(planned.map(i => i.chunk).filter(Boolean))].sort((a, b) => a - b) };
});
const noCycleLeaves = canonical.filter(i => !i.cy && !i.ch.length && !i.d);
const cyclesData = {
  settings: snap.teamSettings || null, list: cycles,
  noCycle: { issues: noCycleLeaves.length, points: noCycleLeaves.reduce((a, i) => a + (i.est || 0), 0) },
  deferred: { issues: canonical.filter(i => i.d && !i.ch.length).length, points: canonical.filter(i => i.d && !i.ch.length).reduce((a, i) => a + (i.est || 0), 0) },
  rule: 'Cycles hold in-flight work: the orchestrator moves an issue into the active cycle when a session claims it, and Linear rolls unfinished issues forward. Planned timing lives in due dates (the milestone target) and the Chunk labels ($2,500 chunk order), so an empty upcoming cycle is not an empty week.'
};
const histogram = {}; for (const i of canonical) if (!i.ch.length) histogram[i.est == null ? 'none' : i.est] = (histogram[i.est == null ? 'none' : i.est] || 0) + 1;
const estimates = {
  type: (snap.teamSettings || {}).issueEstimationType || 'fibonacci', sizeMap: { S: 2, M: 3, L: 5 }, histogram,
  perProject: projects.map(p => ({ key: p.key, short: p.short, color: p.color, phase: p.phase, total: p.points, byState: p.pointsByState, issues: p.total, estimated: p.estimated })),
  totals: { points: totals.points, done: totals.pointsDone, estimated: totals.estimated, unestimatedLeaves: totals.unestimatedLeaves, ready: canonical.filter(i => i.s === 'Ready for Claude').reduce((a, i) => a + (i.est || 0), 0), deferred: canonical.filter(i => i.d).reduce((a, i) => a + (i.est || 0), 0) },
  byDue: (() => { const m = {}; for (const i of canonical) if (i.due && !i.ch.length) m[i.due] = (m[i.due] || 0) + (i.est || 0); return Object.entries(m).sort((a, b) => a[0].localeCompare(b[0])).map(([date, pts]) => ({ date, pts })); })(),
  burnup: { start: '2026-09-18', today: TODAY, deadline: DEADLINE, points: [{ date: TODAY, scope: totals.points, done: totals.pointsDone }], note: 'Done points read from the snapshot: 0 today. The line fills in as merges land; the plan line is the cumulative points due by date.' }
};
const num = (re, src, fb) => { const m = re.exec(src || ''); return m ? Number(m[1]) : fb; };
const r4Before = { issues: num(/\((\d+) before round 4/, verifyMd, 493), projects: 18, relations: num(/Existing blocks edges:\s*(\d+)/, mergeReport, 1224), initiatives: 0, cycles: 0, estimated: 0 };
const featureRows = [...(featuresMd.split('## Initiatives')[0] || '').matchAll(/^\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*$/gm)].map(m => ({ feature: m[1], used: m[2], since: m[3], how: m[4] })).filter(r => r.feature !== 'Feature' && !/^-+$/.test(r.feature));
const topGaps = [
  { area: 'Tenant AI assistant', gap: 'Nobody could talk to the product: no grounded chat, copilot, cited answers or audited actions for tenants, staff or customers.', fix: 'New project Tenant AI Assistant & Business Agents (`assistant`): model and ModelProviderPort spec, retrieval and chat panel, actions with confirmation, business characters.', projects: ['assistant'] },
  { area: 'Workflows and approvals', gap: 'Processes stopped at one table: automations were single-table reactions and five issues each hand-rolled an approval step; no task inbox.', fix: 'New project Workflows, Approvals, Forms, Documents & E-Signature (`workflows`): workflow model, run engine, approvals framework, task inbox, step catalogue.', projects: ['workflows'] },
  { area: 'Forms, documents, signatures', gap: 'A single-page form view and a Webflow embed cannot run intake or paid forms; document generation existed only for invoices; nothing signed anything.', fix: 'Form builder, document templates and e-signature issues in `workflows`, most deferred to v0.2 at priority 4.', projects: ['workflows'] },
  { area: 'Customer engagement', gap: 'Growth acquired the customer and then forgot them: no booking, two-way messaging, help center, NPS, reviews, memberships or loyalty.', fix: 'New project Scheduling, Messaging & Customer Engagement (`engagement`): booking engine first, the rest specified as v0.2.', projects: ['engagement', 'growth'] },
  { area: 'Commerce and operations', gap: 'Finance had no operations under it: products, stock, orders, POS, purchasing, projects and time, shifts, assets, marketplaces were absent, so eleven business types in the brief had no pack.', fix: 'New project Commerce, Operations & Vertical Packs (`commerce`): catalog and inventory live, the operations packs deferred.', projects: ['commerce', 'business-core'] },
  { area: 'Platform operations', gap: 'PaperOS had no console for PaperOS: no tenant list, overrides, per-tenant flag rules, DLQ, health scores, status page or incident comms; compliance controls implemented but unmapped to SOC 2, GDPR or HIPAA.', fix: 'New project Platform Operations, Analytics & Compliance (`platform-ops`): super-admin console, status page and control mapping live; analytics, experiments and evidence deferred.', projects: ['platform-ops'] },
  { area: 'Data layer', gap: 'No generic entity path: every module would re-implement CRUD, cursors, audit and events; migrations were guarded but never rehearsed; local-first had no lost-device story.', fix: '`defineEntity()`, migration safety lint and dry run, cache wipe on sign-out, per-PR databases, tenant sequences; four umbrella-sized M issues split.', projects: ['data-layer'] },
  { area: 'Identity', gap: 'Authorization stopped at roles and rows: no custom roles, no sharing one record or link, no field permissions; three consumers assumed a `permission.changed` signal nobody emitted.', fix: 'Custom roles, resource grants, field permissions and permission propagation; delegated authority for agents acting for people; device-flow login.', projects: ['identity'] },
  { area: 'Tables and views', gap: 'The `records.*` write path for custom datasets was referenced by five specs and owned by none; no `registerViewKind` or `ViewHost`; every DoD pointed at demo pages and a 100k-row seed nobody built.', fix: 'Records write path (P1, Opus 5), view renderer registry, demo pages and seed, export, conditional formatting, system fields; four M issues split into eight children.', projects: ['tables'] },
  { area: 'Quality and forge', gap: 'Eleven gate DoDs rehearsed against a sandbox repo and seeded defects no issue created; nothing re-queued a builder after a review block; nothing merged anything (no merge queue) and nothing created worktrees on PR branches for the branch-start rule.', fix: 'Gate sandbox and defect catalogue (P0 Infra), review fix loop, migration gate, merge automation, dependent branches, forge cleanup.', projects: ['quality', 'forge'] },
  { area: 'Agent org and pipeline', gap: 'Three P0 security issues each hid two sessions of work; consumers assumed per-character Linear bot users that do not exist; cold sessions read about 150 KB of documents; the workspace used none of Linear\'s planning features.', fix: 'Security issues split, character identity decision (one Needs Justin card), context packs under 8k tokens, plugin packaging, session-end guard hooks; estimates, cycles, triage, templates and views turned on from a workspace-as-code script.', projects: ['agents', 'pm-linear'] },
  { area: 'Small shared engines', gap: 'Recurrence (five consumers), FX conversion, file scanning and previews, SMS channel, labels and barcodes, geocoding, scheduled report delivery, settings registry, OAuth apps and bank reconciliation were owned by nobody.', fix: 'Twelve cross-project suggestions filed into data-layer, collab, business-core, tables, design-system, app-shell, identity and growth (see `plan/round4/digest/cross-cutting.md`).', projects: ['data-layer', 'collab', 'business-core', 'tables', 'design-system', 'app-shell', 'identity', 'growth'] }
];
const round4 = {
  date: '2026-09-18', before: r4Before,
  after: { issues: totals.issues, canonical: totals.canonical, projects: projects.length, relations, initiatives: initiatives.length, cycles: cycles.length, estimated: totals.estimated, points: totals.points, views: (snap.views || []).length, templates: (snap.templates || []).length, documents: (snap.documents || []).length, updates: (snap.projectUpdates || []).length, links: projects.reduce((a, p) => a + p.links.length, 0), triage: totals.triage },
  newIssues: totals.newRound4, newLeaves: canonical.filter(i => i.r4 && !i.ch.length).length, newChildren: canonical.filter(i => i.r4 && i.par).length, newDeferred: canonical.filter(i => i.r4 && i.d).length,
  newProjects: projects.filter(p => p.isNew).map(p => p.key), amendments: num(/Amendments:\s*(\d+)/, mergeReport, 143), suggestions: num(/Cross-project suggestions:\s*(\d+)/, mergeReport, 93),
  newRelations: relations - r4Before.relations, digestFiles: 18,
  projects: projects.map(p => ({ key: p.key, short: p.short, name: p.name, isNew: p.isNew, total: p.total, r4New: p.r4New, r4Children: p.r4Children, r4Deferred: p.r4Deferred, points: p.points, url: p.url, ini: iniOfProject[p.key] || '' })),
  gaps: topGaps, features: featureRows,
  docs: [
    { title: 'Per-project digests', path: 'plan/round4/digest/', url: `${REPO}/tree/main/plan/round4/digest` }, { title: 'Cross-cutting analysis', path: 'plan/round4/digest/cross-cutting.md', url: `${REPO}/blob/main/plan/round4/digest/cross-cutting.md` },
    { title: 'Merge report', path: 'plan/round4/merge-report.md', url: `${REPO}/blob/main/plan/round4/merge-report.md` }, { title: 'Linear team features', path: 'plan/round4/linear-team-features.md', url: `${REPO}/blob/main/plan/round4/linear-team-features.md` },
    { title: 'Linear features used by PaperOS', path: 'docs/linear-features.md', url: `${REPO}/blob/main/docs/linear-features.md` }, { title: 'Snapshot summary', path: 'plan/round4/snapshot-summary.md', url: `${REPO}/blob/main/plan/round4/snapshot-summary.md` }
  ],
  views: (snap.views || []).map(v => ({ name: v.name, url: v.url })).filter(v => v.url),
  triageView: ((snap.views || []).find(v => /triage inbox/i.test(v.name)) || {}).url || 'https://linear.app/paperos/team/PAP/triage',
  njView: ((snap.views || []).find(v => /^needs justin$/i.test(v.name)) || {}).url || 'https://linear.app/paperos/team/PAP/all'
};

/* ---------------- hand-written content ---------------- */
const lede = 'PaperOS Core Platform is the reusable foundation every future PaperOS app is generated from: one spec-driven TypeScript monorepo that ships to web, desktop and mobile with the data layer, design system, multiplayer, tables, identity and business plumbing already wired. Since round 3 every project is a <b>module behind a versioned contract</b>, plugged into a thin kernel so that the shell, or anything else, can be rewritten and everything reconnects. It is built and reviewed by <b>nine Claude agent characters</b> working from Linear behind four automated quality gates, around the clock, in <b>$2,500 chunks that cost Justin $50 each</b>. Round 4 (18 September) benchmarked every project against the best products in its category, added <b>five projects</b> for what no module owned and turned on Linear\'s estimates, cycles, initiatives and triage.';
const meta = [
  `<a href="https://linear.app/paperos/team/PAP/all">Linear team PAP</a>`, `<a href="${REPO}">imagine-os/linear-builder</a>`, `<a href="${PAGES}previous/index-v4.html">previous version of this page</a>`,
  `${projects.length} projects`, `${totals.issues} issues`, `${totals.points.toLocaleString('en-US')} points`, `${relations} blocking relations`, `${totals.milestones} milestones`, `${initiatives.length} initiatives`, chunks ? `$${Math.round(chunks.mixes.B.totals.discountedCost)} to Justin at the discount` : '$10,000 credits'
];
const nj = [
  { id: 'NJ-1', when: 'Sep 17 12:50Z', done: true, show: true, text: 'Linear: upgrade the workspace plan so the remaining specified issues can be created (PAP-91).', resolved: 'Justin upgraded to Basic; all 153 pending issues were created as PAP-280 to PAP-432 and PAP-91 is back in Ready for Claude.' },
  { id: 'NJ-2', when: 'chunk 1', show: true, text: 'Infra credential batch on PAP-25: Hetzner account, registrar or Cloudflare token, Resend, sops recovery key. Every infra issue waits on these.' },
  { id: 'NJ-3', when: 'chunk 1', show: true, text: 'GitHub App on the imagine-os org with repo and workflow scope (PAP-47).' },
  { id: 'NJ-4', when: 'chunk 2', show: true, text: 'Anthropic Console: orchestrator API key, hard spend limit, usage export (PAP-98).' },
  { id: 'NJ-5', when: 'chunk 1', show: true, text: 'Linear: orchestrator API key and webhook signing secret (PAP-92, PAP-97).' },
  { id: 'NJ-6', when: 'chunk 1', show: true, text: 'Code signing (PAP-256): Apple Developer Program and Windows signing, or accept unsigned v0.1.0 installers. Default after 48 h: unsigned.' },
  { id: 'NJ-7', when: 'chunk 1', text: 'Licence of the template code (PAP-211); default Apache-2.0.' },
  { id: 'NJ-8', when: 'chunk 1', text: 'Approve the Justin queue format (PAP-94) and the issue contract (PAP-93).' },
  { id: 'NJ-9', when: 'chunk 1', text: 'Hire the roster (PAP-104, PAP-210). RC0.' },
  { id: 'NJ-10', when: 'chunk 1', text: 'Stripe test-mode account (PAP-177); Google OAuth consent screen (PAP-224, PAP-200).' },
  { id: 'NJ-11', when: 'chunk 2', text: 'Domain: set PAPEROS_DOMAIN or keep sslip.io for v0.1.0. RC1.' },
  { id: 'NJ-12', when: 'chunk 1', text: 'Payroll provider (PAP-176): Check sandbox (default) or Gusto Embedded.' },
  { id: 'NJ-13', when: 'chunk 3', text: 'Airtable demo base and token (PAP-202); Slack incoming webhook (PAP-136).' },
  { id: 'NJ-14', when: 'after RC3', text: 'Stop-loss checkpoint: go or no-go on the deferred stretch pool (the optional final chunk).' },
  { id: 'NJ-15', when: 'chunk 3', text: 'Release candidate v0.1.0-rc.2 (PAP-254): /approve or /reject. RC2.' },
  { id: 'NJ-16', when: 'chunk 3', text: 'Approve the content agent (PAP-192) and migration agent (PAP-208).' },
  { id: 'NJ-17', when: 'chunk 4', text: 'Accessibility statement wording (PAP-160).' },
  { id: 'NJ-18', when: 'chunk 3', text: 'Industry list and terminology defaults (PAP-126).' },
  { id: 'NJ-19', when: 'chunk 4', text: 'Scope freeze: the deferred list becomes milestone v0.2.' },
  { id: 'NJ-20', when: 'chunk 4', text: 'Release candidate v0.1.0: /approve promotes and tags. RC3.' },
  { id: 'NJ-21', when: 'chunk 4', text: 'PAP-5: close or keep as scoreboard (PAP-95 vs PAP-29).' },
  { id: 'NJ-22', when: 'before a critical swap', text: 'Any breaking change to a critical module\'s contract (app-shell, data-layer, identity, kernel) is a Needs Justin card with the ADR and the affected-consumer list.' }
];
const docs = [
  { key: 'blueprint', title: 'Blueprint', line: 'Vision, the sixteen decisions, phases, budget and the project index. This page is its visual form.', linear: 'https://linear.app/paperos/document/paperos-core-platform-blueprint-0c2115fe48f1', github: `${REPO}/blob/main/docs/blueprint.md` },
  { key: 'contracts', title: 'Interface & Data Contracts', line: 'The shapes every project codes against (ids, tenancy, Principal, Money, FilterTree, events) and the module map. Changing one needs an ADR.', linear: 'https://linear.app/paperos/document/paperos-interface-and-data-contracts-d40e6a4d227c', github: `${REPO}/blob/main/docs/interface-and-data-contracts.md` },
  { key: 'modules', title: 'Module System', line: 'How the shell or any module gets rewritten without touching the rest: manifests, contract packages, the kernel, conformance suites and the seven-step swap playbook.', linear: 'https://linear.app/paperos/document/paperos-module-system-8007373cc6bb', github: `${REPO}/blob/main/docs/module-system.md` },
  { key: 'project-contracts', title: 'Project Contract sections', line: 'Each Linear project carries what it provides to and consumes from the others.', linear: 'https://linear.app/paperos/team/PAP/projects', github: '' },
  { key: 'roster', title: 'Agent Roster', line: 'The org chart, the routing rules that decide who picks up an issue, and links to every character sheet.', linear: 'https://linear.app/paperos/document/paperos-agent-roster-org-chart-and-character-index-fc7ea7f41ff3', github: `${REPO}/blob/main/docs/agent-roster.md` },
  { key: 'security', title: 'Security & Threat Model', line: 'Assets, trust boundaries, the Linear deny list and which issue owns each control.', linear: 'https://linear.app/paperos/document/paperos-security-and-threat-model-51fd5fd8929c', github: `${REPO}/blob/main/docs/security-and-threat-model.md` },
  { key: 'schedule', title: 'Execution Schedule', line: 'Day by day to 1 October, now with the discounted terms and the $2,500 chunks: starts, capacity, the Needs Justin table, credit burn and stop-loss rules.', linear: 'https://linear.app/paperos/document/paperos-execution-schedule-1fa3d38d6795', github: `${REPO}/blob/main/docs/execution-schedule.md` },
  { key: 'chunks', title: 'Build in $2,500 chunks', line: 'The two model mixes, four chunks at $50 each, what each chunk delivers and which Needs Justin answers it needs first.', linear: '', github: `${REPO}/blob/main/docs/build-chunks.md` },
  { key: 'estimate', title: 'Cost & Duration Estimate', line: 'The token model, prices and scheduler the chunk plan reuses; scenarios A to E.', linear: '', github: `${REPO}/blob/main/docs/cost-and-duration-estimate.md` },
  { key: 'golden', title: 'New App in Ten Minutes', line: 'The golden path the whole platform serves: one command, one paragraph, a deployed multi-device app.', linear: '', github: `${REPO}/blob/main/docs/new-app-in-ten-minutes.md` }
];
const risks = [
  { title: 'P0 is serial: scaffold, local stack, Drizzle, entities, RLS, API, auth, Yjs cannot run in parallel.', body: 'The 24/7 chunk schedule respects the same blockedBy graph; its 37 hours assume the branch-start rule (start against a blocker\'s open PR). If sessions wait for merges instead, chunk 1 alone stretches past a day and every later chunk slides with it.' },
  { title: 'Human account setup is on the critical path.', body: 'Hetzner, a domain or Cloudflare, Resend, the Apple developer program, Stripe test keys, a payroll sandbox. Nine Needs Justin items gate chunk 1 (NJ-2, 3, 5, 6, 7, 8, 9, 10, 12); answer them before the first session starts or every infra issue waits. Issues whose credential is late start in sandbox or dry-run mode.' },
  { title: 'Contracts are frozen at v0.1 before any implementation exists.', body: 'The 17 Publish-contract issues land in P0 and P1 while the modules they describe are still being built. Pre-1.0 semver treats minor as breaking, so a wrong port shape costs an ADR and a consumer bump rather than a quiet edit. Keep contract packages small (50 KB cap, lint R9) and expect two or three v0.2 bumps before RC2.' },
  { title: 'The orchestrator and the Coolify host hold every credential.', body: 'A compromised session prompt or leaked token there is a total compromise. Tool scopes, security scans and the destructive-action deny list are the mitigations; they must not slip to P1. The kernel\'s secrets port (PAP-444) is what stops modules from reading process.env directly.' },
  { title: 'Automated review replaces human review, but nobody has calibrated it yet.', body: 'Every reviewer session runs on Fable 5.1 at high effort in both chunk mixes. Until the eval harness produces a false-negative rate, treat RC0 and RC1 as smoke tests and spot-check five Gate 2 verdicts in chunk 1.' },
  { title: 'P2 carries the business layer, growth, migration and hardening, plus the shell swap drill.', body: 'Stripe Connect, ledger, payroll adapter, CRM, social scheduler and importers are each large, and PAP-446 must prove the swap claim before RC3. Decide now what the release candidate must contain (suggested: template, spec builder, tables, collaboration, identity, billing, kernel) and let the rest land after the deadline.' },
  { title: 'The chunk clock is session time, not calendar time.', body: '37 hours at 16 builders assumes every Needs Justin answer is in hand, no merge-queue conflicts and no re-review bounce minutes. The tokens for retries sit in the x1.25 contingency; the minutes do not. Re-baseline after chunk 1 with real per-size token burn.' },
  { title: 'Linear\'s issue cap shaped the plan once and can again.', body: 'The Basic plan now holds 493 issues. If the cap returns, umbrella parents run as single large sessions using their children\'s specs inline, which means coarser sessions and a thinner Ready queue, not lost scope.' }
];
const decisions = plan.decisions.map(d => ({ title: d.title, decision: d.decision, why: d.why }));
if (!decisions.some(d => /module/i.test(d.title))) decisions.push({
  title: 'Modules: every project is a swappable module behind a versioned contract, wired through a thin kernel',
  decision: 'Each of the seventeen projects becomes a module with a manifest (provides, requires with semver ranges, slots, events, owner, swap risk) and a contract package `@paperos/contract-<module>` holding only types, schemas, topics, route signatures, slot definitions and port interfaces. Modules depend on contracts, never on each other\'s internals (lint R7 to R11). `@paperos/kernel` (PAP-433 to PAP-446) is the only middle tooling a cross-module dependency may live in: registry and DI, flag-driven swaps with shadow-run, event schema registry, gateway routing by contract, UI slots, conformance runner, swap CLI and migration adapter kit. Rewriting the shell means providing `contract-app-shell` again and running the seven-step playbook; the shell swap drill proves it before 1 October.',
  why: 'Justin asked that rewriting the shell later, or anything else, leaves the rest plug and play with dependencies visible in one place. Contracts plus a kernel make a swap a search of five places instead of the whole repo, and the Linear blocks graph, the committed dependency map and this page render the same graph.'
});

/* ---------------- model and effort matrix from live labels ---------------- */
const meRows = [['Fable 5.1', 'Fable 5.1'], ['Opus 5', 'Opus 5'], ['Sonnet 5', 'Sonnet 5'], ['Haiku 4.5', 'Haiku 4.5']];
const leaves = canonical.filter(i => !i.ch.length);
const rows = meRows.map(([k, label]) => { const r = { label }; let tot = 0; for (const e of ['low', 'medium', 'high', 'max']) { r[e] = leaves.filter(i => i.m === k && i.e === e).length; tot += r[e]; } r.total = tot; return r; }).filter(r => r.total);
const assigned = rows.reduce((a, r) => a + r.total, 0);
const modelEffort = {
  rows, assigned, umbrellas: canonical.filter(i => i.ch.length).length, effs: ['low', 'medium', 'high', 'max'],
  note: `Live Linear labels on the ${assigned} leaf issues (${TODAY} snapshot): Model and Effort labels follow scenario E of the cost estimate, Fable 5.1 on the keystone specs, Opus 5 on the scaffold, orchestrator, security and P0 core, Sonnet 5 elsewhere, plus the round-3 module issues and the round-4 gap issues (Sonnet 5 or Opus 5, mostly high). The round-4 chunk plan below (plan/round4/chunks-v2.json) prices two mixes on top of these labels over the ${chunks ? chunks.mixes.B.totals.issues : 601} scheduled leaves: <b>mix B</b> runs the labelled builder models with Fable 5.1 on every spec, research, review and release candidate (${chunks ? '$' + Math.round(chunks.mixes.B.totals.listCost).toLocaleString('en-US') : '$10,450'} list, <b>${chunks ? '$' + Math.round(chunks.mixes.B.totals.discountedCost) : '$209'} to Justin</b>, ${chunks ? chunks.mixes.B.totals.chunks : 5} chunks, ${chunks ? chunks.mixes.B.totals.wallClockHours : 38.6} h at 16 builders); mix A runs Fable 5.1 everywhere (${chunks ? '$' + Math.round(chunks.mixes.A.totals.listCost).toLocaleString('en-US') : '$18,522'} list, ${chunks ? '$' + Math.round(chunks.mixes.A.totals.discountedCost) : '$370'}, ${chunks ? chunks.mixes.A.totals.chunks : 8} chunks). The deferred v0.2 set is an extra ${chunks && chunks.mixes.B.deferred ? '$' + Math.round(chunks.mixes.B.deferred.listCost).toLocaleString('en-US') + ' list, $' + Math.round(chunks.mixes.B.deferred.discountedCost) : '$3,418 list, $68'} in mix B. Round 3 priced 326 issues at $7,909 / $158 in 4 chunks.${me ? '' : ''}`
};

const footer = `<span>Built from <span class="mono">plan/linear-snapshot-live.json</span> taken ${snap.takenAt} by <span class="mono">tools/blueprint/build_v5.js</span>.</span><span>Linear is the system of record; where this page and an issue disagree, the issue wins.</span><span><a href="${PAGES}previous/index-v4.html">Previous version</a> · <a href="${REPO}">Source</a> · <a href="https://github.com/imagine-os/graph-gallery">Visual ideas: graph-gallery</a></span>`;

const data = {
  takenAt: snap.takenAt, today: TODAY, deadline: DEADLINE, daysLeft, phaseNow: phaseNow.key, lede, meta, totals, phases, projects, edges,
  topEdges: edges.slice(0, 3), critical: { days: critical.days, ids: critical.path, projects: critProjects }, milestonesFlat,
  issues: issues.map(({ _blocks, _blockedBy, ...i }) => i), agents: plan.agents, budget: plan.budget, decisions, modelEffort, nj, docs, risks, footer,
  modules, kernelPieces, playbook, chunks, pages: PAGES, repo: REPO,
  initiatives, cycles: cyclesData, estimates, round4, teamSettings: snap.teamSettings || null
};

/* ---------------- render ---------------- */
archSvg = archSvg.replace(/267 issues · 534 blocking relations/, `${totals.issues} issues · ${relations} blocking relations`).replace(/class="fig"/, 'class="fig arch-fig"');
const json = JSON.stringify(data).replace(/<\/script/gi, '<\\/script').replace(/<!--/g, '<\\!--');
const CDN_TAG = '<script src="https://cdn.jsdelivr.net/npm/3d-force-graph@1.80.0/dist/3d-force-graph.min.js" async onload="window.__fg3dLoaded=true" onerror="window.__fg3dFailed=true"></script>';
const js = [v4('views.js'), v4('modules.js'), v4('chunks.js'), v4('round4.js')].join('\n');
const css = v4('views.css') + '\n' + v4('round4.css');
function render(mode) {
  return template.replace('__ARCH_SVG__', () => archSvg).replace('__DATA__', () => json).replace('__V4_CSS__', () => css).replace('__V4_JS__', () => js)
    .replace('__CDN__', () => mode === 'pages' ? CDN_TAG : '').replace('__MODE__', mode);
}
const body = render('pages');
const doc = `<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n</head>\n<body>\n${body}\n</body>\n</html>\n`;

const siteDir = path.join(ROOT, 'site');
fs.mkdirSync(siteDir, { recursive: true });
fs.writeFileSync(path.join(siteDir, 'index.html'), doc);
fs.writeFileSync(path.join(siteDir, 'data.json'), JSON.stringify(data, null, 1));
if (process.env.PAPEROS_ARTIFACT_OUT) fs.writeFileSync(process.env.PAPEROS_ARTIFACT_OUT, render('artifact'));
console.log(`issues ${totals.issues} · canonical ${totals.canonical} · points ${totals.points} · new in round 4 ${totals.newRound4} · triage ${totals.triage} · initiatives ${initiatives.length} · cycles ${cycles.length} · projects ${projects.length} (${round4.newProjects.length} new) · features ${featureRows.length} · ready ${totals.ready} · deferred ${totals.deferred} · relations ${relations} · edges ${edges.length} · milestones ${totals.milestones} · modules ${modules.length} (trios resolved: ${modules.filter(m => m.trio && m.trio.contract && m.trio.conformance && m.trio.wire).length}) · chunks ${chunks ? Object.keys(chunks.mixes).join('/') : 'none'} · critical ${critical.path.length} issues / ${critical.days} days · html ${(doc.length / 1024).toFixed(0)} KB`);
