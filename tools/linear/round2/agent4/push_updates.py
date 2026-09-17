"""Push rewritten descriptions for the 37 issues (idempotent, batches of 5)."""
import sys, os, re, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import r4, rw_tables_a, rw_tables_b, rw_biz_a, rw_biz_b, rw_growth_a, rw_growth_b
DRY = "--dry" in sys.argv
ch = r4.load_changes()
DOCS = {d["project"]: d["url"] for d in ch.get("documents", [])}
PKEY_BY_NAME = {v: k for k, v in r4.PNAME.items()}
ALL = {}
for m in (rw_tables_a, rw_tables_b, rw_biz_a, rw_biz_b, rw_growth_a, rw_growth_b): ALL.update(m.SPECS)
assert len(ALL) == 37, len(ALL)

def finalize(key, sections):
    text = r4.render(sections)
    pkey = PKEY_BY_NAME[r4.BY_ID[key]["projectName"]]
    unresolved = set(re.findall(r"\{\{([^}]+)\}\}", text))
    text = r4.resolve(text, ch)
    if unresolved:
        # references to issues that could not be created: point at the project document holding the specs
        projs = sorted({u.split("/")[1] if u.startswith("gap/") else u.split("/")[0] for u in unresolved})
        links = ", ".join(f"[{p}]({DOCS[p]})" if p in DOCS else p for p in projs)
        text += ("\n**Pending issues**\n\nBracketed references above are fully specified work packages that Linear refused to create on 2026-09-17 "
                 "(`USAGE_LIMIT_EXCEEDED`, free-plan issue cap). Their specs live in the project document(s) " + links +
                 " and they are created as issues by `round2/agent4/create_issues.py` once the workspace plan is upgraded.\n")
    return text

todo = []
for k, s in ALL.items():
    if r4.BY_ID[k]["id"] in ch["updated"]: continue
    t = finalize(k, s)
    w = r4.words(t)
    if not (380 <= w <= 760): print("WORDCOUNT", k, w)
    todo.append((k, t))
print("to update:", len(todo))
if DRY:
    for k, t in todo: print(" ", k, r4.words(t))
    open(os.path.join(r4.HERE, "_preview.md"), "w").write("\n\n----\n\n".join(f"# {k}\n\n{t}" for k, t in todo))
    sys.exit(0)

for i in range(0, len(todo), 5):
    batch = todo[i:i+5]
    q = "mutation(" + ",".join(f"$i{j}:String!,$d{j}:String!" for j in range(len(batch))) + "){ " + \
        " ".join(f"u{j}: issueUpdate(id:$i{j}, input:{{description:$d{j}}}){{ success issue{{ identifier }} }}" for j in range(len(batch))) + " }"
    v = {}
    for j, (k, t) in enumerate(batch): v[f"i{j}"] = r4.BY_ID[k]["id"]; v[f"d{j}"] = t
    d = r4.gql(q, v)
    for j, (k, t) in enumerate(batch):
        r = d[f"u{j}"]
        if r["success"]: ch["updated"].append(r4.BY_ID[k]["id"]); print("updated", k)
        else: print("FAILED", k, r)
    r4.save_changes(ch)
print("updated total:", len(ch["updated"]))
