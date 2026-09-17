import os
"""Push rewritten descriptions (batched issueUpdate). PAP-136 also gets P1 label, priority 1 and the second collab milestone."""
import sys, json
sys.path.insert(0, os.environ.get("PAPEROS_PLAN_DIR", ".") + "/round2/agent3")
import r3, rw_collab, rw_realtime, rw_input
DRY = "--dry" in sys.argv
ch = r3.load_changes()
ALL = {}
for R in (rw_collab.R, rw_realtime.R, rw_input.R): ALL.update(R)

todo = []
for ident, secs in ALL.items():
    iss = r3.BY_ID[ident]
    if iss["id"] in ch["updated"]: print("skip", ident); continue
    inp = {"description": r3.render(secs)}
    if ident == "PAP-136":
        labels = [l for l in iss["labels"] if l != "Phase/P2"] + ["Phase/P1"]
        inp["labelIds"] = r3.label_ids(labels)
        inp["priority"] = 1
        inp["projectMilestoneId"] = r3.MILESTONES[(r3.PROJECTS["collab"], "Comments and canvas")]
    if ident == "PAP-133":
        inp["projectMilestoneId"] = r3.MILESTONES[(r3.PROJECTS["collab"], "Docs and prompt log stores")]
    todo.append((ident, iss["id"], inp))
print("to update:", len(todo))
if DRY:
    for ident, iid, inp in todo: print(" ", ident, r3.words(inp["description"]), list(inp.keys()))
    sys.exit(0)
for i in range(0, len(todo), 8):
    batch = todo[i:i+8]
    vardefs = []; parts = []; variables = {}
    for j, (ident, iid, inp) in enumerate(batch):
        vardefs.append(f"$i{j}: IssueUpdateInput!")
        parts.append(f'u{j}: issueUpdate(id: "{iid}", input: $i{j}) {{ success issue {{ identifier }} }}')
        variables[f"i{j}"] = inp
    q = "mutation(" + ", ".join(vardefs) + ") { " + " ".join(parts) + " }"
    try:
        data = r3.gql(q, variables)
    except RuntimeError as e:
        print("batch failed, singly:", str(e)[:300]); data = {}
        for j, (ident, iid, inp) in enumerate(batch):
            try:
                d = r3.gql('mutation($id: String!, $i: IssueUpdateInput!) { u: issueUpdate(id: $id, input: $i) { success issue { identifier } } }', {"id": iid, "i": inp})
                data[f"u{j}"] = d["u"]
            except RuntimeError as e2:
                print("FAILED", ident, str(e2)[:300]); ch["notes"].append(f"update failed {ident}: {str(e2)[:200]}")
    for j, (ident, iid, inp) in enumerate(batch):
        r = data.get(f"u{j}")
        if r and r.get("success"):
            ch["updated"].append(iid); print("updated", ident)
            if ident in ("PAP-136", "PAP-133"): ch["milestoneChanges"].append({"issue": ident, "milestone": "Comments and canvas" if ident == "PAP-136" else "Docs and prompt log stores", "labels": inp.get("labelIds"), "priority": inp.get("priority")})
        else: print("no result", ident)
    r3.save_changes(ch)
print("done; updated total", len(ch["updated"]))
