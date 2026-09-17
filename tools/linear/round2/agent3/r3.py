"""Round-2 helper for agent 3 (collab, realtime, input)."""
import json, os, time, urllib.request, urllib.error, sys, re

URL = "https://api.linear.app/graphql"
KEY = os.environ.get("LINEAR_API_KEY") or "placeholder"
BASE = os.environ.get("PAPEROS_PLAN_DIR", ".") + ""
R2 = os.path.join(BASE, "round2")
A3 = os.path.join(R2, "agent3")
CHANGES = os.path.join(R2, "changes-3.json")
SNAP = json.load(open(os.path.join(R2, "linear-snapshot.json")))
BY_ID = {i["identifier"]: i for i in SNAP["issues"]}
TEAM = SNAP["team"]["id"]
STATES = {s["name"]: s["id"] for s in SNAP["states"]}
LABELS = {}
for l in SNAP["labels"]:
    if l["teamId"]:
        LABELS[(l["group"] + "/" + l["name"]) if l["group"] else l["name"]] = l["id"]
PROJECTS = {
    "collab": "0a92662d-a088-42ef-b847-bf22b63582fc",
    "realtime": "fa82de86-f88a-41d0-953f-a6253c2460fd",
    "input": "bcfb9178-60fb-48f1-9c91-3c2d2d4aa080",
}
PNAME = {"collab": "In-App Collaboration & Knowledge", "realtime": "Multiplayer & Realtime", "input": "Multi-Input Control & Accessibility"}
MILESTONES = {}
for p in SNAP["projects"]:
    for m in p["milestones"]:
        MILESTONES[(p["id"], m["name"])] = m["id"]
SURFACES = {"Customer", "Staff", "Developer", "Agent"}

_last = [0.0]
def gql(query, variables=None, retries=8):
    body = json.dumps({"query": query, "variables": variables or {}}).encode()
    for attempt in range(retries):
        wait = 0.35 - (time.time() - _last[0])
        if wait > 0: time.sleep(wait)
        req = urllib.request.Request(URL, data=body, headers={"Authorization": KEY, "Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=180) as r:
                data = json.loads(r.read().decode())
            _last[0] = time.time()
        except urllib.error.HTTPError as e:
            _last[0] = time.time()
            raw = e.read().decode()
            if e.code == 429 or "RATELIMITED" in raw:
                print("rate limited; sleeping 60s", file=sys.stderr); time.sleep(60); continue
            try: data = json.loads(raw)
            except Exception: data = {"errors": [{"message": "HTTP %s %s" % (e.code, raw[:500])}]}
        except Exception as e:
            print("net error", e, file=sys.stderr); time.sleep(5); continue
        errs = data.get("errors")
        if errs:
            codes = [(x.get("extensions") or {}).get("code") for x in errs]
            if "RATELIMITED" in codes:
                print("RATELIMITED; sleeping 60s", file=sys.stderr); time.sleep(60); continue
            raise RuntimeError(json.dumps(errs)[:1500])
        return data["data"]
    raise RuntimeError("retries exhausted")

def load_changes():
    if os.path.exists(CHANGES):
        return json.load(open(CHANGES))
    return {"updated": [], "created": [], "relations": [], "projectsUpdated": [], "milestoneChanges": [], "notes": []}

def save_changes(c):
    tmp = CHANGES + ".tmp"
    json.dump(c, open(tmp, "w"), indent=1)
    os.replace(tmp, CHANGES)

def words(s): return len(re.findall(r"\S+", s))

def find_created(ch, key):
    for c in ch["created"]:
        if c["key"] == key: return c
    return None

def label_ids(names):
    return [LABELS[n] for n in names]

SECTION_ORDER = ["Goal", "Scope", "Spec", "Interface contract", "Definition of done", "Test plan", "Demo", "Edge cases", "Dependencies", "Agent", "Size"]
def render(sections):
    parts = []
    for k in SECTION_ORDER:
        v = sections.get(k)
        if not v: raise ValueError("missing section " + k)
        parts.append("**%s**\n\n%s" % (k, v.strip()))
    return "\n\n".join(parts) + "\n"

def check(sections, lo=400, hi=720):
    txt = render(sections)
    n = words(txt)
    return n, (lo <= n <= hi)
