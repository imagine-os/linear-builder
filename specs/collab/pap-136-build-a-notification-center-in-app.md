---
identifier: "PAP-136"
title: "Build a notification center (in-app, email, Slack) with per-audience preferences"
project: "collab"
projectName: "In-App Collaboration & Knowledge"
phase: "P1"
type: "Build"
priority: 1
surfaces: ["Staff"]
milestone: "Comments and canvas"
state: "Backlog"
parent: null
children: ["PAP-725", "PAP-324", "PAP-325", "PAP-323"]
blockedBy: ["PAP-43", "PAP-131", "PAP-302", "PAP-303", "PAP-319", "PAP-436", "PAP-555", "PAP-556", "PAP-564", "PAP-565"]
blocks: ["PAP-513", "PAP-639", "PAP-795", "PAP-807", "PAP-849", "PAP-852", "PAP-855", "PAP-859", "PAP-865", "PAP-869", "PAP-870", "PAP-873", "PAP-874", "PAP-879", "PAP-880", "PAP-895", "PAP-910"]
key: "collab/notifications"
url: "https://linear.app/paperos/issue/PAP-136/build-a-notification-center-in-app-email-slack-with-per-audience"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:28:41.406Z"
model: null
effort: null
estimate: null
dueDate: "2026-09-29"
cycle: null
---

# PAP-136: Build a notification center (in-app, email, Slack) with per-audience preferences

**Model / Effort:** set on children (umbrella is never claimed)

**Goal**

Deliver mentions, review results, release news and Justin's decisions where people are: a kinds registry and worker that turn domain events into notification rows, in-app and email channels, then an inbox, preferences with digests and quiet hours, and Slack. Re-phased to P1 because PAP-94, PAP-88 and PAP-89 deliver through it; work package 1 must not depend on comments.

**Scope**

Work packages (build in order; each becomes a child issue once the Linear issue limit is lifted, see the pinned comment):

1. **Notification core** — schema `notification`, `notification_preference`, `notification_delivery`; kinds registry (`issue.needs_justin`, `review.gate_failed`, `review.ready`, `release.candidate`, `changelog.published`, `agent.blocked`, `import.finished`, `comment.mentioned`, `comment.replied`, `thread.resolved`) with default channels per audience and templates; pg-boss worker (PAP-43) expanding recipients, applying preferences, writing rows and enqueuing deliveries with 3 retries; `InAppChannel` and `EmailChannel` (React Email via PAP-235, per-kind one-click unsubscribe JWT). Depends only on PAP-43 and the event bus.
2. **Inbox UI, bell badge and preferences page** — bell popover (latest 10), `/_app/inbox`, `/_app/settings/notifications` matrix; live badge via Electric shape (PAP-143) with polling fallback.
3. **Digests, quiet hours and burst collapse** — hourly and daily digest jobs, `quiet_hours` with `@date-fns/tz`, same-kind-same-source collapse within 10 minutes, per-tenant preference rows with a global fallback.
4. **Slack channel and tenant configuration** — `tenant_slack_config` with encrypted webhook, Block Kit templates, revoked-webhook banner.

Out: push (planned realtime push transport), SMS, marketing email (PAP-191), Linear-side notifications.

**Spec**

* Actor never notified of own action; recipients without access to the source are `suppressed`; idempotency key `(kind, source, recipient, bucket)`.
* In-app row within 2 s of emit; email within 60 s outside digests; `issue.needs_justin` applies the PAP-94 batching rule.
* Digests cap at 50 items; recipient expansion capped at 500.

*Round 4 amendment (2026-09-18):*
Work package 1 is the child issue PAP-725 (Opus 5 / high, blocked by PAP-43 and PAP-303 only). Because PAP-235 is Deferred, the `EmailChannel` ships a plain-HTML fallback template and switches to the PAP-235 kit when it lands. The `notification` row stores `ActorRef` (PAP-302) for the actor and `EntityRef` for the source, per Contracts §2.

**Interface contract**

