#!/usr/bin/env python3
"""Round 4: regenerate docs/build-chunks.md and splice the schedule/burn tables into docs/execution-schedule.md and
the round-4 results section into docs/cost-and-duration-estimate.md from plan/round4/chunks-v2.json and sched/*.json."""
import json, os, re, collections, datetime
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
G = json.load(open(os.path.join(HERE, "graph.json"))); I = G["issues"]
V2 = json.load(open(os.path.join(HERE, "..", "chunks-v2.json")))
S = json.load(open(os.path.join(HERE, "summary.json")))
DAYS = json.load(open(os.path.join(HERE, "days.json")))
BURN = json.load(open(os.path.join(HERE, "burn.json")))
OLD = json.load(open(os.path.join(ROOT, "plan", "chunks.json")))
A, B = V2["mixes"]["A"], V2["mixes"]["B"]
B3 = V2["reference"]["B3_round3Definition"]["totals"]
PNAME = {}
for k, i in I.items(): pass
from model import PKEY, NEW_PROJECTS  # noqa: E402  (model.py is import-safe; it re-runs the simulation quickly)
KEY2NAME = {v: k for k, v in PKEY.items()}
MODEL_SHORT = {"claude-fable-5-1": "Fable", "claude-opus-5": "Opus", "claude-sonnet-5": "Sonnet", "claude-haiku-4-5": "Haiku"}
umbrellas = {k for k, i in I.items() if i["children"]}
active = set(); chunk_of = {}
for c in B["chunks"]:
    for k in c["issues"]: active.add(k); chunk_of[k] = c["chunk"]
deferred = set(B["deferredChunk"]["issues"])
for k in deferred: chunk_of[k] = "v0.2"


def usd(x): return "${:,.0f}".format(x)
def usd2(x): return "${:,.2f}".format(x)
def short(ids): return " ".join(k.replace("PAP-", "") for k in ids)
def models(d): return ", ".join("%s %d" % (MODEL_SHORT[m], n) for m, n in sorted(d.items(), key=lambda x: -x[1]))


# ------------------------------------------------------------------ build-chunks.md
out = []
w = out.append
w("# PaperOS build in $2,500 chunks (discounted terms)\n")
w("Round 4 (2026-09-18). Live graph: `plan/round4/sched/graph.json`, takenAt %s (%d PAP issues after excluding PAP-1..PAP-12 and the %d Triage ideas; %d umbrellas, %d leaves of which %d carry `Deferred`). "
  "Generated %s by `plan/round4/sched/model.py`; raw data in `plan/round4/chunks-v2.json` (same shape as the round-3 `plan/chunks.json`, plus `round: 4`), per-issue schedule and cost in `plan/round4/sched/sched-A.json` / `sched-B.json`. "
  "Companion to `docs/cost-and-duration-estimate.md` (token model and prices, unchanged; round-4 results in its section 9) and `docs/execution-schedule.md` (block-by-block table and credit burn). "
  "The Chunk labels in Linear follow **mix B** of this document (`Chunk 1`..`Chunk 5` on the %d scheduled leaves, `Chunk: v0.2` on the %d deferred leaves, none on umbrellas; log `plan/round4/changes/chunks-relabel.json`).\n"
  % (G["takenAt"], S["issues"], len(G["excluded"]["triage"]), S["umbrellas"], S["leaves"], S["deferredLeaves"], V2["generatedAt"], S["activeLeaves"], S["deferredLeaves"]))
w("## 1. Terms\n")
w("* **Discount.** Justin pays **$50 for every $2,500 of list-price Claude spend** (x0.02). Every figure is given at list price and at the discounted price. A chunk = $2,500 list = $50 to Justin; a started chunk is billed whole, so the \"whole chunks billed\" line is what the invoice would read.")
w("* **Sessions run 24/7** with **16 concurrent builder sessions**; reviewer and QA sessions run on top of that cap. The clock starts at **%s** (the graph pull, rounded to the quarter hour)." % S["t0"])
w("* **Scope.** The **%d buildable, non-deferred leaves** (every PAP issue except PAP-1..PAP-12, the %d Triage ideas, the %d umbrellas and the %d deferred leaves). Umbrellas are never claimed; they complete when their last child lands. The deferred leaves are priced as the final `v0.2` chunk in section 5." % (S["activeLeaves"], len(G["excluded"]["triage"]), S["umbrellas"], S["deferredLeaves"]))
w("* **Sizes** come from the Linear estimate (Fibonacci, set in round 4): 2 = S (half a session-day), 3 = M (one), 5 = L (two). Scheduled set: S %d / M %d / L %d; %d points." % (S["sizes"].get("S", 0), S["sizes"].get("M", 0), S["sizes"].get("L", 0), B["totals"]["points"]))
w("* **Ordering.** List scheduling over the live `blocks` graph (%s relations; umbrella edges mapped onto their children give %s effective leaf edges; no cycles), ready-first by longest remaining build tail, then phase, priority, size. **Branch-start rule**: a dependent starts as soon as every blocker's PR is open, i.e. when the blocker's build minutes end; the blocker's review and QA run in parallel. Per-issue wall-clock S 30 / M 75 / L 180 min of build, plus 20 min review and 15 min QA (code issues). Identical for both mixes; only the price differs." % ("{:,}".format(S["edgesRaw"]), "{:,}".format(S["effectiveLeafEdges"])))
w("* **Cutting.** Issues are streamed in landing order (build + review + QA) and their fully loaded cost is accumulated; when the next issue would push the running total past $2,500 a new chunk starts. The four release-candidate reviews are inserted into the stream when their gate set (execution schedule section 3) lands.")
w("* **Cost per issue** (`cost-and-duration-estimate.md` section 3): builder tokens by Size (S 1.5M in / 60K out, M 4M / 150K, L 10M / 400K; 80% cache reads, 20% cache writes), k = 0.60 for Spec/Research/Docs/Review; **Effort from the `Reasoning effort` label** scales output tokens (low x0.6, medium x1.0, high x1.4, max x2.0); reviewer session = 40% of builder tokens; QA gate = 25% (code issues); x1.25 contingency. Each RC review = one L-size Fable 5.1 / high session = $68.75 list.")
w("* **Prices** ($/MTok, `claude-api` skill, 2026-09-17): Fable 5.1 $10 in / $50 out / $0.25 cache read / $12.50 cache write; Opus 5 $5 / $25 / $0.50 / $6.25; Sonnet 5 $2 / $10 / $0.20 / $2.50; Haiku 4.5 $1 / $5 / $0.10 / $1.25.\n")

