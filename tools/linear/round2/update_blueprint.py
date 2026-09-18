#!/usr/bin/env python3
import os
"""Round-2 in-place update of blueprint.html: refreshed numbers, Round 2 section,
interface map, day-by-day schedule, regenerated timeline, index and ready list."""
import json, re, html, sys
from collections import Counter, defaultdict

BASE = os.environ.get("PAPEROS_PLAN_DIR", ".") + ""
HTML = BASE + "/blueprint.html"
snap = json.load(open(BASE + "/round2/linear-snapshot-3.json"))
plan = json.load(open(BASE + "/plan.json"))
lin = json.load(open(BASE + "/linear-ids.json"))
doc = open(HTML, encoding="utf-8").read()
orig_len = len(doc)
esc = lambda s: html.escape(str(s), quote=True)

ART = "https://claude.ai/artifact/RhSgtKN7k64GnVmKFrxf8h"
TAKEN = snap["takenAt"]

# ---------------------------------------------------------------- data
issues = [i for i in snap["issues"] if int(i["identifier"].split("-")[1]) >= 13]
by_id = {i["identifier"]: i for i in issues}
nums = lambda k: int(k.split("-")[1])
states = Counter(i["state"] for i in issues)
n_issues = len(issues)
n_ready = states.get("Ready for Claude", 0)
n_nj = states.get("Needs Justin", 0)
n_children = sum(1 for i in issues if i["parent"])
n_parents = len({i["parent"] for i in issues if i["parent"]})
n_blocks = sum(1 for i in issues for r in i["relations"] if r["type"] == "blocks")
n_deferred = sum(1 for i in issues if "Deferred" in i["labels"])
n_docs = len(snap["documents"])
n_milestones = sum(len(p["milestones"]) for p in snap["projects"])
n_pending = 156  # FIX-6 verification: pendingEntries after dedupe
phase_counts = Counter(l for i in issues for l in i["labels"] if l in ("P0", "P1", "P2"))
type_labels = {"Research", "Spec", "Build", "Review", "Infra", "Docs"}
TYPE_CLS = {"Build": "build", "Research": "research", "Spec": "spec", "Review": "review", "Infra": "infra", "Docs": "docs"}

proj_by_name = {p["name"]: p for p in snap["projects"]}
key_by_name = {v["name"]: k for k, v in lin["projects"].items()}
plan_proj = {p["key"]: p for p in plan["projects"]}
phase_order = {"P0": 0, "P1": 1, "P2": 2}
plan_order = [p["key"] for p in plan["projects"]]
proj_keys = sorted(plan_order, key=lambda k: (phase_order[plan_proj[k]["phase"]], plan_order.index(k)))
short_name = {
    'app-shell': 'App shell & template', 'data-layer': 'Data layer', 'forge': 'Forge independence', 'identity': 'Identity & audiences',
    'design-system': 'Design system', 'quality': 'Quality pipeline', 'pm-linear': 'PM & Claude pipeline', 'agents': 'Agent characters',
    'spec-builder': 'Spec builder', 'collab': 'Collaboration & knowledge', 'realtime': 'Multiplayer & realtime', 'input': 'Multi-input & a11y',
    'tables': 'Table & views engine', 'business-core': 'Business core', 'growth': 'Growth & CRM', 'migration': 'Migration & import', 'libraries': 'Library discovery'
}
docs_by_title = {d["title"]: d for d in snap["documents"]}
def docurl(frag):
    for d in snap["documents"]:
        if frag in d["url"]:
            return d["url"]
    raise KeyError(frag)
D = {
    "blueprint": docurl("core-platform-blueprint"),
    "contracts": docurl("interface-and-data-contracts"),
    "threat": docurl("security-and-threat-model"),
    "schedule": docurl("execution-schedule"),
    "roster": docurl("agent-roster"),
    "golden": docurl("ten-minutes"),
}
char_sheets = {d["title"].split(":")[1].split("—")[0].strip(): d["url"] for d in snap["documents"] if d["title"].startswith("Character sheet")}
pending_docs = sorted([d for d in snap["documents"] if d["title"].startswith("Round 2 pending")], key=lambda d: -int(re.search(r"\((\d+)\)", d["title"]).group(1)))

print(f"issues {n_issues} ready {n_ready} nj {n_nj} children {n_children}/{n_parents} blocks {n_blocks} deferred {n_deferred} docs {n_docs} milestones {n_milestones}", file=sys.stderr)

# ---------------------------------------------------------------- helpers
def sub1(pattern, repl, text, flags=0, name=""):
    new, n = re.subn(pattern, repl, text, count=1, flags=flags)
    if n != 1:
        raise SystemExit(f"pattern not found: {name or pattern[:60]}")
    return new

def replace_literal(old, new, text, name=""):
    if old not in text:
        raise SystemExit(f"literal not found: {name or old[:60]}")
    return text.replace(old, new, 1)

# ---------------------------------------------------------------- 0. CSS additions
css_add = """
/* round 2 additions */
.issues li.group{display:grid;gap:0;padding:0;border-top:0}
.issues li.group>.row{padding:5px 0;border-top:1px solid var(--line);display:grid;gap:3px}
.issues .kids{margin:0;padding:0;list-style:none}
.issues .kids li{margin-left:18px;border-top:1px dashed var(--line);font-size:12.5px}
.issues .kids .id{color:var(--ink-2)}
.issues .kids li a{grid-template-columns:62px 1fr}
.nj{font-size:10.5px;padding:0 6px;border-radius:3px;background:var(--justin-soft);color:var(--justin);font-weight:600}
.def{font-size:10.5px;padding:0 6px;border-radius:3px;border:1px dashed var(--line);color:var(--ink-2)}
.kid-n{font-size:10.5px;color:var(--ink-2)}
.issues .row[data-ready="true"]{background:linear-gradient(90deg,var(--ready-soft),transparent 55%);border-radius:4px}
.issues li[data-state="Needs Justin"]{background:linear-gradient(90deg,var(--justin-soft),transparent 55%);border-radius:4px}
.facts{width:100%;border-collapse:collapse;font-size:13.5px;margin-top:18px}
.facts th,.facts td{text-align:left;padding:7px 10px;border-top:1px solid var(--line);vertical-align:top}
.facts th{font-family:var(--mono);font-size:11px;letter-spacing:.06em;text-transform:uppercase;color:var(--ink-2);font-weight:500;border-top:0}
.facts td.n{font-family:var(--mono);font-variant-numeric:tabular-nums;white-space:nowrap}
.facts td.up{color:var(--accent);font-weight:600}
.facts .bar{display:inline-block;height:8px;border-radius:2px;background:var(--accent);opacity:.35;vertical-align:middle;margin-right:6px}
.facts .bar.after{opacity:1}
.tablewrap{overflow-x:auto;background:var(--card);border:1px solid var(--line);border-radius:10px;padding:6px 14px 12px}
.two{display:grid;grid-template-columns:1fr 1fr;gap:22px;margin-top:22px;align-items:start}
.doclist{margin:0;padding:0;list-style:none;display:grid;gap:10px;font-size:14px}
.doclist li{display:grid;grid-template-columns:22px 1fr;gap:10px;align-items:baseline}
.doclist li b{display:block}.doclist li span{color:var(--ink-2);font-size:13px}
.doclist .t-mono{font-size:12px;color:var(--accent)}
.fixes{margin:0;padding:0;list-style:none;display:grid;gap:8px;font-size:13.5px;counter-reset:f}
.fixes li{display:grid;grid-template-columns:52px 1fr;gap:10px;align-items:baseline}
.fixes li::before{counter-increment:f;content:"FIX-" counter(f);font-family:var(--mono);font-size:11px;color:var(--accent);font-weight:600}
.fixes b{font-weight:600}.fixes span{color:var(--ink-2)}
.sched{width:100%;border-collapse:collapse;font-size:13px}
.sched th,.sched td{text-align:left;padding:7px 8px;border-top:1px solid var(--line);vertical-align:top}
.sched th{font-family:var(--mono);font-size:11px;letter-spacing:.06em;text-transform:uppercase;color:var(--ink-2);font-weight:500;border-top:0}
.sched td.d{font-family:var(--mono);white-space:nowrap;font-variant-numeric:tabular-nums}
.sched td.pk{white-space:nowrap;font-family:var(--mono);font-variant-numeric:tabular-nums}
.sched .pkbar{display:inline-block;height:9px;border-radius:2px;background:var(--accent);vertical-align:middle;margin-right:6px}
.sched tr.rc td{background:var(--accent-soft)}
.sched tr.p0 td.d{color:var(--p0-ink)}.sched tr.p1 td.d{color:var(--p1-ink)}.sched tr.p2 td.d{color:var(--p2-ink)}
.sched .njid{font-family:var(--mono);font-size:11px;color:var(--justin);font-weight:600;margin-right:4px}
.sched .rcx{font-family:var(--mono);font-size:11px;padding:0 6px;border-radius:3px;background:var(--accent);color:var(--accent-ink);font-weight:600;margin-left:4px}
.sched td.starts{font-family:var(--mono);font-size:11.5px;color:var(--ink-2);max-width:260px}
.agent header a.sheet{font-family:var(--mono);font-size:11px}
@media (max-width:640px){.two{grid-template-columns:1fr}}
"""
doc = replace_literal("\n@media (prefers-reduced-motion:no-preference){a{transition:color .15s}}\n</style>",
                      css_add + "@media (prefers-reduced-motion:no-preference){a{transition:color .15s}}\n</style>", doc, "css tail")

