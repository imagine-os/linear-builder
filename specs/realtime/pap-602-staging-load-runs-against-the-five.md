---
identifier: "PAP-602"
title: "Staging load runs against the five scenarios, tuning knobs with before and after numbers, `load/baseline.json`, the Grafana collab-load dashboard and the nightly regression job"
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
blockedBy: ["PAP-40", "PAP-601"]
blocks: []
key: "r4/realtime/load-runs-tuning"
url: "https://linear.app/paperos/issue/PAP-602/staging-load-runs-against-the-five-scenarios-tuning-knobs-with-before"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:15.075Z"
model: "claude-opus-5"
effort: "high"
estimate: 3
dueDate: "2026-09-30"
cycle: null
---

# PAP-602: Staging load runs against the five scenarios, tuning knobs with before and after numbers, `load/baseline.json`, the Grafana collab-load dashboard and the nightly regression job

**Model / Effort:** Opus 5 (`claude-opus-5`) / high — Review M

**Goal**

Second half of PAP-147: the numbers. Run the harness against staging with the generator on a second host, tune Hocuspocus persistence, compaction and Caddy until the targets pass or an ADR records the accepted limit, commit the baseline, and run nightly so a regression over 20 percent fails before a tenant notices.

**Scope**

In: Runs of scenarios (a) to (e) against `wss://collab-staging.<domain>` with the generator on the PAP-50 second runner host (fallback: 50 percent scale from the VPS with results marked partial), tuning log per commit (`debounce`, `maxDebounce`, compaction threshold, `extension-throttle`, Caddy idle timeout, Postgres `work_mem` for `yjs_updates`, `extension-redis` break-even), `load/baseline.json`, `load/REPORT.md` with the scaling formula (rooms per GB, connections per vCPU), Grafana dashboard `ops/grafana/collab-load.json`, nightly workflow `.forgejo/workflows/collab-load.yml` posting `Load <date>: <pass|fail> <link>` through PAP-97, ADR for any accepted limit (PAP-130), `docs/platform/realtime/capacity.md`.

Out: The harness (sibling), multi-region, CDN, Electric service scaling beyond one instance (documented as the next step).

**Spec**

* Targets: p95 propagation under 250 ms (a) and 500 ms (b); RSS under 4 GB during (b); zero dropped updates; storm (c) recovered under 60 s; (d) awareness CPU under 50 percent; (e) shape lag p95 under 500 ms.
* Each tuning change is one commit with the before and after table; the final configuration lands in `ops/compose/collab-server.yml` and PAP-140's runbook.
* Regression rule: any metric over 20 percent worse than baseline fails the nightly job and opens a Linear comment on this issue; baseline updates require a PR.
* Ops checks during (b): Caddy idle timeout survives 10 minutes of quiet; `yjs_updates` stays under 1M rows; vacuum observed; replication slot lag flat.
* Redis fan-out evaluated single-instance: documented break-even connection count for enabling `extension-redis` and a second replica.

**Interface contract**

Provides: `load/baseline.json`, `load/REPORT.md`, dashboard JSON, nightly workflow and comment format, capacity doc, tuned server config, ADR if needed.

Consumes: Harness (sibling), Grafana and Prometheus (PAP-40), second generator host (PAP-50, soft), Linear comment helper (PAP-97, soft), ADR log (PAP-130, soft), staging deploy of the collab server (PAP-140, PAP-26). Consumed by PAP-88 release digest, PAP-242, PAP-253.

**Definition of done**

* Five scenarios run against staging with results committed under `load/results/<date>/`; targets met or an ADR records the accepted limit with a follow-up issue.
* Nightly job green three consecutive nights with the summary comment; dashboard screenshot at 1280 and 1920 on the PR; baseline committed.
* Capacity doc with the scaling formula; changelog; Linear comment with the report link.

**Test plan**

* Unit: baseline comparison flags a 25 percent regression and passes 15 percent; report renderer; scaling formula on fixture numbers.
* E2E: the staging runs themselves; the nightly workflow executed once by hand with a forced regression to prove the failure path.

**Demo**

Open the latest `load/results/<date>/report.html` and the Grafana collab-load dashboard for that window, then read the capacity doc's formula and plug in 200 tenants. Under two minutes.

**Edge cases**

* Generator saturates first: split across two hosts, report generator p95 alongside server p95.
* Second host unavailable before 10-01: (a) and (c) run at 50 percent and are marked partial in the baseline; the full run is a follow-up.
* Staging shared with other tests at night: the workflow takes a lock (PAP-253) and refuses to overlap.

**Dependencies**

Blocked by PAP-601 and PAP-40 (hard). Soft: PAP-50, PAP-97, PAP-130, PAP-26, PAP-253. Consumed by PAP-88, PAP-242.

**Agent**

Builder: Forge (Ops Runner) applies tuning; Sentinel (Edge Case Hunter) runs scenarios. Reviewer: Sentinel (Edge Case Hunter; Nova signs off on limits and the ADR).

**Size**

M: one session.

*Round 4 critique fix (2026-09-18):* resolved 1 round-4 file key in this description to Linear identifiers: `r4/realtime/load-harness` = PAP-601.
