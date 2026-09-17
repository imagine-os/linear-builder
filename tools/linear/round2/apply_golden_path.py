import json, os, sys, time, glob, re
sys.path.insert(0, os.environ.get("PAPEROS_PLAN_DIR", ".") + "")
from lin import gql

R2 = os.environ.get("PAPEROS_PLAN_DIR", ".") + "/round2"
CH = os.path.join(R2, "changes-golden-path.json")
TEAM = "0ee78894-89f8-4376-a829-f8685dbc1868"
PROJECTS = {"app-shell": "9358cbfb-37a6-4636-be1d-a055e9e39ba9", "spec-builder": "2751f85d-339c-4b19-868d-eae91b31334c"}
PNAME = {"app-shell": "Universal App Shell & Repo Template", "spec-builder": "Spec Builder"}
MILESTONES = {"Multi-monitor and PWA polish": "b0c6dcc4-327d-4a5b-a0c2-5f3a31dd90cc",
              "Codegen and conformance tests": "1d3f21ec-ea83-4f8a-9ff5-af9848a1cabc"}
LABELS = {"P0": "7c4369ee-8fca-4ed1-b4c7-4a0ecae0324e", "P1": "09af3067-2c65-4ab5-a915-f553a4931ec1", "P2": "7fb0186c-e615-4588-a9d5-7f1031791e82",
          "Build": "562d6a37-6bd0-4680-a1a6-6bc55e642d21", "Spec": "c08922b7-13bb-4a44-ac15-14943d22c8d1", "Infra": "9b3bfd13-b0ab-415e-aad7-e8d351c5750e",
          "Review": "827147a3-27e2-4225-a4ca-d6a1b4b7d5a8", "Docs": "b03b6d66-4bad-4021-9f20-4f39df1d290a", "Research": "6fbe3c0c-2641-44ae-a660-863a633297ac",
          "Developer": "ff4b5d8d-f236-4d15-a75a-0eacc09e988e", "Agent": "bb6ce0ab-cc34-4fc2-9973-ade330d2af8f",
          "Customer": "9526e961-186c-4ebb-8c10-102d588a1bb6", "Staff": "d043f950-f433-45c4-9bfe-65b9813369f8"}
STATES = {"Ready for Claude": "9f24c1d6-b544-4d67-be55-6a1da5323ee2", "Backlog": "0aed245d-f842-423f-bb5c-246061bf9b1b"}
PAP5_ID = "8468d71c-8653-434a-ba55-469056f2c243"
DOC_TITLE = "New App in Ten Minutes: the golden path"

snap = json.load(open(os.path.join(R2, "linear-snapshot.json")))
ids = {i["identifier"]: i["id"] for i in snap["issues"]}
titles = {(i["projectName"], i["title"]) for i in snap["issues"]}
for f in glob.glob(os.path.join(R2, "changes-*.json")):
    if f.endswith("changes-golden-path.json"):
        continue
    for c in json.load(open(f)).get("created", []) or []:
        if c.get("identifier") and c.get("id"):
            ids[c["identifier"]] = c["id"]
        if c.get("title"):
            titles.add((c.get("project"), c["title"]))

ch = json.load(open(CH)) if os.path.exists(CH) else {"documents": [], "created": [], "relations": [], "comments": [], "pendingIssues": [], "notes": []}
def save(): json.dump(ch, open(CH, "w"), indent=1)

issues = json.load(open(os.path.join(R2, "golden-path-issues.json")))
bykey = {it["key"]: it for it in issues}
step = sys.argv[1]

def doc_body():
    content = open(os.path.join(R2, "golden-path-doc.md")).read()
    return content.split("\n", 1)[1].lstrip("\n")

if step == "doc":
    if any(d["key"] == "golden-path-doc" for d in ch["documents"]):
        print("doc exists", [d for d in ch["documents"] if d["key"] == "golden-path-doc"]); sys.exit()
    r = gql('mutation($i:DocumentCreateInput!){ documentCreate(input:$i){ success document{ id url title } } }',
            {"i": {"title": DOC_TITLE, "content": doc_body(), "projectId": PROJECTS["app-shell"]}})
    d = r["documentCreate"]["document"]; print(r["documentCreate"]["success"], d)
    ch["documents"].append({"key": "golden-path-doc", "project": PNAME["app-shell"], **d}); save()

