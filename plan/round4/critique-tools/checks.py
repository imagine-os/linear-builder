#!/usr/bin/env python3
"""Round 4 critique step 2: integrity checks over critique-snapshot.json. Prints a markdown summary and writes
<snapshot>-checks.json. Usage: checks.py [snapshot.json] [--seed N]"""
import json, sys, re, random, collections, difflib, os
HERE = os.path.dirname(os.path.abspath(__file__))
SNAP = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith('--') else os.path.join(HERE, "..", "critique-snapshot.json")
SEED = 4
if '--seed' in sys.argv: SEED = int(sys.argv[sys.argv.index('--seed')+1])
d = json.load(open(SNAP)); I = d['issues']
by = {i['identifier']: i for i in I}
NEW_PROJECTS = {"Tenant AI Assistant & Business Agents", "Workflows, Approvals, Forms, Documents & E-Signature",
  "Scheduling, Messaging & Customer Engagement", "Commerce, Operations & Vertical Packs", "Platform Operations, Analytics & Compliance"}
SECTIONS = ["Goal", "Scope", "Spec", "Interface contract", "Test plan", "Definition of done", "Edge cases", "Dependencies", "Agent", "Size", "Demo"]
OPEN_STATES = {"Backlog", "Todo", "Ready for Claude", "In Progress", "Needs Justin", "Triage"}
res = {}; counts = {}
def lab(i, group): return [l['name'] for l in i['labels'] if l['group'] == group]
def has(i, name): return any(l['name'] == name for l in i['labels'])
def is_umb(i): return len(i['children']) > 0
def is_triage(i): return i['state'] == 'Triage'
spec = [i for i in I if not is_triage(i)]
leaves = [i for i in spec if not is_umb(i)]
umbs = [i for i in spec if is_umb(i)]
blocks = [(i['identifier'], r['to']) for i in I for r in i['relations'] if r['type'] == 'blocks']

# 1 duplicate titles within a project
seen = collections.defaultdict(list)
for i in I: seen[(i['project'], i['title'].strip().lower())].append(i['identifier'])
res['dup_titles'] = [v for v in seen.values() if len(v) > 1]
# 2 relation to missing issue
res['rel_missing'] = [(i['identifier'], r['type'], r['to']) for i in I for r in i['relations'] if r['to'] is None or r['to'] not in by]
res['rel_missing'] += [(r['from'], r['type'], i['identifier']) for i in I for r in i['inverseRelations'] if r['from'] is None or r['from'] not in by]
# 3 orphan child
res['orphan_child'] = [i['identifier'] for i in I if i['parent'] and i['parent'] not in by]
# 4 child project/milestone mismatch
res['child_project_mismatch'] = [(i['identifier'], i['parent']) for i in I if i['parent'] in by and by[i['parent']]['project'] != i['project']]
res['child_milestone_mismatch'] = [(i['identifier'], i['milestone'], i['parent'], by[i['parent']]['milestone']) for i in I if i['parent'] in by and by[i['parent']]['milestone'] != i['milestone']]
# 5 labels
res['leaf_missing_labels'] = [(i['identifier'], [g for g in ("Phase", "Type", "Model", "Reasoning effort") if not lab(i, g)]) for i in leaves if any(not lab(i, g) for g in ("Phase", "Type", "Model", "Reasoning effort"))]
res['umbrella_with_model_effort'] = [(i['identifier'], lab(i, "Model") + lab(i, "Reasoning effort")) for i in umbs if lab(i, "Model") or lab(i, "Reasoning effort")]
res['umbrella_with_estimate'] = [(i['identifier'], i['estimate']) for i in umbs if i['estimate'] is not None]
res['leaf_no_surface'] = [i['identifier'] for i in leaves if len(lab(i, "Surface")) != 1]
# 6 estimate; 7 dueDate
res['leaf_no_estimate'] = [i['identifier'] for i in leaves if i['estimate'] is None]
res['leaf_no_duedate'] = [i['identifier'] for i in leaves if not has(i, 'Deferred') and not i['dueDate']]
res['deferred_with_duedate'] = [i['identifier'] for i in leaves if has(i, 'Deferred') and i['dueDate']]
res['deferred_not_p4'] = [(i['identifier'], i['priority']) for i in spec if has(i, 'Deferred') and i['priority'] != 4]
# 8 Ready hygiene
ready = [i for i in I if i['state'] == 'Ready for Claude']
def open_blockers(i): return [r['from'] for r in i['inverseRelations'] if r['type'] == 'blocks' and r['from'] in by and by[r['from']]['state'] in OPEN_STATES]
res['ready_blocked'] = [(i['identifier'], open_blockers(i)) for i in ready if open_blockers(i)]
res['ready_umbrella'] = [i['identifier'] for i in ready if is_umb(i)]
res['ready_deferred'] = [i['identifier'] for i in ready if has(i, 'Deferred')]
res['ready_no_cycle'] = [i['identifier'] for i in ready if not i['cycle']]
res['backlog_with_cycle'] = [i['identifier'] for i in I if i['state'] == 'Backlog' and i['cycle']]
# promotable: Backlog leaf, no open blockers, no Deferred, not umbrella, not Triage
res['backlog_promotable'] = [i['identifier'] for i in leaves if i['state'] == 'Backlog' and not has(i, 'Deferred') and not open_blockers(i) and not i['parent']]
res['backlog_promotable_children'] = [i['identifier'] for i in leaves if i['state'] == 'Backlog' and not has(i, 'Deferred') and not open_blockers(i) and i['parent']]
# 9 deferred -> scheduled
res['deferred_blocks_scheduled'] = [(a, b) for a, b in blocks if a in by and b in by and has(by[a], 'Deferred') and not has(by[b], 'Deferred') and not is_triage(by[b])]
# 10 milestone inversions
res['milestone_inversions'] = [(a, by[a]['milestoneDate'], b, by[b]['milestoneDate']) for a, b in blocks if a in by and b in by and by[a]['milestoneDate'] and by[b]['milestoneDate'] and by[a]['milestoneDate'] > by[b]['milestoneDate']]
# dueDate inversions (leaf-level): blocker due after blocked due
res['duedate_inversions'] = [(a, by[a]['dueDate'], b, by[b]['dueDate']) for a, b in blocks if a in by and b in by and by[a]['dueDate'] and by[b]['dueDate'] and by[a]['dueDate'] > by[b]['dueDate']]
# 11 cycles
adj = collections.defaultdict(list)
for a, b in blocks:
    if a in by and b in by: adj[a].append(b)
