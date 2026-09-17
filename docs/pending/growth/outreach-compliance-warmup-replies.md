---
key: "growth/outreach/compliance-warmup-replies"
title: "Consent and suppression checks, quiet hours, unsubscribe and STOP handling, warmup stages, bounce handling and reply detection"
project: "growth"
parent: "PAP-191"
phase: "P2"
type: "Build"
priority: 2
size: "M"
surfaces: []
milestone: "Campaigns and social"
intendedState: "Backlog"
blockedBy: []
blocks: []
source: "round2/agent4/pending-issues.json"
linearDocument: "https://linear.app/paperos/document/round-2-pending-issues-growth-13-3fd4406e8012"
identifier: "PAP-405"
status: "created"
createdAt: "2026-09-17"
---

# Consent and suppression checks, quiet hours, unsubscribe and STOP handling, warmup stages, bounce handling and reply detection

**Goal**

Make outbound lawful and deliverable: every send passes consent, suppression and quiet-hour checks, recipients can leave in one click, domains warm up automatically and replies stop sequences.

**Scope**

In: send-time gate, List-Unsubscribe (RFC 8058) and footer, STOP and HELP keywords, TCPA quiet hours, warmup state machine on `sending_domain`, bounce and complaint handlers, inbound webhooks and reply matching (`In-Reply-To`, plus-address token, phone), "Unmatched" list. Out: UI (sibling).

**Spec**

* Gate reads consent and `do_not_contact` (PAP-187) and the suppression list from `gap/growth/consent-centre` (stub with `do_not_contact` if absent).
* Quiet hours 8am to 9pm recipient local time; timezone fallback contact, company, tenant, logged on the message.
* Warmup caps 20, 50, 100, 250, 500, 1000; advance after three clean days; regress on bounce over 2 percent or complaints over 0.1 percent.
* Hard bounce sets `email_status: invalid` and stops enrolments; complaint adds to suppression; webhook signatures verified (`svix`, `X-Twilio-Signature`).

**Interface contract**

Provides: `canSend(contact, channel) => { ok, reason }`, warmup job, inbound route, events `outreach.replied|bounced|unsubscribed`. Consumes: worker child, consent centre gap, PAP-187, PAP-197 (replies open conversations, soft).

**Definition of done**

* Timezone fixtures for five zones; warmup advance and regression tests; STOP round trip in sandbox; three reply-matching strategies tested.

**Test plan**

* Unit: gate reasons, quiet hours, warmup, matching.
* Integration: Resend inbound and Twilio STOP webhooks with signatures; replay idempotent.

**Demo**

Send to a contact in a quiet-hours zone and watch it defer; reply from a mailbox and see the enrolment pause.

**Edge cases**

* Forwarded reply from a different address lands in Unmatched; contact in two sequences capped at one send per day.

**Dependencies**

Worker child (hard), consent centre gap (hard for suppression), PAP-187.

**Agent**

Builder: Beacon (Outreach Sequencer). Reviewer: Sentinel (Edge Case Hunter), Quill on compliance.

**Size**

M: compliance logic.
