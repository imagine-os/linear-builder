---
identifier: "PAP-620"
title: "Form view runtime and builder: FormSpec, conditional fields, drafts, public /f/:token submission with honeypot, Turnstile and rate limits"
project: "tables"
projectName: "Table & Views Engine"
phase: "P1"
type: "Build"
priority: 2
surfaces: ["Customer"]
milestone: "All view types"
state: "Backlog"
parent: "PAP-169"
children: []
blockedBy: ["PAP-338", "PAP-613", "PAP-619", "PAP-660"]
blocks: ["PAP-160", "PAP-193", "PAP-388", "PAP-793", "PAP-850", "PAP-854"]
key: "r4/tables/form-view-runtime-and-public-submit"
url: "https://linear.app/paperos/issue/PAP-620/form-view-runtime-and-builder-formspec-conditional-fields-drafts"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:17.780Z"
model: "claude-opus-5"
effort: "high"
estimate: 3
dueDate: "2026-09-29"
cycle: null
---

# PAP-620: Form view runtime and builder: FormSpec, conditional fields, drafts, public /f/:token submission with honeypot, Turnstile and rate limits

**Model / Effort:** Opus 5 (`claude-opus-5`) / high — Build M

**Goal**

Second half of PAP-169 and the only public write path in the views engine: a form view that creates records, with a builder panel, conditional logic, drafts, and a hardened public route. PAP-160 and PAP-193 depend on it.

**Scope**

In: `packages/views/src/views/form/{FormView,FormBuilder,FormField,register}.tsx`; `FormSpec` Zod; procedure `forms.submit`; route `/f/:token` page spec; event `form.submitted`; `docs/views/forms.md` with a security note.

Out: payments in forms, multi-page forms, file limits beyond PAP-37, share token issuance (PAP-172; internal-only until then), notifications on submit (PAP-174).

**Spec**

* `FormSpec = { fields: { fieldId, label?, help?, required, placeholder?, hiddenWhen?: FilterTree, prefillParam? }[], title, description, submitLabel, successMessage, redirectUrl?, allowMultiple, honeypot: true, captcha?: 'turnstile' }` stored in `spec.options`.
* Rendering: one PAP-338/339 editor per row in form mode wrapped in PAP-233 `Form` adapters; validation on blur then submit through `validateRecord`; draft saved per form id in `localStorage` (try/catch, cleared on success); Markdown via `marked` + `dompurify`.
* `hiddenWhen` evaluated client-side with PAP-279's in-memory evaluator and re-evaluated server-side; hidden required fields are not required; prefill from `?p.<param>=` only for fields with `prefillParam`.
* `forms.submit({ token, values, honeypot, turnstileToken? })`: validates a `public` share token of kind `form` (PAP-172 shape; internal `viewId` path for signed-in users), 30 per minute per IP (PAP-304), strips unknown and hidden fields, rejects a filled honeypot silently as success, verifies Turnstile when configured, creates through `records.create` as service principal `form-submitter` with `audit_event.reason = 'form:<viewId>'` and emits `form.submitted { viewId, recordId, values }`.
* Public page uses tenant branding (PAP-75) and the PaperOS footer unless entitlement `whiteLabel` (PAP-178); unpublished or revoked token renders a friendly 410; idempotency key per draft prevents double submit.
* Builder: drag reorder fields (PAP-329), toggle required, edit label and help, set `hiddenWhen` with `FilterBuilder`, preview at 375 and 1024, copy public link.

**Interface contract**

Provides: `<FormView />`, `<FormBuilder />`, `FormSpec`, `forms.submit`, event `form.submitted` (declared with `defineTopic`, consumed by PAP-388 triggers and PAP-193), route `/f/:token`, registration `kind: 'form'`. Consumes: `records.create` (PAP-613), editors and `validateRecord` (PAP-338, PAP-339), form adapters (PAP-233), `FilterBuilder` and evaluator (PAP-617, PAP-279), share tokens (PAP-172, soft), rate limits (PAP-304), theming (PAP-75), entitlements (PAP-178, soft), card styles (sibling).

**Definition of done**

* Vitest, integration and Playwright below green; Storybook for form and builder at 320, 375, 768, 1024, 1440, 1920 in three themes with two tenant brands; axe clean with label and error associations verified.
* Security review (Sentinel Security Auditor) sign-off comment on the public path; `docs/views/forms.md`; CHANGELOG; Linear comment with a live public form on the demo tenant.

**Test plan**

* Unit: `FormSpec` validation; `hiddenWhen` logic; prefill parsing; honeypot; idempotency key derivation; Markdown sanitisation (script and `javascript:` stripped).
* Integration: `forms.submit` with valid, expired, revoked and non-form tokens; hidden-field injection stripped; 31st request in a minute rejected; record created under `form-submitter` with the audit reason; `form.submitted` payload matches the schema.
* E2E: fill the demo form with two errors then success from a fresh browser context; draft survives reload; RTL locale layout; builder reorders a field by keyboard and toggles conditional visibility.

**Demo**

Reviewer opens the builder, marks Email required, hides Budget unless Type is "Project", copies the public link into a private window, submits with one invalid email, fixes it and sees the card appear in `/demo/gallery`. Under two minutes.

**Edge cases**

* Relation field on a public form: hidden unless `form-submitter` may read targets; builder warns.
* 50 MB upload: rejected by PAP-37 limits with a clear message; partial uploads cleaned.
* Turnstile unavailable: submissions rejected with retry guidance, never silently accepted.
* Double-click submit: single record via the idempotency key.

**Dependencies**

PAP-613 (hard), PAP-338 (hard), sibling gallery/list (hard, shared styles and registration order). Soft: PAP-172 (tokens; internal path first), PAP-304, PAP-75, PAP-178, PAP-329. Blocks PAP-388 (`form.submitted` trigger), PAP-193, PAP-160 (feedback form).

**Agent**

Builder: Nova (Views Engineer); Iris on form styling. Reviewer: Sentinel (Security Auditor, Visual Inspector).

**Size**

M: one session.

*Round 4 critique fix (2026-09-18):* resolved 2 round-4 file keys in this description to Linear identifiers: `r4/tables/filter-builder-component` = PAP-617, `r4/tables/records-crud-procedures` = PAP-613.
