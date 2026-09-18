#!/usr/bin/env python3
"""Round 4 closing pass: the remaining mechanical critique fixes (FIX-R4-1, -3, -8, -9).
Usage: final_fixes.py <phase> [--apply]   phases: fix1 | fix3 | fix8 | fix9
Reads the newest critique snapshot (critique-snapshot-final.json if present, else critique-snapshot.json), fetches fresh
text before every description or comment edit, batches <=10 mutations per request with 300 ms between requests, and logs
every mutation to plan/round4/changes/final-fixes.json. Never deletes or archives; never touches PAP-1..12."""
import json, os, sys, re, time, collections, urllib.request, urllib.error, datetime
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, "..")
SNAP_PATH = os.path.join(ROOT, "critique-snapshot-final.json")
if not os.path.exists(SNAP_PATH): SNAP_PATH = os.path.join(ROOT, "critique-snapshot.json")
SNAP = json.load(open(SNAP_PATH)); I = SNAP['issues']; by = {i['identifier']: i for i in I}
LABEL_ID = {l['name']: l['id'] for l in SNAP['labels']}
STATE_ID = {s['name']: s['id'] for s in SNAP['states']}
C1 = "e8272686-b4d3-4ac7-a89e-ba227bd63250"
PHASE = next((a for a in sys.argv[1:] if not a.startswith('--')), None); APPLY = '--apply' in sys.argv
URL = "https://api.linear.app/graphql"; KEY = os.environ.get("LINEAR_API_KEY") or "placeholder"
MARK = "_Round 4 critique fix (2026-09-18):_"
LOG = os.path.join(ROOT, "changes", "final-fixes.json")
log = json.load(open(LOG)) if os.path.exists(LOG) else {"startedAt": None, "mutations": [], "skipped": [], "decisions": []}
def now(): return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
def save():
    if APPLY: json.dump(log, open(LOG, "w"), indent=1)

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

def run_batch(parts, vars_, entries):
    """parts: alias'd mutation strings; vars_: alias -> (gqlType, value); entries: log rows with 'alias'."""
    if not parts: return 0
    q = ("mutation(" + ", ".join("$%s: %s" % (k, t) for k, (t, _) in vars_.items()) + ")" if vars_ else "mutation") + " { " + " ".join(parts) + " }"
    if not APPLY:
        for e in entries: print("  DRY", json.dumps({k: v for k, v in e.items() if k not in ('alias',)})[:300])
        return len(entries)
    data = gql(q, {k: v for k, (_, v) in vars_.items()})
    errs = data.get("__errors") or []
    for e in entries:
        node = data.get(e['alias']) or {}
        e['ok'] = bool(node.get('success')); e['at'] = now(); e['phase'] = PHASE
        if not e['ok']: e['error'] = [x.get('message') for x in errs if e['alias'] in str(x.get('path', ''))] or [x.get('message') for x in errs][:2]
        if node.get('issueRelation'): e['relationId'] = node['issueRelation']['id']
        log['mutations'].append(e)
    save(); time.sleep(0.3)
    return sum(1 for e in entries if e['ok'])

class Batcher:
    def __init__(self): self.parts, self.vars, self.entries, self.ok, self.n = [], {}, [], 0, 0
    def add(self, part_fmt, entry, var=None):
        a = "m%d" % len(self.parts); self.parts.append(part_fmt.replace("$A", a)); entry['alias'] = a; self.entries.append(entry)
        if var: self.vars[a] = var
        self.n += 1
        if len(self.parts) == 10: self.flush()
    def flush(self):
        self.ok += run_batch(self.parts, self.vars, self.entries); self.parts, self.vars, self.entries = [], {}, []

def fresh(idents, fields="id identifier description"):
    out = {}
    for k in range(0, len(idents), 20):
        ids = [by[x]['id'] for x in idents[k:k+20]]
        d = gql("query($ids: [ID!]!) { issues(filter: {id: {in: $ids}}, first: 20) { nodes { %s } } }" % fields, {"ids": ids})
        if d.get("__errors"): raise SystemExit(json.dumps(d["__errors"])[:800])
        for n in d['issues']['nodes']: out[n['identifier']] = n
        time.sleep(0.3)
    return out

def has(i, n): return any(l['name'] == n for l in i['labels'])
def deps_text(desc):
    m = re.search(r'\*\*Dependencies\*\*\s*\n(.*?)(?=\n\*\*[A-Z][^*\n]*\*\*\s*\n|\Z)', desc, re.S); return m.group(1) if m else ''
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
    if B['milestoneDate'] and X['milestoneDate'] and B['milestoneDate'] > X['milestoneDate']: return "milestone inversion %s > %s" % (B['milestoneDate'], X['milestoneDate'])
    if B['dueDate'] and X['dueDate'] and B['dueDate'] > X['dueDate']: return "dueDate inversion %s > %s" % (B['dueDate'], X['dueDate'])
    if X['state'] == 'Ready for Claude' and B['state'] in OPEN: return "would block a Ready issue"
    if reaches(i, b): return "cycle"
    return None

