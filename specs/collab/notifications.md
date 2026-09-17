---
identifier: "PAP-136"
title: "Build a notification center (in-app, email, Slack) with per-audience preferences"
project: "collab"
projectName: "In-App Collaboration & Knowledge"
phase: "P2"
type: "Build"
priority: 2
surfaces: ["Customer", "Staff"]
milestone: "Comments and canvas"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-131", "PAP-43"]
blocks: []
key: "collab/notifications"
url: "https://linear.app/paperos/issue/PAP-136/build-a-notification-center-in-app-email-slack-with-per-audience"
source: "plan/specs/bucket-4.json (round-1 canonical spec JSON)"
---

# PAP-136: Build a notification center (in-app, email, Slack) with per-audience preferences

**Goal**

Deliver mentions, replies, resolutions, review results and release news to people where they are: an in-app inbox with a live badge, email through Resend and Slack messages, governed by per-user and per-audience preferences with digests and quiet hours. Justin's Needs Justin queue and comment mentions both flow through this one system.

**Scope**

In:
- Drizzle schema `packages/db/src/schema/notifications.ts`: `notification` (`id uuidv7`, `tenant_id`, `user_id`, `kind`, `title`, `body_md`, `link`, `source jsonb { type, id }`, `actor_id`, `actor_kind`, `seen_at`, `read_at`, `archived_at`, `created_at`); `notification_preference` (`user_id`, `tenant_id`, `kind`, `channels jsonb { inApp, email, slack }`, `digest: none|hourly|daily`, `quiet_hours jsonb { start, end, tz }`); `notification_delivery` (`notification_id`, `channel`, `status: queued|sent|failed|suppressed`, `attempts`, `provider_id`, `error`, `sent_at`); `tenant_slack_config` (`tenant_id`, `webhook_url` encrypted, `default_channel`).
- Kinds registry `packages/collab/notifications/kinds.ts`: `comment.mentioned`, `comment.replied`, `thread.resolved`, `issue.needs_justin`, `review.gate_failed`, `review.ready`, `release.candidate`, `changelog.published`, `agent.blocked`, `import.finished`; each with default channels per audience kind and a template (React Email 3 for email, Block Kit JSON for Slack, markdown for in-app).
- Event bus: `packages/core/events` `emit(kind, { recipients: userId[] | audience, payload })`; producers include `collab/comments`, `pm-linear/webhooks`, `quality/release-train`, `collab/changelog`.
- Worker with `pg-boss` 10 on the API host: expands recipients, applies preferences and quiet hours, writes `notification` rows, enqueues channel deliveries with retry (3 attempts, exponential backoff), builds hourly and daily digests per user, collapses bursts (same kind and source within 10 minutes becomes one notification with a count).
- Channels: in-app via Electric shape on `notification` for the current user (`realtime/record-sync`) powering the bell badge, popover (latest 10, mark read, archive) and `/_app/inbox` (filters by kind, unread, grouped by day); email via Resend with per-tenant sender and one-click unsubscribe link per kind (JWT token); Slack via tenant incoming webhook.
- Preferences UI `/_app/settings/notifications`: matrix of kinds by channels, digest selector, quiet hours, test send.

Out: push notifications on mobile and desktop (`app-shell/tauri-mobile` later), SMS, marketing email (`growth/outreach-sequences`), Linear-side notifications.

**Spec**

- Recipient expansion for `audience` uses `identity/audience-model` segments; capped at 500 recipients per event, above that a digest-only mode.
- Suppression rules: actor never notified of own action; mention of a user without access to the source is suppressed with `status: suppressed`; unsubscribed kind is suppressed, not failed.
- Idempotency key `(kind, source, recipient, bucket)` prevents duplicates on retries.
- Email templates render with tokens from `design-system/tokens` inlined; plain-text alternative generated.
- Latency target: in-app under 2 s from emit; email under 60 s outside digests.

**Definition of done**

- Vitest: preference resolution, quiet hours across timezones, collapse and digest grouping, idempotency, template rendering snapshots (email HTML and Slack JSON).
- Integration: a comment mention produces an in-app notification in a second browser context within 2 s, an email captured by a Resend test key (or Mailpit in CI) and a Slack message to a test webhook (link or screenshot).
- Playwright: inbox and preferences at 320, 375, 768, 1024, 1280, 1536 and 1920 in light and dark; unsubscribe link works.
- axe clean; `docs/collab/notifications.md` including how to add a kind; CHANGELOG entry; Linear comment with screenshots and delivery logs.
- `issue.needs_justin` delivers to Justin's configured channels with the batching rule from `pm-linear/justin-queue`.

**Edge cases**

- User in two tenants with different preferences: preferences are per tenant; global fallback row when unset.
- Resend rate limit or outage: deliveries stay queued up to 24 h, then fail with alert to Ops (`data-layer/observability`).
- Quiet hours spanning midnight and DST changes: computed with `@date-fns/tz`; test cases included.
- Slack webhook revoked: delivery fails; tenant admin sees a banner in settings.
- Digest with 300 items: truncated to 50 with a link to the inbox.
- Deleted source (thread removed): notification stays with "no longer available" on click.

**Dependencies**

`collab/comments` (hard, first producer). `data-layer/api-layer`, `realtime/record-sync` (fallback polling), `identity/audience-model`, `app-shell/env-config` for provider keys. Consumed by `pm-linear/justin-queue`, `quality/release-train`, `collab/changelog`, `migration/import-framework`.

**Agent**

Built by Nova with Forge (Ops Runner) on the worker and providers. Reviewed by Sentinel (Security Auditor for unsubscribe tokens and secrets, Visual Inspector) and Beacon for email deliverability.

**Size**

L: three channels, digests, preferences and a queue worker.
