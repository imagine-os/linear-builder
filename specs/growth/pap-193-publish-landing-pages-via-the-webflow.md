---
identifier: "PAP-193"
title: "Publish landing pages via the Webflow API and capture forms into the CRM"
project: "growth"
projectName: "Growth: Marketing, Outreach & CRM"
phase: "P2"
type: "Build"
priority: 4
surfaces: ["Customer"]
milestone: "Campaigns and social"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-35", "PAP-187", "PAP-269", "PAP-304", "PAP-353", "PAP-485"]
blocks: []
key: "growth/landing-forms"
url: "https://linear.app/paperos/issue/PAP-193/publish-landing-pages-via-the-webflow-api-and-capture-forms-into-the"
source: "Linear snapshot 2026-09-17T15:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T15:00:38.913Z"
model: "claude-sonnet-5"
effort: "low"
---

# PAP-193: Publish landing pages via the Webflow API and capture forms into the CRM

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / low — Deferred label (excluded from Oct-1 scope)

**Goal**

Deferred to v0.2 by the Execution Schedule (NJ-14 stop-loss 09-27 can reinstate). Not claimable before 10-01.

Close the loop from marketing page to CRM record: publish landing pages to the tenant's Webflow site through the Data API, embed a PaperOS form on them, and capture every submission as a `crm_lead` with UTM attribution, spam filtering and notification, so campaigns produce leads without manual export.

**Scope**

In: `packages/growth/src/landing/schema.ts` (`landing_page`, `lead_form`, `form_submission`); Webflow integration (`webflow-api` 3.x, OAuth per tenant, CMS collection "Landing Pages", site publish) with a GitHub Pages fallback (PAP-15); embed script `form.js` under 8 KB gzipped served at `/embed/forms/<id>.js`; public endpoint `POST /api/v1/public/forms/<id>/submit`; submission pipeline; editors for pages and forms; submissions grid; Webflow settings.

Out: full visual page builder, A/B tests, Designer API extensions, payments on pages.

**Spec**

* `landing_page (title, slug, webflow_site_id, webflow_page_id, webflow_item_id, status: draft|pending_approval|published|archived, content jsonb blocks, seo jsonb, form_id, published_at)`; `lead_form (name, fields jsonb, success_action, notify_user_ids, honeypot_field, recaptcha: none|turnstile, allowed_origins[])`; `form_submission (form_id, payload jsonb, lead_id, utm jsonb, referrer, ip_hash, user_agent_class, spam_score, status: accepted|spam|error)`.
* The submit endpoint is the only unauthenticated write besides PAP-169 forms: CORS to `allowed_origins`, 20 per minute per IP via PAP-267 rate limiting, 64 KB body, client nonce idempotency for five minutes.
* Pipeline: validate against `fields`, honeypot, optional Turnstile, spam score (disposable domains, link count), upsert `crm_lead` by email, attach UTM from hidden fields and `document.referrer`, write consent through PAP-187 work package 0 (`consent.record`, double opt-in when the tenant requires it) when the consent box is ticked, emit `lead.created`.
* Field types text, email, phone, select, checkbox, textarea, hidden; email and phone validated server-side.
* Publishing needs `landing.publish`; agent drafts stop at `pending_approval`; CMS field mapping stored per site; publish idempotent by `webflow_item_id`.
* `ip_hash` is SHA-256 with a tenant salt; raw IP never stored.

**Interface contract**

Provides: `landing.pages.*`, `landing.drafts.create` (for PAP-192), `landing.forms.*`, `form.js` embed contract (`data-form-id`, success callbacks), public submit route, event `lead.created { leadId, formId, utm }` consumed by PAP-194 and PAP-136 core, `form_submission` dataset. Consumes: `crm_lead` and consent (PAP-187 and its work package 0), public route pattern and rate limiting (PAP-267), Pages fallback (PAP-15), notifications (PAP-136 core), drag reorder (PAP-155), attribution client hook (PAP-194), Webflow OAuth app (Needs Justin).

**Definition of done**

* Vitest, integration and Playwright below green; `form.js` size budget enforced in CI; works in Chromium, WebKit and Firefox projects.
* Screenshots at 320, 375, 768, 1024, 1280, 1536, 1920 in light and dark for editor, form builder and a published page.
* `docs/growth/landing-forms.md` with Webflow setup; CHANGELOG; Linear comment with the live page URL.

**Test plan**

* Unit: field validation, spam scoring fixtures, lead upsert by email, UTM extraction and normalisation, CORS and rate-limit middleware, CMS mapping rename safety.
* Integration: publish to the connected Webflow staging site and submit from the live page (recording); Pages fallback publishes static HTML; archived form returns 410; disallowed origin returns 403 with a settings hint in the log.
* E2E: build page, build form, publish, submit, see the lead on the PAP-189 contacts grid with its UTM.
* Visual: matrix above plus the embed rendered inside a third-party test page.

**Demo**

Reviewer publishes the demo landing page, opens the live Webflow URL, submits the embedded form with a UTM-tagged link, then opens `/crm/contacts` to see the new lead with source and campaign filled. Under two minutes.

**Edge cases**

* Webflow quota exceeded: `pending_publish` with retry and banner.
* Double submit: nonce idempotency.
* Email matches an existing customer: lead created and linked, contact untouched.
* Turnstile down: accept with flag when the honeypot passes; flagged rows reviewed in the grid.
* Page embedded on a non-allowlisted origin: 403 logged.

**Dependencies**

PAP-187 (hard), PAP-35 children (hard, public route pattern), PAP-15 (fallback), PAP-136 core, PAP-155, PAP-187 work package 0 (consent centre; soft: write consent through its `consent.record` when it exists, else store on `crm_contact.consent jsonb` and migrate), Webflow account (Needs Justin). Feeds PAP-194; receives drafts from PAP-192.

**Agent**

Builder: Beacon (Campaign Composer for editors, CRM Builder for the pipeline). Reviewer: Sentinel (Security Auditor for the public endpoint, Visual Inspector), Quill.

**Size**

M: one external API, one public endpoint, an embed script and two editors.
