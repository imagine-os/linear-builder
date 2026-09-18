---
identifier: "PAP-799"
title: "Email broadcast campaigns: one-off sends to a segment with template editor, send-time scheduling, subject-line test, per-campaign stats and compliance gates"
project: "growth"
projectName: "Growth: Marketing, Outreach & CRM"
phase: "P2"
type: "Build"
priority: 4
surfaces: ["Staff"]
milestone: "Campaigns and social"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-404", "PAP-405"]
blocks: []
key: "r4/growth/email-broadcast-campaigns"
url: "https://linear.app/paperos/issue/PAP-799/email-broadcast-campaigns-one-off-sends-to-a-segment-with-template"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:45.447Z"
model: "claude-sonnet-5"
effort: "high"
estimate: 3
dueDate: null
cycle: null
---

# PAP-799: Email broadcast campaigns: one-off sends to a segment with template editor, send-time scheduling, subject-line test, per-campaign stats and compliance gates

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / high — Build M

**Goal**

Deferred to v0.2 by the Execution Schedule (NJ-14 stop-loss 09-27 can reinstate). Not claimable before 10-01.

Sequences (PAP-191) are drip automation for individuals. Newsletters and announcements are one send to many; Mailchimp, Listmonk and [Customer.io](<http://Customer.io>) treat them as a first-class object with their own stats. The provider layer, consent gate and segments already exist; this adds the campaign object and the batching that keeps a 50k send inside warmup caps.

**Scope**

In: `campaign (name, channel: email, segment_id, template_id, status: draft|pending_approval|scheduled|sending|sent|cancelled, scheduled_at, batch_size, stats jsonb)`, `campaign_recipient (campaign_id, contact_id, status, message_id, events)`; audience freeze at schedule time (PAP-195 `freeze`); send worker batching through the PAP-404 provider with warmup caps from PAP-405 and per-recipient `canContact` at send time; subject-line test on 10 percent with winner selection after 2 hours; stats (sent, delivered, opened, clicked, bounced, unsubscribed) from provider webhooks and PAP-800 when present; approval by owner or admin binding a content hash; `_app/marketing/campaigns` list and editor.

Out: SMS broadcasts (TCPA volume rules, v0.3), automation journeys beyond sequences, template marketplace.

**Spec**

* Sending is resumable: `campaign_recipient` rows are claimed with `FOR UPDATE SKIP LOCKED`; a crash resumes without duplicates (unique message per recipient).
* Sandbox: every recipient is rewritten by PAP-370 rules and recorded in the outbound ledger; the live flip is Needs Justin per tenant.
* Unsubscribe headers from the consent centre on every message; the footer is mandatory and cannot be removed in the editor.
* Content agent (PAP-192) may create `pending_approval` campaigns via `ContentDraftPort`.

**Interface contract**

Provides: `campaigns.*`, send worker `campaign.send`, stats dataset `growth.campaignStats`, editor route, event `campaign.sent|failed` (already in the contract catalogue). Consumes: provider and templates (PAP-404), gate and warmup (PAP-405), segments (PAP-195), consent centre, outbound ledger, engagement tracking (soft), approval pattern (PAP-401).

**Definition of done**

* Test-clock integration: a 2,000-recipient fixture campaign sends in warmup-capped batches, 5 percent suppressed recipients skipped with reasons, stats reconcile to recipient rows; crash-and-resume test; all sandbox.
* Playwright editor, schedule, approve; screenshots at 320, 375, 768, 1024, 1280, 1536, 1920 light and dark; axe clean; `docs/growth/campaigns.md`; CHANGELOG.

**Test plan**

* Unit: audience freeze, batching under caps, subject test split and winner rule, stats aggregation, hash binding.
* E2E: build a campaign for a frozen segment, schedule, approve, advance the clock and read stats on the outbound ledger.

**Demo**

Reviewer creates a newsletter to the 'Customers' segment, approves it, advances the clock and reads sent and skipped counts with reasons. Under two minutes.

**Edge cases**

* Segment shrinks after freeze: frozen list wins; new members get nothing.
* Provider outage mid-send: batches retry up to six hours, then `partial` with a report.
* Template variable missing for one contact: that recipient fails with reason, campaign continues.

**Dependencies**

Hard: PAP-404, PAP-405, PAP-195. Soft: PAP-791, PAP-792, PAP-800, PAP-192.

* Soft dependency (round 4): PAP-195 is a soft dependency, not a `blocks` relation, because its milestone (2026-10-01) is later than this issue's (2026-09-30); build against its interface and reconcile when it lands.
  **Agent**

Builder: Beacon (Campaign Composer). Reviewer: Sentinel (Security Auditor for compliance, Edge Case Hunter).

**Size**

M: one session.

*Round 4 critique fix (2026-09-18):* resolved 3 round-4 file keys in this description to Linear identifiers: `r4/growth/consent-compliance-centre` = PAP-791, `r4/growth/email-engagement-tracking` = PAP-800, `r4/growth/outbound-sandbox-ledger` = PAP-792.
*Round 4 critique fix (2026-09-18):* PAP-195 appears in the Hard list above and in a round-4 soft note; it is soft (no `blocks` relation). Read the Hard list without it.
