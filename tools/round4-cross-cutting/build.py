"""Assemble, validate and write cross-cutting.json and the digest."""
import json, re, sys, collections
sys.path.insert(0, '/tmp/claude-0/-home-claude/c81b343e-37f0-53d7-b291-027405cb96ed/scratchpad/r4cross')
from gen_common import render
from capmap import CAPMAP
from cross import CROSS
import proj_assistant, proj_workflows, proj_engagement, proj_commerce, proj_platform_ops

INV = '/tmp/claude-0/-home-claude/c81b343e-37f0-53d7-b291-027405cb96ed/scratchpad/linear-inventory.json'
PLAN = '/home/claude/linear-builder/plan/plan.json'
OUT_JSON = '/home/claude/linear-builder/plan/round4/gaps/cross-cutting.json'
OUT_MD = '/home/claude/linear-builder/plan/round4/digest/cross-cutting.md'

inv = json.load(open(INV))
plan = json.load(open(PLAN))
name_to_key = {p['name']: p['key'] for p in plan['projects']}
name_to_key['Module System & Swap Tooling'] = 'module-system'
pap_ids = set()
proj_ms = {}
for p in inv['projects']:
    k = name_to_key[p['name']]
    proj_ms[k] = {m['name'] for m in p['projectMilestones']['nodes']}
    for i in p['issues']:
        pap_ids.add(i['identifier'])
for i in inv['issuesWithoutProject']:
    pap_ids.add(i['identifier'])
existing_keys = set(proj_ms)

PROJECTS = [proj_assistant, proj_workflows, proj_engagement, proj_commerce, proj_platform_ops]
new_projects = []
all_new_keys = set()
errors = []

for mod in PROJECTS:
    P = dict(mod.PROJECT)
    ms_names = {m['name'] for m in P['milestones']}
    issues = []
    for iss in mod.ISSUES:
        m = render(iss, P['key'])
        if m['milestone'] not in ms_names:
            errors.append(f"{m['key']}: milestone '{m['milestone']}' not in project")
        if not (2500 <= len(m['description']) <= 8500):
            errors.append(f"{m['key']}: description length {len(m['description'])}")
        if not m['description'].startswith('**Model / Effort:**'):
            errors.append(f"{m['key']}: bad first line")
        for sec in ['**Goal**', '**Scope**', '**Spec**', '**Interface contract**', '**Definition of done**', '**Test plan**', '**Demo**', '**Edge cases**', '**Dependencies**', '**Agent**', '**Size**']:
            if sec not in m['description']:
                errors.append(f"{m['key']}: missing {sec}")
        issues.append(m)
        all_new_keys.add(m['key'])
    P['issues'] = issues
    new_projects.append(P)

cross = []
for c in CROSS:
    m = render(c, c['targetProject'])
    tp = m['targetProject']
    if tp not in existing_keys:
        errors.append(f"{m['key']}: unknown target project {tp}")
    elif m['milestone'] not in proj_ms[tp]:
        errors.append(f"{m['key']}: milestone '{m['milestone']}' not in {tp}: {sorted(proj_ms[tp])}")
    if not (2500 <= len(m['description']) <= 8500):
        errors.append(f"{m['key']}: description length {len(m['description'])}")
    cross.append(m)
    all_new_keys.add(m['key'])

# reference checks
def check_refs(m):
    for f in ('blockedBy', 'blocks'):
        for ref in m[f]:
            if ref.startswith('PAP-'):
                if ref not in pap_ids:
                    errors.append(f"{m['key']}: {f} references missing {ref}")
            elif ref.startswith('r4/'):
                if ref not in all_new_keys:
                    errors.append(f"{m['key']}: {f} references unknown key {ref}")
            else:
                errors.append(f"{m['key']}: odd ref {ref}")
    for ref in set(re.findall(r'PAP-\d+', m['description'])):
        if ref not in pap_ids:
            errors.append(f"{m['key']}: description cites missing {ref}")
    for ref in set(re.findall(r'r4/[a-z-]+/[a-z0-9-]+', m['description'])):
        if ref not in all_new_keys:
            errors.append(f"{m['key']}: description cites unknown key {ref}")

for P in new_projects:
    for m in P['issues']:
        check_refs(m)
    for ref in set(re.findall(r'PAP-\d+', P['content'] + P['description'])):
        if ref not in pap_ids:
            errors.append(f"project {P['key']} content cites missing {ref}")
    for ref in set(re.findall(r'r4/[a-z-]+/[a-z0-9-]+', P['content'])):
        if ref not in all_new_keys:
            errors.append(f"project {P['key']} content cites unknown key {ref}")
