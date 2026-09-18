#!/usr/bin/env python3
"""Round 4 schedule model and $2,500 chunk planner over the live PAP graph (plan/round4/sched/graph.json).

Reuses the round-3 token model, prices and list scheduler (docs/cost-and-duration-estimate.md, docs/build-chunks.md):
  sizes from the Fibonacci estimate (2 = S half a session-day, 3 = M one, 5 = L two); build minutes S 30 / M 75 / L 180,
  review 20 min, QA gate 15 min on code issues; branch-start rule (a dependent starts once every blocker's PR is open,
  i.e. when the blocker's build minutes end); 16 builders 24/7, reviewer and QA sessions on top of the cap;
  ready-first by longest remaining build tail, then phase, priority, size.
Mixes: A = all Fable 5.1; B (canonical, round 4) = builder model from the issue's `Model` label (Opus 5 when the label
  is missing; Spec and Research issues on Fable 5.1), reviewer Fable 5.1 / high, QA gate Opus 5 / low, 4 RC reviews
  on Fable 5.1; B3 = the round-3 definition of mix B (Opus 5 on every Build/Infra/Docs/Review issue) as a reference.
Writes sched-<mix>.json, summary.json, days.json, burn.json and ../chunks-v2.json. Read-only against Linear.
"""
import json, os, sys, collections, datetime, math

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
G = json.load(open(os.path.join(HERE, "graph.json")))
I = G["issues"]
OLD = json.load(open(os.path.join(ROOT, "plan", "chunks.json")))

PKEY = {"Universal App Shell & Repo Template": "app-shell", "Data Layer & Database": "data-layer",
        "Version Control & Forge Independence": "forge", "Identity, Roles & Audiences": "identity",
        "Design System": "design-system", "Quality Pipeline": "quality",
        "Project Management & Claude Pipeline": "pm-linear", "Agent Characters & Orgs": "agents",
        "Spec Builder": "spec-builder", "In-App Collaboration & Knowledge": "collab",
        "Multiplayer & Realtime": "realtime", "Multi-Input Control & Accessibility": "input",
        "Table & Views Engine": "tables", "Business Core: Payments, Finance & Payroll": "business-core",
        "Growth: Marketing, Outreach & CRM": "growth", "Migration & Import Tools": "migration",
        "Library Discovery & Integration": "libraries", "Module System & Swap Tooling": "module-system",
        "Commerce, Operations & Vertical Packs": "commerce", "Platform Operations, Analytics & Compliance": "platform-ops",
        "Scheduling, Messaging & Customer Engagement": "engagement",
        "Workflows, Approvals, Forms, Documents & E-Signature": "workflows",
        "Tenant AI Assistant & Business Agents": "assistant"}
NEW_PROJECTS = ["assistant", "workflows", "engagement", "commerce", "platform-ops"]
SIZE = {2: "S", 3: "M", 5: "L"}
BUILD_MIN = {"S": 30, "M": 75, "L": 180}
REVIEW_MIN, QA_MIN = 20, 15
CODE = {"Build", "Infra"}
TOK = {"S": (1.5e6, 60e3), "M": (4.0e6, 150e3), "L": (10.0e6, 400e3)}
EFFORT = {"low": 0.6, "medium": 1.0, "high": 1.4, "max": 2.0}
KTYPE = {"Build": 1.0, "Infra": 1.0, "Spec": 0.6, "Research": 0.6, "Docs": 0.6, "Review": 0.6}
PRICES = {"claude-fable-5-1": {"inp": 10, "out": 50, "cw": 12.5, "cr": 0.25},
          "claude-opus-5": {"inp": 5, "out": 25, "cw": 6.25, "cr": 0.5},
          "claude-sonnet-5": {"inp": 2, "out": 10, "cw": 2.5, "cr": 0.2},
          "claude-haiku-4-5": {"inp": 1, "out": 5, "cw": 1.25, "cr": 0.1}}
LABEL_MODEL = {"Model: Fable 5.1": "claude-fable-5-1", "Model: Opus 5": "claude-opus-5",
               "Model: Sonnet 5": "claude-sonnet-5", "Model: Haiku 4.5": "claude-haiku-4-5"}
