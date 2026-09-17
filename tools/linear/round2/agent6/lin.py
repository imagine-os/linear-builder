import json, os, time, re, sys, urllib.request, urllib.error
URL="https://api.linear.app/graphql"
KEY=os.environ.get("LINEAR_API_KEY") or "placeholder"
R2=os.environ.get("PAPEROS_PLAN_DIR", ".") + "/round2"
CHANGES=os.path.join(R2,"changes-security.json")
SNAP=json.load(open(os.path.join(R2,"linear-snapshot.json")))
NEW=json.load(open(os.path.join(R2,"_new_since_snapshot.json")))
TEAM=SNAP["team"]["id"]
STATES={s["name"]:s["id"] for s in SNAP["states"]}
LABELS={l["name"]:l["id"] for l in SNAP["labels"] if l.get("teamId")}
PROJECTS={p["name"]:p for p in SNAP["projects"]}
BY_ID={i["identifier"]:i for i in SNAP["issues"]}
for n in NEW: BY_ID.setdefault(n["identifier"], {"identifier":n["identifier"],"id":n["id"],"title":n["title"],"projectName":(n.get("project") or {}).get("name")})
def milestone_id(project, name):
    for m in PROJECTS[project]["milestones"]:
        if m["name"]==name: return m["id"]
    raise KeyError(name)
def load_changes():
    if os.path.exists(CHANGES): return json.load(open(CHANGES))
    return {"created":[],"relations":[],"documents":[],"updated":[],"notes":[],"pendingIssuesFile":None}
def save_changes(c):
    tmp=CHANGES+".tmp"; json.dump(c,open(tmp,"w"),indent=1); os.replace(tmp,CHANGES)
_last=[0.0]
class UsageLimit(Exception): pass
def gql(query, variables=None, retries=6):
    body=json.dumps({"query":query,"variables":variables or {}}).encode()
    for attempt in range(retries):
        wait=0.35-(time.time()-_last[0])
        if wait>0: time.sleep(wait)
        req=urllib.request.Request(URL,data=body,headers={"Authorization":KEY,"Content-Type":"application/json"})
        try:
            with urllib.request.urlopen(req,timeout=120) as r: data=json.loads(r.read().decode())
        except urllib.error.HTTPError as e:
            raw=e.read().decode(); _last[0]=time.time()
            if e.code==429 or "RATELIMITED" in raw:
                print("rate limited; sleeping 60s",file=sys.stderr); time.sleep(60); continue
            try: data=json.loads(raw)
            except Exception: raise RuntimeError("HTTP %s %s"%(e.code,raw[:500]))
        except Exception as e:
            print("transport error",e,file=sys.stderr); time.sleep(5); continue
        _last[0]=time.time()
        errs=data.get("errors")
        if errs:
            codes=[(x.get("extensions") or {}).get("code") for x in errs]
            if "RATELIMITED" in codes: print("RATELIMITED; sleeping 60s",file=sys.stderr); time.sleep(60); continue
            if "USAGE_LIMIT_EXCEEDED" in codes: raise UsageLimit(json.dumps(errs)[:400])
            raise RuntimeError(json.dumps(errs)[:1500])
        return data["data"]
    raise RuntimeError("retries exhausted")
def existing_title(project, title):
    t=title.strip().lower()
    for i in BY_ID.values():
        if (i.get("projectName") or "")==project and (i.get("title") or "").strip().lower()==t: return i
    return None
