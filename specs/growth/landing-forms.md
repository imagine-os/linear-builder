---
identifier: "PAP-193"
title: "Publish landing pages via the Webflow API and capture forms into the CRM"
project: "growth"
projectName: "Growth: Marketing, Outreach & CRM"
phase: "P2"
type: "Build"
priority: 3
surfaces: ["Customer"]
milestone: "Campaigns and social"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-187", "PAP-269", "PAP-35"]
blocks: []
key: "growth/landing-forms"
url: "https://linear.app/paperos/issue/PAP-193/publish-landing-pages-via-the-webflow-api-and-capture-forms-into-the"
source: "plan/specs/bucket-7.json (round-1 canonical spec JSON)"
---

# PAP-193: Publish landing pages via the Webflow API and capture forms into the CRM

**Goal**

Close the loop from marketing page to CRM record: publish landing pages to the tenant's Webflow site through the Webflow Data API, embed a PaperOS form on them, and capture every submission as a `crm_lead` with UTM attribution, spam filtering and instant notification, so campaigns produce leads without manual export.

**Scope**

In:
- Schema `packages/growth/src/landing/schema.ts`: `landing_page` (`title`, `slug`, `webflow_site_id`, `webflow_page_id`, `webflow_item_id`, `status: draft|pending_approval|published|archived`, `content jsonb` blocks, `seo jsonb`, `form_id`, `published_at`), `lead_form` (`name`, `fields jsonb` schema, `success_action`, `notify_user_ids`, `honeypot_field`, `recaptcha: none|turnstile`), `form_submission` (`form_id`, `payload jsonb`, `lead_id`, `utm jsonb`, `referrer`, `ip_hash`, `user_agent`, `spam_score`, `status: accepted|spam|error`).
- Webflow integration `packages/growth/src/landing/webflow.ts` using `webflow-api` 3.x: OAuth connect per tenant, list sites, publish to a CMS collection "Landing Pages" (created if missing with fields matching `content`) and trigger site publish; fallback path writes static HTML to the app's GitHub Pages demo (`app-shell/gh-pages-demo`) when no Webflow site is connected.
- Embeddable form: `packages/growth/src/landing/embed/` builds `form.js` (plain TS, under 8 KB gzipped, no framework) served from the API at `/embed/forms/<id>.js`; renders fields from `lead_form.fields`, posts to `POST /api/v1/public/forms/<id>/submit`, handles success message or redirect.
- Submission pipeline: validate against field schema, honeypot and Cloudflare Turnstile check, rate limit by `ip_hash`, spam scoring (disposable email list, link count), create or update `crm_lead` (match on email), attach UTM from hidden fields and `document.referrer`, emit `lead.created` for `collab/notifications` and `growth/attribution`.
- UI: landing page editor (block list with hero, features, CTA, form blocks; live preview), form builder (drag fields via `input/drag-drop`), submissions grid view, Webflow connection settings.

Out: full visual page builder, A/B testing, Webflow Designer API extensions, payments on landing pages.

**Spec**

- Public submit endpoint is the only unauthenticated write in the API: CORS restricted to origins registered on the form (`allowed_origins[]`), 20 req/min per IP, 64 KB body max.
- Field types: text, email, phone, select, checkbox, textarea, hidden; email and phone validated server-side; consent checkbox writes `crm_contact.consent`.
- Publishing requires `landing.publish` permission; agent drafts (`growth/content-agent`) stop at `pending_approval`.
- Webflow CMS mapping stored per site so renaming fields does not break publish; publish is idempotent by `webflow_item_id`.
- Success action: inline message, redirect URL, or calendar link; all render without JS errors when embedded on a third-party page.
- PII: `ip_hash` is SHA-256 with tenant salt; raw IP never stored.

**Definition of done**

- Vitest: field validation, spam scoring, lead upsert, UTM extraction, CORS and rate limit middleware, Webflow mapping.
- Integration: publish a page to the connected Webflow staging site and submit the embedded form from the live page (recording attached); Pages fallback verified too.
- Playwright: build page, build form, publish, submit, see lead in `growth/crm-views`; screenshots at 320, 375, 768, 1024, 1280, 1536 and 1920 in light and dark for editor, form builder and a published page.
- `form.js` size budget test under 8 KB gzipped; works in Chrome, Safari and Firefox (Playwright projects).
- `docs/growth/landing-forms.md` with the Webflow setup steps; CHANGELOG entry; Linear comment with live page URL and screenshots.

**Edge cases**

- Webflow publish quota exceeded: page stays `pending_publish` with retry at next window and a banner.
- Duplicate submission (double click): idempotency key from client nonce for 5 minutes.
- Submission for a form that was archived: 410 with friendly message, no lead created.
- Email matches an existing customer contact: lead created and linked, contact not overwritten; activity logged.
- Page embedded on an origin not in the allowlist: 403 and a settings hint in the submissions log.
- Turnstile unavailable: fail open for accepted-with-flag when honeypot passes; flagged submissions reviewed in grid.

**Dependencies**

`growth/crm-model` (hard). `data-layer/api-layer` (public route pattern), `app-shell/gh-pages-demo` (fallback), `collab/notifications`, `input/drag-drop`. Feeds `growth/attribution` and receives drafts from `growth/content-agent`.

**Agent**

Built by Beacon (Campaign Composer for editor, CRM Builder for pipeline). Reviewed by Sentinel (Security Auditor for the public endpoint, Visual Inspector) and Quill.

**Size**

M: one external API, one public endpoint, an embed script and two editors.
