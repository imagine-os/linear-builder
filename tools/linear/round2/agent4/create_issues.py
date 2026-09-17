"""Create gap and child issues for tables, business-core, growth (idempotent, batched).
On USAGE_LIMIT_EXCEEDED the remaining specs are written to pending-issues.json for later creation."""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import r4, new_tables, new_biz, new_growth
DRY = "--dry" in sys.argv
ch = r4.load_changes()
PENDING = os.path.join(r4.HERE, "pending-issues.json")

other_titles = set()
for f in ["changes-0.json", "changes-1.json", "changes-2.json", "changes-3.json"]:
    try:
        for c in json.load(open(os.path.join(r4.R2, f))).get("created", []):
            if c.get("title"): other_titles.add(c["title"].strip().lower())
    except Exception: pass

def existing_title(title, pid):
    t = title.strip().lower()
    for i in r4.SNAP["issues"]:
        if i["title"].strip().lower() == t and i["projectId"] == pid: return i
    if t in other_titles: return {"identifier": "created-elsewhere"}
    return None

plan = []  # (key, input, parentKey, meta)
for mod in (new_tables, new_biz, new_growth):
    pid = r4.PROJECTS[mod.P]
    for g in mod.GAPS:
        if r4.find_created(ch, g["key"]) or existing_title(g["title"], pid):
            print("skip existing", g["key"]); continue
        labels = ["Phase/" + g["phase"], "Type/" + g["type"]] + g["surfaces"]
        state = g["state"]
        inp = {"teamId": r4.TEAM, "title": g["title"], "description": r4.render(g["sections"]), "priority": g["priority"],
               "stateId": r4.STATES[state], "labelIds": r4.label_ids(labels), "projectId": pid,
               "projectMilestoneId": r4.MILESTONES[(pid, g["milestone"])]}
        plan.append((g["key"], inp, None, g))
    for parent, kids in mod.CHILDREN.items():
        p = r4.BY_ID[parent]
        assert p["projectId"] == pid, parent
        phase = [l for l in p["labels"] if l.startswith("Phase/")][0]
        surfaces = [l for l in p["labels"] if l in r4.SURFACES]
        for c in kids:
            if r4.find_created(ch, c["key"]) or existing_title(c["title"], pid):
                print("skip existing", c["key"]); continue
            labels = [phase, "Type/" + c["type"]] + surfaces
            inp = {"teamId": r4.TEAM, "title": c["title"], "description": r4.render(c["sections"]), "priority": p["priority"],
                   "stateId": r4.STATES["Backlog"], "labelIds": r4.label_ids(labels), "projectId": pid,
                   "projectMilestoneId": p["milestoneId"], "parentId": p["id"]}
            plan.append((c["key"], inp, parent, dict(c, parent=parent, project=mod.P, milestone=p["milestone"], phase=phase, surfaces=surfaces, priority=p["priority"])))

print("to create:", len(plan))
if DRY:
    for k, inp, par, _ in plan:
        print(" ", k, "|", inp["title"][:70], "| parent", par, "| words", r4.words(inp["description"]), "| labels", len(inp["labelIds"]))
    sys.exit(0)

limit_hit = False
pending = []
for i in range(0, len(plan), 5):
    batch = plan[i:i+5]
    if limit_hit:
        pending += batch; continue
    vardefs = []; parts = []; variables = {}
    for j, (k, inp, par, _) in enumerate(batch):
        vardefs.append(f"$i{j}: IssueCreateInput!")
        parts.append(f"c{j}: issueCreate(input: $i{j}) {{ success issue {{ id identifier url }} }}")
        variables[f"i{j}"] = inp
    q = "mutation(" + ", ".join(vardefs) + ") { " + " ".join(parts) + " }"
    data = {}
    try:
        data = r4.gql(q, variables)
    except RuntimeError as e:
        msg = str(e)
        if "USAGE_LIMIT_EXCEEDED" in msg:
            print("USAGE_LIMIT_EXCEEDED; switching to pending file"); limit_hit = True
            ch["notes"].append("issueCreate refused with USAGE_LIMIT_EXCEEDED (free-plan issue cap) at batch %d" % (i // 5))
            pending += batch; continue
        print("batch failed, retrying singly:", msg[:300])
        for j, (k, inp, par, _) in enumerate(batch):
            try:
                data[f"c{j}"] = r4.gql("mutation($i: IssueCreateInput!) { c: issueCreate(input: $i) { success issue { id identifier url } } }", {"i": inp})["c"]
            except RuntimeError as e2:
                if "USAGE_LIMIT_EXCEEDED" in str(e2):
                    limit_hit = True; pending.append(batch[j]); continue
                print("FAILED", k, str(e2)[:300]); ch["notes"].append(f"create failed {k}: {str(e2)[:200]}")
    for j, (k, inp, par, _) in enumerate(batch):
        r = data.get(f"c{j}")
        if not r or not r.get("success"): continue
        iss = r["issue"]
        ch["created"].append({"key": k, "identifier": iss["identifier"], "id": iss["id"], "url": iss["url"], "parent": par, "title": inp["title"], "projectName": r4.PNAME[[m for m in r4.PROJECTS if r4.PROJECTS[m] == inp["projectId"]][0]]})
        print("created", iss["identifier"], k)
    r4.save_changes(ch)

if pending:
    out = []
    for k, inp, par, meta in pending:
        rec = {"key": k, "title": inp["title"], "project": meta.get("project") or [m for m in r4.PROJECTS if r4.PROJECTS[m] == inp["projectId"]][0],
               "parent": par, "input": inp,
               "labels": [l for l in r4.LABELS if r4.LABELS[l] in inp["labelIds"]],
               "milestone": [n for (pid, n), mid in r4.MILESTONES.items() if mid == inp["projectMilestoneId"]][0],
               "state": [n for n, sid in r4.STATES.items() if sid == inp["stateId"]][0],
               "size": meta.get("size"), "blockedBy": meta.get("blockedBy", []), "blocks": meta.get("blocks", [])}
        out.append(rec)
    json.dump({"reason": "Linear USAGE_LIMIT_EXCEEDED (activeIssueCount, free plan cap). Create with agent4/create_issues.py once the workspace is upgraded; inputs are complete.", "issues": out}, open(PENDING, "w"), indent=1)
    ch["pendingIssuesFile"] = {"path": PENDING, "count": len(out)}
    r4.save_changes(ch)
    print("pending written:", len(out))
print("created total:", len(ch["created"]))
