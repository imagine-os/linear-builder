---
identifier: "PAP-855"
title: "Build form publishing: public routes, embeds, anti-spam, rate limits, payment step via Stripe Checkout, partial saves, notifications and submission views"
project: "workflows"
projectName: "Workflows, Approvals, Forms, Documents & E-Signature"
phase: "P2"
type: "Build"
priority: 4
surfaces: ["Customer"]
milestone: "Forms builder and document templates"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-136", "PAP-172", "PAP-193", "PAP-304", "PAP-396", "PAP-558", "PAP-624", "PAP-725", "PAP-794", "PAP-854"]
blocks: []
key: "r4/workflows/forms-publishing"
url: "https://linear.app/paperos/issue/PAP-855/build-form-publishing-public-routes-embeds-anti-spam-rate-limits"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:51:34.463Z"
model: "claude-opus-5"
effort: "high"
estimate: 3
dueDate: null
cycle: null
---

# PAP-855: Build form publishing: public routes, embeds, anti-spam, rate limits, payment step via Stripe Checkout, partial saves, notifications and submission views

**Model / Effort:** Opus 5 (`claude-opus-5`) / high — Build M

**Goal**

Put forms in front of the public safely: `/f/:token` public routes and a `form.js` embed (shared with PAP-193), anti-spam (Turnstile port, honeypot, timing, PAP-304 rate limits), a payment block that collects money through PAP-396 Checkout before the submission completes, partial saves with resume links, notifications to owners and submitters, and submission grids and charts as saved views.

**Scope**

In: Publishing: `form_publication` (`token`, `mode public|portal|internal`, `expires`, `maxSubmissions`, `password?`, `allowedOrigins[]`) reusing PAP-172 token semantics; `/f/:token` route on the public layout with tenant branding (PAP-75) and custom domains (PAP-431); embed script `form.js` (iframe with resize messaging, under 6 KB) replacing PAP-193's. Anti-spam: `CaptchaPort` (Cloudflare Turnstile adapter, `noop` for tests), honeypot field, minimum fill time, per-IP and per-form limits (PAP-304), disposable-email heuristic; suspected spam lands in `status: spam` for review. Payment block: creates a PAP-396 Checkout session (platform or connected account) for a fixed or computed amount; submission completes on the webhook; unpaid submissions expire after 24 h. Notifications: kinds `form.submitted` to owners with a summary, confirmation email to submitter through PAP-370 with the receipt when paid; submission views: grid, chart and a per-form dashboard (PAP-173) auto-created.

Out: Survey logic and NPS (engagement). Payment methods beyond Checkout.

**Spec**

* Public submissions never create principals; the submitter is an `ActorRef { kind: anonymous }` with a hashed IP; PII stays in `payload` under PAP-355 rules
* Money never touches the API: amounts are computed server-side from the definition and the payload, then sent to Stripe; the webhook is the only completion path (PCI SAQ-A, PAP-359)
* Resume links are signed, single-use per save and expire with the publication; partial payloads are encrypted at rest (PAP-353) because they may hold PII before consent is complete
* Embeds refuse origins not on `allowedOrigins`; CSP frame-ancestors is set per publication
* Rate limits: 10 submissions per IP per hour by default, per-form override, 429 with retry copy in the runner

**Interface contract**

Provides: `FormPort.publish`, `/f/:token`, `form.js`, `CaptchaPort`, payment block, notification kinds, auto-created submission views and dashboard. Consumes: forms runtime, token semantics (PAP-172), rate limits (PAP-304), Checkout and webhooks (PAP-396), landing forms (PAP-193, superseded embed), notifications (PAP-136), email (PAP-370), branding and domains (PAP-75, PAP-431), field encryption (PAP-353). Consumed by: growth landing pages (PAP-193), engagement surveys and booking intake, commerce order forms, migration packs.

**Definition of done**

* A public paid registration form completes end to end in Stripe test mode with a receipt; spam fixtures are quarantined; embed works on a Webflow test page; submission dashboard renders
* Every new page has a `page.spec.yaml` (PAP-114) that passes the validator, declared loading, empty, error and denied states, and Gate 3 screenshots at 375, 768, 1024 and 1920 in light and dark themes.
* Linear comment on the issue with the evidence links (PR, gate artefacts, recording or report) and the module docs page updated where the interface changed.

**Test plan**

* Unit: origin allow-list; amount computation; resume link signing and single use; spam scoring.
* Integration: Checkout webhook completes the submission once even when delivered twice; expired unpaid submission cleanup.
* E2E: public form on a phone with Turnstile in test mode; embed resize; 429 path.
* Isolation: the PAP-34 cross-tenant harness auto-enrols every new table; one negative case per new oRPC procedure proves `NOT_FOUND` on a foreign tenant row.

**Demo**

Publish a workshop registration form with a $25 fee, embed it on the demo landing page, register and pay in test mode, then open the auto-created dashboard showing registrations and revenue.

**Edge cases**

* Publication expired mid-fill: submit returns `FORM_CLOSED` with the tenant's closing message; drafts are kept for the resume window
* Stripe webhook late by hours: submission shows `awaiting payment` and completes when it arrives; owner notified once
* Module disabled for the tenant (PAP-266): routes return `MODULE_DISABLED` (409), slot fills unmount and the manifest declares the dependency so consumers fail closed rather than half-render.

**Dependencies**

PAP-854 (hard), PAP-172, PAP-304 (hard), PAP-396 (hard: payments), PAP-193 (soft: supersedes its embed), PAP-136, PAP-370 (soft).

**Agent**

Builder: Nova. Reviewer: Sentinel (Security Auditor).

**Size**

M: one session.

*Round 4 critique fix (2026-09-18):* resolved 1 round-4 file key in this description to Linear identifiers: `r4/workflows/forms-schema-runtime` = PAP-854.