elif step == "issues":
    done = {c["key"] for c in ch["created"]}
    for it in issues:
        if it["key"] in done: print("skip", it["key"]); continue
        if (PNAME[it["project"]], it["title"]) in titles: print("DUP title exists", it["key"]); continue
        inp = {"teamId": TEAM, "title": it["title"], "description": it["description"], "priority": it["priority"],
               "projectId": PROJECTS[it["project"]], "projectMilestoneId": MILESTONES[it["milestone"]],
               "stateId": STATES[it["state"]],
               "labelIds": [LABELS[it["phase"]], LABELS[it["type"]]] + [LABELS[s] for s in it["surfaces"]]}
        try:
            r = gql('mutation($i:IssueCreateInput!){ issueCreate(input:$i){ success issue{ id identifier url } } }', {"i": inp})
            iss = r["issueCreate"]["issue"]; print("created", it["key"], iss["identifier"])
            ch["created"].append({"key": it["key"], "project": PNAME[it["project"]], "title": it["title"], **iss}); save()
        except RuntimeError as e:
            msg = str(e); print("FAILED", it["key"], msg[:240])
            ch["notes"].append(f"issueCreate failed for {it['key']}: {msg[:200]}"); save()
            if "USAGE_LIMIT_EXCEEDED" in msg or "usage limit" in msg:
                break
        time.sleep(0.35)

elif step == "relations":
    byk = {c["key"]: c for c in ch["created"]}
    def resolve(ref):
        if ref in byk: return byk[ref]["identifier"], byk[ref]["id"]
        if ref in ids: return ref, ids[ref]
        return None
    done = {(r["from"], r["to"]) for r in ch["relations"]}
    pairs = []
    for it in issues:
        me = byk.get(it["key"])
        if not me: continue
        for b in it["blockedBy"]:
            x = resolve(b)
            if x: pairs.append((x[0], x[1], me["identifier"], me["id"]))
            else: ch["notes"].append(f"relation skipped, {b} not created: {b} blocks {it['key']}")
        for b in it["blocks"]:
            x = resolve(b)
            if x: pairs.append((me["identifier"], me["id"], x[0], x[1]))
            else: ch["notes"].append(f"relation skipped, {b} not created: {it['key']} blocks {b}")
    pairs = [p for p in pairs if (p[0], p[2]) not in done]
    print(len(pairs), "relations to create")
    for i in range(0, len(pairs), 10):
        chunk = pairs[i:i+10]
        q = "mutation{" + " ".join(f'r{j}: issueRelationCreate(input:{{issueId:"{a}", relatedIssueId:"{b}", type: blocks}}){{ success issueRelation{{ id }} }}' for j, (_, a, _, b) in enumerate(chunk)) + "}"
        r = gql(q)
        for j, (fa, _, tb, _) in enumerate(chunk):
            rel = r[f"r{j}"]["issueRelation"]; ch["relations"].append({"id": rel["id"], "from": fa, "to": tb})
        save(); print("relations", len(ch["relations"])); time.sleep(0.35)

elif step == "pending":
    created = {c["key"] for c in ch["created"]}
    pend = [it for it in issues if it["key"] not in created]
    ch["pendingIssues"] = [p["key"] for p in pend]; save()
    if not pend: print("nothing pending"); sys.exit()
    json.dump(pend, open(os.path.join(R2, "pending-issues-golden-path.json"), "w"), indent=1)
    if any(d["key"] == "pending-doc" for d in ch["documents"]): print("pending doc exists"); sys.exit()
    parts = [f"Linear refused `issueCreate` with `USAGE_LIMIT_EXCEEDED` (workspace issue cap) on 2026-09-17. These {len(pend)} golden path issues are fully specified here and in `round2/pending-issues-golden-path.json`; create them verbatim once the cap lifts, then add the `blocks` relations listed under each. They are referenced from the document *New App in Ten Minutes: the golden path* and are the resolution path of PAP-5.\n"]
    for it in pend:
        parts.append(f"\n---\n\n## {it['title']}\n\n**Project** {PNAME[it['project']]} · **Milestone** {it['milestone']} · **Labels** {it['phase']}, {it['type']}, {', '.join(it['surfaces'])} · **Priority** {it['priority']} · **State** {it['state']} · **Key** `{it['key']}`\n\n**Blocked by** {', '.join(it['blockedBy']) or 'none'} · **Blocks** {', '.join(it['blocks']) or 'none'}\n\n{it['description']}\n")
    r = gql('mutation($i:DocumentCreateInput!){ documentCreate(input:$i){ success document{ id url title } } }',
            {"i": {"title": f"Round 2 pending issues: golden path ({len(pend)})", "content": "".join(parts), "projectId": PROJECTS["app-shell"]}})
    d = r["documentCreate"]["document"]; print(r["documentCreate"]["success"], d)
    ch["documents"].append({"key": "pending-doc", "project": PNAME["app-shell"], "pendingKeys": [p["key"] for p in pend], **d}); save()

