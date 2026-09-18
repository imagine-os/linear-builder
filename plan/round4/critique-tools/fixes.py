#!/usr/bin/env python3
"""Round 4 critique step 5: mechanical fixes. Usage: fixes.py [--apply]. Without --apply prints the plan only.
Mutations: issueUpdate (description, milestone, dueDate), issueRelationCreate. Never deletes or archives; never touches PAP-1..12.
Log: plan/round4/changes/critique-fixes.json."""
import json, os, sys, re, time, collections, urllib.request, urllib.error, datetime
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, "..")
SNAP = json.load(open(os.path.join(ROOT, "critique-snapshot.json"))); I = SNAP['issues']; by = {i['identifier']: i for i in I}
IDS = json.load(open(os.path.join(ROOT, "r4-ids.json"))); key2id = {k: v['identifier'] for k, v in IDS.items()}
key2id.update({"r4/business-core/fx-rates": "PAP-766", "r4/growth/bulk-campaigns": "PAP-799", "r4/data-layer/file-scanning-previews": "PAP-574",
               "r4/tables/scheduled-view-delivery": "PAP-639", "r4/business-core/bank-feeds-reconciliation": "PAP-770", "r4/tables/address-geo-field": "PAP-622"})
APPLY = '--apply' in sys.argv
URL = "https://api.linear.app/graphql"; KEY = os.environ.get("LINEAR_API_KEY") or "placeholder"
MARK = "_Round 4 critique fix (2026-09-18):_"
LOG = os.path.join(ROOT, "changes", "critique-fixes.json")
log = json.load(open(LOG)) if os.path.exists(LOG) else {"startedAt": None, "mutations": [], "skipped": []}

