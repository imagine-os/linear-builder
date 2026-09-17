---
identifier: "PAP-303"
title: "Specify the domain event contract: envelope, topic catalogue, `defineTopic` registry, transactional outbox and subscriber delivery (`packages/core/events`)"
project: "data-layer"
projectName: "Data Layer & Database"
phase: "P0"
type: "Spec"
priority: 1
surfaces: ["Agent", "Developer"]
milestone: "Postgres + Drizzle baseline"
state: "Ready for Claude"
parent: null
children: []
blockedBy: []
blocks: ["PAP-28", "PAP-97", "PAP-136", "PAP-174", "PAP-177", "PAP-179", "PAP-195", "PAP-222"]
key: "contracts/domain-events"
url: "https://linear.app/paperos/issue/PAP-303/specify-the-domain-event-contract-envelope-topic-catalogue-definetopic"
source: "Linear snapshot 2026-09-17T13:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T13:00:52.035Z"
---

# PAP-303: Specify the domain event contract: envelope, topic catalogue, `defineTopic` registry, transactional outbox and subscriber delivery (`packages/core/events`)

**Goal**

Give PaperOS one way to say "something happened": a typed event envelope, a registry of topics with Zod payloads, a transactional outbox written in the same transaction as the row change, and a dispatcher that delivers to in-process subscribers, jobs, live events, tenant webhooks and the orchestrator. PAP-28 mandates cross-module coupling only via `emit('invoice.paid')`; PAP-136 kinds, PAP-174 triggers, PAP-195 enter/exit events, PAP-222 webhooks and PAP-97 all need the bus; only the orchestrator has an in-process emitter today. This issue supersedes the pending gap `gap/data-layer/event-bus` (merged here 2026-09-17, FIX-6; from it: `flags.changed` for the runtime flags gap and `file.ready` for PAP-37 join the initial catalogue, and PAP-181 is a consumer).

**Scope**

In:

* `packages/core/src/events/`: `envelope.ts` (Zod `DomainEvent`), `registry.ts` (`defineTopic(name, payloadSchema, { version, description, producer })`, `topics()`), `catalogue/*.ts` (initial topics from the contracts document, each in the producing package's folder but registered here), `subscribe.ts` (`on(topic, handler, { name, idempotent: true })`), `publish.ts` (`publish(tx, event)` writes to the outbox inside the caller's transaction).
* `packages/db/src/schema/events.ts`: `outbox_event (id uuidv7 pk, tenant_id, topic, version, occurred_at, actor_id, actor_kind, actor_character, subject_type, subject_id, request_id, causation_id, correlation_id, idempotency_key, payload jsonb, published_at, attempts, last_error)` partitioned monthly, and `event_subscription (name pk, topics text[], kind: inproc|job|webhook|live, config jsonb, active)`.
* Dispatcher job `events.dispatch` (PAP-43) polling `outbox_event where published_at is null` with `FOR UPDATE SKIP LOCKED` in batches of 100, fanning out per subscription kind: in-process handler, `enqueue(job)`, `publishLiveEvent()` (push transport), `emitWebhook()` (PAP-222), orchestrator HTTP (PAP-97).
* `pnpm events:catalogue` renders `docs/platform/events.md` from the registry (topic, version, payload schema, producer, known consumers); Gate 1 fails on drift.
* Testing helpers `packages/core/events/testing`: `collectEvents(fn)`, `expectEvent(topic, matcher)`.

Out: the consumers' own logic, external webhook receivers (PAP-97, PAP-177 keep theirs and normalise into the envelope), Kafka or Redis, exactly-once delivery.

**Spec**

