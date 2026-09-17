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
blockedBy: ["PAP-140", "PAP-143"]
blocks: []
key: "realtime/load-test"
url: "https://linear.app/paperos/issue/PAP-147/load-test-500-concurrent-users-per-room-and-10k-rooms-tune-persistence"
source: "plan/specs/bucket-5.json (round-1 canonical spec JSON)"
---

# PAP-147: Load test 500 concurrent users per room and 10k rooms; tune persistence and scaling

**Goal**

Find the real limits of the collab server and record sync before a tenant does: 500 concurrent users in one room and 10,000 active rooms across the cluster, with p95 latency and memory measured. Tune persistence, compaction and scaling knobs until the targets pass, and turn the harness into a nightly CI job so regressions are caught.

**Scope**

In:
- Load harness in `apps/collab-server/load/` using k6 (0.5x, `xk6-websockets` extension) for WebSocket rooms and a Node worker pool for Yjs-aware clients (k6 cannot run Yjs; workers use `@hocuspocus/provider` with `ws`).
- Scenarios: (a) one room, 500 clients, each typing 2 chars/s for 10 minutes; (b) 10,000 rooms, 2 clients each, one edit per 10 s; (c) reconnect storm: 2,000 clients reconnect within 5 s after a simulated server restart; (d) awareness-only: 1,000 clients moving cursors at 20 Hz.
- Electric shape load: 1,000 clients subscribed to a 100k-row `records` shape receiving 50 writes/s.
- Targets: p95 update propagation under 250 ms (scenario a), under 500 ms (b); server RSS under 4 GB for (b); no dropped updates; reconnect storm fully recovered under 60 s; zero data loss verified by comparing final `Y.Text` across all clients.
- Tuning outputs: Hocuspocus `debounce`/`maxDebounce`, compaction thresholds, Postgres pool size, Redis fan-out on/off, Node `--max-old-space-size`, Caddy WebSocket idle timeouts; document each change as a commit with before/after numbers.
- Grafana dashboard `ops/grafana/collab-load.json` and a nightly GitHub/Forgejo Actions job on a staging-sized VPS posting results to Linear (`pm-linear/webhooks` comment format).

Out: multi-region, CDN, client-side performance (covered by `quality/perf-budgets`).

**Spec**

- Harness entry `pnpm load:collab --scenario a --target wss://collab-staging.<domain> --duration 10m --out results/`; outputs JSON summary plus an HTML report (k6 `handleSummary`).
- Each client authenticates with a load-test agent key minted via `identity/agent-principals` (`scope: loadtest`, tenant `loadtest`), so RLS and auth are exercised too; the tenant is truncated after each run.
- Correctness check: workers append `${clientId}:${seq}` tokens; after quiescence every client's text must contain all tokens exactly once.
- Metrics scraped from `/metrics` (`realtime/yjs-server`) and Postgres (`pg_stat_statements`), stored under `results/<date>/` and compared to `load/baseline.json`; a regression over 20% fails the nightly job.
- Report template `load/REPORT.md`: target, result, pass/fail, knob changes, recommended max per instance, scaling formula (rooms per GB, connections per vCPU).

**Definition of done**

- All four Yjs scenarios and the Electric scenario run against staging with results committed under `apps/collab-server/load/results/`.
- Targets met or, where not met, an ADR recording the accepted limit and a follow-up issue.
- Tuning commits each carry before/after numbers in the message.
- Nightly job runs green for three consecutive nights and posts a summary comment to this issue.
- Grafana dashboard screenshot attached to the PR.
- Docs `docs/platform/realtime/capacity.md` with the scaling formula and runbook for adding instances.
- Changelog entry (developer) and Linear comment with the report link.

**Edge cases**

- Load generator saturates first (CPU-bound workers): distribute across two runner machines and verify generator p95 separately.
- Postgres `yjs_updates` table grows to millions of rows in scenario (b): compaction must keep it under 1M; test vacuum behaviour.
- Redis fan-out adds latency for single-instance deployments; document the break-even point.
- Client clocks drift: measure propagation with server-echoed timestamps, not client clocks.
- Caddy default idle timeout closes quiet WebSockets: set `read_timeout` and verify scenario (b) survives 10 minutes idle.
- A run left the `loadtest` tenant dirty: harness refuses to start until cleanup completes.

**Dependencies**

- `realtime/yjs-server` (target, metrics), `data-layer/observability` (Grafana), `identity/agent-principals` (keys), `realtime/record-sync` (Electric scenario), `pm-linear/webhooks` (result comments).

**Agent**

Builder: Sentinel (Edge Case Hunter sub-agent) writes the harness; Forge (Ops Runner) applies tuning. Reviewer: Nova signs off on limits and the ADR.

**Size**

M: harness is straightforward; tuning iterations are the variable part.