# ---------------------------------------------------------------- 1. masthead
doc = replace_literal('Blueprint rev 1 · Sep 17, 2026', 'Blueprint rev 2 · Sep 17, 2026 · round 2', doc, "kicker rev")
doc = replace_literal('<span>Budget ≈ $10,000 Claude credits</span>',
                      f'<span>{n_docs} Linear documents</span><span>Budget ≈ $10,000 Claude credits</span>', doc, "meta docs")
doc = replace_literal(
    '<a href="#s1"><b>1</b>Ten-second summary</a><a href="#s2"><b>2</b>Architecture</a><a href="#s3"><b>3</b>Agent organisation</a><a href="#s4"><b>4</b>Two-week plan</a><a href="#s5"><b>5</b>Credit budget</a><a href="#s6"><b>6</b>Decisions</a><a href="#s7"><b>7</b>Project index</a><a href="#s8"><b>8</b>Risks</a><a href="#s9"><b>9</b>How the pipeline runs</a>',
    '<a href="#s1"><b>1</b>Ten-second summary</a><a href="#s10"><b>2</b>Round 2: what got better</a><a href="#s2"><b>3</b>Architecture</a><a href="#s11"><b>4</b>Interface map</a><a href="#s3"><b>5</b>Agent organisation</a><a href="#s4"><b>6</b>Two-week plan</a><a href="#s12"><b>7</b>Day by day</a><a href="#s5"><b>8</b>Credit budget</a><a href="#s6"><b>9</b>Decisions</a><a href="#s7"><b>10</b>Project index</a><a href="#s8"><b>11</b>Risks</a><a href="#s9"><b>12</b>How the pipeline runs</a>',
    doc, "toc")

# ---------------------------------------------------------------- 2. summary stats
stats_new = f'''<div class="stats">
    <div class="stat"><span class="n">17</span><span class="l">Linear projects</span></div>
    <div class="stat"><span class="n">{n_issues}</span><span class="l">issues with full specs ({n_children} are children of {n_parents} split parents)</span></div>
    <div class="stat hot"><span class="n">{n_ready}</span><span class="l">Ready for Claude right now</span></div>
    <div class="stat"><span class="n">{n_blocks}</span><span class="l">blocking relations, zero cycles, zero milestone inversions</span></div>
    <div class="stat"><span class="n">{n_docs}</span><span class="l">Linear documents (contracts, threat model, schedule, roster, golden path)</span></div>
    <div class="stat"><span class="n">14</span><span class="l">days to Oct 1 deadline</span></div>
    <div class="stat"><span class="n">{n_milestones}</span><span class="l">dated milestones</span></div>
    <div class="stat"><span class="n">9+28</span><span class="l">lead characters + sub-characters, each with a character sheet</span></div>
    <div class="stat"><span class="n">{n_pending}</span><span class="l">more specs written, waiting on the Linear plan cap (NJ-1)</span></div>
  </div>'''
doc = sub1(r'<div class="stats">.*?</div>\n  </div>', stats_new, doc, flags=re.S, name="stats block")
doc = replace_literal(
    '<li><b>Linear is the queue.</b> Ready for Claude issues become parallel Claude Code sessions; only weekly release candidates and a dozen one-off decisions reach Justin.</li>',
    f'<li><b>Linear is the queue.</b> Ready for Claude issues become parallel Claude Code sessions; the orchestrator promotes Backlog issues as their blockers land (branch-start rule); only release candidates and 21 numbered one-off decisions reach Justin.</li>\n    <li><b>Documents hold the decisions; issues say what to build.</b> Every session reads the <a href="{D["contracts"]}" target="_blank" rel="noopener">Contracts</a>, its project\'s Contract section, its <a href="{D["roster"]}" target="_blank" rel="noopener">character sheet</a>, the <a href="{D["threat"]}" target="_blank" rel="noopener">Threat Model</a> and the <a href="{D["schedule"]}" target="_blank" rel="noopener">Execution Schedule</a> before writing code. If an issue and a document disagree, the document wins and an ADR is filed.</li>',
    doc, "queue bullet")

# ---------------------------------------------------------------- 3. architecture numbers
doc = replace_literal('206 issues · 284 blocking relations', f'{n_issues} issues · {n_blocks} blocking relations', doc, "arch numbers")

