import sys; sys.path.insert(0,os.environ.get("PAPEROS_PLAN_DIR", ".") + "/round2/fix4")
from common import *
out={}
# labels on the team
d=gql('{ team(id:"0ee78894-89f8-4376-a829-f8685dbc1868") { labels(first:100) { nodes { id name parent { name } } } } }')
out["labels"]=d["team"]["labels"]["nodes"]
# issues
ids=DEFERRED_IDS+["PAP-192","PAP-96"]
issues={}
for i in range(0,len(ids),10):
    chunk=ids[i:i+10]
    q="{ "+" ".join(f'i{j}: issue(id:"{k}") {{ id identifier priority description updatedAt labels {{ nodes {{ id name }} }} relations {{ nodes {{ id type relatedIssue {{ identifier }} }} }} inverseRelations {{ nodes {{ id type issue {{ identifier }} }} }} }}' for j,k in enumerate(chunk))+" }"
    d=gql(q)
    for j,k in enumerate(chunk): issues[k]=d[f"i{j}"]
out["issues"]=issues
d=gql(f'{{ document(id:"{SCHED_DOC}") {{ id title updatedAt content }} }}')
out["schedDoc"]=d["document"]
json.dump(out,open(R2+"/fix4/_live.json","w"),indent=1)
print("requests",REQ["n"]); print("labels:",[l["name"] for l in out["labels"]])
for k,v in issues.items(): print(k,"prio",v["priority"],[l["name"] for l in v["labels"]["nodes"]],"outbound:",[(r["type"],r["relatedIssue"]["identifier"]) for r in v["relations"]["nodes"]], "desc starts:",repr(v["description"][:60]))
print("sched doc updatedAt",out["schedDoc"]["updatedAt"],len(out["schedDoc"]["content"]))