w("## 2. The mixes\n")
w("| | Mix A | **Mix B (canonical)** | Mix B, round-3 definition (reference) |")
w("|---|---|---|---|")
w("| Builders | Fable 5.1 on all %d | the issue's `Model` label (%s); Fable 5.1 on every Spec / Research issue | Opus 5 on every Build / Infra / Docs / Review issue (%d); Fable 5.1 on Spec / Research (%d) |"
  % (S["activeLeaves"], models(B["totals"]["buildersByModel"]), B3["buildersByModel"]["claude-opus-5"], B3["buildersByModel"]["claude-fable-5-1"]))
w("| Reviewer sessions | Fable 5.1 / high | Fable 5.1 / high | Fable 5.1 / high |")
w("| QA gate (code issues) | Fable 5.1 / low | Opus 5 / low | Opus 5 / low |")
w("| 4 release-candidate reviews | Fable 5.1 / high | Fable 5.1 / high | Fable 5.1 / high |")
w("| Effort | as labeled | as labeled | as labeled |")
w("| **Chunks ($2,500 list each)** | **%d** | **%d** | %d |" % (A["totals"]["chunks"], B["totals"]["chunks"], B3["chunks"]))
w("| List cost, %d issues + 4 RC reviews | %s | %s | %s |" % (S["activeLeaves"], usd(A["totals"]["listCost"]), usd(B["totals"]["listCost"]), usd(B3["listCost"])))
w("| **Discounted cost to Justin** | **%s** | **%s** | %s |" % (usd2(A["totals"]["discountedCost"]), usd2(B["totals"]["discountedCost"]), usd2(B3["discountedCost"])))
w("| Whole chunks billed | %d x $50 = $%d | %d x $50 = $%d | %d x $50 = $%d |" % (A["totals"]["chunks"], A["totals"]["wholeChunksBilledUsd"], B["totals"]["chunks"], B["totals"]["wholeChunksBilledUsd"], B3["chunks"], B3["wholeChunksBilledUsd"]))
w("| Wall-clock at 16 builders, 24/7 | %.1f h (%.2f days), ends %s | same | same |" % (S["wallClock"]["hours"], S["wallClock"]["days24h"], S["wallClock"]["end"]))
w("| By phase (list) P0 / P1 / P2 | %s / %s / %s | %s / %s / %s | %s / %s / %s |" % tuple(usd(m["byPhase"][p]) for m in (A["totals"], B["totals"], B3) for p in ("P0", "P1", "P2")))
w("| + %d deferred (`v0.2` chunk, section 5) | +%s list = +%s, +%.1f h | +%s list = +%s, +%.1f h | +%s list = +%s |"
  % (S["deferredLeaves"], usd(A["deferredChunk"]["listCost"]), usd2(A["deferredChunk"]["discountedCost"]), A["deferredChunk"]["hours"],
     usd(B["deferredChunk"]["listCost"]), usd2(B["deferredChunk"]["discountedCost"]), B["deferredChunk"]["hours"],
     usd(B3["withDeferred"]["listCost"] - B3["listCost"]), usd2((B3["withDeferred"]["listCost"] - B3["listCost"]) * 0.02)))
w("| Everything (%d + %d) | %s list = **%s**, %.1f h | %s list = **%s**, %.1f h | %s list = %s |"
  % (S["activeLeaves"], S["deferredLeaves"], usd(A["totals"]["withDeferred"]["listCost"]), usd2(A["totals"]["withDeferred"]["discountedCost"]), S["wallClock"]["withDeferredHours"],
     usd(B["totals"]["withDeferred"]["listCost"]), usd2(B["totals"]["withDeferred"]["discountedCost"]), S["wallClock"]["withDeferredHours"],
     usd(B3["withDeferred"]["listCost"]), usd2(B3["withDeferred"]["discountedCost"])))