CONTINGENCY = 1.25
CHUNK_USD, DISCOUNT = 2500.0, 0.02
BUILDERS = 16
STEP = 5
RC_LIST_COST = 68.75  # one L-size Fable 5.1 / high session, contingency included
RCS = [("RC0", "RC0 staging + sign-in + orchestrator claiming",
        ["PAP-25", "PAP-30", "PAP-269", "PAP-223", "PAP-224", "PAP-281", "PAP-282", "PAP-283"]),
       ("RC1", "RC1 v0.1.0-rc.1: RLS permissions, installers, Yjs server, codegen, Stripe test mode, story baselines",
        ["PAP-227", "PAP-228", "PAP-229", "PAP-256", "PAP-257", "PAP-140", "PAP-314", "PAP-315", "PAP-316", "PAP-177", "PAP-246", "PAP-52"]),
       ("RC2", "RC2 v0.1.0-rc.2, first real cut: gates 1-4, grid + compiler, comments, record sync, ledger + invoices, imports, drill",
        ["PAP-335", "PAP-336", "PAP-337", "PAP-341", "PAP-342", "PAP-343", "PAP-317", "PAP-318", "PAP-319", "PAP-326", "PAP-327",
         "PAP-328", "PAP-392", "PAP-393", "PAP-394", "PAP-395", "PAP-396", "PAP-397", "PAP-347", "PAP-348", "PAP-349", "PAP-29", "PAP-254"]),
       ("RC3", "RC3 = v0.1.0: every non-deferred issue Done", [])]

# Needs Justin items (execution schedule section 2) and the issues they gate; reused from round 3.
NJ = {}
for mix in ("A", "B"):
    for c in OLD["mixes"][mix]["chunks"] + [OLD["mixes"][mix]["deferredChunk"]]:
        for nj in c.get("needsJustinBeforeStart", []):
            NJ[nj["id"]] = nj

# ---------------------------------------------------------------- graph
for k, i in I.items():
    i["pkey"] = PKEY.get(i["project"], i["project"])
    i["size"] = SIZE.get(i["estimate"], "M")
umbrellas = {k for k, i in I.items() if i["children"]}
leaves = [k for k in I if k not in umbrellas]


def is_deferred(k):
    while k:
        if I[k]["deferred"]:
            return True
        k = I[k]["parent"]
    return False


deferred = {k for k in leaves if is_deferred(k)}
active = [k for k in leaves if k not in deferred]
umb_deferred = {k for k in umbrellas if is_deferred(k)}


def eff_blockers(k):
    i = I[k]
    src = set(i["blockedBy"])
    if i["parent"]:
        src |= set(I[i["parent"]]["blockedBy"])
    out = set()
    for b in src:
        if b == k or b == i["parent"]:
            continue
        if b in umbrellas:
            out |= {c for c in I[b]["children"] if c not in umbrellas}
        else:
            out.add(b)
    return sorted(out - {k})


EFF = {k: eff_blockers(k) for k in leaves}
DEPS = collections.defaultdict(list)
for k, bs in EFF.items():
    for b in bs:
        DEPS[b].append(k)

# cycle check
sys.setrecursionlimit(20000)
_state = {}


def _dfs(k, stack):
    if _state.get(k) == 1:
        raise RuntimeError("cycle: %s" % (stack[stack.index(k):] + [k]))
    if _state.get(k) == 2:
        return
    _state[k] = 1; stack.append(k)
    for b in EFF[k]:
        _dfs(b, stack)
    stack.pop(); _state[k] = 2


for k in leaves:
    _dfs(k, [])


def build_min(k): return BUILD_MIN[I[k]["size"]]
def post_min(k): return REVIEW_MIN + (QA_MIN if I[k]["type"] in CODE else 0)
def full_min(k): return build_min(k) + post_min(k)


def tails(units, soft):
    """Longest remaining tail in minutes, branch-start (build minutes only, post minutes on the last issue)
    and full (round-3 style: every issue's build + review + QA)."""
    U = set(units); memo_b, memo_f = {}, {}

    def tb(k):
        if k in memo_b: return memo_b[k]
        downs = [d for d in DEPS[k] if d in U]
        memo_b[k] = build_min(k) + (max(tb(d) for d in downs) if downs else post_min(k))
        return memo_b[k]

    def tf(k):
        if k in memo_f: return memo_f[k]
        downs = [d for d in DEPS[k] if d in U]
        memo_f[k] = full_min(k) + (max(tf(d) for d in downs) if downs else 0)
        return memo_f[k]

    for k in units:
        tb(k); tf(k)
    return memo_b, memo_f


