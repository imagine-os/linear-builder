---
identifier: "PAP-43"
title: "Build the background jobs and scheduler package (pg-boss) with retries, idempotency keys, cron, dead-letter queue and an admin view"
project: "data-layer"
projectName: "Data Layer & Database"
phase: "P1"
type: "Build"
priority: 1
surfaces: ["Developer", "Staff"]
milestone: "Local-first sync working"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-32", "PAP-214", "PAP-297"]
blocks: ["PAP-37", "PAP-39", "PAP-136", "PAP-174", "PAP-190", "PAP-191", "PAP-194", "PAP-199", "PAP-205", "PAP-221", "PAP-222", "PAP-324", "PAP-347", "PAP-355", "PAP-388", "PAP-391", "PAP-402", "PAP-404", "PAP-420"]
key: "data-layer/jobs-queue"
url: "https://linear.app/paperos/issue/PAP-43/build-the-background-jobs-and-scheduler-package-pg-boss-with-retries"
source: "Linear snapshot 2026-09-17T13:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T13:05:24.319Z"
model: "claude-sonnet-5"
effort: "high"
---

# PAP-43: Build the background jobs and scheduler package (pg-boss) with retries, idempotency keys, cron, dead-letter queue and an admin view

**Goal**

Provide the one background-work runtime eight later issues assume by name: `packages/jobs` on pg-boss 10.x (Postgres-native, no Redis; PAP-214 confirms or overrides) with at-least-once delivery, idempotent handlers, ordered retries, cron, a dead-letter queue and a staff admin view. The transactional outbox for domain events (events issue) and the tenant-lifecycle purge job build on it.

**Scope**

In:

* `defineJob({ name, schema, handler, retry, concurrency, singletonKey, timeout })` registry; `enqueue(job, input, { idempotencyKey, runAt, priority, tenantId })`; `schedule(job, cron, input)`.
* `apps/worker` entry with its own Dockerfile (PAP-26) loading every registered job.
* pg-boss schema `jobs`; tenant and actor context propagated so PAP-38 records `actor_kind = 'system'`.
* `withIdempotency(key, fn)` backed by `jobs.idempotency`.
* Retries 5 attempts, backoff 10 s to 10 min; `jobs.dead_letter` with requeue.
* `/admin/jobs` page (staff only) using PAP-165 grid.

Out: durable workflows and human approvals (PAP-174 automations), event catalogue (events issue).

**Spec**

* Job names `domain.action`; duplicates rejected at boot.
* Payload validated on enqueue and dequeue; drift fails into dead-letter, not a crash.
* `concurrency: { perTenant: n }` via `singletonKey = tenantId` groups.
* SIGTERM drains 30 s; unfinished jobs return to the queue.
* `runAt` and cron in UTC.
* Archive after 7 days, delete after 30; dead-letter kept 90 days.
* Inputs over 64 KB rejected; store blobs in PAP-37 and pass a reference.
* `pnpm dev` runs an inline worker; dev shell banner when jobs are pending without a worker.

**Interface contract**

Provides (from `@paperos/jobs`):

* `defineJob`, `enqueue`, `schedule`, `withIdempotency`, `JobContext = { tenantId?, actorId?, requestId, attempt, log }`; `JobDefinition<TInput>` type.
* Tables `jobs.*` (pg-boss), `jobs.idempotency (key, completed_at, result)`, `jobs.dead_letter`.
* oRPC `jobs.list|get|requeue|cancel` (staff only) and page `/admin/jobs`.
* Docker image `ghcr.io/imagine-os/<app>-worker` (PAP-26).
* Metrics `paperos_jobs_*` for PAP-40.

Consumers by name: `files.variants` (PAP-37), `search.upsert|embed` (PAP-39), `audit.partitions|archive` (PAP-38), `notify.deliver` (PAP-136), `outreach.step` (PAP-191), `social.publish` (PAP-190), `attribution.rollup` (PAP-194), `import.chunk` (PAP-199), `export.run` (PAP-205), `events.dispatch` (events issue), `tenant.purge` (lifecycle issue). Consumes: schema and migrations (PAP-32), library decision (PAP-214), audit vars (PAP-38), `can()` for the admin page (PAP-59).

**Definition of done**

* 1,000 jobs processed by two replicas with zero duplicate effects (one row per key).
* Worker killed mid-job: reruns on the other replica; idempotency guard prevents a double effect (log).
* Cron fires within a 3-minute window; admin view shows the run.
* Dead-letter requeue works; customer principal cannot open `/admin/jobs`.
* PAP-37 variants converted to `packages/jobs` as the reference consumer.
* `docs/platform/jobs.md`, ADR note, CHANGELOG, Linear comment with metrics screenshot.

**Test plan**

* Unit: registry duplicate rejection; schema validation on both sides; backoff schedule; `withIdempotency` under concurrent callers.
* Integration (CI compose): two worker processes, 1,000 enqueues with 500 distinct keys, assert 500 effects; SIGKILL one worker mid-handler; per-tenant concurrency limit observed.
* Cron: `*/1 * * * *` job asserted within 3 minutes.
* Permission: `callAs(customer)` on `jobs.list` returns `FORBIDDEN`.
* Visual: `/admin/jobs` at 768, 1280, 1920 with a dead-letter row.

**Demo**

Reviewer opens `/admin/jobs` as staff, enqueues a demo job that fails twice then succeeds from the "Run demo" button, watches attempts and the retry schedule update live, then requeues a dead-letter row. Under 90 seconds.

**Edge cases**

* Postgres failover mid-poll: reconnect; expired `active` jobs retried.
* Handler never resolves: per-job timeout, default 5 minutes.
* Thundering herd after downtime: `singletonKey` per schedule collapses runs.
* Tenant deleted while queued: handler completes as `skipped`.
* Schema drift after deploy: dead-letter with a clear error.

**Dependencies**

PAP-32, PAP-214 (hard). Soft: PAP-26, PAP-38, PAP-40, PAP-59, PAP-165. Unblocks PAP-37, PAP-39, PAP-136, PAP-174, PAP-190, PAP-191, PAP-194, PAP-199, PAP-205 and the events, email, DR and lifecycle issues.

**Agent**

Built by Forge (Platform Engineer). Reviewed by Sentinel (Code Reviewer).

**Size**

M: one package, one worker app, one admin page.
