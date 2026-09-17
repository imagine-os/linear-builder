import os
"""Apply rewritten descriptions (idempotent via changes file), batched 8 per request."""
import sys
sys.path.insert(0, os.environ.get("PAPEROS_PLAN_DIR", ".") + "/round2/agent1")
import r2, rw_identity, rw_design, rw_quality
DRY = "--dry" in sys.argv
ch = r2.load_changes()
done = set(ch["updated"])
todo = []
for m in (rw_identity, rw_design, rw_quality):
    for k, desc in m.DESCRIPTIONS.items():
        i = r2.BY_ID[k]
        w = r2.words(desc)
        assert 400 <= w <= 700, (k, w)
        for sec in ("**Goal**", "**Scope**", "**Spec**", "**Interface contract**", "**Definition of done**", "**Test plan**", "**Demo**", "**Edge cases**", "**Dependencies**", "**Agent**", "**Size**"):
            assert sec in desc, (k, sec)
        if i["id"] in done: continue
        todo.append((k, i["id"], desc))
print("to update:", len(todo))
if DRY: sys.exit(0)
for s in range(0, len(todo), 8):
    batch = todo[s:s+8]
    vardefs=[]; parts=[]; variables={}
    for j,(k,iid,desc) in enumerate(batch):
        vardefs.append(f"$id{j}: String!, $i{j}: IssueUpdateInput!")
        parts.append(f"u{j}: issueUpdate(id: $id{j}, input: $i{j}) {{ success }}")
        variables[f"id{j}"]=iid; variables[f"i{j}"]={"description": desc}
    q="mutation("+", ".join(vardefs)+") { "+" ".join(parts)+" }"
    try:
        data=r2.gql(q, variables)
    except RuntimeError as e:
        print("batch failed, singly:", str(e)[:200]); data={}
        for j,(k,iid,desc) in enumerate(batch):
            try: data[f"u{j}"]=r2.gql("mutation($id: String!, $i: IssueUpdateInput!) { u: issueUpdate(id: $id, input: $i) { success } }", {"id": iid, "i": {"description": desc}})["u"]
            except RuntimeError as e2: print("FAILED", k, str(e2)[:200]); ch["notes"].append(f"update failed {k}: {str(e2)[:160]}")
    for j,(k,iid,desc) in enumerate(batch):
        r=data.get(f"u{j}")
        if r and r.get("success"):
            ch["updated"].append(iid); print("updated", k)
    r2.save_changes(ch)
print("updated total", len(ch["updated"]))
