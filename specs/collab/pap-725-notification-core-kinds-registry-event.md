---
identifier: "PAP-725"
title: "Notification core: kinds registry, event-bus subscriber worker, preference resolution, in-app and email channels"
project: "collab"
projectName: "In-App Collaboration & Knowledge"
phase: "P1"
type: "Build"
priority: 1
surfaces: ["Customer"]
milestone: "Comments and canvas"
state: "Backlog"
parent: "PAP-136"
children: []
blockedBy: ["PAP-43", "PAP-131", "PAP-302", "PAP-303", "PAP-319", "PAP-436", "PAP-555", "PAP-556", "PAP-564", "PAP-565"]
blocks: ["PAP-323", "PAP-324", "PAP-325", "PAP-513", "PAP-639", "PAP-726", "PAP-730", "PAP-736", "PAP-795", "PAP-807", "PAP-849", "PAP-852", "PAP-855", "PAP-859", "PAP-865", "PAP-869", "PAP-870", "PAP-873", "PAP-874", "PAP-879", "PAP-880", "PAP-895"]
key: "r4/collab/notification-core"
url: "https://linear.app/paperos/issue/PAP-725/notification-core-kinds-registry-event-bus-subscriber-worker"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:20:21.304Z"
model: "claude-opus-5"
effort: "high"
estimate: 3
dueDate: "2026-09-29"
cycle: null
---

# PAP-725: Notification core: kinds registry, event-bus subscriber worker, preference resolution, in-app and email channels

**Model / Effort:** Opus 5 (`claude-opus-5`) / high — Build M

**Goal**

Ship work package 1 of PAP-136, the only package without a child issue: tables, kinds registry, worker and the first two channels that turn domain events into notification rows. `issue.needs_justin` (PAP-94), `review.gate_failed` and `release.candidate` (PAP-88, PAP-89) deliver through this before comments exist, so it depends on jobs and the event bus only, never on PAP-131.

**Scope**

In: `packages/db/src/schema/notifications.ts` (`notification`, `notification_preference`, `notification_delivery` per Contracts §2, `ActorRef` on the row); `packages/collab/notifications/{kinds,worker,channels,preferences}.ts`; `InAppChannel`, `EmailChannel`; ten seed kinds; `pnpm notify:demo`; core sections of `docs/collab/notifications.md`. Out: inbox UI (PAP-323), digests and quiet hours (PAP-324), Slack (PAP-325), push (PAP-381), marketing email (PAP-191).

**Spec**

* Kinds registry: `defineKind({ id, audiences, defaultChannels, template, batch? })` for `issue.needs_justin`, `review.gate_failed`, `review.ready`, `release.candidate`, `changelog.published`, `agent.blocked`, `import.finished`, `comment.mentioned`, `comment.replied`, `thread.resolved`; a kind naming an unregistered topic fails at boot (PAP-303).
* Worker: pg-boss job `notifications.dispatch` (PAP-43) subscribed through `subscribe()` from `@paperos/core/events`; expands recipients (cap 500), drops the actor, marks recipients failing `can()` on the source `suppressed`, writes rows idempotent on `(kind, source, recipient, bucket)`, enqueues one `notification_delivery` per channel with 3 retries and backoff.
* `issue.needs_justin` applies the PAP-94 batching rule (`batch: { window: '15m', max: 5 }`).
* Channels: `Channel { id, send(n, recipient) -> DeliveryResult }`; `InAppChannel` writes the row and emits `notification.sent`; `EmailChannel` uses `packages/email` (PAP-370) when merged, else Resend with allowlist and Mailpit; plain-HTML fallback template because PAP-235 is Deferred; per-kind unsubscribe JWT at `/n/unsubscribe/:token` (24 h, single use).
* Preference resolution: per-tenant row, global row, kind default; `resolvePreferences(userId, tenantId, kind) -> { channels[], digest, quietHours }`, columns PAP-324 extends.
* Budget: in-app row within 2 s, email within 60 s. RLS: recipients read own rows, `owner|admin` read tenant rows, agents only rows addressed to them.

**Interface contract**

Provides: `Notification`, `NotificationKind`, `defineKind`, `registerChannel`, `Channel`, `notify`, `resolvePreferences`, tables above, topic `notification.sent` v1, unsubscribe route, `pnpm notify:demo`; exported as `NotificationPort` in `@paperos/contract-collab` (PAP-474). Consumes: `subscribe()` (PAP-303), `defineJob` (PAP-43), `ActorRef` (PAP-302), audiences (PAP-55), `can()` (PAP-59), email package (PAP-370, soft), `SecretStore` (PAP-17). Consumed by: PAP-323, PAP-324, PAP-325, PAP-94, PAP-88, PAP-89, PAP-97, PAP-133, PAP-199.

**Definition of done**

* Migration applied on staging; RLS harness (PAP-34) shows user B never reads user A's rows.
* A `review.gate_failed` event produces an in-app row within 2 s and a Mailpit email within 60 s in CI; five `issue.needs_justin` events inside 15 minutes produce one batched row.
* Unsubscribe link suppresses the next email for that kind only; `docs/collab/notifications.md` explains how to add a kind; CHANGELOG entry; Linear comment with delivery logs.

**Test plan**

* Unit: kind validation, recipient cap, actor exclusion, suppression on `can()` denial, idempotency on retry, preference fallback order, unsubscribe JWT expiry and single use, template snapshots.
* Integration (Postgres, pg-boss, Mailpit): emit each kind and assert row and email; provider 500 retries three times then `failed`; `callAs(userB)` cannot list userA's rows; boot with an unregistered topic fails.
* E2E: bell count through PAP-323 once merged; until then `pnpm notify:demo` plus an oRPC `notifications.list` smoke.

**Demo**

Run `pnpm notify:demo review.gate_failed --to justin`, see the Mailpit email and the `notifications.list` row; fire five `issue.needs_justin` events and see one batched row. Under two minutes.

**Edge cases**

* Provider outage: deliveries queue up to 24 h, then `failed` with an ops alert (PAP-40).
* Source deleted before delivery: row kept with `sourceMissing: true`.
* Recipient in two tenants: separate rows and preference lookups.
* Outbox replay (at-least-once): second write is a no-op by idempotency key.
* Kind registered by a disabled module (PAP-266): worker skips with a debug log.

**Dependencies**

Hard: PAP-43, PAP-303, PAP-302. Soft: PAP-370 (Resend fallback), PAP-55, PAP-59, PAP-17, PAP-240. Blocks PAP-323, PAP-324, PAP-325; consumed by PAP-94, PAP-88, PAP-89, PAP-97.

**Agent**

Builder: Forge (Ops Runner) with Nova on the kinds registry. Reviewer: Sentinel (Security Auditor: RLS, unsubscribe tokens, suppression).

**Size**

M: one session.
