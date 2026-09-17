---
identifier: "PAP-253"
title: "Nightly staging workflow with full gate run"
project: "quality"
projectName: "Quality Pipeline"
phase: "P1"
type: "Build"
priority: 1
surfaces: ["Agent", "Developer"]
milestone: "Edge-case hunting and release trains"
state: "Backlog"
parent: "PAP-88"
children: []
blockedBy: ["PAP-26", "PAP-81", "PAP-82", "PAP-242", "PAP-252"]
blocks: ["PAP-254"]
key: "quality/release-train/nightly-staging"
url: "https://linear.app/paperos/issue/PAP-253/nightly-staging-workflow-with-full-gate-run"
source: "Linear snapshot 2026-09-17T13:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T06:22:43.005Z"
model: "claude-sonnet-5"
effort: "high"
---

# PAP-253: Nightly staging workflow with full gate run

**Goal**

Deploy `main` to staging every night through Coolify, run the full suites (e2e `@full`, visual matrix, edge-case library, perf), and write a nightly report so the RC on Monday starts from known-good evidence.

**Scope**

* In: `.github/workflows/staging-nightly.yml` at 02:00 UTC and `workflow_dispatch`, Coolify deploy step with status polling and smoke (`/healthz`, `/__version` equals SHA), pre-deploy backup call and snapshot id capture, migrations via `drizzle-kit migrate`, suite invocations, `reports/nightly-<date>.json` aggregate in the contracts shape, failure notification comment on a pinned "Nightly" Linear issue.
* Out: RC cut and promotion (sibling), the suites themselves.

**Spec**

* Deploy: `POST /api/v1/deploy?uuid=<staging>` with bearer secret; poll deployment status until `finished` (cap 15 minutes); smoke checks; on failure stop and report.
* Backup: call PAP-30's backup script before migrations, record `snapshotId`.
* Suites: PAP-86 `@full` including 375 run, PAP-82 full 21 combinations, PAP-85 nightly library, PAP-87 informational Pages run, API perf smoke when available.
* Aggregate: `{ date, sha, deploy: { status, durationMs }, suites: [{ name, status, reportUrl }], trends }`; three consecutive nights of reports are the DoD evidence.
* Notification: comment on the pinned Linear issue via PAP-97 with a one-line status and links; red nights also open a task for Atlas.

**Interface contract**

* Provides: nightly report artifact and Pages URL `/nightly/<date>/`, `deployToEnvironment(name, sha)` composite action reused by the RC sibling, staging trend data for PAP-89.
* Requires: sibling policy (`environments.yaml`), PAP-26 images and Coolify, PAP-30 backup script, PAP-86, PAP-82, PAP-85, PAP-97.

**Definition of done**

* Three consecutive nightly runs with reports (links).
* Seeded failing deploy (bad SHA) stops before suites and reports `deploy: failed` (link).
* `deployToEnvironment` reused by the RC workflow (PR reference).
* Docs section "Nightly".

**Test plan**

* Unit: aggregate writer, status polling with fake responses.
* Integration: `workflow_dispatch` rehearsal against staging.

**Demo**

Trigger `workflow_dispatch` on `staging-nightly`, watch the deploy step finish, then open the nightly report page for that date. Two minutes of watching after the run.

**Edge cases**

* Migration fails: no app rollout; report flags it; snapshot id retained for restore.
* Coolify API down: retry 30 minutes then fail loudly.
* Suites exceed runner capacity: sequential fallback with a duration warning.

**Dependencies**

Sibling policy child (hard), PAP-26 (hard). Soft: PAP-30, PAP-86, PAP-82, PAP-85, PAP-97.

**Agent**

Built by Forge (Ops Runner) with Sentinel. Reviewed by Atlas.

**Size**

M.
