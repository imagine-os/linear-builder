---
identifier: "PAP-139"
title: "Benchmark Yjs vs Automerge vs Loro for document CRDT and write an ADR"
project: "realtime"
projectName: "Multiplayer & Realtime"
phase: "P0"
type: "Research"
priority: 2
surfaces: ["Developer"]
milestone: "Yjs server and presence"
state: "Ready for Claude"
parent: null
children: []
blockedBy: []
blocks: ["PAP-140"]
key: "realtime/realtime-research"
url: "https://linear.app/paperos/issue/PAP-139/benchmark-yjs-vs-automerge-vs-loro-for-document-crdt-and-write-an-adr"
source: "Linear snapshot 2026-09-17T13:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T04:53:30.222Z"
---

# PAP-139: Benchmark Yjs vs Automerge vs Loro for document CRDT and write an ADR

**Goal**

Confirm with measurements that Yjs is the right document CRDT before the Hocuspocus server (PAP-140), editor (PAP-142) and canvas (PAP-132) are built on it. Output: an ADR plus a reproducible benchmark harness so the choice can be reopened with the same numbers if Loro or Automerge overtake Yjs.

**Scope**

In:

* Harness `packages/collab/bench/` comparing `yjs` 13.6.x, `@automerge/automerge` 2.x and `loro-crdt` 1.x behind one `CrdtAdapter` interface.
* Workloads: (a) 200k-character rich-text doc with 50k random edits; (b) canvas map of 10k shapes with 20k property updates; (c) 50 simulated peers for 60 s at 200 ms latency.
* Metrics: encoded size, load time, memory after load, per-op apply p50/p99, merge time of two divergent 10k-op histories, gzip WASM size, TypeScript quality, ecosystem (Tiptap and React Flow bindings, server persistence, awareness, licence).
* ADR `docs/adr/00NN-PAP-139-document-crdt.md` in the PAP-130 format with reopen criteria; registry entries for the three libraries (PAP-216).

Out: record-level sync (PAP-31), peer-to-peer transports, any server.

**Spec**

* `vitest bench` file plus `pnpm bench:crdt --out results.json`; results table `bench/results.md` committed from a fresh run on `ubuntu-latest`, Node 22, median of 5 runs.
* Scoring per PAP-209 weights recorded in the ADR.
* The ADR recommends the persistence encoding (`Y.encodeStateAsUpdateV2`) and snapshot cadence for PAP-140.

**Interface contract**

Exposes: `CrdtAdapter { create(); applyText(pos, text); deleteText(pos, len); setShape(id, props); encode(); load(bytes); merge(other) }` for future reruns; `results.json` `{ lib, workload, metric, value, unit, runs }[]`; ADR `decision` block naming the library, encoding (`updateV2`), snapshot cadence (every 500 updates or 60 s) and pinned versions, which PAP-140 copies into its config and PAP-142 into its peer matrix. Consumes: rubric weights from PAP-209 (draft acceptable), ADR template from PAP-130 or `docs/decisions/TEMPLATE.md` from PAP-44.

**Definition of done**

* `pnpm bench:crdt` runs on CI under 10 minutes and writes `results.json` and `results.md`; every workload has numbers for every library.
* ADR merged as `accepted`, linked from the ADR index and the realtime project description; registry updated.
* Linear comment with results table, ADR link and a one-paragraph recommendation; developer changelog entry.

**Test plan**

* Unit: deterministic 1,000-op edit script yields identical final text across all three adapters; encode/load round-trip per adapter; merge of two divergent histories converges.
* Bench: each workload asserts it completes and reports p50/p99; WASM init measured separately; memory read after `global.gc()` with `--expose-gc`.
* CI: bench job runs on a fixed runner class and fails if any cell is missing; results file diffed against the committed one (informational).
* Review: Sentinel reruns `pnpm bench:crdt` locally and compares medians within 20 percent.

**Demo**

Run `pnpm bench:crdt --workload a --runs 1` and watch the table print for three libraries; open `bench/results.md` and the ADR's decision block. Under two minutes.

**Edge cases**

* Await WASM init before timing; report it separately.
* Automerge UTF-16 vs grapheme offsets: adapter normalises or documents.
* Yjs `gc: true` changes encoded size: measure both.
* Loro version churn: pin exact versions in `bench/package.json`.
* Runner noise: median of 5.

**Dependencies**

None hard (Ready). Soft: PAP-209, PAP-130. Blocks PAP-140 (encoding and cadence); informs PAP-142, PAP-132.

**Agent**

Builder: Scout (Library Evaluator) with Nova (CRDT Engineer) on workloads. Reviewer: Nova signs the ADR; Sentinel (Code Reviewer) reviews the harness.

**Size**

S: two-day time box with a fixed output shape.
