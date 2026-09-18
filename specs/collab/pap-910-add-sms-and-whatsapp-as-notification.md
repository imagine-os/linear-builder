---
identifier: "PAP-910"
title: "Add SMS and WhatsApp as notification channels on the notification core: Twilio provider shared with outreach, per-kind opt-in, consent and quiet hours, STOP handling and cost metering"
project: "collab"
projectName: "In-App Collaboration & Knowledge"
phase: "P2"
type: "Build"
priority: 4
surfaces: ["Customer"]
milestone: "Knowledge surfaced everywhere"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-136", "PAP-324", "PAP-391", "PAP-404", "PAP-405"]
blocks: []
key: "r4/collab/sms-notification-channel"
url: "https://linear.app/paperos/issue/PAP-910/add-sms-and-whatsapp-as-notification-channels-on-the-notification-core"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:19:53.733Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 2
dueDate: null
cycle: null
---

# PAP-910: Add SMS and WhatsApp as notification channels on the notification core: Twilio provider shared with outreach, per-kind opt-in, consent and quiet hours, STOP handling and cost metering

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Build S

**Goal**

Let notifications reach phones: an `sms` (and `whatsapp`) channel in the PAP-136 notification core reusing the PAP-404 Twilio provider and the PAP-405 compliance rules, opt-in per kind in the preferences page (PAP-323), quiet hours (PAP-324), STOP handling shared with outreach, and cost metering, so booking reminders, approval requests and security alerts can be texted.

**Scope**

In: `NotificationChannel` `sms` and `whatsapp` adapters in `packages/collab/notifications/channels/`: render kind templates to 160-character variants with a short link (PAP-136 templates gain `sms` bodies), send via the PAP-404 provider client, delivery status back to `notification_delivery`. Preferences: phone number verification (OTP via the same provider), per-kind channel toggles restricted to kinds flagged `smsEligible` (reminders, approvals, security alerts; never marketing), quiet hours apply; STOP marks the number suppressed for notifications and outreach alike. Metering `outreach.messages` (PAP-391) with `channel: sms|whatsapp`; tenant daily caps.

Out: Two-way conversations (engagement messaging channels). Bulk campaigns.

**Spec**

* Transactional only: kinds must be flagged `smsEligible`; the flag is reviewed by Sentinel per kind
* Numbers stored E.164, verified, encrypted at rest (PAP-353)
* WhatsApp uses approved templates; falls back to SMS when no template applies

**Interface contract**

Provides: `sms` and `whatsapp` notification channels, phone verification, `smsEligible` kind flag, preference UI additions. Consumes: notification core, inbox and digests (PAP-136, PAP-323, PAP-324), outreach provider and compliance (PAP-404, PAP-405), metering (PAP-391), encryption (PAP-353). Consumed by: engagement booking reminders and surveys, workflows approvals and signature requests, platform-ops status subscribers, security alerts (PAP-356).

**Definition of done**

* Verified phone receives a booking reminder fixture in the Twilio test sandbox; quiet hours defer; STOP suppresses both notifications and outreach; usage metered
* Every new page has a `page.spec.yaml` (PAP-114) that passes the validator, declared loading, empty, error and denied states, and Gate 3 screenshots at 375, 768, 1024 and 1920 in light and dark themes.
* Linear comment on the issue with the evidence links (PR, gate artefacts, recording or report) and the module docs page updated where the interface changed.

**Test plan**

* Unit: template shortening; eligibility; quiet hours.
* Integration: provider send and status webhook with recorded fixtures; STOP propagation.
* Isolation: the PAP-34 cross-tenant harness auto-enrols every new table; one negative case per new oRPC procedure proves `NOT_FOUND` on a foreign tenant row.

**Demo**

Verify a phone in preferences, enable SMS for approvals, submit an expense over threshold and receive the text with a signed approve link.

**Edge cases**

* Number ported or invalid: provider error marks it unverified and falls back to email with a notice
* Module disabled for the tenant (PAP-266): routes return `MODULE_DISABLED` (409), slot fills unmount and the manifest declares the dependency so consumers fail closed rather than half-render.

**Dependencies**

PAP-136, PAP-324 (hard), PAP-404, PAP-405 (hard: shared client and rules), PAP-391, PAP-353 (soft).

**Agent**

Builder: Beacon. Reviewer: Sentinel (Security Auditor).

**Size**

S: half a session.
