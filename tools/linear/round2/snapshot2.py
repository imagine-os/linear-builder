import os
import json, time, sys
sys.path.insert(0, os.environ.get("PAPEROS_PLAN_DIR", ".") + "")
from lin import gql
TEAM="0ee78894-89f8-4376-a829-f8685dbc1868"
OUT=os.environ.get("PAPEROS_PLAN_DIR", ".") + "/round2/linear-snapshot-2.json"
snap={"takenAt":"2026-09-17T06:05Z","team":{"id":TEAM,"key":"PAP"}}

# issues
ISSUE_Q='''query($cursor:String,$team:ID!){ issues(first:100, after:$cursor, orderBy:createdAt, filter:{team:{id:{eq:$team}}}){
 pageInfo{hasNextPage endCursor}
 nodes{ id identifier title description priority estimate url archivedAt
  state{id name type} labels{nodes{id name}} project{id name} projectMilestone{id name}
  parent{id identifier} children{nodes{identifier}}
  relations{nodes{id type relatedIssue{identifier}}}
  inverseRelations{nodes{id type issue{identifier}}}
 }}}'''
issues=[]; cursor=None
while True:
    d=gql(ISSUE_Q,{"cursor":cursor,"team":TEAM})["issues"]
    for n in d["nodes"]:
        if n.get("archivedAt"): continue
        issues.append({"identifier":n["identifier"],"id":n["id"],"title":n["title"],"description":n["description"],
          "state":n["state"]["name"],"stateType":n["state"]["type"],"priority":n["priority"],"estimate":n["estimate"],
          "labels":[l["name"] for l in n["labels"]["nodes"]],
          "projectId":n["project"]["id"] if n["project"] else None,"projectName":n["project"]["name"] if n["project"] else None,
          "milestone":n["projectMilestone"]["name"] if n["projectMilestone"] else None,
          "milestoneId":n["projectMilestone"]["id"] if n["projectMilestone"] else None,
          "parent":n["parent"]["identifier"] if n["parent"] else None,
          "children":[c["identifier"] for c in n["children"]["nodes"]],
          "url":n["url"],
          "relations":[{"id":r["id"],"type":r["type"],"related":r["relatedIssue"]["identifier"]} for r in n["relations"]["nodes"]],
          "inverseRelations":[{"id":r["id"],"type":r["type"],"from":r["issue"]["identifier"]} for r in n["inverseRelations"]["nodes"]]})
    print("issues so far",len(issues),file=sys.stderr)
    if not d["pageInfo"]["hasNextPage"]: break
    cursor=d["pageInfo"]["endCursor"]; time.sleep(0.3)
snap["issues"]=issues
time.sleep(0.3)
# projects
PROJ_Q='''query($cursor:String){ projects(first:20, after:$cursor){ pageInfo{hasNextPage endCursor}
 nodes{ id name description url targetDate startDate status{name} teams{nodes{id}} projectMilestones(first:10){nodes{id name targetDate}} }}}'''
projects=[]; cursor=None
while True:
    d=gql(PROJ_Q,{"cursor":cursor})["projects"]
    for n in d["nodes"]:
        if not any(t["id"]==TEAM for t in n["teams"]["nodes"]): continue
        projects.append({"id":n["id"],"name":n["name"],"description":n["description"],"url":n["url"],"targetDate":n["targetDate"],"startDate":n["startDate"],"status":n["status"]["name"],
          "milestones":[{"id":m["id"],"name":m["name"],"targetDate":m["targetDate"]} for m in n["projectMilestones"]["nodes"]]})
    if not d["pageInfo"]["hasNextPage"]: break
    cursor=d["pageInfo"]["endCursor"]; time.sleep(0.3)
snap["projects"]=projects
time.sleep(0.3)
d=gql('''query($t:String!){ team(id:$t){ states{nodes{id name type position}} labels{nodes{id name parent{id name} isGroup}} }
 issueLabels(first:100){nodes{id name parent{id name} isGroup team{id}}} }''',{"t":TEAM})
snap["states"]=d["team"]["states"]["nodes"]
snap["labels"]=[{"id":l["id"],"name":l["name"],"group":l["parent"]["name"] if l["parent"] else None,"isGroup":l["isGroup"],"teamId":l["team"]["id"] if l["team"] else None} for l in d["issueLabels"]["nodes"]]
time.sleep(0.3)
docs=[]; cursor=None
while True:
    d=gql('''query($cursor:String){ documents(first:25, after:$cursor){ pageInfo{hasNextPage endCursor} nodes{ id title url project{id name} updatedAt content }}}''',{"cursor":cursor})["documents"]
    docs+=[{"id":n["id"],"title":n["title"],"url":n["url"],"project":n["project"]["name"] if n["project"] else None,"updatedAt":n["updatedAt"],"contentLength":len(n["content"] or ""),"contentHead":(n["content"] or "")[:400]} for n in d["nodes"]]
    if not d["pageInfo"]["hasNextPage"]: break
    cursor=d["pageInfo"]["endCursor"]; time.sleep(0.3)
snap["documents"]=docs
json.dump(snap,open(OUT,"w"),indent=1)
print("issues",len(issues),"projects",len(projects),"states",len(snap["states"]),"labels",len(snap["labels"]),"docs",len(docs))