for m in cross:
    check_refs(m)
for row in CAPMAP:
    for ref in row['coveredBy']:
        if ref not in pap_ids:
            errors.append(f"capmap '{row['capability']}': missing {ref}")
    if row['home'] not in existing_keys and row['home'] not in {p['key'] for p in new_projects}:
        errors.append(f"capmap '{row['capability']}': unknown home {row['home']}")
    if row['status'] not in ('covered', 'partial', 'gap'):
        errors.append(f"capmap '{row['capability']}': bad status")
    for ref in set(re.findall(r'r4/[a-z-]+/[a-z0-9-]+', row['note'])):
        if ref not in all_new_keys:
            errors.append(f"capmap '{row['capability']}': note cites unknown key {ref}")

# duplicate keys / titles
keys = [m['key'] for P in new_projects for m in P['issues']] + [m['key'] for m in cross]
dups = [k for k, n in collections.Counter(keys).items() if n > 1]
if dups:
    errors.append(f"duplicate keys {dups}")

if errors:
    print('\n'.join(errors))
    sys.exit(1)

out = {'capabilityMap': CAPMAP, 'newProjects': new_projects, 'crossProjectSuggestions': cross}
json.dump(out, open(OUT_JSON, 'w'), indent=1, ensure_ascii=False)
json.load(open(OUT_JSON))

# ---- digest ----
status_counts = collections.Counter(r['status'] for r in CAPMAP)
groups = collections.OrderedDict()
for r in CAPMAP:
    groups.setdefault(r['group'], []).append(r)

L = []
L.append('# Round 4 cross-cutting analysis: platform capability map and new projects')
L.append('')
L.append(f"Source: live Linear inventory ({inv['fetchedAt']}, 18 projects, {len(pap_ids)} issues), `docs/blueprint.md`, `docs/module-system.md`, Justin\'s brief. Output data: `plan/round4/gaps/cross-cutting.json`.")
L.append('')
L.append(f"**Capability map:** {len(CAPMAP)} capabilities across {len(groups)} areas: {status_counts['covered']} covered, {status_counts['partial']} partial, {status_counts['gap']} gap. Gaps and partials resolve to {len(new_projects)} proposed projects ({sum(len(p['issues']) for p in new_projects)} issues) and {len(cross)} cross-project suggestions for existing projects.")
L.append('')
L.append('## What the plan was missing at platform level')
L.append('')
summary = [
 "1. **Nobody can talk to the product.** The roster builds PaperOS with agents, but no tenant, staff member or customer can ask the app a question, get a cited answer, or have it draft or act. The assistant project adds grounded chat, copilots, actions with confirmation and tenant-configurable business characters.",
 "2. **Processes stop at one table.** Automations (PAP-174) are single-table reactions; five issues each hand-roll an approval step. There is no workflow engine, approvals framework or task inbox, so \"expense over $500 needs a manager\" has no home.",
 "3. **Forms, documents and signatures are invoices only.** A single-page form view and a Webflow embed cannot run intake, registration or paid forms; document generation exists only for invoices; nothing signs anything.",
 "4. **The customer is won and then forgotten.** Growth acquires; nothing books appointments, texts back, publishes a help center, asks for NPS or reviews, runs memberships or rewards loyalty. Cal.com and Formbricks were spiked and dropped.",
 "5. **Finance has no operations under it.** The ledger, invoices and payroll are there; products, stock, orders, POS, purchasing, projects and time, HR shifts, assets and work orders, customer subscriptions and marketplaces are not, so the five business packs stay shallow and eleven business types in the brief have no pack.",
 "6. **PaperOS has no console for PaperOS.** Tenants get PAP-63; the platform gets nothing: no tenant list, overrides, per-tenant flag rules, DLQ, health scores, status page or incident comms.",
 "7. **Compliance is implemented but unmapped.** Twenty security issues exist and no document says which SOC 2, GDPR or HIPAA control they satisfy, no evidence is collected, no HIPAA mode exists for a clinic tenant, and there is no trust center.",
 "8. **Product analytics, replay and experiments are missing** beyond acquisition attribution and traces, so nobody will know what users do after signup or which variant of a flag worked.",
 "9. **Small shared engines were never owned:** recurrence (five consumers), FX conversion, file scanning and previews, SMS as a notification channel, labels and barcodes, geocoding, scheduled report delivery, settings registry, OAuth apps for third parties, bulk campaigns and bank reconciliation are filed as cross-project suggestions.",
]
_tot = sum(len(P['issues']) for P in new_projects)
_live = sum(1 for P in new_projects for i in P['issues'] if not i['deferred'])
summary.append(f"10. **Honest phasing:** 13 days remain. Of the {_tot} new-project issues, {_live} are not deferred (contract publishes, keystone model specs, approvals framework and task inbox, retrieval and chat panel, booking engine, catalog and inventory, super-admin console, status page, control mapping); {_tot - _live} are `deferred: true` for v0.2 at priority 4 but fully specified so the plan is complete.")
L += summary
L.append('')
L.append('## Capability map')
L.append('')
for g, rows in groups.items():
    c = collections.Counter(r['status'] for r in rows)
    L.append(f"### {g} ({c['covered']} covered, {c['partial']} partial, {c['gap']} gap)")
    L.append('')
    L.append('| Capability | Covered by | Status | Home | Note |')
    L.append('|---|---|---|---|---|')
    for r in rows:
        cov = ', '.join(r['coveredBy']) if r['coveredBy'] else '—'
        L.append(f"| {r['capability']} | {cov} | {r['status']} | `{r['home']}` | {r['note']} |")
    L.append('')