color = {}; cyc = []
def dfs(u, stack):
    color[u] = 1; stack.append(u)
    for v in adj[u]:
        if color.get(v, 0) == 0: dfs(v, stack)
        elif color[v] == 1: cyc.append(stack[stack.index(v):] + [v])
    stack.pop(); color[u] = 2
sys.setrecursionlimit(10000)
for n in by:
    if color.get(n, 0) == 0: dfs(n, [])
res['cycles'] = cyc[:20]; counts['cycles'] = len(cyc)
# 12 description sections
def missing_sections(i):
    t = i['description']; miss = [s for s in SECTIONS if not re.search(r'(^|\n)\**#*\s*\**' + re.escape(s) + r'\**\s*(\n|:)', t)]
    if not re.search(r'\*\*Model / Effort:\*\*', t): miss.append('Model / Effort line')
    return miss
res['desc_missing_sections'] = [(i['identifier'], missing_sections(i)) for i in spec if missing_sections(i)]
res['umbrella_missing_model_effort_line'] = [i['identifier'] for i in umbs if 'Model / Effort line' in missing_sections(i)]
# 13 text/graph drift in Dependencies
def deps_text(i):
    m = re.search(r'\*\*Dependencies\*\*\s*\n(.*?)(?=\n\*\*[A-Z][^*\n]*\*\*\s*\n|\Z)', i['description'], re.S)
    return m.group(1) if m else ''
def drift(i):
    txt = deps_text(i)
    if not txt: return None
    named = set(re.findall(r'PAP-\d+', txt)); rel = {r['to'] for r in i['relations']} | {r['from'] for r in i['inverseRelations']} | ({i['parent']} if i['parent'] else set()) | set(i['children'])
    # soft dependencies are expected to have no relation
    soft = set()
    for m in re.finditer(r'(PAP-\d+)[^.\n]{0,40}?\bsoft\b|\bsoft\b[^.\n]{0,60}?(PAP-\d+)', txt, re.I):
        soft.update(x for x in m.groups() if x)
    for line in txt.split('\n'):
        if re.search(r'\bsoft\b', line, re.I) or re.search(r'not a blocker|no relation|may start|branch-start|informational|see also|related:|consumes later|deferred', line, re.I):
            soft.update(re.findall(r'PAP-\d+', line))
    hard_missing = sorted(x for x in named - rel - soft - {i['identifier']} if x in by)
    return hard_missing
