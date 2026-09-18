# Round 4 digest: Business Core: Payments, Finance & Payroll (`business-core`)

Benchmarks: Stripe (Billing, Connect, Tax, Invoicing, Terminal, Radar, Billing Meters), QuickBooks Online, Xero, FreshBooks, Wave, Bill.com, Expensify, Square POS, Gusto, Rippling, Check, Deel, Toggl and Harvest (time), Brex and Ramp (spend), Chargebee and Stripe Billing (usage and recognition)

Feature matrix: 57 rows (27 covered, 6 partial, 24 gap). New issues: 25 (1 children, 24 gap issues; 20 deferred to v0.2). Amendments: 8. Cross-project suggestions: 4.

## Feature matrix

| Feature | Status | Covered by | Note |
|---|---|---|---|
| Finance data model: parties, chart of accounts, periods, Money | covered | PAP-175 | Six default charts; Money decided in contracts doc |
| Exchange rates and FX conversion | gap | r4/business-core/fx-rates-and-conversion | Referenced by five specs, defined nowhere |
| Ledger dimensions (department, location, project, class) | partial | PAP-183, r4/business-core/ledger-dimensions-registry | jsonb exists, no registry or validation |
| Platform plans, subscriptions, customer portal (Stripe Billing) | covered | PAP-177 |  |
| Entitlements and limits | covered | PAP-178 |  |
| Platform usage metering and metered prices | covered | PAP-391 | Amend to Billing Meters API |
| Double-entry journal, immutability, gapless numbering | covered | PAP-392 |  |
| Hash chain, reversals, period close and lock | covered | PAP-393 |  |
| Posting rule registry and journal UI | covered | PAP-394 |  |
| Finance permissions, role presets, separation of duties | gap | r4/business-core/finance-permissions-and-roles | Permissions invented per spec, never registered |
| Quotes, invoices, receipts, credit notes, bills model | covered | PAP-395 |  |
| Branded PDFs, public pay page, Checkout | covered | PAP-396 |  |
| Invoice postings, reminders, portal invoice list, emails | covered | PAP-397 |  |
| Recurring invoices and dunning ladder | partial | PAP-180, r4/business-core/recurring-invoices-dunning | Inline work package; now a child |
| Item and service catalogue with prices and accounts | gap | r4/business-core/item-catalogue | Lines are free text today |
| Discounts, coupons and promotion codes | gap | r4/business-core/discounts-and-promo-codes | PAP-408 assumes Stripe coupons |
| Deposits, retainers and instalment plans | gap | r4/business-core/deposits-retainers-installments | Agency and clinic packs need it |
| Refunds and customer credit balances | gap | r4/business-core/document-refunds-and-credit-balance | Credit notes exist, money never returns |
| Customer statements of account | gap | r4/business-core/customer-statements |  |
| Metered billing for tenant customers | gap | r4/business-core/tenant-metered-billing | PAP-180 out; SaaS pack needs it |
| Revenue recognition and deferred revenue | gap | r4/business-core/revenue-recognition |  |
| Stripe Connect onboarding, direct charges, payouts | covered | PAP-181 |  |
| Connect reconciliation and discrepancy dataset | covered | PAP-181 |  |
| Disputes, chargebacks, Radar rules | partial | PAP-181, r4/business-core/disputes-radar-evidence | Postings only; no inbox or evidence |
| Sales tax and VAT (Stripe Tax) with evidence | covered | PAP-182 | Deferred v0.2 |
| P&L, balance sheet, cash flow, aging, GL, trial balance | covered | PAP-183 |  |
| Report exports CSV, XLSX, PDF | covered | PAP-183 |  |
| Budgets and variance reporting | gap | r4/business-core/budgets-and-variance | PAP-183 out |
| Cash-flow dashboard and runway | covered | PAP-186 | MRR source needs amendment |
| Cash forecast scenarios | gap | r4/business-core/cash-forecast-scenarios | PAP-186 out |
| Bank feeds and statement import | gap | r4/business-core/bank-feed-port-and-statement-import |  |
| Bank reconciliation and matching | gap | r4/business-core/bank-reconciliation-matching |  |
| Vendor bills, approval and AP payments | gap | r4/business-core/vendor-bills-and-ap-payments | bill kind exists, no AP workflow |
| Purchase orders and receiving | gap | r4/business-core/purchase-orders-and-receiving |  |
| Inventory stock and COGS | gap | r4/business-core/inventory-stock-and-cogs | Retail and restaurant packs |
| Expense capture with receipt OCR | covered | PAP-185 | Deferred v0.2 |
| Mileage and per diem | gap | - | v0.3; PAP-185 out; no issue this round |
| Payroll provider research and ADR | covered | PAP-176 |  |
| Payroll adapter, webhooks, contract suite | covered | PAP-398 |  |
| Payroll company and employee onboarding | covered | PAP-399 |  |
| Payroll runs, approval, postings, paystubs | covered | PAP-400 |  |
| Contractors and 1099 tracking | gap | r4/business-core/contractors-and-1099 |  |
| Timesheets, time-off and hours into payroll | gap | r4/business-core/timesheets-to-payroll-hours | PAP-184 out |
| Payroll filings status, W-2 and 1099 forms, deductions and benefits mapping | gap | r4/business-core/payroll-filings-forms-and-deductions |  |
| Point of sale and Stripe Terminal | gap | r4/business-core/stripe-terminal-pos |  |
| Year-end close and closing entries | gap | r4/business-core/year-end-close |  |
| Fixed assets and depreciation | gap | - | v0.3; no issue this round |
| Multi-entity consolidation | gap | - | Explicit non-goal (PAP-183); v0.3 |
| PCI SAQ-A posture and key custody | covered | PAP-359 |  |
| Finance demo seed and golden fixtures | partial | PAP-183, PAP-487, r4/business-core/finance-demo-seed | Three issues each seed their own numbers |
| Contract package, conformance, kernel wiring | covered | PAP-484, PAP-487, PAP-490 |  |
| Accountant hand-off exports (GL CSV) | partial | PAP-183, PAP-420 | Covered by report exports and archive; no QBO-shaped file |
| Tenant webhooks for finance events | covered | PAP-222 | Identity project; deferred |
| Notifications for finance alerts | covered | PAP-186, PAP-136 |  |
| Multi-currency documents and FX gain or loss postings | partial | PAP-397, r4/business-core/fx-rates-and-conversion | Needs the rates table |
| Audit trail on money movement | covered | PAP-38, PAP-393 |  |
| Agent guardrails on money (draft only, deny list) | covered | PAP-359, PAP-298 |  |

