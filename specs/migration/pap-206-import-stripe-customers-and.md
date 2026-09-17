---
identifier: "PAP-206"
title: "Import Stripe customers and subscriptions and QuickBooks/Xero charts of accounts into the ledger"
project: "migration"
projectName: "Migration & Import Tools"
phase: "P2"
type: "Build"
priority: 4
surfaces: ["Staff"]
milestone: "Business migrations"
state: "Backlog"
parent: null
children: ["PAP-423", "PAP-424", "PAP-425"]
blockedBy: ["PAP-179", "PAP-199", "PAP-201", "PAP-349", "PAP-394"]
blocks: []
key: "migration/stripe-quickbooks"
url: "https://linear.app/paperos/issue/PAP-206/import-stripe-customers-and-subscriptions-and-quickbooksxero-charts-of"
source: "Linear snapshot 2026-09-17T13:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T13:05:45.105Z"
---

# PAP-206: Import Stripe customers and subscriptions and QuickBooks/Xero charts of accounts into the ledger

**Goal**

Deferred to v0.2 by the Execution Schedule (NJ-14 stop-loss 09-27 can reinstate). Not claimable before 10-01.

Let a business arrive with its finance history intact: Stripe customers, products, prices, subscriptions and invoices into CRM, billing and ledger; a QuickBooks Online or Xero chart of accounts with opening balances into the double-entry ledger; reports in PAP-183 correct from the conversion date. Umbrella for three work packages.

**Scope**

Work packages (full specs in the project document):

* **WP1 Stripe connector and postings** (M): `stripe` Node 18.x with restricted key or Connect account, auto-pagination with `created` cursors; customer -> `crm_contact|crm_company` plus finance customer; products and prices -> PAP-177 catalog marked `imported`; subscriptions; paid invoices -> PAP-180 records and balanced journals (AR, cash, revenue per product, fee expense from `balance_transaction.fee`, tax liability); refunds reversing; payouts as transfers.
* **WP2 QuickBooks and Xero connectors** (M): `intuit-oauth` Accounting API with CDC; `xero-node` 6.x with `If-Modified-Since`; chart of accounts to ledger `kind|code|name|parent|currency|is_active`; opening journal on the conversion date; optional history.
* **WP3 Finance wizard** (M): conversion date, account mapping review with suggested matches, duplicate customer resolution, trial balance gate per currency, reversing rollback via `ledger.reverseRun(run_id)`.

Out: writing back to any source, payroll history (PAP-181 scope), inventory, multi-entity consolidation.

**Spec**

* Amounts in minor units in transaction currency with base equivalent from the invoice rate or the rates table.
* Ledger immutability: rollback posts reversing entries dated at rollback time, never deletes.
* Every journal carries `source: import`, `run_id`, external ids.
* Order WP1 and WP2 in parallel, then WP3, on `PAP-206/wp<n>-<slug>`.

**Interface contract**

Provides: `registerConnector('stripe'|'quickbooks'|'xero')`, pure `postingRulesStripe(invoice): JournalLine[]` for Ledger review, `mapChartOfAccounts()`, `openingJournal()`, `trialBalance(preview)`, `ledger.reverseRun()`, component `JournalPreview` (reusable by PAP-180), wizard steps. Consumes: PAP-199, PAP-179 `postJournal` and accounts, PAP-175, PAP-177, PAP-180, PAP-183 (verification), PAP-187, PAP-201, PAP-198 work package 2 (test accounts) sandboxes. PAP-207 consumes the chart mapping for code conflicts.

**Definition of done**

* Three work packages merged and reported.
* Integration test: Stripe test account (50 customers, 3 products, 40 subscriptions, 120 invoices, 10 refunds), QuickBooks sandbox and Xero demo imported; PAP-183 P&L and balance sheet match source reports within rounding (comparison table attached); rollback returns the trial balance to its prior state.
* Posting rules document signed off by Ledger (Bookkeeper).
* Screenshots at 320, 375, 768, 1024, 1280, 1536 and 1920 in light and dark for account mapping and trial balance; axe clean.
* `docs/migration/finance-imports.md`; CHANGELOG; Linear comment with recordings and comparison.

**Test plan**

* Vitest: posting rules on 15 invoice fixtures (partial payments, credit notes, multi-currency, refunds) all balanced; every QuickBooks type and subtype and Xero class mapped; opening journal balances; cursors; trial balance offenders; reversing idempotence.
* Conformance suite for three connectors; recorded API responses in CI, live sandboxes weekly.
* Playwright: wizard with an unbalanced then a balanced fixture; visual baselines at the seven widths, both themes.

**Demo**

Reviewer connects the Stripe test account, walks the wizard, sees one duplicate customer resolved and the trial balance green, commits, then clicks Rollback and sees reversing entries in the journal. Under two minutes.

**Edge cases**

* Partially paid invoice or credit note: separate payment portions; credit notes reverse revenue.
* Missing or disabled QuickBooks codes: mapped by name, flagged, reserved range.
* Tracking categories and classes: dimensions if PAP-179 supports them, else tags.
* Journal references an unimported account: dry run stops with the dependency.
* Deleted Stripe customer: placeholder.
* Conversion date in tenant timezone.

**Dependencies**

PAP-199 and PAP-179 (hard). PAP-175, PAP-177, PAP-180, PAP-183, PAP-187, PAP-201; PAP-198 work package 2 (importer test accounts; integration tests read only its env names and skip with `skipped: no-credentials` when unset) for the live Stripe, QuickBooks and Xero runs.

**Agent**

Built by Scout (Import Mapper) with Ledger (Bookkeeper) owning posting rules and Iris on the wizard. Reviewed by Sentinel (Security Auditor, Code Reviewer, Visual Inspector) and Ledger.

**Size**

L umbrella; three M work packages. Pending sub-issue specs: [Round 2 pending issues: migration (20)](https://linear.app/paperos/document/round-2-pending-issues-migration-20-6cb063cc1be6)
