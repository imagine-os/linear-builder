---
identifier: "PAP-180"
title: "Implement invoices, quotes and receipts with PDF generation and Stripe payment links"
project: "business-core"
projectName: "Business Core: Payments, Finance & Payroll"
phase: "P2"
type: "Build"
priority: 2
surfaces: ["Customer", "Staff"]
milestone: "Ledger and reports"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-177", "PAP-179", "PAP-37"]
blocks: ["PAP-182", "PAP-183"]
key: "business-core/invoicing"
url: "https://linear.app/paperos/issue/PAP-180/implement-invoices-quotes-and-receipts-with-pdf-generation-and-stripe"
source: "plan/specs/bucket-6.json (round-1 canonical spec JSON)"
---

# PAP-180: Implement invoices, quotes and receipts with PDF generation and Stripe payment links

**Goal**

Let any tenant bill anyone for anything: quotes that convert to invoices, invoices with line items, taxes and payment terms, receipts on payment, branded PDFs, a public pay page backed by Stripe, and automatic ledger postings for accounts receivable, revenue and cash.

**Scope**

In:
- Tables `fin_document` (quote, invoice, receipt, credit note) and `fin_document_line`; number sequences; oRPC `documents.*`.
- PDF rendering service and templates; public routes `/pay/:token` and `/doc/:token`.
- Pages: documents grid, editor, detail with activity; customer portal "Invoices" list (`identity/customer-portal-shell`).
- Posting rules `invoice.issued`, `invoice.paid`, `invoice.voided`, `credit_note.issued`.
- Email sending via `collab/notifications` templates (send, reminder, receipt).

Out: recurring invoices (Stripe Billing handles subscriptions), inventory, multi-language templates beyond locale number/date formatting.

**Spec**

- `fin_document`: `id, tenant_id, kind: quote|invoice|receipt|credit_note, number (per-tenant per-kind sequence formatted by `fin_settings.invoice_number_format`, e.g. `INV-{YYYY}-{0000}`), party_id, status (quote: draft|sent|accepted|declined|expired; invoice: draft|issued|sent|viewed|partial|paid|overdue|void; receipt: issued; credit_note: issued|applied), issue_date, due_date, currency, subtotal_minor, discount_minor, tax_minor, total_minor, paid_minor, balance_minor, terms text, notes text, source_document_id (quote to invoice), stripe_payment_intent_id?, stripe_checkout_session_id?, public_token, pdf_file_id, sent_at, viewed_at, metadata`. `fin_document_line`: `document_id, line_no, description, quantity numeric(12,4), unit_price_minor, discount_pct, tax_rate_id?, tax_minor, amount_minor, revenue_account_id?, dimensions`.
- Totals computed server-side with `Money` in the document's currency; tax lines from `business-core/tax-compliance` when enabled, else manual tax rates table `fin_tax_rate`.
- Lifecycle: `documents.issue` freezes lines and number, posts `invoice.issued` (debit AR, credit revenue per line account, credit tax payable), creates a Stripe Checkout Session (or PaymentIntent for saved cards) on the tenant's connected account when `business-core/stripe-connect` is enabled, else on the platform account in test mode with a `fin_transaction`; `/pay/:token` renders the invoice summary and a Pay button (Checkout redirect) plus "Download PDF"; webhook `checkout.session.completed` records payment, posts `invoice.paid` (debit cash, credit AR), sets `paid|partial`, issues a receipt document and emails it.
- Quotes: `documents.accept` from the public page (signature name and timestamp stored) converts to an invoice draft; expiry job marks `expired`.
- Void: only for issued invoices without payments; posts a reversal; credit notes handle paid ones and apply against balances.
- PDF: `@react-pdf/renderer` 4.x templates in `packages/finance/src/pdf/` using tenant branding (logo from file-storage, colours from `tenant.branding`), fonts embedded (Inter), locale formatting; rendered in a worker on issue and on demand, stored via `data-layer/file-storage`, content-addressed so identical documents are not re-rendered.
- Reminders: overdue job daily; sends reminder at due+3 and due+14 unless disabled; marks `overdue`.
- Portal: customers with `fin_customer.portal_enabled` see their documents and pay from the portal; access restricted by party link to `user_id`.
- Permissions: `document.create|issue|void|send` for finance staff; customers `document.read` own.

**Definition of done**

- Vitest for totals (rounding, discounts, multi-rate tax), state machine transitions, number formatting and sequence gaplessness under concurrency.
- Integration: issue → pay in Stripe test mode → receipt and ledger entries verified against expected lines.
- PDF snapshot tests (rasterised via `pdf-to-img`) for invoice, quote, receipt at two brands; visual diff in CI.
- Playwright: editor flow, public pay page at 375 and 1024, portal list; screenshots at 375, 768, 1024, 1440, 1920 in three themes.
- `docs/finance/invoicing.md`; CHANGELOG entry; Linear comment with a live test-mode pay link and video replay.

**Edge cases**

- Partial payment via bank transfer recorded manually: `documents.recordPayment` posts cash/AR and sets `partial`.
- Currency differs from functional currency: FX rate captured at issue and at payment; gain/loss posted.
- Customer opens a voided invoice's pay link: page shows "Voided" and no Pay button.
- Line quantity 0.3333 hours: quantity precision 4, amounts rounded per line then summed (documented policy).
- Duplicate webhook after receipt already issued: idempotent by `stripe_event` id.
- Number format changed mid-year: existing numbers untouched; new sequence continues from the max.

**Dependencies**

- `business-core/stripe-billing` (Stripe client, webhook plumbing), `business-core/ledger` (posting), `business-core/stripe-connect` (optional connected-account charges), `business-core/tax-compliance` (optional), `data-layer/file-storage`, `collab/notifications`, `identity/customer-portal-shell`.

**Agent**

Builder: Ledger (Payments Integrator with Bookkeeper on posting rules). Reviewer: Sentinel (Security Auditor for public pay route, Visual Inspector for PDFs).

**Size**

L: state machine, PDFs, payments and portal touch many systems; two sessions.
