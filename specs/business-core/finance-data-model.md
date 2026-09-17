---
identifier: "PAP-175"
title: "Specify the finance data model: customers, vendors, employees, accounts, transactions and periods across all business types"
project: "business-core"
projectName: "Business Core: Payments, Finance & Payroll"
phase: "P1"
type: "Spec"
priority: 1
surfaces: ["Staff"]
milestone: "Stripe billing live"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-33"]
blocks: ["PAP-177", "PAP-179", "PAP-181", "PAP-184", "PAP-185"]
key: "business-core/finance-data-model"
url: "https://linear.app/paperos/issue/PAP-175/specify-the-finance-data-model-customers-vendors-employees-accounts"
source: "plan/specs/bucket-6.json (round-1 canonical spec JSON)"
---

# PAP-175: Specify the finance data model: customers, vendors, employees, accounts, transactions and periods across all business types

**Goal**

Specify and migrate the finance entities every business built on PaperOS shares, regardless of type: parties (customers, vendors, employees), the chart of accounts, accounting periods, money as a type, and the transaction header that payments, invoices, expenses, payroll and the ledger all reference. Later business-core issues add behaviour; this issue fixes the vocabulary so they do not drift.

**Scope**

In:
- `packages/finance/src/schema/` Drizzle tables with RLS, seeds and a spec doc `docs/finance/data-model.md` with an ER diagram (Mermaid).
- `Money` value type and helpers in `packages/finance/src/money.ts`.
- Default charts of accounts per business type (service, retail, SaaS, agency, clinic, restaurant) as seed JSON.
- oRPC CRUD for parties, accounts and periods following `data-layer/api-layer` conventions.

Out: journal posting (`business-core/ledger`), Stripe objects (`business-core/stripe-billing`), payroll fields beyond identity (`business-core/payroll-adapter`).

**Spec**

- `Money = { amountMinor: bigint, currency: ISO4217 }` stored as `amount_minor bigint` plus `currency char(3)`; helpers `add`, `subtract`, `allocate(ratios)` (largest-remainder), `convert(rate)` using `decimal.js` 10.x for rates; formatting reuses `design-system/data-display` `Money`. Tenant `fin_settings`: `functional_currency`, `fiscal_year_start_month`, `tax_id`, `address`, `invoice_number_format`, `default_payment_terms_days`.
- `fin_party`: `id, tenant_id, kind flags is_customer|is_vendor|is_employee, display_name, legal_name, email, phone, billing_address jsonb, shipping_address jsonb, tax_id, tax_exempt, currency, payment_terms_days, user_id? (link to identity user for portal access), external_ids jsonb ({ stripeCustomerId, quickbooksId, ... }), notes, archived_at`. Role extensions: `fin_customer (party_id, credit_limit_minor, portal_enabled)`, `fin_vendor (party_id, default_expense_account_id, w9_on_file)`, `fin_employee (party_id, start_date, end_date, employment_type: 'w2'|'contractor'|'intl', pay_schedule, payroll_external_id, manager_party_id)`.
- `fin_account`: `id, tenant_id, code (unique per tenant, e.g. 1000), name, type: asset|liability|equity|revenue|expense, subtype (cash, ar, ap, sales_tax_payable, payroll_liability, fixed_asset, cogs, ...), parent_id, currency?, is_system (cannot delete), is_active, description`. System accounts required by posting rules are identified by `subtype` so rules never hardcode codes.
- `fin_period`: `id, tenant_id, start_date, end_date, status: open|closed|locked, closed_by, closed_at`; generated monthly on first use; no overlaps (exclusion constraint).
- `fin_transaction` (business event header, distinct from journal entries): `id, tenant_id, kind: invoice|payment|refund|expense|payroll_run|transfer|adjustment|payout|fee, party_id?, occurred_at, amount_minor, currency, status, source: { system: 'stripe'|'manual'|'payroll'|'import', id }, memo, metadata jsonb`; unique `(tenant_id, source.system, source.id)` for idempotent imports.
- `fin_dimension`: optional tags (`department`, `location`, `project`) as `dimensions jsonb` on transactions and journal lines with a per-tenant dimension registry.
- All tables get `tenant_id` RLS via `data-layer/rls-tenancy`, `audit_event` on write via `data-layer/audit-log`, and register as datasets in `packages/views` so parties and accounts get grid views for free.
- Spec doc includes the mapping table to Stripe, QuickBooks and Xero concepts for `migration/stripe-quickbooks`.

**Definition of done**

- Migrations apply on a fresh DB and on the staging DB; cross-tenant harness green.
- Seeds create six default charts of accounts; a test asserts every posting-rule subtype exists in each.
- Vitest for `Money` (allocation sums exactly, no float paths, currency mismatch throws).
- Data dictionary regenerated (`data-layer/data-dictionary`) and `docs/finance/data-model.md` with ER diagram published.
- Parties and accounts appear as datasets with grid views in the demo tenant; screenshots at 375, 1024, 1920.
- ADR `docs/adr/00xx-finance-model.md`; CHANGELOG entry; Linear comment with doc link.

**Edge cases**

- A party who is both customer and vendor (contra settlement): flags allow it; reports treat roles separately.
- Currency with zero minor units (JPY) or three (KWD): `Money` uses ISO exponent table.
- Period locked while an import backdates transactions: reject with `CONFLICT` and suggest the earliest open period.
- Employee converted from contractor to W-2: `fin_employee` keeps history via `employment_type` change audit.
- Deleting a system account: blocked; deactivate only if balance is zero (checked by ledger later).
- Tenant changes functional currency after transactions exist: blocked with explanation.

**Dependencies**

- `data-layer/core-entities` (tenant, user), `data-layer/drizzle-schema`, `data-layer/rls-tenancy`, `tables/view-model-spec` (dataset registry).

**Agent**

Builder: Ledger (Bookkeeper). Reviewer: Forge (Schema Wright) on schema, Sentinel (Code Reviewer) on money helpers.

**Size**

M: schema and seeds are mechanical; the value is in getting subtypes and mappings right.
