---
identifier: "PAP-601"
title: "Collab load harness: k6 `xk6-websockets` connection load, Node pool of Yjs-aware clients, five scenario definitions, token-set correctness checker and the 30-second CI smoke"
project: "realtime"
projectName: "Multiplayer & Realtime"
phase: "P2"
type: "Review"
priority: 2
surfaces: ["Developer"]
milestone: "Scale and offline tested"
state: "Backlog"
parent: "PAP-147"
children: []
blockedBy: ["PAP-140", "PAP-143", "PAP-326", "PAP-328"]
blocks: ["PAP-602"]
key: "r4/realtime/load-harness"
url: "https://linear.app/paperos/issue/PAP-601/collab-load-harness-k6-xk6-websockets-connection-load-node-pool-of-yjs"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:14.981Z"
model: "claude-opus-5"
effort: "high"
estimate: 3
dueDate: "2026-09-30"
cycle: null
---

# PAP-601: Collab load harness: k6 `xk6-websockets` connection load, Node pool of Yjs-aware clients, five scenario definitions, token-set correctness checker and the 30-second CI smoke

**Model / Effort:** Opus 5 (`claude-opus-5`) / high — Review M

**Goal**

First half of PAP-147: the instrument. A reproducible harness that can open thousands of authenticated WebSocket and Electric connections, type real Yjs edits, and prove afterwards that no update was lost, packaged so it runs scaled down on every PR and scaled up on staging in the sibling.

**Scope**

In: `apps/collab-server/load/` with k6 plus `xk6-websockets` for connection and awareness load, a Node 22 worker pool of `@hocuspocus/provider` clients over `ws` for Yjs edits, scenario files (a) one room 500 clients typing, (b) 10,000 rooms x 2 clients, (c) reconnect storm of 2,000 clients, (d) 1,000 awareness-only clients at 20 Hz, (e) Electric 1,000 clients on a 100k-row `records` shape at 50 writes/s; correctness checker asserting every `${clientId}:${seq}` token appears exactly once after quiescence; `pnpm load:collab --scenario --target --duration --clients --out`; JSON summary and HTML report; CI smoke job running (a) at 20 clients for 30 s on the compose stack; generator CPU guard refusing above 70 percent; `loadtest` tenant seeding and truncation.

Out: Staging runs, tuning, baseline, dashboard and nightly job (sibling PAP-602), client performance (PAP-87), API budgets (PAP-242).

**Spec**

* Clients authenticate with a `loadtest`-scoped agent key (PAP-586, soft: dev token until it lands) in tenant `loadtest`; the harness refuses to start when the tenant has rows from a previous run.
* Metrics collected per scenario: propagation p50/p95/max (server-echoed timestamps, no client clocks), connection success rate, dropped updates, RSS and CPU from `/metrics` (PAP-140) and `pg_stat_statements`, generator CPU.
* Scenario (e) uses PAP-326's shape registry against the `records` table with a bounding predicate; writes go through the API with `Idempotency-Key`.
* Report schema `{ scenario, metric, p50, p95, max, unit, runs }[]` compatible with PAP-31's `summary.json` so sync and collab numbers sit in one table.
* Smoke job in Gate 1 for changes under `apps/collab-server` and `packages/sync`: proves auth, edits, correctness and cleanup in under 2 minutes.

**Interface contract**

Provides: Harness CLI, scenario files, correctness checker, report schema, CI smoke workflow step, `loadtest` tenant seed.

Consumes: Collab server metrics and admin route (PAP-140), live record shapes (PAP-326), Electric proxy (PAP-270), agent keys (PAP-586, soft), compose stack (PAP-42), test-mode seed (PAP-240, soft). Consumed by the sibling, PAP-253 nightly staging, PAP-612 (shares client pool).

**Definition of done**

* All five scenarios run end to end against the compose stack at reduced scale with the correctness checker green; CI smoke green on a PR touching the collab server.
* Generator guard proven by an artificial CPU load; dirty `loadtest` tenant refused; report JSON validates against the schema.
* `load/README.md`; changelog; Linear comment with a sample report.

**Test plan**

* Unit: token-set checker (missing, duplicated, all present), report aggregation and percentile math, guard thresholds, scenario config validation.
* E2E: the CI smoke itself; a 2-minute local run of (b) at 200 rooms producing the HTML report.

**Demo**

Run `pnpm load:collab --scenario a --duration 1m --clients 50` against the compose stack, open the HTML report and read propagation p95 and the correctness line. Under two minutes.

**Edge cases**

* Client clock drift: server-echoed timestamps only.
* WebSocket limit on the generator host: `ulimit` check and a clear error before starting.
* Electric shape refuses without a bounding predicate: scenario (e) seeds a bounded dataset.

**Dependencies**

Blocked by PAP-140 and PAP-326 (hard). Soft: PAP-270, PAP-42, PAP-240, PAP-586. Blocks the sibling PAP-602.

**Agent**

Builder: Sentinel (Edge Case Hunter) writes the harness with Nova on client semantics. Reviewer: Sentinel (Code Reviewer; Nova signs off scenario realism).

**Size**

M: one session.

*Round 4 critique fix (2026-09-18):* resolved 3 round-4 file keys in this description to Linear identifiers: `r4/identity/agent-keys` = PAP-586, `r4/realtime/load-runs-tuning` = PAP-602, `r4/realtime/test-kit` = PAP-612.