rev_share = sum(r["qa"] for r in BURN if not r["day"].startswith("v0.2")) / B["totals"]["listCost"]
w("\nMix A costs %s more at list than mix B, which is **%s more to Justin**. Both mixes run the same %.1f-hour schedule because durations are per Size, not per model. **Mix B stays the recommendation and is what the Chunk labels encode.** "
  "Two things changed in its definition since round 3: builder models now come from the `Model` labels every leaf carries (the CLAUDE.md model/effort rule, so the plan prices what the sessions will actually run: %s), and Spec / Research issues stay on Fable 5.1. "
  "Because %d of the builders are Sonnet 5, the Fable 5.1 reviewer overlay (40%% of builder tokens at 5x the price) is now the largest line: reviewer + QA + RC sessions are %d%% of the mix-B list cost. Switching reviewers to the `cost-and-duration-estimate.md` section 4b rule (Opus 5 after an Opus or Fable builder, Sonnet 5 after a Sonnet builder) would take roughly a chunk off; it is not applied here because every reviewer-session prompt in the plan names Fable. The round-3 definition (Opus 5 on every code builder) is kept as a reference column: %d chunks, %s."
  % (usd(A["totals"]["listCost"] - B["totals"]["listCost"]), usd2(A["totals"]["discountedCost"] - B["totals"]["discountedCost"]), S["wallClock"]["hours"],
     models(B["totals"]["buildersByModel"]), B["totals"]["buildersByModel"].get("claude-sonnet-5", 0), round(rev_share * 100), B3["chunks"], usd2(B3["discountedCost"])))
w("\nReading the clock: %.1f hours is session time with dependencies respected and nothing else in the way; 16 builders are busy %.1f of the time on average, so the build is capacity-bound (the branch-start critical path is %.1f h; without the branch-start rule the longest chain alone is %.1f h). "
  "Not in the clock: `Needs Justin` answers, merge-queue conflicts on shared files, the 30%% re-review bounce (its tokens are in the x1.25 contingency, its minutes are not). Section 3 lists, per chunk, which decisions must be answered before it starts. The `Needs Justin` queue holds five open items at a time (PAP-94), so chunk 1's items have to be batched into two cards.\n"
  % (S["wallClock"]["hours"], S["wallClock"]["meanBuildersBusy"], S["criticalPath"]["branchStartHours"], S["criticalPath"]["fullHours"]))


def overview(mix, name):
    w("| Chunk | Issues | Points | List | To Justin | Hours | Start | End | Builders by model | Release candidates | Milestones done | Issues from the 5 new projects |")
    w("|---|---|---|---|---|---|---|---|---|---|---|---|")
    for c in mix["chunks"]:
        w("| %d | %d | %d | %s | %s | %.1f | %s | %s | %s | %s | %d | %d |" % (c["chunk"], c["issueCount"], c["points"], usd(c["listCost"]), usd2(c["discountedCost"]), c["hours"], c["start"], c["end"],
                                                                   models(c["byBuilderModel"]), ", ".join(r["rc"] for r in c["releaseCandidatesReached"]) or "-", len(c["milestonesCompleted"]), sum(c["newProjectIssues"].values())))
    t = mix["totals"]
    w("| **Total** | **%d** | **%d** | **%s** | **%s** | **%.1f** | %s | %s | %s | RC0-RC3 | %d | %d |\n" % (t["issues"], t["points"], usd(t["listCost"]), usd2(t["discountedCost"]), t["wallClockHours"], mix["chunks"][0]["start"], t["end"], models(t["buildersByModel"]),
                                                                              sum(len(c["milestonesCompleted"]) for c in mix["chunks"]), sum(sum(c["newProjectIssues"].values()) for c in mix["chunks"])))


w("## 3. Mix B (canonical): builders from the Model labels, Fable 5.1 on Spec/Research, reviewers and RC reviews; Opus 5 QA gate\n")
overview(B, "B")
for c in B["chunks"]:
    w("### Chunk %d: %s list, %s to Justin, %.1f h (%s to %s)\n" % (c["chunk"], usd(c["listCost"]), usd2(c["discountedCost"]), c["hours"], c["start"], c["end"]))
    w("%d issues, %d points: P0 %d / P1 %d / P2 %d; %s; sizes S %d / M %d / L %d; builders %s. Earliest issue in the chunk started %s (overlap with the previous chunk).\n"
      % (c["issueCount"], c["points"], c["byPhase"].get("P0", 0), c["byPhase"].get("P1", 0), c["byPhase"].get("P2", 0),
         ", ".join("%s %d" % (t, n) for t, n in sorted(c["byType"].items())), c["bySize"].get("S", 0), c["bySize"].get("M", 0), c["bySize"].get("L", 0), models(c["byBuilderModel"]), c["firstIssueStart"]))
    w("**Needs Justin before this chunk starts**\n")
    if c["needsJustinBeforeStart"]:
        for nj in c["needsJustinBeforeStart"]:
            w("* %s%s: %s Gates: %s." % (nj["id"], " (resolved)" if nj.get("status") == "resolved" else "", nj["text"], ", ".join(g.replace("PAP-", "") for g in nj["mappedTo"])))
    else:
        w("* None new; every earlier item stays answered.")
    w("\n**Issues by project** (identifiers omit `PAP-`; umbrellas in bold complete in this chunk)\n")
    w("| Project | Issues | Points | Umbrellas completed |")
    w("|---|---|---|---|")
    for pk, v in c["byProject"].items():
        umbs = ", ".join("**%s** %s" % (u.replace("PAP-", ""), I[u]["title"][:60]) for u in v["umbrellasCompleted"]) or "-"
        w("| %s (`%s`) | %s | %d | %s |" % (KEY2NAME.get(pk, pk), pk, short(v["issues"]), v["points"], umbs))
    w("\n**Deliverable at the end of the chunk**\n")
    for rc in c["releaseCandidatesReached"]:
        w("* **%s** review runs at %s: %s." % (rc["rc"], rc["at"], rc["label"]))
    if c["milestonesCompleted"]:
        w("* Milestones completed (non-deferred scope): " + "; ".join("%s / %s (%d issues%s, target %s, done %s)" % (KEY2NAME.get(m["project"], m["project"]), m["milestone"], m["issues"], ", %d deferred excluded" % m["deferredIssuesExcluded"] if m["deferredIssuesExcluded"] else "", m["targetDate"], m["completedAt"]) for m in c["milestonesCompleted"]) + ".")
    else:
        w("* No milestone closes in this chunk; it is the middle of the long P1 chains (tables, identity, realtime, spec-builder).")
    if c["newProjectIssues"]:
        w("* New projects (round 4): " + ", ".join("`%s` %d" % (p, n) for p, n in c["newProjectIssues"].items()) + ".")
    w("")

