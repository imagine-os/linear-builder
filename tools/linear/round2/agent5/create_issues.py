import os
"""Create gap issues and children (idempotent through changes-5.json and the snapshot)."""
import sys, json
sys.path.insert(0, os.environ.get("PAPEROS_PLAN_DIR", ".") + "/round2/agent5")
import r5, new_gaps, new_children

DRY = "--dry" in sys.argv
ch = r5.load_changes()

def existing_title(project_id, title):
    for i in r5.SNAP["issues"]:
        if i["projectId"] == project_id and i["title"].strip() == title.strip():
            return i
    for c in ch["created"]:
        if c.get("projectId") == project_id and c["title"].strip() == title.strip():
            return c
    return None

todo = []  # (key, input, meta)
for g in new_gaps.GAPS:
    pid = r5.PROJECTS[g["project"]]
    if r5.find_created(ch, g["key"]) or existing_title(pid, g["title"]):
        print("skip existing", g["key"]); continue
    r5.check_sections(g["key"], g["description"], 400, 750)
    labels = [f"Phase/{g['phase']}", f"Type/{g['type']}"] + g["surfaces"]
    inp = {"teamId": r5.TEAM, "title": g["title"], "description": g["description"], "priority": g["priority"],
           "projectId": pid, "projectMilestoneId": r5.MILESTONES[(pid, g["milestone"])],
           "stateId": r5.STATES[g["state"]], "labelIds": r5.label_ids(labels)}
    todo.append((g["key"], inp, {"parent": None, "projectId": pid, "title": g["title"]}))

counts = {}
for c in new_children.CHILDREN:
    p = r5.BY_ID[c["parent"]]
    idx = counts.get(c["parent"], 0); counts[c["parent"]] = idx + 1
    key = f"child/{c['parent']}/{idx}"
    desc = new_children.render(c["sections"])
    w = r5.words(desc)
    assert 220 <= w <= 600, (key, w)
    for sec in r5.SECTIONS: assert sec in desc, (key, sec)
    if r5.find_created(ch, key) or existing_title(p["projectId"], c["title"]):
        print("skip existing", key); continue
    phase = [l for l in p["labels"] if l.startswith("Phase/")]
    surfaces = [l for l in p["labels"] if "/" not in l]
    labels = phase + [f"Type/{c['type']}"] + surfaces
    inp = {"teamId": r5.TEAM, "title": c["title"], "description": desc, "priority": p["priority"],
           "projectId": p["projectId"], "projectMilestoneId": p["milestoneId"], "parentId": p["id"],
           "stateId": r5.STATES["Backlog"], "labelIds": r5.label_ids(labels)}
    todo.append((key, inp, {"parent": c["parent"], "projectId": p["projectId"], "title": c["title"]}))

print("to create:", len(todo))
if DRY:
    for k, inp, m in todo: print(" ", k, "|", r5.words(inp["description"]), "words |", inp["title"][:90])
    sys.exit(0)

M1 = "mutation($i: IssueCreateInput!) { c: issueCreate(input: $i) { success issue { id identifier url } } }"
for s in range(0, len(todo), 5):
    batch = todo[s:s+5]
    vardefs = []; parts = []; variables = {}
    for j, (k, inp, m) in enumerate(batch):
        vardefs.append(f"$i{j}: IssueCreateInput!")
        parts.append(f"c{j}: issueCreate(input: $i{j}) {{ success issue {{ id identifier url }} }}")
        variables[f"i{j}"] = inp
    q = "mutation(" + ", ".join(vardefs) + ") { " + " ".join(parts) + " }"
    try:
        data = r5.gql(q, variables)
    except RuntimeError as e:
        print("batch failed, singly:", str(e)[:300]); data = {}
        for j, (k, inp, m) in enumerate(batch):
            try: data[f"c{j}"] = r5.gql(M1, {"i": inp})["c"]
            except RuntimeError as e2:
                print("FAILED", k, str(e2)[:300]); ch["notes"].append(f"create failed {k}: {str(e2)[:200]}")
    for j, (k, inp, m) in enumerate(batch):
        r = data.get(f"c{j}")
        if r and r.get("success"):
            iss = r["issue"]
            ch["created"].append({"key": k, "identifier": iss["identifier"], "id": iss["id"], "url": iss["url"],
                                  "parent": m["parent"], "title": m["title"], "projectId": m["projectId"]})
            print("created", k, iss["identifier"])
    r5.save_changes(ch)
print("created total", len(ch["created"]))
