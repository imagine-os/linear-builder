---
identifier: "PAP-405"
title: "Consent and suppression checks, quiet hours, unsubscribe and STOP handling, warmup stages, bounce handling and reply detection"
project: "growth"
projectName: "Growth: Marketing, Outreach & CRM"
phase: "P2"
type: "Build"
priority: 4
surfaces: ["Staff"]
milestone: "Campaigns and social"
state: "Backlog"
parent: "PAP-191"
children: []
blockedBy: ["PAP-404", "PAP-791"]
blocks: ["PAP-406", "PAP-799", "PAP-867", "PAP-900", "PAP-910"]
key: "growth/outreach/compliance-warmup-replies"
url: "https://linear.app/paperos/issue/PAP-405/consent-and-suppression-checks-quiet-hours-unsubscribe-and-stop"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:21:15.310Z"
model: "claude-sonnet-5"
effort: "low"
estimate: 3
dueDate: null
cycle: null
---

# PAP-405: Consent and suppression checks, quiet hours, unsubscribe and STOP handling, warmup stages, bounce handling and reply detection

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / low — Deferred label (excluded from Oct-1 scope)

**Goal**

Make outbound lawful and deliverable: every send passes consent, suppression and quiet-hour checks, recipients can leave in one click, domains warm up automatically and replies stop sequences.

**Scope**

In: send-time gate, List-Unsubscribe (RFC 8058) and footer, STOP and HELP keywords, TCPA quiet hours, warmup state machine on `sending_domain`, bounce and complaint handlers, inbound webhooks and reply matching (`In-Reply-To`, plus-address token, phone), "Unmatched" list. Out: UI (sibling).

**Spec**

* Gate reads consent and `do_not_contact` (PAP-187) and the suppression list from PAP-187 (work package 0) (stub with `do_not_contact` if absent).
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
