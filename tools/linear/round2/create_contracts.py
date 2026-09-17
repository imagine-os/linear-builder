import json, os, sys, time
sys.path.insert(0, os.environ.get("PAPEROS_PLAN_DIR", ".") + "")
from lin import gql

R2 = os.environ.get("PAPEROS_PLAN_DIR", ".") + "/round2"
CH = os.path.join(R2, "changes-contracts.json")
TEAM = "0ee78894-89f8-4376-a829-f8685dbc1868"
DATA_LAYER = "64e49138-b979-4650-b5f9-1987134231f8"
PROJECTS = {"data-layer": DATA_LAYER, "app-shell": "9358cbfb-37a6-4636-be1d-a055e9e39ba9"}
MILESTONES = {"Postgres + Drizzle baseline": "fe9ae139-9a2d-452b-a6a7-eb4ae0228659",
              "Template scaffolds and runs on web": "c48b2fa3-aebc-4520-877d-7f301322bcc9"}
LABELS = {"P0": "7c4369ee-8fca-4ed1-b4c7-4a0ecae0324e", "Spec": "c08922b7-13bb-4a44-ac15-14943d22c8d1",
          "Developer": "ff4b5d8d-f236-4d15-a75a-0eacc09e988e", "Agent": "bb6ce0ab-cc34-4fc2-9973-ade330d2af8f",
          "Customer": "9526e961-186c-4ebb-8c10-102d588a1bb6", "Staff": "d043f950-f433-45c4-9bfe-65b9813369f8"}
STATES = {"Ready for Claude": "9f24c1d6-b544-4d67-be55-6a1da5323ee2", "Backlog": "0aed245d-f842-423f-bb5c-246061bf9b1b"}

snap = json.load(open(os.path.join(R2, "linear-snapshot.json")))
ids = {i["identifier"]: i["id"] for i in snap["issues"]}
titles = {(i["projectName"], i["title"]) for i in snap["issues"]}
for f in ["changes-0.json", "changes-1.json"]:
    for c in json.load(open(os.path.join(R2, f))).get("created", []):
        ids[c["identifier"]] = c["id"]
ids.update({"PAP-267": "5ed9573f-1f5f-4f2f-b3d4-2b881f502cf4", "PAP-268": "d64bd8d8-488f-49a2-bad2-eae6b127ca7f",
            "PAP-279": "98cd2929-525b-4866-995c-54926ffc6c08", "PAP-264": "e03764a3-17a9-4ea3-8313-e3312d0a502d",
            "PAP-222": "095991a8-2286-4529-919e-7d3eeb32489e", "PAP-239": "9ff9bb9e-5c89-43a0-b5e4-2b2a97e4fb85"})
PNAME = {"data-layer": "Data Layer & Database", "app-shell": "Universal App Shell & Repo Template"}

ch = json.load(open(CH)) if os.path.exists(CH) else {"documents": [], "created": [], "relations": [], "pendingIssues": [], "notes": []}
def save(): json.dump(ch, open(CH, "w"), indent=1)

step = sys.argv[1]
issues = json.load(open(os.path.join(R2, "contracts-issues.json")))

if step == "doc":
    if any(d["key"] == "contracts-doc" for d in ch["documents"]):
        print("doc exists", [d for d in ch["documents"] if d["key"] == "contracts-doc"]); sys.exit()
    content = open(os.path.join(R2, "contracts-doc.md")).read()
    body = content.split("\n", 1)[1].lstrip("\n")  # title comes from the document title field
    r = gql('mutation($i:DocumentCreateInput!){ documentCreate(input:$i){ success document{ id url title } } }',
            {"i": {"title": "PaperOS Interface & Data Contracts", "content": body, "projectId": DATA_LAYER}})
    d = r["documentCreate"]["document"]; print(r["documentCreate"]["success"], d)
    ch["documents"].append({"key": "contracts-doc", **d}); save()

