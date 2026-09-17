import json, sys
from r2lib import *
import specs_appshell, specs_datalayer, specs_forge
ALL={}
for m in (specs_appshell, specs_datalayer, specs_forge): ALL.update(m.SPECS)
ch=load_changes()
done=set(ch["updated"])
todo=[(k,render(v)) for k,v in ALL.items() if BY_ID[k]["id"] not in done]
print("to update:",len(todo))
B=5
for i in range(0,len(todo),B):
    batch=todo[i:i+B]
    parts=[]; vars_={}
    for j,(k,desc) in enumerate(batch):
        parts.append('u%d: issueUpdate(id:$id%d, input:{description:$d%d}){ success issue{ identifier } }'%(j,j,j))
        vars_["id%d"%j]=BY_ID[k]["id"]; vars_["d%d"%j]=desc
    q="mutation("+",".join("$id%d:String!,$d%d:String!"%(j,j) for j in range(len(batch)))+"){ "+" ".join(parts)+" }"
    res=gql(q,vars_)
    for j,(k,_) in enumerate(batch):
        r=res["u%d"%j]
        if not r["success"]: print("FAILED",k,r); continue
        ch["updated"].append(BY_ID[k]["id"]); print("updated",k,r["issue"]["identifier"])
    save_changes(ch)
print("total updated ids:",len(ch["updated"]))