def chain(units, memo):
    """Reconstruct the longest chain for reporting."""
    U = set(units)
    k = max(units, key=lambda x: memo[x]); out = [k]
    while True:
        downs = [d for d in DEPS[k] if d in U]
        if not downs: break
        k = max(downs, key=lambda x: memo[x]); out.append(k)
    return out


def schedule(units, t0_min, done_before=None):
    """List scheduling at BUILDERS concurrent builders, branch-start rule. Returns start/build_end/land per issue."""
    done_before = done_before or {}
    tail_b, _ = tails(units, True)
    U = set(units)
    start, bend, land = {}, {}, {}
    pending = set(units)
    running = []  # build_end times
    t = t0_min
    PRIO = {"P0": 0, "P1": 1, "P2": 2, None: 3}
    while pending or running:
        running = [e for e in running if e > t]
        def ready(k):
            for b in EFF[k]:
                if b in deferred and k not in deferred:
                    continue  # soft: deferred blockers never hold scheduled work
                if b in bend:
                    if bend[b] > t: return False
                elif b in done_before:
                    continue
                elif b in U:
                    return False
                # blocker outside this unit set and not done: treated as soft
            return True
        if len(running) < BUILDERS:
            cands = [k for k in pending if ready(k)]
            cands.sort(key=lambda k: (-tail_b[k], PRIO[I[k]["phase"]], I[k]["priority"] or 3, -build_min(k), I[k]["number"]))
            for k in cands:
                if len(running) >= BUILDERS: break
                start[k] = t; bend[k] = t + build_min(k); land[k] = bend[k] + post_min(k)
                running.append(bend[k]); pending.discard(k)
        if not pending and not running: break
        t += STEP
        if t > t0_min + 60 * 24 * 60:
            raise RuntimeError("scheduler did not converge; pending %s" % sorted(pending)[:10])
    return start, bend, land


# ---------------------------------------------------------------- cost
def builder_model(k, mix):
    t = I[k]["type"]
    if mix == "A":
        return "claude-fable-5-1"
    if t in ("Spec", "Research"):
        return "claude-fable-5-1"
    if mix == "B3":
        return "claude-opus-5"
    return LABEL_MODEL.get(I[k]["model"], "claude-opus-5")


MIX = {
    "A": {"description": "all Fable 5.1 (builders, reviewers, QA, RC reviews)", "reviewer": "claude-fable-5-1",
          "qa": "claude-fable-5-1", "rc": "claude-fable-5-1",
          "builderModels": {t: "claude-fable-5-1" for t in KTYPE}},
    "B": {"description": "canonical, round 4: builder model from the issue's Model label (Opus 5 if missing; Sonnet 5 and Haiku 4.5 labels kept), "
                         "Fable 5.1 on Spec/Research issues, every reviewer session (high) and the 4 RC reviews; QA gate Opus 5 / low",
          "reviewer": "claude-fable-5-1", "qa": "claude-opus-5", "rc": "claude-fable-5-1",
          "builderModels": {"Build": "label (Opus 5 default)", "Infra": "label (Opus 5 default)", "Docs": "label (Opus 5 default)",
                            "Review": "label (Opus 5 default)", "Spec": "claude-fable-5-1", "Research": "claude-fable-5-1"}},
    "B3": {"description": "reference only: the round-3 definition of mix B (Opus 5 on every Build/Infra/Docs/Review issue, Fable 5.1 on Spec/Research, "
                          "Fable reviewers, Opus QA)", "reviewer": "claude-fable-5-1", "qa": "claude-opus-5", "rc": "claude-fable-5-1",
           "builderModels": {"Build": "claude-opus-5", "Infra": "claude-opus-5", "Docs": "claude-opus-5", "Review": "claude-opus-5",
                             "Spec": "claude-fable-5-1", "Research": "claude-fable-5-1"}},
}


def session_cost(inp, out, model):
    p = PRICES[model]
    return (0.8 * inp * p["cr"] + 0.2 * inp * p["cw"] + out * p["out"]) / 1e6


