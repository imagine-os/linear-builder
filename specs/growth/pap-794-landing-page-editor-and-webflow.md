---
identifier: "PAP-794"
title: "Landing page editor and Webflow publisher: block content model, CMS collection mapping, site publish with a GitHub Pages fallback, approval before publish"
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
blockedBy: ["PAP-15", "PAP-353", "PAP-793"]
blocks: ["PAP-809", "PAP-855", "PAP-870"]
key: "r4/growth/webflow-landing-publisher-and-editor"
url: "https://linear.app/paperos/issue/PAP-794/landing-page-editor-and-webflow-publisher-block-content-model-cms"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:44.678Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 3
dueDate: null
cycle: null
---

# PAP-794: Landing page editor and Webflow publisher: block content model, CMS collection mapping, site publish with a GitHub Pages fallback, approval before publish

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Build M

**Goal**

Deferred to v0.2 by the Execution Schedule (NJ-14 stop-loss 09-27 can reinstate). Not claimable before 10-01.

The publishing half of PAP-193: compose a landing page from blocks, attach a lead form, and publish it to the tenant's Webflow site through the Data API or to GitHub Pages when Webflow is not connected, with the same approval state machine the rest of growth uses.

**Scope**

In: `landing_page (title, slug, webflow_site_id, webflow_page_id, webflow_item_id, status: draft|pending_approval|published|archived, content jsonb blocks, seo jsonb, form_id, published_at)`; block editor (hero, features, testimonial, form, CTA, FAQ) with live preview; `webflow-api` 3.x integration with per-tenant OAuth (encrypted via PAP-353), CMS collection 'Landing Pages' field mapping stored per site, `sites.publish`; Pages fallback rendering static HTML with the embed script into the tenant's Pages repo (PAP-15); `landing.drafts.create` for PAP-192; settings page for the Webflow connection.

Out: visual page builder, Designer API extensions, A/B tests (PAP-809), custom domains beyond what Webflow or Pages provide.

**Spec**

* Publishing requires `landing.publish`; agent drafts stop at `pending_approval`; publish is idempotent by `webflow_item_id`.
* In `dryRun` (the CI default) the Webflow adapter writes the exact CMS payload to a snapshot; live publish is per-tenant and off until Justin connects a site.
* Content blocks are Zod-validated and render identically in the preview, Webflow (through CMS rich text) and Pages HTML; a golden render test compares the three.
* Quota exceeded or API error: `pending_publish` with retry and a banner.

**Interface contract**

Provides: `landing.pages.*`, `landing.drafts.create`, `LandingPagePublisherPort` with `webflow` and `pages` adapters, block schemas, settings page. Consumes: lead forms (sibling), Pages fallback (PAP-15), Webflow OAuth app (Needs Justin), encryption (PAP-353), content agent drafts (PAP-192), approval badge `drafted_by` (PAP-401 pattern).

**Definition of done**

* Adapter snapshot tests for Webflow payloads; Pages fallback publishes a static page in the fixture repo (CI); golden render comparison green.
* Playwright: build, attach a form, submit for approval, approve, publish to Pages; screenshots at 320, 375, 768, 1024, 1280, 1536, 1920 light and dark.
* `docs/growth/landing-pages.md` with Webflow setup; CHANGELOG; comment on PAP-193.

**Test plan**

* Unit: block validation, CMS mapping rename safety, idempotent publish, state machine.
* E2E: the Playwright flow above; a recorded Webflow staging publish when `WEBFLOW_TEST_TOKEN` exists, else `skipped: no-credentials`.

**Demo**

Reviewer composes a hero and form page, approves it and publishes to Pages, then opens the URL and submits the form. Under two minutes.

**Edge cases**

* Webflow site disconnected after publish: page stays published there; PaperOS marks the connection stale.
* Slug collision on the site: suffixed and reported.
* Draft edited after approval: returns to `pending_approval` (hash binding).

**Dependencies**

Hard: PAP-793, PAP-15. Soft: PAP-353, PAP-192, Webflow account (NJ).

**Agent**

Builder: Beacon (Campaign Composer). Reviewer: Sentinel (Security Auditor for OAuth tokens, Visual Inspector).

**Size**

M: one session.

*Round 4 critique fix (2026-09-18):* resolved 2 round-4 file keys in this description to Linear identifiers: `r4/growth/experiments-and-ab-tests` = PAP-809, `r4/growth/lead-forms-embed-and-submit-pipeline` = PAP-793.
