"""Relations (idempotent), flagged field fixes, umbrella comments on L parents."""
import sys, json
sys.path.insert(0, os.environ.get("PAPEROS_PLAN_DIR", ".") + "/round2/agent5")
import r5
DRY = "--dry" in sys.argv
ch = r5.load_changes()
ch.setdefault("comments", []); ch.setdefault("fieldChanges", [])

# ---- relations: spec-text dependencies not yet encoded (all within or into my projects) ----
WANTED = [
    ("PAP-198", "PAP-199"),  # format research shapes SourceConnector and rate-limit defaults
    ("PAP-37", "PAP-199"),   # attachments stream to object storage
    ("PAP-201", "PAP-202"), ("PAP-201", "PAP-203"), ("PAP-201", "PAP-204"), ("PAP-201", "PAP-205"), ("PAP-201", "PAP-206"),  # two-pass relations and round trip
    ("PAP-128", "PAP-205"),  # docs export reads the docs store
    ("PAP-114", "PAP-207"),  # packs carry page specs
    ("PAP-211", "PAP-216"),  # license field verification
    ("PAP-48", "PAP-217"),   # Renovate needs the Scout bot token
    ("PAP-213", "PAP-170"),  # chart and map ADRs before map/chart views (09-24 -> 09-27)
]
existing = set()
for i in r5.SNAP["issues"]:
    for r in i["relations"]:
        if r["type"] == "blocks": existing.add((i["identifier"], r["related"]))
for rel in ch["relations"]:
    if isinstance(rel, dict): existing.add((rel["from"], rel["to"]))
# also skip pairs other agents created this round
import glob, os
for f in glob.glob(os.path.join(r5.R2, "changes-*.json")):
    if f.endswith("changes-5.json"): continue
    try:
        for rel in json.load(open(f)).get("relations", []):
            if isinstance(rel, dict) and "from" in rel: existing.add((rel["from"], rel["to"]))
    except Exception: pass
todo = [(a, b) for a, b in WANTED if (a, b) not in existing and (b, a) not in existing]
print("relations to create:", len(todo), todo)
if not DRY:
    for i in range(0, len(todo), 8):
        batch = todo[i:i + 8]
        vardefs = []; parts = []; variables = {}
        for j, (a, b) in enumerate(batch):
            vardefs.append(f"$i{j}: IssueRelationCreateInput!")
            parts.append(f"r{j}: issueRelationCreate(input: $i{j}) {{ success issueRelation {{ id }} }}")
            variables[f"i{j}"] = {"issueId": r5.BY_ID[a]["id"], "relatedIssueId": r5.BY_ID[b]["id"], "type": "blocks"}
        q = "mutation(" + ", ".join(vardefs) + ") { " + " ".join(parts) + " }"
        try:
            data = r5.gql(q, variables)
        except RuntimeError as e:
            print("batch failed, singly:", str(e)[:200]); data = {}
            for j, (a, b) in enumerate(batch):
                try:
                    data[f"r{j}"] = r5.gql("mutation($i: IssueRelationCreateInput!) { r: issueRelationCreate(input: $i) { success issueRelation { id } } }",
                                           {"i": {"issueId": r5.BY_ID[a]["id"], "relatedIssueId": r5.BY_ID[b]["id"], "type": "blocks"}})["r"]
                except RuntimeError as e2:
                    print("FAILED", a, b, str(e2)[:200]); ch["notes"].append(f"relation failed {a}->{b}: {str(e2)[:160]}")
        for j, (a, b) in enumerate(batch):
            r = data.get(f"r{j}")
            if r and r.get("success"):
                ch["relations"].append({"id": r["issueRelation"]["id"], "from": a, "to": b}); print("rel", a, "blocks", b)
        r5.save_changes(ch)

