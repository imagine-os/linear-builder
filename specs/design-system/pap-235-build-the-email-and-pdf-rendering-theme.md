---
identifier: "PAP-235"
title: "Build the email and PDF rendering theme: `brandingToInlineCss`, print stylesheet and a template kit shared by invoices, receipts, digests and the ACR export"
project: "design-system"
projectName: "Design System"
phase: "P2"
type: "Build"
priority: 4
surfaces: ["Customer", "Staff"]
milestone: "Themable per tenant with docs"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-75", "PAP-459"]
blocks: []
key: "design-system/email-pdf-theme"
url: "https://linear.app/paperos/issue/PAP-235/build-the-email-and-pdf-rendering-theme-brandingtoinlinecss-print"
source: "Linear snapshot 2026-09-17T15:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T14:54:11.367Z"
model: "claude-sonnet-5"
effort: "low"
---

# PAP-235: Build the email and PDF rendering theme: `brandingToInlineCss`, print stylesheet and a template kit shared by invoices, receipts, digests and the ACR export

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / low — Deferred label (excluded from Oct-1 scope)

**Goal**

Deferred to v0.2 by the Execution Schedule (NJ-14 stop-loss 09-27 can reinstate). Not claimable before 10-01.

Make everything the product sends or prints look like the product: one branded layout kit for HTML email and HTML-to-PDF, driven by the same tenant branding JSON as the app, used by invoices and receipts (PAP-180), the release digest (PAP-89), notification emails and the accessibility conformance report (PAP-160).

**Scope**

* In: `packages/ui-print/` with `brandingToInlineCss(branding)`, `EmailLayout`, `PdfLayout`, blocks (`Header`, `Footer`, `Table`, `Totals`, `Callout`, `Signature`, `PageBreak`), React Email components for mail, a print stylesheet for PDF, `renderPdf(element, options)` using headless Chromium (Playwright already in the toolchain), `renderEmail(element)` producing inlined HTML plus text, previews in Storybook and a `/__preview/print` dev route.
* Out: template content (each consumer), sending (Resend transport), PDF signing, multi-language copy (consumers pass strings).

**Spec**

* `brandingToInlineCss` maps `tenant.branding` (PAP-75) to a fixed set of inline-safe values: accent, accent contrast, neutral text, border, logo URL (absolute, light variant), font stack (system fallback for email); OKLCH converted to hex with `culori`.
* Email: React Email 3.x components, table-based layout, 600 px column, dark-mode meta with safe colours, plain-text alternative generated with `html-to-text`; tested in Litmus-like snapshot set via `@react-email/render` and a visual check in Mailpit.
* PDF: A4 and Letter, margins 18 mm, running header with logo and document title, footer with page x of y (Chromium `headerTemplate`), `@page` rules, fonts embedded from the Google fonts allowlist or system; `renderPdf` returns a Buffer and a stable text layer.
* Kit contract: consumers build a React tree from blocks and call render; no consumer writes CSS.

**Interface contract**

* Provides: `brandingToInlineCss()`, `renderEmail()`, `renderPdf()`, layout and block components, spec IDs `print.*` in the registry, `PrintBranding` type.
* Requires: PAP-75 branding JSON and font allowlist, PAP-66 tokens (default values), PAP-37 for logo URLs, Playwright Chromium on runners (PAP-50 image).
* Consumers: PAP-180 invoices and receipts, PAP-89 digest HTML, PAP-136 emails, PAP-160 ACR PDF, PAP-191 outreach.

**Definition of done**

* Sample invoice, receipt, digest and ACR render to PDF and email with the seeded tenant's branding; PDFs under 300 KB; text selectable.
* Email renders acceptably in Gmail web, Apple Mail and Outlook web (manual screenshots once, snapshot tests thereafter).
* `brandingToInlineCss` contrast test: accent-on-white text passes 4.5:1 or is nudged (reuses PAP-75 validator).
* Storybook previews at 375 and 1280; print preview route screenshots for A4 and Letter.
* Docs `docs/design/print-and-email.md`; changelog under "Design system".

**Test plan**

* Unit: branding mapping for 20 random accents, hex conversion, plain-text generation.
* Integration: `renderPdf` page count and header text via `pdf-parse`; `renderEmail` snapshot of inlined HTML.
* Visual: PDF first page rasterised and compared at 1240 px width; email preview stories.

**Demo**

Run `pnpm print:preview invoice --tenant acme` to open the preview route, toggle Letter and A4, click Download PDF, then open Mailpit after `pnpm print:send-sample` to see the branded email. Under two minutes.

**Edge cases**

* Tenant without a logo: text wordmark in the accent colour.
* Very long tables spanning pages: repeating table header, no orphaned totals.
* RTL locale: `dir="rtl"` on both layouts; numerals per locale.
* Dark-mode email clients inverting colours: forced light background with `color-scheme: light only`.
* Chromium unavailable at runtime: `renderPdf` throws a typed error the job retries; never a blank PDF.

**Dependencies**

PAP-75 (hard). Soft: PAP-37, PAP-27, PAP-50. Downstream, PAP-180 is soft, not blocked: invoices render PDFs with their own template first and adopt `packages/ui-print` when it lands; the `blocks` relation to PAP-180 was removed on 2026-09-17 (round-2 FIX-1; this milestone is 09-30, PAP-180's is 09-29). PAP-89 and PAP-160 adopt the kit the same way.

**Agent**

Built by Iris (Token Keeper) with Ledger consulted on invoice layout needs. Reviewed by Sentinel (Visual Inspector) and Quill (digest fit).

**Size**

M: two renderers and a block kit; email client quirks take the time.