L.append('## Proposed new projects')
L.append('')
for P in new_projects:
    n_def = sum(1 for i in P['issues'] if i['deferred'])
    est = sum(i['estimate'] for i in P['issues'])
    L.append(f"### {P['name']} (`{P['key']}`)")
    L.append('')
    L.append(f"Lead: {P['lead']}. Phase: {P['phase']}. Module: `@paperos/contract-{P['key']}`. Issues: {len(P['issues'])} ({len(P['issues']) - n_def} live, {n_def} deferred v0.2), {est} points.")
    L.append('')
    L.append(P['description'])
    L.append('')
    L.append('Milestones: ' + '; '.join(f"{m['name']} ({m['targetDate']})" for m in P['milestones']) + '.')
    L.append('')
    L.append('| Key | Title | Type | Model / effort | Size | Pri | Deferred | Milestone |')
    L.append('|---|---|---|---|---|---|---|---|')
    for i in P['issues']:
        L.append(f"| `{i['key']}` | {i['title']} | {i['type']} | {i['model']} / {i['effort']} | {i['size']} | P{i['priority']} | {'yes' if i['deferred'] else 'no'} | {i['milestone']} |")
    L.append('')

L.append('## Cross-project suggestions (gaps that belong in existing projects)')
L.append('')
L.append('| Key | Target | Title | Model / effort | Size | Pri | Deferred | Milestone |')
L.append('|---|---|---|---|---|---|---|---|')
for m in cross:
    L.append(f"| `{m['key']}` | `{m['targetProject']}` | {m['title']} | {m['model']} / {m['effort']} | {m['size']} | P{m['priority']} | {'yes' if m['deferred'] else 'no'} | {m['milestone']} |")
L.append('')
L.append('## Method')
L.append('')
L.append('Every capability was checked against issue titles and full descriptions in the live inventory (keyword search plus reading the Goal and Scope of the partially covering issues). `covered` means an existing issue owns the capability end to end (deferred issues count as covered because they are fully specified); `partial` means a piece exists but the capability as a business would recognise it does not; `gap` means nothing owns it. Every new issue follows the canonical spec format (PAP-342), cites only identifiers that exist in the inventory, includes the module trio required by `docs/module-system.md`, and uses the model rule: Sonnet 5 / medium by default, Opus 5 / high for security-sensitive, money-moving or widely consumed pieces, Fable 5.1 / max for the three keystone model specs, Haiku 4.5 unused this round (no mechanical docs). Estimates S=2, M=3, L=5. Milestones after 2026-10-01 are marked deferred (v0.2) in their descriptions.')
L.append('')
open(OUT_MD, 'w').write('\n'.join(L))

# report
print('OK')
print('capabilities', len(CAPMAP), dict(status_counts))
for P in new_projects:
    n_def = sum(1 for i in P['issues'] if i['deferred'])
    print(P['key'], len(P['issues']), 'issues,', n_def, 'deferred,', sum(i['estimate'] for i in P['issues']), 'pts')
print('cross', len(cross), 'deferred', sum(1 for m in cross if m['deferred']))
tot = sum(len(P['issues']) for P in new_projects)
print('total new issues', tot, 'not deferred', sum(1 for P in new_projects for i in P['issues'] if not i['deferred']))
lens = [len(i['description']) for P in new_projects for i in P['issues']] + [len(m['description']) for m in cross]
print('desc len min/median/max', min(lens), sorted(lens)[len(lens)//2], max(lens))
import os
print('json bytes', os.path.getsize(OUT_JSON), 'md bytes', os.path.getsize(OUT_MD))
models = collections.Counter(i['model'] for P in new_projects for i in P['issues'])
print('models', dict(models))