elif step == "docfix":
    # Rewrite section 8 of the golden path document with the real identifiers (or the pending document link).
    doc = next(d for d in ch["documents"] if d["key"] == "golden-path-doc")
    byk = {c["key"]: c for c in ch["created"]}
    pend = next((d for d in ch["documents"] if d["key"] == "pending-doc"), None)
    def ref(key, short):
        c = byk.get(key)
        if c: return f"[{c['identifier']}]({c['url']}) {short}"
        return f"{short} (pending, `{key}`)"
    lines = [
        "New in this round:",
        "",
        "- Universal App Shell & Repo Template: " + "; ".join([
            ref("gp/app-shell/driver", "golden path driver (`paperos create --idea`)"),
            ref("gp/app-shell/provisioning", "golden path provisioning (parallel steps, warm pools, `--resume`)"),
            ref("gp/app-shell/starter-surfaces", "default surfaces starter kit"),
            ref("gp/app-shell/acceptance", "golden path acceptance test"),
            ref("gp/app-shell/upgrade", "`paperos upgrade` so a ten-minute app keeps receiving template fixes")]) + ".",
        "- Spec Builder: " + "; ".join([
            ref("gp/spec-builder/app-interview", "app interview skill (paragraph to `app.spec.yaml`)"),
            ref("gp/spec-builder/entity-pages", "entity-derived page specs"),
            ref("gp/spec-builder/gen-pipeline", "`paperos gen` whole-app pipeline")]) + ".",
    ]
    if pend:
        lines.append(f"- Issues marked pending could not be created today (Linear `USAGE_LIMIT_EXCEEDED`, workspace issue cap); their full specs are in [{pend['title']}]({pend['url']}) and in `round2/pending-issues-golden-path.json`.")
    body = doc_body()
    start = body.index("New in this round (specs in the linked issues):")
    end = body.index("Existing issues on the critical path")
    body = body[:start] + "\n".join(lines) + "\n\n" + body[end:]
    r = gql('mutation($id:String!,$i:DocumentUpdateInput!){ documentUpdate(id:$id, input:$i){ success document{ id url } } }',
            {"id": doc["id"], "i": {"content": body}})
    print(r["documentUpdate"]["success"])
    open(os.path.join(R2, "golden-path-doc.published.md"), "w").write("# " + DOC_TITLE + "\n\n" + body)
    ch["notes"].append("golden-path-doc section 8 updated with issue identifiers"); save()

elif step == "comment":
    if any(c.get("issue") == "PAP-5" for c in ch["comments"]): print("comment exists"); sys.exit()
    doc = next(d for d in ch["documents"] if d["key"] == "golden-path-doc")
    pend = next((d for d in ch["documents"] if d["key"] == "pending-doc"), None)
    created = ch["created"]
    lines = [f"**Resolution path for this issue: [New App in Ten Minutes: the golden path]({doc['url']})** (document on the Universal App Shell & Repo Template project).",
             "",
             "The answer to \"how quickly do we get from blank screen to electrons\" is now a specified, measurable path: `paperos create <name> --idea \"<one paragraph>\"` runs a six-question interview, writes `app.spec.yaml`, generates every page, hook, policy, test and seed, provisions repo, mirror, CI, Pages, Linear project, database and preview slot in parallel, opens PR #1, and waits for gates 1 to 4. Acceptance test: **a new app passes gates 1 to 4 and deploys to a preview URL in under 10 minutes of wall clock**, run nightly on three canned ideas; every generated app ships a customer portal and a staff console with auth, grid views, comments and docs from minute one. PAP-29 keeps measuring the realistic four-hour drill on top of it.",
             "",
             "Issues that make it real (all with full specs, labels, milestones and blocking relations):"]
    for c in created:
        lines.append(f"- [{c['identifier']}]({c['url']}) {c['title']}")
    if pend:
        lines.append(f"- {len(pend['pendingKeys'])} further issues could not be created today because Linear returned `USAGE_LIMIT_EXCEEDED` (workspace issue cap); their complete specs are in [{pend['title']}]({pend['url']}) and will be created when the cap lifts.")
    lines += ["", "Existing critical path: PAP-13, PAP-16, PAP-114, PAP-115, PAP-117, PAP-118, PAP-119, PAP-120, PAP-122, PAP-22, PAP-15, PAP-26, PAP-78, PAP-81, PAP-82, PAP-239, PAP-240, PAP-55, PAP-57, PAP-59, PAP-161, PAP-165, PAP-131, PAP-128, PAP-264, PAP-266. Title and state of this issue are unchanged; it stays the scoreboard."]
    r = gql('mutation($i:CommentCreateInput!){ commentCreate(input:$i){ success comment{ id url } } }',
            {"i": {"issueId": PAP5_ID, "body": "\n".join(lines)}})
    c = r["commentCreate"]["comment"]; print(r["commentCreate"]["success"], c)
    ch["comments"].append({"issue": "PAP-5", **c}); save()