# ---------------------------------------------------------------- 4. Round 2 section
scores = [  # key, before (C,P,B,T), after
    ("app-shell", (5,5,4,4), (5,5,4,4)), ("data-layer", (5,5,4,5), (5,5,4,5)), ("forge", (4,5,4,5), (4,5,4,5)),
    ("identity", (4,5,4,5), (5,5,4,5)), ("design-system", (4,5,5,4), (5,5,5,5)), ("quality", (5,4,3,4), (5,5,4,5)),
    ("pm-linear", (4,4,4,4), (4,5,3,4)), ("agents", (5,4,3,4), (5,5,3,4)), ("spec-builder", (5,5,4,5), (5,5,4,5)),
    ("collab", (4,4,4,4), (4,5,4,4)), ("realtime", (5,5,4,4), (5,5,4,4)), ("input", (5,5,3,3), (5,5,4,4)),
    ("tables", (5,5,4,4), (5,5,4,4)), ("business-core", (4,5,3,4), (4,5,4,4)), ("growth", (4,4,2,3), (4,5,3,4)),
    ("migration", (4,5,3,4), (4,5,3,4)), ("libraries", (5,4,5,4), (5,5,5,4)),
]
tb = sum(sum(b) for _, b, _ in scores); ta = sum(sum(a) for _, _, a in scores)
score_rows = ""
for k, b, a in scores:
    sb, sa = sum(b), sum(a)
    delta = sa - sb
    P = lin["projects"][k]
    score_rows += (f'<tr><td><a href="{P["url"]}" target="_blank" rel="noopener">{esc(short_name[k])}</a></td>'
                   f'<td class="n">{"/".join(map(str,b))}</td><td class="n">{"/".join(map(str,a))}</td>'
                   f'<td class="n"><span class="bar" style="width:{sb*6}px"></span>{sb}</td>'
                   f'<td class="n"><span class="bar after" style="width:{sa*6}px"></span>{sa}</td>'
                   f'<td class="n{" up" if delta>0 else ""}">{"+"+str(delta) if delta>0 else ("±0" if delta==0 else delta)}</td></tr>')
score_rows += (f'<tr><td><b>Total</b></td><td class="n"></td><td class="n"></td><td class="n"><b>{tb}</b> / 340</td><td class="n"><b>{ta}</b> / 340</td><td class="n up">+{ta-tb}</td></tr>')

facts = [
    ("Non-archived issues (PAP-13 and up)", "206", str(n_issues), f"+{n_issues-206}: 12 gap issues and {n_children} children of {n_parents} L-size parents (PAP-219 to PAP-279)"),
    ("<code>blocks</code> relations", "284", str(n_blocks), "children now inherit their parents' blockers; zero cycles, zero milestone date inversions"),
    ("Ready for Claude", "21", str(n_ready), "every Ready issue has zero open inbound blockers (READY_BUT_BLOCKED is now a validator error)"),
    ("Needs Justin", "0", str(n_nj), "PAP-91 carries NJ-1: upgrade the Linear plan so the pending specs can be created"),
    ("Issues labelled <code>Deferred</code> (v0.2)", "0", str(n_deferred), "priority 4, never claimed by the orchestrator, reinstated only at the 09-27 stop-loss checkpoint"),
    ("Linear documents", "1", str(n_docs), "Contracts, Threat Model, Execution Schedule, Golden Path, Roster + 9 character sheets, 11 pending-issue documents"),
    ("Spec sections per issue", "8", "11", "every spec now has Interface contract, Test plan and Demo, so a reviewer session can verify a PR without Justin"),
    ("Specified issues Linear refused to create", "0", str(n_pending), "free-plan cap (USAGE_LIMIT_EXCEEDED); full specs live in the pending documents, ordered for creation on /approve"),
]
fact_rows = "".join(f'<tr><td>{f[0]}</td><td class="n">{f[1]}</td><td class="n up">{f[2]}</td><td class="mute">{f[3]}</td></tr>' for f in facts)

new_docs = [
    (D["contracts"], "PaperOS Interface &amp; Data Contracts", "ids and RLS session context, <code>Principal</code>, <code>Money</code>, <code>FilterTree</code>, shared data model, event envelope and topic catalogue, API conventions, package boundaries, a 30-row provide/consume matrix"),
    (D["threat"], "PaperOS Security &amp; Threat Model", "STRIDE per trust boundary, destructive-action deny list for agents, secrets, prompt-injection tiers T0-T4, backup and DR, PCI SAQ-A posture; PAP-219 turns it into <code>controls.yaml</code>"),
    (D["schedule"], "PaperOS Execution Schedule", "day-by-day starts 09-17 to 10-01 for 223 scheduled units, capacity curve 8 → 20 → 2 sessions, RC0-RC3, NJ-1..NJ-21, credit burn model ($8,345 of $10,000) and stop-loss rules"),
    (D["roster"], "PaperOS Agent Roster + 9 character sheets", "org chart, routing, shared rules and escalation matrix; one sheet per lead: " + ", ".join(f'<a href="{u}" target="_blank" rel="noopener">{esc(n)}</a>' for n, u in sorted(char_sheets.items()))),
    (D["golden"], "New App in Ten Minutes: the golden path", "the answer to PAP-5: what <code>paperos create</code> asks, generates and deploys, with the acceptance test that times it"),
]
doc_items = "".join(f'<li><span class="t-mono">{i+1}</span><div><b><a href="{u}" target="_blank" rel="noopener">{t}</a></b><span>{s}</span></div></li>' for i, (u, t, s) in enumerate(new_docs))
pending_items = " · ".join(f'<a href="{d["url"]}" target="_blank" rel="noopener">{esc(d["title"].replace("Round 2 pending issues: ",""))}</a>' for d in pending_docs)

fixes = [
    ("Milestone date inversions 8 → 0.", "three milestone dates moved, PAP-26 re-homed, three edges made soft with matching Dependencies text on both ends."),
    ("Ready-but-blocked 2 → 0.", "PAP-13 → PAP-279 and PAP-279 → PAP-161 became soft; READY_BUT_BLOCKED is an error in PAP-93's validator."),
    ("Children inherit blockers: +103 relations.", "every one of the 49 children has at least one external blocker; umbrella rule written into PAP-92, PAP-93 and PAP-96 (an issue with sub-issues is never claimed)."),
    ("<code>Deferred</code> label on 28 v0.2 issues.", "priority 4, deferral line under Goal, orchestrator claim filter; PAP-235 → PAP-180 and PAP-190 → PAP-192 softened so nothing scheduled waits on deferred work."),
    ("The issue cap became a visible ask.", "NJ-1 on PAP-91 (Needs Justin) with the create order; Plan B folds test accounts into PAP-198, consent centre into PAP-187, dunning into PAP-180, spec versioning into PAP-114."),
    ("Pending documents deduplicated.", "10 twin specs merged, one obsolete issue removed, runtime sandbox rewritten; 156 pending entries, zero unresolved bracketed keys in live issues."),
    ("A read-first path exists.", "the Linear Blueprint lists every document in reading order; PAP-92, 13, 91, 103, 114, 219, 279, 96 and 25 say what to read; 29 issues cite the Contracts section they implement."),
    ("Promotion rule defined.", "PAP-96 promotes Backlog → Ready when every blocker is Done or In Review with a PR (branch-start rule); BLOCKED_BY_OPEN is an error; Atlas runs <code>pnpm linear:promote --dry-run</code> until the orchestrator is live."),
]
fix_items = "".join(f'<li><div><b>{a}</b> <span>{b}</span></div></li>' for a, b in fixes)

