"""Round-2 helper for agent 4 (tables, business-core, growth)."""
import json, os, time, urllib.request, urllib.error, sys, re

URL = "https://api.linear.app/graphql"
KEY = os.environ.get("LINEAR_API_KEY") or "placeholder"
BASE = os.environ.get("PAPEROS_PLAN_DIR", ".") + ""
R2 = os.path.join(BASE, "round2")
HERE = os.path.join(R2, "agent4")
CHANGES = os.path.join(R2, "changes-4.json")
SNAP = json.load(open(os.path.join(R2, "linear-snapshot.json")))
BY_ID = {i["identifier"]: i for i in SNAP["issues"]}
TEAM = "0ee78894-89f8-4376-a829-f8685dbc1868"
STATES = {s["name"]: s["id"] for s in SNAP["states"]}
LABELS = {}
for l in SNAP["labels"]:
    if l["isGroup"]: continue
    LABELS[(l["group"] + "/" + l["name"]) if l["group"] else l["name"]] = l["id"]
SURFACES = {"Customer", "Staff", "Developer", "Agent"}
PROJECTS = {
    "tables": "cb945472-3eb1-4669-9883-0e49008a2b68",
    "business-core": "789f25c0-d006-4f6c-bd12-7f21866d8bc0",
    "growth": "9eba0335-55a2-42e4-af3f-21d61516b790",
}
PNAME = {
    "tables": "Table & Views Engine",
    "business-core": "Business Core: Payments, Finance & Payroll",
    "growth": "Growth: Marketing, Outreach & CRM",
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
    return {"updated": [], "created": [], "relations": [], "relationPairs": [], "projectsUpdated": [],
            "stateChanges": [], "documents": [], "pendingRelations": [], "notes": []}

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

SECTION_ORDER = ["Goal", "Scope", "Spec", "Interface contract", "Definition of done", "Test plan", "Demo",
                 "Edge cases", "Dependencies", "Agent", "Size"]

SHORT = {"Contract": "Interface contract", "DoD": "Definition of done", "Test": "Test plan", "Edge": "Edge cases", "Deps": "Dependencies"}
def norm(sections):
    return {SHORT.get(k, k): v for k, v in sections.items()}

def render(sections):
    sections = norm(sections)
    parts = []
    for k in SECTION_ORDER:
        v = sections.get(k)
        if not v: raise ValueError("missing section " + k)
        parts.append("**%s**\n\n%s" % (k, v.strip()))
    return "\n\n".join(parts) + "\n"

def resolve(text, ch):
    """Replace {{key}} references with created identifiers, else a bracketed key."""
    created = {c["key"]: c["identifier"] for c in ch["created"]}
    return re.sub(r"\{\{([^}]+)\}\}", lambda m: created.get(m.group(1), "[%s]" % m.group(1)), text)

def label_ids(names):
    out = []
    for n in names:
        if n in LABELS: out.append(LABELS[n])
        elif ("Phase/" + n) in LABELS: out.append(LABELS["Phase/" + n])
        elif ("Type/" + n) in LABELS: out.append(LABELS["Type/" + n])
        else: raise KeyError(n)
    return out
