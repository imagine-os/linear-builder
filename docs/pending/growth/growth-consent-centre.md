---
key: "gap/growth/consent-centre"
title: "Build the consent and marketing compliance centre: preference page, unsubscribe centre, double opt-in, suppression list shared by outreach, notifications and forms, GDPR/CAN-SPAM/TCPA rules"
project: "growth"
parent: null
phase: "P2"
type: "Build"
priority: 2
size: null
surfaces: []
milestone: "Campaigns and social"
intendedState: "Backlog"
blockedBy: ["PAP-187", "PAP-43"]
blocks: ["PAP-191", "PAP-193"]
source: "round2/agent4/pending-issues.json"
linearDocument: "https://linear.app/paperos/document/round-2-pending-issues-growth-13-3fd4406e8012"
status: "folded"
into: "PAP-187"
---

# Build the consent and marketing compliance centre: preference page, unsubscribe centre, double opt-in, suppression list shared by outreach, notifications and forms, GDPR/CAN-SPAM/TCPA rules

> **FOLDED.** Folded into PAP-187 as work package 0 (FIX-5). Do not create; text kept for reference.

**Goal**

Replace three partial consent implementations (PAP-187 stores it, PAP-191 checks it, PAP-193 writes it) with one: a consent record per contact and channel, a shared suppression list, a public preference and unsubscribe centre, double opt-in, and the rule set that decides whether a message may go out under GDPR, CAN-SPAM and TCPA.

**Scope**

In: tables `consent_record`, `suppression_entry`, `consent_purpose`; `canContact(contactId, channel, purpose)`; public routes `/c/:token` (preferences), `/u/:token` (one-click unsubscribe, RFC 8058 POST), double opt-in confirm route; procedures `consent.*`, `suppression.*`; staff pages under `_app/marketing/compliance`; audit export. Out: cookie banners for the marketing site (PAP-221 owns privacy pages), consent for agent data access (PAP-60).

**Spec**

* `consent_record (contact_id, channel: email|sms|push, purpose: marketing|transactional|product_updates, status: granted|denied|pending_double_opt_in|withdrawn, source, evidence jsonb { ip_hash, user_agent_class, form_id, text_shown, timestamp }, version, granted_at, withdrawn_at)`; append-only, current row per `(contact, channel, purpose)` via a view.
* `suppression_entry (tenant_id, kind: email|phone|domain, value_hash, reason: unsubscribe|complaint|hard_bounce|manual|legal, source, created_at)`; global per tenant across sequences, notifications and forms; `suppression.check(values[])` batched.
* `canContact` returns `{ ok, reason }` combining consent, suppression, `do_not_contact`, quiet hours for SMS (TCPA) and the purpose rules: transactional allowed without marketing consent, marketing requires `granted`, SMS marketing requires explicit opt-in with evidence.
* Preference centre: per channel and purpose toggles, "unsubscribe from all", tenant branding, no login required with a signed token per contact; changes write consent records and suppression entries.
* Double opt-in: forms (PAP-169, PAP-193) create `pending_double_opt_in` and send a confirm email through PAP-136 core; unconfirmed after 30 days expires.
* `List-Unsubscribe` and `List-Unsubscribe-Post` headers supplied to PAP-191 and PAP-136; STOP keywords from PAP-191 write suppression here.
* Exports: per-contact consent history for DSAR (PAP-221) and a tenant compliance report dataset.

**Interface contract**

Provides: `canContact`, `consent.record|withdraw|history`, `suppression.add|check|list`, `preferenceLink(contactId)`, `unsubscribeHeaders(contactId, channel)`, routes above, events `consent.changed`, `suppression.added`, dataset `growth.compliance`. Consumes: contacts (PAP-187), notifications (PAP-136 core), forms (PAP-169, PAP-193 write through `consent.record`), rate limiting (PAP-267), theming (PAP-74), jobs (PAP-43). Consumed by PAP-191 (hard), PAP-193, PAP-136, `gap/business-core/recurring-dunning`, PAP-221 exports.

**Definition of done**

* Vitest, integration and Playwright below green.
* Screenshots at 320, 375, 768, 1024, 1280, 1536, 1920 in light and dark for the preference centre (two brands) and the staff compliance page; axe clean.
* `docs/growth/consent.md` with the rule table per jurisdiction; CHANGELOG; Linear comment with a live preference link on the demo tenant.

**Test plan**

* Unit: `canContact` decision table (channel by purpose by status by suppression), token signing and expiry, double opt-in expiry, header generation.
* Integration: unsubscribe POST suppresses across a running PAP-191 sequence and a PAP-136 digest in the same test; form submission with consent creates `pending_double_opt_in` then `granted` on confirm; STOP writes suppression; history export matches records.
* E2E: open the preference link, toggle SMS marketing off, confirm the sequence skips the SMS step; one-click unsubscribe from an email header.
* Visual: matrix above.

**Demo**

Reviewer opens a contact's preference link from the CRM page, turns off marketing email, then enrols the contact in a sequence and watches `canContact` refuse with the reason; finally clicks the one-click unsubscribe from a test email and sees the suppression entry. Under two minutes.

**Edge cases**

* Contact merged: consent records re-pointed, most restrictive status wins.
* Withdrawal then re-grant: new record with fresh evidence; history intact.
* Suppressed domain (whole company opted out): every contact at that domain refused.
* Token leaked: preference page shows no PII beyond masked email; rotate via `preferenceLink`.
* Legal hold: `reason: legal` suppression cannot be removed by staff.

**Dependencies**

PAP-187 (hard), PAP-43 (hard), PAP-136 core, PAP-169, PAP-193, PAP-74, PAP-267. Blocks PAP-191 (suppression), PAP-193 (consent writes).

**Agent**

Builder: Beacon (CRM Builder) with Quill on the rule table. Reviewer: Sentinel (Security Auditor for public routes and PII, Edge Case Hunter).

**Size**

M: a decision function, two public pages and append-only tables.
