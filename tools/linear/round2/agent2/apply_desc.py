"""Apply rewritten descriptions (placeholders {{key}} -> identifiers of created issues); idempotent via changes file; 8 per request."""
import sys, os, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import r2, rw_pm, rw_agents, rw_spec
DRY = "--dry" in sys.argv
ch = r2.load_changes()
created = {c["key"]: c["identifier"] for c in ch["created"]}

DOCS = {d["project"]: d["url"] for d in ch.get("documents", [])}
def resolve(desc):
    pending = set()
    def rep(m):
        k = m.group(1)
        if k in created: return created[k]
        pending.add(k); return f"[{k}]"
    out = re.sub(r"\{\{([^}]+)\}\}", rep, desc)
    if pending:
        projects = sorted({k.split("/")[0] for k in pending})
        links = ", ".join(f"[{p}]({DOCS[p]})" for p in projects if p in DOCS)
        note = f"\nIssues in square brackets are specified in the project document(s) {links} and will be created when the workspace issue limit is lifted (Linear free plan, `USAGE_LIMIT_EXCEEDED` on 2026-09-17).\n"
        out = out.replace("\n**Agent**", note + "\n**Agent**", 1)
    return out

done = set(ch["updated"])
todo = []
for m in (rw_pm, rw_agents, rw_spec):
    for k, desc in m.DESCRIPTIONS.items():
        i = r2.BY_ID[k]
        d = resolve(desc)
        w = r2.words(d)
        assert 400 <= w <= 700, (k, w)
        for sec in ("**Goal**", "**Scope**", "**Spec**", "**Interface contract**", "**Definition of done**", "**Test plan**", "**Demo**", "**Edge cases**", "**Dependencies**", "**Agent**", "**Size**"):
            assert sec in d, (k, sec)
        assert "{{" not in d, k
        if i["id"] in done: continue
        todo.append((k, i["id"], d))
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
