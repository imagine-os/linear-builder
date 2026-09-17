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
blockedBy: ["PAP-33", "PAP-302"]
blocks: ["PAP-177", "PAP-179", "PAP-181", "PAP-184", "PAP-185", "PAP-392", "PAP-395", "PAP-399"]
key: "business-core/finance-data-model"
url: "https://linear.app/paperos/issue/PAP-175/specify-the-finance-data-model-customers-vendors-employees-accounts"
source: "Linear snapshot 2026-09-17T13:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T13:04:58.278Z"
---

# PAP-175: Specify the finance data model: customers, vendors, employees, accounts, transactions and periods across all business types

**Goal**

Fix the finance vocabulary every business on PaperOS shares: parties (customer, vendor, employee), chart of accounts, accounting periods, `Money`, dimensions and the `fin_transaction` header that payments, invoices, expenses, payroll and the ledger all reference. Later issues add behaviour; this one stops them drifting.

**Scope**

In: `packages/finance/src/schema/` Drizzle tables with RLS and seeds; `packages/finance/src/money.ts`; six default charts of accounts (service, retail, SaaS, agency, clinic, restaurant) as seed JSON; oRPC CRUD `finance.parties|accounts|periods.*`; `docs/finance/data-model.md` with a Mermaid ER diagram and a Stripe, QuickBooks and Xero mapping table for PAP-206.

Out: journal posting (PAP-179), Stripe objects (PAP-177), payroll fields beyond identity (PAP-184).

**Spec**

* `Money = { amountMinor: bigint, currency }` stored as `amount_minor bigint` plus `currency char(3)`; helpers `add`, `subtract`, `allocate(ratios)` (largest remainder), `convert(rate)` with `decimal.js`; ISO exponent table for JPY and KWD; formatting through PAP-27 `formatMoney`.
* `fin_settings`: `functional_currency, fiscal_year_start_month, tax_id, address, invoice_number_format, default_payment_terms_days, expense_approval_threshold_minor`.
* `fin_party`: role flags `is_customer|is_vendor|is_employee`, names, contact fields, addresses jsonb, `tax_id`, `tax_exempt`, `currency`, `payment_terms_days`, `user_id?`, `external_ids jsonb`, `archived_at`; extensions `fin_customer (credit_limit_minor, portal_enabled)`, `fin_vendor (default_expense_account_id, w9_on_file)`, `fin_employee (start_date, end_date, employment_type, pay_schedule, compensation jsonb, payroll_external_id, manager_party_id)`.
* `fin_account`: `code` unique per tenant, `type: asset|liability|equity|revenue|expense`, `subtype` (the stable handle posting rules use: `cash, ar, ap, stripe_balance, sales_tax_payable, payroll_liability, fees, fx_gain_loss, ...`), `parent_id`, `is_system`, `is_active`.
* `fin_period`: monthly, `status: open|closed|locked`, exclusion constraint against overlap.
* `fin_transaction`: `kind: invoice|payment|refund|expense|payroll_run|transfer|adjustment|payout|fee`, `party_id?`, `occurred_at`, `amount_minor`, `currency`, `status`, `source { system, id }` unique per tenant, `memo`, `metadata`, `dimensions jsonb`.
* All tables: `tenant_id` RLS (PAP-34), audit on write (PAP-38), registered as datasets (PAP-161).

**Interface contract**

Provides: types `Money`, `Party`, `Account`, `Period`, `FinTransaction`, `AccountSubtype` enum, `moneySchema`, procedures `finance.parties|accounts|periods.list|get|create|update|archive`, datasets `finance.parties`, `finance.accounts`, seed `charts/<businessType>.json`. Consumes: `tenant|user` (PAP-33), RLS (PAP-34), audit (PAP-38), API conventions (PAP-268), `registerDataset` (PAP-161), `Money` formatting (PAP-27). Consumed by PAP-177 to PAP-186, PAP-196, PAP-206, PAP-187 (`billing_customer_id`).

* Contract source: [Interface & Data Contracts](<https://linear.app/paperos/document/paperos-interface-and-data-contracts-d40e6a4d227c>) §1 (the `Money` bullet is decided in this issue's favour: `{ amountMinor: bigint, currency }` at runtime, `amount_minor bigint + currency char(3)` in Postgres, decimal string in JSON; PAP-71, PAP-164 and PAP-187 conform to it); §2 row "Ledger entry" (`fin_transaction`, `fin_journal_entry`, `fin_journal_line`, `fin_account_balance`; lines balance in functional currency or `UNBALANCED`; posted entries immutable and reversed, never edited; `ledger.postEvent(tx)` idempotent on `(source_type, source_id)`; accounts resolved by `subtype`, never code); §3 topics `invoice.*`, `payment.*`, `subscription.updated`, `payroll.run.*`, `ledger.entry.posted|reversed`; §6 row "Finance model and ledger posting". `moneySchema` here is the reference implementation until pending contracts issue A moves it into `@paperos/core/types`.

**Definition of done**

* Migrations apply on fresh and staging databases; cross-tenant harness green.
* Seeds create six charts; a test asserts every subtype named by any posting rule exists in each.
* Data dictionary regenerated (PAP-41); `docs/finance/data-model.md` published.
* Parties and accounts render as grid views in the demo tenant; screenshots at 375, 1024, 1920.
* ADR `docs/adr/00xx-finance-model.md`; CHANGELOG; Linear comment with doc link.

**Test plan**

* Unit: `Money` allocation sums exactly for 10k random splits, currency mismatch throws, JPY and KWD exponents, no float path (`fast-check`).
* Integration (PGlite and Postgres): period overlap rejected; `source` uniqueness rejects a duplicate import; `is_system` account delete blocked; RLS harness on every table; each seed chart passes the subtype test.
* E2E: create a party through the API, open `finance.parties` grid, edit terms inline.
* Visual: grid at 375, 1024, 1920 in light and dark.

**Demo**

Reviewer runs `pnpm db:seed --profile demo --business clinic`, opens `/finance/accounts` and sees the clinic chart of accounts grouped by type, then runs `pnpm tsx scripts/money-demo.ts` printing a 3-way allocation of 100.00 that sums exactly. Under two minutes.

**Edge cases**

* Party that is both customer and vendor: flags allow it; reports treat roles separately.
* Period locked while an import backdates: `CONFLICT` naming the earliest open period.
* Contractor becomes W-2: `employment_type` change audited, history kept.
* Deleting a system account blocked; deactivation only at zero balance (checked by PAP-179).
* Changing functional currency after transactions exist: blocked with explanation.

**Dependencies**

PAP-33 (hard), PAP-34 (hard), PAP-161 (dataset registry), PAP-27 (`Money` formatting), PAP-38. Blocks PAP-177, PAP-179, PAP-181, PAP-184, PAP-185.

**Agent**

Builder: Ledger (Bookkeeper). Reviewer: Forge (Schema Wright) on schema, Sentinel (Code Reviewer) on money helpers.

**Size**

M: schema and seeds are mechanical; the value is getting subtypes and mappings right.