round2_section = f'''
<section id="s10">
  <header><div class="kicker"><b>02</b> Round 2: what got better</div><h2>Same plan, deeper: {n_issues-206} new issues, {n_blocks-284} new relations, {n_docs-1} new documents, {ta-tb} points on the audit</h2></header>
  <p class="prose">Round 2 read every one of the 206 specs against the brief, the relation graph and the live workspace, scored each project on coverage, precision, buildability and testability (1-5 each), then sent seven agents to fix the weakest parts: split the L-size issues into children, write the cross-project contracts that nobody owned, give every spec an interface contract, test plan and demo script, schedule every unit to a half-day, and describe each agent character. A second critique found eight regressions and gaps, all fixed the same morning. Snapshot {esc(TAKEN)}.</p>
  <div class="tablewrap" style="margin-top:22px"><table class="facts"><thead><tr><th>Fact</th><th>03:30Z</th><th>now</th><th>What changed</th></tr></thead><tbody>{fact_rows}</tbody></table></div>
  <div class="two">
    <div>
      <h3 style="margin-bottom:10px">Project scores, before → after</h3>
      <p class="mute" style="font-size:13px;margin-bottom:10px">Coverage / precision / buildability / testability, each 1-5. Precision is now 5 everywhere; the remaining deficit is buildability, and most of it has one cause: the {n_pending} specified issues the free plan will not let us create.</p>
      <div class="tablewrap"><table class="facts" style="margin-top:0"><thead><tr><th>Project</th><th>C/P/B/T before</th><th>after</th><th>before</th><th>after</th><th>Δ</th></tr></thead><tbody>{score_rows}</tbody></table></div>
    </div>
    <div>
      <h3 style="margin-bottom:10px">New documents, in reading order</h3>
      <ol class="doclist">{doc_items}</ol>
      <p class="mute" style="font-size:13px;margin-top:14px">Waiting on the issue cap, one document per project with the full spec of every pending issue: {pending_items}.</p>
    </div>
  </div>
  <h3 style="margin-top:26px;margin-bottom:10px">Eight fixes from the second critique</h3>
  <ol class="fixes">{fix_items}</ol>
</section>
'''

# ---------------------------------------------------------------- 5. interface map SVG
def box(x, y, w, h, title, sub, cls="", fill="var(--card)", stroke="currentColor", dash=False, sw=1.2):
    dasha = ' stroke-dasharray="5 4"' if dash else ''
    s = f'<g class="node {cls}"><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{dasha}/>'
    s += f'<text x="{x+12}" y="{y+20}" class="t-strong">{esc(title)}</text>'
    for i, line in enumerate(sub):
        s += f'<text x="{x+12}" y="{y+38+i*15}" class="t-small t-mute">{esc(line)}</text>'
    return s + '</g>'
def arrow(d, label=None, lx=0, ly=0, anchor="middle", start=False, stroke="currentColor"):
    ms = ' marker-start="url(#ahs2)"' if start else ''
    s = f'<path d="{d}" fill="none" stroke="{stroke}" stroke-width="1.4" marker-end="url(#ah2)"{ms}/>'
    if label:
        s += f'<text x="{lx}" y="{ly}" text-anchor="{anchor}" class="t-small t-mute lbl">{esc(label)}</text>'
    return s

im = ('<svg class="fig" viewBox="0 0 1000 570" role="img" aria-label="Interface map: which core system provides which contract to which other system. Data layer provides entities, RLS context, FilterTree, sync shapes, events and jobs to identity, realtime, tables and the optional modules; identity provides Principal and can() to collaboration; design system provides component ids and tokens to the spec builder, which drives the app shell; the app shell provides the module manifest; realtime provides Yjs rooms to collaboration; spec builder feeds conformance tests into the quality pipeline, which exchanges gate verdicts with the Linear pipeline; agents consume the issue contract and gate artifacts and provide character definitions to the template.">'
      '<defs><marker id="ah2" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0L10 5L0 10z" fill="currentColor"/></marker>'
      '<marker id="ahs2" viewBox="0 0 10 10" refX="1" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M10 0L0 5L10 10z" fill="currentColor"/></marker></defs>')
im += '<text x="0" y="14" class="t-mono t-mute">BUILD LOOP</text>'
im += box(0, 24, 270, 80, 'PM & Linear pipeline', ['provides issue contract, states (PAP-91, 93)', 'and the Justin queue (PAP-94)', 'consumes gate verdicts, handoff, events'])
im += box(365, 24, 270, 80, 'Quality pipeline', ['provides gate artifacts (PAP-239)', 'and test-mode seeding (PAP-240)', 'consumes page specs, threat model (219)'], cls="hot")
im += box(730, 24, 270, 80, 'Agent characters', ['provides handoff + character schema', '(PAP-103, 108), tool scopes', 'consumes issue contract, gate artifacts'])
im += arrow('M270 64 L363 64', 'issue contract', 317, 54, start=True) + '<text x="317" y="80" text-anchor="middle" class="t-small t-mute lbl">gate verdicts</text>'
im += arrow('M635 64 L728 64', 'gate artifacts', 681, 54)
im += arrow('M380 150 L380 106', 'spec → conformance tests', 388, 132, anchor="start")
im += arrow('M860 104 L860 148', 'character defs → .claude/', 852, 130, anchor="end")
im += '<text x="0" y="140" class="t-mono t-mute">PRODUCT SURFACES</text>'
im += box(0, 150, 300, 80, 'Design system', ['provides component ids (PAP-74),', 'tokens and branding (PAP-66, 75)', 'consumes tenant.branding (PAP-33)'])
im += box(350, 150, 300, 80, 'Spec builder', ['provides page + app spec schema', '(PAP-114, 117), codegen (PAP-120)', 'consumes component ids, FilterTree'], fill="var(--accent-soft)", stroke="var(--accent)", sw=1.6)
im += box(700, 150, 300, 80, 'App shell & template', ['provides module manifest (PAP-264),', 'package boundary map, router slots (16)', 'consumes page specs, tokens, auth client'])
im += arrow('M150 230 L150 262 L500 262 L500 232', 'component ids · tokens', 325, 256)
im += arrow('M600 230 L600 250 L850 250 L850 232', 'page specs → routes · codegen', 725, 244)
im += arrow('M920 230 L920 298', 'module manifest · route slots', 912, 280, anchor="end")
im += '<text x="0" y="290" class="t-mono t-mute">COLLABORATION, DATA VIEWS, MODULES</text>'
im += box(0, 300, 210, 80, 'Collaboration', ['provides comment anchors', '(PAP-131), docs (PAP-128)', 'consumes rooms, files, search'])
im += box(250, 300, 210, 80, 'Realtime', ['provides Yjs rooms + auth', 'hook (PAP-140), presence', 'consumes sync shapes, Principal'])
im += box(500, 300, 210, 80, 'Table & views engine', ['provides view model (PAP-161)', 'consumes FilterTree, cursors,', 'can() predicates (PAP-59)'])
im += box(750, 300, 250, 80, 'Optional modules', ['business core provides finance model', 'and ledger posting (PAP-175, 179)', 'growth · PM · migration consume views'], dash=True)
im += arrow('M350 380 L350 402 L140 402 L140 382', 'Yjs rooms · presence', 245, 396)
im += '<text x="0" y="420" class="t-mono t-mute">FOUNDATION</text>'
im += box(0, 430, 310, 96, 'Identity & audiences', ['provides Principal (PAP-55), can() and', 'SQL predicates (PAP-59), agent keys (60)', 'consumes entities, RLS context, events', 'every actor: human · agent · service'])
im += box(380, 430, 620, 96, 'Data layer', ['provides core entities (PAP-33), RLS session context (PAP-34), FilterTree (PAP-279),', 'API middleware + routers (PAP-267, 268), sync shapes + outbox (PAP-270-272), jobs (43),', 'audit (38), files (37), search (39); pending: value types, event envelope, idempotency', 'consumes Principal for the API context'])
im += arrow('M100 430 L100 382', 'Principal · can() · sessions', 108, 418, anchor="start")
im += arrow('M420 430 L420 382', 'sync shapes · outbox', 428, 418, anchor="start")
im += arrow('M600 430 L600 382', 'FilterTree · cursors · routers', 608, 418, anchor="start")
im += arrow('M880 430 L880 382', 'entities · Money · events · jobs', 872, 418, anchor="end")
im += arrow('M380 480 L312 480', 'entities', 346, 470) + '<text x="346" y="496" text-anchor="middle" class="t-small t-mute lbl">RLS context</text>'
im += '<text x="0" y="556" class="t-small t-mute">Arrows point from the system that owns a contract to the system that codes against it, labelled with the contract. Dashed box: modules an app can ship without. Tinted box: the spec contract every surface reads.</text>'
im += '</svg>'

