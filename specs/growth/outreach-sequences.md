---
identifier: "PAP-191"
title: "Build email and SMS outreach sequences (Resend, Twilio) with warmup and reply detection"
project: "growth"
projectName: "Growth: Marketing, Outreach & CRM"
phase: "P2"
type: "Build"
priority: 2
surfaces: ["Staff"]
milestone: "Campaigns and social"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-187", "PAP-43"]
blocks: []
key: "growth/outreach-sequences"
url: "https://linear.app/paperos/issue/PAP-191/build-email-and-sms-outreach-sequences-resend-twilio-with-warmup-and"
source: "plan/specs/bucket-7.json (round-1 canonical spec JSON)"
---

# PAP-191: Build email and SMS outreach sequences (Resend, Twilio) with warmup and reply detection

**Goal**

Automate compliant outbound: multi-step email and SMS sequences over Resend and Twilio that enrol CRM contacts, pause on reply, honour consent and quiet hours, warm up new sending domains, and record every touch as a CRM activity. Sending is sandboxed (allowlisted recipients) until Justin flips the tenant flag.

**Scope**

In:
- Schema `packages/growth/src/outreach/schema.ts`: `outreach_sequence` (`name`, `status`, `channel_mix`, `settings jsonb` for quiet hours, timezone mode, daily cap), `outreach_step` (`position`, `channel: email|sms`, `delay_minutes`, `template_id`, `condition jsonb`), `outreach_template` (`subject`, `body_mjml|body_text`, variables, `approved_by`), `outreach_enrolment` (`contact_id`, `sequence_id`, `status: active|paused|replied|bounced|unsubscribed|completed|failed`, `current_step`, `next_send_at`), `outreach_message` (`enrolment_id`, `step_id`, `channel`, `provider_message_id`, `status`, `events jsonb`), `sending_domain` (`domain`, `dns_status`, `warmup_stage`, `daily_limit`, `reputation_score`).
- Providers: Resend Node SDK 4.x (send, domains, webhooks), Twilio Node 5.x (Messaging Service, status callbacks, inbound webhook); provider interface `packages/growth/src/outreach/providers/` so Postmark or SES can be added per `growth/growth-research`.
- Worker on pg-boss: every minute selects due enrolments, evaluates step conditions, renders templates (Handlebars-style variables from contact, company, deal), checks consent and `do_not_contact`, enforces daily and warmup caps, sends, records `outreach_message` and a `crm_activity`.
- Reply detection: Resend inbound webhook and Twilio inbound SMS route to `outreach.inbound`; match by `In-Reply-To`/`References`, plus-address token `reply+<enrolment>@`, or phone; on match set `replied`, stop the sequence, create an activity and (later) a support conversation (`growth/support-inbox`).
- Compliance: List-Unsubscribe headers (one-click RFC 8058), footer with physical address, STOP/HELP keyword handling for SMS, TCPA quiet hours 8am-9pm recipient local time, suppression list per tenant.
- UI: sequence builder (steps list with delay editors and template picker), enrolment table (grid view), template editor with live preview and test send, domain setup wizard showing DNS records.

Out: cold-data purchase, AI writing (`growth/content-agent` drafts templates), deliverability analytics dashboard beyond counters, WhatsApp.

**Spec**

- Sandbox mode: tenant setting `outreach.sandbox=true` (default) restricts recipients to `settings.allowlist` and rewrites others to `sandbox+<hash>@paperos.test`; flipping it is `Needs Justin`.
- Warmup schedule: stage caps 20, 50, 100, 250, 500, 1000 per day, advancing after 3 clean days (bounce under 2 percent, complaint under 0.1 percent); regression drops a stage.
- Idempotency: `outreach_message` unique on `(enrolment_id, step_id)`; worker uses `SELECT ... FOR UPDATE SKIP LOCKED`.
- Webhook signatures verified (Resend `svix` headers, Twilio `X-Twilio-Signature`); events appended to `events jsonb` and mapped to status.
- Bounce (hard) sets contact `email_status: invalid` and stops all enrolments; complaint adds to suppression.
- Templates render in a sandboxed renderer with an allowlist of variables; missing variable fails the step in preview, not at send.

**Definition of done**

- Vitest: scheduler selection, condition evaluation, quiet hours across timezones (fixtures for 5 zones), warmup advancement and regression, consent gating, webhook signature verification, reply matching by three strategies.
- Integration test against Resend and Twilio test credentials in sandbox mode: one email and one SMS delivered to allowlisted addresses; STOP round trip; recordings attached.
- Playwright: build a two-step sequence, enrol a contact, fast-forward clock (test hook), see messages and a reply pause; screenshots at 320, 375, 768, 1024, 1280, 1536 and 1920 in light and dark for builder, enrolments and domain wizard.
- Security review sign-off on webhook endpoints and template rendering.
- `docs/growth/outreach.md` incl. compliance checklist; CHANGELOG entry; Linear comment with demo recording.

**Edge cases**

- Contact enrolled in two sequences: allowed but a global per-contact cap of one outbound per day unless overridden.
- Contact timezone unknown: fall back to company, then tenant timezone; log the assumption on the message.
- Reply arrives from a different address (forwarded): unmatched inbound lands in an "Unmatched" inbox for manual linking.
- Provider outage: step retried with backoff up to 6 h, then marked `failed` without advancing.
- Template edited while enrolments are mid-sequence: existing enrolments keep the version they started with (`template_version`).
- Daily cap reached mid-batch: remaining sends roll to next window, never dropped.

**Dependencies**

`growth/crm-model` (hard: contacts, consent, activities). `app-shell/env-config` for secrets, `data-layer/audit-log`, `tables/grid-view` for enrolment table. Sequencing templates will be drafted by `growth/content-agent`; replies feed `growth/support-inbox`. Decision on provider set from `growth/growth-research`.

**Agent**

Built by Beacon (Outreach Sequencer). Reviewed by Sentinel (Security Auditor, Edge Case Hunter for timezones and caps) and Quill for compliance docs.

**Size**

L: two channels, worker, webhooks, warmup and compliance logic each carry real risk.
