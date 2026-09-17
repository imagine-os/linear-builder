---
key: "collab/notifications/slack-channel"
title: "Slack channel and tenant Slack configuration"
project: "collab"
parent: "PAP-136"
phase: "P2"
type: "Build"
priority: 2
size: null
surfaces: ["Customer", "Staff"]
milestone: "Knowledge surfaced everywhere"
intendedState: "Backlog"
blockedBy: []
blocks: []
source: "round2/agent3/pending-issues.json"
linearDocument: null
status: "pending"
---

# Slack channel and tenant Slack configuration

**Goal**

Deliver notifications (PAP-136) to Slack: tenant admins configure an incoming webhook, each kind renders a Block Kit message, deliveries retry through the core, and a revoked webhook is surfaced in settings.

**Scope**

In:

* `tenant_slack_config(tenant_id, webhook_url encrypted, default_channel, kind_channels jsonb, status)`; settings section in `/_app/settings/notifications` (admin only) with "Test send".
* `SlackChannel implements Channel` registered with the core; Block Kit templates per kind in `packages/collab/notifications/templates/slack/`.
* Revoked or failing webhook: `status: broken` after three failures and a banner for admins.
* oRPC `slack.configure`, `slack.test`.

Out: Slack app and OAuth (later), interactive buttons.

**Spec**

* Webhook URL encrypted with the server-side secret helper (data-layer gap; fall back to `SecretStore` from PAP-17 until it lands).
* Templates keep payloads under 40 blocks; links use the deep-link grammar of the source.
* Deliveries recorded in the core's `notification_delivery` with `channel: 'slack'`.

**Interface contract**

Exposes `SlackChannel`, `tenant_slack_config`, procedures above, Block Kit template snapshots. Consumes `Channel { send(notification, recipient) }` interface and `registerChannel()` from the core, secret encryption helper, admin permission `notifications.admin` (PAP-59), settings page slot (sibling 1).

**Definition of done**

* Test webhook receives a Block Kit message for `comment.mentioned` and `issue.needs_justin`; broken webhook shows the banner; Linear comment with a screenshot of the Slack message.

**Test plan**

* Vitest: template snapshots for every kind, block count limit, status transition after three failures.
* Integration: mock Slack server asserts payload schema and returns 410 to trigger `broken`; `callAs(staff)` cannot read the webhook URL.
* Playwright: admin configures the webhook, clicks Test send, sees success; run at 1280.

**Demo**

Paste a test webhook in settings, click Test send, see the message in Slack, revoke the webhook, trigger a mention and watch the broken banner appear. Under two minutes.

**Edge cases**

* Slack rate limit 429: honour `Retry-After` via the core.
* Kind routed to a channel that no longer exists: default channel.
* Webhook URL not on `hooks.slack.com`: rejected.

**Dependencies**

Notification core (hard). Sibling 1, PAP-59, PAP-17 or the secret helper (soft).

**Agent**

Built by Forge (Ops Runner). Reviewed by Sentinel (Security Auditor for the webhook secret).

**Size**

S: one channel adapter and a settings section.
