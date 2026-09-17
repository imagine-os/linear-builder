"""Create blocks relations (idempotent across all changes-*.json) and apply the flagged label fix (PAP-110 Review -> Build)."""
import sys, os, json, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import r2, new_pm, new_agents, new_spec
DRY = "--dry" in sys.argv
ch = r2.load_changes()
ch.setdefault("labelChanges", []); ch.setdefault("notes", [])

# identifiers created by any agent (for cross refs like PAP-279)
created_ids = {}
for f in glob.glob(os.path.join(r2.R2, "changes-*.json")):
    for c in json.load(open(f)).get("created", []):
        created_ids[c["identifier"]] = c["id"]
        if f.endswith("changes-2.json"): created_ids[c["key"]] = c["id"]
def resolve(ref):
    if ref.startswith("PAP-"):
        if ref in r2.BY_ID: return ref, r2.BY_ID[ref]["id"]
        if ref in created_ids: return ref, created_ids[ref]
        raise KeyError(ref)
    c = r2.find_created(ch, ref)
    if not c: raise KeyError(ref)
    return c["identifier"], c["id"]

existing = set()
for i in r2.SNAP["issues"]:
    for r in i["relations"]:
        if r["type"] == "blocks": existing.add((i["identifier"], r["related"]))
for f in glob.glob(os.path.join(r2.R2, "changes-*.json")):
    for rel in json.load(open(f)).get("relations", []):
        if isinstance(rel, dict) and "from" in rel: existing.add((rel["from"], rel["to"]))
    for pair in json.load(open(f)).get("relationPairs", []):
        if isinstance(pair, (list, tuple)) and len(pair) == 2: existing.add(tuple(pair))

wanted = []
for mod in (new_pm, new_agents, new_spec):
    for g in mod.GAPS:
        for b in g["blockedBy"]: wanted.append((b, g["key"]))
        for b in g["blocks"]: wanted.append((g["key"], b))
    for parent, kids in mod.CHILDREN.items():
        for c in kids:
            for b in c["blockedBy"]: wanted.append((b, c["key"]))
            for b in c["blocks"]: wanted.append((c["key"], b))
# audit-flagged and spec-stated hard dependencies owned by my projects
wanted += [
    ("PAP-25", "PAP-96"),      # orchestrator deploys onto the VPS (plan.json edge missing)
    ("PAP-117", "PAP-123"),    # app spec needed for start nodes
    ("PAP-123", "PAP-132"),    # canvas loads the flow graph
    ("PAP-279", "PAP-116"),    # shared Condition grammar
    ("PAP-279", "PAP-119"),    # shared FilterTree
    ("PAP-239", "PAP-97"),     # gate artifact contract for status comments
    ("PAP-234", "PAP-120"),    # state components (already added by agent1; dedupe)
    ("PAP-240", "PAP-122"),    # login-as fixtures for generated Playwright suites
    ("PAP-120", "PAP-29"),     # drill uses codegen (plan.json edge missing)
    ("PAP-94", "PAP-108"),     # escalate handoffs render decision cards
    ("PAP-105", "PAP-108"),    # linear-update validates handoffs
    ("PAP-98", "PAP-113"),     # spend in org chart
    ("PAP-105", "PAP-118"),    # already exists; dedupe check
]
todo = []; seen = set(); pending = []
for a, b in wanted:
    try:
        fa, ia = resolve(a); fb, ib = resolve(b)
    except KeyError as e:
        pending.append((a, b)); continue
    if (fa, fb) in existing or (fa, fb) in seen: continue
    seen.add((fa, fb)); todo.append((fa, ia, fb, ib))
print("relations to create:", len(todo), "| pending (uncreated issues):", len(pending))
ch["pendingRelations"] = [f"{a} -> {b}" for a, b in pending]
for fa, ia, fb, ib in todo: print(f"  {fa} blocks {fb}")

if not DRY:
    for i in range(0, len(todo), 8):
        batch = todo[i:i + 8]
        vardefs = []; parts = []; variables = {}
        for j, (fa, ia, fb, ib) in enumerate(batch):
            vardefs.append(f"$i{j}: IssueRelationCreateInput!")
            parts.append(f"r{j}: issueRelationCreate(input: $i{j}) {{ success issueRelation {{ id }} }}")
            variables[f"i{j}"] = {"issueId": ia, "relatedIssueId": ib, "type": "blocks"}
        q = "mutation(" + ", ".join(vardefs) + ") { " + " ".join(parts) + " }"
        try:
            data = r2.gql(q, variables)
        except RuntimeError as e:
            print("batch failed, singly:", str(e)[:200]); data = {}
            for j, (fa, ia, fb, ib) in enumerate(batch):
                try:
                    data[f"r{j}"] = r2.gql("mutation($i: IssueRelationCreateInput!) { r: issueRelationCreate(input: $i) { success issueRelation { id } } }", {"i": {"issueId": ia, "relatedIssueId": ib, "type": "blocks"}})["r"]
                except RuntimeError as e2:
                    print("FAILED", fa, fb, str(e2)[:200]); ch["notes"].append(f"relation failed {fa}->{fb}: {str(e2)[:160]}")
        for j, (fa, ia, fb, ib) in enumerate(batch):
            r = data.get(f"r{j}")
            if r and r.get("success"):
                ch["relations"].append({"id": r["issueRelation"]["id"], "from": fa, "to": fb}); print("rel", fa, "blocks", fb)
        r2.save_changes(ch)

# flagged label fix: PAP-110 is Type/Review but builds a harness -> Type/Build
p110 = r2.BY_ID["PAP-110"]
if "Type/Review" in p110["labels"] and not any(x.get("what") == "PAP-110:labels" for x in ch["labelChanges"]):
    labels = [l if l != "Type/Review" else "Type/Build" for l in p110["labels"]]
    print("fix PAP-110 labels", p110["labels"], "->", labels)
    if not DRY:
        d = r2.gql("mutation($id: String!, $i: IssueUpdateInput!) { u: issueUpdate(id: $id, input: $i) { success } }", {"id": p110["id"], "i": {"labelIds": r2.label_ids(labels)}})
        if d["u"]["success"]:
            ch["labelChanges"].append({"what": "PAP-110:labels", "issue": "PAP-110", "note": "Type/Review -> Type/Build (audit: Review-typed issue builds a harness)"}); r2.save_changes(ch); print("fixed PAP-110")
