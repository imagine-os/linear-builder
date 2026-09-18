---
identifier: "PAP-793"
title: "Lead forms: form builder, 8 KB embed script, public submit endpoint with spam scoring and rate limits, lead upsert with UTM and consent, submissions grid"
project: "growth"
projectName: "Growth: Marketing, Outreach & CRM"
phase: "P2"
type: "Build"
priority: 4
surfaces: ["Customer"]
milestone: "Campaigns and social"
state: "Backlog"
parent: "PAP-193"
children: []
blockedBy: ["PAP-35", "PAP-187", "PAP-267", "PAP-269", "PAP-304", "PAP-485", "PAP-558", "PAP-620", "PAP-658", "PAP-790", "PAP-791"]
blocks: ["PAP-794"]
key: "r4/growth/lead-forms-embed-and-submit-pipeline"
url: "https://linear.app/paperos/issue/PAP-793/lead-forms-form-builder-8-kb-embed-script-public-submit-endpoint-with"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:44.532Z"
model: "claude-sonnet-5"
effort: "high"
estimate: 3
dueDate: null
cycle: null
---

# PAP-793: Lead forms: form builder, 8 KB embed script, public submit endpoint with spam scoring and rate limits, lead upsert with UTM and consent, submissions grid

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / high — Build M

**Goal**

Deferred to v0.2 by the Execution Schedule (NJ-14 stop-loss 09-27 can reinstate). Not claimable before 10-01.

Half of PAP-193 works on any website, not only Webflow: a form the tenant embeds anywhere that lands in the CRM with attribution and consent. Splitting it from the publisher lets the form ship even when the Webflow OAuth app is still in review.

**Scope**

In: tables `lead_form (name, fields jsonb, success_action, notify_user_ids, honeypot_field, recaptcha: none|turnstile, allowed_origins[])`, `form_submission (form_id, payload jsonb, lead_id, utm jsonb, referrer, ip_hash, user_agent_class, spam_score, status: accepted|spam|error)`; form builder with field types text, email, phone, select, checkbox, textarea, hidden and drag reorder (PAP-155); embed `form.js` under 8 KB gzipped at `/embed/forms/<id>.js` with success callbacks; `POST /api/v1/public/forms/<id>/submit`; pipeline: validate, honeypot, optional Turnstile, spam score, upsert `crm_lead` by email, attach UTM and referrer, write consent through `consent.record`, emit `lead.created`; submissions grid; notification to `notify_user_ids`.

Out: landing pages and Webflow (sibling), payments in forms, multi-page forms (PAP-169 owns table forms; this is the marketing lead form that writes leads, not records).

**Spec**

* The submit endpoint is the only unauthenticated write besides PAP-169 forms: CORS to `allowed_origins`, 20 per minute per IP via PAP-267, 64 KB body, client nonce idempotency for five minutes.
* `ip_hash` is SHA-256 with a tenant salt; raw IP never stored (PAP-355 `pii()` annotations on payload columns).
* Spam score from disposable-domain list, link count and submission velocity; `spam` rows are kept 30 days for review, never create leads.
* Embed renders with the tenant theme tokens inline and works without JavaScript frameworks; verified in Chromium, WebKit and Firefox.

**Interface contract**

Provides: `landing.forms.*`, `form.js` contract (`data-form-id`, callbacks), public submit route, event `lead.created { leadId, formId, utm }`, dataset `form_submission`, `<FormEmbedSnippet />`. Consumes: CRM leads (sibling schema), consent (PAP-791, soft), rate limiting (PAP-267), notifications (PAP-136), drag (PAP-155), attribution client hook (PAP-194, soft), outbound ledger for notifications.

**Definition of done**

* Vitest, integration and Playwright green; `form.js` size budget in CI; three browser projects.
* Screenshots at 320, 375, 768, 1024, 1280, 1536, 1920 light and dark for builder and an embedded form on a third-party test page; axe clean.
* `docs/growth/lead-forms.md`; CHANGELOG.

**Test plan**

* Unit: field validation, spam fixtures, lead upsert by email, UTM normalisation, CORS and rate-limit middleware, nonce idempotency.
* E2E: build a form, embed it in a fixture HTML page served by Playwright, submit with a UTM link, see the lead on the contacts grid with source and consent pending.

**Demo**

Reviewer builds a three-field form, pastes the snippet into the test page, submits and opens `/crm/contacts` to find the new lead with its UTM. Under two minutes.

**Edge cases**

* Double submit: nonce idempotency.
* Email matches an existing customer: lead created and linked, contact untouched.
* Turnstile down: accept with flag when the honeypot passes.
* Non-allowlisted origin: 403 logged with a settings hint.

**Dependencies**

Hard: PAP-790, PAP-267. Soft: PAP-791, PAP-136, PAP-155, PAP-194. Blocks the Webflow sibling.

**Agent**

Builder: Beacon (CRM Builder). Reviewer: Sentinel (Security Auditor for the public endpoint, Visual Inspector).

**Size**

M: one session.

*Round 4 critique fix (2026-09-18):* resolved 2 round-4 file keys in this description to Linear identifiers: `r4/growth/consent-compliance-centre` = PAP-791, `r4/growth/crm-schema-routers-page-specs` = PAP-790.
