import json, os, time, urllib.request, urllib.error, sys

URL="https://api.linear.app/graphql"
KEY=os.environ.get("LINEAR_API_KEY") or "placeholder"
BASE=os.environ.get("PAPEROS_PLAN_DIR", ".") + ""
IDS=os.path.join(BASE,"linear-ids.json")

def load_ids():
    if os.path.exists(IDS):
        return json.load(open(IDS))
    return {"team":{}, "states":{}, "labels":{}, "labelGroups":{}, "projects":{}, "milestones":{}, "issues":{}, "relations":[], "notes":[], "template":None}

def save_ids(d):
    tmp=IDS+".tmp"
    json.dump(d, open(tmp,"w"), indent=1)
    os.replace(tmp, IDS)

def gql(query, variables=None, retries=6):
    body=json.dumps({"query":query,"variables":variables or {}}).encode()
    for attempt in range(retries):
        req=urllib.request.Request(URL, data=body, headers={
            "Authorization":KEY, "Content-Type":"application/json"})
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                data=json.loads(r.read().decode())
        except urllib.error.HTTPError as e:
            raw=e.read().decode()
            try: data=json.loads(raw)
            except Exception: data={"errors":[{"message":"HTTP %s %s"%(e.code,raw[:300])}]}
            if e.code==429:
                time.sleep(60); continue
        except Exception as e:
            time.sleep(5); continue
        errs=data.get("errors")
        if errs:
            codes=[ (x.get("extensions") or {}).get("code") for x in errs ]
            if "RATELIMITED" in codes:
                time.sleep(60); continue
            raise RuntimeError(json.dumps(errs)[:800])
        return data["data"]
    raise RuntimeError("retries exhausted")
