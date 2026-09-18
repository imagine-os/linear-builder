#!/usr/bin/env python3
"""FIX-R4 follow-up: propagate inbound blockers of umbrellas to a child (FIX-3 rule) where the critique's new
text-hard-dep relations landed on an umbrella. Child = the one whose Dependencies text names the blocker, else the
earliest-due non-deferred child. Logs to changes/critique-fixes.json. Usage: fixes_propagate.py [--apply]"""
import json, os, sys, re, time, collections, urllib.request, urllib.error, datetime
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, "..")
sys.argv_backup = list(sys.argv); APPLY = '--apply' in sys.argv
SNAP = json.load(open(os.path.join(ROOT, "critique-snapshot.json"))); I = SNAP['issues']; by = {i['identifier']: i for i in I}
URL = "https://api.linear.app/graphql"; KEY = os.environ.get("LINEAR_API_KEY") or "placeholder"
LOG = os.path.join(ROOT, "changes", "critique-fixes.json"); log = json.load(open(LOG))
def gql(query, variables=None):
    body = json.dumps({"query": query, "variables": variables or {}}).encode()
    req = urllib.request.Request(URL, data=body, headers={"Authorization": KEY, "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=120) as r: data = json.loads(r.read().decode())
    if data.get("errors"): return {"__errors": data["errors"], **(data.get("data") or {})}
    return data["data"]
def has(i, n): return any(l['name'] == n for l in i['labels'])
def deps_text(i):
    m = re.search(r'\*\*Dependencies\*\*\s*\n(.*?)(?=\n\*\*[A-Z][^*\n]*\*\*\s*\n|\Z)', i['description'], re.S); return m.group(1) if m else ''
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
    B, X = by[b], by[i]
    if b == i: return "self"
    if i in adj[b]: return "exists"
    if has(B, 'Deferred') and not has(X, 'Deferred'): return "deferred blocker -> scheduled"
    if B['milestoneDate'] and X['milestoneDate'] and B['milestoneDate'] > X['milestoneDate']: return "milestone inversion"
    if B['dueDate'] and X['dueDate'] and B['dueDate'] > X['dueDate']: return "dueDate inversion"
    if X['state'] == 'Ready for Claude' and B['state'] in OPEN: return "would block a Ready issue"
    if reaches(i, b): return "cycle"
    return None
umbs = [u for u in I if u['children'] and u['state'] != 'Triage']
new_umbs = [u for u in umbs if u['number'] < 498 and any(by[c]['number'] >= 498 for c in u['children'] if c in by)]
plan = []
for u in new_umbs:
    kids = [by[c] for c in u['children'] if c in by]
    for b in sorted({r['from'] for r in u['inverseRelations'] if r['type'] == 'blocks' and r['from'] in by}):
        if b in u['children'] or any(b in {r['from'] for r in k['inverseRelations']} for k in kids): continue
        named = [k for k in kids if b in deps_text(k)]
        cands = named or sorted([k for k in kids if not has(k, 'Deferred')], key=lambda k: ((k['dueDate'] or '9'), k['number']))[:1]
        for k in cands:
            why = safe_edge(b, k['identifier'])
            plan.append({"umbrella": u['identifier'], "blocker": b, "child": k['identifier'], "safe": why is None, "reason": why, "named": bool(named)})
            if why is None: adj[b].add(k['identifier'])
print(json.dumps(plan, indent=0))
if not APPLY: sys.exit(0)
todo = [p for p in plan if p['safe']]
for k in range(0, len(todo), 10):
    chunk = todo[k:k+10]
    parts = ['p%d: issueRelationCreate(input: {issueId: "%s", relatedIssueId: "%s", type: blocks}) { success issueRelation { id } }' % (n, by[p['blocker']]['id'], by[p['child']]['id']) for n, p in enumerate(chunk)]
    data = gql("mutation { " + " ".join(parts) + " }")
    for n, p in enumerate(chunk):
        node = data.get("p%d" % n) or {}
        log['mutations'].append({"kind": "relation", "blocker": p['blocker'], "blocked": p['child'], "fix": "umbrella-inbound-propagation:" + p['umbrella'], "ok": bool(node.get('success')),
                                 "relationId": (node.get('issueRelation') or {}).get('id'), "at": datetime.datetime.now(datetime.timezone.utc).strftime("%H:%M:%SZ"), "error": data.get("__errors")})
    time.sleep(0.3)
log['summary']['relations'] = sum(1 for m in log['mutations'] if m['kind'] == 'relation' and m.get('ok'))
log['summary']['propagation'] = sum(1 for m in log['mutations'] if m['kind'] == 'relation' and m.get('ok') and m['fix'].startswith('umbrella-inbound'))
json.dump(log, open(LOG, "w"), indent=1); print("propagated", log['summary']['propagation'])
