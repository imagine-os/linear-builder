---
key: "child/PAP-206/0"
title: "Stripe connector and mapping: customers to CRM, catalog and subscriptions to billing, invoices, fees, tax, refunds and payouts to ledger postings"
project: "migration"
parent: "PAP-206"
phase: "P2"
type: "Build"
priority: 3
size: "M"
surfaces: ["Staff"]
milestone: "Business migrations"
intendedState: "Backlog"
blockedBy: []
blocks: []
source: "round2/agent5/pending-issues.json"
linearDocument: "https://linear.app/paperos/document/round-2-pending-issues-migration-20-6cb063cc1be6"
status: "pending"
---

# Stripe connector and mapping: customers to CRM, catalog and subscriptions to billing, invoices, fees, tax, refunds and payouts to ledger postings

**Goal**

Bring a business's Stripe history in correctly: customers, products, prices, subscriptions, invoices, charges, refunds and payouts stream through the framework and post balanced journal entries with fees, tax and refunds split the way the ledger expects.

**Scope**

In: `connectors/stripe/` on `stripe` Node 18.x with restricted read-only key or Connect account; auto-pagination with `created` cursors; `mapping/stripe.ts`: customer -> `crm_contact|crm_company` plus finance customer with `stripe_customer_id`; products and prices -> PAP-177 catalog rows marked `imported`; subscriptions -> subscription rows; paid invoices -> PAP-180 invoice records and PAP-179 journals (debit AR then cash, credit revenue per product, fee expense from `balance_transaction.fee`, tax liability); refunds reversing; payouts as transfers.

Out: QuickBooks and Xero (child 2), wizard and trial balance gate (child 3).

**Spec**

* Amounts in minor units in transaction currency with base-currency equivalent from the invoice rate or the finance rates table.
* Missing balance transactions fall back to `application_fee` or zero with a warning.
* Existing CRM contact with the same email is linked, not duplicated.

**Interface contract**

Provides: `registerConnector('stripe', ...)`, `postingRulesStripe` (pure function invoice -> journal lines, exported for Ledger review), fixture set of 15 invoices. Consumes: PAP-199 child 1, PAP-179 `postJournal`, PAP-177 catalog, PAP-180 invoices, PAP-187 CRM, PAP-201.

**Definition of done**

* Test-mode account (50 customers, 3 products, 40 subscriptions, 120 invoices, 10 refunds) imports; P&L from PAP-183 matches Stripe's balance report within rounding (comparison table attached).
* Posting rules document signed off by Ledger (Bookkeeper).

**Test plan**

* Vitest: posting rules on 15 invoice fixtures including partial payments, credit notes, multi-currency, refunds; every journal balances.
* Integration: recorded Stripe responses; then live test-mode run from the test-accounts issue.
* Contract test via `connectorConformance()`.

**Demo**

Reviewer runs `pnpm paperos import --connector stripe --dry` against the seeded test account and sees invoice counts, then opens the generated journal preview where debits equal credits for each currency. Under two minutes.

**Edge cases**

* Customer deleted but invoices remain: placeholder "Deleted Stripe customer <id>".
* Subscription with trial and proration lines: proration posted as revenue adjustment.
* Payout to an unknown bank account: cash account chosen in child 3 wizard.

**Dependencies**

PAP-199 child 1 (hard), PAP-179 (hard), PAP-177, PAP-180, PAP-187, PAP-201, test-accounts issue. Blocks child 3.

**Agent**

Built by Scout (Import Mapper) with Ledger (Bookkeeper) owning posting rules. Reviewed by Sentinel (Security Auditor, Code Reviewer) and Ledger.

**Size**

M