interface_section = f'''
<section id="s11">
  <header><div class="kicker"><b>04</b> Interface map</div><h2>Who provides which contract to whom, so seventeen projects converge instead of drifting</h2></header>
  <p class="prose" style="margin-bottom:22px">Round 1 left the shapes that cross project lines unowned: three different <code>Money</code> types, two actor enums, filter grammars in four packages. The <a href="{D["contracts"]}" target="_blank" rel="noopener">Contracts document</a> now fixes each one to a single owning issue and a 30-row provide/consume matrix; this figure is that matrix reduced to the flows a cold session must know before it writes a line. Every arrow is also a <code>Contract source:</code> line in the consuming issue's Interface contract section.</p>
  <figure>
    <div class="figwrap">{im}</div>
    <figcaption>Conventions that apply everywhere and are not drawn: ids are UUIDv7; every tenant-scoped table has <code>tenant_id</code> first and soft delete; <code>Money</code> is <code>{{ amountMinor: bigint, currency }}</code> at runtime and a decimal string on the wire; Zod 4 is the schema language and JSON Schema is generated, never written by hand; the event bus is a Postgres transactional outbox drained by the jobs worker, at-least-once, ordered per subject. Four contracts (shared value types, event envelope, idempotency and rate limits, package boundary map) are fully specified but wait on the issue cap; until then the Contracts document is their body.</figcaption>
  </figure>
</section>
'''

# ---------------------------------------------------------------- 6. timeline regenerated from live milestones
def day_idx(d):
    from datetime import date
    y, m, dd = map(int, d.split("-"))
    return (date(y, m, dd) - date(2026, 9, 17)).days
TL_left, TL_top, TL_rowH, TL_w, TL_right = 200, 46, 24, 760/15, 20
tlH = TL_top + len(proj_keys) * TL_rowH + 34
tlW = TL_left + 760 + TL_right
bands = [("P0", 0, 4), ("P1", 4, 10), ("P2", 10, 15)]
phase_name = {p["key"]: p["name"] for p in plan["phases"]}
tl = f'<svg class="fig" viewBox="0 0 {tlW:g} {tlH:g}" role="img" aria-label="Milestone timeline: every project\'s three milestones plotted by target date across the three phases from 17 September to 1 October 2026, after the round-2 schedule moved twenty of them">'
tl += f'<defs><clipPath id="tlclip"><rect x="0" y="0" width="{tlW:g}" height="{tlH:g}"/></clipPath></defs>'
for k, a, b in bands:
    x = TL_left + a * TL_w; w = (b - a) * TL_w
    tl += f'<rect x="{x:.2f}" y="{TL_top-8}" width="{w:.2f}" height="{len(proj_keys)*TL_rowH+8}" fill="var(--{k.lower()})" opacity="0.13"/>'
    tl += f'<text x="{x+6:.2f}" y="16" class="t-mono t-strong" fill="var(--{k.lower()}-ink)">{k} · {esc(phase_name[k])}</text>'
from datetime import date, timedelta
for d in range(15):
    x = TL_left + d * TL_w
    dt = date(2026, 9, 17) + timedelta(days=d)
    lab = ("Sep " if dt.month == 9 else "Oct ") + str(dt.day)
    tl += f'<line x1="{x:.2f}" y1="{TL_top-8}" x2="{x:.2f}" y2="{TL_top+len(proj_keys)*TL_rowH}" stroke="currentColor" opacity="{0.35 if d%7==0 or d==14 else 0.12}"/>'
    if d % 2 == 0:
        tl += f'<text x="{x+TL_w/2:.2f}" y="{TL_top-14}" text-anchor="middle" class="t-mono t-mute">{lab}</text>'
tl += f'<line x1="{TL_left+15*TL_w:.2f}" y1="{TL_top-8}" x2="{TL_left+15*TL_w:.2f}" y2="{TL_top+len(proj_keys)*TL_rowH}" stroke="currentColor" opacity="0.35"/>'
moved = 0
for i, k in enumerate(proj_keys):
    P = proj_by_name[lin["projects"][k]["name"]]
    plan_ms = {m["name"]: m for m in plan_proj[k]["milestones"]}
    y = TL_top + i * TL_rowH + TL_rowH / 2
    tl += f'<text x="{TL_left-12}" y="{y+4:.1f}" text-anchor="end" class="t-label">{esc(short_name[k])}</text>'
    tl += f'<line x1="{TL_left}" y1="{y:.1f}" x2="{TL_left+15*TL_w:.2f}" y2="{y:.1f}" stroke="currentColor" opacity="0.08"/>'
    ms = sorted(P["milestones"], key=lambda m: m["targetDate"])
    xs = [TL_left + (day_idx(m["targetDate"]) + 0.5) * TL_w for m in ms]
    tl += f'<line x1="{TL_left+0.5*TL_w:.2f}" y1="{y:.1f}" x2="{xs[-1]:.2f}" y2="{y:.1f}" stroke="var(--accent)" stroke-width="2" opacity="0.55"/>'
    for m, x in zip(ms, xs):
        pm = plan_ms.get(m["name"], {})
        was = pm.get("targetDate")
        if was and was != m["targetDate"]:
            moved += 1
            wx = TL_left + (day_idx(was) + 0.5) * TL_w
            tl += f'<circle cx="{wx:.2f}" cy="{y:.1f}" r="4" fill="none" stroke="var(--accent)" stroke-width="1.2" stroke-dasharray="2 2" opacity="0.7"/>'
        title = f'{P["name"]} · {m["name"]} ({m["targetDate"]}' + (f', was {was}' if was and was != m["targetDate"] else '') + ')' + (f': {pm["goal"]}' if pm.get("goal") else '')
        tl += f'<circle cx="{x:.2f}" cy="{y:.1f}" r="5" fill="var(--accent)" stroke="var(--card)" stroke-width="2"><title>{esc(title)}</title></circle>'
tl += f'<text x="{TL_left}" y="{tlH-10}" class="t-mono t-mute">Today: Sep 17</text><text x="{TL_left+15*TL_w:.2f}" y="{tlH-10}" text-anchor="end" class="t-mono t-mute">Deadline: Oct 1 · 14 days</text>'
tl += '</svg>'
doc = sub1(r'<svg class="fig" viewBox="0 0 980 488" role="img" aria-label="Milestone timeline:.*?</svg>', lambda m: tl, doc, flags=re.S, name="timeline svg")
doc = sub1(r'<figcaption>Each row is a Linear project; each dot is one of its three milestones.*?</figcaption>',
           lambda m: f'<figcaption>Each row is a Linear project; each solid dot is one of its three milestones at its live target date (hover a dot for the milestone, its goal and its previous date). Dotted rings are where {moved} of the {n_milestones} milestones sat before the Execution Schedule simulated the {n_blocks}-edge graph and moved them; every move is later, none past Oct 1, and no blocker now sits in a milestone dated after the issue it blocks. The P0 rows land their first milestones on Sep 20 to 22, which is the serial chain the risks section warns about.</figcaption>', doc, flags=re.S, name="timeline caption")
