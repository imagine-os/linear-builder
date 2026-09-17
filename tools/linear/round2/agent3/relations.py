"""Create blocks relations flagged by the audit or stated as hard in spec text (idempotent)."""
import sys
sys.path.insert(0, os.environ.get("PAPEROS_PLAN_DIR", ".") + "/round2/agent3")
import r3, json, os
DRY = "--dry" in sys.argv
ch = r3.load_changes()
existing = set()
for i in r3.SNAP["issues"]:
    for r in i["relations"]:
        if r["type"] == "blocks": existing.add((i["identifier"], r["related"]))
# relations created by sibling agents this round
for f in ["changes-0.json", "changes-1.json", "changes-2.json", "changes-3.json"]:
    p = os.path.join(r3.R2, f)
    if not os.path.exists(p): continue
    c = json.load(open(p))
    for rel in c.get("relations", []):
        if isinstance(rel, dict) and "from" in rel: existing.add((rel["from"], rel["to"]))
    for pr in c.get("relationPairs", []) or []:
        existing.add(tuple(pr["pair"]))

WANTED = [
 ("PAP-139", "PAP-140"),  # CRDT ADR fixes encoding and snapshot cadence for the server
 ("PAP-142", "PAP-131"),  # comments composer is RichTextEditor local mode
 ("PAP-144", "PAP-148"),  # offline queue implements the conflict UX spec
 ("PAP-143", "PAP-147"),  # load test Electric scenario
 ("PAP-150", "PAP-151"),  # chord format
 ("PAP-150", "PAP-157"),  # pen fields and palm rule
 ("PAP-150", "PAP-158"),  # gamepad events and cursor pointer
 ("PAP-152", "PAP-155"),  # LiveAnnouncer and focus restore
 ("PAP-152", "PAP-158"),  # focus regions
 ("PAP-86", "PAP-156"),   # core flow scripts
 ("PAP-73", "PAP-156"),   # component-level baseline; manual AT handed to PAP-156
 ("PAP-117", "PAP-160"),  # app-level spec fills the statement
 ("PAP-43", "PAP-136"),   # already exists in snapshot; kept for idempotence
]
# NOTE: audit asked for PAP-123 -> PAP-132, but Linear already holds PAP-132 -> PAP-123 (canvas owns the shared
# FlowGraph types file). Adding the reverse edge would create a cycle, so it is intentionally skipped.
todo = []
for a, b in WANTED:
    if (a, b) in existing: continue
    todo.append((a, r3.BY_ID[a]["id"], b, r3.BY_ID[b]["id"]))
print("relations to create:", len(todo))
if DRY:
    for a, ia, b, ib in todo: print(f"  {a} blocks {b}")
    sys.exit(0)
for i in range(0, len(todo), 8):
    batch = todo[i:i+8]
    vardefs = []; parts = []; variables = {}
    for j, (a, ia, b, ib) in enumerate(batch):
        vardefs.append(f"$i{j}: IssueRelationCreateInput!")
        parts.append(f"r{j}: issueRelationCreate(input: $i{j}) {{ success issueRelation {{ id }} }}")
        variables[f"i{j}"] = {"issueId": ia, "relatedIssueId": ib, "type": "blocks"}
    q = "mutation(" + ", ".join(vardefs) + ") { " + " ".join(parts) + " }"
    try:
        data = r3.gql(q, variables)
    except RuntimeError as e:
        print("batch failed, singly:", str(e)[:200]); data = {}
        for j, (a, ia, b, ib) in enumerate(batch):
            try:
                d = r3.gql("mutation($i: IssueRelationCreateInput!) { r: issueRelationCreate(input: $i) { success issueRelation { id } } }", {"i": variables[f"i{j}"]})
                data[f"r{j}"] = d["r"]
            except RuntimeError as e2:
                print("FAILED", a, b, str(e2)[:200]); ch["notes"].append(f"relation failed {a}->{b}: {str(e2)[:150]}")
    for j, (a, ia, b, ib) in enumerate(batch):
        r = data.get(f"r{j}")
        if r and r.get("success"):
            ch["relations"].append({"id": r["issueRelation"]["id"], "from": a, "to": b}); print("created", a, "blocks", b)
    r3.save_changes(ch)
print("done; relations total", len(ch["relations"]))