## New issues

| Key | Title | Parent | Size | Model / effort | Prio | Deferred | Milestone |
|---|---|---|---|---|---|---|---|
| `r4/business-core/recurring-invoices-dunning` | Recurring invoice schedules, dunning ladder with late fees and saved-card retry on the connected account | PAP-180 | M (3) | Opus 5 / high | 2 | no | Ledger and reports |
| `r4/business-core/fx-rates-and-conversion` | Exchange rate table and FX service: daily rates job with a fixture provider, rateAt lookup, functional-currency conversion and realised gain or loss helpers | - | S (2) | Sonnet 5 / medium | 2 | no | Ledger and reports |
| `r4/business-core/finance-demo-seed` | Finance demo seed: twelve months of balanced journals, invoices, bills, subscriptions and payroll runs for the demo tenant and the conformance fixtures | - | S (2) | Haiku 4.5 / low | 2 | no | Ledger and reports |
| `r4/business-core/finance-permissions-and-roles` | Finance permission set and role presets: bookkeeper, accountant read-only, payroll admin and billing admin, with the ledger:post and payroll.approve guards in the permission matrix | - | S (2) | Opus 5 / high | 2 | no | Ledger and reports |
| `r4/business-core/ledger-dimensions-registry` | Ledger dimension registry: department, location, project and class dimensions per tenant, validated on posting and exposed as report filters | - | S (2) | Sonnet 5 / medium | 3 | no | Ledger and reports |
| `r4/business-core/bank-feed-port-and-statement-import` | Bank feed port with a fixture adapter and statement import (CSV, OFX, CAMT.053) into bank accounts and bank transactions | - | M (3) | Sonnet 5 / high | 4 | yes | Payroll adapter and cash dashboard |
| `r4/business-core/bank-reconciliation-matching` | Bank reconciliation: automatic matching rules, suggested matches, split and create-from-bank actions, reconciliation statement and month-end lock check | - | M (3) | Sonnet 5 / high | 4 | yes | Payroll adapter and cash dashboard |
| `r4/business-core/vendor-bills-and-ap-payments` | Vendor bills and accounts payable: bill entry and approval, due-date scheduling, payment batches via Stripe or manual, remittance advice and AP postings | - | M (3) | Opus 5 / high | 4 | yes | Payroll adapter and cash dashboard |
| `r4/business-core/purchase-orders-and-receiving` | Purchase orders and receiving: PO editor from vendor items, approval, partial receipts, three-way match to vendor bills and open-PO reporting | - | M (3) | Sonnet 5 / medium | 4 | yes | Payroll adapter and cash dashboard |
| `r4/business-core/item-catalogue` | Item catalogue: products and services with SKU, prices per currency, default revenue and expense accounts, tax codes and Stripe Price sync for tenant checkout | - | M (3) | Sonnet 5 / high | 4 | yes | Ledger and reports |
| `r4/business-core/inventory-stock-and-cogs` | Inventory stock levels and COGS: stock movements per location, weighted-average and FIFO costing, cost of goods sold postings on sale, adjustments and low-stock alerts | - | M (3) | Opus 5 / high | 4 | yes | Payroll adapter and cash dashboard |
| `r4/business-core/customer-statements` | Customer statements and account balances: per-party statement of account with running balance, PDF and portal download, batch send and overdue summary | - | S (2) | Sonnet 5 / medium | 4 | yes | Ledger and reports |
| `r4/business-core/deposits-retainers-installments` | Deposits, retainers and installment plans: partial payment schedules on quotes and invoices, retainer balances with drawdown, deferred liability postings | - | M (3) | Opus 5 / high | 4 | yes | Payroll adapter and cash dashboard |
| `r4/business-core/discounts-and-promo-codes` | Discounts and promotion codes: tenant-level coupon rules for quotes, invoices and checkout plus Stripe Coupons and Promotion Codes for platform plans | - | M (3) | Sonnet 5 / medium | 4 | yes | Payroll adapter and cash dashboard |
| `r4/business-core/disputes-radar-evidence` | Disputes and fraud controls: Stripe Radar rules per tenant, dispute inbox with evidence assembly from documents and activity, deadlines, outcome postings | - | S (2) | Sonnet 5 / medium | 4 | yes | Payroll adapter and cash dashboard |
| `r4/business-core/budgets-and-variance` | Budgets and variance: per-account and per-dimension budgets by period, budget import from spreadsheet, variance columns in the P&L and threshold alerts | - | M (3) | Sonnet 5 / medium | 4 | yes | Payroll adapter and cash dashboard |
| `r4/business-core/contractors-and-1099` | Contractor payments and 1099 tracking: contractor onboarding through the payroll provider, payments via provider or Connect transfers, W-9 status, 1099-NEC threshold tracking and year-end forms | - | M (3) | Opus 5 / high | 4 | yes | Payroll adapter and cash dashboard |
| `r4/business-core/timesheets-to-payroll-hours` | Timesheets and time-off: time entries with approval, PTO policies and balances through the provider where supported, and hours flowing into the payroll run grid | - | M (3) | Sonnet 5 / high | 4 | yes | Payroll adapter and cash dashboard |
| `r4/business-core/stripe-terminal-pos` | Point of sale with Stripe Terminal: in-person checkout screen from the item catalogue, reader pairing and simulated reader, tips, receipts and daily Z-report postings | - | M (3) | Opus 5 / high | 4 | yes | Payroll adapter and cash dashboard |
| `r4/business-core/year-end-close` | Year-end close and closing entries: retained earnings roll-forward, close checklist, accountant review package and reopening rules | - | S (2) | Sonnet 5 / medium | 4 | yes | Payroll adapter and cash dashboard |
| `r4/business-core/revenue-recognition` | Revenue recognition schedules: deferred revenue for prepaid periods and multi-period services, monthly recognition job and deferred revenue roll-forward report | - | M (3) | Opus 5 / high | 4 | yes | Payroll adapter and cash dashboard |
| `r4/business-core/document-refunds-and-credit-balance` | Refunds and customer credit balances: refund a paid document through Stripe or manually, credit note application to future invoices, credit balance tracking and postings | - | M (3) | Opus 5 / high | 4 | yes | Ledger and reports |
| `r4/business-core/payroll-filings-forms-and-deductions` | Payroll filings, year-end forms and deduction codes: provider filing status, W-2 and 1099 availability in the portal, benefit and garnishment deduction mapping to ledger accounts | - | S (2) | Sonnet 5 / medium | 4 | yes | Payroll adapter and cash dashboard |
| `r4/business-core/tenant-metered-billing` | Metered billing for tenants' own customers: usage meters on items, usage ingestion API, monthly usage invoicing through recurring schedules and Stripe Billing Meters on the connected account | - | M (3) | Sonnet 5 / high | 4 | yes | Payroll adapter and cash dashboard |
| `r4/business-core/cash-forecast-scenarios` | Cash forecast scenarios: 13-week projection from open AR and AP, recurring schedules, payroll calendar and manual assumptions with best, base and worst cases | - | M (3) | Sonnet 5 / medium | 4 | yes | Payroll adapter and cash dashboard |

