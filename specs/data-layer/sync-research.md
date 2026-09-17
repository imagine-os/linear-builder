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
blocks: ["PAP-271", "PAP-36"]
key: "data-layer/sync-research"
url: "https://linear.app/paperos/issue/PAP-31/evaluate-zero-electricsql-powersync-and-replicache-for-local-first"
source: "plan/specs/bucket-0.json (round-1 canonical spec JSON)"
---

# PAP-31: Evaluate Zero, ElectricSQL, PowerSync and Replicache for local-first sync and write an ADR

**Goal**

Confirm or overturn the plan's default of ElectricSQL + PGlite for local-first sync by benchmarking it against Zero, PowerSync and Replicache on PaperOS's real core entities, and record the decision as an ADR that `data-layer/local-first-sync` implements without further debate.

**Scope**

In:
- Rubric (weights agreed with Atlas): Postgres-native change capture, partial sync/shapes by tenant, offline writes and conflict model, RLS/permission story, bundle size, browser and Tauri WebView support, self-hostability and licence (per `libraries/license-policy`), maturity/maintenance, TypeScript ergonomics, cost of exit.
- Spike repo `spikes/sync-bench/` with a 10k-row `tasks` table under `tenant_id`, measuring: initial sync time for a 2k-row shape, incremental update latency (p50/p95), offline queue replay of 200 writes, memory footprint in Chrome and WebView, cold-start time on a mid-range Android emulator.
- Written evaluation of how each engine coexists with Yjs (documents) and with Postgres RLS.
- ADR `docs/adr/0004-local-first-sync.md`.

Out: production integration (that is `data-layer/local-first-sync`), CRDT text/canvas choice (`realtime/realtime-research`).

**Spec**

- Time-box: 1.5 agent-days total; each engine gets a spike no longer than 3 hours; unknowns become explicit rubric penalties rather than more research.
- Benchmark harness: Vitest bench plus Playwright for browser measurements; results written as JSON to `spikes/sync-bench/results/*.json` and rendered into a Markdown table by a script.
- Engines and versions to test: ElectricSQL 1.x (HTTP shapes) + PGlite 0.3; Zero (Rocicorp) current release with zero-cache; PowerSync self-hosted service + web SDK; Replicache with a custom push/pull server on oRPC.
- Evaluate permission enforcement path: does the engine respect RLS via a per-user Postgres role, require a proxy, or need its own rules language? Score accordingly, referencing `data-layer/rls-tenancy`.
- Include a "do nothing" baseline: TanStack Query with optimistic updates and a hand-rolled outbox.
- Decision criteria: engine must self-host in Docker on the existing VPS, be MIT/Apache/BSL-with-acceptable-terms, and support Tauri WebView.
- Deliver a migration-cost estimate from the winner to the runner-up (hours), to keep the exit door documented.

**Definition of done**

- Spike code merged under `spikes/` (excluded from `turbo build`), results JSON and generated table committed.
- ADR with decision, scores, rejected options and re-open criteria approved by Atlas and Nova (comment on PR).
- Benchmark screenshots/recordings of the browser harness at 375 and 1280.
- `libraries/registry` entry drafted for the chosen engine (or an issue comment for Scout to add).
- CHANGELOG entry noting the decision; Linear comment linking the ADR and results table.
- `data-layer/local-first-sync` description updated with the exact libraries and versions chosen.

**Edge cases**

- Engine requires Postgres superuser or disables RLS: hard fail on rubric.
- Vendor cloud is easy but self-host is undocumented: score self-host only.
- Licence change risk (BSL/ELv2): record and require ADR re-open if terms change.
- Benchmark noise on shared CI runners: run three times, report median.
- PGlite in Tauri WebView on Android (WASM memory limits): test specifically.
- Shapes over 10k rows: note limits and pagination strategy.

**Dependencies**

None; ready now. Blocks `data-layer/local-first-sync`; informs `realtime/record-sync`, `realtime/offline-queue`, `libraries/data-landscape`.

**Agent**

Researched by Scout (Library Evaluator) paired with Forge (Schema Wright) for the Postgres side. Reviewed by Atlas (decision) and Nova (consumer of the choice).

**Size**

M: four spikes with measurements is real work, but strictly time-boxed.