random.seed(SEED)
new = [i for i in spec if i['number'] >= 498]
old = [i for i in spec if i['number'] < 498]
sample_old = random.sample(old, min(100, len(old)))
res['drift_new'] = [(i['identifier'], drift(i)) for i in new if drift(i)]
res['drift_old_sample'] = [(i['identifier'], drift(i)) for i in sample_old if drift(i)]
res['drift_old_sample_ids'] = [i['identifier'] for i in sample_old]
counts['drift_new_checked'] = len(new); counts['drift_old_checked'] = len(sample_old)
# 15 new umbrellas: parent < 498 with children >= 498; inbound blockers propagated to a child?
def inbound(i): return [r['from'] for r in i['inverseRelations'] if r['type'] == 'blocks' and r['from'] in by]
def outbound(i): return [r['to'] for r in i['relations'] if r['type'] == 'blocks' and r['to'] in by]
new_umbs = [u for u in umbs if u['number'] < 498 and any(by[c]['number'] >= 498 for c in u['children'] if c in by)]
res['new_umbrellas'] = [u['identifier'] for u in new_umbs]
prop = []
for u in new_umbs:
    kids = [c for c in u['children'] if c in by]
    for b in inbound(u):
        if b in kids: continue
        if not any(b in inbound(by[c]) for c in kids): prop.append((u['identifier'], b))
res['new_umbrella_unpropagated_inbound'] = prop
propo = []
for u in new_umbs:
    kids = [c for c in u['children'] if c in by]
    for dst in outbound(u):
        if dst in kids: continue
        if not any(dst in outbound(by[c]) for c in kids): propo.append((u['identifier'], dst))
res['new_umbrella_unpropagated_outbound'] = propo
# all umbrellas: children with no external inbound blocker at all (neither own nor inherited) and no sibling blocker
res['children_no_blockers'] = [c['identifier'] for c in leaves if c['parent'] and not inbound(c)]
# 16 new projects: issues with no inbound blocks
res['newproj_no_deps'] = [(i['identifier'], i['project']) for i in spec if i['project'] in NEW_PROJECTS and not inbound(i)]
# 17 triage duplicates
def norm(t): return re.sub(r'[^a-z0-9 ]', ' ', t.lower())
tri = [i for i in I if is_triage(i)]
spec_titles = [(norm(i['title']), i['identifier']) for i in spec]
tdup = []
for t in tri:
    nt = norm(t['title']); tw = set(nt.split())
    best = (0, None)
    for st, sid in spec_titles:
        sw = set(st.split()); j = len(tw & sw) / max(1, len(tw | sw))
        r = difflib.SequenceMatcher(None, nt, st).ratio()
        sc = max(j, r)
        if sc > best[0]: best = (sc, sid)
    if best[0] >= 0.5: tdup.append((t['identifier'], best[1], round(best[0], 2), t['title'][:80], by[best[1]]['title'][:80]))
res['triage_dups'] = tdup

# 13b refined hard-dependency drift (same parser as fixes.py), all specified issues, keys resolved first
IDS = json.load(open(os.path.join(HERE, "..", "r4-ids.json"))); key2id = {k: v['identifier'] for k, v in IDS.items()}
key2id.update({"r4/business-core/fx-rates": "PAP-766", "r4/growth/bulk-campaigns": "PAP-799", "r4/data-layer/file-scanning-previews": "PAP-574",
               "r4/tables/scheduled-view-delivery": "PAP-639", "r4/business-core/bank-feeds-reconciliation": "PAP-770", "r4/tables/address-geo-field": "PAP-622"})
