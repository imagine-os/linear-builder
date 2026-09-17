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
blockedBy: ["PAP-214", "PAP-32"]
blocks: ["PAP-136", "PAP-174", "PAP-190", "PAP-191", "PAP-194", "PAP-199", "PAP-205", "PAP-221", "PAP-222", "PAP-37", "PAP-39"]
key: "data-layer/jobs-queue"
url: "https://linear.app/paperos/issue/PAP-43/build-the-background-jobs-and-scheduler-package-pg-boss-with-retries"
source: "plan/specs/gaps.json (round-1 canonical spec JSON)"
---

# PAP-43: Build the background jobs and scheduler package (pg-boss) with retries, idempotency keys, cron, dead-letter queue and an admin view

**Goal**

Provide the one background-work runtime that eight later issues already assume by name (`data-layer/file-storage` variants worker, `data-layer/search` indexing, `collab/notifications` delivery, `growth/social-scheduler`, `growth/outreach-sequences`, `growth/attribution` rollups, `migration/import-framework`, `migration/export`) but none owns. `libraries/backend-landscape` decides between pg-boss, Graphile Worker, Inngest and Trigger.dev; this issue implements the winner (default pg-boss, Postgres-native, no Redis) as `packages/jobs` with the guarantees those consumers need: at-least-once delivery, idempotent handlers, ordered retries, cron, and visibility for staff.

**Scope**

In:
- `packages/jobs/`: `defineJob({ name, schema (Zod), handler, retry, concurrency, singletonKey })` registry; typed `enqueue(job, input, { idempotencyKey, runAt, priority, tenantId })`; `schedule(job, cron, input)`; worker entry `apps/worker` (own Dockerfile through `app-shell/app-deploy-pipeline`) that loads every registered job from packages.
- pg-boss 10.x on the application Postgres in schema `jobs`; tenant context and actor propagated into the handler so `data-layer/audit-log` records `actor_kind = 'system'` with the job name as reason.
- Idempotency: `idempotencyKey` maps to pg-boss `singletonKey` for enqueue-dedup plus a `jobs.idempotency` table for handler-side exactly-once effects (`withIdempotency(key, fn)`).
- Retry policy defaults: 5 attempts, exponential backoff 10 s to 10 min; per-job override; poison messages land in `jobs.dead_letter` with input and last error; requeue action.
- Cron via pg-boss schedules with timezone support; a `jobs.schedules` table mirrors them for the admin UI.
- Admin view: staff page `/admin/jobs` (page spec under `specs/pages/admin/jobs.page.spec.yaml`) using `tables/grid-view` when available, otherwise a simple table: queue depth, running, failed, dead-letter with retry and cancel actions; permission `jobs.manage` from `identity/rbac-abac`.
- Observability: OpenTelemetry spans per job run, metrics `jobs_active`, `jobs_failed_total`, `jobs_latency_seconds` exported for `data-layer/observability`; structured logs with `job_id`, `tenant_id`.
- Testing helpers: `packages/jobs/testing` with an in-process runner (`runJobsUntilIdle()`) so consumers test without a worker process; `pnpm jobs:dev` runs the worker inline with `pnpm dev`.

Out: durable multi-step workflows with human waits (revisit with Inngest or Temporal if a consumer needs it; ADR notes the trigger condition), Redis, cross-tenant fair scheduling beyond per-tenant concurrency limits, the UI polish beyond the admin grid.

**Spec**

- Job names are `domain.action` (`files.variants`, `search.upsert`, `notify.deliver`, `outreach.step`, `import.chunk`); the registry rejects duplicates at boot.
- Payloads validated with the job's Zod schema on enqueue and on dequeue (schema drift after a deploy fails safe into dead-letter, not a crash).
- Per-tenant concurrency: `concurrency: { perTenant: n }` implemented with pg-boss `singletonKey = tenantId` groups; documented limits.
- Graceful shutdown: worker drains for up to 30 s on SIGTERM (Coolify redeploys), unfinished jobs return to the queue.
- Clock: `runAt` and cron evaluated in UTC; tenant timezone conversions happen in the consumer.
- Maintenance: pg-boss archive after 7 days, delete after 30; `jobs.dead_letter` kept 90 days.

**Definition of done**

- 1,000 enqueued jobs processed by two worker replicas with zero duplicates of an idempotent effect (test asserts one row per key).
- Kill a worker mid-job: the job re-runs on the other replica and the idempotency guard prevents a double effect (test log).
- Cron job fires at the scheduled minute in a 3-minute test window; admin view shows the run.
- Dead-letter requeue from the admin page succeeds; permission test proves customers cannot see `/admin/jobs`.
- Consumer migration: `data-layer/file-storage` variants worker converted to `packages/jobs` in this PR as the reference consumer.
- Docs `docs/platform/jobs.md` (how to define, enqueue, test a job), ADR update to `libraries/backend-landscape`, `CHANGELOG.md`, Linear comment with metrics screenshot.

**Edge cases**

- Postgres failover mid-poll: pg-boss reconnects with backoff; jobs in `active` past their `expireInSeconds` are retried.
- A handler that never resolves: per-job timeout (default 5 min) converts to a failure; long imports chunk themselves (`migration/import-framework`).
- Thundering herd after downtime: 10,000 due cron runs on restart; `singletonKey` per schedule collapses them to one.
- Tenant deleted while jobs are queued: handler checks tenant existence and completes as `skipped`.
- Very large payloads: inputs over 64 KB are rejected at enqueue; consumers store the blob (`data-layer/file-storage`) and pass a reference.
- Local dev without a worker running: `pnpm dev` starts the inline worker; a banner in the dev shell warns when jobs are pending with no worker.

**Dependencies**

`data-layer/drizzle-schema` (database, migrations, `jobs` schema), `libraries/backend-landscape` (final library choice; this spec defaults to pg-boss). Soft: `data-layer/audit-log`, `data-layer/observability`, `identity/rbac-abac`, `tables/grid-view`, `app-shell/app-deploy-pipeline` (worker image). Consumed by `data-layer/file-storage`, `data-layer/search`, `collab/notifications`, `growth/social-scheduler`, `growth/outreach-sequences`, `growth/attribution`, `migration/import-framework`, `migration/export`, `tables/automations`.

**Agent**

Built by Forge (Platform Engineer). Reviewed by Sentinel (Code Reviewer, Edge Case Hunter for the failure matrix) and Nova (first heavy consumer).

**Size**

M: well-supported library, but the idempotency and shutdown semantics must be right because eight consumers inherit them.