doc = replace_literal('<h2>Three phases, 51 milestones, one deadline</h2>', f'<h2>Three phases, {n_milestones} milestones ({moved} re-dated by the schedule), one deadline</h2>', doc, "s4 h2")

# ---------------------------------------------------------------- 7. day-by-day schedule section
def link(k):
    i = by_id.get(f"PAP-{k}")
    return f'<a href="{i["url"]}" target="_blank" rel="noopener">PAP-{k}</a>' if i else f"PAP-{k}"
def linkify(text):
    return re.sub(r'PAP-(\d+)', lambda m: link(m.group(1)), text)
sched = [
    ("09-17", "13 14 25 31 55 56 66 79 209 212", 8, "manual /code-review", [("NJ-1", "Linear: upgrade the workspace plan so ~156 specified issues can be created (PAP-91, in Needs Justin now)"), ("NJ-2", "Infra batch (PAP-25): Hetzner account, registrar or Cloudflare token, Resend, sops recovery key"), ("NJ-3", "GitHub App on org imagine-os (PAP-47)"), ("NJ-4", "Anthropic Console: orchestrator API key, $10K hard limit, usage export (PAP-98)")], None, "P0"),
    ("09-18", "16 17 30 32 42 46 78 91 92 94 127 150 214 236 239 273 279", 12, "manual; Gate 1 CI live (PAP-78)", [("NJ-5", "Linear: orchestrator API key and webhook signing secret (PAP-92, PAP-97)")], None, "P0"),
    ("09-19", "26 33 68 96 103 104 105 114 128 139 161 210 213 219 237 243 255 274 275", 16, "manual; harness PAP-243 lands", [("NJ-6", "Code signing (PAP-256): Apple Developer Program and Windows signing, or accept unsigned v0.1.0; default after 48 h: unsigned")], None, "P0"),
    ("09-20", "15 18 34 43 44 47 48 49 93 95 115 117 133 175 211 223 238 244 245 256 267", 20, "Gate 2 dry run", [("NJ-7", "License of the template code (PAP-211): default Apache-2.0"), ("NJ-8", "Approve docs/pm/justin-queue.md (PAP-94) and the issue contract (PAP-93)")], None, "P0"),
    ("09-21", "22 27 38 69 70 71 80 97 98 99 130 151 162 198 224 225 226 227 233 257 268", 20, "Gate 2 on every PR from here", [("NJ-9", "Hire the roster (PAP-104, PAP-210): nine leads, 28 sub-characters, tool scope classes")], "RC0", "P1"),
    ("09-22", "37 50 58 74 106 110 118 121 152 164 179 215 228 229 234 240 258 261 262 269", 20, "Gate 2; SAST (PAP-80)", [("NJ-10", "Stripe test-mode account and restricted key (PAP-177); Google OAuth consent screen (PAP-224, PAP-200)")], None, "P1"),
    ("09-23", "51 52 73 87 116 119 120 129 140 163 177 246 259 260 263 264 270", 20, "Gate 2; evals (PAP-110)", [], None, "P1"),
    ("09-24", "39 61 63 86 107 108 111 122 132 141 142 155 180 199 247 249 271", 20, "Gate 2; story baselines (PAP-246)", [("NJ-11", "Domain: set PAPEROS_DOMAIN or keep sslip.io for v0.1.0")], "RC1", "P1"),
    ("09-25", "62 72 109 112 123 131 134 145 156 165 168 170 176 220 241 242 248 250 265 272", 20, "Gates 2-3; calibration (PAP-241)", [("NJ-12", "Payroll provider (PAP-176): Check sandbox (default) or Gusto Embedded"), ("NJ-13", "Airtable demo base and token (PAP-202); Slack incoming webhook (PAP-136)")], None, "P1"),
    ("09-26", "60 83 84 100 124 143 153 154 167 169 178 187 188 200 201 251 252 253 266", 20, "Gates 2-3; PAP-83, 84, 251 land", [], None, "P1"),
    ("09-27", "24 64 101 102 135 136 166 171 172 181 183 184 189 202 205 254", 18, "Gates 2-4; nightly staging (PAP-253)", [("NJ-14", "Stop-loss checkpoint: go or no-go on the 28-issue stretch pool")], None, "P2"),
    ("09-28", "29 75 89 125 138 144 147 173 174 192 216", 16, "Gates 2-4; RC2 certify", [("NJ-15", "Release candidate v0.1.0-rc.2 from PAP-254: /approve or /reject")], "RC2", "P2"),
    ("09-29", "40 41 53 76 90 113 126 146 148 159 160 217", 14, "Gates 2-4; PAP-147, PAP-53 drills", [("NJ-16", "Approve the content agent (PAP-192) and migration agent (PAP-208)"), ("NJ-17", "Accessibility statement wording (PAP-160)")], None, "P2"),
    ("09-30", "77 186 208", 10, "Gates 2-4; no new claims after 12:00Z", [("NJ-18", "Industry list and terminology defaults (PAP-126)"), ("NJ-19", "Scope freeze: deferred list becomes milestone v0.2")], None, "P2"),
    ("10-01", "(none; RC3 regression only)", 2, "Gates 2-4 on RC3", [("NJ-20", "Release candidate v0.1.0: /approve promotes and tags"), ("NJ-21", "PAP-5: close or keep as scoreboard (PAP-95 vs PAP-29)")], "RC3", "P2"),
]
plan_line = {"09-17": 306, "09-18": 803, "09-19": 1435, "09-20": 2070, "09-21": 2793, "09-22": 3532, "09-23": 4289, "09-24": 4998, "09-25": 5685, "09-26": 6335, "09-27": 7063, "09-28": 7596, "09-29": 8044, "09-30": 8272, "10-01": 8345}
rows = ""
n_nj_items = 0
for day, starts, peak, rev, nj, rc, ph in sched:
    n_nj_items += len(nj)
    start_ids = [s for s in starts.split() if s.isdigit()]
    starts_html = " ".join(link(s) for s in start_ids) if start_ids else f'<span class="mute">{esc(starts)}</span>'
    nj_html = "<br>".join(f'<span class="njid">{k}</span>{linkify(esc(v))}' for k, v in nj) or '<span class="mute">queue drains</span>'
    if rc:
        nj_html += f' <span class="rcx">{rc}</span>'
    rows += (f'<tr class="{ph.lower()}{" rc" if rc else ""}"><td class="d">{day}</td><td class="starts">{len(start_ids)} · {starts_html}</td>'
             f'<td class="pk"><span class="pkbar" style="width:{peak*5}px"></span>{peak}</td><td class="mute">{linkify(esc(rev))}</td>'
             f'<td class="pk">${plan_line[day]:,}</td><td>{nj_html}</td></tr>')
