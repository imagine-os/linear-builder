import os
"""Create blocks relations (idempotent) and apply flagged label/milestone fixes."""
import sys
sys.path.insert(0, os.environ.get("PAPEROS_PLAN_DIR", ".") + "/round2/agent1")
import r2, new_identity, new_design, new_quality

DRY = "--dry" in sys.argv
ch = r2.load_changes()

def resolve(ref):
    """identifier or key -> (identifier, id)"""
    if ref.startswith("PAP-"):
        return ref, r2.BY_ID[ref]["id"]
    c = r2.find_created(ch, ref)
    if not c: raise KeyError(ref)
    return c["identifier"], c["id"]

existing = set()
for i in r2.SNAP["issues"]:
    for r in i["relations"]:
        if r["type"] == "blocks": existing.add((i["identifier"], r["related"]))
for rel in ch["relations"]:
    if isinstance(rel, dict): existing.add((rel["from"], rel["to"]))

wanted = []  # (fromRef, toRef)
for mod in (new_identity, new_design, new_quality):
    for g in mod.GAPS:
        for b in g["blockedBy"]: wanted.append((b, g["key"]))
        for b in g["blocks"]: wanted.append((g["key"], b))
    for src, dsts in mod.SIBLING_BLOCKS.items():
        for d in dsts: wanted.append((src, d))
    for a, b in getattr(mod, "EXTRA_RELATIONS", []): wanted.append((a, b))
# audit edges owned by my projects
wanted += [("PAP-59", "PAP-140"), ("PAP-59", "PAP-39"), ("PAP-59", "PAP-116"), ("PAP-57", "PAP-86")]

todo = []
seen = set()
for a, b in wanted:
    fa, ia = resolve(a); fb, ib = resolve(b)
    if (fa, fb) in existing or (fa, fb) in seen: continue
    seen.add((fa, fb)); todo.append((fa, ia, fb, ib))
print("relations to create:", len(todo))
if DRY:
    for fa, ia, fb, ib in todo: print(f"  {fa} blocks {fb}")

M = "mutation($i: IssueRelationCreateInput!) { r: issueRelationCreate(input: $i) { success issueRelation { id } } }"
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
                    data[f"r{j}"] = r2.gql(M, {"i": {"issueId": ia, "relatedIssueId": ib, "type": "blocks"}})["r"]
                except RuntimeError as e2:
                    print("FAILED", fa, fb, str(e2)[:200]); ch["notes"].append(f"relation failed {fa}->{fb}: {str(e2)[:160]}")
        for j, (fa, ia, fb, ib) in enumerate(batch):
            r = data.get(f"r{j}")
            if r and r.get("success"):
                ch["relations"].append({"id": r["issueRelation"]["id"], "from": fa, "to": fb})
                print("rel", fa, "blocks", fb)
        r2.save_changes(ch)

# Flagged fixes: PAP-88 Type/Spec -> Type/Build; PAP-70, PAP-71 -> first design-system milestone
fixes = []
p88 = r2.BY_ID["PAP-88"]
if "Type/Spec" in p88["labels"] and "PAP-88:labels" not in [x.get("what") for x in ch["labelChanges"]]:
    labels = [l if l != "Type/Spec" else "Type/Build" for l in p88["labels"]]
    fixes.append(("PAP-88", {"labelIds": r2.label_ids(labels)}, "PAP-88:labels", f"labels {p88['labels']} -> {labels}"))
ms1 = r2.MILESTONES[(r2.PROJECTS["design-system"], "Tokens and primitives")]
for k in ("PAP-70", "PAP-71"):
    i = r2.BY_ID[k]
    if i["milestoneId"] != ms1 and f"{k}:milestone" not in [x.get("what") for x in ch["labelChanges"]]:
        fixes.append((k, {"projectMilestoneId": ms1}, f"{k}:milestone", f"milestone {i['milestone']} -> Tokens and primitives"))
print("fixes:", [(f[0], f[3]) for f in fixes])
if not DRY:
    for k, inp, what, note in fixes:
        d = r2.gql("mutation($id: String!, $i: IssueUpdateInput!) { u: issueUpdate(id: $id, input: $i) { success } }", {"id": r2.BY_ID[k]["id"], "i": inp})
        if d["u"]["success"]:
            ch["labelChanges"].append({"what": what, "issue": k, "note": note}); print("fixed", k, note)
        r2.save_changes(ch)