# ---- flagged fixes ----
fixes = []
done_fixes = {x["what"] for x in ch["fieldChanges"]}
# audit: PAP-198 has no blockers, is Research, sits in Backlog -> Ready for Claude
if r5.BY_ID["PAP-198"]["state"] != "Ready for Claude" and "PAP-198:state" not in done_fixes:
    fixes.append(("PAP-198", {"stateId": r5.STATES["Ready for Claude"]}, "PAP-198:state", "state Backlog -> Ready for Claude (audit: unblocked Research issue)"))
# audit: milestone inversion PAP-212 (09-24) blocks PAP-67 (09-20); PAP-212 must land by 09-19 anyway
ms_eval = r5.MILESTONES[(r5.PROJECTS["libraries"], "Evaluation process")]
if r5.BY_ID["PAP-212"]["milestoneId"] != ms_eval and "PAP-212:milestone" not in done_fixes:
    fixes.append(("PAP-212", {"projectMilestoneId": ms_eval}, "PAP-212:milestone", "milestone Core adoptions decided -> Evaluation process (blocks PAP-67 due 09-20)"))
print("fixes:", [(f[0], f[3]) for f in fixes])
if not DRY:
    for k, inp, what, note in fixes:
        d = r5.gql("mutation($id: String!, $i: IssueUpdateInput!) { u: issueUpdate(id: $id, input: $i) { success } }", {"id": r5.BY_ID[k]["id"], "i": inp})
        if d["u"]["success"]:
            ch["fieldChanges"].append({"what": what, "issue": k, "note": note}); print("fixed", k, note)
        r5.save_changes(ch)

# ---- umbrella comments on L parents ----
DOCS = {d["project"]: d["url"] for d in ch.get("documents", [])}
PARENTS = {"PAP-199": "migration", "PAP-202": "migration", "PAP-203": "migration", "PAP-205": "migration", "PAP-206": "migration", "PAP-207": "migration",
           "PAP-213": "libraries", "PAP-214": "libraries", "PAP-215": "libraries"}
pending = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "pending-issues.json")))
done_comments = {c["issue"] for c in ch["comments"]}
todo = []
for parent, proj in PARENTS.items():
    if parent in done_comments: continue
    kids = [p for p in pending if p["parent"] == parent]
    lines = "\n".join(f"{n+1}. **WP{n+1}** ({k['size']}, Type/{k['type']}): {k['title']}" for n, k in enumerate(kids))
    body = (f"**Work packages pending as sub-issues.** This L issue was split into {len(kids)} work packages on 2026-09-17, but Linear returned "
            f"`USAGE_LIMIT_EXCEEDED` (free-plan issue cap) for every `issueCreate`. Full specs (Goal, Scope, Spec, Interface contract, Definition of done, "
            f"Test plan, Demo, Edge cases, Dependencies, Agent, Size) live in the project document [{DOCS.get(proj, 'Round 2 pending issues')}]({DOCS.get(proj, '')}) "
            f"and in `round2/agent5/pending-issues.json`; `round2/agent5/create_issues.py` creates them idempotently once the cap lifts.\n\n{lines}\n\n"
            f"Until then: build in this order on branches `{parent}/wp<n>-<slug>`, one PR per work package, and report each here with the PR link. "
            f"The parent's Definition of done is the integration test across all work packages.")
    todo.append((parent, body))
print("comments to post:", [t[0] for t in todo])
if not DRY:
    for i in range(0, len(todo), 5):
        batch = todo[i:i + 5]
        vardefs = []; parts = []; variables = {}
        for j, (parent, body) in enumerate(batch):
            vardefs.append(f"$i{j}: CommentCreateInput!"); parts.append(f"c{j}: commentCreate(input: $i{j}) {{ success comment {{ id }} }}")
            variables[f"i{j}"] = {"issueId": r5.BY_ID[parent]["id"], "body": body}
        d = r5.gql("mutation(" + ", ".join(vardefs) + ") { " + " ".join(parts) + " }", variables)
        for j, (parent, body) in enumerate(batch):
            if d[f"c{j}"]["success"]:
                ch["comments"].append({"issue": parent, "id": d[f"c{j}"]["comment"]["id"]}); print("comment", parent)
        r5.save_changes(ch)
