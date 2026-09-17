"""Create the security mitigation issues (idempotent). Falls back to pending-issues.json on USAGE_LIMIT_EXCEEDED."""
import sys, os, re, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lin, specs
ch=lin.load_changes()
created={c["key"]:c for c in ch["created"]}
def resolve(desc, ids):
    return re.sub(r"\{\{([^}]+)\}\}", lambda m: ids.get(m.group(1), f"[{m.group(1)}]"), desc)
pending=[]
for it in specs.ISSUES:
    if it["key"] in created: print("already created", it["key"], created[it["key"]]["identifier"]); continue
    ex=lin.existing_title(it["project"], it["title"])
    if ex:
        print("exists in Linear", it["key"], ex["identifier"]); ch["created"].append({"key":it["key"],"identifier":ex["identifier"],"id":ex["id"],"url":None,"title":it["title"],"preexisting":True}); created[it["key"]]=ch["created"][-1]; lin.save_changes(ch); continue
    labels=[lin.LABELS["Phase"] if False else None]
    label_ids=[lin.LABELS[it["phase"]], lin.LABELS[it["type"]]]+[lin.LABELS[s] for s in it["surfaces"]]
    inp={"teamId":lin.TEAM,"title":it["title"],"description":resolve(it["description"],{k:v["identifier"] for k,v in created.items()}),
         "priority":it["priority"],"projectId":lin.PROJECTS[it["project"]]["id"],"projectMilestoneId":lin.milestone_id(it["project"],it["milestone"]),
         "stateId":lin.STATES[it["state"]],"labelIds":label_ids}
    try:
        d=lin.gql("mutation($i: IssueCreateInput!){ c: issueCreate(input:$i){ success issue{ id identifier url } } }",{"i":inp})
    except lin.UsageLimit as e:
        print("USAGE_LIMIT_EXCEEDED for", it["key"]); pending.append(it); continue
    iss=d["c"]["issue"]; print("created", it["key"], iss["identifier"])
    ch["created"].append({"key":it["key"],"identifier":iss["identifier"],"id":iss["id"],"url":iss["url"],"title":it["title"],"project":it["project"]})
    created[it["key"]]=ch["created"][-1]; lin.save_changes(ch)
if pending:
    pf=os.path.join(os.path.dirname(os.path.abspath(__file__)),"pending-issues.json")
    json.dump(pending, open(pf,"w"), indent=1)
    ch["pendingIssuesFile"]=pf
    ch["notes"].append(f"Linear returned USAGE_LIMIT_EXCEEDED (free-plan issue cap) for {len(pending)} security issues; full specs saved in {pf} and published as a Linear document.")
    lin.save_changes(ch)
print("created", len(created), "pending", len(pending))

# Second pass (runs only when issues exist): resolve {{key}} placeholders and add blocks relations. Idempotent.
if created and not pending:
    ids={k:v["identifier"] for k,v in created.items()}
    done_rel={(r["from"],r["to"]) for r in ch["relations"]}
    for it in specs.ISSUES:
        me=created[it["key"]]
        if me.get("preexisting"): continue
        if "{{" in it["description"] and me["id"] not in ch["updated"]:
            lin.gql("mutation($id:String!,$i:IssueUpdateInput!){ u: issueUpdate(id:$id,input:$i){ success } }",{"id":me["id"],"i":{"description":resolve(it["description"],ids)}})
            ch["updated"].append(me["id"]); lin.save_changes(ch); print("resolved placeholders", me["identifier"])
        def rel(frm_key, to_key):
            frm=created.get(frm_key,{}).get("identifier", frm_key); to=created.get(to_key,{}).get("identifier", to_key)
            if (frm,to) in done_rel: return
            frm_id=created.get(frm_key,{}).get("id") or lin.BY_ID[frm]["id"]; to_id=created.get(to_key,{}).get("id") or lin.BY_ID[to]["id"]
            d=lin.gql("mutation($i: IssueRelationCreateInput!){ r: issueRelationCreate(input:$i){ success issueRelation{ id } } }",{"i":{"issueId":frm_id,"relatedIssueId":to_id,"type":"blocks"}})
            ch["relations"].append({"id":d["r"]["issueRelation"]["id"],"from":frm,"to":to}); done_rel.add((frm,to)); lin.save_changes(ch); print("relation", frm, "blocks", to)
        for b in it["blockedBy"]: rel(b, it["key"])
        for b in it["blocks"]: rel(it["key"], b)