## Amendments to existing specs

* **PAP-186** (Spec): Round 4 clarification: `finance.mrr` cannot read 'active subscriptions on the connected account' because PAP-181 creates no subscription model and PAP-177 subscriptions are PaperOS's own plans. Compute tenant MRR from active `fin_recurring_schedule` rows (`r4/business-core/recurring-invoices-dunning`, normalised monthly) plus imported Stripe subscriptions when PAP-423 has run; show 'n/a' with an enable link when neither exists.
* **PAP-391** (Spec): Round 4: Stripe deprecated `subscriptionItems.createUsageRecord` in favour of Billing Meters. For the pinned `apiVersion`, use `billing.meterEvents.create({ event_name, payload: { stripe_customer_id, value } })` with `meterId` declared per metered price in `plans.ts`, keep the usage-record path only behind a `legacyUsageRecords` flag for older API versions, and store `stripe_meter_event_id` instead of `stripe_usage_record_id`.
* **PAP-175** (Spec): Round 4: `convert(rate)` takes a rate from `fin_fx_rate` owned by `r4/business-core/fx-rates-and-conversion`; PAP-183, PAP-185, PAP-206 and PAP-423 must call `fx.rateAt` rather than keeping their own rates. Add `fin_item` (`r4/business-core/item-catalogue`) and `fin_dimension` (`r4/business-core/ledger-dimensions-registry`) to the ER diagram as planned tables.
* **PAP-177** (Edge cases): Round 4: the concurrent-upgrade refund is executed by the webhook worker with the restricted key that has refund scope, never by an agent session (deny list, PAP-298) and never in live mode without the PAP-359 custody card; the integration test uses a Stripe test clock and `stripe trigger` only.
* **PAP-399** (Definition of done): Round 4: the CI gate is the mock adapter path (onboarding, sync, conflict review) with recorded fixtures; the sandbox recording is attached when `PAYROLL_SANDBOX_KEY` exists and otherwise the test reports `skipped: no-credentials`, so this child is mergeable before NJ-12 resolves.
* **PAP-183** (Dependencies): Round 4: the `dimensions` parameter resolves keys and options through `r4/business-core/ledger-dimensions-registry` (soft; until it lands only free-form `department` from payroll postings is accepted). Textbook expected values come from `r4/business-core/finance-demo-seed` so PAP-186 and PAP-487 agree to the cent.
* **PAP-181** (Edge cases): Round 4: dispute evidence deadlines, the evidence pack and the `won|lost` outcome postings move to `r4/business-core/disputes-radar-evidence`; this issue only posts the reserve movement on `charge.dispute.created` and emits `connect.dispute.opened` with `evidence_due_by`.
* **PAP-395** (Spec): Round 4: line editors accept an optional `item_id` from `r4/business-core/item-catalogue` that pre-fills description, unit price, revenue account and tax code; the line snapshots those values at issue, so catalogue edits never rewrite issued documents. `computeTotals` exposes a `discounts` hook consumed by `r4/business-core/discounts-and-promo-codes`.

