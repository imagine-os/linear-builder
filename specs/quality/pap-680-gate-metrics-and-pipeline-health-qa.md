---
identifier: "PAP-680"
title: "Gate metrics and pipeline health: `qa_gate_runs` table, duration and pass-rate trends, reviewer cost per PR, bounce rate and queue time, with a Grafana board and a digest section"
project: "quality"
projectName: "Quality Pipeline"
phase: "P1"
type: "Build"
priority: 3
surfaces: ["Developer"]
milestone: "Edge-case hunting and release trains"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-40", "PAP-239"]
blocks: ["PAP-89"]
key: "r4/quality/gate-metrics-and-pipeline-health"
url: "https://linear.app/paperos/issue/PAP-680/gate-metrics-and-pipeline-health-qa-gate-runs-table-duration-and-pass"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:26.641Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 2
dueDate: "2026-09-30"
cycle: null
---

# PAP-680: Gate metrics and pipeline health: `qa_gate_runs` table, duration and pass-rate trends, reviewer cost per PR, bounce rate and queue time, with a Grafana board and a digest section

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Build S

**Goal**

Every gate writes an artefact and nobody aggregates them: Gate 1 wall time, Gate 2 cost and bounce rate, Gate 3 diff rate, Gate 4 finding yield and runner queue time are the numbers that tell Justin whether the 30 percent QA budget is buying anything. This issue collects every `GateReport` into one table, renders trends and feeds a section of the release digest.

**Scope**

* In: collector step in every gate workflow posting `GateReport` summaries to `POST /api/qa/gate-runs` (or committing `ops/quality/gate-runs.ndjson` on `main` until the API exists), table `qa_gate_runs`, Grafana dashboard `Quality pipeline` (`ops/observability/dashboards/quality.json`), `pnpm qa:metrics --since 7d`, `pipelineHealth` summary for PAP-89 section 3, `docs/quality/metrics.md`.
* Out: fixing slow gates, runner provisioning (PAP-50), the flake store (PAP-90 owns `qa_flakes`).

**Spec**

* `qa_gate_runs(id, repo, pr, sha, gate, status, started_at, finished_at, duration_ms, queue_ms, findings_s0, findings_s1, cost_usd, shard, runner, artifact_url)` written from every `reports/*.json` via a shared composite action `ops/ci/actions/report-gate` that reads the PAP-239 shape.
* Derived metrics: p50 and p95 duration per gate, pass rate per gate per day, reviewer cost per PR (from `review-cost.json`), bounce rate (from the fix loop metric), time from PR open to all gates green, runner queue time, findings per PR by severity, flake rate (PAP-90 join).
* Dashboard panels for each metric with 14-day trend; budget lines from `ops/quality/budgets.yaml` (Gate 1 3 min, Gate 3 8 min, Gate 2 $6 per PR).
* `pipelineHealth = { gates: [{ name, p95Ms, passRate, budgetOk }], reviewCostPerPr, bounceRate, medianTimeToGreen }` rendered by PAP-89.
* Alert: a gate over budget p95 for two consecutive days opens one Linear issue for Sentinel (dedupe by gate).

**Interface contract**

* Provides: table `qa_gate_runs`, action `report-gate`, `pnpm qa:metrics`, dashboard JSON, `pipelineHealth` for PAP-89.
* Consumes: PAP-239 artefacts, PAP-40 Grafana and Postgres, PAP-35 endpoint (soft, NDJSON fallback), PAP-90 flake table, the fix loop metric.

**Definition of done**

* Every gate workflow reports a row; 7 days of data visible on the dashboard (screenshot at 1280 px light and dark).
* `pnpm qa:metrics --since 7d` prints the table; `pipelineHealth` validates and renders in a digest rehearsal.
* Seeded slow gate (sleep in a job) trips the budget alert and opens the issue (screenshot).
* Docs; changelog under "Quality"; Linear comment with the dashboard link.

**Test plan**

* Unit: row derivation from each artefact kind, percentile math, budget comparison, alert dedupe.
* E2E: composite action in a sandbox PR writes rows for all gates.

**Demo**

Open the `Quality pipeline` dashboard: Gate 1 p95 under 3 minutes, Gate 2 cost per PR, bounce rate for the week; then read the same numbers in the digest rehearsal section. Under one minute.

**Edge cases**

* Gate errored (no artefact): row with `status: error` from the workflow conclusion, never missing.
* Re-runs of the same SHA: rows keep both; metrics use the latest per gate per SHA.
* Forgejo-hosted runs: `artifact_url` falls back to the run link.
* Cost missing for a reviewer run: `cost_usd` null, flagged in the digest as `n/a`.

**Dependencies**

Hard: PAP-239, PAP-40. Soft: PAP-35, PAP-90, PAP-89, PAP-679.

**Agent**

Builder: Sentinel (Edge Case Hunter) with Forge (Ops Runner) for the dashboard. Reviewer: Sentinel (Code Reviewer).

**Size**

S: half a session.

*Round 4 critique fix (2026-09-18):* resolved 1 round-4 file key in this description to Linear identifiers: `r4/quality/review-fix-loop` = PAP-679.
