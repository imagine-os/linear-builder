---
identifier: "PAP-182"
title: "Handle sales tax and VAT via Stripe Tax and store tax evidence"
project: "business-core"
projectName: "Business Core: Payments, Finance & Payroll"
phase: "P2"
type: "Build"
priority: 3
surfaces: ["Staff"]
milestone: "Ledger and reports"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-177", "PAP-180"]
blocks: []
key: "business-core/tax-compliance"
url: "https://linear.app/paperos/issue/PAP-182/handle-sales-tax-and-vat-via-stripe-tax-and-store-tax-evidence"
source: "plan/specs/bucket-6.json (round-1 canonical spec JSON)"
---

# PAP-182: Handle sales tax and VAT via Stripe Tax and store tax evidence

**Goal**

Handle sales tax and VAT without spreadsheets: use Stripe Tax to calculate tax on invoices, checkout and subscriptions, collect and validate customer tax IDs, store tax evidence per transaction (jurisdiction, rate, amounts, location evidence, calculation id) in our own tables for audits and reports, and post tax liabilities to the ledger.

**Scope**

In:
- Tables `fin_tax_registration`, `fin_tax_evidence`, `fin_tax_rate` (manual fallback); oRPC `tax.*`.
- Stripe Tax integration for Checkout (`automatic_tax`), Billing subscriptions and invoice calculations via the Tax Calculation API for documents charged outside Checkout.
- Settings page `/org/settings/tax` (registrations, nexus, default product tax code, tax-inclusive pricing toggle).
- Tax summary report dataset for `business-core/finance-reports`.

Out: filing returns (link to Stripe Tax filing partners), customs/duties, payroll taxes (`business-core/payroll-adapter`).

**Spec**

- Enable Stripe Tax on the platform account and on connected accounts (`tax.settings` per account with `head_office` address and default `tax_code`, e.g. `txcd_10000000` general SaaS or product-specific per line). `fin_tax_registration` mirrors `tax.registrations` (`jurisdiction, type, active_from, active_to, stripe_registration_id`) and is the source for the settings UI; creation via `tax.addRegistration` calls Stripe and stores.
- Checkout and subscriptions: pass `automatic_tax: { enabled: true }` and `customer_update: { address: 'auto' }`; collect billing address; for B2B, `tax_id_collection: { enabled: true }` and store validated IDs on `fin_party.tax_id` with `tax_id_type` and validation status from Stripe.
- Documents outside Checkout (bank-transfer invoices): `tax.calculate(document)` calls `stripe.tax.calculations.create` with line items (amount, quantity, tax_code, reference), customer address and tax IDs; results write `fin_document_line.tax_minor` and create `fin_tax_evidence` rows; on payment, `stripe.tax.transactions.createFromCalculation` records the transaction for Stripe's reporting and stores `stripe_tax_transaction_id`; reversals on void/credit note via `createReversal`.
- `fin_tax_evidence`: `id, tenant_id, document_id?, transaction_id?, calculation_id, tax_transaction_id?, jurisdiction jsonb (country, state, display_name), tax_type (vat, sales_tax, gst), rate_pct numeric(8,4), taxable_minor, tax_minor, currency, taxability_reason, customer_location_evidence jsonb (ip country, billing address, tax id), reverse_charge boolean, created_at`; immutable after write; retained 10 years.
- Ledger posting: tax amounts credit `sales_tax_payable` (per jurisdiction dimension `tax_jurisdiction`) on `invoice.issued`; reverse-charge posts nothing but records evidence; the rule lives in `business-core/invoicing` and reads evidence rows.
- Tax-inclusive pricing: tenant toggle sets `tax_behavior: inclusive` on prices; totals display accordingly; documented per region.
- Manual fallback: when Stripe Tax is disabled (tenant choice or unsupported country), `fin_tax_rate` table (name, rate, jurisdiction, account) with per-line selection and the same evidence rows marked `source: manual`.
- Report dataset `finance.taxSummary` grouped by jurisdiction and period: taxable, tax collected, tax reversed, filing status placeholder; exported as CSV.
- Permissions: `tax.manage` for finance staff; evidence readable by finance and auditors (`auditor` role in `identity/audience-model` if present, else admin).

**Definition of done**

- Vitest for calculation mapping, evidence writes, reverse-charge logic, inclusive/exclusive totals.
- Integration in Stripe test mode: US address with nexus registration produces tax; EU B2B with valid VAT ID produces reverse charge; evidence rows verified.
- Playwright: settings page with registrations, invoice showing tax lines, tax summary report grid; screenshots at 375, 1024, 1920 in three themes.
- `docs/finance/tax.md` including "what Stripe Tax does not do" and the manual path.
- ADR on Stripe Tax; CHANGELOG entry; Linear comment with report screenshot and evidence sample (test data).

**Edge cases**

- Customer address missing: calculation returns `requires address`; invoice cannot be issued until collected, with a request-address email action.
- Tax ID validation pending or invalid: charge tax and flag; re-run when Stripe reports valid.
- Registration added retroactively: past documents untouched; report shows "uncollected" for the gap.
- Rate changes mid-period: evidence stores the rate used at calculation time.
- Refund after tax transaction created: partial reversal with proportional tax.
- Connected account in a country Stripe Tax does not support: fallback to manual rates with a warning banner.

**Dependencies**

- `business-core/stripe-billing` (Stripe client, Checkout), `business-core/invoicing` (documents and posting), `business-core/stripe-connect` (per-account tax settings), `business-core/finance-reports` (report consumer).

**Agent**

Builder: Ledger (Payments Integrator) with Bookkeeper on postings. Reviewer: Sentinel (Code Reviewer, Edge Case Hunter with cross-border cases).

**Size**

M: Stripe Tax handles rates and jurisdictions; the work is evidence storage, fallbacks and reporting.
