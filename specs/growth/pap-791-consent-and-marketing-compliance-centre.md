---
identifier: "PAP-791"
title: "Consent and marketing compliance centre: consent records per channel and purpose, shared suppression list, canContact, public preference and one-click unsubscribe routes, double opt-in"
project: "growth"
projectName: "Growth: Marketing, Outreach & CRM"
phase: "P1"
type: "Build"
priority: 2
surfaces: ["Customer"]
milestone: "CRM core"
state: "Backlog"
parent: "PAP-187"
children: []
blockedBy: ["PAP-43", "PAP-370", "PAP-565", "PAP-790"]
blocks: ["PAP-189", "PAP-190", "PAP-191", "PAP-193", "PAP-194", "PAP-195", "PAP-197", "PAP-401", "PAP-404", "PAP-405", "PAP-410", "PAP-485", "PAP-765", "PAP-793", "PAP-804", "PAP-863", "PAP-867", "PAP-897"]
key: "r4/growth/consent-compliance-centre"
url: "https://linear.app/paperos/issue/PAP-791/consent-and-marketing-compliance-centre-consent-records-per-channel"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:44.269Z"
model: "claude-opus-5"
effort: "high"
estimate: 3
dueDate: "2026-09-29"
cycle: null
---

# PAP-791: Consent and marketing compliance centre: consent records per channel and purpose, shared suppression list, canContact, public preference and one-click unsubscribe routes, double opt-in

**Model / Effort:** Opus 5 (`claude-opus-5`) / high — Build M

**Goal**

Formerly PAP-187 work package 0 (folded in 2026-09-17, FIX-5), now a child so it can be claimed and cited on its own. One consent record per contact, channel and purpose, one suppression list, a `canContact` decision function and public preference and unsubscribe pages give PAP-405, PAP-193, PAP-136 and finance reminders a single lawful gate under GDPR, CAN-SPAM and TCPA.

**Scope**

In: `packages/growth/src/consent/`: tables `consent_record (contact_id, channel: email|sms|push, purpose: marketing|transactional|product_updates, status: granted|denied|pending_double_opt_in|withdrawn, source, evidence jsonb, version, granted_at, withdrawn_at)` append-only with a current-row view, `suppression_entry (kind: email|phone|domain, value_hash, reason: unsubscribe|complaint|hard_bounce|manual|legal, source)`; `canContact(contactId, channel, purpose) -> { ok, reason }`; public routes `/c/:token` preference centre and `/u/:token` one-click unsubscribe (RFC 8058 POST) plus double opt-in confirm; `unsubscribeHeaders(contactId, channel)`; staff pages `_app/marketing/compliance`; dataset `growth.compliance`; DSAR export of consent history for PAP-221.

Out: cookie banners for marketing sites (PAP-221), consent for agent data access (PAP-60), outreach sending (PAP-404), the schema tables of the sibling.

**Spec**

* Decision table: transactional is allowed without marketing consent unless suppressed with `reason: legal|complaint|hard_bounce`; marketing requires `granted`; SMS marketing requires explicit opt-in with evidence and honours PAP-405 quiet hours; `do_not_contact` wins over everything.
* Tokens are signed per contact with rotation via `preferenceLink(contactId)`; pages show only a masked email; rate limited per PAP-267; tenant branding via PAP-74.
* Double opt-in: forms (PAP-169, PAP-193) create `pending_double_opt_in` and send the confirm email through PAP-370 `sendEmail` (sandbox rewrite applies); unconfirmed expires after 30 days (PAP-43 job).
* `suppression.check(values[])` is batched and indexed on `value_hash`; STOP keywords from PAP-405 and PAP-370 bounces and complaints write here; `reason: legal` cannot be removed by staff.
* `crm_contact.consent jsonb` is the denormalised cache of current rows, refreshed by trigger; events `consent.changed`, `suppression.added` via `defineTopic`.

**Interface contract**

Provides: `canContact`, `consent.record|withdraw|history`, `suppression.add|check|list`, `preferenceLink`, `unsubscribeHeaders`, public routes, dataset `growth.compliance`, events, staff compliance page. Consumes: CRM schema (sibling), jobs (PAP-43), email package with sandbox (PAP-370), forms (PAP-169, PAP-193 soft), rate limiting (PAP-267), theming (PAP-74), DSAR registry (PAP-221 soft).

**Definition of done**

* Unit decision table green (channel by purpose by status by suppression); token signing and expiry; double opt-in expiry; header generation.
* Integration: an unsubscribe POST suppresses a running PAP-404 test sequence and a PAP-136 digest in one test; form submission goes pending then granted on confirm; history export matches records; all in PAP-370 sandbox mode.
* Playwright: open the preference link, toggle SMS marketing off, one-click unsubscribe from an email header; screenshots at 320, 375, 768, 1024, 1280, 1536, 1920 light and dark for the preference centre (two brands) and the staff page; axe clean.
* `docs/growth/consent.md` with the rule table per jurisdiction; CHANGELOG; Linear comment on PAP-187 with a live preference link on the demo tenant.

**Test plan**

* Unit: decision table exhaustively, hash normalisation (case, plus-address policy), token rotation, expiry job, header formats.
* E2E: the Playwright flows above plus a form submission that lands `pending_double_opt_in` and flips to `granted` on the confirm link.

**Demo**

Reviewer opens a contact's preference link from the CRM page, turns off marketing email, enrols the contact in a test sequence and watches `canContact` refuse with the reason, then one-click unsubscribes from a sandbox email and sees the suppression entry. Under two minutes.

**Edge cases**

* Contact merged (PAP-796): records re-pointed, most restrictive status wins.
* Withdrawal then re-grant: new record with fresh evidence, history intact.
* Suppressed domain refuses every contact at it.
* Leaked token shows no PII beyond a masked email and rotates on next `preferenceLink`.

**Dependencies**

Hard: PAP-790, PAP-43, PAP-370. Soft: PAP-169, PAP-267, PAP-74, PAP-221. Blocks PAP-405 (hard), PAP-193 and PAP-765 (soft, they stub with `do_not_contact` until this merges).

**Agent**

Builder: Beacon (CRM Builder) with Quill on the jurisdiction table. Reviewer: Sentinel (Security Auditor for public routes and PII, Edge Case Hunter).

**Size**

M: one session.

*Round 4 critique fix (2026-09-18):* resolved 3 round-4 file keys in this description to Linear identifiers: `r4/business-core/recurring-invoices-dunning` = PAP-765, `r4/growth/contact-company-merge-and-dedup` = PAP-796, `r4/growth/crm-schema-routers-page-specs` = PAP-790.
