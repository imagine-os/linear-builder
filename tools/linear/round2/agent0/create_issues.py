import json, sys
from r2lib import *
import children
mode=sys.argv[1]  # children | gaps
PKEY_BY_NAME={v:k for k,v in PKEY.items()}
ch=load_changes()
existing_titles={(i["projectName"],i["title"]) for i in SNAP["issues"]}
created_keys={c["key"] for c in ch["created"]}
created_titles={(c.get("projectName"),c["title"]) for c in ch["created"]}
items=[]
if mode=="children":
    for idx,c in enumerate(children.CHILDREN):
        p=BY_ID[c["parent"]]; pkey=PKEY_BY_NAME[p["projectName"]]
        phase=[l.split("/")[1] for l in p["labels"] if l.startswith("Phase/")][0]
        key="child/%s/%d"%(c["parent"],idx)
        items.append(dict(key=key,title=c["title"],projectId=p["projectId"],projectName=p["projectName"],
            milestoneId=p["milestoneId"],parentId=p["id"],parentKey=c["parent"],
            labels=[phase,c["type"]]+c["surfaces"],priority=p["priority"],state="Backlog",
            description=render(c["sections"])))
else:
    import gaps
    for g in gaps.GAPS:
        pname=PKEY[g["project"]]
        items.append(dict(key="gap/%s/%s"%(g["project"],g["slug"]),title=g["title"],projectId=PROJECTS[pname]["id"],projectName=pname,
            milestoneId=milestone_id(g["project"],g["milestone"]),parentId=None,parentKey=None,
            labels=[g["phase"],g["type"]]+g["surfaces"],priority=g["priority"],state=g.get("state","Backlog"),
            description=render(g["sections"])))
todo=[]
for it in items:
    if it["key"] in created_keys: continue
    if (it["projectName"],it["title"]) in existing_titles or (it["projectName"],it["title"]) in created_titles:
        print("SKIP duplicate title:",it["title"][:70]); continue
    todo.append(it)
print(mode,"to create:",len(todo))
B=5
for i in range(0,len(todo),B):
    batch=todo[i:i+B]; parts=[]; vars_={}
    for j,it in enumerate(batch):
        inp={"teamId":TEAM,"title":it["title"],"description":it["description"],"projectId":it["projectId"],
             "projectMilestoneId":it["milestoneId"],"stateId":STATES[it["state"]],"priority":it["priority"],
             "labelIds":[LABELS[l] for l in it["labels"]]}
        if it["parentId"]: inp["parentId"]=it["parentId"]
        vars_["in%d"%j]=inp
        parts.append('c%d: issueCreate(input:$in%d){ success issue{ id identifier url title } }'%(j,j))
    q="mutation("+",".join("$in%d:IssueCreateInput!"%j for j in range(len(batch)))+"){ "+" ".join(parts)+" }"
    res=gql(q,vars_)
    for j,it in enumerate(batch):
        r=res["c%d"%j]
        if not r["success"]: print("FAILED",it["title"][:60],r); continue
        iss=r["issue"]
        ch["created"].append({"key":it["key"],"identifier":iss["identifier"],"id":iss["id"],"url":iss["url"],"parent":it["parentKey"],"title":it["title"],"projectName":it["projectName"]})
        print("created",iss["identifier"],"parent",it["parentKey"],"|",it["title"][:60])
    save_changes(ch)
print("created total:",len(ch["created"]))