KEYRE = re.compile(r'`?(r4/[a-z0-9-]+/[a-z0-9-]+)`?')
def resolve(t): return KEYRE.sub(lambda m: key2id.get(m.group(1), m.group(1)), t)
def hard_ids(t):
    hard = set()
    for sent in re.split(r'(?<=[.;])\s+|\n', t):
        sent = sent.strip()
        if not sent or re.search(r'\bsoft\b|not a `?blocks|soft dependency|^None hard', sent, re.I): continue
        def ids(seg):
            if re.search(r'\bor\b', seg): return []
            return [m.group(1) for m in re.finditer(r'(PAP-\d+)((\s+\w+)?\s+(child|children)\b)?', seg) if not m.group(2)]
        if re.match(r'\*?\*?Hard\*?\*?:', sent, re.I) or re.match(r'Blocked by\b', sent, re.I):
            hard.update(ids(sent)); continue
        if not re.search(r'\(hard|hard\)|\bhard\b', sent, re.I): continue
        items = [x.strip() for x in re.split(r',|\band\b', sent) if x.strip()]
        hard_items = [x for x in items if re.search(r'\bhard\b', x, re.I)]
        if len(hard_items) == 1 and items and items[-1] is hard_items[0] and not any('(' in x for x in items[:-1]):
            for x in items: hard.update(ids(x))
        else:
            for x in hard_items: hard.update(ids(x))
    return hard
def soft_ids(t):
    soft = set()
    for sent in re.split(r'(?<=[.;])\s+|\n', t):
        if re.search(r'\bsoft\b', sent, re.I): soft.update(re.findall(r'PAP-\d+', sent))
    return soft
def hard_drift(i):
    t = resolve(deps_text(i)); rel = {r['to'] for r in i['relations']} | {r['from'] for r in i['inverseRelations']} | {i['parent']} | set(i['children'])
    # a critique note declaring X soft removes it from the hard set
    for m in re.finditer(r'Round 4 critique fix \(2026-09-18\):\*?_? (PAP-\d+) (is named as a hard dependency|appears in the Hard list)', i['description']): rel.add(m.group(1))
    return sorted(x for x in hard_ids(t) - rel - soft_ids(t) if x in by and x != i['identifier'])
res['hard_drift_all'] = [(i['identifier'], hard_drift(i)) for i in spec if hard_drift(i)]
res['hard_drift_new'] = [x for x in res['hard_drift_all'] if by[x[0]]['number'] >= 498]
res['hard_drift_old'] = [x for x in res['hard_drift_all'] if by[x[0]]['number'] < 498]
# unresolved round-4 file keys outside critique marker lines
def body_keys(i): return sorted(set(KEYRE.findall("\n".join(l for l in i['description'].split("\n") if 'Round 4 critique fix' not in l))))
res['r4_keys_in_body'] = [(i['identifier'], body_keys(i)) for i in I if body_keys(i)]
res['r4_keys_unresolvable'] = sorted({k for i in I for k in body_keys(i) if k not in key2id})
# zero-inbound Backlog leaves that are not children (nothing gates them)
res['backlog_leaf_no_inbound'] = [i['identifier'] for i in leaves if i['state'] == 'Backlog' and not i['parent'] and not [r for r in i['inverseRelations'] if r['type'] == 'blocks'] and not has(i, 'Deferred')]
# umbrellas converted today whose children cover none of the parent's core (single child, parent scope broader): reported as list of single-child fresh umbrellas
fresh = [u for u in umbs if u['number'] < 498 and all(by[c]['number'] >= 498 for c in u['children'] if c in by)]
res['fresh_umbrellas'] = [(u['identifier'], len(u['children'])) for u in fresh]
res['fresh_umbrellas_single_child'] = [u['identifier'] for u in fresh if len(u['children']) == 1]
res['umbrella_due_before_last_child'] = [(u['identifier'], u['dueDate'], max((by[c]['dueDate'] or '' for c in u['children'] if c in by), default='')) for u in umbs if u['dueDate'] and any(by[c]['dueDate'] and by[c]['dueDate'] > u['dueDate'] for c in u['children'] if c in by)]
# state facts
counts.update({'issues': len(I), 'specified': len(spec), 'leaves': len(leaves), 'umbrellas': len(umbs), 'triage': len(tri), 'ready': len(ready),
  'blocks': len(blocks), 'deferred': sum(1 for i in spec if has(i, 'Deferred')), 'new_umbrellas': len(new_umbs),
  'states': dict(collections.Counter(i['state'] for i in I)), 'projects': len({i['project'] for i in I})})
for k, v in res.items():
    if isinstance(v, list): counts[k] = len(v)
out = {'snapshot': d['takenAt'], 'counts': counts, 'results': res}
json.dump(out, open(SNAP.replace('.json', '-checks.json'), 'w'), indent=1)
print("snapshot", d['takenAt']); print(json.dumps(counts, indent=1))