log["startedAt"] = log["startedAt"] or now()
done = {(m['kind'], m.get('identifier') or (m.get('blocker'), m.get('blocked'))) for m in log['mutations'] if m.get('ok')}

# ------------------------------------------------------------------ FIX-R4-1: single-child fresh umbrellas
if PHASE == 'fix1':
    inv = json.load(open("/tmp/claude-0/-home-claude/c81b343e-37f0-53d7-b291-027405cb96ed/scratchpad/linear-inventory.json"))
    inv_issue = {}
    for p in inv['projects']:
        for x in p['issues']: inv_issue[x['identifier']] = x
    fields = {f['identifier']: f for f in json.load(open(os.path.join(ROOT, "issue-fields.json")))}
    PARENTS = ["PAP-434", "PAP-441", "PAP-435", "PAP-26", "PAP-47", "PAP-48", "PAP-22", "PAP-27", "PAP-366", "PAP-367", "PAP-368",
               "PAP-363", "PAP-365", "PAP-442", "PAP-443", "PAP-50", "PAP-51", "PAP-52", "PAP-53"]
    # judgement (from the two descriptions): every child is an add-on (an integration, monitor, settings page, CI shim or
    # reporting layer) to the parent's core scope, so option (b) of the brief applies to all 19 rows.
    JUDGEMENT = {p: "add-on" for p in PARENTS}
    fr = fresh(PARENTS + [by[p]['children'][0] for p in PARENTS], "id identifier estimate description parent{identifier} children{nodes{identifier}} labels{nodes{id name}} state{name} comments(first:20){nodes{id body}}")
    b = Batcher()
    for p in PARENTS:
        P = fr[p]; kids = [c['identifier'] for c in P['children']['nodes']]
        if len(kids) != 1:
            log['decisions'].append({"parent": p, "decision": "skipped: children now %s" % kids}); continue
        c = kids[0]; C = fr[c]
        # labels to restore: the 12:50Z inventory labels, cross-checked with the **Model / Effort:** line
        inv_labels = [l['name'] for l in inv_issue[p]['labels']['nodes']] if isinstance(inv_issue[p].get('labels'), dict) else [l['name'] for l in inv_issue[p].get('labels', [])]
        me = re.search(r'\*\*Model / Effort:\*\*\s*([^\n]+)', P['description'])
        mm = re.match(r'\s*(Fable 5\.1|Opus 5|Sonnet 5|Haiku 4\.5)', me.group(1)) if me else None
        em = re.search(r'/\s*(low|medium|high|max)\b', me.group(1)) if me else None
        model_lbl = next((l for l in inv_labels if l.startswith("Model: ")), None) or ("Model: " + mm.group(1) if mm else None)
        effort_lbl = next((l for l in inv_labels if l.startswith("Effort: ")), None) or ("Effort: " + em.group(1) if em else None)
        assert model_lbl and effort_lbl and (not mm or model_lbl == "Model: " + mm.group(1)) and (not em or effort_lbl == "Effort: " + em.group(1)), (p, inv_labels, me and me.group(1))
        est = fields[p]['estimate']
        inv_state = inv_issue[p]['state']['name'] if isinstance(inv_issue[p].get('state'), dict) else inv_issue[p].get('state')
        why = safe_edge(p, c)
        if why == "exists": why = None
        soft = why is not None
        log['decisions'].append({"parent": p, "child": c, "judgement": JUDGEMENT[p], "restore": {"labels": [model_lbl, effort_lbl], "estimate": est, "inventoryState": inv_state, "currentState": P['state']['name']},
                                 "relation": "soft (%s)" % why if soft else "parent blocks child"})
        # (1) child: de-parent + note in Dependencies
        if ('description', c) not in done:
            note = "%s de-parented from %s (FIX-R4-1: this issue is an add-on to its former parent's core scope, which is a claimable leaf again). %s" % (
                MARK, p, ("%s blocks this issue (`blocks` relation)." % p) if not soft else ("%s is a soft dependency (no `blocks` relation: %s); start when it is In Review." % (p, why)))
            newd = C['description'].rstrip() + "\n\n" + note + "\n"
            b.add('$A: issueUpdate(id: "%s", input: {parentId: null, description: $$A}) { success }' % C['id'],
                  {"kind": "description", "identifier": c, "fix": "FIX-R4-1", "what": "parentId: null + Dependencies note", "formerParent": p}, ("String!", newd))
        # (2) relation parent blocks child
        if not soft and ('relation', (p, c)) not in done:
            b.add('$A: issueRelationCreate(input: {issueId: "%s", relatedIssueId: "%s", type: blocks}) { success issueRelation { id } }' % (P['id'], C['id']),
                  {"kind": "relation", "blocker": p, "blocked": c, "fix": "FIX-R4-1"})
            adj[p].add(c)
        elif soft:
            log['skipped'].append({"blocker": p, "blocked": c, "reason": why, "fix": "FIX-R4-1"})
        # (3) parent: labels, estimate, note; state restore only if it was Ready and is unblocked (none of the 19 was Ready)
        if ('fields', p) not in done:
            inp = {"addedLabelIds": [LABEL_ID[model_lbl], LABEL_ID[effort_lbl]], "estimate": est}
            inp["description"] = P['description'].rstrip() + "\n\n%s %s was split out as a follow-on issue (FIX-R4-1); this issue is a leaf again with its Model / Effort labels and estimate restored, and it %s %s.\n" % (
                MARK, c, "blocks" if not soft else "is a soft dependency of", c)
            if inv_state == "Ready for Claude" and P['state']['name'] != "Ready for Claude":
                open_in = [r['from'] for r in by[p]['inverseRelations'] if r['type'] == 'blocks' and r['from'] in by and by[r['from']]['state'] in OPEN]
                if not open_in: inp["stateId"] = STATE_ID["Ready for Claude"]; inp["cycleId"] = C1
            b.add('$A: issueUpdate(id: "%s", input: $$A) { success }' % P['id'],
                  {"kind": "fields", "identifier": p, "fix": "FIX-R4-1", "input": {k: v for k, v in inp.items() if k != 'description'}, "labels": [model_lbl, effort_lbl], "descriptionNote": True}, ("IssueUpdateInput!", inp))
        # (4) split comment
        cm = next((x for x in P['comments']['nodes'] if x['body'].startswith("Round 4 (2026-09-18): split into sub-issues")), None)
        if cm and ('comment', p) not in done and MARK not in cm['body']:
            body = cm['body'].rstrip() + "\n\n%s %s became a follow-on issue instead (de-parented, FIX-R4-1). This issue is a claimable leaf again; it %s %s." % (MARK, c, "blocks" if not soft else "is a soft dependency of", c)
            b.add('$A: commentUpdate(id: "%s", input: {body: $$A}) { success }' % cm['id'], {"kind": "comment", "identifier": p, "commentId": cm['id'], "fix": "FIX-R4-1"}, ("String!", body))
    b.flush(); save()
    print("FIX-R4-1 mutations planned", b.n, "ok", b.ok if APPLY else "(dry)")

