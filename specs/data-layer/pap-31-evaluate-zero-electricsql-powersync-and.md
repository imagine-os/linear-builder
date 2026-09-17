---
identifier: "PAP-31"
title: "Evaluate Zero, ElectricSQL, PowerSync and Replicache for local-first sync and write an ADR"
project: "data-layer"
projectName: "Data Layer & Database"
phase: "P0"
type: "Research"
priority: 1
surfaces: ["Developer"]
milestone: "Postgres + Drizzle baseline"
state: "Ready for Claude"
parent: null
children: []
blockedBy: []
blocks: ["PAP-36", "PAP-271"]
key: "data-layer/sync-research"
url: "https://linear.app/paperos/issue/PAP-31/evaluate-zero-electricsql-powersync-and-replicache-for-local-first"
source: "Linear snapshot 2026-09-17T13:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T04:05:38.096Z"
model: "claude-opus-5"
effort: "medium"
---

# PAP-31: Evaluate Zero, ElectricSQL, PowerSync and Replicache for local-first sync and write an ADR

**Goal**

Confirm or overturn ElectricSQL plus PGlite for local-first sync by benchmarking Zero, PowerSync and Replicache on PaperOS's real core entities, and record the decision as an ADR that PAP-36 implements without further debate. Time-boxed to 1.5 agent-days.

**Scope**

In:

* Rubric (weights agreed with Atlas): Postgres-native change capture, tenant-scoped partial sync, offline writes and conflict model, RLS story, bundle size, browser and Tauri WebView support, self-host and licence (PAP-212), maturity, TypeScript ergonomics, cost of exit.
* Spike `spikes/sync-bench/` with a 10k-row `tasks` table under `tenant_id`: initial sync of a 2k-row shape, incremental latency p50 and p95, replay of 200 offline writes, memory in Chrome and WebView, cold start on a mid-range Android emulator.
* Coexistence notes with Yjs (PAP-140) and RLS (PAP-34).
* ADR `docs/adr/0004-local-first-sync.md`.

Out: production integration (PAP-36), CRDT choice (PAP-139).

**Spec**

* Each engine gets at most 3 hours; unknowns become rubric penalties.
* Versions: ElectricSQL 1.x HTTP shapes plus PGlite 0.3; Zero current with zero-cache; PowerSync self-hosted plus web SDK; Replicache with an oRPC push/pull server; baseline TanStack Query with a hand-rolled outbox.
* Permission path scored: per-user role respecting RLS, proxy, or own rules language.
* Hard criteria: self-hosts in Docker on the VPS, acceptable licence, runs in Tauri WebView.
* Results JSON in `spikes/sync-bench/results/*.json`, rendered to a Markdown table by script; three runs, median reported.
* Migration-cost estimate from winner to runner-up in hours.

**Interface contract**

Provides:

* ADR 0004 with a `decision` block PAP-36 copies verbatim: engine, versions, persistence per target, permission path (`proxy` expected), known limits.
* `spikes/sync-bench/results/summary.json` schema `{ engine, initialSyncMs, incrementalP50Ms, incrementalP95Ms, replay200Ms, heapMb, coldStartMs, score }` reused by PAP-147 load tests as a baseline.
* Registry entry draft for PAP-216.

Consumes: rubric format (PAP-210), licence tiers (PAP-212), RLS context contract (PAP-34, read from its spec).

**Definition of done**

* Spike code merged under `spikes/` (excluded from `turbo build`); results and table committed.
* ADR approved by Atlas and Nova on the PR.
* Browser harness recordings at 375 and 1280.
* Registry entry drafted; PAP-36 description updated with the chosen libraries and versions; CHANGELOG; Linear comment.

**Test plan**

* Bench: Vitest bench for server-side measures; Playwright for browser heap and timing; Android emulator cold start via `adb` script; each three runs, median kept.
* Correctness: after replay of 200 offline writes, row count and checksums match the server for every engine.
* Permission: cross-tenant shape request must fail for every engine; result recorded per engine.
* Review: every score in the table cites the results file or a source URL.

**Demo**

Reviewer opens the ADR, reads the decision block and the scores table, then runs `pnpm --filter sync-bench bench:electric` to reproduce one engine's numbers locally in about a minute.

**Edge cases**

* Engine needs superuser or disables RLS: hard fail.
* Cloud easy, self-host undocumented: score self-host only.
* BSL or ELv2 terms: recorded with a re-open trigger.
* PGlite WASM memory on Android WebView tested specifically.
* Shapes over 10k rows: note pagination strategy.

**Dependencies**

None; ready now. Blocks PAP-36; informs PAP-143, PAP-148, PAP-214.

**Agent**

Researched by Scout (Library Evaluator) paired with Forge. Reviewed by Atlas and Nova.

**Size**

M: 1.5 agent-days, time-boxed.
