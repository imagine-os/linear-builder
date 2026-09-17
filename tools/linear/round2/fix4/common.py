import json, os, time, sys, urllib.request
KEY=os.environ.get("LINEAR_API_KEY","placeholder")
R2=os.environ.get("PAPEROS_PLAN_DIR", ".") + "/round2"
CH=os.path.join(R2,"changes-fix-FIX-4 deferred-set-consistency.json")
DEFERRED=[23,137,149,157,158,182,185,190,191,193,194,195,196,197,203,204,206,207,218,221,222,230,231,232,235,276,277,278]
DEFERRED_IDS=[f"PAP-{n}" for n in DEFERRED]
NOTE="Deferred to v0.2 by the Execution Schedule (NJ-14 stop-loss 09-27 can reinstate). Not claimable before 10-01."
SCHED_DOC="1623cb9d-9ed5-4af1-aa62-f520948fc21c"
def load_ch():
    if os.path.exists(CH): return json.load(open(CH))
    return {"fix":"FIX-4 deferred-set-consistency","startedAt":"2026-09-17T06:25Z","labelsCreated":[],"relationsDeleted":[],"issuesUpdated":[],"documentUpdates":[],"created":[],"notes":[],"requestsUsed":0}
def save_ch(ch): json.dump(ch,open(CH,"w"),indent=1)
REQ={"n":0}
def gql(q,v=None):
    for attempt in range(6):
        body=json.dumps({"query":q,"variables":v}).encode()
        req=urllib.request.Request("https://api.linear.app/graphql",data=body,headers={"Authorization":KEY,"Content-Type":"application/json"})
        REQ["n"]+=1
        try:
            with urllib.request.urlopen(req,timeout=90) as r: d=json.load(r)
        except urllib.error.HTTPError as e:
            txt=e.read().decode()
            if e.code==429 or "RATELIMITED" in txt: print("rate limited, sleeping 60s",flush=True); time.sleep(60); continue
            print("HTTP",e.code,txt[:800]); sys.exit(1)
        time.sleep(0.3)
        if d.get("errors"):
            if any(er.get("extensions",{}).get("code")=="RATELIMITED" for er in d["errors"]): print("RATELIMITED, sleeping 60s",flush=True); time.sleep(60); continue
            print("GQL errors:",json.dumps(d["errors"])[:2000]); sys.exit(1)
        return d["data"]
    sys.exit("retries exhausted")