# ------------------------------------------------------------------ FIX-R4-3: umbrella outbound edges through the last child
if PHASE == 'fix3':
    umbs = [u for u in I if u['children'] and u['state'] != 'Triage']
    plan, skips = [], []
    for u in umbs:
        kids_all = [by[c] for c in u['children'] if c in by]
        kids = [k for k in kids_all if not has(k, 'Deferred')] or kids_all
        if not kids: continue
        last = max(kids, key=lambda k: ((k['dueDate'] or ''), k['number']))
        for dst in sorted(adj[u['identifier']], key=lambda s: int(s.split('-')[1])):
            if dst in u['children']: continue
            if any(dst in adj[k['identifier']] for k in kids_all): continue
            why = safe_edge(last['identifier'], dst)
            row = {"umbrella": u['identifier'], "lastChild": last['identifier'], "blocked": dst, "fix": "FIX-R4-3"}
            if why is None: plan.append(row); adj[last['identifier']].add(dst)
            else: row["reason"] = why; skips.append(row)
    print("FIX-R4-3: umbrellas", len(umbs), "edges to create", len(plan), "skipped", len(skips), collections.Counter(s['reason'].split(' ')[0] for s in skips))
    b = Batcher()
    for r in plan:
        if ('relation', (r['lastChild'], r['blocked'])) in done: continue
        b.add('$A: issueRelationCreate(input: {issueId: "%s", relatedIssueId: "%s", type: blocks}) { success issueRelation { id } }' % (by[r['lastChild']]['id'], by[r['blocked']]['id']),
              {"kind": "relation", "blocker": r['lastChild'], "blocked": r['blocked'], "umbrella": r['umbrella'], "fix": "FIX-R4-3"})
    b.flush()
    for s in skips:
        if s not in log['skipped']: log['skipped'].append(s)
    # rule sentence in PAP-92 and PAP-96
    SENT = ("An umbrella's dependents are also blocked by its last child in build order: for every `P blocks D` the last child carries `Clast blocks D` "
            "(skipped only where it would create a cycle, a milestone inversion or a deferred -> scheduled edge), so the promotion pass gates D on the real work; "
            "the umbrella itself reaches In Review when that last child does.")
    fr = fresh(["PAP-92", "PAP-96"])
    for x in ("PAP-92", "PAP-96"):
        d = fr[x]['description']
        if "last child in build order" in d or ('description', x) in done: continue
        m = re.search(r'(\*\*Dependencies\*\*\s*\n)(.*?)(?=\n\*\*[A-Z][^*\n]*\*\*\s*\n|\Z)', d, re.S)
        ins = "\n%s %s\n" % (MARK, SENT)
        newd = d[:m.end()].rstrip("\n") + "\n" + ins + d[m.end():] if m else d.rstrip() + "\n\n" + ins
        b.add('$A: issueUpdate(id: "%s", input: {description: $$A}) { success }' % fr[x]['id'], {"kind": "description", "identifier": x, "fix": "FIX-R4-3", "what": "umbrella last-child rule sentence in Dependencies"}, ("String!", newd))
    b.flush(); save()
    json.dump({"plan": plan, "skipped": skips}, open(os.path.join(HERE, "fix3-plan.json"), "w"), indent=1)
    print("FIX-R4-3 mutations planned", b.n, "ok", b.ok if APPLY else "(dry)")

