---
key: "pm-linear/linear-sync/outbound"
title: "Linear sync: transactional outbox, outbound worker and loop prevention"
project: "pm-linear"
parent: "PAP-101"
phase: "P2"
type: "Build"
priority: null
size: "M"
surfaces: ["Staff"]
milestone: null
intendedState: "Backlog"
blockedBy: ["pm-linear/linear-sync/inbound"]
blocks: ["pm-linear/linear-sync/conflicts"]
source: "round2/agent2/new_pm.py"
linearDocument: "https://linear.app/paperos/document/round-2-pending-issues-pm-linear-9-d4829fc00859"
identifier: "PAP-373"
status: "created"
createdAt: "2026-09-17"
---

# Linear sync: transactional outbox, outbound worker and loop prevention

**Goal**

Let PaperOS write to Linear: every PM mutation records an outbox row in the same transaction, a worker drains it with batched, rate-aware `@linear/sdk` mutations, stores returned ids and never echoes its own changes back in, so a board drag in PaperOS lands in Linear within seconds without ping-pong.

**Scope**

* In: `pm_outbox` table, oRPC middleware that enqueues on `pm.*` mutations, `packages/pm-sync/src/outbound.ts` worker (PAP-43 job), loop prevention, retry and dead-letter, `pm.sync.retry(id)`.
* Out: conflict detection (`pm-linear/linear-sync/conflicts`), inbound (`pm-linear/linear-sync/inbound`).

**Spec**

* `pm_outbox(id, tenant_id, entity_type, entity_id, op: create | update | archive | comment | relation | label, payload, idempotency_key, attempts, next_attempt_at, last_error, state: pending | sent | dead, created_at)`; written by the mutation transaction unless the write has `source: "linear"`.
* Worker: every 2 s take up to 10 pending rows `FOR UPDATE SKIP LOCKED`, group by op, send one aliased mutation request, store Linear ids into `pm_external_ref`, mark `sent`; respect `X-RateLimit-Requests-Remaining` and pause at 10 percent; backoff 1 s to 10 min, eight attempts, then `dead`.
* Loop prevention: mutations use the sync API key whose `actor.id` PAP-97 recognises and skips on inbound; the description footer or attachment metadata carries `idempotency_key` so an early inbound echo matches the pending row instead of creating a duplicate.
* Ordering: rows for one entity are sent in `id` order; a `create` must be `sent` before its `update`s.

**Interface contract**

* Provides: `enqueueOutbox(tx, row)`, worker job `pm-sync.outbound`, `pm.sync.retry(id)`, `pm.sync.dead()` list, event `pm.sync.outbound.sent { entity, id, linearId }`, metric `outboxDepth`.
* Consumers: PAP-102 (drag to state), PAP-204 (imported issues flow out), sibling conflicts child (reads `sent` timestamps), PAP-98 optional Linear request budget accounting.
* Requires: inbound child (`pm_external_ref` ids for updates), PAP-43 jobs, PAP-35 middleware hook, PAP-60 sync principal.

**Definition of done**

* Create, update, comment, label and relation ops round-trip to Linear in staging with correct ids stored.
* Loop test: 1000 synthetic PaperOS edits produce exactly 1000 outbox rows and zero echo rows.
* Rate-limit pause and dead-letter exercised with mocked headers.
* Changelog; Linear comment with results.

**Test plan**

* Unit: enqueue middleware (skips `source: linear`), ordering per entity, backoff schedule, alias batching of mixed ops.
* Integration: `nock` Linear with `RATELIMITED` and 429 responses; idempotency-key echo match.
* e2e: staging round trip of each op.
* No UI.

**Demo**

Call `pnpm api call pm.issues.update --id <id> --state "In Progress"`, watch the worker log send the mutation, and see the Linear issue change within five seconds; run `pm.sync.dead` and see an empty list. One minute.

**Edge cases**

* Linear rejects a label not existing there: create it, flag `source: paperos`.
* Entity has no `pm_external_ref` yet (create still pending): later ops wait.
* Worker crash mid-batch: rows stay `pending` with `attempts` incremented.
* Description exceeds Linear limits: truncate with a link back to PaperOS.
* Tenant other than the PAP mirror tenant: outbox disabled per tenant setting.

**Dependencies**

Blocked by `pm-linear/linear-sync/inbound`. Uses PAP-43, PAP-60.

**Agent**

Built by Forge (Schema Wright) with Nova; reviewed by Sentinel.

**Size**

M
