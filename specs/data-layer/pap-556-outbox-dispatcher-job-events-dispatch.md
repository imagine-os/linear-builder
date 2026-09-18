---
identifier: "PAP-556"
title: "Outbox dispatcher job `events.dispatch`: per-subject ordering, fan-out to in-process, job, live-event, webhook and orchestrator sinks, dead-letter and `events:replay`"
project: "data-layer"
projectName: "Data Layer & Database"
phase: "P0"
type: "Build"
priority: 1
surfaces: ["Developer"]
milestone: "Postgres + Drizzle baseline"
state: "Backlog"
parent: "PAP-303"
children: []
blockedBy: ["PAP-555"]
blocks: ["PAP-28", "PAP-97", "PAP-136", "PAP-174", "PAP-177", "PAP-179", "PAP-195", "PAP-222", "PAP-436", "PAP-448", "PAP-725", "PAP-833", "PAP-834", "PAP-847", "PAP-848", "PAP-851", "PAP-862", "PAP-864", "PAP-877", "PAP-893", "PAP-897"]
key: "r4/data-layer/events-outbox-dispatcher"
url: "https://linear.app/paperos/issue/PAP-556/outbox-dispatcher-job-eventsdispatch-per-subject-ordering-fan-out-to"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:07.084Z"
model: "claude-opus-5"
effort: "high"
estimate: 3
dueDate: "2026-09-22"
cycle: null
---

# PAP-556: Outbox dispatcher job `events.dispatch`: per-subject ordering, fan-out to in-process, job, live-event, webhook and orchestrator sinks, dead-letter and `events:replay`

**Model / Effort:** Opus 5 (`claude-opus-5`) / high — Build M

**Goal**

Second half of PAP-303: turn outbox rows into deliveries. A pg-boss job polls undelivered `outbox_event` rows with `FOR UPDATE SKIP LOCKED`, groups by subject so per-entity ordering holds, fans out to every active subscription kind, retries with backoff, dead-letters poison events and can replay a topic window. Until PAP-43 merges the same loop runs in-process behind `EVENTS_DISPATCH=inline`.

**Scope**

In: `packages/core/src/events/dispatch/{poll,fanout,sinks,replay}.ts`, job definition `events.dispatch` (`defineJob` from PAP-43 when present, else `setInterval` runner), sinks `inproc`, `job` (`enqueue`), `live` (`publishLiveEvent` from PAP-599, no-op until it exists), `webhook` (`emitWebhook`, PAP-222, no-op stub), `orchestrator` (HTTP POST with HMAC to PAP-97), CLI `pnpm events:replay --topic --since --subscription`, metrics `paperos_events_*`.

Out: Envelope, registry and `publish()` (sibling); upcasters and dual publish (PAP-436); the sinks' own consumers.

**Spec**

* Batch of 100 rows per poll, concurrency 4 across subjects, strictly sequential per `subject_id`; a subject with a failing event blocks only that subject.
* Delivery at-least-once: each `(event, subscription)` pair has a row in `event_delivery (event_id, subscription, attempts, last_error, delivered_at)`; `published_at` is set when every active subscription delivered or dead-lettered.
* Retry backoff 1 s to 10 min, 10 attempts, then `jobs.dead_letter` (PAP-43) with the subscription name; other subscriptions still receive the event.
* `replayed: true` in the envelope for `events:replay`; idempotent handlers may opt out; replay is limited to 90 days (partition retention).
* Subscriptions of a module disabled for the tenant (PAP-266 `tenant_module`) are skipped with `skipped_reason = 'module_disabled'`; a deleted tenant yields `tenant_gone` and marks published.
* Outbox partitions: monthly, kept 90 days, archived to MinIO as Parquet by the same archive job PAP-38 uses; `event_delivery` pruned with its event.
* Metrics: lag (`now - occurred_at` of the oldest undelivered row), throughput, dead-letter count; alert when lag exceeds 60 s (PAP-40).

**Interface contract**

Provides: Job `events.dispatch`, table `event_delivery`, sink interface `EventSink { name, deliver(event, subscription) }` and `registerSink()`, CLI `events:replay`, metrics above.

Consumes: `publish`/registry/tables from the sibling, `defineJob` and `jobs.dead_letter` (PAP-43, soft with the inline runner), `publishLiveEvent` (PAP-599, soft), `emitWebhook` (PAP-222, soft), orchestrator receiver (PAP-97, soft), audit for `actor_kind='system'` (PAP-38). Consumed by PAP-177, PAP-179, PAP-222, PAP-136, PAP-174, PAP-195, PAP-113, PAP-148.

**Definition of done**

* Dispatcher delivers to an in-process handler exactly once for 1,000 events with a crash injected at event 500 and no duplicates after restart (idempotent handler asserts).
* Per-subject ordering preserved under concurrency 4 (property test with 200 subjects); bench: 10,000 events drained in under 60 s on the dev stack, numbers committed.
* Poison event dead-lettered after 10 attempts while its sibling subscriptions still deliver; `events:replay` re-delivers with `replayed: true`.
* `docs/platform/events.md` gains the delivery and replay sections; CHANGELOG; Linear comment with the bench.

**Test plan**

* Unit: poll query with `SKIP LOCKED` semantics against PGlite; subject grouping; backoff schedule; sink registry duplicate rejection; `tenant_gone` and `module_disabled` paths.
* E2E: compose stack with two worker replicas: 1,000 publishes across 50 subjects, assert one delivery per pair, ordering per subject, and the Grafana lag panel returns to zero.

**Demo**

Reviewer publishes `invoice.paid` from the example script, watches the worker log show the in-process handler, a queued job and (if present) a `live_event` row; then kills the handler with a thrown error and sees the dead-letter row appear in `/admin/jobs`. Under two minutes.

**Edge cases**

* Two dispatcher replicas: `SKIP LOCKED` prevents double pickup; a crashed replica's locked rows return after `statement_timeout`.
* Subscriber added after events were published: no automatic replay; `events:replay` is explicit and time-bounded.
* Sink unavailable (orchestrator down): that subscription's deliveries retry; others unaffected; lag alert fires after 60 s.
* Subject deleted before delivery: delivered anyway; handlers tolerate `NOT_FOUND`.

**Dependencies**

Blocked by PAP-555 (hard). Soft: PAP-43 (inline runner until pg-boss merges; converts to `defineJob` then), PAP-599, PAP-222, PAP-97, PAP-40. Blocks PAP-177, PAP-179, PAP-222.

**Agent**

Builder: Forge (Platform Engineer). Reviewer: Sentinel (Code Reviewer; Edge Case Hunter for ordering and crash injection).

**Size**

M: one session.

*Round 4 critique fix (2026-09-18):* resolved 2 round-4 file keys in this description to Linear identifiers: `r4/data-layer/events-core` = PAP-555, `r4/realtime/live-events-channel` = PAP-599.
