"""Round-2 helper for agent 1 (identity, design-system, quality)."""
import json, os, time, urllib.request, urllib.error, sys, re

URL = "https://api.linear.app/graphql"
KEY = os.environ.get("LINEAR_API_KEY") or "placeholder"
BASE = os.environ.get("PAPEROS_PLAN_DIR", ".") + ""
R2 = os.path.join(BASE, "round2")
CHANGES = os.path.join(R2, "changes-1.json")
SNAP = json.load(open(os.path.join(R2, "linear-snapshot.json")))
BY_ID = {i["identifier"]: i for i in SNAP["issues"]}
TEAM = "0ee78894-89f8-4376-a829-f8685dbc1868"
STATES = {s["name"]: s["id"] for s in SNAP["states"]}
LABELS = {}
for l in SNAP["labels"]:
    LABELS[(l["group"] + "/" + l["name"]) if l["group"] else l["name"]] = l["id"]
PROJECTS = {
    "identity": "b590e463-5980-47f8-9d74-889addb9434c",
    "design-system": "0e067722-38f0-4e4c-88a5-54158acc56fd",
    "quality": "32967d75-af65-43a0-8dc9-b906f28ed2b4",
}
MILESTONES = {}
for p in SNAP["projects"]:
    for m in p["milestones"]:
        MILESTONES[(p["id"], m["name"])] = m["id"]

_last = 0.0
def gql(query, variables=None, retries=8):
    global _last
    body = json.dumps({"query": query, "variables": variables or {}}).encode()
    for attempt in range(retries):
        wait = 0.3 - (time.time() - _last)
        if wait > 0: time.sleep(wait)
        req = urllib.request.Request(URL, data=body, headers={"Authorization": KEY, "Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=180) as r:
                data = json.loads(r.read().decode())
            _last = time.time()
        except urllib.error.HTTPError as e:
            _last = time.time()
            raw = e.read().decode()
            if e.code == 429:
                print("429, sleeping 60", file=sys.stderr); time.sleep(60); continue
            try: data = json.loads(raw)
            except Exception: data = {"errors": [{"message": "HTTP %s %s" % (e.code, raw[:500])}]}
        except Exception as e:
            print("net error", e, file=sys.stderr); time.sleep(5); continue
        errs = data.get("errors")
        if errs:
            codes = [(x.get("extensions") or {}).get("code") for x in errs]
            if "RATELIMITED" in codes:
                print("RATELIMITED, sleeping 60", file=sys.stderr); time.sleep(60); continue
            raise RuntimeError(json.dumps(errs)[:1500])
        return data["data"]
    raise RuntimeError("retries exhausted")

def load_changes():
    if os.path.exists(CHANGES):
        return json.load(open(CHANGES))
    return {"updated": [], "created": [], "relations": [], "projectsUpdated": [], "labelChanges": [], "notes": []}

def save_changes(c):
    tmp = CHANGES + ".tmp"
    json.dump(c, open(tmp, "w"), indent=1)
    os.replace(tmp, CHANGES)

def words(s):
    return len(re.findall(r"\S+", s))

def find_created(ch, key):
    for c in ch["created"]:
        if c["key"] == key: return c
    return None

def label_ids(names):
    out = []
    for n in names:
        if n not in LABELS: raise KeyError(n)
        out.append(LABELS[n])
    return out
