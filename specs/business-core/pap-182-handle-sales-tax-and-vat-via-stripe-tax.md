---
identifier: "PAP-182"
title: "Handle sales tax and VAT via Stripe Tax and store tax evidence"
project: "business-core"
projectName: "Business Core: Payments, Finance & Payroll"
phase: "P2"
type: "Build"
priority: 4
surfaces: ["Staff"]
milestone: "Ledger and reports"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-177", "PAP-180", "PAP-397"]
blocks: []
key: "business-core/tax-compliance"
url: "https://linear.app/paperos/issue/PAP-182/handle-sales-tax-and-vat-via-stripe-tax-and-store-tax-evidence"
source: "Linear snapshot 2026-09-17T15:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T13:41:47.459Z"
model: "claude-sonnet-5"
effort: "low"
---

# PAP-182: Handle sales tax and VAT via Stripe Tax and store tax evidence

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / low — Deferred label (excluded from Oct-1 scope)

**Goal**

Deferred to v0.2 by the Execution Schedule (NJ-14 stop-loss 09-27 can reinstate). Not claimable before 10-01.

Handle sales tax and VAT without spreadsheets: Stripe Tax calculates tax on Checkout, subscriptions and invoices, customer tax IDs are collected and validated, evidence per transaction (jurisdiction, rate, amounts, location evidence, calculation id) lives in our tables for audits, and liabilities post to the ledger.

**Scope**

In: tables `fin_tax_registration`, `fin_tax_evidence`, `fin_tax_rate`; procedures `tax.*`; Stripe Tax on Checkout and Billing plus the Tax Calculation API for documents charged outside Checkout; `/org/settings/tax`; report dataset `finance.taxSummary`.

Out: filing returns, customs and duties, payroll taxes (PAP-184).

**Spec**

* Enable Stripe Tax on the platform and connected accounts (`tax.settings` with head office and default `tax_code`, for example `txcd_10000000`); `fin_tax_registration (jurisdiction, type, active_from, active_to, stripe_registration_id)` mirrors `tax.registrations`; `tax.addRegistration` writes both.
* Checkout and subscriptions: `automatic_tax: { enabled: true }`, `customer_update.address: 'auto'`, `tax_id_collection` for B2B; validated IDs stored on `fin_party.tax_id` with type and status.
* Documents outside Checkout: `tax.calculate(documentId)` calls `stripe.tax.calculations.create` with lines, address and IDs, writes `fin_document_line.tax_minor` and evidence rows; on payment `transactions.createFromCalculation` stores `stripe_tax_transaction_id`; void and credit notes call `createReversal`.
* `fin_tax_evidence (document_id?, transaction_id?, calculation_id, tax_transaction_id?, jurisdiction jsonb, tax_type, rate_pct numeric(8,4), taxable_minor, tax_minor, currency, taxability_reason, customer_location_evidence jsonb, reverse_charge, source: stripe|manual, created_at)`; immutable; retained 10 years.
* Posting: tax credits `sales_tax_payable` with dimension `tax_jurisdiction` inside the PAP-180 `invoice.issued` rule, which reads evidence rows; reverse charge posts nothing.
* Tenant toggle for tax-inclusive pricing sets `tax_behavior: inclusive`.
* Manual fallback when Stripe Tax is off or unsupported: `fin_tax_rate (name, rate, jurisdiction, account_id)` with per-line selection and `source: manual` evidence.
* `tax.manage` for finance staff; evidence readable by finance and the auditor role (PAP-62) if present.

**Interface contract**

Provides: `tax.calculate(documentId)`, `tax.addRegistration|listRegistrations|settings`, `tax.rates.*`, `TaxEvidence` type, dataset `finance.taxSummary` (jurisdiction by period: taxable, collected, reversed, filing placeholder, CSV export), a `taxLinesFor(document)` helper PAP-180 calls before issue. Consumes: Stripe client and Checkout (PAP-177), documents and `invoice.issued` rule (PAP-180), connected accounts (PAP-181), report rendering (PAP-183), `fin_party.tax_id` (PAP-175).

**Definition of done**

* Vitest and Stripe test-mode integration below green.
* Playwright: settings with registrations, invoice with tax lines, tax summary grid; screenshots at 375, 1024, 1920 in three themes.
* `docs/finance/tax.md` including "what Stripe Tax does not do" and the manual path; ADR; CHANGELOG; Linear comment with report screenshot and a test evidence sample.

**Test plan**

* Unit: calculation to line mapping, evidence writes, reverse-charge logic, inclusive versus exclusive totals to the cent, retroactive registration leaves past documents untouched.
* Integration (test mode): US address with a nexus registration produces tax; EU B2B with a valid VAT ID produces reverse charge; missing address returns `requires address`; partial refund creates a proportional reversal; manual fallback produces `source: manual` evidence.
* E2E: add a registration, issue a taxed invoice, open the summary report and export CSV.
* Visual: 375, 1024, 1920 in three themes.

**Demo**

Reviewer adds a California registration in `/org/settings/tax`, issues an invoice to a Los Angeles customer and sees the tax line appear with the jurisdiction tooltip, then opens the tax summary report showing the collected amount. Under two minutes.

**Edge cases**

* Missing customer address: issue blocked with a request-address email action.
* Tax ID pending or invalid: tax charged and flagged; re-run when valid.
* Rate change mid-period: evidence keeps the rate used.
* Refund after transaction: proportional reversal.
* Connected account in an unsupported country: manual rates with a banner.

**Dependencies**

PAP-177 (hard), PAP-180 (hard), PAP-181 (soft, per-account settings), PAP-183 (consumer). Blocks nothing hard.

**Agent**

Builder: Ledger (Payments Integrator) with Bookkeeper on postings. Reviewer: Sentinel (Code Reviewer, Edge Case Hunter with cross-border cases).

**Size**

M: Stripe Tax handles rates; evidence, fallbacks and reporting are the work.
