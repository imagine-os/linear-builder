---
identifier: "PAP-867"
title: "Build two-way conversational messaging: MessagingChannelPort with SMS and WhatsApp (Twilio), threads unified with support conversations, consent and quiet hours, templates and delivery status"
project: "engagement"
projectName: "Scheduling, Messaging & Customer Engagement"
phase: "P2"
type: "Build"
priority: 4
surfaces: ["Staff"]
milestone: "Messaging channels, help center and surveys"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-187", "PAP-353", "PAP-404", "PAP-405", "PAP-410", "PAP-412", "PAP-791", "PAP-862"]
blocks: ["PAP-876"]
key: "r4/engagement/messaging-channels"
url: "https://linear.app/paperos/issue/PAP-867/build-two-way-conversational-messaging-messagingchannelport-with-sms"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:51:22.347Z"
model: "claude-opus-5"
effort: "high"
estimate: 3
dueDate: null
cycle: null
---

# PAP-867: Build two-way conversational messaging: MessagingChannelPort with SMS and WhatsApp (Twilio), threads unified with support conversations, consent and quiet hours, templates and delivery status

**Model / Effort:** Opus 5 (`claude-opus-5`) / high — Build M

**Goal**

Let staff text customers and customers text back inside the same inbox: a `MessagingChannelPort` whose SMS and WhatsApp adapters share the Twilio client with PAP-404 outreach, inbound webhooks that thread into PAP-410 support conversations by phone number and contact, consent and quiet-hour checks from PAP-405 and PAP-187, WhatsApp template management, delivery status, and per-conversation channel switching.

**Scope**

In: `packages/engagement/src/messaging/`: `channel_account` (kind sms|whatsapp|email|in-app, provider, number or sender id, encrypted credentials PAP-353, capabilities), `MessagingChannelPort.send(conversationId, body, attachments)` and `receiveWebhook`; adapters `twilio-sms`, `twilio-whatsapp` (reusing PAP-404 provider client), `email` (delegates to PAP-410), `in-app` (delegates to PAP-411). Threading: inbound by `(channel_account, from)` → existing open conversation within 7 days, else new conversation with contact match by phone (PAP-410 heuristics extended); unknown numbers create a contact with `consent: inbound` (they wrote first). Compliance: outbound checks `canContact(channel)` (PAP-187 WP0), quiet hours (PAP-405), STOP and START handling, WhatsApp 24-hour session window with template fallback, opt-in capture in booking and forms flows. Inbox: channel badge on conversations (PAP-412), composer channel switcher, delivery receipts (queued, sent, delivered, read, failed with reason), MMS and WhatsApp media into PAP-37 files; console page for channel accounts and WhatsApp templates with approval status.

Out: Bulk campaigns (PAP-191 and PAP-799). Voice calls. Native WhatsApp Business onboarding beyond Twilio.

**Spec**

* One Twilio client, two owners: PAP-404 owns sequences, this issue owns conversations; both call `provider.send` and share the suppression list so a STOP anywhere stops everything
* Inbound webhooks verify the Twilio signature, are rate-limited (PAP-304) and enqueue a job; the job is idempotent on the provider message id
* Templates for WhatsApp are stored with their approval status and language; the composer refuses a non-template outside the session window
* Media is scanned (PAP-574 when present) before staff preview; unknown types are downloadable only
* Costs: every message records `outreach.messages` usage (PAP-391) with the channel kind

**Interface contract**

Provides: `MessagingChannelPort` with four adapters, `channel_account`, inbox channel UI, WhatsApp template management, `message.received|sent|failed` events. Consumes: support conversations and inbox (PAP-410, PAP-412), in-app chat (PAP-411), outreach provider and compliance (PAP-404, PAP-405), consent (PAP-187), encryption (PAP-353), files (PAP-37), rate limits (PAP-304), metering (PAP-391). Consumed by: booking reminders with replies ("reply C to confirm"), surveys by SMS, assistant escalation, commerce order updates, PAP-910 (shares adapters).

**Definition of done**

* A customer texts the demo number, the conversation appears in the inbox with the contact matched, staff reply over SMS and switch to WhatsApp template when outside the window; STOP suppresses reminders too; recorded fixtures in CI
* Every new page has a `page.spec.yaml` (PAP-114) that passes the validator, declared loading, empty, error and denied states, and Gate 3 screenshots at 375, 768, 1024 and 1920 in light and dark themes.
* Linear comment on the issue with the evidence links (PR, gate artefacts, recording or report) and the module docs page updated where the interface changed.

**Test plan**

* Unit: threading rules; session window; consent and quiet hours gates; STOP/START parsing in three languages.
* Integration: Twilio signature verification; duplicate webhook idempotency; media ingestion; delivery status updates.
* Isolation: the PAP-34 cross-tenant harness auto-enrols every new table; one negative case per new oRPC procedure proves `NOT_FOUND` on a foreign tenant row.

**Demo**

Text "can I move my appointment?" to the salon demo number; watch it land in the inbox threaded to the right contact; reply from the composer; then show the WhatsApp template picker after the session window closes.

**Edge cases**

* Two contacts share one phone (family): the inbox shows both candidates and staff pick; the choice is remembered for that number
* Provider outage: sends queue with backoff (PAP-43) and the composer shows delayed status; nothing is lost or duplicated
* Module disabled for the tenant (PAP-266): routes return `MODULE_DISABLED` (409), slot fills unmount and the manifest declares the dependency so consumers fail closed rather than half-render.

**Dependencies**

PAP-410, PAP-412 (hard: conversation model and inbox), PAP-404, PAP-405 (hard: shared client and compliance), PAP-187 (hard), PAP-353 (hard), PAP-37, PAP-304, PAP-391 (soft).

**Agent**

Builder: Beacon. Reviewer: Sentinel (Security Auditor).

**Size**

M: one session.

*Round 4 critique fix (2026-09-18):* resolved 3 round-4 file keys in this description to Linear identifiers: `r4/collab/sms-notification-channel` = PAP-910, `r4/data-layer/file-scanning-previews` = PAP-574, `r4/growth/bulk-campaigns` = PAP-799.
