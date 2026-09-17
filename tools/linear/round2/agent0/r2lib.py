import json, os, time, re, urllib.request, urllib.error, sys
URL="https://api.linear.app/graphql"
KEY=os.environ.get("LINEAR_API_KEY") or "placeholder"
R2=os.environ.get("PAPEROS_PLAN_DIR", ".") + "/round2"
CHANGES=os.path.join(R2,"changes-0.json")
SNAP=json.load(open(os.path.join(R2,"linear-snapshot.json")))
TEAM=SNAP["team"]["id"]
BY_ID={i["identifier"]:i for i in SNAP["issues"]}
STATES={s["name"]:s["id"] for s in SNAP["states"]}
LABELS={l["name"]:l["id"] for l in SNAP["labels"] if l["teamId"]}
PROJECTS={p["name"]:p for p in SNAP["projects"]}
PKEY={"app-shell":"Universal App Shell & Repo Template","data-layer":"Data Layer & Database","forge":"Version Control & Forge Independence"}
def milestone_id(pkey, name):
    for m in PROJECTS[PKEY[pkey]]["milestones"]:
        if m["name"]==name: return m["id"]
    raise KeyError(name)

def load_changes():
    if os.path.exists(CHANGES): return json.load(open(CHANGES))
    return {"updated":[],"created":[],"relations":[],"projectsUpdated":[]}
def save_changes(c):
    tmp=CHANGES+".tmp"; json.dump(c,open(tmp,"w"),indent=1); os.replace(tmp,CHANGES)

_last=[0.0]
def gql(query, variables=None, retries=8):
    body=json.dumps({"query":query,"variables":variables or {}}).encode()
    for attempt in range(retries):
        wait=0.3-(time.time()-_last[0])
        if wait>0: time.sleep(wait)
        req=urllib.request.Request(URL,data=body,headers={"Authorization":KEY,"Content-Type":"application/json"})
        try:
            with urllib.request.urlopen(req,timeout=120) as r:
                data=json.loads(r.read().decode())
        except urllib.error.HTTPError as e:
            raw=e.read().decode()
            _last[0]=time.time()
            try: data=json.loads(raw)
            except Exception: data={"errors":[{"message":"HTTP %s %s"%(e.code,raw[:300])}]}
            if e.code==429 or "RATELIMITED" in raw:
                print("rate limited; sleeping 60s",file=sys.stderr); time.sleep(60); continue
        except Exception as e:
            print("transport error",e,file=sys.stderr); time.sleep(5); continue
        _last[0]=time.time()
        errs=data.get("errors")
        if errs:
            codes=[(x.get("extensions") or {}).get("code") for x in errs]
            if "RATELIMITED" in codes:
                print("RATELIMITED; sleeping 60s",file=sys.stderr); time.sleep(60); continue
            raise RuntimeError(json.dumps(errs)[:1500])
        return data["data"]
    raise RuntimeError("retries exhausted")

SECTION_ORDER=["Goal","Scope","Spec","Interface contract","Definition of done","Test plan","Demo","Edge cases","Dependencies","Agent","Size"]
def render(sections):
    parts=[]
    for k in SECTION_ORDER:
        v=sections.get(k)
        if not v: raise ValueError("missing section "+k)
        parts.append("**%s**\n\n%s"%(k,v.strip()))
    return "\n\n".join(parts)+"\n"
def wc(text): return len(re.findall(r"\S+",text))
