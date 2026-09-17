import json,os,sys,time,urllib.request
KEY=os.environ.get("LINEAR_API_KEY","placeholder")
CH="changes-fix-FIX-3 child-blockers-umbrella-rule.json"
ch=json.load(open(CH)) if os.path.exists(CH) else {"fix":"FIX-3 child-blockers-umbrella-rule","startedAt":"2026-09-17T06:40Z","relationsCreated":[],"relationsSkipped":[],"issuesUpdated":[],"created":[],"notes":[]}
def save(): json.dump(ch,open(CH,"w"),indent=1)
def gql(q,v=None):
    for attempt in range(6):
        req=urllib.request.Request("https://api.linear.app/graphql",data=json.dumps({"query":q,"variables":v}).encode(),headers={"Authorization":KEY,"Content-Type":"application/json"})
        try:
            with urllib.request.urlopen(req,timeout=90) as r: d=json.load(r)
        except urllib.error.HTTPError as e:
            txt=e.read().decode()
            if e.code==429 or "RATELIMITED" in txt: print("rate limited; sleeping 60s"); time.sleep(60); continue
            print("HTTP",e.code,txt[:800]); return None
        time.sleep(0.3)
        if d.get("errors"):
            if any(er.get("extensions",{}).get("code")=="RATELIMITED" for er in d["errors"]): print("RATELIMITED; sleeping 60s"); time.sleep(60); continue
            print("GQL errors:",json.dumps(d["errors"])[:1500]); return d
        return d
    return None
edges=json.load(open("_fix3_edges.json"))
DROP={("PAP-257","PAP-225"):"would create a new milestone inversion (09-24 -> 09-23); PAP-225 keeps 'PAP-19 hard' in text only, for FIX-1 to place",
      ("PAP-254","PAP-29"):"FIX-1 softens and deletes PAP-88 -> PAP-29 (inversion 09-30 -> 09-29); recreating it at child level would undo that"}
for (b,c),why in DROP.items():
    if not any(s["relation"]==f"{b} blocks {c}" for s in ch["relationsSkipped"]): ch["relationsSkipped"].append({"relation":f"{b} blocks {c}","why":why})
done={r["relation"] for r in ch["relationsCreated"]}
todo=[e for e in edges if (e["blocker"],e["blocked"]) not in DROP and f'{e["blocker"]} blocks {e["blocked"]}' not in done]
print("to create:",len(todo))
for i in range(0,len(todo),10):
    batch=todo[i:i+10]
    q="mutation("+",".join(f"$in{j}: IssueRelationCreateInput!" for j in range(len(batch)))+") { "+" ".join(f"r{j}: issueRelationCreate(input: $in{j}) {{ success issueRelation {{ id }} }}" for j in range(len(batch)))+" }"
    v={f"in{j}":{"issueId":e["blockerId"],"relatedIssueId":e["blockedId"],"type":"blocks"} for j,e in enumerate(batch)}
    d=gql(q,v)
    if d is None: print("batch failed hard; stopping"); save(); sys.exit(1)
    data=d.get("data") or {}
    for j,e in enumerate(batch):
        r=data.get(f"r{j}")
        if r and r.get("success"):
            ch["relationsCreated"].append({"id":r["issueRelation"]["id"],"relation":f'{e["blocker"]} blocks {e["blocked"]}',"rule":e["rule"],"why":e["why"]})
        else:
            print("FAILED",e["blocker"],"->",e["blocked"])
    save()
    print(f"batch {i//10+1}: created so far {len(ch['relationsCreated'])}")
    if d.get("errors"): break
print("done. created:",len(ch["relationsCreated"]))