w("## 4. Mix A: all Fable 5.1 (builders, reviewers, QA, RC reviews)\n")
overview(A, "A")
nj_a = collections.OrderedDict()
for c in A["chunks"]:
    nj_a[c["chunk"]] = [n["id"] for n in c["needsJustinBeforeStart"]]
w("Same schedule and the same issue order as mix B; only the dollar boundaries move, so the chunk contents differ. Chunk contents, milestones and Needs Justin items per chunk are in `plan/round4/chunks-v2.json` under `mixes.A.chunks`. The Needs Justin items map to mix A chunks as follows: " +
  "; ".join("chunk %d: %s" % (n, ", ".join(ids) if ids else "none") for n, ids in nj_a.items()) + ".\n")

d = B["deferredChunk"]
w("## 5. Final chunk `v0.2`: the %d deferred leaves\n" % d["issueCount"])
w("Claimable only after NJ-14 (stop-loss go) and rescoped to v0.2 at NJ-19; each carries the `Deferred` label (own or inherited from a deferred umbrella) and now the `Chunk: v0.2` label. %d points. Scheduled with the same 16 builders after RC3: **%.1f h** (%s to %s) in both mixes. It is one chunk in the plan but %.2f chunks of money under mix B, so billed whole it is $100.\n" % (d["points"], d["hours"], d["start"], d["end"], d["equivalentChunks"]))
w("| Mix | List | To Justin | Equivalent chunks | Builders |")
w("|---|---|---|---|---|")
w("| A | %s | %s | %.2f | %s |" % (usd(A["deferredChunk"]["listCost"]), usd2(A["deferredChunk"]["discountedCost"]), A["deferredChunk"]["equivalentChunks"], models(A["deferredChunk"]["byBuilderModel"])))
w("| B | %s | %s | %.2f | %s |\n" % (usd(d["listCost"]), usd2(d["discountedCost"]), d["equivalentChunks"], models(d["byBuilderModel"])))
w("Issues by project: " + "; ".join("`%s` %s (%d pts)" % (pk, short(v["issues"]), v["points"]) for pk, v in d["byProject"].items()) + ".\n")
w("Needs Justin before it starts: NJ-14: Stop-loss checkpoint: go or no-go on the stretch pool (deferred set).\n")

w("## 6. The five round-4 projects\n")
w("Each has three milestones (10-01 contract, 10-09 surfaces, 10-16 swap and hardening) and mostly deferred work: the 10-01 contract slice is scheduled, the rest is `v0.2`.\n")
w("| Project | Key | Leaves | Scheduled | Deferred | Points | Scheduled issues by chunk | Milestones |")
w("|---|---|---|---|---|---|---|---|")
for pk in NEW_PROJECTS:
    name = KEY2NAME[pk]
    ks = [k for k, i in I.items() if i["project"] == name and k not in umbrellas]
    sched = sorted((k for k in ks if k in active), key=lambda x: I[x]["number"])
    by = collections.defaultdict(list)
    for k in sched: by[chunk_of[k]].append(k)
    ms = sorted({(i["milestoneTarget"], i["milestone"]) for k, i in I.items() if i["project"] == name})
    w("| %s | `%s` | %d | %d | %d | %d | %s | %s |" % (name, pk, len(ks), len(sched), len([k for k in ks if k in deferred]), sum(I[k]["estimate"] or 0 for k in ks),
                                                     "; ".join("chunk %s: %s" % (c, short(v)) for c, v in sorted(by.items())) or "-", "; ".join("%s (%s)" % (m, t) for t, m in ms)))
w("")