Exposes: `Notification`, `NotificationKind`, `defineKind({ id, audiences, defaultChannels, template })`, `registerChannel(name, impl)`, `Channel { send(n, recipient) -> DeliveryResult }`, `notify(kind, { recipients, payload })`, `resolvePreferences(userId, tenantId, kind)`; oRPC `notifications.list|markRead|archive`, `preferences.get|set`, `slack.configure|test`; components `NotificationBell`, `InboxList`, `PreferenceMatrix`; unsubscribe route `/n/unsubscribe/:token`; tables above. Consumes: `emit()`/`subscribe()` from `packages/core/events` (planned; until then an in-process emitter with the same signature in `packages/collab/notifications/bus.ts`), `defineJob` (PAP-43), audience segments (PAP-55), `renderEmail` (PAP-235), email adapter (planned `packages/email`, else Resend with allowlist and Mailpit), shape subscriptions (PAP-143), producers PAP-131, PAP-97, PAP-88, PAP-133, PAP-199, `SecretStore` (PAP-17) for the webhook.

* Contract source: [Interface & Data Contracts](<https://linear.app/paperos/document/paperos-interface-and-data-contracts-d40e6a4d227c>) §2 row "Notification" (`notification`, `notification_preference`, `notification_delivery`; kinds registry; idempotency on `(kind, source, recipient, bucket)`; produced by subscribing to the event bus); §3 (envelope and the topics this consumes: `issue.needs_justin`, `review.gate_failed`, `review.ready`, `release.candidate`, `comment.created|mentioned|resolved`, `changelog.published`, `import.finished`, `payment.failed`); §1 (`Principal` audiences from PAP-55, `ActorRef` on the notification row); §6 row "Domain event envelope". The interim in-process emitter in `packages/collab/notifications/bus.ts` must use the §3 envelope shape so the move to `@paperos/core/events` is a one-import change.

**Definition of done**

* Work package 1 alone: a `review.gate_failed` event produces an in-app row and a Mailpit email in CI; `issue.needs_justin` reaches Justin with batching.
* All four merged: inbox and preferences screenshots at the seven widths in light and dark; a Slack test message delivered.
* axe clean; `docs/collab/notifications.md` including how to add a kind; CHANGELOG entry; Linear comment with screenshots and delivery logs.

**Test plan**

* Vitest: kind registry validation, recipient expansion cap, suppression rules, idempotency on retry, preference resolution matrix, quiet hours across midnight and DST, collapse and digest grouping, template snapshots (email HTML, in-app markdown, Block Kit).
* Integration (Postgres, pg-boss, Mailpit, mock Slack): emit each kind, assert row within 2 s and email within 60 s; provider failure retries three times then `failed`; `callAs(userB)` cannot read userA's rows; Slack 410 marks the webhook broken.
* Playwright, two contexts: mention → badge within 2 s, mark read; switch a kind to daily digest and run the job through the `/__test` clock (PAP-240); unsubscribe link suppresses the next email; run at 375 and 1280.
* Visual: Gate 3 baselines for inbox and settings at the seven widths.

**Demo**

Run `pnpm notify:demo review.gate_failed --to justin`, watch the bell badge and the Mailpit email; open settings, move mentions to a daily digest, click Slack “Test send” and see the message land. Under two minutes.

**Edge cases**

* Provider outage: queued up to 24 h, then failed with an ops alert (PAP-40).
* Deleted source: kept with "no longer available"; digest of 300: truncated to 50.

**Dependencies**

PAP-43 (hard) for work package 1; PAP-131 (relation kept; first comment producer, needed only for work package 2's mention flows). Soft: PAP-55, PAP-235, PAP-143, PAP-240, PAP-17, planned event bus and email package (data-layer). Consumed by PAP-94, PAP-88, PAP-89, PAP-133, PAP-199, PAP-97.

**Agent**

Built by Forge (Ops Runner) for the core and Slack with Nova on inbox and preferences. Reviewed by Sentinel (Security Auditor for unsubscribe tokens and the webhook secret, Visual Inspector) and Beacon for deliverability.

**Size**

L, planned as four work packages (M, M, S, S) that become child issues once the issue limit is lifted.

*Round 4 critique fix (2026-09-18):* resolved 1 round-4 file key in this description to Linear identifiers: `r4/collab/notification-core` = PAP-725.