def issue_cost(k, mix, effort_override=None):
    i = I[k]
    inp, out = TOK[i["size"]]
    eff = (effort_override or (i["effort"] or "Effort: medium").replace("Effort: ", ""))
    out = out * EFFORT.get(eff, 1.0)
    kt = KTYPE.get(i["type"], 1.0)
    inp, out = inp * kt, out * kt
    bm = builder_model(k, mix)
    b = session_cost(inp, out, bm)
    r = session_cost(0.4 * inp, 0.4 * out, MIX[mix]["reviewer"])
    q = session_cost(0.25 * inp, 0.25 * out, MIX[mix]["qa"]) if i["type"] in CODE else 0.0
    return {"builder": b * CONTINGENCY, "reviewer": r * CONTINGENCY, "qa": q * CONTINGENCY,
            "total": (b + r + q) * CONTINGENCY, "builderModel": bm, "effort": eff}


# ---------------------------------------------------------------- run
def tstr(m):
    return (T0 + datetime.timedelta(minutes=m)).strftime("%Y-%m-%dT%H:%MZ")


taken = datetime.datetime.strptime(G["takenAt"], "%Y-%m-%dT%H:%M:%SZ")
T0 = (taken + datetime.timedelta(minutes=15)).replace(second=0, microsecond=0)
T0 = T0 - datetime.timedelta(minutes=T0.minute % 15)

tail_b, tail_f = tails(active, True)
cp_branch = max(tail_b.values()); cp_full = max(tail_f.values())
chain_b = chain(active, tail_b); chain_f = chain(active, tail_f)
start, bend, land = schedule(active, 0)
end_main = max(land.values())
# deferred set after RC3
dstart, dbend, dland = schedule(sorted(deferred), end_main, done_before=bend)
end_def = max(dland.values()) if dland else end_main

# RC times
def rc_time(gate):
    ids = set()
    for g in gate:
        if g in umbrellas:
            ids |= {c for c in I[g]["children"] if c in land}
        elif g in land:
            ids.add(g)
    return max((land[g] for g in ids), default=None), sorted(ids)


rc_events = []
for rc, label, gate in RCS:
    t, ids = rc_time(gate)
    if rc == "RC3": t = end_main
    rc_events.append({"rc": rc, "label": label, "at": t, "gateIssues": ids})

# milestones
MS = collections.defaultdict(lambda: {"active": [], "deferred": 0, "target": None})
for k in leaves:
    key = (I[k]["pkey"], I[k]["milestone"])
    MS[key]["target"] = I[k]["milestoneTarget"]
    if k in deferred: MS[key]["deferred"] += 1
    else: MS[key]["active"].append(k)
MS_DONE = {key: max(land[k] for k in v["active"]) for key, v in MS.items() if v["active"]}


