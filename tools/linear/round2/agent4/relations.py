"""Add missing `blocks` relations for tables, business-core, growth; cycle- and phase-checked; idempotent."""
import sys, os, json, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import r4
DRY = "--dry" in sys.argv
ch = r4.load_changes(); ch.setdefault("relationPairs", []); ch.setdefault("relations", [])

# blocker -> blocked (spec-stated hard dependencies not encoded in Linear)
NEW = [
    ("PAP-59", "PAP-163"), ("PAP-279", "PAP-163"), ("PAP-279", "PAP-166"),
    ("PAP-71", "PAP-164"), ("PAP-67", "PAP-164"), ("PAP-233", "PAP-164"),
    ("PAP-151", "PAP-165"), ("PAP-162", "PAP-171"), ("PAP-172", "PAP-173"), ("PAP-38", "PAP-174"),
    ("PAP-179", "PAP-181"), ("PAP-175", "PAP-181"), ("PAP-180", "PAP-182"), ("PAP-180", "PAP-183"),
    ("PAP-175", "PAP-184"), ("PAP-175", "PAP-185"), ("PAP-37", "PAP-180"), ("PAP-235", "PAP-180"),
    ("PAP-165", "PAP-189"), ("PAP-37", "PAP-190"), ("PAP-35", "PAP-193"), ("PAP-163", "PAP-194"),
    ("PAP-163", "PAP-195"), ("PAP-177", "PAP-196"), ("PAP-179", "PAP-196"), ("PAP-37", "PAP-197"),
]

# existing graph: snapshot + edges other agents added
edges = set()
for i in r4.SNAP["issues"]:
    for r in i["relations"]:
        if r["type"] == "blocks": edges.add((i["identifier"], r["related"]))
for f in ["changes-0.json", "changes-1.json", "changes-2.json", "changes-3.json"]:
    try:
        c = json.load(open(os.path.join(r4.R2, f)))
        for key in ("relationPairs", "relations"):
            for x in c.get(key, []):
                s = x if isinstance(x, str) else json.dumps(x)
                m = re.findall(r"(PAP-\d+)\D+(PAP-\d+)", s)
                if m and isinstance(x, (str, dict)):
                    a, b = m[0]
                    if isinstance(x, dict) and x.get("blocked") and x.get("blocker"): a, b = x["blocker"], x["blocked"]
                    edges.add((a, b))
    except Exception as e: print("warn", f, e)

# ids for issues not in the snapshot (created by other agents this round)
EXTRA = {}
for f in ["changes-0.json", "changes-1.json"]:
    for c in json.load(open(os.path.join(r4.R2, f))).get("created", []):
        EXTRA[c["identifier"]] = c
def iid(k):
    if k in r4.BY_ID: return r4.BY_ID[k]["id"]
    return EXTRA[k]["id"]

# phase lookup (fetch for issues outside the snapshot)
phase = {i["identifier"]: [l for l in i["labels"] if l.startswith("Phase/")] for i in r4.SNAP["issues"]}
need = [k for pair in NEW for k in pair if k not in phase]
if need:
    q = "query(" + ",".join(f"$a{n}: String!" for n in range(len(need))) + "){ " + " ".join(f"i{n}: issue(id:$a{n}){{ identifier labels{{nodes{{name}}}} projectMilestone{{name targetDate}} }}" for n in range(len(need))) + " }"
    d = r4.gql(q, {f"a{n}": iid(k) for n, k in enumerate(need)})
    for n, k in enumerate(need):
        node = d[f"i{n}"]
        phase[k] = ["Phase/" + l["name"] for l in node["labels"]["nodes"] if l["name"] in ("P0", "P1", "P2")]
        print("fetched", k, phase[k], node["projectMilestone"])
PH = lambda k: (phase.get(k) or ["Phase/P?"])[0]

def has_path(src, dst, g):
    seen = set(); stack = [src]
    while stack:
        n = stack.pop()
        if n == dst: return True
        if n in seen: continue
        seen.add(n)
        stack += [b for (a, b) in g if a == n]
    return False

todo = []
for a, b in NEW:
    if (a, b) in edges or f"{a} -> {b}" in ch["relationPairs"]:
        print("exists", a, "->", b); continue
    if has_path(b, a, edges):
        print("CYCLE, skip", a, "->", b); continue
    if PH(a) > PH(b):
        print("PHASE INVERSION, skip", a, PH(a), "->", b, PH(b)); continue
    todo.append((a, b)); edges.add((a, b))
print("to add:", len(todo))
if DRY:
    for a, b in todo: print(" ", a, PH(a), "blocks", b, PH(b))
    sys.exit(0)

for i in range(0, len(todo), 8):
    batch = todo[i:i+8]
    q = "mutation(" + ",".join(f"$r{j}: IssueRelationCreateInput!" for j in range(len(batch))) + "){ " + \
        " ".join(f"r{j}: issueRelationCreate(input:$r{j}){{ success issueRelation{{ id }} }}" for j in range(len(batch))) + " }"
    vars_ = {f"r{j}": {"issueId": iid(a), "relatedIssueId": iid(b), "type": "blocks"} for j, (a, b) in enumerate(batch)}
    try:
        d = r4.gql(q, vars_)
    except RuntimeError as e:
        print("batch failed, singly:", str(e)[:200]); d = {}
        for j, (a, b) in enumerate(batch):
            try: d[f"r{j}"] = r4.gql("mutation($r: IssueRelationCreateInput!){ r: issueRelationCreate(input:$r){ success issueRelation{ id } } }", {"r": vars_[f"r{j}"]})["r"]
            except RuntimeError as e2: print("FAILED", a, b, str(e2)[:200])
    for j, (a, b) in enumerate(batch):
        r = d.get(f"r{j}")
        if r and r.get("success"):
            ch["relations"].append(r["issueRelation"]["id"]); ch["relationPairs"].append(f"{a} -> {b}"); print("added", a, "->", b)
    r4.save_changes(ch)

# pending relations for issues that could not be created
pend = json.load(open(os.path.join(r4.HERE, "pending-issues.json")))["issues"]
pr = set(ch.get("pendingRelations", []))
for it in pend:
    for b in it.get("blockedBy", []): pr.add(f"{b} -> {it['key']}")
    for b in it.get("blocks", []): pr.add(f"{it['key']} -> {b}")
    if it["parent"]:
        pr.add(f"{it['parent']} parent-of {it['key']}")
ch["pendingRelations"] = sorted(pr); r4.save_changes(ch)
print("relations total:", len(ch["relations"]), "pending:", len(ch["pendingRelations"]))