# ------------------------------------------------------------------ FIX-R4-8: promote PAP-754
if PHASE == 'fix8':
    fr = fresh(["PAP-754"], "id identifier state{name} cycle{id} parent{identifier} children{nodes{identifier}} labels{nodes{name}} inverseRelations{nodes{type issue{identifier state{name}}}}")['PAP-754']
    open_in = [r['issue']['identifier'] for r in fr['inverseRelations']['nodes'] if r['type'] == 'blocks' and r['issue']['state']['name'] in OPEN]
    ok = not open_in and not fr['children']['nodes'] and not fr['parent'] and not any(l['name'] == 'Deferred' for l in fr['labels']['nodes']) and fr['state']['name'] == 'Backlog'
    log['decisions'].append({"issue": "PAP-754", "fix": "FIX-R4-8", "openBlockers": open_in, "children": [c['identifier'] for c in fr['children']['nodes']], "state": fr['state']['name'], "promote": ok})
    if ok:
        b = Batcher()
        b.add('$A: issueUpdate(id: "%s", input: {stateId: "%s", cycleId: "%s"}) { success }' % (fr['id'], STATE_ID["Ready for Claude"], C1), {"kind": "state", "identifier": "PAP-754", "fix": "FIX-R4-8", "to": "Ready for Claude", "cycle": "C1"})
        b.add('$A: commentCreate(input: {issueId: "%s", body: $$A}) { success }' % fr['id'], {"kind": "commentCreate", "identifier": "PAP-754", "fix": "FIX-R4-8"}, ("String!", "promoted: no blockers (round 4 critique)"))
        b.flush()
    save(); print("FIX-R4-8 promote:", ok, open_in)

# ------------------------------------------------------------------ FIX-R4-9: new project target dates and v0.1/v0.2 line
if PHASE == 'fix9':
    NEW = ["Tenant AI Assistant & Business Agents", "Workflows, Approvals, Forms, Documents & E-Signature", "Scheduling, Messaging & Customer Engagement",
           "Commerce, Operations & Vertical Packs", "Platform Operations, Analytics & Compliance"]
    d = gql('{ projects(first: 50) { nodes { id name targetDate content projectMilestones(first: 20) { nodes { name targetDate } } } } }')
    LINE = "v0.1 scope is the first milestone (2026-10-01); the later milestones are v0.2 (deferred)"
    b = Batcher()
    for p in d['projects']['nodes']:
        if p['name'] not in NEW: continue
        latest = max(m['targetDate'] for m in p['projectMilestones']['nodes'] if m['targetDate'])
        first = min(m['targetDate'] for m in p['projectMilestones']['nodes'] if m['targetDate'])
        content = p['content'] or ''
        inp = {}
        if p['targetDate'] != latest: inp['targetDate'] = latest
        if LINE not in content: inp['content'] = "%s %s\n\n%s" % (MARK, LINE.replace("2026-10-01", first), content.lstrip())
        log['decisions'].append({"project": p['name'], "fix": "FIX-R4-9", "targetDate": {"before": p['targetDate'], "after": latest}, "firstMilestone": first, "contentLine": 'content' in inp})
        if inp and ('project', p['name']) not in done:
            b.add('$A: projectUpdate(id: "%s", input: $$A) { success }' % p['id'], {"kind": "project", "identifier": p['name'], "fix": "FIX-R4-9", "input": {k: (v if k != 'content' else '(prepended v0.1/v0.2 line)') for k, v in inp.items()}}, ("ProjectUpdateInput!", inp))
    b.flush(); save(); print("FIX-R4-9 mutations", b.n, "ok", b.ok if APPLY else "(dry)")
log['finishedAt'] = now(); save()