elif step == "issues":
    done = {c["key"] for c in ch["created"]}
    for it in issues:
        if it["key"] in done: print("skip", it["key"]); continue
        if (PNAME[it["project"]], it["title"]) in titles: print("DUP title in snapshot", it["key"]); continue
        inp = {"teamId": TEAM, "title": it["title"], "description": it["description"], "priority": it["priority"],
               "projectId": PROJECTS[it["project"]], "projectMilestoneId": MILESTONES[it["milestone"]],
               "stateId": STATES[it["state"]],
               "labelIds": [LABELS[it["phase"]], LABELS[it["type"]]] + [LABELS[s] for s in it["surfaces"]]}
        try:
            r = gql('mutation($i:IssueCreateInput!){ issueCreate(input:$i){ success issue{ id identifier url } } }', {"i": inp})
            iss = r["issueCreate"]["issue"]; print("created", it["key"], iss["identifier"])
            ch["created"].append({"key": it["key"], "project": PNAME[it["project"]], "title": it["title"], **iss}); save()
        except RuntimeError as e:
            msg = str(e); print("FAILED", it["key"], msg[:200])
            ch["notes"].append(f"issueCreate failed for {it['key']}: {msg[:160]}"); save()
            if "USAGE_LIMIT_EXCEEDED" in msg:
                break
        time.sleep(0.3)

elif step == "relations":
    byk = {c["key"]: c for c in ch["created"]}
    done = {(r["from"], r["to"]) for r in ch["relations"]}
    pairs = []
    for it in issues:
        me = byk.get(it["key"])
        if not me: continue
        for b in it["blocks"]: pairs.append((me["identifier"], me["id"], b, ids[b]))
        for b in it["blockedBy"]: pairs.append((b, ids[b], me["identifier"], me["id"]))
    pairs = [p for p in pairs if (p[0], p[2]) not in done]
    for i in range(0, len(pairs), 10):
        chunk = pairs[i:i+10]
        q = "mutation{" + " ".join(f'r{j}: issueRelationCreate(input:{{issueId:"{a}", relatedIssueId:"{b}", type: blocks}}){{ success issueRelation{{ id }} }}' for j, (_, a, _, b) in enumerate(chunk)) + "}"
        r = gql(q)
        for j, (fa, _, tb, _) in enumerate(chunk):
            rel = r[f"r{j}"]["issueRelation"]; ch["relations"].append({"id": rel["id"], "from": fa, "to": tb})
        save(); print("relations", len(ch["relations"])); time.sleep(0.3)

elif step == "pending":
    created = {c["key"] for c in ch["created"]}
    pend = [it for it in issues if it["key"] not in created]
    if not pend: print("nothing pending"); sys.exit()
    json.dump(pend, open(os.path.join(R2, "pending-issues-contracts.json"), "w"), indent=1)
    if any(d["key"] == "pending-doc" for d in ch["documents"]): print("pending doc exists"); sys.exit()
    parts = [f"Linear refused `issueCreate` with `USAGE_LIMIT_EXCEEDED` (workspace issue cap) on 2026-09-17. These {len(pend)} contract issues are fully specified here and in `round2/pending-issues-contracts.json`; create them verbatim once the cap lifts, then add the `blocks` relations listed under each. They are referenced from the *PaperOS Interface & Data Contracts* document.\n"]
    for it in pend:
        parts.append(f"\n---\n\n## {it['title']}\n\n**Project** {PNAME[it['project']]} · **Milestone** {it['milestone']} · **Labels** {it['phase']}, {it['type']}, {', '.join(it['surfaces'])} · **Priority** {it['priority']} · **State** {it['state']}\n\n**Blocked by** {', '.join(it['blockedBy']) or 'none'} · **Blocks** {', '.join(it['blocks'])}\n\n{it['description']}\n")
    body = "".join(parts)
    r = gql('mutation($i:DocumentCreateInput!){ documentCreate(input:$i){ success document{ id url title } } }',
            {"i": {"title": f"Round 2 pending issues: contracts ({len(pend)})", "content": body, "projectId": DATA_LAYER}})
    d = r["documentCreate"]["document"]; print(r["documentCreate"]["success"], d)
    ch["documents"].append({"key": "pending-doc", "pendingKeys": [p["key"] for p in pend], **d}); save()