def gql(query, variables=None, retries=6):
    body = json.dumps({"query": query, "variables": variables or {}}).encode()
    for attempt in range(retries):
        req = urllib.request.Request(URL, data=body, headers={"Authorization": KEY, "Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=120) as r: data = json.loads(r.read().decode())
        except urllib.error.HTTPError as e:
            raw = e.read().decode()
            try: data = json.loads(raw)
            except Exception: data = {"errors": [{"message": "HTTP %s %s" % (e.code, raw[:300])}]}
            if e.code == 429: time.sleep(60); continue
        except Exception as e:
            print("retry after", repr(e)[:200], file=sys.stderr); time.sleep(5); continue
        errs = data.get("errors")
        if errs:
            codes = [(x.get("extensions") or {}).get("code") for x in errs]
            if "RATELIMITED" in codes: print("rate limited, sleeping 60 s", file=sys.stderr); time.sleep(60); continue
            return {"__errors": errs, **(data.get("data") or {})}
        return data["data"]
    raise RuntimeError("retries exhausted")

def has(i, n): return any(l['name'] == n for l in i['labels'])
def deps_text(i):
    m = re.search(r'\*\*Dependencies\*\*\s*\n(.*?)(?=\n\*\*[A-Z][^*\n]*\*\*\s*\n|\Z)', i['description'], re.S); return m.group(1) if m else ''
KEYRE = re.compile(r'`?(r4/[a-z0-9-]+/[a-z0-9-]+)`?')
def resolve(t): return KEYRE.sub(lambda m: key2id.get(m.group(1), m.group(1)), t)

# --- graph helpers -------------------------------------------------------------------------------
adj = collections.defaultdict(set)
for i in I:
    for r in i['relations']:
        if r['type'] == 'blocks' and r['to'] in by: adj[i['identifier']].add(r['to'])
def reaches(src, dst):
    seen = {src}; st = [src]
    while st:
        n = st.pop()
        if n == dst: return True
        for v in adj[n]:
            if v not in seen: seen.add(v); st.append(v)
    return False
OPEN = {"Backlog", "Todo", "Ready for Claude", "In Progress", "Needs Justin", "Triage"}
def safe_edge(b, i):
    """Return None if B blocks I may be added, else a reason string."""
    B, X = by[b], by[i]
    if b == i: return "self"
    if i in adj[b]: return "exists"
    if has(B, 'Deferred') and not has(X, 'Deferred'): return "deferred blocker -> scheduled"
    if B['milestoneDate'] and X['milestoneDate'] and B['milestoneDate'] > X['milestoneDate']: return "milestone inversion %s > %s" % (B['milestoneDate'], X['milestoneDate'])
    if B['dueDate'] and X['dueDate'] and B['dueDate'] > X['dueDate']: return "dueDate inversion %s > %s" % (B['dueDate'], X['dueDate'])
    if X['state'] == 'Ready for Claude' and B['state'] in OPEN: return "would block a Ready issue"
    if B['parent'] == i or X['parent'] == b: return "parent/child"
    if reaches(i, b): return "cycle"
    return None

# --- plan ----------------------------------------------------------------------------------------
notes = collections.defaultdict(list)   # identifier -> list of note strings appended under MARK
rels = []                               # (blocker, blocked, reason-tag)
skipped = []
# F-B: hard-dependency drift -> relations
def hard_ids(t):
    """PAP ids the Dependencies text marks as hard. Handles 'Hard: A, B.', 'Blocked by A and B (hard)', 'A, B, C (hard)' and 'A (hard), B, C'."""
    hard = set()
    for sent in re.split(r'(?<=[.;])\s+|\n', t):
        sent = sent.strip()
        if not sent or re.search(r'\bsoft\b|not a `?blocks|soft dependency|^None hard', sent, re.I): continue
        def ids(seg):
            if re.search(r'\bor\b', seg): return []  # 'PAP-30 or PAP-42' is an alternative, not a hard blocker
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
def hard_missing(i):
    t = resolve(deps_text(i)); rel = {r['to'] for r in i['relations']} | {r['from'] for r in i['inverseRelations']} | {i['parent']} | set(i['children'])
    hard = hard_ids(t); soft = soft_ids(t)
    return sorted(x for x in hard - rel - soft if x in by and x != i['identifier']), sorted(x for x in (hard & soft) - rel if x in by)
for i in I:
    if i['state'] == 'Triage': continue
    miss, contra = hard_missing(i)
    for b in miss:
        why = safe_edge(b, i['identifier'])
        if why is None:
            rels.append((b, i['identifier'], "text-hard-dep")); adj[b].add(i['identifier'])
        else:
            skipped.append({"blocker": b, "blocked": i['identifier'], "reason": why, "fix": "text-hard-dep"})
            if why not in ("exists", "self", "parent/child"):
                notes[i['identifier']].append("%s is named as a hard dependency above but stays a soft dependency (no `blocks` relation): %s. Start when it is In Review or work against its contract and leave a TODO naming it." % (b, why))
    for b in contra:
        notes[i['identifier']].append("%s appears in the Hard list above and in a round-4 soft note; it is soft (no `blocks` relation). Read the Hard list without it." % b)
# F-E: umbrella outbound propagation (last non-deferred child blocks the umbrella's dependents)
umbs = [u for u in I if u['children'] and u['state'] != 'Triage']
outbound_plan = []  # brief only (FIX-R4): not applied
for u in umbs:
    kids = [by[c] for c in u['children'] if c in by and not has(by[c], 'Deferred')]
    if not kids: continue
    last = max(kids, key=lambda k: ((k['dueDate'] or ''), k['number']))
    for dst in sorted(adj[u['identifier']]):
        if dst in u['children']: continue
        if any(dst in adj[k['identifier']] for k in kids): continue
        why = safe_edge(last['identifier'], dst)
        outbound_plan.append({"umbrella": u['identifier'], "lastChild": last['identifier'], "blocked": dst, "safe": why is None, "reason": why, "new": u['number'] < 498 and all(by[c]['number'] >= 498 for c in u['children'] if c in by)})
# F-A: key resolution in descriptions
keyfix = {}
for i in I:
    ks = sorted(set(KEYRE.findall(i['description'])))
    if ks: keyfix[i['identifier']] = ks
# F-F: triage duplicate note
notes['PAP-950'].append("overlaps PAP-70 (which already ships `SplitPane` in the layout components). If promoted, scope this issue to the `Tabs` workspace (multi-document tabs) and persisted split ratios only, and depend on PAP-70.")
# F-D: milestone/dueDate fixes
field_updates = [
    ("PAP-636", {"projectMilestoneId": by['PAP-170']['milestoneId']}, "child milestone -> parent PAP-170 milestone 'All view types' (deferred child, no dueDate)"),
    ("PAP-627", {"projectMilestoneId": by['PAP-164']['milestoneId'], "dueDate": "2026-09-28"}, "child milestone -> parent PAP-164 milestone 'Grid with sort, filter, group'; dueDate 09-29 -> 09-28 (all 7 blockers due <= 09-28; dependents due 09-29+); also repairs umbrella PAP-164 due < last child due"),
]
notes['PAP-627'].append("moved to the parent's milestone (Grid with sort, filter, group) and dueDate 2026-09-28 so the umbrella PAP-164 closes with its last child.")
desc_targets = sorted(set(keyfix) | set(notes), key=lambda x: int(x.split('-')[1]))
print("umbrella outbound (brief only):", len(outbound_plan), "safe", sum(1 for o in outbound_plan if o["safe"]), "new umbrellas", sum(1 for o in outbound_plan if o["new"]))
print("plan: descriptions %d (key resolution %d, notes %d), relations %d (text-hard-dep %d, umbrella-outbound %d), field updates %d, skipped %d" % (
    len(desc_targets), len(keyfix), len(notes), len(rels), sum(1 for r in rels if r[2] == 'text-hard-dep'), sum(1 for r in rels if r[2].startswith('umbrella')), len(field_updates), len(skipped)))
print(collections.Counter(s['reason'].split(' ')[0] for s in skipped))
if not APPLY:
    for r in rels[:15]: print("  rel", r)
    for s in skipped[:40]: print("  skip", s)
    json.dump({"rels": rels, "skipped": skipped, "outbound_plan": outbound_plan, "desc_targets": desc_targets, "notes": notes, "field_updates": field_updates}, open(os.path.join(HERE, "fix-plan.json"), "w"), indent=1)
    sys.exit(0)

# --- apply ---------------------------------------------------------------------------------------
log["startedAt"] = log["startedAt"] or datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
done_desc = {m['identifier'] for m in log['mutations'] if m['kind'] == 'description' and m.get('ok')}
done_rel = {(m['blocker'], m['blocked']) for m in log['mutations'] if m['kind'] == 'relation' and m.get('ok')}
done_field = {m['identifier'] for m in log['mutations'] if m['kind'] == 'fields' and m.get('ok')}
def save(): json.dump(log, open(LOG, "w"), indent=1)
def run_batch(parts, vars_, entries):
    q = ("mutation(" + ", ".join("$%s: %s" % (k, t) for k, (t, _) in vars_.items()) + ")" if vars_ else "mutation") + " { " + " ".join(parts) + " }"
    data = gql(q, {k: v for k, (_, v) in vars_.items()})
    errs = data.get("__errors") or []
    for e in entries:
        node = data.get(e['alias']) or {}
        e['ok'] = bool(node.get('success')); e['at'] = datetime.datetime.now(datetime.timezone.utc).strftime("%H:%M:%SZ")
        if not e['ok']: e['error'] = [x.get('message') for x in errs if e['alias'] in str(x.get('path', ''))] or [x.get('message') for x in errs][:2]
        if e['kind'] == 'relation' and node.get('issueRelation'): e['relationId'] = node['issueRelation']['id']
        log['mutations'].append(e)
    save(); time.sleep(0.3)
    return sum(1 for e in entries if e['ok'])

# 1. descriptions: refetch fresh text, transform, update
targets = [t for t in desc_targets if t not in done_desc]
fresh = {}
for k in range(0, len(targets), 25):
    chunk = [by[t]['id'] for t in targets[k:k+25]]
    d = gql("query($ids: [ID!]!) { issues(filter: {id: {in: $ids}}, first: 25) { nodes { id identifier description } } }", {"ids": chunk})
    for n in d['issues']['nodes']: fresh[n['identifier']] = n['description'] or ''
    time.sleep(0.3)
ok = 0; batch_parts = []; batch_vars = {}; batch_entries = []
for t in targets:
    old = fresh.get(t, by[t]['description']); new = old
    ks = sorted(set(KEYRE.findall(new))); lines = []
    if ks:
        new = resolve(new)
        lines.append("resolved %d round-4 file key%s in this description to Linear identifiers: %s." % (len(ks), "s" if len(ks) != 1 else "", ", ".join("`%s` = %s" % (k, key2id.get(k, "unresolved")) for k in ks)))
    for n in notes.get(t, []):
        if n not in new: lines.append(n)
    if not lines: continue
    new = new.rstrip() + "\n\n" + "\n".join("%s %s" % (MARK, l) for l in lines) + "\n"
    a = "d%d" % len(batch_parts)
    batch_parts.append('%s: issueUpdate(id: "%s", input: {description: $%s}) { success }' % (a, by[t]['id'], a))
    batch_vars[a] = ("String!", new)
    batch_entries.append({"kind": "description", "identifier": t, "alias": a, "keys": ks, "notes": len(notes.get(t, [])), "oldLen": len(old), "newLen": len(new)})
    if len(batch_parts) == 10:
        ok += run_batch(batch_parts, batch_vars, batch_entries); batch_parts, batch_vars, batch_entries = [], {}, []
if batch_parts: ok += run_batch(batch_parts, batch_vars, batch_entries)
print("descriptions updated", ok)
# 2. relations
ok = 0; batch_parts = []; batch_vars = {}; batch_entries = []
for b, x, tag in rels:
    if (b, x) in done_rel: continue
    a = "r%d" % len(batch_parts)
    batch_parts.append('%s: issueRelationCreate(input: {issueId: "%s", relatedIssueId: "%s", type: blocks}) { success issueRelation { id } }' % (a, by[b]['id'], by[x]['id']))
    batch_entries.append({"kind": "relation", "blocker": b, "blocked": x, "alias": a, "fix": tag})
    if len(batch_parts) == 10:
        ok += run_batch(batch_parts, batch_vars, batch_entries); batch_parts, batch_vars, batch_entries = [], {}, []
if batch_parts: ok += run_batch(batch_parts, batch_vars, batch_entries)
print("relations created", ok)
# 3. field updates
batch_parts = []; batch_vars = {}; batch_entries = []
for t, inp, why in field_updates:
    if t in done_field: continue
    a = "f%d" % len(batch_parts)
    batch_parts.append('%s: issueUpdate(id: "%s", input: $%s) { success }' % (a, by[t]['id'], a)); batch_vars[a] = ("IssueUpdateInput!", inp)
    batch_entries.append({"kind": "fields", "identifier": t, "alias": a, "input": inp, "why": why})
if batch_parts: print("fields updated", run_batch(batch_parts, batch_vars, batch_entries))
log['skipped'] = skipped; log['finishedAt'] = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"); save()
print("failures:", [m for m in log['mutations'] if not m.get('ok')][:10])