schedule_section = f'''
<section id="s12">
  <header><div class="kicker"><b>07</b> Day by day</div><h2>Fifteen days, 223 scheduled units, {n_nj_items} decisions for Justin, one plan line for the credits</h2></header>
  <p class="prose" style="margin-bottom:18px">The <a href="{D["schedule"]}" target="_blank" rel="noopener">Execution Schedule</a> simulates the live <code>blocks</code> graph with S = half a session-day, M = one, L = two, and the branch-start rule (a dependent may start once every blocker is In Review with a PR open). Capacity ramps 8 → 20 parallel builder sessions and tapers to 2; reviewer sessions sit on top. Identifiers omit <code>PAP-</code>. Atlas re-simulates nightly and republishes the table; this is the 2026-09-17 cut.</p>
  <div class="tablewrap"><table class="sched"><thead><tr><th>Day</th><th>Starts</th><th>Peak sessions</th><th>Review</th><th>Plan line</th><th>Needs Justin · checkpoint</th></tr></thead><tbody>{rows}</tbody></table></div>
  <p class="mute" style="font-size:13px;margin-top:12px;max-width:80ch">Zero-slack chains, where a slip moves a milestone by the same amount: orchestrator {link(25)} → {link(96)} → {link(97)}/{link(98)}/{link(99)}; API and sync {link(33)} → {link(267)} → {link(268)} → {link(269)} → {link(270)} → {link(271)} → {link(272)} → {link(143)}; permissions {link(279)}/{link(34)} → {link(227)} → {link(228)}/{link(229)} → {link(140)} → {link(142)} → {link(131)}; gates {link(239)} → {link(243)} → {link(244)}/{link(245)} then {link(240)} → {link(246)} → {link(247)} → {link(248)}; tables {link(228)} → {link(163)} → {link(165)} → {link(166)}/{link(172)} → {link(173)}/{link(174)}. Stop-loss: two days above 115% of the plan line ends P2 claims; any day above 125% restricts claims to these chains and offers Justin a cut list or a top-up; $500 is locked from 09-29 for RC3 fixes.</p>
</section>
'''

# ---------------------------------------------------------------- 8. regenerate the full index
def issue_row(i, child=False):
    t = next((l for l in i["labels"] if l in type_labels), "")
    tags = f'<span class="type {TYPE_CLS.get(t,"")}">{esc(t)}</span>' if t else ""
    if i["state"] == "Ready for Claude":
        tags += '<span class="ready">Ready for Claude</span>'
    elif i["state"] == "Needs Justin":
        tags += '<span class="nj">Needs Justin</span>'
    if "Deferred" in i["labels"]:
        tags += '<span class="def">Deferred to v0.2</span>'
    if i["children"] and not child:
        tags += f'<span class="kid-n">{len(i["children"])} children</span>'
    ready = "true" if i["state"] == "Ready for Claude" else "false"
    a = f'<a href="{i["url"]}" target="_blank" rel="noopener"><span class="id">{i["identifier"]}</span><span class="tt">{esc(i["title"])}</span></a><span class="tags">{tags}</span>'
    if child:
        return f'<li data-ready="{ready}" data-state="{esc(i["state"])}">{a}</li>'
    return a, ready

def project_card(k):
    P = proj_by_name[lin["projects"][k]["name"]]
    ph = plan_proj[k]["phase"]
    pi = sorted([i for i in issues if i["projectName"] == P["name"]], key=lambda i: nums(i["identifier"]))
    tops = [i for i in pi if not i["parent"] or i["parent"] not in {x["identifier"] for x in pi}]
    kids_of = defaultdict(list)
    for i in pi:
        if i["parent"] and i["parent"] in {x["identifier"] for x in pi}:
            kids_of[i["parent"]].append(i)
    ready = sum(1 for i in pi if i["state"] == "Ready for Claude")
    nj = sum(1 for i in pi if i["state"] == "Needs Justin")
    nchild = sum(len(v) for v in kids_of.values())
    ms = sorted(P["milestones"], key=lambda m: m["targetDate"])
    lis = ""
    for i in tops:
        a, r = issue_row(i)
        if kids_of[i["identifier"]]:
            lis += f'<li class="group" data-ready="false"><div class="row" data-ready="{r}">{a}</div><ul class="kids">' + "".join(issue_row(c, True) for c in kids_of[i["identifier"]]) + '</ul></li>'
        else:
            lis += f'<li data-ready="{r}" data-state="{esc(i["state"])}">{a}</li>'
    meta = f'{len(pi)} issues' + (f' ({nchild} children)' if nchild else '') + f' · {len(ms)} milestones · target {P["targetDate"]}'
    if ready: meta += f' · <b class="ready-n">{ready} ready now</b>'
    if nj: meta += f' · <b style="color:var(--justin)">{nj} needs Justin</b>'
    return f'''<article class="proj" id="proj-{k}" data-phase="{ph}">
  <header>
    <div class="ph"><span class="phase {ph.lower()}">{ph}</span><span class="t-mono t-mute">{meta}</span></div>
    <h3><a href="{P["url"]}" target="_blank" rel="noopener">{esc(P["name"])}</a></h3>
    <p>{esc(plan_proj[k]["summary"])}</p>
  </header>
  <ol class="ms">{"".join(f'<li><span class="t-mono">{m["targetDate"]}</span> {esc(m["name"])}</li>' for m in ms)}</ol>
  <ul class="issues">{lis}</ul>
</article>'''

index_html = '<div class="index">' + "".join(project_card(k) for k in proj_keys) + '</div>'
doc = sub1(r'<div class="index">.*?</div>\n</section>', lambda m: index_html + '\n</section>', doc, flags=re.S, name="index")
doc = replace_literal('<h2>17 projects, 206 issues, every one linked to Linear</h2>',
                      f'<h2>17 projects, {n_issues} issues ({n_children} children indented under their {n_parents} parents), every one linked to Linear</h2>', doc, "s7 h2")
doc = replace_literal('<span class="ready">Ready for Claude</span><span>unblocked now; the orchestrator may claim it</span></div>',
                      '<span class="ready">Ready for Claude</span><span>unblocked now; the orchestrator may claim it</span><span class="nj">Needs Justin</span><span>waiting on a human decision</span><span class="def">Deferred to v0.2</span><span>not claimable before Oct 1</span><span class="kid-n">n children</span><span>umbrella issue; sessions claim the indented children, never the parent</span></div>', doc, "legend")

# ---------------------------------------------------------------- 9. risks
doc = replace_literal('<h2>Six things that can break the plan, from the completeness review</h2>', '<h2>Seven things that can break the plan, from the two completeness reviews</h2>', doc, "risks h2")
doc = replace_literal('<b>P0 is 68 issues in four days (Sep 17 to 20).</b><p>Even with parallel sessions, the chain scaffold → local stack → Drizzle → core entities → RLS → API → Better Auth → Yjs server is serial and each step is M-size. Expect P0 to spill into Sep 22 or 23; treat phase dates as targets for the ready set, not for the whole phase.</p>',
                      f'<b>P0 is {phase_counts["P0"]} issues, children included, and its chains are serial.</b><p>The schedule already moved the first milestones of data-layer, identity, design-system and pm-linear to Sep 20 to 23 because the chain scaffold → local stack → Drizzle → core entities → RLS → API → Better Auth → Yjs server cannot be parallelised. The branch-start rule (start against a blocker\'s open PR) is what makes the rest fit before Oct 1; if sessions wait for merges instead, add two days to every P1 milestone.</p>', doc, "risk 1")
