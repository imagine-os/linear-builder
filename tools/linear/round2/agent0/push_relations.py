import json, sys
from r2lib import *
# pairs (blocker, blocked) using identifiers; new issues resolved via changes file by key
ch=load_changes()
created={c["key"]:c for c in ch["created"]}
created_by_title={c["title"]:c for c in ch["created"]}
def rid(ref):
    if ref in BY_ID: return BY_ID[ref]["id"], ref
    if ref in created: return created[ref]["id"], created[ref]["identifier"]
    raise KeyError(ref)
existing=set()
for i in SNAP["issues"]:
    for r in i["relations"]:
        if r["type"]=="blocks": existing.add((i["identifier"],r["related"]))
done=set(tuple(x["pair"]) for x in ch.get("relationPairs",[]))
pairs=[tuple(p.split(">")) for p in sys.argv[1:]]
todo=[]
for a,b in pairs:
    ida,ka=rid(a); idb,kb=rid(b)
    if (ka,kb) in existing or (ka,kb) in done: print("skip existing",ka,kb); continue
    todo.append((ida,idb,ka,kb))
print("relations to create:",len(todo))
B=8
ch.setdefault("relationPairs",[])
for i in range(0,len(todo),B):
    batch=todo[i:i+B]; parts=[]; vars_={}
    for j,(ida,idb,ka,kb) in enumerate(batch):
        vars_["in%d"%j]={"issueId":ida,"relatedIssueId":idb,"type":"blocks"}
        parts.append('r%d: issueRelationCreate(input:$in%d){ success issueRelation{ id } }'%(j,j))
    q="mutation("+",".join("$in%d:IssueRelationCreateInput!"%j for j in range(len(batch)))+"){ "+" ".join(parts)+" }"
    try:
        res=gql(q,vars_)
    except RuntimeError as e:
        print("batch error",e); 
        # fall back one by one
        for j,(ida,idb,ka,kb) in enumerate(batch):
            try:
                r=gql('mutation($in:IssueRelationCreateInput!){ r: issueRelationCreate(input:$in){ success issueRelation{ id } } }',{"in":vars_["in%d"%j]})["r"]
                ch["relations"].append(r["issueRelation"]["id"]); ch["relationPairs"].append({"pair":[ka,kb],"id":r["issueRelation"]["id"]}); print("created",ka,"blocks",kb)
            except RuntimeError as e2: print("FAILED",ka,kb,str(e2)[:200])
        save_changes(ch); continue
    for j,(ida,idb,ka,kb) in enumerate(batch):
        r=res["r%d"%j]
        if r["success"]:
            ch["relations"].append(r["issueRelation"]["id"]); ch["relationPairs"].append({"pair":[ka,kb],"id":r["issueRelation"]["id"]}); print("created",ka,"blocks",kb)
        else: print("FAILED",ka,kb,r)
    save_changes(ch)
print("relations total:",len(ch["relations"]))