def chunk_plan(mix):
    costs = {k: issue_cost(k, mix) for k in leaves}
    stream = [(land[k], 0, k) for k in active] + [(e["at"], 1, e["rc"]) for e in rc_events]
    stream.sort(key=lambda x: (x[0], x[1], I[x[2]]["number"] if x[1] == 0 else 0))
    chunks, cur, run, prev_end = [], [], 0.0, 0
    for t, kind, k in stream:
        c = RC_LIST_COST if kind else costs[k]["total"]
        if run + c > CHUNK_USD + 1e-9 and cur:
            chunks.append((cur, run)); cur, run = [], 0.0
        cur.append((t, kind, k)); run += c
    if cur: chunks.append((cur, run))
    out = []
    umb_done_before = set()
    ms_done_before = set()
    for n, (items, run) in enumerate(chunks, 1):
        ids = [k for t, kind, k in items if kind == 0]
        rcs = [k for t, kind, k in items if kind == 1]
        cstart = prev_end; cend = max(t for t, _, _ in items); prev_end = cend
        byp = collections.defaultdict(lambda: {"issues": [], "umbrellasCompleted": [], "points": 0})
        for k in sorted(ids, key=lambda x: I[x]["number"]):
            byp[I[k]["pkey"]]["issues"].append(k); byp[I[k]["pkey"]]["points"] += I[k]["estimate"] or 0
        umb = {}
        for u in sorted(umbrellas, key=lambda x: I[x]["number"]):
            if u in umb_deferred or u in umb_done_before: continue
            ch = [c for c in I[u]["children"] if c in land]
            if ch and all(land[c] <= cend for c in ch):
                umb_done_before.add(u)
                umb[u] = {"title": I[u]["title"], "children": ch, "deferredChildren": len([c for c in I[u]["children"] if c in deferred])}
                byp[I[u]["pkey"]]["umbrellasCompleted"].append(u)
        ms = []
        for key, t in sorted(MS_DONE.items(), key=lambda x: x[1]):
            if key in ms_done_before or t > cend: continue
            ms_done_before.add(key)
            ms.append({"project": key[0], "milestone": key[1], "targetDate": MS[key]["target"], "issues": len(MS[key]["active"]),
                       "deferredIssuesExcluded": MS[key]["deferred"], "completedAt": tstr(t)})
        nj = []
        for nid in sorted(NJ, key=lambda x: int(x.split("-")[1])):
            item = NJ[nid]
            if nid == "NJ-14": continue
            gates = item["mappedTo"]
            firsts = []
            for g in gates:
                if g.startswith("RC"):
                    e = next(e for e in rc_events if e["rc"] == g)
                    firsts.append(e["at"])
                elif g in umbrellas:
                    firsts += [start[c] for c in I[g]["children"] if c in start]
                elif g in start:
                    firsts.append(start[g])
            if not firsts: continue
            f = min(firsts)
            if (cstart <= f < cend) or (n == 1 and f < cend) or (n == len(chunks) and f >= cstart):
                nj.append(item)
        rc_reached = [dict(e, at=tstr(e["at"])) for e in rc_events if e["rc"] in rcs]
        out.append({
            "chunk": n, "issues": ids, "issueCount": len(ids), "points": sum(I[k]["estimate"] or 0 for k in ids),
            "listCost": round(run, 2), "discountedCost": round(run * DISCOUNT, 2),
            "start": tstr(cstart), "end": tstr(cend), "end_min": cend, "hours": round((cend - cstart) / 60, 1),
            "cumulativeHours": round(cend / 60, 1), "firstIssueStart": tstr(min(start[k] for k in ids)) if ids else tstr(cstart),
            "byProject": dict(sorted(byp.items())), "umbrellasCompleted": umb,
            "byPhase": dict(collections.Counter(I[k]["phase"] for k in ids)),
            "byType": dict(collections.Counter(I[k]["type"] for k in ids)),
            "bySize": dict(collections.Counter(I[k]["size"] for k in ids)),
            "byBuilderModel": dict(collections.Counter(costs[k]["builderModel"] for k in ids)),
            "newProjectIssues": {p: len(byp[p]["issues"]) for p in NEW_PROJECTS if p in byp},
            "milestonesCompleted": ms, "releaseCandidatesReached": rc_reached, "needsJustinBeforeStart": nj,
        })
    # deferred chunk
    dcost = sum(costs[k]["total"] for k in deferred)
    dbyp = collections.defaultdict(lambda: {"issues": [], "points": 0})
    for k in sorted(deferred, key=lambda x: I[x]["number"]):
        dbyp[I[k]["pkey"]]["issues"].append(k); dbyp[I[k]["pkey"]]["points"] += I[k]["estimate"] or 0
    dchunk = {"chunk": "v0.2", "label": "Deferred set (%d leaves; needs NJ-14 go and NJ-19 v0.2 scoping)" % len(deferred),
              "issues": sorted(deferred, key=lambda x: I[x]["number"]), "issueCount": len(deferred),
              "points": sum(I[k]["estimate"] or 0 for k in deferred),
              "listCost": round(dcost, 2), "discountedCost": round(dcost * DISCOUNT, 2), "equivalentChunks": round(dcost / CHUNK_USD, 2),
              "start": tstr(end_main), "end": tstr(end_def), "hours": round((end_def - end_main) / 60, 1),
              "byProject": dict(sorted(dbyp.items())),
              "byBuilderModel": dict(collections.Counter(costs[k]["builderModel"] for k in deferred)),
              "needsJustinBeforeStart": [NJ["NJ-14"]] if "NJ-14" in NJ else []}
    total = sum(c["listCost"] for c in out)
    by_type = collections.defaultdict(float); by_phase = collections.defaultdict(float); by_model = collections.defaultdict(float)
    for k in active:
        by_type[I[k]["type"]] += costs[k]["total"]; by_phase[I[k]["phase"]] += costs[k]["total"]; by_model[costs[k]["builderModel"]] += costs[k]["builder"]
    totals = {"chunks": len(out), "issues": len(active), "points": sum(I[k]["estimate"] or 0 for k in active),
              "listCost": round(total, 2), "discountedCost": round(total * DISCOUNT, 2),
              "wholeChunksBilled": len(out), "wholeChunksBilledUsd": 50 * len(out),
              "wallClockHours": round(end_main / 60, 1), "wallClockDays24h": round(end_main / 60 / 24, 2), "end": tstr(end_main),
              "byType": {k: round(v, 2) for k, v in sorted(by_type.items())}, "byPhase": {k: round(v, 2) for k, v in sorted(by_phase.items())},
              "builderCostByModel": {k: round(v, 2) for k, v in sorted(by_model.items())},
              "buildersByModel": dict(collections.Counter(costs[k]["builderModel"] for k in active)),
              "rcReviews": RC_LIST_COST * 4,
              "withDeferred": {"listCost": round(total + dcost, 2), "discountedCost": round((total + dcost) * DISCOUNT, 2),
                               "wallClockHours": round(end_def / 60, 1), "end": tstr(end_def),
                               "chunks": math.ceil((total + dcost) / CHUNK_USD)}}
    return {"description": MIX[mix]["description"], "builderModels": MIX[mix]["builderModels"], "reviewerModel": MIX[mix]["reviewer"],
            "qaModel": MIX[mix]["qa"], "rcReviewModel": MIX[mix]["rc"], "rcReviewListCostEach": RC_LIST_COST,
            "totals": totals, "chunks": out, "deferredChunk": dchunk}, costs