w("## 7. Delta versus round 3\n")
o = OLD["mixes"]["B"]["totals"]
w("| | Round 3 (2026-09-17) | Round 4 (2026-09-18) |")
w("|---|---|---|")
w("| Scheduled leaves | %d | %d |" % (o["issues"], S["activeLeaves"]))
w("| Deferred leaves | 42 | %d |" % S["deferredLeaves"])
w("| Umbrellas | 52 | %d |" % S["umbrellas"])
w("| `blocks` relations | 1,148 effective | %s live, %s effective |" % ("{:,}".format(S["edgesRaw"]), "{:,}".format(S["effectiveLeafEdges"])))
w("| Critical path | 36.8 h (full durations) | %.1f h branch-start, %.1f h full durations |" % (S["criticalPath"]["branchStartHours"], S["criticalPath"]["fullHours"]))
w("| Wall-clock at 16 builders | %.1f h | %.1f h (mean builders busy %.1f of 16) |" % (o["wallClockHours"], S["wallClock"]["hours"], S["wallClock"]["meanBuildersBusy"]))
w("| Mix B chunks / list / to Justin | %d / %s / %s | %d / %s / %s |" % (o["chunks"], usd(o["listCost"]), usd2(o["discountedCost"]), B["totals"]["chunks"], usd(B["totals"]["listCost"]), usd2(B["totals"]["discountedCost"])))
w("| Mix A chunks / list / to Justin | %d / %s / %s | %d / %s / %s |" % (OLD["mixes"]["A"]["totals"]["chunks"], usd(OLD["mixes"]["A"]["totals"]["listCost"]), usd2(OLD["mixes"]["A"]["totals"]["discountedCost"]), A["totals"]["chunks"], usd(A["totals"]["listCost"]), usd2(A["totals"]["discountedCost"])))
w("| Deferred chunk, mix B | $983 / $19.66 / 5.5 h | %s / %s / %.1f h |\n" % (usd(d["listCost"]), usd2(d["discountedCost"]), d["hours"]))
w("Why: (1) **Scope.** 601 scheduled leaves instead of 326: 280 of the round-3 leaves are still leaves, 46 became umbrellas when round 4 gave them sub-issues (their children are counted instead), 60 are the round-3 module-system issues PAP-433..497 that had no chunk yet, and 261 are round-4 issues; 155 of the 416 round-4 issues are deferred (`v0.2`). "
  "(2) **Models.** Builder models now follow the `Model` labels (scenario E of the estimate: mostly Sonnet 5), so the per-issue price fell while the issue count rose 84%%: list cost +%d%% for +84%% issues. Under the round-3 definition (Opus 5 on every code builder) the same graph would be %d chunks / %s / %s. "
  "(3) **Clock.** The branch-start rule shortened the longest chain (%.1f h instead of a would-be %.1f h), but with 84%% more build minutes 16 builders are saturated, so the wall clock moved only from %.1f h to %.1f h; the schedule is now capacity-bound, and 20 builders would bring it near the %.1f-hour critical path. "
  "(4) **Recount.** The token model recomputed over the round-3 issue set with round-4 sizes gives $7,714 versus the $7,634 booked then (1%%, from estimates that moved when Size text became Fibonacci points).\n"
  % (round((B["totals"]["listCost"] / o["listCost"] - 1) * 100), B3["chunks"], usd(B3["listCost"]), usd2(B3["discountedCost"]), S["criticalPath"]["branchStartHours"], S["criticalPath"]["fullHours"], o["wallClockHours"], S["wallClock"]["hours"], S["criticalPath"]["branchStartHours"]))

w("## 8. How to use this\n")
w("1. Answer the chunk-1 Needs Justin items (%s) before the first session starts; batch them into cards of five." % ", ".join(n["id"] for n in B["chunks"][0]["needsJustinBeforeStart"] if n.get("status") != "resolved"))
w("2. Run chunk 1 at 16 builders. The orchestrator uses the Chunk label order as its tie-breaker among Ready for Claude issues; sessions still claim from Ready for Claude only. Ledger reports list spend per chunk in the daily burn report (PAP-98) so the x0.02 invoice can be checked against the console.")
w("3. Re-baseline after chunk 1: real per-size token burn replaces the S / M / L assumptions, `plan/round4/sched/pull_graph.py` then `model.py` regenerate this document, and `relabel.py` moves the Chunk labels.")
w("4. Each chunk boundary is a natural stop: nothing in a later chunk is needed to keep an earlier chunk's deliverable working, so Justin can pause after any $50.")
open(os.path.join(ROOT, "docs", "build-chunks.md"), "w").write("\n".join(out) + "\n")

# ------------------------------------------------------------------ execution-schedule.md
NJTEXT = {}
for c in B["chunks"] + [B["deferredChunk"]]:
    for nj in c["needsJustinBeforeStart"]: NJTEXT[nj["id"]] = nj["text"]
rows = ["| Block (UTC) | Starts | Peak | Landed (reviewer sessions) | Chunk | Needs Justin / checkpoint |", "| -- | -- | -- | -- | -- | -- |"]
for b, v in DAYS["blocks"].items():
    nj = " ".join("%s %s" % (n, NJTEXT.get(n, "")) for n in v["nj"])
    rc = " ".join("**%s.**" % r for r in v["rc"])
    rows.append("| %s | %d: %s | %d | %d | %s | %s |" % (b, len(v["starts"]), short(v["starts"]), v["peak"], v["landed"], ", ".join(str(c) for c in v["chunks"]), (nj + " " + rc).strip() or "Queue drains."))
sec2 = ("## 2. Block by block\n\nIdentifiers omit `PAP-`. Regenerated 2026-09-18 from `plan/round4/sched/model.py` (16 builders 24/7, branch-start rule, clock start %s); one row per six-hour block because the whole scheduled scope lands in %.1f h. "
        "*Starts* = builder sessions launched in the block; *Peak* = concurrent builder sessions; *Landed* = PRs whose review and QA finish in the block (one reviewer session each, on top of the builder cap); *Chunk* = the `Chunk` label(s) of the issues starting in the block (`v0.2` = deferred set, after RC3 and NJ-14 only). Raw rows: `plan/round4/sched/days.json`.\n\n%s\n\n"
        "Longest chain (branch-start, %.1f h): %s. Without the branch-start rule the same chain is %.1f h. The schedule is capacity-bound (16 builders busy %.1f of the time), so a slipped issue moves its milestone only if it sits on this chain or on the tables / identity / realtime P1 chains; Atlas re-simulates nightly and republishes this table.\n"
        % (S["t0"], S["wallClock"]["hours"], "\n".join(rows), S["criticalPath"]["branchStartHours"], " -> ".join(k.replace("PAP-", "") for k in S["criticalPath"]["branchStartChain"]), S["criticalPath"]["fullHours"], S["wallClock"]["meanBuildersBusy"]))