* Envelope: `{ id: Uuid, topic: string, version: number, occurredAt: IsoDateTime, tenantId: Uuid | null, actor: ActorRef, subject: EntityRef, requestId?, causationId?, correlationId?, idempotencyKey?, payload }`; `ActorRef` and `EntityRef` from the shared value types issue.
* Topic names are `<entity>.<past-tense-verb>` with optional qualifier (`agent.session.started`), lower-case, dot-separated, max 48 chars; the registry rejects duplicates and names not matching the pattern at boot.
* Payloads carry ids and changed fields only, never whole rows, emails or names (PII policy shared with PAP-40); a `payloadSchema` refinement rejects keys listed in `pii.json` (PAP-41).
* Delivery is at-least-once, ordered per `subject` (dispatcher groups a batch by `subject_id`), unordered across subjects; handlers must be idempotent on `event.id` and declare it.
* `publish()` requires a transaction handle so an event can never be written without its row change; a lint rule flags `publish(db, ...)` outside `withTenant`.
* Versioning: breaking payload change bumps `version`; the registry keeps the previous schema for 30 days and the dispatcher upcasts with `migrate(from, to)`.
* Retention: `outbox_event` partitions kept 90 days, then archived to MinIO like PAP-38; `attempts` over 10 moves the event to `jobs.dead_letter` with the subscription name.
* Initial catalogue (registered in this issue with placeholder producers where the producer's issue has not merged): `tenant.created|deleted`, `membership.invited|accepted|removed`, `agent.session.started|finished|blocked`, `agent.quota.exceeded`, `issue.needs_justin`, `review.gate_failed|ready`, `release.candidate`, `record.created|updated|deleted`, `view.shared`, `comment.created|mentioned|resolved`, `doc.published`, `changelog.published`, `file.ready|failed`, `job.finished|failed`, `import.finished`, `invoice.issued|paid|voided`, `payment.succeeded|failed|refunded`, `subscription.updated`, `payroll.run.approved|paid`, `ledger.entry.posted|reversed`, `segment.entered|exited`, `webhook.delivery.failed`, `sync.conflict`.

**Interface contract**

Provides (from `@paperos/core/events`): `DomainEvent`, `domainEventSchema`, `defineTopic`, `TopicPayload<T>`, `publish`, `on`, `topics`, `collectEvents`, `expectEvent`; tables `outbox_event`, `event_subscription`; job `events.dispatch`; generated `docs/platform/events.md`. Consumes: `ActorRef`/`EntityRef` (shared value types issue), `createDb`/`withTenant` (PAP-32), jobs (PAP-43) for the dispatcher, `pii.json` (PAP-41, soft), `publishLiveEvent` (pending push transport), `emitWebhook` (PAP-222), orchestrator receiver (PAP-97). Consumed by PAP-28, PAP-97, PAP-136 (work package 1, the notification core), PAP-174, PAP-179, PAP-195, PAP-222, PAP-113, PAP-60, PAP-148.

**Test plan**

* Unit: envelope schema fixtures (valid, bad topic name, PII key, missing subject); registry duplicate and pattern rejection; `migrate` upcast.
* Integration (PAP-42 stack): a row insert plus `publish()` in one transaction commits both or neither (forced failure after publish); dispatcher delivers to an in-process handler exactly once for 1,000 events with a crash injected at event 500 and no duplicates after restart (idempotent handler asserts); per-subject ordering preserved under concurrency 4.
* Type: `on('invoice.paid', h)` infers the payload type (`expectTypeOf`).
* Perf: dispatcher drains 10,000 events in under 60 s on the dev stack; bench committed.

**Definition of done**

* Package, schema, dispatcher job and testing helpers merged; catalogue doc generated and drift check green.
* Integration tests above green in CI; bench results committed.
* PAP-28, PAP-136 (work package 1), PAP-174, PAP-195 and PAP-222 owners have a comment from this session pointing at the topics they consume.
* `docs/platform/events.md`; ADR `docs/adr/00xx-domain-events.md` recording the Postgres-outbox decision and the trigger condition for moving to a broker; CHANGELOG; Linear comment with the docs link.

**Edge cases**

* Tenant deleted while events pending: dispatcher skips with `tenant_gone` and marks published.
* Handler throws on a poison payload: retried with backoff, then dead-lettered with the subscription name; other subscriptions still receive the event.
* Subscriber added after events were published: no replay by default; `pnpm events:replay --topic --since` replays with `replayed: true` in the envelope so handlers can opt out.
* Payload over 64 KB: rejected at `publish`; producers store a reference instead.
* Clock skew between API instances: `occurredAt` is the database `now()` at insert, not the process clock.
* Same `idempotencyKey` published twice in one tenant: second insert is a no-op (unique partial index).

**Dependencies**

None hard for the package and schema (pure on the PAP-13 layout with PAP-32 conventions). Dispatcher needs PAP-43 (soft: in-process runner until it merges). Soft: shared value types issue, PAP-41, PAP-222, PAP-97. Ready now. Blocks PAP-28, PAP-97, PAP-136, PAP-174, PAP-177, PAP-179, PAP-195, PAP-222.

**Agent**

Specified and built by Forge (Platform Engineer). Reviewed by Sentinel (Security Auditor for the PII refinement) and Atlas (catalogue completeness).

**Size**

M

**Demo**

Reviewer runs `pnpm dev` with the PAP-42 stack, executes `pnpm tsx examples/events.ts` which creates a demo invoice and publishes `invoice.paid` in the same transaction, then watches the dispatcher log show the in-process handler, a queued job and a `live_event` row; finally `pnpm events:catalogue` prints the topic table. Under two minutes.
