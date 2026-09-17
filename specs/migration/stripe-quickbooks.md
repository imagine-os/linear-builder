---
identifier: "PAP-206"
title: "Import Stripe customers and subscriptions and QuickBooks/Xero charts of accounts into the ledger"
project: "migration"
projectName: "Migration & Import Tools"
phase: "P2"
type: "Build"
priority: 3
surfaces: ["Staff"]
milestone: "Business migrations"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-179", "PAP-199", "PAP-201"]
blocks: []
key: "migration/stripe-quickbooks"
url: "https://linear.app/paperos/issue/PAP-206/import-stripe-customers-and-subscriptions-and-quickbooksxero-charts-of"
source: "plan/specs/bucket-7.json (round-1 canonical spec JSON)"
---

# PAP-206: Import Stripe customers and subscriptions and QuickBooks/Xero charts of accounts into the ledger

**Goal**

Let a business arrive with its finance history intact: import Stripe customers, products, prices, subscriptions and paid invoices into the CRM, billing and ledger tables, and import a QuickBooks Online or Xero chart of accounts with opening balances (and optionally historical journal lines) into the double-entry ledger, so reports in `business-core/finance-reports` are correct from day one.

**Scope**

In:
- Connector `packages/import/src/connectors/stripe/` using `stripe` Node 18.x with the tenant's restricted key or Connect account (read-only scopes): `discover` lists object types with counts; `stream` uses auto-pagination on `customers`, `products`, `prices`, `subscriptions` (all statuses), `invoices` (`status: paid|open|void|uncollectible`), `charges`, `refunds`, `payouts` with `created` cursors for incremental; respects rate limits with the SDK's retry.
- Stripe mapping: customer -> `crm_company` or `crm_contact` (by presence of a name with a domain email) plus `business-core/finance-data-model` customer with `stripe_customer_id`; products and prices -> `business-core/stripe-billing` catalog rows (marked `imported`, not re-created in Stripe); subscriptions -> subscription rows with status and period; paid invoices -> `business-core/invoicing` invoice records (PDF link kept) and ledger journal entries (debit AR then cash, credit revenue by product, Stripe fee expense from balance transactions, tax liability from `tax` amounts); refunds -> reversing entries; payouts -> cash transfers between Stripe balance and bank accounts.
- Connector `packages/import/src/connectors/quickbooks/` (OAuth 2 via `intuit-oauth`, Accounting API `Account`, `JournalEntry`, `Customer`, `Vendor`, `Invoice`, `Bill`, `Payment` with `CDC` for incremental) and `packages/import/src/connectors/xero/` (`xero-node` 6.x, `Accounts`, `Contacts`, `Invoices`, `ManualJournals`, `BankTransactions`, `If-Modified-Since` incremental).
- Chart of accounts mapping to `business-core/ledger` accounts: account type and subtype (or Xero class and type) -> ledger `kind: asset|liability|equity|revenue|expense`, `code`, `name`, `parent`, `currency`, `is_active`; opening balances as a single opening journal on the chosen conversion date; optional history import of journals and invoices after that date.
- Wizard steps: source pick, conversion date, account mapping review (suggested matches to the tenant's existing ledger accounts by code and name), duplicate customer resolution against existing CRM records, trial balance check before commit.

Out: pushing anything back to Stripe, QuickBooks or Xero; payroll history (`business-core/payroll-adapter` scope); inventory; multi-entity consolidation.

**Spec**

- Ledger integrity: dry run must produce a balanced trial balance (debits equal credits per currency) or the commit button is disabled with the offending entries listed.
- Every posted journal carries `source: import`, `run_id`, external ids; ledger immutability means rollback posts reversing entries, never deletes (framework rollback delegates to `ledger.reverseRun(run_id)`).
- Currency: amounts in minor units; multi-currency invoices posted in transaction currency with the tenant's base currency equivalent from the invoice's exchange rate when Stripe provides it, otherwise the finance rates table.
- Stripe fees taken from `balance_transaction.fee` per charge; missing balance transactions (old data) fall back to `application_fee` or zero with a warning.
- Duplicate policy: Stripe customer matching existing CRM contact by email links rather than creates; QuickBooks customers matching by name and email offer merge.
- Conversion date before earliest data: opening journal zero; history import covers everything.

**Definition of done**

- Vitest: every mapping rule with fixtures from `migration/format-research`; trial balance check; reversing rollback; incremental cursors; fee and tax splitting on 15 invoice fixtures including refunds and multi-currency.
- Integration: Stripe test-mode account seeded with 50 customers, 3 products, 40 subscriptions, 120 invoices and 10 refunds; QuickBooks sandbox company and Xero demo company; import all three, run `business-core/finance-reports` P&L and balance sheet and match them to the sandbox reports within rounding; recordings and comparison table attached.
- Playwright: wizard with account mapping and trial balance step; screenshots at 320, 375, 768, 1024, 1280, 1536 and 1920 in light and dark for account mapping and trial balance.
- Ledger review sign-off by Ledger (Bookkeeper) on posting rules document.
- `docs/migration/finance-imports.md`; CHANGELOG entry; Linear comment with recordings and report comparison.

**Edge cases**

- Stripe invoice partially paid or with credit notes: post payment portions separately; credit notes as reversing revenue entries.
- QuickBooks account codes disabled or missing: mapping by name only, flagged for review; codes generated in a reserved range.
- Xero tracking categories or QuickBooks classes: imported as ledger dimensions if `business-core/ledger` supports them, else tags with a note.
- Historical journal referencing an account the user chose not to import: run stops in dry run with the dependency listed.
- Stripe customer deleted but invoices remain: placeholder customer "Deleted Stripe customer <id>".
- Timezone of conversion date: interpreted in tenant timezone, documented on the wizard.

**Dependencies**

`migration/import-framework` and `business-core/ledger` (hard). `business-core/finance-data-model`, `business-core/stripe-billing`, `business-core/invoicing`, `business-core/finance-reports` (verification), `growth/crm-model`, `migration/id-mapping`.

**Agent**

Built by Scout (Import Mapper) with Ledger (Bookkeeper) owning posting rules. Reviewed by Sentinel (Security Auditor for key handling, Code Reviewer) and Ledger.

**Size**

L: three financial APIs and ledger correctness verified against source reports.
