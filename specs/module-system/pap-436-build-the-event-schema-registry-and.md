---
identifier: "PAP-436"
title: "Build the event schema registry and versioned envelopes: aggregated `topics.json`, upcasters, dual-publish and subscriber compatibility checks"
project: "module-system"
projectName: "Module System & Swap Tooling"
phase: "P0"
type: "Build"
priority: 1
surfaces: ["Developer"]
milestone: "Kernel and lint live"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-303", "PAP-433"]
blocks: ["PAP-136", "PAP-174", "PAP-443"]
key: "module-system/event-schema-registry"
url: "https://linear.app/paperos/issue/PAP-436/build-the-event-schema-registry-and-versioned-envelopes-aggregated"
source: "Linear snapshot 2026-09-17T15:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T14:50:05.968Z"
model: "claude-opus-5"
effort: "medium"
---

# PAP-436: Build the event schema registry and versioned envelopes: aggregated `topics.json`, upcasters, dual-publish and subscriber compatibility checks

**Model / Effort:** Opus 5 / medium

**Goal**

Make the event bus (PAP-303) swap-safe. Every contract package declares its topics; this issue aggregates them into one schema registry, checks that manifests' `events.publishes|subscribes` agree with the contracts, adds `defineUpcaster()` so a subscriber written for version 2 can read version 1 events during a deprecation window, and `dualPublish()` so a module mid-swap emits both versions. The bus stays Postgres-native and the envelope stays as the contracts document section 3 defines it.

**Scope**

In:

* `packages/kernel/events`: `collectTopics(contracts)` producing `topics.json` (name, version, JSON Schema, publisher module, subscribers, since); committed and drift-checked; served at `/api/v1/events/topics` for staff.
* `defineUpcaster(topic, from, to, fn)` registered in the publisher's contract; the dispatcher applies chains (1 to 2 to 3) before handing an event to a subscriber that declared a newer version.
* `dualPublish(topic, versions[])` writing two outbox rows with the same `causationId`; subscribers idempotent on `event.id` so duplicates during a swap are harmless.
* Boot checks: publishing an undeclared topic fails (already PAP-303); subscribing to a topic no module publishes warns; subscribing with a version newer than any publisher and no upcaster fails.
* Manifest cross-check: `events.publishes` and `subscribes` must match contract declarations (`TOPIC_UNDECLARED` from the manifest validator).

Out: the outbox and dispatcher themselves (PAP-303), webhooks (PAP-222), Kafka or Redis (never).

**Spec**

* Topic versions are integers; a payload schema change that fails the old fixtures is a new version; readers for the old version are kept 30 days (contracts document rule).
* `topics.json` is generated from contract packages, never edited; the docs generator renders it.
* Upcasters are pure, total and tested with the old version's golden fixtures as input and the new version's schema as the oracle.
* Dual-publish is enabled per topic by the swap CLI and disabled at step 7; the registry records the window.
* Ordering per `subject` is preserved across versions (same outbox partition key).

**Interface contract**

Provides: `topics.json`, `collectTopics`, `defineUpcaster`, `dualPublish`, `/api/v1/events/topics`, the boot checks. Consumes: PAP-303 envelope, `defineTopic` and outbox; manifest validator; contract packages' `events.ts`; PAP-43 worker for the dispatcher. Consumed by: every contract package (topic declarations), PAP-136 notification kinds, PAP-174 automations (trigger sources read `topics.json`), PAP-222 webhooks (topic catalogue for tenants), the migration adapter kit, the swap CLI.

**Test plan**

* Unit: upcaster chains, missing chain fails at boot, dual-publish writes two rows with shared `causationId`.
* Integration (compose): publish v1 while a v2 subscriber is registered with an upcaster; the subscriber receives v2 shape; ordering per subject holds under 1,000 events.
* Static: `topics.json` drift check; every topic in every manifest exists in a contract.
* Fixtures: each topic's golden payloads validate; upcasters map old fixtures onto new schemas.

**Definition of done**

* Registry, upcasters, dual-publish and checks merged; `topics.json` committed with the initial catalogue from the contracts document section 3; docs page rendered.
* PAP-303 owner acknowledged the extension in a comment; ADR; Linear comment.

**Edge cases**

* Two modules declare the same topic name: `TOPIC_DUPLICATE` at boot naming both.
* A subscriber declares no version: treated as the current publisher version, warned.
* Upcaster that cannot map a field (new required field with no default): the contract change is a new topic, not a version; the validator says so.
* Replay of historical outbox rows after a version bump: the dispatcher upcasts on read, never rewrites stored rows.

**Dependencies**

Blocked by PAP-303, module-system/manifest-schema. Blocks PAP-136, PAP-174.

**Agent**

Built by Forge. Reviewed by Sentinel.

**Size**

M

**Demo**

Reviewer opens `/api/v1/events/topics` and sees the catalogue with publishers and subscribers; bumps `invoice.paid` to version 2 in a fixture branch without an upcaster and boot fails naming the two subscribers that would break; adds the upcaster and the v1 fixtures pass the v2 schema. Two minutes.
