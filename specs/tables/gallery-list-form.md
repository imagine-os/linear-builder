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
blockedBy: ["PAP-163"]
blocks: []
key: "tables/gallery-list-form"
url: "https://linear.app/paperos/issue/PAP-169/build-gallery-list-and-form-views"
source: "plan/specs/bucket-6.json (round-1 canonical spec JSON)"
---

# PAP-169: Build gallery, list and form views

**Goal**

Ship the three presentation-oriented views: gallery (card grid with cover images), list (dense vertical feed usable on phones and in sidebars) and form (a data-entry view that creates records, optionally public). Together they cover customer-facing directories, feeds and intake forms without custom pages.

**Scope**

In:
- `packages/views/src/views/gallery/`, `views/list/`, `views/form/` with options in `ViewSpec.options`.
- Form runtime and public form route `/f/:token` (token issuance from `tables/view-sharing`; until it lands, forms are internal only).
- Form builder panel (field order, labels, help text, required, conditional visibility, prefill via URL params, submit message, redirect).

Out: payments in forms (`business-core/invoicing` payment links can be embedded later), file upload limits beyond file-storage defaults, multi-page forms (v2).

**Spec**

- Gallery options `{ coverField?, coverFit: 'cover'|'contain', cardSize: 'sm'|'md'|'lg', cardFields: fieldId[], titleField?, showEmptyFields }`; responsive CSS grid `repeat(auto-fill, minmax(size, 1fr))` with 200/280/360 px card widths; virtualised rows; card click opens the record panel; cover from `attachment` (first image, `variants.md` from file-storage) or a URL field; skeleton cards on load.
- List options `{ titleField, subtitleField?, metaFields: fieldId[], avatarField?, dense }`; rows 56/72 px; grouped headers from `spec.groups`; swipe actions on touch (`input/touch-gestures`) configurable to two actions (e.g. set status, delete); suits sidebars at 320 px.
- Form model: `FormSpec = { fields: { fieldId, label?, help?, required, placeholder?, hiddenWhen?: FilterGroup (over form values), prefillParam? }[], title, description (Markdown), submitLabel, successMessage, redirectUrl?, allowMultiple, honeypot: true, captcha?: 'turnstile' }` stored in `spec.options`.
- Rendering: one field per row using field type `Editor` in form mode; validation on blur and submit via `validateRecord`; error summary at top with links; progress saved to `localStorage` per form id (draft), cleared on submit; Markdown via `marked` with sanitisation.
- Submission: internal forms call `records.create`; public forms call `forms.submit({ token, values, honeypot })` which validates the token (view visibility `public`, kind `form`), rate limits 30/min per IP, rejects hidden-field values, strips fields not in the form, runs the honeypot and optional Cloudflare Turnstile check, creates the record as the `service` principal `form-submitter` with `audit_event.reason = 'form:<viewId>'`, and returns `{ recordId? }` only if the form allows showing it.
- Conditional visibility evaluates `hiddenWhen` client-side and server-side (a hidden required field is not required).
- Theming: public form page uses tenant branding from `design-system/theming`; PaperOS footer unless the entitlement `whiteLabel` is on (`business-core/entitlements`).
- Builder panel: drag to reorder via `input/drag-drop`, live preview at phone and desktop widths side by side above 1280 px.

**Definition of done**

- Vitest for form validation, conditional logic, prefill parsing, honeypot and rate limiting.
- Playwright: gallery scroll and open record, list swipe action (touch emulation), form fill with errors then success, public form submission with a token.
- Storybook stories tagged `visual` for the three views and the builder; screenshots at 375, 768, 1024, 1440, 1920 in three themes; public form screenshotted with two tenant brands.
- axe clean; form labels and error associations verified.
- `docs/views/gallery-list-form.md`; CHANGELOG entry; Linear comment with a live public form link on the demo tenant.

**Edge cases**

- Cover image missing or `failed`: placeholder illustration from `design-system/icons-illustrations`.
- Form with a relation field: public forms render it as a select of records the `form-submitter` principal may read (usually none) or hide it; builder warns.
- Submitting after the form was unpublished: 410 with a friendly page.
- 50 MB attachment on a public form: rejected by file-storage limits with a clear message.
- Duplicate submissions on double-click: idempotency key per draft.
- Right-to-left locale: layout mirrors, list swipe directions flip.

**Dependencies**

- `tables/query-compiler`, `tables/field-types`, `data-layer/file-storage`, `design-system/theming`, `input/touch-gestures`, `input/drag-drop`; `tables/view-sharing` for public tokens.

**Agent**

Builder: Nova (Views Engineer); Iris (Component Crafter) on gallery card and form styling. Reviewer: Sentinel (Security Auditor for the public endpoint, Visual Inspector).

**Size**

M: three views, but gallery and list are thin over existing cells; the form runtime is the substantive part.