plans, costs = {}, {}
for mix in ("A", "B", "B3"):
    plans[mix], costs[mix] = chunk_plan(mix)

# ---------------------------------------------------------------- per-day / per-block tables (mix B)
def day_of(m): return (T0 + datetime.timedelta(minutes=m)).strftime("%Y-%m-%d")
def block_of(m):
    d = T0 + datetime.timedelta(minutes=m)
    return d.strftime("%Y-%m-%d") + " %02d-%02dZ" % (d.hour // 6 * 6, d.hour // 6 * 6 + 6)


def concurrency_peak(pred):
    peak = 0
    for t in range(0, end_def + STEP, STEP):
        if not pred(t): continue
        peak = max(peak, sum(1 for k in start if start[k] <= t < bend[k]) + sum(1 for k in dstart if dstart[k] <= t < dbend[k]))
    return peak


all_start = dict(start); all_start.update(dstart)
all_land = dict(land); all_land.update(dland)
chunk_of = {}
for c in plans["B"]["chunks"]:
    for k in c["issues"]: chunk_of[k] = c["chunk"]
for k in deferred: chunk_of[k] = "v0.2"
blocks = collections.OrderedDict()
for k in sorted(all_start, key=lambda x: (all_start[x], I[x]["number"])):
    b = block_of(all_start[k])
    blocks.setdefault(b, {"starts": [], "landed": 0, "peak": 0, "chunks": set(), "nj": [], "rc": []})
    blocks[b]["starts"].append(k); blocks[b]["chunks"].add(chunk_of[k])
for k, t in all_land.items():
    b = block_of(t)
    blocks.setdefault(b, {"starts": [], "landed": 0, "peak": 0, "chunks": set(), "nj": [], "rc": []})
    blocks[b]["landed"] += 1
for e in rc_events:
    b = block_of(e["at"]); blocks.setdefault(b, {"starts": [], "landed": 0, "peak": 0, "chunks": set(), "nj": [], "rc": []}); blocks[b]["rc"].append(e["rc"])
for nid, item in NJ.items():
    firsts = []
    for g in item["mappedTo"]:
        if g.startswith("RC"): firsts.append(next(e["at"] for e in rc_events if e["rc"] == g))
        elif g in umbrellas: firsts += [all_start[c] for c in I[g]["children"] if c in all_start]
        elif g in all_start: firsts.append(all_start[g])
    if nid == "NJ-14": firsts = [end_main]
    if firsts:
        b = block_of(min(firsts)); blocks.setdefault(b, {"starts": [], "landed": 0, "peak": 0, "chunks": set(), "nj": [], "rc": []}); blocks[b]["nj"].append(nid)
blocks = collections.OrderedDict(sorted(blocks.items()))
for b, v in blocks.items():
    v["peak"] = concurrency_peak(lambda t, b=b: block_of(t) == b)
    v["chunks"] = sorted(v["chunks"], key=lambda x: (isinstance(x, str), x))
    v["nj"] = sorted(v["nj"], key=lambda x: int(x.split("-")[1]))

# per-day credit burn (mix B, list), buckets as in execution-schedule section 4
BUCKET = {"Build": "build", "Infra": "build", "Spec": "plan", "Research": "research", "Docs": "docs", "Review": "qa"}
ALLOW = {"S": 10, "M": 22, "L": 50}
days = collections.OrderedDict()
def dget(d):
    return days.setdefault(d, {"sessions": collections.Counter(), "phase": collections.Counter(), "build": 0.0, "qa": 0.0, "plan": 0.0,
                               "docs": 0.0, "research": 0.0, "allowance": 0.0, "starts": 0, "landed": 0, "rc": []})
for k, t in all_start.items():
    d = dget("v0.2 (after RC3)" if k in deferred else day_of(t)); c = costs["B"][k]
    d["sessions"][I[k]["size"]] += 1; d["starts"] += 1
    if I[k]["type"] in CODE: d["phase"][I[k]["phase"]] += 1
    d[BUCKET[I[k]["type"]]] += c["builder"]; d["qa"] += c["reviewer"] + c["qa"]; d["allowance"] += ALLOW[I[k]["size"]]
for k, t in all_land.items(): dget("v0.2 (after RC3)" if k in deferred else day_of(t))["landed"] += 1
for e in rc_events:
    d = dget(day_of(e["at"])); d["qa"] += RC_LIST_COST; d["rc"].append(e["rc"])
days = collections.OrderedDict(sorted(days.items(), key=lambda x: (x[0].startswith("v0.2"), x[0])))
cum = 0.0; burn_rows = []
for d, v in days.items():
    day_usd = v["build"] + v["qa"] + v["plan"] + v["docs"] + v["research"]; cum += day_usd
    burn_rows.append({"day": d, "sessions": "%d/%d/%d" % (v["sessions"]["S"], v["sessions"]["M"], v["sessions"]["L"]),
                      "buildStartsByPhase": "%d/%d/%d" % (v["phase"]["P0"], v["phase"]["P1"], v["phase"]["P2"]),
                      "build": round(v["build"]), "qa": round(v["qa"]), "plan": round(v["plan"]), "docs": round(v["docs"]),
                      "research": round(v["research"]), "day": d, "dayUsd": round(day_usd), "planLine": round(cum),
                      "justinUsd": round(cum * DISCOUNT, 2), "allowanceCrossCheck": round(v["allowance"]), "starts": v["starts"],
                      "landed": v["landed"], "rc": v["rc"]})

# ---------------------------------------------------------------- write
def dump(o, name):
    json.dump(o, open(os.path.join(HERE, name), "w"), indent=1)


for mix in ("A", "B", "B3"):
    dump({"mix": mix, "t0": T0.strftime("%Y-%m-%dT%H:%MZ"),
          "issues": {k: {"start": start[k], "buildEnd": bend[k], "land": land[k], "startAt": tstr(start[k]), "landAt": tstr(land[k]),
                         "size": I[k]["size"], "type": I[k]["type"], "phase": I[k]["phase"], "chunk": next((c["chunk"] for c in plans[mix]["chunks"] if k in c["issues"]), None),
                         **{kk: (round(v, 2) if isinstance(v, float) else v) for kk, v in costs[mix][k].items()}} for k in active},
          "deferred": {k: {"start": dstart[k], "land": dland[k], "startAt": tstr(dstart[k]), "landAt": tstr(dland[k]),
                           **{kk: (round(v, 2) if isinstance(v, float) else v) for kk, v in costs[mix][k].items()}} for k in deferred}},
         "sched-%s.json" % mix)
dump({"t0": T0.strftime("%Y-%m-%dT%H:%MZ"), "blocks": blocks}, "days.json")
dump(burn_rows, "burn.json")

summary = {
    "takenAt": G["takenAt"], "t0": T0.strftime("%Y-%m-%dT%H:%MZ"),
    "issues": len(I), "umbrellas": len(umbrellas), "deferredUmbrellas": len(umb_deferred), "leaves": len(leaves),
    "deferredLeaves": len(deferred), "activeLeaves": len(active),
    "edgesRaw": sum(len(i["blocks"]) for i in I.values()), "effectiveLeafEdges": sum(len(v) for v in EFF.values()),
    "sizes": dict(collections.Counter(I[k]["size"] for k in active)), "types": dict(collections.Counter(I[k]["type"] for k in active)),
    "phases": dict(collections.Counter(I[k]["phase"] for k in active)),
    "labelModels": dict(collections.Counter(I[k]["model"] for k in active)), "efforts": dict(collections.Counter(I[k]["effort"] for k in active)),
    "criticalPath": {"branchStartMin": cp_branch, "branchStartHours": round(cp_branch / 60, 1), "branchStartChain": chain_b,
                     "fullMin": cp_full, "fullHours": round(cp_full / 60, 1), "fullChain": chain_f},
    "serialHours": round(sum(full_min(k) for k in active) / 60, 1),
    "wallClock": {"builders": BUILDERS, "hours": round(end_main / 60, 1), "days24h": round(end_main / 60 / 24, 2), "end": tstr(end_main),
                  "meanBuildersBusy": round(sum(build_min(k) for k in active) / end_main, 1),
                  "withDeferredHours": round(end_def / 60, 1), "withDeferredEnd": tstr(end_def)},
    "rcEvents": [dict(e, at=tstr(e["at"])) for e in rc_events],
    "mixes": {m: plans[m]["totals"] for m in plans},
    "perDayStarts": {d: v["starts"] for d, v in days.items()},
    "perDayStartsAll": dict(collections.Counter(day_of(t) for t in all_start.values())),
}
dump(summary, "summary.json")

chunks_v2 = {"generatedAt": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
             "snapshotTakenAt": G["takenAt"], "round": 4, "canonicalMix": "B",
             "terms": dict(OLD["terms"], start=T0.strftime("%Y-%m-%dT%H:%MZ"),
                           scheduler="list scheduling over the live blocks graph (umbrella edges mapped onto children), branch-start rule "
                                     "(a dependent starts when every blocker's build minutes end = PR open), ready-first by longest remaining "
                                     "build tail; sizes from the Fibonacci estimate 2=S/3=M/5=L; build S 30 / M 75 / L 180 min + 20 review + 15 QA (code)",
                           costModel="round-3 token model (docs/cost-and-duration-estimate.md section 3); effort from the Effort label scales output "
                                     "tokens (low 0.6, medium 1.0, high 1.4, max 2.0); reviewer 40% of builder tokens; QA 25% (code only); "
                                     "x1.25 contingency; 4 RC reviews = L-size Fable 5.1 / high sessions at the RC gate times"),
             "counts": {"issues": len(I), "umbrellas": len(umbrellas), "leaves": len(leaves), "deferredLeaves": len(deferred), "activeLeaves": len(active)},
             "criticalPath": summary["criticalPath"], "wallClock": summary["wallClock"],
             "mixes": {"A": plans["A"], "B": plans["B"]},
             "reference": {"B3_round3Definition": {"description": plans["B3"]["description"], "totals": plans["B3"]["totals"]}},
             "round3": {"chunksB": OLD["mixes"]["B"]["totals"]["chunks"], "listCostB": OLD["mixes"]["B"]["totals"]["listCost"],
                        "discountedB": OLD["mixes"]["B"]["totals"]["discountedCost"], "wallClockHours": OLD["mixes"]["B"]["totals"]["wallClockHours"],
                        "issues": OLD["mixes"]["B"]["totals"]["issues"]}}
json.dump(chunks_v2, open(os.path.join(HERE, "..", "chunks-v2.json"), "w"), indent=1)

if __name__ == "__main__":
    print(json.dumps({k: v for k, v in summary.items() if k not in ("perDayStarts",)}, indent=1))
    for m in plans:
        print(m, [(c["chunk"], c["issueCount"], c["listCost"], c["hours"], c["end"]) for c in plans[m]["chunks"]], "deferred", plans[m]["deferredChunk"]["listCost"])
    print("per-day starts", summary["perDayStarts"])