brows = ["| Day | Sessions S/M/L | Build starts P0/P1/P2 | Landed | Build $ | QA $ | Plan $ | Docs $ | Research $ | Day $ | Plan line $ | To Justin (x0.02) | Allowance cross-check $ |", "| -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- |"]
for r in BURN:
    brows.append("| %s | %s | %s | %d | %s | %s | %s | %s | %s | %s | %s | %s | %s |" % (r["day"] + (" (%s)" % ", ".join(r["rc"]) if r["rc"] else ""), r["sessions"], r["buildStartsByPhase"], r["landed"], "{:,}".format(r["build"]), "{:,}".format(r["qa"]), "{:,}".format(r["plan"]), r["docs"], r["research"], "{:,}".format(r["dayUsd"]), "{:,}".format(r["planLine"]), usd2(r["justinUsd"]), "{:,}".format(r["allowanceCrossCheck"])))
bt = B["totals"]["byType"]
build_b = sum(json.load(open(os.path.join(HERE, "sched-B.json")))["issues"][k]["builder"] for k in active if I[k]["type"] in ("Build", "Infra"))
plan_b = sum(json.load(open(os.path.join(HERE, "sched-B.json")))["issues"][k]["builder"] for k in active if I[k]["type"] == "Spec")
docs_b = sum(json.load(open(os.path.join(HERE, "sched-B.json")))["issues"][k]["builder"] for k in active if I[k]["type"] == "Docs")
res_b = sum(json.load(open(os.path.join(HERE, "sched-B.json")))["issues"][k]["builder"] for k in active if I[k]["type"] == "Research")
rev_b = sum(json.load(open(os.path.join(HERE, "sched-B.json")))["issues"][k]["builder"] for k in active if I[k]["type"] == "Review")
qa_b = B["totals"]["listCost"] - build_b - plan_b - docs_b - res_b - rev_b
tot = B["totals"]["listCost"]
sec4 = ("## 4. Credit burn model\n\nRound 4: list price under mix B from the token model of `docs/cost-and-duration-estimate.md` section 3 (builder tokens by Size, Effort as labeled, reviewer 40%% on Fable 5.1, QA gate 25%% on Opus 5 for code issues, x1.25 contingency, RC reviews $68.75 each), booked on the day a session starts. "
        "*Build $* = builder sessions of Build / Infra issues; *QA $* = every reviewer session, QA gate and RC review; *Plan $* = Spec builders; *Docs $*, *Research $* = those builders. *To Justin* is the cumulative plan line x0.02 (billed as whole $2,500 chunks: %d x $50 = $%d for the scheduled scope, +$100 with `v0.2`). "
        "The *allowance cross-check* is the old per-session allowance (S $10, M $22, L $50) summed over the day's builder starts: it tracks the builder columns within about 15%%, so PAP-98 metering and the PAP-111 2x hard stop (S $20, M $44, L $100) keep their numbers. Raw rows: `plan/round4/sched/burn.json`.\n\n%s\n\n"
        "Reconciliation to the round-2 12/45/30/8/5 split (scheduled scope, mix B, list):\n\n| Bucket | List $ | Share | To Justin | Round-2 share |\n| -- | -- | -- | -- | -- |\n"
        "| Planning (%d Spec builders) | %s | %d%% | %s | 12%% |\n| Building (%d Build / Infra builders) | %s | %d%% | %s | 45%% |\n| Automated QA (%d reviewer sessions, %d QA gates, 4 RC reviews, %d Review builders) | %s | %d%% | %s | 30%% |\n| Docs (%d Docs builders) | %s | %d%% | %s | 8%% |\n| Research (%d Research builders) | %s | %d%% | %s | 5%% |\n| **Total** | **%s** | 100%% | **%s** | |\n\n"
        "QA is the largest bucket because the reviewer overlay runs on Fable 5.1 behind %d Sonnet 5 builders; the retry pool ($360), the $500 RC3 reserve and the stop-loss rules of section 5 are unchanged and sit outside these figures.\n"
        % (B["totals"]["chunks"], B["totals"]["wholeChunksBilledUsd"], "\n".join(brows),
           S["types"]["Spec"], usd(plan_b), round(plan_b / tot * 100), usd2(plan_b * 0.02),
           S["types"]["Build"] + S["types"]["Infra"], usd(build_b), round(build_b / tot * 100), usd2(build_b * 0.02),
           S["activeLeaves"], S["types"]["Build"] + S["types"]["Infra"], S["types"]["Review"], usd(qa_b + rev_b), round((qa_b + rev_b) / tot * 100), usd2((qa_b + rev_b) * 0.02),
           S["types"]["Docs"], usd(docs_b), round(docs_b / tot * 100), usd2(docs_b * 0.02),
           S["types"]["Research"], usd(res_b), round(res_b / tot * 100), usd2(res_b * 0.02),
           usd(tot), usd2(tot * 0.02), B["totals"]["buildersByModel"].get("claude-sonnet-5", 0)))

