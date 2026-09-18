---
identifier: "PAP-565"
title: "`/admin/jobs` staff page and `jobs.list|get|requeue|cancel` procedures with dead-letter requeue, `paperos_jobs_*` metrics and the dev banner for pending jobs without a worker"
project: "data-layer"
projectName: "Data Layer & Database"
phase: "P1"
type: "Build"
priority: 2
surfaces: ["Staff"]
milestone: "Local-first sync working"
state: "Backlog"
parent: "PAP-43"
children: []
blockedBy: ["PAP-268", "PAP-564"]
blocks: ["PAP-37", "PAP-39", "PAP-136", "PAP-174", "PAP-190", "PAP-191", "PAP-194", "PAP-199", "PAP-205", "PAP-221", "PAP-222", "PAP-324", "PAP-347", "PAP-355", "PAP-388", "PAP-391", "PAP-402", "PAP-404", "PAP-420", "PAP-432", "PAP-443", "PAP-454", "PAP-540", "PAP-560", "PAP-561", "PAP-566", "PAP-567", "PAP-574", "PAP-577", "PAP-625", "PAP-640", "PAP-725", "PAP-765", "PAP-766", "PAP-772", "PAP-791", "PAP-820", "PAP-835", "PAP-849", "PAP-851", "PAP-857", "PAP-864", "PAP-866", "PAP-894", "PAP-903", "PAP-908"]
key: "r4/data-layer/jobs-admin"
url: "https://linear.app/paperos/issue/PAP-565/adminjobs-staff-page-and-jobslistgetrequeuecancel-procedures-with-dead"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:08.998Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 2
dueDate: "2026-09-25"
cycle: null
---

# PAP-565: `/admin/jobs` staff page and `jobs.list|get|requeue|cancel` procedures with dead-letter requeue, `paperos_jobs_*` metrics and the dev banner for pending jobs without a worker

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Build S

**Goal**

Second child of PAP-43: make background work visible. Staff see queued, active, failed and dead-lettered jobs with attempts and errors, can requeue or cancel, and Grafana gets queue depth and latency; developers get a banner when jobs are pending but no worker runs.

**Scope**

In: oRPC router `jobs` in `packages/api-contract` (staff only, `authorize('jobs.manage')`), page `/admin/jobs` with spec `specs/pages/admin/jobs.spec.yaml` using the PAP-165 grid when present else the PAP-71 table, metrics exporter `paperos_jobs_{queued,active,failed,dead_letter,duration_seconds}` by job name, dev banner component, `docs/platform/jobs.md` admin section.

Out: Core runtime (sibling), workflow visualisation (PAP-174 automations), agent session status (PAP-288).

**Spec**

* `jobs.list({ state?, name?, tenantId?, cursor })` returns `{ id, name, state, attempts, createdAt, startedAt, finishedAt, lastError, tenantId }` with signed cursors; `jobs.get` adds the redacted payload (`pii.json`); `jobs.requeue(id)` and `jobs.cancel(id)` audited with reason.
* Page columns and filters per state; row action Requeue on dead-letter rows; a Run demo button enqueues the demo job in non-production.
* Metrics scraped from the worker `/metrics`; alert when `dead_letter` grows by more than 10 in an hour or `queued` age exceeds 10 minutes (PAP-40).
* Dev banner: `pnpm dev` polls `jobs.queued` count; if greater than zero and no worker heartbeat in 60 s, the shell shows a banner with the command to start one.

**Interface contract**

Provides: oRPC `jobs.*`, page `/admin/jobs`, metrics above, `JobsDevBanner`.

Consumes: Core package (sibling), routers and `callAs` (PAP-268), `can()` (PAP-229, soft), grid (PAP-165, soft) or table (PAP-71), spec schema (PAP-114), Grafana (PAP-40, soft).

**Definition of done**

* Customer principal gets `FORBIDDEN` on `jobs.list`; staff sees the run; dead-letter requeue works and is audited.
* Page screenshots at 768, 1280, 1920 with a dead-letter row, light and dark; axe clean; spec validates.
* Metrics visible in Grafana with the two alerts configured; docs; CHANGELOG; Linear comment with the screenshot.

**Test plan**

* Unit: list filter to SQL, payload redaction, cursor round trip, banner condition logic with fake timers.
* E2E: Playwright: staff opens the page, runs the demo job, watches attempts update, requeues a dead-letter row; `callAs(customer)` denied.

**Demo**

Reviewer opens `/admin/jobs` as staff, clicks Run demo, watches the retry schedule, then requeues the seeded dead-letter row. Under 90 seconds.

**Edge cases**

* 10,000 dead-letter rows: paginated; bulk requeue by name capped at 500.
* Payload contains a `file_id` only: page links to the file, never inlines blobs.
* Worker heartbeat missing in production: alert, no banner.

**Dependencies**

Blocked by PAP-564 and PAP-268 (hard). Soft: PAP-229, PAP-165, PAP-71, PAP-114, PAP-40.

**Agent**

Builder: Forge (Platform Engineer) with Iris on the page. Reviewer: Sentinel (Code Reviewer).

**Size**

S: half a session.

*Round 4 critique fix (2026-09-18):* resolved 1 round-4 file key in this description to Linear identifiers: `r4/data-layer/jobs-core` = PAP-564.
