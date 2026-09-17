---
identifier: "PAP-191"
title: "Build email and SMS outreach sequences (Resend, Twilio) with warmup and reply detection"
project: "growth"
projectName: "Growth: Marketing, Outreach & CRM"
phase: "P2"
type: "Build"
priority: 4
surfaces: ["Staff"]
milestone: "Campaigns and social"
state: "Backlog"
parent: null
children: ["PAP-404", "PAP-405", "PAP-406"]
blockedBy: ["PAP-43", "PAP-187"]
blocks: []
key: "growth/outreach-sequences"
url: "https://linear.app/paperos/issue/PAP-191/build-email-and-sms-outreach-sequences-resend-twilio-with-warmup-and"
source: "Linear snapshot 2026-09-17T13:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T13:06:11.462Z"
---

# PAP-191: Build email and SMS outreach sequences (Resend, Twilio) with warmup and reply detection

**Goal**

Deferred to v0.2 by the Execution Schedule (NJ-14 stop-loss 09-27 can reinstate). Not claimable before 10-01.

Automate compliant outbound: multi-step email and SMS sequences over Resend and Twilio that enrol CRM contacts, pause on reply, honour consent and quiet hours, warm up sending domains and record every touch as an activity. Sending is sandboxed to an allowlist until Justin flips the tenant flag. Umbrella for three children.

**Scope**

Children (M each, same milestone, Backlog):

* PAP-404 Schema, provider interface with Resend and Twilio adapters, the per-minute scheduler worker, template rendering and idempotency.
* PAP-405 Consent and suppression checks, quiet hours, List-Unsubscribe and STOP handling, warmup stages, bounce and complaint handling, reply detection webhooks.
* PAP-406 Sequence builder, template editor with preview and test send, enrolments grid, domain setup wizard.

Out: purchased data, AI drafting (PAP-192), deliverability dashboards beyond counters, WhatsApp.

**Spec**

Decisions binding all children:

* `outreach_sequence (name, status, channel_mix, settings jsonb)`, `outreach_step (position, channel, delay_minutes, template_id, condition jsonb)`, `outreach_template (subject, body_mjml|body_text, variables, approved_by, version)`, `outreach_enrolment (contact_id, sequence_id, status: active|paused|replied|bounced|unsubscribed|completed|failed, current_step, next_send_at, template_version)`, `outreach_message (enrolment_id, step_id, channel, provider_message_id, status, events jsonb)` unique on `(enrolment_id, step_id)`, `sending_domain (domain, dns_status, warmup_stage, daily_limit, reputation_score)`.
* Provider interface `send`, `verifyWebhook`, `parseEvent`, `parseInbound`; Resend SDK 4.x and Twilio 5.x first; Postmark or SES per PAP-188.
* Worker uses `SELECT ... FOR UPDATE SKIP LOCKED`; consent, `do_not_contact` and the suppression list from PAP-187 work package 0 (`canContact`) are checked at send time.
* Sandbox: `outreach.sandbox = true` rewrites non-allowlisted recipients to `sandbox+<hash>@paperos.test`; flipping it is Needs Justin.
* Warmup caps 20, 50, 100, 250, 500, 1000 per day, advancing after three clean days, regressing on bounce over 2 percent or complaints over 0.1 percent.
* Quiet hours 8am to 9pm recipient local time; contact timezone, then company, then tenant.

**Interface contract**

Provides: `outreach.sequences|steps|templates|enrolments.*`, `outreach.enrol({ sequenceId, contactIds | segmentId })`, `OutreachProvider` interface, inbound route `outreach.inbound`, events `outreach.replied`, `outreach.bounced`, `outreach.unsubscribed`, `outreach_message` rows as `crm_activity kind email|sms`. Consumes: contacts, consent, activities (PAP-187), suppression and preference API (PAP-187 work package 0), secrets (PAP-17), audit (PAP-38), grid (PAP-165), segments (PAP-195, enrol by segment), provider decision (PAP-188). Consumed by PAP-192 templates, PAP-197 (replies open conversations).

**Definition of done**

* All three children Done.
* Integration against Resend and Twilio test credentials in sandbox: one email and one SMS to allowlisted addresses, STOP round trip, recordings attached.
* Screenshots at 320, 375, 768, 1024, 1280, 1536, 1920 in light and dark for builder, enrolments and domain wizard; security sign-off on webhooks and template rendering.
* `docs/growth/outreach.md` with the compliance checklist; CHANGELOG; Linear comment with recording.

**Test plan**

Umbrella `outreach.e2e.spec.ts` with a test clock: build a two-step sequence (email then SMS after one day), enrol three contacts (one with revoked consent, one in a quiet-hours timezone), advance the clock and assert exactly the compliant sends with correct local times; post a Resend inbound reply matching the plus-address token and assert `replied` and a paused enrolment; send a STOP SMS and assert suppression; simulate three clean days and a bounce spike and assert warmup advance then regression; replay a webhook and assert idempotency.

**Demo**

Reviewer builds a two-step sequence, enrols a contact from the allowlist, presses the test-clock "advance one day" button, sees the email and SMS rows with provider ids, replies to the email from their inbox and watches the enrolment pause with the reply as an activity. Under two minutes.

**Edge cases**

* Contact in two sequences: one outbound per day globally unless overridden.
* Unknown timezone: assumption logged on the message.
* Reply from a different address lands in an "Unmatched" list for manual linking.
* Provider outage: retries up to 6 hours, then `failed` without advancing.
* Template edited mid-sequence: enrolments keep their `template_version`.

**Dependencies**

PAP-187 (hard, including its work package 0, the consent centre: hard for suppression and `canContact`; import from branch `PAP-187/wp0-consent-centre` if not merged and stub with `do_not_contact` only if that branch does not exist yet), PAP-43 (hard), PAP-17, PAP-38, PAP-165, PAP-188 (decision), PAP-195 (soft). Feeds PAP-192, PAP-197.

**Agent**

Builder: Beacon (Outreach Sequencer). Reviewer: Sentinel (Security Auditor, Edge Case Hunter for timezones and caps), Quill for compliance docs.

**Size**

L, split into three M children.

**Pending issues**

Bracketed references above are fully specified work packages that Linear refused to create on 2026-09-17 (`USAGE_LIMIT_EXCEEDED`, free-plan issue cap). Their specs live in the project document(s) [growth](<https://linear.app/paperos/document/round-2-pending-issues-growth-13-3fd4406e8012>) and they are created as issues by `round2/agent4/create_issues.py` once the workspace plan is upgraded.
