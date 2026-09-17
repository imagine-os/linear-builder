"""Create gap issues and child issues for pm-linear, agents, spec-builder (idempotent, aliased batches)."""
import json, sys, glob, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import r2, new_pm, new_agents, new_spec
DRY = "--dry" in sys.argv
ch = r2.load_changes()
SURFACES = {"Customer", "Staff", "Developer", "Agent"}

# titles created by any round-2 agent (avoid duplicates)
other_titles = set()
for f in glob.glob(os.path.join(r2.R2, "changes-*.json")):
    try:
        for c in json.load(open(f)).get("created", []):
            if c.get("title"): other_titles.add(c["title"].strip().lower())
    except Exception: pass

def existing_title(title, project_id):
    t = title.strip().lower()
    for i in r2.SNAP["issues"]:
        if i["title"].strip().lower() == t and i["projectId"] == project_id: return i
    if t in other_titles: return {"identifier": "created-elsewhere"}
    return None

plan = []
for mod in (new_pm, new_agents, new_spec):
    pid = r2.PROJECTS[mod.P]
    for g in mod.GAPS:
        if r2.find_created(ch, g["key"]) or existing_title(g["title"], pid):
            print("skip existing", g["key"]); continue
        labels = ["Phase/" + g["phase"], "Type/" + g["type"]] + g["surfaces"]
        inp = {"teamId": r2.TEAM, "title": g["title"], "description": g["description"], "priority": g["priority"],
               "stateId": r2.STATES[g["state"]], "labelIds": r2.label_ids(labels), "projectId": pid,
               "projectMilestoneId": r2.MILESTONES[(pid, g["milestone"])]}
        plan.append((g["key"], inp, None))
    for parent, kids in mod.CHILDREN.items():
        p = r2.BY_ID[parent]
        phase = [l for l in p["labels"] if l.startswith("Phase/")][0]
        surfaces = [l for l in p["labels"] if l in SURFACES]
        for c in kids:
            if r2.find_created(ch, c["key"]) or existing_title(c["title"], pid):
                print("skip existing", c["key"]); continue
            labels = [phase, "Type/" + c["type"]] + surfaces
            inp = {"teamId": r2.TEAM, "title": c["title"], "description": c["description"], "priority": p["priority"],
                   "stateId": r2.STATES["Backlog"], "labelIds": r2.label_ids(labels), "projectId": pid,
                   "projectMilestoneId": p["milestoneId"], "parentId": p["id"]}
            plan.append((c["key"], inp, parent))

print("to create:", len(plan))
if DRY:
    for k, inp, par in plan: print(k, "|", inp["title"][:70], "| parent", par, "| labels", len(inp["labelIds"]), "| state", [s for s,i in r2.STATES.items() if i==inp["stateId"]][0])
    sys.exit(0)

for i in range(0, len(plan), 8):
    batch = plan[i:i + 8]
    parts = []; variables = {}; vardefs = []
    for j, (k, inp, par) in enumerate(batch):
        vardefs.append(f"$i{j}: IssueCreateInput!")
        parts.append(f"c{j}: issueCreate(input: $i{j}) {{ success issue {{ id identifier url }} }}")
        variables[f"i{j}"] = inp
    q = "mutation(" + ", ".join(vardefs) + ") { " + " ".join(parts) + " }"
    try:
        data = r2.gql(q, variables)
    except RuntimeError as e:
        print("batch failed, retrying singly:", str(e)[:300]); data = {}
        for j, (k, inp, par) in enumerate(batch):
            try:
                data[f"c{j}"] = r2.gql("mutation($i: IssueCreateInput!) { c: issueCreate(input: $i) { success issue { id identifier url } } }", {"i": inp})["c"]
            except RuntimeError as e2:
                print("FAILED", k, str(e2)[:300]); ch["notes"].append(f"create failed {k}: {str(e2)[:200]}")
    for j, (k, inp, par) in enumerate(batch):
        r = data.get(f"c{j}")
        if not r or not r.get("success"): print("no result", k); continue
        iss = r["issue"]
        ch["created"].append({"key": k, "identifier": iss["identifier"], "id": iss["id"], "url": iss["url"], "parent": par, "title": inp["title"]})
        print("created", iss["identifier"], k)
    r2.save_changes(ch)
print("done; created total", len(ch["created"]))