note = ("\n### Round 4 (2026-09-18)\n\n"
        "* **Scope re-planned over the expanded graph.** Team PAP now holds %d specified issues (PAP-13 upward, Triage ideas excluded): %d umbrellas, %d leaves of which %d carry `Deferred` (own label or a deferred umbrella) and %d are scheduled. The tables in sections 2 and 4 were regenerated from `plan/round4/sched/model.py` under Justin's 24/7 terms (16 builders, $50 per $2,500 list, mix B); the rules above are unchanged, only the calendar moved from 15 days of half-day sessions to %.1f hours of continuous sessions (%s to %s), plus %.1f h for the `v0.2` set. The `Needs Justin` items keep their NJ numbers; section 2 shows the block in which each is first needed.\n"
        "* **Cycles hold in-flight work only.** Linear moves a Backlog issue to the default unstarted state when it joins a cycle, so planned issues never carry a cycle; `cycleIssueAutoAssignStarted` is on for team PAP and an issue joins the active cycle (C1 to 09-25, C2 to 10-02, C3 v0.2 stretch) the moment it moves to In Progress. Ready for Claude issues sit in the current cycle. Planned timing lives in due dates and Chunk labels, not in cycles.\n"
        "* **Estimates are Fibonacci points**: S = 2 (half a session-day), M = 3 (one), L = 5 (two), set on every leaf; umbrellas carry none so Linear rolls up their children. The scheduler reads the estimate, not the `**Size**` text. Scheduled scope: %d points; deferred: %d.\n"
        "* **Due dates are milestone target dates**, not the simulated landing time: every non-deferred issue's `dueDate` equals its project milestone's `targetDate` (section 7 dates; the five round-4 projects use 10-01 / 10-09 / 10-16). The simulation lands everything well before those dates; the dates stay as the commitment the burn report measures slips against.\n"
        "* **Chunk labels follow mix B** of `docs/build-chunks.md`: `Chunk 1`..`Chunk 5` on the %d scheduled leaves, `Chunk: v0.2` on the %d deferred leaves, none on umbrellas (exactly one per leaf; round 3 had applied mix A to 326 leaves and left 46 issues that later became umbrellas labelled). Log: `plan/round4/changes/chunks-relabel.json`. The orchestrator uses the chunk order only as a tie-breaker among Ready for Claude issues.\n"
        "* **Deferred set.** The 28 issues listed under *Deferred to v0.2* above grew to %d leaves and %d umbrellas in rounds 3-4 (label `Deferred`, priority 4, `Chunk: v0.2`, no cycle, no due date); the two FIX rules still hold: no `blocks` edge runs from a deferred issue to a scheduled one (verified 2026-09-18, `plan/round4/verify.md`) and PAP-96 never claims one.\n"
        % (S["issues"], S["umbrellas"], S["leaves"], S["deferredLeaves"], S["activeLeaves"], S["wallClock"]["hours"], S["t0"], S["wallClock"]["end"], B["deferredChunk"]["hours"],
           B["totals"]["points"], B["deferredChunk"]["points"], S["activeLeaves"], S["deferredLeaves"], S["deferredLeaves"], S["deferredUmbrellas"]))

p = os.path.join(ROOT, "docs", "execution-schedule.md")
doc = open(p).read()
header_new = ("# PaperOS Execution Schedule\n\n"
              "Plan for team PAP under the round-4 graph (2026-09-18): %d specified issues, %d umbrellas tracked through their children, %d leaves of which %d are scheduled and %d deferred to `v0.2`. Simulated over the live `blocks` graph (%s relations, no cycles) with 16 builder sessions running 24/7 from %s; model in `plan/round4/sched/` (round 2's 15-day half-day model stays in `round2/sched/` for history). The rules in section 1 are unchanged; the Round 4 note at the end of section 1 records what changed in Linear.\n"
              % (S["issues"], S["umbrellas"], S["leaves"], S["activeLeaves"], S["deferredLeaves"], "{:,}".format(S["edgesRaw"]), S["t0"]))
doc = re.sub(r"\A# PaperOS Execution Schedule\n\n.*?\n(?=\n## 1\.)", header_new, doc, count=1, flags=re.S)
doc = re.sub(r"## 2\. Day by day\n.*?(?=\n## 3\.)", sec2, doc, count=1, flags=re.S)
doc = re.sub(r"## 4\. Credit burn model\n.*?(?=\n## 5\.)", sec4, doc, count=1, flags=re.S)
if "### Round 4 (2026-09-18)" not in doc:
    doc = doc.replace("\n## 2. Block by block", note + "\n## 2. Block by block", 1)
else:
    doc = re.sub(r"\n### Round 4 \(2026-09-18\)\n.*?(?=\n## 2\.)", note, doc, count=1, flags=re.S)
open(p, "w").write(doc)

