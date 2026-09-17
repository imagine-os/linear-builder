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
source: "plan/specs/bucket-5.json (round-1 canonical spec JSON)"
---

# PAP-139: Benchmark Yjs vs Automerge vs Loro for document CRDT and write an ADR

**Goal**

Confirm with measurements that Yjs is the right document CRDT for PaperOS before the Hocuspocus server, collaborative editor and canvas are built on it. The output is an ADR in the decision log plus a reproducible benchmark harness, so the choice can be reopened later with the same numbers if Loro or Automerge overtake Yjs.

**Scope**

In:
- Benchmark harness in `packages/collab/bench/` comparing `yjs` 13.6.x, `@automerge/automerge` 2.x (with `automerge-repo`) and `loro-crdt` 1.x.
- Workloads: (a) rich-text doc of 200k characters with 50k random edits, (b) canvas map of 10k shapes with 20k property updates, (c) 50 simulated peers editing concurrently for 60s with 200 ms artificial latency.
- Metrics: encoded document size, load time from snapshot, memory after load, per-op apply time (p50/p99), merge time of two divergent 10k-op histories, WASM bundle size gzipped, TypeScript typing quality, ecosystem (editor bindings for Tiptap and tldraw, server persistence options, presence/awareness support, licence).
- ADR `docs/decisions/00xx-document-crdt.md` following the template from `collab/decision-log` (status, context, options, decision, consequences, reopen criteria).
- Registry entries for all three libraries in `libraries/registry` (adopted / rejected with reasons).

Out: record-level sync (decided by `data-layer/sync-research`), peer-to-peer transports, building any server.

**Spec**

- Harness is a Vitest bench file (`vitest bench`) plus a Node script `pnpm bench:crdt --out results.json` that runs all three implementations behind one interface `CrdtAdapter { create(); applyText(pos, text); deleteText(pos, len); setShape(id, props); encode(); load(bytes); merge(other) }`.
- Results table generated as Markdown (`bench/results.md`) and committed; numbers must come from a fresh run on the CI runner class (`ubuntu-latest`, Node 22) so they are comparable with later reruns.
- Scoring uses the rubric from `libraries/eval-rubric` (licence, maintenance, bundle size, a11y n/a, TS quality, agent-friendliness) with weights recorded in the ADR.
- The ADR must state explicit reopen criteria, for example "Loro ships stable Tiptap and tldraw bindings and beats Yjs on p99 apply time by 2x".
- Recommend the Yjs persistence encoding (`Y.encodeStateAsUpdateV2`) and the snapshot cadence the server should use; this feeds `realtime/yjs-server`.

**Definition of done**

- `pnpm bench:crdt` runs on CI in under 10 minutes and writes `results.json` and `results.md`.
- All three workloads produce numbers for all three libraries (no "n/a" without an explanation).
- ADR merged with status `accepted`, linked from the decision log index and from the `realtime` project description.
- Registry updated with three entries and owners.
- Unit test asserting the adapter interface behaves identically (same final text) across implementations for a deterministic edit script.
- Linear comment on the issue with the results table, the ADR link and a one-paragraph recommendation.
- Changelog entry under `docs/changelog/` (developer audience).

**Edge cases**

- WASM initialisation must be awaited before timing; exclude it from per-op numbers but report it separately.
- Automerge text uses different offset semantics (UTF-16 vs grapheme); the adapter must normalise or document the difference.
- Garbage collection differences (Yjs `gc: true`) change encoded size; benchmark with GC on and off.
- Memory measurements need `--expose-gc` and a forced GC before reading `process.memoryUsage()`.
- Loro version churn: pin exact versions in `bench/package.json` and record them in the ADR.
- Runner noise: run each workload 5 times and report the median.

**Dependencies**

- `libraries/eval-rubric` for the scoring rubric (use the draft if not yet merged).
- `collab/decision-log` for the ADR template; if unavailable, use `docs/decisions/TEMPLATE.md` from `forge/vcs-decision-adr`.
- Feeds `realtime/yjs-server`, `realtime/collab-text`, `collab/canvas-view`.

**Agent**

Builder: Scout (Library Evaluator sub-agent) with Nova (CRDT Engineer) pairing on the workloads. Reviewer: Nova signs the ADR; Sentinel (Code Reviewer) reviews the harness.

**Size**

S: a two-day, time-boxed research task with a fixed output shape.
