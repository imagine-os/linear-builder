"""Fallback for the workspace issue limit: store the pending gap/child specs as one Linear document per project."""
import sys, os, re, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import r2, new_pm, new_agents, new_spec
DRY = "--dry" in sys.argv
ch = r2.load_changes(); ch.setdefault("documents", [])
created = {c["key"]: c["identifier"] for c in ch["created"]}
def resolve(desc):
    return re.sub(r"\{\{([^}]+)\}\}", lambda m: created.get(m.group(1), f"[{m.group(1)}]"), desc)
SURFACES = {"Customer", "Staff", "Developer", "Agent"}
INTRO = """> Created 2026-09-17 by the round-2 planning session. Linear refused `issueCreate` with `USAGE_LIMIT_EXCEEDED` (free plan, team PAP at 275 issues). The issues below are fully specified and ready to be created with `round2/agent2/create_new.py` (idempotent) as soon as the workspace plan is upgraded. Until then, descriptions of existing issues reference them as `[project/key]`.

"""
for mod in (new_pm, new_agents, new_spec):
    pid = r2.PROJECTS[mod.P]
    if any(d["project"] == mod.P for d in ch["documents"]): print("skip", mod.P); continue
    parts = [f"# Round 2 pending issues: {mod.P}\n", INTRO, "## Contents\n"]
    items = []
    for g in mod.GAPS:
        if g["key"] in created: continue
        items.append(("gap", g, None))
    for parent, kids in mod.CHILDREN.items():
        for c in kids:
            if c["key"] in created: continue
            items.append(("child", c, parent))
    for kind, it, parent in items:
        parts.append(f"* `{it['key']}` - {it['title']}" + (f" (child of {parent})" if parent else ""))
    parts.append("")
    for kind, it, parent in items:
        parts.append(f"## {it['title']}\n")
        if kind == "gap":
            meta = f"`{it['key']}` | new issue | Phase/{it['phase']}, Type/{it['type']}, {', '.join(it['surfaces'])} | priority {it['priority']} | milestone: {it['milestone']} | state: {it['state']} | blocked by: {', '.join(it['blockedBy']) or 'none'} | blocks: {', '.join(it['blocks']) or 'none'}"
        else:
            p = r2.BY_ID[parent]
            meta = f"`{it['key']}` | child of {parent} | {[l for l in p['labels'] if l.startswith('Phase/')][0]}, Type/{it['type']}, {', '.join(l for l in p['labels'] if l in SURFACES)} | priority {p['priority']} | milestone: {p['milestone']} | state: Backlog | size {it['size']} | blocked by: {', '.join(it['blockedBy']) or 'none'} | blocks: {', '.join(it['blocks']) or 'none'}"
        parts.append(meta + "\n")
        parts.append(resolve(it["description"]).strip() + "\n")
    content = "\n".join(parts)
    title = f"Round 2 pending issues: {mod.P} ({len(items)})"
    print(mod.P, "items", len(items), "chars", len(content))
    if DRY: continue
    d = r2.gql("mutation($i: DocumentCreateInput!) { d: documentCreate(input: $i) { success document { id url title } } }", {"i": {"title": title, "content": content, "projectId": pid}})
    if d["d"]["success"]:
        doc = d["d"]["document"]; ch["documents"].append({"project": mod.P, "id": doc["id"], "url": doc["url"], "title": doc["title"], "pendingKeys": [it["key"] for _, it, _ in items]})
        r2.save_changes(ch); print("created document", doc["url"])
