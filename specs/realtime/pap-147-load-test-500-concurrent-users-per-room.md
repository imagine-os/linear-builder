---
identifier: "PAP-147"
title: "Load test 500 concurrent users per room and 10k rooms; tune persistence and scaling"
project: "realtime"
projectName: "Multiplayer & Realtime"
phase: "P2"
type: "Review"
priority: 2
surfaces: ["Developer"]
milestone: "Scale and offline tested"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-140", "PAP-143", "PAP-328"]
blocks: []
key: "realtime/load-test"
url: "https://linear.app/paperos/issue/PAP-147/load-test-500-concurrent-users-per-room-and-10k-rooms-tune-persistence"
source: "Linear snapshot 2026-09-17T15:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T13:41:37.456Z"
model: "claude-opus-5"
effort: "high"
---

# PAP-147: Load test 500 concurrent users per room and 10k rooms; tune persistence and scaling

**Model / Effort:** Opus 5 (`claude-opus-5`) / high — Review

**Goal**

Find the real limits of the collab server and record sync before a tenant does: 500 users in one room and 10,000 active rooms, with p95 latency and memory measured. Tune persistence, compaction and scaling until targets pass, and run the harness nightly so regressions are caught.

**Scope**

In:

* Harness `apps/collab-server/load/`: k6 with `xk6-websockets` for connection load plus a Node worker pool of Yjs-aware clients (`@hocuspocus/provider` with `ws`).
* Scenarios: (a) one room, 500 clients typing 2 chars/s for 10 minutes; (b) 10,000 rooms × 2 clients, one edit per 10 s; (c) reconnect storm of 2,000 clients within 5 s after a restart; (d) 1,000 awareness-only clients at 20 Hz; (e) Electric: 1,000 clients on a 100k-row `records` shape at 50 writes/s.
* Targets: p95 propagation under 250 ms (a) and 500 ms (b); RSS under 4 GB (b); zero dropped updates; storm recovered under 60 s.
* Tuning knobs documented per commit with before and after numbers; Grafana dashboard `ops/grafana/collab-load.json`; nightly job on a staging-sized VPS posting results to Linear (PAP-97 comment format).

Out: multi-region, CDN, client performance (PAP-87).

**Spec**

* `pnpm load:collab --scenario a --target wss://collab-staging.<domain> --duration 10m --out results/`; JSON summary plus HTML report.
* Clients authenticate with a `loadtest`-scoped agent key (PAP-60) in tenant `loadtest`, truncated after each run.
* Correctness: each client appends `${clientId}:${seq}`; after quiescence every client's text contains every token once.
* Metrics from `/metrics` (PAP-140) and `pg_stat_statements`; regression over 20 percent versus `load/baseline.json` fails the nightly job.
* A second generator host is required for (a) and (c); the harness refuses to run a scenario whose generator CPU exceeds 70 percent.

**Interface contract**

Exposes: `load/baseline.json` `{ scenario, metric, p50, p95, max, unit }[]`, `load/REPORT.md` template with the scaling formula (rooms per GB, connections per vCPU), `docs/platform/realtime/capacity.md`, Grafana dashboard JSON, nightly workflow `.forgejo/workflows/collab-load.yml` posting a comment `Load <date>: <pass|fail> <link>`. Consumes: server metrics and admin route (PAP-140), Grafana and Prometheus (PAP-40), agent keys (PAP-60), Electric shapes (PAP-143, PAP-270), Linear comment API (PAP-97), a second runner or VPS from PAP-50 for the generator.

**Definition of done**

* All five scenarios run against staging; results committed under `load/results/<date>/`.
* Targets met or an ADR (PAP-130) records the accepted limit with a follow-up issue.
* Nightly job green three consecutive nights with a summary comment here; dashboard screenshot on the PR; docs; changelog; Linear comment with the report link.

**Test plan**

* Unit: token-set correctness checker on synthetic client texts (missing, duplicated, all present); baseline comparison flags a 25 percent regression and passes 15 percent.
* Smoke in CI: scenario (a) scaled to 20 clients for 30 s against the compose stack proves the harness, auth and cleanup work on every PR.
* Full runs: each scenario executed against staging with the generator on a separate host; generator p95 reported alongside server p95.
* Ops: Caddy idle timeout survives 10 minutes of quiet in (b); `yjs_updates` stays under 1M rows during (b); vacuum observed.

**Demo**

Run `pnpm load:collab --scenario a --duration 1m --clients 50` against staging, open the Grafana collab-load dashboard and watch connections and propagation p95, then open the generated HTML report. Under two minutes.

**Edge cases**

* Generator saturates first: split across two hosts, report generator p95.
* Redis fan-out adds latency single-instance: document the break-even.
* Client clock drift: server-echoed timestamps.
* Dirty `loadtest` tenant: refuse to start until cleanup.

**Dependencies**

PAP-140, PAP-143 (hard, encoded). Soft: PAP-40, PAP-60, PAP-97, PAP-50 (second generator host).

**Agent**

Builder: Sentinel (Edge Case Hunter) writes the harness; Forge (Ops Runner) applies tuning. Reviewer: Nova signs off on limits and the ADR.

**Size**

M: harness is straightforward; tuning iterations vary.