# ------------------------------------------------------------------ cost-and-duration-estimate.md
sec9 = ("\n## 9. Round 4 results (2026-09-18)\n\n"
        "Re-run of the same token model, prices and scheduler over the live graph after round 4 (`plan/round4/sched/graph.json`, takenAt %s; model `plan/round4/sched/model.py`; chunk plan `plan/round4/chunks-v2.json`; narrative in `docs/build-chunks.md`). "
        "Inventory: %d specified issues, %d umbrellas, %d leaves, **%d scheduled** (S %d / M %d / L %d from the Fibonacci estimates; Build %d, Infra %d, Spec %d, Research %d, Docs %d, Review %d; P0 %d / P1 %d / P2 %d) and %d deferred. %s live `blocks` relations (%s effective leaf edges after mapping umbrella edges onto children), no cycles. Builder models are read from the `Model` labels (%s), Effort from the `Reasoning effort` labels (%s).\n\n"
        "| | Mix A (all Fable 5.1) | **Mix B (canonical)** | Mix B, round-3 definition (reference) |\n|---|---|---|---|\n"
        "| Builders | Fable 5.1 | `Model` label (Opus 5 default); Fable 5.1 on Spec / Research | Opus 5 on every code / docs / review issue; Fable 5.1 on Spec / Research |\n"
        "| Reviewer / QA gate / RC reviews | Fable / Fable / Fable | Fable 5.1 high / Opus 5 low / Fable 5.1 | Fable 5.1 high / Opus 5 low / Fable 5.1 |\n"
        "| List, %d issues + 4 RC reviews | %s | **%s** | %s |\n| To Justin (x0.02) | %s | **%s** | %s |\n| Chunks ($2,500 list), billed whole | %d ($%d) | **%d ($%d)** | %d ($%d) |\n"
        "| + %d deferred (`v0.2`) | +%s (+%s) | +%s (+%s) | +%s (+%s) |\n| Everything | %s (%s), %d chunks | **%s (%s), %d chunks** | %s (%s), %d chunks |\n\n"
        "Duration (both mixes): critical path **%.1f h** with the branch-start rule (%.1f h if every dependent waited for its blocker's review and QA); serial %.1f h; **%.1f h at 16 builders 24/7** (%s to %s, mean builders busy %.1f, so the build is capacity-bound rather than chain-bound); +%.1f h for the deferred set. Per-day builder starts: %s.\n\n"
        "Delta versus round 3 (326 issues, 4 chunks, $7,909 / $158.17, 37.3 h): +275 scheduled leaves (46 round-3 leaves became umbrellas and are replaced by their children; 60 module-system issues PAP-433..497 and 261 round-4 issues joined; 155 round-4 issues are deferred); list cost +%d%% because the builders now run on the labelled models, mostly Sonnet 5, instead of Opus 5 everywhere (the round-3 definition gives %d chunks / %s / %s on the same graph); wall clock +%.1f h because the extra build minutes saturate 16 builders even though the branch-start rule cut the longest chain to %.1f h. The reviewer overlay on Fable 5.1 is now %d%% of the mix-B list cost; applying section 4b's reviewer rule instead would save about a chunk and is the first lever if Justin wants fewer than %d chunks.\n"
        % (G["takenAt"], S["issues"], S["umbrellas"], S["leaves"], S["activeLeaves"], S["sizes"].get("S", 0), S["sizes"].get("M", 0), S["sizes"].get("L", 0),
           S["types"]["Build"], S["types"]["Infra"], S["types"]["Spec"], S["types"]["Research"], S["types"]["Docs"], S["types"]["Review"], S["phases"]["P0"], S["phases"]["P1"], S["phases"]["P2"], S["deferredLeaves"],
           "{:,}".format(S["edgesRaw"]), "{:,}".format(S["effectiveLeafEdges"]),
           ", ".join("%s %d" % (k.replace("Model: ", ""), v) for k, v in sorted(S["labelModels"].items(), key=lambda x: -x[1])),
           ", ".join("%s %d" % (k.replace("Effort: ", ""), v) for k, v in sorted(S["efforts"].items(), key=lambda x: -x[1])),
           S["activeLeaves"], usd(A["totals"]["listCost"]), usd(B["totals"]["listCost"]), usd(B3["listCost"]),
           usd2(A["totals"]["discountedCost"]), usd2(B["totals"]["discountedCost"]), usd2(B3["discountedCost"]),
           A["totals"]["chunks"], A["totals"]["wholeChunksBilledUsd"], B["totals"]["chunks"], B["totals"]["wholeChunksBilledUsd"], B3["chunks"], B3["wholeChunksBilledUsd"],
           S["deferredLeaves"], usd(A["deferredChunk"]["listCost"]), usd2(A["deferredChunk"]["discountedCost"]), usd(B["deferredChunk"]["listCost"]), usd2(B["deferredChunk"]["discountedCost"]),
           usd(B3["withDeferred"]["listCost"] - B3["listCost"]), usd2((B3["withDeferred"]["listCost"] - B3["listCost"]) * 0.02),
           usd(A["totals"]["withDeferred"]["listCost"]), usd2(A["totals"]["withDeferred"]["discountedCost"]), A["totals"]["withDeferred"]["chunks"],
           usd(B["totals"]["withDeferred"]["listCost"]), usd2(B["totals"]["withDeferred"]["discountedCost"]), B["totals"]["withDeferred"]["chunks"],
           usd(B3["withDeferred"]["listCost"]), usd2(B3["withDeferred"]["discountedCost"]), B3["withDeferred"]["chunks"],
           S["criticalPath"]["branchStartHours"], S["criticalPath"]["fullHours"], S["serialHours"], S["wallClock"]["hours"], S["t0"], S["wallClock"]["end"], S["wallClock"]["meanBuildersBusy"], B["deferredChunk"]["hours"],
           ", ".join("%s %d" % (d, n) for d, n in S["perDayStarts"].items()),
           round((B["totals"]["listCost"] / OLD["mixes"]["B"]["totals"]["listCost"] - 1) * 100), B3["chunks"], usd(B3["listCost"]), usd2(B3["discountedCost"]),
           S["wallClock"]["hours"] - OLD["mixes"]["B"]["totals"]["wallClockHours"], S["criticalPath"]["branchStartHours"], round(rev_share * 100), B["totals"]["chunks"]))
p = os.path.join(ROOT, "docs", "cost-and-duration-estimate.md")
doc = open(p).read()
doc = re.sub(r"\n## 9\. Round 4 results.*\Z", "", doc, flags=re.S).rstrip("\n") + "\n" + sec9
open(p, "w").write(doc)
print("docs written")
