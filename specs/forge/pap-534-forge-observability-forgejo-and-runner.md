---
identifier: "PAP-534"
title: "Forge observability: Forgejo and runner metrics in Grafana, mirror lag, runner queue depth, disk, backup age and hook health alerts"
project: "forge"
projectName: "Version Control & Forge Independence"
phase: "P1"
type: "Infra"
priority: 2
surfaces: ["Developer"]
milestone: "Disaster recovery proven"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-40", "PAP-273"]
blocks: []
key: "r4/forge/forge-observability"
url: "https://linear.app/paperos/issue/PAP-534/forge-observability-forgejo-and-runner-metrics-in-grafana-mirror-lag"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:03.433Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 2
dueDate: "2026-09-30"
cycle: null
---

# PAP-534: Forge observability: Forgejo and runner metrics in Grafana, mirror lag, runner queue depth, disk, backup age and hook health alerts

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Infra S

**Goal**

PAP-40 builds tracing and dashboards for the API and sync; PAP-275 leaves a "metrics scrape hint"; PAP-47 alerts on divergence by issue. Nothing shows whether the forge is healthy: runner queue depth when twenty sessions push, disk on the Forgejo host, hours since the last backup, mirror lag. Forge independence needs the same observability as the app.

**Scope**

In:

* Forgejo `[metrics] ENABLED=true` with a bearer token; Prometheus scrape jobs for Forgejo, the runners (`forgejo-runner` exporter or log-derived queue depth), node exporter on both hosts; `ops/observability/forge-dashboard.json` provisioned into the PAP-40 Grafana.
* Derived metrics: `mirror_lag_seconds` from `mirror-status.json` (PAP-520), `backup_age_hours` from the restic manifest (PAP-274), `prereceive_hook_failures_total` (PAP-530), `merge_queue_wait_minutes` (PAP-527).
* Alerts (Grafana rules to the PAP-97 orchestrator webhook, interim Linear comment): disk over 80 percent, backup older than 30 h, mirror lag over 15 minutes, queue depth over 8 for 30 minutes, hook failing closed.
* Runbook links on each alert; `docs/runbooks/forgejo.md` monitoring section completed (PAP-275 placeholder).

Out: application tracing (PAP-40), security telemetry (PAP-356), cost reporting (PAP-371).

**Spec**

* Scrape every 30 s; dashboards load in under 2 s; retention 30 days (PAP-40 Prometheus).
* Alert thresholds in `ops/observability/forge-alerts.yml` so a change is a PR.
* No alert flaps: 5-minute `for` on every rule.

**Interface contract**

Provides: dashboard, alert rules, derived metric exporters; consumed by PAP-53 (drill health), PAP-88 (release gate reads forge health), PAP-306, PAP-275 runbook.

Consumes: Grafana and Prometheus (PAP-40), Forgejo config (PAP-273), mirror status, backup manifest (PAP-274), runner compose (PAP-50).

**Definition of done**

* Dashboard shows live panels for all metrics (screenshot at 1280); a simulated backup gap fires the alert into the webhook (log).
* Rules file merged; runbook section; CHANGELOG; Linear comment.

**Test plan**

* Unit: derived exporters over fixture inputs (lag, age, queue depth).
* E2E: stop the backup sidecar for a test window and observe the alert; restore.

**Demo**

Reviewer opens the Forge dashboard, sees runner queue depth spike as they push three PRs, then the mirror lag panel return to zero. Under a minute.

**Edge cases**

* Metrics token leaked: rotate via `app.ini` reload; documented.
* Second host down: node exporter target down alert distinct from queue depth.
* Prometheus down: Forgejo unaffected; alert on the PAP-40 side.

**Dependencies**

Hard: PAP-40, PAP-273. Soft: PAP-274, PAP-50, PAP-520, PAP-530, PAP-527.

**Agent**

Builder: Forge (Ops Runner). Reviewer: Sentinel (Code Reviewer).

**Size**

S: half a session.

*Round 4 critique fix (2026-09-18):* resolved 3 round-4 file keys in this description to Linear identifiers: `r4/forge/merge-automation` = PAP-527, `r4/forge/mirror-drift-monitor` = PAP-520, `r4/forge/push-protection` = PAP-530.
