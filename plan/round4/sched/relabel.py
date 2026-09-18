#!/usr/bin/env python3
"""Round 4 step 4: make every leaf issue carry exactly one Chunk label matching plan/round4/chunks-v2.json (mix B);
umbrellas carry none; deferred leaves get `Chunk: v0.2`. Creates missing `Chunk n` / `Chunk: v0.2` labels in the
Chunk group. Only mutations: issueLabelCreate (Chunk group) and issueUpdate {addedLabelIds, removedLabelIds}.
Batches of 10 issueUpdate aliases per request, 300 ms apart. Log: plan/round4/changes/chunks-relabel.json.
Run with VERIFY_ONLY=1 to only re-count labels."""
import json, os, sys, time, datetime
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from pull_graph import gql, TEAM
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
LOG = os.path.join(ROOT, "plan", "round4", "changes", "chunks-relabel.json")
G = json.load(open(os.path.join(HERE, "graph.json")))
I = G["issues"]
V2 = json.load(open(os.path.join(HERE, "..", "chunks-v2.json")))
B = V2["mixes"]["B"]
GROUP_ID = next(l["id"] for l in G["chunkLabels"] if l["name"] == "Chunk")
FAMILY = ["#BAE6FD", "#7DD3FC", "#38BDF8", "#0284C7", "#075985", "#0369A1", "#0C4A6E", "#E0F2FE", "#082F49", "#0EA5E9"]
V02_COLOR = "#082F49"

want = {}
for c in B["chunks"]:
    for k in c["issues"]:
        want[k] = "Chunk %d" % c["chunk"]
for k in B["deferredChunk"]["issues"]:
    want[k] = "Chunk: v0.2"
umbrellas = {k for k, i in I.items() if i["children"]}
assert not (set(want) & umbrellas)

log = {"startedAt": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "labelCreates": [], "issueUpdates": [], "failures": [], "verify": None}


def save():
    json.dump(log, open(LOG, "w"), indent=1)


def label_map():
    d = gql("query($t: String!) { team(id: $t) { labels(first: 250) { nodes { id name color parent { id } } } } }", {"t": TEAM})
    return {l["name"]: l for l in d["team"]["labels"]["nodes"] if (l["parent"] or {}).get("id") == GROUP_ID}


labels = label_map()
if not os.environ.get("VERIFY_ONLY"):
    needed = sorted(set(want.values()), key=lambda x: (x.startswith("Chunk:"), x))
    for name in needed:
        if name in labels:
            continue
        n = int(name.split()[1]) if name.startswith("Chunk ") else None
        color = V02_COLOR if n is None else FAMILY[(n - 1) % len(FAMILY)]
        r = gql("mutation($input: IssueLabelCreateInput!) { issueLabelCreate(input: $input) { success issueLabel { id name color } } }",
                {"input": {"teamId": TEAM, "parentId": GROUP_ID, "name": name, "color": color}})["issueLabelCreate"]
        log["labelCreates"].append({"name": name, "color": color, "result": r}); save()
        print("created label", r, file=sys.stderr)
        time.sleep(0.3)
    labels = label_map()
    chunk_label_ids = {l["id"]: name for name, l in labels.items()}

    # plan the per-issue changes
    ops = []
    for k, i in I.items():
        have = [lab for lab in i["labels"] if lab in labels]
        target = want.get(k)
        if k in umbrellas or target is None:
            if have:
                ops.append((k, [], [labels[h]["id"] for h in have], have, None))
            continue
        if have == [target]:
            continue
        add = [labels[target]["id"]] if target not in have else []
        rem = [labels[h]["id"] for h in have if h != target]
        ops.append((k, add, rem, have, target))
    print("planned updates", len(ops), file=sys.stderr)
    for b in range(0, len(ops), 10):
        batch = ops[b:b + 10]
        parts, vars_, defs = [], {}, []
        for j, (k, add, rem, have, target) in enumerate(batch):
            inp = {}
            if add: inp["addedLabelIds"] = add
            if rem: inp["removedLabelIds"] = rem
            vars_["i%d" % j] = I[k]["id"]; vars_["u%d" % j] = inp
            defs.append("$i%d: String!, $u%d: IssueUpdateInput!" % (j, j))
            parts.append("u%d: issueUpdate(id: $i%d, input: $u%d) { success issue { identifier labels { nodes { name } } } }" % (j, j, j))
        q = "mutation(%s) { %s }" % (", ".join(defs), " ".join(parts))
        try:
            r = gql(q, vars_)
        except Exception as e:
            log["failures"].append({"batch": b // 10, "issues": [x[0] for x in batch], "error": str(e)[:500]}); save()
            print("batch failed", b // 10, str(e)[:200], file=sys.stderr); time.sleep(1); continue
        for j, (k, add, rem, have, target) in enumerate(batch):
            res = r["u%d" % j]
            after = [l["name"] for l in res["issue"]["labels"]["nodes"] if l["name"] in labels]
            entry = {"identifier": k, "before": have, "after": after, "target": target, "addedLabelIds": add, "removedLabelIds": rem, "success": res["success"]}
            log["issueUpdates"].append(entry)
            if not res["success"] or (target and after != [target]) or (not target and after):
                log["failures"].append(entry)
        if (b // 10) % 10 == 0:
            save(); print("batch", b // 10, "of", (len(ops) + 9) // 10, file=sys.stderr)
        time.sleep(0.3)
    save()

# verify: re-query identifier + labels for the whole team
counts, mismatches, cursor = {}, [], None
for page in range(100):
    d = gql("query($t: String!, $c: String) { team(id: $t) { issues(first: 100, after: $c) { pageInfo { hasNextPage endCursor } nodes { identifier labels { nodes { name } } } } } }",
            {"t": TEAM, "c": cursor})["team"]["issues"]
    for n in d["nodes"]:
        have = [l["name"] for l in n["labels"]["nodes"] if l["name"] in labels]
        for h in have: counts[h] = counts.get(h, 0) + 1
        k = n["identifier"]
        exp = [want[k]] if k in want else []
        if k in I and have != exp:
            mismatches.append({"identifier": k, "have": have, "expected": exp})
    if not d["pageInfo"]["hasNextPage"]: break
    cursor = d["pageInfo"]["endCursor"]; time.sleep(0.25)
expected = {}
for v in want.values(): expected[v] = expected.get(v, 0) + 1
log["verify"] = {"at": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "countsInLinear": dict(sorted(counts.items())),
                 "expectedFromChunksV2": dict(sorted(expected.items())), "mismatches": mismatches}
save()
print(json.dumps(log["verify"], indent=1)[:3000])
print("updates", len(log["issueUpdates"]), "failures", len(log["failures"]), "labelCreates", len(log["labelCreates"]))
