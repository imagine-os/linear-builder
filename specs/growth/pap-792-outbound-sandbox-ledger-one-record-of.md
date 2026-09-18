---
identifier: "PAP-792"
title: "Outbound sandbox ledger: one record of every email, SMS, social post and webhook the growth module would send, with the gate decision, for sandbox-only verification"
project: "growth"
projectName: "Growth: Marketing, Outreach & CRM"
phase: "P2"
type: "Infra"
priority: 2
surfaces: ["Developer"]
milestone: "Campaigns and social"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-370", "PAP-790"]
blocks: []
key: "r4/growth/outbound-sandbox-ledger"
url: "https://linear.app/paperos/issue/PAP-792/outbound-sandbox-ledger-one-record-of-every-email-sms-social-post-and"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:44.401Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 2
dueDate: "2026-09-30"
cycle: null
---

# PAP-792: Outbound sandbox ledger: one record of every email, SMS, social post and webhook the growth module would send, with the gate decision, for sandbox-only verification

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Infra S

**Goal**

Every growth Definition of done must be provable without a live send (deny list, Security Model section 4) yet each child records its attempts differently: PAP-404 rewrites recipients, PAP-402 has `dryRun`, PAP-193 logs. One `outbound_attempt` table and a dev page make 'nothing left the building' a query and give reviewers one place to read what would have gone out and why it was allowed or refused.

**Scope**

In: table `outbound_attempt (tenant_id, channel: email|sms|social|webhook|push, provider, recipient_hash, recipient_masked, subject_or_preview, payload_file_id?, gate: { ok, reason }, mode: sandbox|dryRun|live, provider_message_id?, status, source EntityRef, created_at)`; `recordOutbound()` helper called by PAP-370 `sendEmail` (sandbox mode), the PAP-404 provider layer, PAP-402 adapters and PAP-193 notifications; dev route `_app/dev/outbound` (staff, non-production) with filters and payload preview; Vitest matcher `expectNoLiveSend()` reading the table; nightly assertion job on staging that `mode = live` count is zero until NJ approval flags exist.

Out: deliverability analytics, message archive for compliance (PAP-355 retention applies: 30 days).

**Spec**

* Recipient stored as SHA-256 with tenant salt plus a masked display (`j***@e***.com`); payload bodies go to PAP-37 files with 30-day retention, never into the row.
* `mode` is derived, never passed: `live` only when the provider call used a non-sandbox credential, which the credential broker (PAP-300) labels.
* The helper is fire-and-forget on the PAP-43 queue with an idempotency key from the source event so retries do not double count.

**Interface contract**

Provides: `outbound_attempt`, `recordOutbound`, `expectNoLiveSend`, dev route, dataset `growth.outboundAttempts`. Consumes: email package (PAP-370), CRM schema (sibling), jobs (PAP-43), files (PAP-37), credential broker labels (PAP-300, soft). Consumed by PAP-404, PAP-405, PAP-402, PAP-193, PAP-799, PAP-791 tests.

**Definition of done**

* Helper wired into `sendEmail` sandbox path with a test; matcher used by at least one PAP-370 test; dev page screenshots at 375, 1024, 1920.
* `docs/growth/sandbox.md` explaining how a reviewer proves no live send; CHANGELOG; comments on PAP-404 and PAP-402 pointing at the helper.

**Test plan**

* Unit: hashing and masking, mode derivation, idempotency, retention purge.
* E2E: trigger a sandbox email from the demo tenant and read it on `_app/dev/outbound` with `gate.ok = true`; trigger a suppressed one and read the refusal reason.

**Demo**

Reviewer sends a test receipt in sandbox, opens the outbound page and sees the masked recipient, the preview and `mode: sandbox`. Under one minute.

**Edge cases**

* Provider returns success but the row insert fails: send is not retried (money-like semantics); a `outbound.record_failed` telemetry event fires.
* Production tenant: the dev route is hidden and the table is still written for audit.

**Dependencies**

Hard: PAP-370, PAP-790. Soft: PAP-43, PAP-37, PAP-300.

**Agent**

Builder: Beacon (Outreach Sequencer). Reviewer: Sentinel (Security Auditor).

**Size**

S: half a session.

*Round 4 critique fix (2026-09-18):* resolved 3 round-4 file keys in this description to Linear identifiers: `r4/growth/consent-compliance-centre` = PAP-791, `r4/growth/crm-schema-routers-page-specs` = PAP-790, `r4/growth/email-broadcast-campaigns` = PAP-799.