doc = replace_literal('<b>Human account setup is on the critical path.</b><p>Hetzner (may need identity verification), a domain or Cloudflare, Resend, Apple developer program for signed macOS builds, Stripe live keys, a payroll sandbox. PAP-25 batches the first four into one Needs Justin item on day one; answer it the same day or every infra issue waits.</p>',
                      f'<b>Human account setup is on the critical path.</b><p>Hetzner (may need identity verification), a domain or Cloudflare, Resend, Apple developer program for signed macOS builds, Stripe test keys, a payroll sandbox. {link(25)} batches the infra credentials into NJ-2 on day one; answer it the same day or every infra issue waits. Issues whose credential is late start in sandbox or dryRun and mark the DoD line <code>blocked on NJ-2</code>.</p>', doc, "risk 2")
doc = sub1(r'(<ol class="risks">.*?)</ol>',
           lambda m: m.group(1) + f'<li><div><b>{n_pending} fully specified issues cannot be created on the free Linear plan.</b><p>Every <code>issueCreate</code> since 04:20Z returns <code>USAGE_LIMIT_EXCEEDED</code> at 275 issues. The specs exist in eleven "Round 2 pending issues" documents and are ordered for creation; until NJ-1 on {link(91)} is answered, the umbrella parents run as single L sessions using the pending specs inline, and the four hard dependencies on pending work were folded into live issues ({link(198)}, {link(187)}, {link(180)}, {link(114)}). The cost of not upgrading is coarser sessions and a thinner Ready queue from Sep 22, not lost scope.</p></div></li></ol>',
           doc, flags=re.S, name="risk 7")

# ---------------------------------------------------------------- 10. pipeline section: ready list + Justin todo
ready = sorted([i for i in issues if i["state"] == "Ready for Claude"], key=lambda i: nums(i["identifier"]))
ready_html = "".join(f'<li><a href="{i["url"]}" target="_blank" rel="noopener"><span class="id">{i["identifier"]}</span>{esc(i["title"])}</a></li>' for i in ready)
doc = sub1(r'<h3>The 21 issues the orchestrator can start on today</h3>\n    <ul>.*?</ul>',
           lambda m: f'<h3>The {n_ready} issues the orchestrator can start on today</h3>\n    <p class="mute" style="font-size:13px">Every one has zero open inbound blockers. The 09-18 starts ({" ".join(link(s) for s in "16 17 30 32 42 46 78 236 273".split())}) follow by hand promotion the same evening once {link(13)} and {link(25)} have PRs open (branch-start rule).</p>\n    <ul>{ready_html}</ul>', doc, flags=re.S, name="ready list")
todo_new = f'''<ul>
      <li><b>Now (NJ-1, already in Needs Justin on {link(91)}):</b> upgrade the Linear workspace plan (Basic is enough) so the {n_pending} specified issues can be created, or reply <code>/decline</code> and the plan runs on the {n_issues} that exist. Either reply returns PAP-91 to Ready for Claude.</li>
      <li><b>Day one (NJ-2 to NJ-4):</b> the infra credential batch on {link(25)} (Hetzner, registrar or Cloudflare, Resend, sops recovery key), the GitHub App on imagine-os ({link(47)}), the Anthropic Console key with a $10K hard limit ({link(98)}). Every infra issue waits on these.</li>
      <li><b>Days two to five (NJ-5 to NJ-9):</b> Linear orchestrator key and webhook secret, code signing or unsigned installers (default after 48 h: unsigned), template licence (default Apache-2.0), approve the Justin queue format and issue contract, hire the roster.</li>
      <li><b>Release candidates:</b> RC0 Sep 21 (informational), RC1 Sep 24 with the domain decision (NJ-11), RC2 Sep 28 <code>/approve</code> or <code>/reject</code> (NJ-15), RC3 = v0.1.0 on Oct 1 (NJ-20). Treat RC0 as a smoke test and spot-check five Gate 2 verdicts that week.</li>
      <li><b>Sep 27 (NJ-14):</b> the stop-loss checkpoint: go or no-go on the {n_deferred}-issue stretch pool against the plan line; Sep 30 (NJ-19) freezes scope and the deferred list becomes milestone v0.2.</li>
      <li><b>As they arrive:</b> Stripe test account, payroll sandbox, Airtable and Slack tokens (NJ-10, 12, 13), content and migration agent approvals, accessibility statement, industry terminology defaults (NJ-16 to NJ-18). Never more than five open cards at once.</li>
    </ul>'''
doc = sub1(r'(<h3>What Justin has to do</h3>\n    <p class="mute" style="font-size:14px">[^<]*</p>\n    )<ul>.*?</ul>', lambda m: m.group(1) + todo_new, doc, flags=re.S, name="todo list")
doc = replace_literal('<h2>Six states, one human column</h2>', f'<h2>Six states, one human column, {n_nj} card in it today</h2>', doc, "s9 h2")

# ---------------------------------------------------------------- 11. agent cards: link character sheets
for name, url in char_sheets.items():
    pat = f'<header><h4>{name}</h4><span class="t-mono t-mute">'
    if pat in doc:
        doc = doc.replace(pat, f'<header><h4>{name}</h4><a class="sheet" href="{url}" target="_blank" rel="noopener">character sheet</a><span class="t-mono t-mute">', 1)
    else:
        print("no card for", name, file=sys.stderr)
doc = replace_literal('<h2>Nine lead characters, 28 sub-characters, every one with explicit tools and access</h2>',
                      f'<h2>Nine lead characters, 28 sub-characters, every one with explicit tools, access and a <a href="{D["roster"]}" target="_blank" rel="noopener">character sheet</a></h2>', doc, "s3 h2")

# ---------------------------------------------------------------- 12. insert new sections, renumber kickers, footer
doc = replace_literal('\n<section id="s2">', round2_section + '\n<section id="s2">', doc, "insert round2")
doc = replace_literal('\n<section id="s3">', interface_section + '\n<section id="s3">', doc, "insert interface")
doc = replace_literal('\n<section id="s5">', schedule_section + '\n<section id="s5">', doc, "insert schedule")
counter = [0]
def renum(m):
    counter[0] += 1
    return f'<div class="kicker"><b>{counter[0]:02d}</b>'
doc = re.sub(r'<div class="kicker"><b>\d\d</b>', renum, doc)
assert counter[0] == 12, counter
doc = sub1(r'<footer>Generated 2026-09-17 from plan\.json, critique\.md and the Linear build log',
           f'<footer>Rev 2 · regenerated {esc(TAKEN)} from the live Linear snapshot ({n_issues} issues, {n_blocks} relations, {n_docs} documents), plan.json and both critiques', doc, name="footer")

open(HTML, "w", encoding="utf-8").write(doc)
print(f"wrote {len(doc)} bytes (was {orig_len}); moved milestones {moved}; ready {n_ready}; nj items {n_nj_items}", file=sys.stderr)
json.dump({"issues": n_issues, "ready": n_ready, "needsJustin": n_nj, "children": n_children, "parents": n_parents, "blocks": n_blocks,
           "deferred": n_deferred, "documents": n_docs, "milestones": n_milestones, "movedMilestones": moved, "pending": n_pending,
           "scoreBefore": tb, "scoreAfter": ta, "takenAt": TAKEN, "docs": D, "charSheets": char_sheets,
           "pendingDocs": [{"title": d["title"], "url": d["url"]} for d in pending_docs]},
          open(BASE + "/round2/blueprint-r2-numbers.json", "w"), indent=1)
