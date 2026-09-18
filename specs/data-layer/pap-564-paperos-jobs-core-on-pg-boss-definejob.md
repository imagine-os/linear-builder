---
identifier: "PAP-564"
title: "`@paperos/jobs` core on pg-boss: `defineJob`, `enqueue`, `schedule`, `withIdempotency`, tenant and actor context, retries, dead-letter and the `apps/worker` entry with Dockerfile"
project: "data-layer"
projectName: "Data Layer & Database"
phase: "P1"
type: "Build"
priority: 1
surfaces: ["Developer"]
milestone: "Local-first sync working"
state: "Backlog"
parent: "PAP-43"
children: []
blockedBy: ["PAP-32", "PAP-214", "PAP-297"]
blocks: ["PAP-37", "PAP-39", "PAP-136", "PAP-174", "PAP-199", "PAP-205", "PAP-355", "PAP-370", "PAP-420", "PAP-443", "PAP-454", "PAP-540", "PAP-559", "PAP-565", "PAP-566", "PAP-725"]
key: "r4/data-layer/jobs-core"
url: "https://linear.app/paperos/issue/PAP-564/paperosjobs-core-on-pg-boss-definejob-enqueue-schedule-withidempotency"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:08.845Z"
model: "claude-opus-5"
effort: "high"
estimate: 3
dueDate: "2026-09-25"
cycle: null
---

# PAP-564: `@paperos/jobs` core on pg-boss: `defineJob`, `enqueue`, `schedule`, `withIdempotency`, tenant and actor context, retries, dead-letter and the `apps/worker` entry with Dockerfile

**Model / Effort:** Opus 5 (`claude-opus-5`) / high — Build M

**Goal**

First child of PAP-43 and the runtime twenty issues name: the job registry and worker, without the admin page. Everything that runs later than the request (variants, embeddings, emails, exports, retention, event dispatch) goes through this package, so it lands first and stays small: pg-boss 10.x, Zod payloads on both sides, tenant and actor context for RLS and audit, ordered retries, cron and a dead-letter table.

**Scope**

In: `packages/jobs/src/{define,enqueue,schedule,idempotency,context,worker}.ts`, pg-boss schema `jobs` plus `jobs.idempotency (key, completed_at, result)` and `jobs.dead_letter`, `apps/worker` entry loading every registered job with its Dockerfile (PAP-26 image `ghcr.io/imagine-os/<app>-worker`), inline worker for `pnpm dev`, `docs/platform/jobs.md`.

Out: `/admin/jobs` page, `jobs.*` oRPC and metrics (sibling PAP-565), durable multi-step workflows (PAP-174), event dispatcher (PAP-556).

**Spec**

* `defineJob({ name: 'domain.action', schema, handler, retry: { attempts: 5, backoff: '10s..10m' }, concurrency: { global?, perTenant? }, singletonKey?, timeout: '5m' })`; duplicate names rejected at boot; payload validated on enqueue and on dequeue (drift goes to dead-letter, never a crash).
* `enqueue(job, input, { idempotencyKey, runAt, priority, tenantId, actorId, requestId })` maps `idempotencyKey` to pg-boss `singletonKey`; `schedule(job, cron, input)` in UTC; `withIdempotency(key, fn)` backed by `jobs.idempotency`.
* `JobContext = { tenantId?, actorId?, actorKind: 'system', requestId, attempt, log, db }` where `db` is `withTenant` when `tenantId` is set so RLS applies and PAP-38 records `actor_kind='system'` with `reason = job name`.
* Inputs over 64 KB rejected; store blobs in PAP-37 and pass a `file_id`.
* SIGTERM drains 30 s then returns unfinished jobs to the queue; archive after 7 days, delete after 30; dead-letter kept 90 days with requeue support.
* Per-tenant concurrency via `singletonKey = tenantId` groups; thundering herd after downtime collapsed by `singletonKey` per schedule.
* Library pinned by PAP-214's decision; if PAP-214 overrides pg-boss, the `JobsPort` surface stays identical and only `worker.ts` changes.

**Interface contract**

Provides: `defineJob`, `enqueue`, `schedule`, `withIdempotency`, `JobContext`, `JobDefinition<TInput>`, tables `jobs.*`, `jobs.idempotency`, `jobs.dead_letter`, worker image, env `JOBS_INLINE=1`.

Consumes: Schema and migrations (PAP-32), library decision (PAP-214), audit vars (PAP-38, soft), deploy pipeline for the image (PAP-26, soft). Consumed by name: `files.variants` (PAP-37), `search.upsert|embed` (PAP-39), `audit.partitions|archive` (PAP-38), `notify.deliver` (PAP-136), `email.send` (PAP-370), `import.chunk` (PAP-199), `export.run` (PAP-420), `events.dispatch`, `retention.run`, `tenant.purge`, and the sibling admin page.

**Definition of done**

* 1,000 jobs processed by two replicas with zero duplicate effects (one row per key); worker killed mid-job reruns on the other replica and the idempotency guard prevents a double effect (log attached).
* Cron `*/1 * * * *` fires within a 3-minute window; SIGTERM drain test green; schema drift lands in dead-letter with a clear error.
* PAP-37 `files.variants` converted as the reference consumer; `docs/platform/jobs.md`; ADR note; CHANGELOG; Linear comment.

**Test plan**

* Unit: registry duplicate rejection, schema validation on both sides, backoff schedule, `withIdempotency` under concurrent callers, context propagation into `withTenant`.
* E2E: CI compose: two worker processes, 1,000 enqueues with 500 distinct keys, assert 500 effects; SIGKILL one worker mid-handler; per-tenant concurrency limit observed with timestamps.

**Demo**

Reviewer runs `pnpm dev` and enqueues the demo job that fails twice then succeeds from `pnpm tsx examples/jobs.ts`, watches the inline worker log the retry schedule, then inspects `jobs.dead_letter` after forcing a schema mismatch. Under 90 seconds.

**Edge cases**

* Postgres failover mid-poll: reconnect; expired `active` jobs retried.
* Handler never resolves: per-job timeout, default 5 minutes, then retry.
* Tenant deleted while queued: handler receives `tenant_gone` and completes as `skipped`.
* Module disabled for the tenant (PAP-266): jobs of that module skipped with a reason.

**Dependencies**

Blocked by PAP-32 and PAP-214 (hard). Soft: PAP-26, PAP-38, PAP-40. Blocks PAP-37, PAP-39, PAP-136, PAP-174, PAP-199, PAP-205, PAP-355, PAP-370, PAP-420, PAP-443, PAP-454 and the sibling admin child.

**Agent**

Builder: Forge (Platform Engineer). Reviewer: Sentinel (Code Reviewer).

**Size**

M: one session.

*Round 4 critique fix (2026-09-18):* resolved 2 round-4 file keys in this description to Linear identifiers: `r4/data-layer/events-outbox-dispatcher` = PAP-556, `r4/data-layer/jobs-admin` = PAP-565.
