import json, os, re, sys, time, urllib.request, urllib.error
R2=os.environ.get("PAPEROS_PLAN_DIR", ".") + "/round2"
CH=os.path.join(R2,"changes-characters.json"); D=os.path.join(R2,"characters")
URL="https://api.linear.app/graphql"; KEY=os.environ.get("LINEAR_API_KEY","placeholder")
PROJECT="c7b318e7-840a-4aca-99dd-2b5aed3fc26b"
snap=json.load(open(os.path.join(R2,"linear-snapshot.json"))); new=json.load(open(os.path.join(R2,"_new_full.json")))
known={i["identifier"] for i in snap["issues"]}|{i["identifier"] for i in new}
# validate identifiers
bad={}
for f in sorted(os.listdir(D)):
    if not f.endswith(".md"): continue
    txt=open(os.path.join(D,f)).read()
    refs=set(re.findall(r"PAP-\d+",txt))
    for a,b in re.findall(r"PAP-(\d+) to PAP-(\d+)",txt):
        refs|={f"PAP-{n}" for n in range(int(a),int(b)+1)}
    miss=sorted(r for r in refs if r not in known)
    if miss: bad[f]=miss
if bad: print("UNKNOWN IDENTIFIERS", bad); sys.exit(1)
print("identifier check ok")
_last=[0.0]
def gql(q,v=None):
    for attempt in range(6):
        w=0.35-(time.time()-_last[0]);
        if w>0: time.sleep(w)
        req=urllib.request.Request(URL,data=json.dumps({"query":q,"variables":v or {}}).encode(),headers={"Authorization":KEY,"Content-Type":"application/json"})
        try:
            with urllib.request.urlopen(req,timeout=120) as r: data=json.loads(r.read().decode())
        except urllib.error.HTTPError as e:
            raw=e.read().decode(); _last[0]=time.time()
            if e.code==429 or "RATELIMITED" in raw: print("rate limited; 60s",file=sys.stderr); time.sleep(60); continue
            raise RuntimeError("HTTP %s %s"%(e.code,raw[:800]))
        _last[0]=time.time()
        if data.get("errors"):
            codes=[(x.get("extensions") or {}).get("code") for x in data["errors"]]
            if "RATELIMITED" in codes: print("RATELIMITED; 60s",file=sys.stderr); time.sleep(60); continue
            raise RuntimeError(json.dumps(data["errors"])[:1500])
        return data["data"]
    raise RuntimeError("retries exhausted")
ch=json.load(open(CH)) if os.path.exists(CH) else {"created":[],"relations":[],"documents":[],"updated":[],"notes":[],"requests":0}
def save(): json.dump(ch,open(CH+".tmp","w"),indent=1); os.replace(CH+".tmp",CH)
have={d["title"]:d for d in ch["documents"]}
# existing docs on the project (dedupe against other sessions)
live=gql('{ project(id:"%s"){ content documents{ nodes{ id title url } } } }'%PROJECT); ch["requests"]=ch.get("requests",0)+1
for n in live["project"]["documents"]["nodes"]:
    have.setdefault(n["title"],{"id":n["id"],"url":n["url"],"title":n["title"],"project":"Agent Characters & Orgs","preexisting":True})
LEADS=[("atlas","Character sheet: Atlas — Chief Architect and Orchestrator"),("forge","Character sheet: Forge — Platform Engineer"),("iris","Character sheet: Iris — Design Systems Lead"),("quill","Character sheet: Quill — Spec and Documentation Lead"),("sentinel","Character sheet: Sentinel — Quality Lead"),("nova","Character sheet: Nova — Product Systems Engineer"),("ledger","Character sheet: Ledger — Business Systems Lead"),("beacon","Character sheet: Beacon — Growth Lead"),("scout","Character sheet: Scout — Library and Migration Researcher")]
def create(title,content,key):
    if title in have and not have[title].get("preexisting"):
        print("exists",title,have[title]["url"]); return have[title]
    if title in have:  # created by someone else: update content instead of duplicating
        d=gql('mutation($id:String!,$i:DocumentUpdateInput!){ d: documentUpdate(id:$id,input:$i){ success document{ id url title } } }',{"id":have[title]["id"],"i":{"content":content}})["d"]["document"]
        ch["requests"]+=1; rec={"key":key,"id":d["id"],"url":d["url"],"title":d["title"],"project":"Agent Characters & Orgs","updatedExisting":True}
    else:
        d=gql('mutation($i:DocumentCreateInput!){ d: documentCreate(input:$i){ success document{ id url title } } }',{"i":{"title":title,"content":content,"projectId":PROJECT}})["d"]["document"]
        ch["requests"]+=1; rec={"key":key,"id":d["id"],"url":d["url"],"title":d["title"],"project":"Agent Characters & Orgs"}
    ch["documents"]=[x for x in ch["documents"] if x["title"]!=title]+[rec]; have[title]=rec; save(); print("created",title,d["url"]); return rec
urls={}
for key,title in LEADS:
    rec=create(title,open(os.path.join(D,key+".md")).read(),"character/"+key); urls[key]=rec["url"]
roster=open(os.path.join(D,"roster.md")).read()
for k,u in urls.items(): roster=roster.replace("{{%s_url}}"%k,u)
assert "{{" not in roster
open(os.path.join(D,"roster.resolved.md"),"w").write(roster)
rrec=create("PaperOS Agent Roster (org chart and character index)",roster,"roster")
# project content update
content=live["project"]["content"] or ""
marker="## Character sheets"
section=marker+"\n\nOne Linear document per lead (mission, sub-characters, tools and MCP servers, access scopes, skills, memory, owned issues, escalation rules, ready-to-use system prompt, definition of a good day). Index and org chart: [PaperOS Agent Roster](%s).\n\n"%rrec["url"]
section+="\n".join("* [%s](%s)"%(t.replace("Character sheet: ",""),urls[k]) for k,t in LEADS)
section+="\n\nThese sheets are the input for `agents/roster-v1/lead-prompts` (PAP-104) and the handbook pages of PAP-112; the routing table in the Roster stands in for the `Character` label group until `pm-linear/workspace-reconcile` creates it."
if marker in content:
    content=content[:content.index(marker)].rstrip()+"\n\n"+section
else:
    content=content.rstrip()+"\n\n"+section
if not any(u.get("what")=="project-content-character-sheets" for u in ch["updated"]) or True:
    r=gql('mutation($id:String!,$i:ProjectUpdateInput!){ p: projectUpdate(id:$id,input:$i){ success project{ id url } } }',{"id":PROJECT,"i":{"content":content}}); ch["requests"]+=1
    ch["updated"]=[u for u in ch["updated"] if u.get("what")!="project-content-character-sheets"]+[{"project":PROJECT,"what":"project-content-character-sheets","url":r["p"]["project"]["url"],"success":r["p"]["success"]}]
    save(); print("project updated",r["p"])
ch["notes"]=["No issues created: team PAP is at the free-plan issue cap (275 issues; every round-2 issueCreate returned USAGE_LIMIT_EXCEEDED), and the character sheets surfaced no gap that is not already specified in the pending-issues documents (agents, security, pm-linear).","Ownership computed from the Agent line of every canonical issue PAP-13..PAP-279; table in round2/_ownership.txt and _ownership.json.","No issue states, labels, relations, views or PAP-1..PAP-12 touched."]
save(); print(json.dumps(ch,indent=1))
