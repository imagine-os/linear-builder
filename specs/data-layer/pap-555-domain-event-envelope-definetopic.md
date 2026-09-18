---
identifier: "PAP-555"
title: "Domain event envelope, `defineTopic` registry, in-transaction `publish()`, testing helpers and the generated catalogue doc"
project: "data-layer"
projectName: "Data Layer & Database"
phase: "P0"
type: "Build"
priority: 1
surfaces: ["Developer"]
milestone: "Postgres + Drizzle baseline"
state: "Ready for Claude"
parent: "PAP-303"
children: []
blockedBy: []
blocks: ["PAP-28", "PAP-97", "PAP-136", "PAP-174", "PAP-195", "PAP-436", "PAP-448", "PAP-556", "PAP-568", "PAP-591", "PAP-725"]
key: "r4/data-layer/events-core"
url: "https://linear.app/paperos/issue/PAP-555/domain-event-envelope-definetopic-registry-in-transaction-publish"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:06.933Z"
model: "claude-opus-5"
effort: "high"
estimate: 3
dueDate: "2026-09-22"
cycle: {"number": 1, "name": "C1 Foundation & core systems", "startsAt": "2026-09-18", "endsAt": "2026-09-25"}
---

# PAP-555: Domain event envelope, `defineTopic` registry, in-transaction `publish()`, testing helpers and the generated catalogue doc

**Model / Effort:** Opus 5 (`claude-opus-5`) / high — Build M

**Goal**

First half of PAP-303: the pure package every producer and subscriber imports: the Zod `DomainEvent` envelope, `defineTopic()` registry, `publish(tx, event)` writing to the outbox inside the caller's transaction, `on()` subscriptions, the initial catalogue and the `pnpm events:catalogue` generator. Dispatch, fan-out and replay are the sibling PAP-556, so the twenty consumers of the envelope start on day one.

**Scope**

In: `packages/core/src/events/{envelope,registry,publish,subscribe,testing}.ts`, `packages/core/src/events/catalogue/*.ts` (initial topics with placeholder producers), `packages/db/src/schema/events.ts` (`outbox_event`, `event_subscription` tables and the monthly partition helper), `scripts/events-catalogue.ts` writing `docs/platform/events.md`, ADR `docs/adr/00xx-domain-events.md`.

Out: Dispatcher, fan-out, dead-letter and replay (sibling); upcasters and `topics.json` (PAP-436); webhook and orchestrator receivers (PAP-222, PAP-97).

**Spec**

* Envelope exactly as Contracts §3 (`id`, `topic`, `version`, `occurredAt`, `tenantId | null`, `actor: ActorRef`, `subject: EntityRef`, `requestId?`, `causationId?`, `correlationId?`, `idempotencyKey?`, `payload`); `ActorRef` and `EntityRef` from PAP-302 (type-equal local copy until it merges).
* `defineTopic(name, payloadSchema, { version, description, producer })`: names `<entity>.<past-tense-verb>[.<qualifier>]`, lower-case, max 48 chars; duplicates and bad names throw at import; `topics()` lists the registry; `TopicPayload<T>` infers payload types for `on()`.
* `publish(tx, event)` requires a Drizzle transaction handle and inserts into `outbox_event` with `occurred_at = now()` from the database; a Biome rule in `@paperos/config-biome/events` flags `publish(db, ...)` outside `withTenant`.
* PII refinement: `payloadSchema` rejects keys in `pii.json` (static denylist until PAP-559 lands) and payloads over 64 KB.
* `on(topic, handler, { name, idempotent: true })` registers an in-process subscriber (`event_subscription.kind = 'inproc'`) at boot; `drainInProcess(tx)` delivers after commit for dev and tests until the sibling dispatcher lands.
* Initial catalogue: every topic in PAP-303 plus `flags.changed` and `permission.changed` (PAP-591).
* Testing helpers `collectEvents(fn)` and `expectEvent(topic, matcher)` for Vitest; `pnpm events:catalogue --check` fails Gate 1 on drift.

**Interface contract**

Provides: `DomainEvent`, `domainEventSchema`, `defineTopic`, `TopicPayload<T>`, `publish`, `on`, `topics`, `drainInProcess`, `collectEvents`, `expectEvent`; tables `outbox_event`, `event_subscription`; `docs/platform/events.md`; ADR.

Consumes: `ActorRef`/`EntityRef` (PAP-302, soft), `createDb`/`withTenant` (PAP-32), `pii.json` (soft). Consumed by PAP-448, PAP-436, PAP-28, PAP-97, PAP-136, PAP-174, PAP-179, PAP-195, PAP-222, PAP-60, PAP-148 and the sibling dispatcher.

**Definition of done**

* Package and schema merged; catalogue doc generated and drift check green in Gate 1.
* Integration test: a row insert plus `publish()` in one transaction commits both or neither (forced failure after publish).
* Type test: `on('invoice.paid', h)` infers the payload (`expectTypeOf`); lint rule fixture fails on `publish(db, ...)`.
* ADR recording the Postgres-outbox decision; comments on PAP-28, PAP-136, PAP-174, PAP-195, PAP-222 naming their topics; Linear comment with the docs link.

**Test plan**

* Unit: envelope fixtures (valid, bad topic name, PII key, oversize payload, missing subject); registry duplicate and pattern rejection; `drainInProcess` delivers once per handler; partition helper name arithmetic.
* E2E: on the PAP-42 stack, `pnpm tsx examples/events.ts` creates a demo row and publishes in one transaction, then `SELECT` shows one `outbox_event` row with `published_at IS NULL` and the in-process handler log line.

**Demo**

Reviewer runs `pnpm events:catalogue` and reads the topic table, then runs the example script and watches the transaction test roll back both the row and the event when the failure flag is set. Under two minutes.

**Edge cases**

* Same `idempotencyKey` published twice in one tenant: unique partial index makes the second insert a no-op and `publish` returns the existing id.
* Clock skew between API instances: `occurredAt` comes from `now()` in the insert, never the process clock.
* Payload schema changed without a version bump: `events:catalogue --check` diffs the JSON Schema hash and fails.

**Dependencies**

None hard (pure package, ready now like the parent). Soft: PAP-302, PAP-32, PAP-559. Blocks PAP-448, PAP-436, PAP-28, PAP-136, PAP-174, PAP-195, PAP-97 and the sibling dispatcher.

**Agent**

Builder: Forge (Platform Engineer). Reviewer: Sentinel (Security Auditor for the PII refinement; Atlas checks catalogue completeness).

**Size**

M: one session.

*Round 4 critique fix (2026-09-18):* resolved 3 round-4 file keys in this description to Linear identifiers: `r4/data-layer/events-outbox-dispatcher` = PAP-556, `r4/data-layer/pii-registry` = PAP-559, `r4/identity/permission-propagation` = PAP-591.