## Cross-project suggestions

* **growth**: Deal products and quote-from-deal use the finance item catalogue — CRM deals need line items priced from `fin_item` and a 'create quote' action through `documents.create`; growth owns the UI, business-core the catalogue (`r4/business-core/item-catalogue`).
* **identity**: Portal customer to finance party link (`fin_party.user_id`) surfaced in the portal shell — Statements, credit balances, contractor pages and paystubs all resolve the logged-in customer to a party; PAP-62 should expose `usePortalParty()` once rather than each finance page re-deriving it.
* **data-layer**: Monthly partition helper for finance event tables — `fin_usage_event`, `usage_event` (PAP-391) and `attr_event` (PAP-194) each write their own partition-ahead job; one `definePartitionedTable()` helper in `packages/db` would remove three copies.
* **tables**: `Money` field editor with currency picker and per-currency exponent — Budget grids, item prices and bank transaction grids edit `Money` inline; PAP-164 has a currency type but the editor must honour ISO exponents (JPY 0, KWD 3) and never round through floats.

## What was missing and why it matters

1. Five specs depend on an exchange-rate table that no issue owns; multi-currency books, imports and receipts would each have invented one (`fx-rates-and-conversion`).
2. Eleven finance specs invent permissions and none registers them or separates duties; money-moving approvals were unverifiable in the PAP-64 matrix (`finance-permissions-and-roles`).
3. The receivables side was complete but the payables side stopped at a `bill` kind: no bill approval, AP payments, purchase orders, bank feeds or reconciliation, so the `cash` account could never be proven against the bank.
4. Every vertical the brief names sells things: an item catalogue, inventory with COGS, POS, discounts, deposits and refunds were absent, leaving invoice lines as free text and gross profit unmeasurable.
5. Recurring billing lived as an inline work package inside an umbrella and PAP-186's MRR pointed at a model that does not exist; both are now claimable, consistent issues.
