---
key: "business-core/invoicing/pdf-paypage"
title: "Branded PDF rendering, public /pay and /doc pages, Stripe Checkout on platform or connected account, receipts"
project: "business-core"
parent: "PAP-180"
phase: "P2"
type: "Build"
priority: 2
size: "M"
surfaces: []
milestone: "Ledger and reports"
intendedState: "Backlog"
blockedBy: []
blocks: []
source: "round2/agent4/pending-issues.json"
linearDocument: "https://linear.app/paperos/document/round-2-pending-issues-business-core-11-7c8c2526b3c9"
identifier: "PAP-396"
status: "created"
createdAt: "2026-09-17"
---

# Branded PDF rendering, public /pay and /doc pages, Stripe Checkout on platform or connected account, receipts

**Goal**

Let a customer receive, read and pay a document: branded PDFs and a public pay page backed by Stripe Checkout, producing receipts on payment.

**Scope**

In: `packages/finance/src/pdf/` templates on the PAP-235 kit, `renderDocumentPdf`, worker rendering and content-addressed storage; routes `/pay/:token`, `/doc/:token`; Checkout session creation; `checkout.session.completed` handler creating receipts. Out: postings, portal, emails (sibling).

**Spec**

* `@react-pdf/renderer` 4.x with `brandingToInlineCss` and Inter embedded; rendered on issue and on demand; stored via PAP-37 keyed by content hash.
* Pay page shows summary, Pay (Checkout redirect) and Download PDF; uses PAP-181 connected account with application fee when enabled, else platform test mode; voided documents show "Voided".
* Payment handler marks `paid|partial`, issues a receipt document and its PDF; idempotent by `stripe_event.id`.

**Interface contract**

Provides: `renderDocumentPdf(id)`, routes, `createDocumentCheckout(documentId)`, receipt issuance. Consumes: model child, Stripe client and events (PAP-177), connected checkout (PAP-181, optional), files (PAP-37), theme kit (PAP-235), rate limiting for public routes (PAP-267).

**Definition of done**

* PDF snapshot tests for three kinds at two brands; test-mode pay flow recorded; pay page at 375 and 1024 in Playwright.

**Test plan**

* Unit: template props mapping; token validation.
* Integration: `stripe trigger` payment produces receipt and status; duplicate event no-op.
* Visual: PDFs rasterised and diffed; pay page screenshots.

**Demo**

Open a pay link in a private window, pay with `4242`, download the receipt PDF.

**Edge cases**

* Expired or revoked token 410; partial payments recorded manually still render a receipt for the amount.

**Dependencies**

Model child (hard), PAP-177, PAP-37, PAP-235 (hard), PAP-181 (optional).

**Agent**

Builder: Ledger (Payments Integrator). Reviewer: Sentinel (Security Auditor, Visual Inspector).

**Size**

M: one session.
