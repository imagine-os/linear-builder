import os
"""Create child and gap issues for collab, realtime, input (idempotent, batched)."""
import sys, json
sys.path.insert(0, os.environ.get("PAPEROS_PLAN_DIR", ".") + "/round2/agent3")
import r3, new_collab, new_rt_input
DRY = "--dry" in sys.argv
ch = r3.load_changes()

def existing_title(title, pid):
    for i in r3.SNAP["issues"]:
        if i["title"].strip().lower() == title.strip().lower() and i["projectId"] == pid: return i
    return None

plan = []
# gaps
for g, pkey in [(x, "collab") for x in new_collab.GAPS] + [(x, x["project"]) for x in new_rt_input.GAPS]:
    pid = r3.PROJECTS[pkey]
    if r3.find_created(ch, g["key"]) or existing_title(g["title"], pid):
        print("skip existing", g["key"]); continue
    labels = ["Phase/" + g["phase"], "Type/" + g["type"]] + g["surfaces"]
    inp = {"teamId": r3.TEAM, "title": g["title"], "description": r3.render(g["sections"]), "priority": g["priority"],
           "stateId": r3.STATES[g["state"]], "labelIds": r3.label_ids(labels), "projectId": pid,
           "projectMilestoneId": r3.MILESTONES[(pid, g["milestone"])]}
    plan.append((g["key"], inp, None))
# children
for mod in (new_collab, new_rt_input):
    for parent, kids in mod.CHILDREN.items():
        p = r3.BY_ID[parent]; pid = p["projectId"]
        phase = [l for l in p["labels"] if l.startswith("Phase/")][0]
        surfaces = [l for l in p["labels"] if l in r3.SURFACES]
        for c in kids:
            if r3.find_created(ch, c["key"]) or existing_title(c["title"], pid):
                print("skip existing", c["key"]); continue
            labels = [phase, "Type/" + c["type"]] + surfaces
            inp = {"teamId": r3.TEAM, "title": c["title"], "description": r3.render(c["sections"]), "priority": p["priority"],
                   "stateId": r3.STATES["Backlog"], "labelIds": r3.label_ids(labels), "projectId": pid,
                   "projectMilestoneId": p["milestoneId"], "parentId": p["id"]}
            plan.append((c["key"], inp, parent))

print("to create:", len(plan))
if DRY:
    for k, inp, par in plan: print(" ", k, "|", inp["title"][:70], "| parent", par, "| words", r3.words(inp["description"]))
    sys.exit(0)

for i in range(0, len(plan), 8):
    batch = plan[i:i+8]
    vardefs = []; parts = []; variables = {}
    for j, (k, inp, par) in enumerate(batch):
        vardefs.append(f"$i{j}: IssueCreateInput!")
        parts.append(f"c{j}: issueCreate(input: $i{j}) {{ success issue {{ id identifier url }} }}")
        variables[f"i{j}"] = inp
    q = "mutation(" + ", ".join(vardefs) + ") { " + " ".join(parts) + " }"
    try:
        data = r3.gql(q, variables)
    except RuntimeError as e:
        print("batch failed, retrying singly:", str(e)[:300]); data = {}
        for j, (k, inp, par) in enumerate(batch):
            try:
                d = r3.gql("mutation($i: IssueCreateInput!) { c: issueCreate(input: $i) { success issue { id identifier url } } }", {"i": inp})
                data[f"c{j}"] = d["c"]
            except RuntimeError as e2:
                print("FAILED", k, str(e2)[:300]); ch["notes"].append(f"create failed {k}: {str(e2)[:200]}")
    for j, (k, inp, par) in enumerate(batch):
        r = data.get(f"c{j}")
        if not r or not r.get("success"): print("no result", k); continue
        iss = r["issue"]
        ch["created"].append({"key": k, "identifier": iss["identifier"], "id": iss["id"], "url": iss["url"], "parent": par, "title": inp["title"]})
        print("created", iss["identifier"], k)
    r3.save_changes(ch)
print("done; created total", len(ch["created"]))
