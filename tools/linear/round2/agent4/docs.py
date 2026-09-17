"""Fallback for the workspace issue limit: one Linear document per project holding the pending gap and child specs."""
import sys, os, json, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import r4
DRY = "--dry" in sys.argv
ch = r4.load_changes(); ch.setdefault("documents", [])
pending = json.load(open(os.path.join(r4.HERE, "pending-issues.json")))["issues"]
created = {c["key"]: c["identifier"] for c in ch["created"]}
def resolve(desc):
    return re.sub(r"\{\{([^}]+)\}\}", lambda m: created.get(m.group(1), f"[{m.group(1)}]"), desc)
INTRO = """> Created 2026-09-17 by the round-2 planning session (agent 4). Linear refused `issueCreate` with `USAGE_LIMIT_EXCEEDED` (free plan, team PAP at 275 issues). Every issue below is fully specified (Goal, Scope, Spec, Interface contract, Definition of done, Test plan, Demo, Edge cases, Dependencies, Agent, Size) and is created verbatim by `round2/agent4/create_issues.py` (idempotent) once the workspace plan is upgraded. Until then, parent issues describe them as work packages and reference them as `[project/key]`.

"""
for P in ("tables", "business-core", "growth"):
    items = [x for x in pending if x["project"] == P]
    if not items: continue
    if any(d["project"] == P for d in ch["documents"]): print("skip", P); continue
    gaps = [x for x in items if not x["parent"]]; kids = [x for x in items if x["parent"]]
    parts = [f"# Round 2 pending issues: {P}\n", INTRO, f"## Contents ({len(gaps)} new issues, {len(kids)} children)\n"]
    for it in gaps: parts.append(f"* `{it['key']}` - {it['title']}")
    by_parent = {}
    for it in kids: by_parent.setdefault(it["parent"], []).append(it)
    for parent, ks in by_parent.items():
        parts.append(f"* Children of {parent} ({r4.BY_ID[parent]['title'][:80]}):")
        for it in ks: parts.append(f"  * `{it['key']}` - {it['title']} ({it['size']})")
    parts.append("")
    for it in items:
        parts.append(f"## {it['title']}\n")
        meta = (f"`{it['key']}` | " + (f"child of {it['parent']}" if it["parent"] else "new issue") +
                f" | {', '.join(it['labels'])} | priority {it['input']['priority']} | milestone: {it['milestone']} | state: {it['state']}"
                + (f" | size {it['size']}" if it.get("size") else "")
                + (f" | blocked by: {', '.join(it['blockedBy'])}" if it.get("blockedBy") else "")
                + (f" | blocks: {', '.join(it['blocks'])}" if it.get("blocks") else ""))
        parts.append(meta + "\n")
        parts.append(resolve(it["input"]["description"]).strip() + "\n")
    content = "\n".join(parts)
    title = f"Round 2 pending issues: {P} ({len(items)})"
    print(P, "items", len(items), "chars", len(content))
    if DRY: continue
    d = r4.gql("mutation($i: DocumentCreateInput!) { d: documentCreate(input: $i) { success document { id url title } } }",
               {"i": {"title": title, "content": content, "projectId": r4.PROJECTS[P]}})
    if d["d"]["success"]:
        doc = d["d"]["document"]
        ch["documents"].append({"project": P, "id": doc["id"], "url": doc["url"], "title": doc["title"], "pendingKeys": [it["key"] for it in items]})
        r4.save_changes(ch); print("created document", doc["url"])
