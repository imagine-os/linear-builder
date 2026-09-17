"""Fallback for the workspace issue limit: one Linear document per project holding the pending specs."""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import r5
DRY = "--dry" in sys.argv
ch = r5.load_changes(); ch.setdefault("documents", [])
pending = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "pending-issues.json")))
INTRO = """> Created 2026-09-17 by the round-2 planning session (agent 5: migration, libraries). Linear refused `issueCreate` with `USAGE_LIMIT_EXCEEDED` (free plan issue cap). The issues below are fully specified and ready to be created with `round2/agent5/create_issues.py` (idempotent) as soon as the workspace plan is upgraded or old issues are archived. Until then the parent issues describe them as work packages (WP1, WP2, WP3) and cold sessions build them in that order on branches `<parent>/wp<n>-<slug>`, reporting each in a comment on the parent.

"""
for proj in ("migration", "libraries"):
    if any(d["project"] == proj for d in ch["documents"]): print("skip", proj); continue
    items = [p for p in pending if p["project"] == proj]
    parts = [f"# Round 2 pending issues: {proj}\n", INTRO, "## Contents\n"]
    for it in items:
        parts.append(f"* `{it['key']}` - {it['title']}" + (f" (child of {it['parent']})" if it["parent"] else ""))
    parts.append("")
    for it in items:
        parts.append(f"## {it['title']}\n")
        meta = (f"`{it['key']}` | {'child of ' + it['parent'] if it['parent'] else 'new issue'} | Phase/{it['phase']}, Type/{it['type']}, "
                f"{', '.join(it['surfaces'])} | priority {it['priority']} | milestone: {it['milestone']} | state: {it['state']} | size {it['size']} | "
                f"blocked by: {', '.join(it['blockedBy']) or 'parent order'} | blocks: {', '.join(it['blocks']) or 'none'}")
        parts.append(meta + "\n"); parts.append(it["description"].strip() + "\n")
    content = "\n".join(parts)
    title = f"Round 2 pending issues: {proj} ({len(items)})"
    print(proj, "items", len(items), "chars", len(content))
    if DRY: continue
    d = r5.gql("mutation($i: DocumentCreateInput!) { d: documentCreate(input: $i) { success document { id url title } } }",
               {"i": {"title": title, "content": content, "projectId": r5.PROJECTS[proj]}})
    if d["d"]["success"]:
        doc = d["d"]["document"]
        ch["documents"].append({"project": proj, "id": doc["id"], "url": doc["url"], "title": doc["title"], "pendingKeys": [it["key"] for it in items]})
        r5.save_changes(ch); print("created document", doc["url"])
