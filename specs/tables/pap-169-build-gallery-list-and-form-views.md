---
identifier: "PAP-169"
title: "Build gallery, list and form views"
project: "tables"
projectName: "Table & Views Engine"
phase: "P1"
type: "Build"
priority: 2
surfaces: ["Customer", "Staff"]
milestone: "All view types"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-163", "PAP-337"]
blocks: []
key: "tables/gallery-list-form"
url: "https://linear.app/paperos/issue/PAP-169/build-gallery-list-and-form-views"
source: "Linear snapshot 2026-09-17T13:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T13:05:34.130Z"
model: "claude-sonnet-5"
effort: "high"
---

# PAP-169: Build gallery, list and form views

**Goal**

Ship the three presentation views: gallery (card grid with covers), list (dense vertical feed for phones and sidebars) and form (a data-entry view that creates records, optionally public). Together they cover directories, feeds and intake without custom pages.

**Scope**

In: `packages/views/src/views/gallery/`, `views/list/`, `views/form/`; form runtime and builder panel; public route `/f/:token` (tokens from PAP-172; internal-only until then); `forms.submit` procedure.

Out: payments in forms, multi-page forms, file limits beyond PAP-37 defaults.

**Spec**

* Gallery options `{ coverField?, coverFit, cardSize: 'sm'|'md'|'lg', cardFields, titleField?, showEmptyFields }`; `repeat(auto-fill, minmax(200|280|360px, 1fr))`, virtualised rows, cover from an attachment's `variants.md` or a URL field; click opens `RecordPanel`.
* List options `{ titleField, subtitleField?, metaFields, avatarField?, dense }`; rows 56 or 72 px; grouped headers; two configurable swipe actions (PAP-156); works at 320 px.
* `FormSpec = { fields: { fieldId, label?, help?, required, placeholder?, hiddenWhen?: FilterTree, prefillParam? }[], title, description, submitLabel, successMessage, redirectUrl?, allowMultiple, honeypot: true, captcha?: 'turnstile' }` in `spec.options`.
* Rendering: one editor per row in form mode; validation on blur and submit via `validateRecord`; draft saved per form id in `localStorage`; Markdown via `marked` sanitised.
* `forms.submit({ token, values, honeypot })`: validates token (public, kind form), 30 per minute per IP, strips unknown and hidden fields, honeypot and optional Turnstile, creates as service principal `form-submitter` with `audit_event.reason = 'form:<viewId>'`.
* `hiddenWhen` evaluated client and server side; hidden required fields are not required.
* Public page uses tenant branding (PAP-74); PaperOS footer unless entitlement `whiteLabel` (PAP-178).

**Interface contract**

Provides: `<GalleryView />`, `<ListView />`, `<FormView />`, `<FormBuilder />`, `FormSpec`, procedure `forms.submit`, event `form.submitted { viewId, recordId, values }` consumed by PAP-174 triggers and PAP-193, route `/f/:token`. Consumes: query (PAP-163), editors and `validateRecord` (PAP-164), `RecordPanel` (PAP-165), file variants (PAP-37), theming (PAP-74), swipe (PAP-156), drag reorder (PAP-155), share tokens (PAP-172), `FilterTree` in-memory evaluator (PAP-279), rate limiting (PAP-267).

**Definition of done**

* Vitest, integration and Playwright below green.
* Storybook stories for three views and the builder; screenshots at 375, 768, 1024, 1440, 1920 in three themes; public form with two tenant brands; axe clean with label and error associations verified.
* `docs/views/gallery-list-form.md`; CHANGELOG; Linear comment with a live public form on the demo tenant.

**Test plan**

* Unit: form validation, `hiddenWhen` logic, prefill parsing, honeypot, idempotency key, Markdown sanitisation.
* Integration: `forms.submit` with a valid, expired, revoked and non-form token; hidden-field injection stripped; rate limit trips at 31; record created under `form-submitter` with the audit reason.
* E2E: gallery scroll and open record; list swipe action under touch emulation; form fill with two errors then success; public submission from a fresh browser context; RTL locale layout.
* Visual: matrix above.

**Demo**

Reviewer opens `/demo/gallery`, switches the same dataset to list, then to a form, fills it with one invalid email, fixes it, submits, and sees the new card appear in the gallery. Under two minutes.

**Edge cases**

* Missing or failed cover: placeholder illustration (PAP-72).
* Relation field on a public form: hidden unless the submitter principal may read targets; builder warns.
* Unpublished form: 410 with a friendly page.
* 50 MB upload: rejected by PAP-37 limits with a clear message.
* Double-click submit: idempotency key per draft.

**Dependencies**

PAP-163 (hard), PAP-164 (hard), PAP-165 (`RecordPanel`), PAP-37, PAP-74, PAP-156, PAP-155, PAP-172 (public tokens, soft). Feeds PAP-174, PAP-193.

**Agent**

Builder: Nova (Views Engineer); Iris on card and form styling. Reviewer: Sentinel (Security Auditor for the public endpoint, Visual Inspector).

**Size**

M: gallery and list are thin over cells; the form runtime is the substance.
