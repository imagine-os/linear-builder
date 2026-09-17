# Rewritten specs for business-core PAP-181..PAP-186.
SPECS = {}
def add(k, **s): SPECS[k] = s

add("PAP-181",
Goal="""Let tenants accept payments from their own customers and receive payouts through Stripe Connect: one connected account per tenant, direct charges with a platform application fee, connected-account webhooks, and ledger postings for fees, payouts and balances so a tenant's books stay complete.""",
Scope="""In: table `connect_account`; procedures `connect.*`; webhook route `/api/webhooks/stripe-connect`; `/org/settings/payments` onboarding UI; `createConnectedCheckout` helper used by PAP-180 and PAP-196; posting rules `payout.paid`, `application_fee.created`, `charge.dispute.*`; nightly balance-transaction reconciliation and the `/finance/reconciliation` dataset.

Out: Terminal, Issuing, multi-account splits per charge, live-mode activation (Justin approves separately).""",
Spec="""* Express by default (`controller: { fees: { payer: 'application' }, losses: { payments: 'application' }, stripe_dashboard: { type: 'express' } }`); Standard selectable per tenant; capabilities `card_payments`, `transfers`; country from the tenant address.
* `connect_account (tenant_id unique, stripe_account_id, type, country, default_currency, charges_enabled, payouts_enabled, details_submitted, requirements jsonb, payout_schedule jsonb, updated_from_event_id)`.
* `connect.start` creates the account and an Account Link; `connect.refreshLink`, `connect.loginLink`; `account.updated` keeps flags current; UI maps `requirements.currently_due` to plain language.
* Direct charges: `stripe.checkout.sessions.create({...}, { stripeAccount })` with `application_fee_amount = platformFee(plan, amount)` from `plans.platformFeeBps` (PAP-177); refunds with a configurable `refund_application_fee` policy.
* Connected webhooks share `stripe_event` with an `account` column; handlers create `fin_transaction` rows (`payment|refund|fee|payout|adjustment`) and post: payments debit `stripe_balance`, payouts move `stripe_balance` to `cash`, fees debit `fees`, disputes to `disputes_reserve`.
* Reconciliation: nightly `balance_transactions.list` per account; every Stripe balance transaction maps to a `fin_transaction` or appears in the discrepancy dataset with "create from Stripe".
* `payments.manage` for owner and admin; agents read-only.""",
Contract="""Provides: `connect.start|refreshLink|loginLink|status`, `createConnectedCheckout({ tenantId, amountMinor, currency, metadata, successUrl, cancelUrl })`, `createTransfer({ tenantId, destinationAccountId, amountMinor })` for PAP-196, `connectedAccountFor(tenantId)`, events `connect.account.updated`, `connect.payout.paid`, `connect.dispute.opened`, dataset `finance.reconciliation`. Consumes: Stripe client, `stripe_event`, plans (PAP-177), posting (PAP-179), transactions and parties (PAP-175), notifications for disputes and restrictions (PAP-136 core). Consumed by PAP-180, PAP-182 (per-account tax settings), PAP-186 MRR, PAP-196.""",
DoD="""* Test-mode flow recorded: onboard an Express account, pay an invoice link, observe fee and payout events, balanced ledger entries.
* Vitest, integration and Playwright below green; reconciliation shows zero discrepancies on the demo tenant after a seeded day.
* `docs/finance/connect.md` with the live activation checklist for Justin; ADR on Express plus direct charges; CHANGELOG; Linear comment with replay.""",
Test="""* Unit: `platformFee` per plan and cap; handler idempotency and ordering; requirements mapping; reconciliation diff on fixtures.
* Integration: `stripe trigger` for `account.updated`, `payout.paid`, `charge.dispute.created` against a test connected account; each yields the expected `fin_transaction` and posting; unknown `stripe_account_id` acknowledged and logged.
* E2E: settings page in not-started, requirements-due, enabled and restricted states from seeded rows.
* Visual: 375, 1024, 1920 in three themes for the four states.""",
Demo="""Reviewer clicks "Accept payments" on the demo tenant, completes Stripe's test onboarding, returns to see `charges_enabled`, pays a seeded invoice with `4242`, then opens `/finance/journal` to see the payment, fee and (after `stripe trigger payout.paid`) payout entries. Under two minutes.""",
Edge="""* Account restricted mid-month: charges blocked, invoices show bank-transfer instructions, banner to finance.
* Payout failed: amount stays in `stripe_balance`, alert, no cash posting.
* Refund exceeding connected balance: receivable from tenant posted and flagged.
* Express to Standard switch: new account, old one kept for history.
* Connected currency differs from functional: FX captured at payout.""",
Deps="""PAP-177 (hard), PAP-179 (hard), PAP-175 (hard), PAP-136 core (soft). Blocks PAP-196; optional for PAP-180, PAP-182, PAP-186.""",
Agent="""Builder: Ledger (Payments Integrator). Reviewer: Sentinel (Security Auditor, Code Reviewer); Bookkeeper checks postings.""",
Size="""M: Stripe hosts onboarding; webhook and reconciliation correctness is the substance.""")

add("PAP-182",
Goal="""Handle sales tax and VAT without spreadsheets: Stripe Tax calculates tax on Checkout, subscriptions and invoices, customer tax IDs are collected and validated, evidence per transaction (jurisdiction, rate, amounts, location evidence, calculation id) lives in our tables for audits, and liabilities post to the ledger.""",
Scope="""In: tables `fin_tax_registration`, `fin_tax_evidence`, `fin_tax_rate`; procedures `tax.*`; Stripe Tax on Checkout and Billing plus the Tax Calculation API for documents charged outside Checkout; `/org/settings/tax`; report dataset `finance.taxSummary`.

Out: filing returns, customs and duties, payroll taxes (PAP-184).""",
Spec="""* Enable Stripe Tax on the platform and connected accounts (`tax.settings` with head office and default `tax_code`, for example `txcd_10000000`); `fin_tax_registration (jurisdiction, type, active_from, active_to, stripe_registration_id)` mirrors `tax.registrations`; `tax.addRegistration` writes both.
* Checkout and subscriptions: `automatic_tax: { enabled: true }`, `customer_update.address: 'auto'`, `tax_id_collection` for B2B; validated IDs stored on `fin_party.tax_id` with type and status.
* Documents outside Checkout: `tax.calculate(documentId)` calls `stripe.tax.calculations.create` with lines, address and IDs, writes `fin_document_line.tax_minor` and evidence rows; on payment `transactions.createFromCalculation` stores `stripe_tax_transaction_id`; void and credit notes call `createReversal`.
* `fin_tax_evidence (document_id?, transaction_id?, calculation_id, tax_transaction_id?, jurisdiction jsonb, tax_type, rate_pct numeric(8,4), taxable_minor, tax_minor, currency, taxability_reason, customer_location_evidence jsonb, reverse_charge, source: stripe|manual, created_at)`; immutable; retained 10 years.
* Posting: tax credits `sales_tax_payable` with dimension `tax_jurisdiction` inside the PAP-180 `invoice.issued` rule, which reads evidence rows; reverse charge posts nothing.
* Tenant toggle for tax-inclusive pricing sets `tax_behavior: inclusive`.
* Manual fallback when Stripe Tax is off or unsupported: `fin_tax_rate (name, rate, jurisdiction, account_id)` with per-line selection and `source: manual` evidence.
* `tax.manage` for finance staff; evidence readable by finance and the auditor role (PAP-62) if present.""",
Contract="""Provides: `tax.calculate(documentId)`, `tax.addRegistration|listRegistrations|settings`, `tax.rates.*`, `TaxEvidence` type, dataset `finance.taxSummary` (jurisdiction by period: taxable, collected, reversed, filing placeholder, CSV export), a `taxLinesFor(document)` helper PAP-180 calls before issue. Consumes: Stripe client and Checkout (PAP-177), documents and `invoice.issued` rule (PAP-180), connected accounts (PAP-181), report rendering (PAP-183), `fin_party.tax_id` (PAP-175).""",
DoD="""* Vitest and Stripe test-mode integration below green.
* Playwright: settings with registrations, invoice with tax lines, tax summary grid; screenshots at 375, 1024, 1920 in three themes.
* `docs/finance/tax.md` including "what Stripe Tax does not do" and the manual path; ADR; CHANGELOG; Linear comment with report screenshot and a test evidence sample.""",
Test="""* Unit: calculation to line mapping, evidence writes, reverse-charge logic, inclusive versus exclusive totals to the cent, retroactive registration leaves past documents untouched.
* Integration (test mode): US address with a nexus registration produces tax; EU B2B with a valid VAT ID produces reverse charge; missing address returns `requires address`; partial refund creates a proportional reversal; manual fallback produces `source: manual` evidence.
* E2E: add a registration, issue a taxed invoice, open the summary report and export CSV.
* Visual: 375, 1024, 1920 in three themes.""",
Demo="""Reviewer adds a California registration in `/org/settings/tax`, issues an invoice to a Los Angeles customer and sees the tax line appear with the jurisdiction tooltip, then opens the tax summary report showing the collected amount. Under two minutes.""",
Edge="""* Missing customer address: issue blocked with a request-address email action.
* Tax ID pending or invalid: tax charged and flagged; re-run when valid.
* Rate change mid-period: evidence keeps the rate used.
* Refund after transaction: proportional reversal.
* Connected account in an unsupported country: manual rates with a banner.""",
Deps="""PAP-177 (hard), PAP-180 (hard), PAP-181 (soft, per-account settings), PAP-183 (consumer). Blocks nothing hard.""",
Agent="""Builder: Ledger (Payments Integrator) with Bookkeeper on postings. Reviewer: Sentinel (Code Reviewer, Edge Case Hunter with cross-border cases).""",
Size="""M: Stripe Tax handles rates; evidence, fallbacks and reporting are the work.""")

add("PAP-183",
Goal="""Produce books a founder can read: P&L, balance sheet, cash flow (indirect), AR and AP aging, general ledger and trial balance, generated from the ledger and documents as datasets in the views engine so they inherit grouping, filtering, drill-down, export and dashboard embedding.""",
Scope="""In: `packages/finance/src/reports/` (`defineReport`, SQL builders, dataset registrations `finance.pnl|balanceSheet|cashFlow|arAging|apAging|trialBalance|generalLedger`); `/finance/reports/:key` with a parameter bar and saved report views; drill-down to entries and documents; CSV, XLSX (`exceljs` 4.x) and PDF (dashboard print route); `fin_report_snapshot` cache; number blocks for PAP-186.

Out: budgeting and forecasting, consolidation, a custom report builder (saved views cover it).""",
Spec="""* Shared params: `period` presets (`thisMonth|lastMonth|thisQuarter|ytd|lastYear|custom`) resolved with `fiscal_year_start_month`, `comparison` (`none|previousPeriod|previousYear`), `basis` (`accrual|cash`), `dimensions`, functional currency only.
* P&L: revenue and expense accounts grouped by parent with subtotals (Gross profit when `cogs` exists, Operating income, Net income); comparison columns with variance amount and percent; closed periods from `fin_account_balance`, open period from live lines.
* Balance sheet as of `period.end`; retained earnings computed; must balance or shows "Out of balance by X" linking `ledger.verifyChain`.
* Cash flow indirect: net income, non-cash adjustments, working-capital deltas from `ar`, `ap`, `sales_tax_payable`, `payroll_liability` subtypes; reconciles to the change in `cash` plus `stripe_balance`.
* AR aging from open invoices, AP aging from `bill` documents, buckets `current, 1-30, 31-60, 61-90, 90+` as of a chosen date.
* `defineReport({ key, params, build(params, ctx) => SQL, columns, rowKind })` registers a dataset with computed `FieldDef`s; rows carry `drill: { kind, filter }`.
* Snapshots for closed periods in `fin_report_snapshot (tenant_id, key, params_hash, rows, generated_at)`, invalidated on `ledger.entry.posted` into that period.
* `reports.read` for finance staff and owners.""",
Contract="""Provides: `defineReport`, `ReportParams` type, the seven datasets, number blocks `finance.netIncome|cash|arOutstanding|apOutstanding` via PAP-173 `defineNumberBlock`, `exportReport(key, params, 'csv'|'xlsx'|'pdf')`, route `/finance/reports/:key`. Consumes: balances and entries (PAP-179), documents (PAP-180), grid and compiler (PAP-165, PAP-163), dashboard blocks and print (PAP-173), saved views (PAP-172), `fin_settings` (PAP-175). Consumed by PAP-186, PAP-182 summary rendering, PAP-206 migration verification.""",
DoD="""* Vitest, property and Playwright below green; P&L on 100k journal lines under 1 s.
* Screenshots at 375, 768, 1024, 1440, 1920 in three themes; P&L PDF snapshot.
* `docs/finance/reports.md` explaining each derivation; CHANGELOG; Linear comment with demo links.""",
Test="""* Unit: textbook fixture of 60 entries with known answers for all five statements on both bases, to the cent; fiscal year starting July; aging as-of dates.
* Property (`fast-check`): random balanced entries always balance the balance sheet and reconcile cash flow.
* Integration: snapshot invalidation on a new posting; drill filter reproduces the report line total; XLSX opens with `exceljs` and matches CSV.
* E2E: open each report, change period, compare previous year, drill to entries, export CSV.
* Visual: matrix above plus the out-of-balance warning state.""",
Demo="""Reviewer opens `/finance/reports/pnl` on the seeded tenant, switches to "this quarter versus previous year", clicks the Revenue line to see its journal entries, exports XLSX, then opens AR aging and clicks a 61-90 bucket to see the invoices. Under two minutes.""",
Edge="""* Unposted drafts excluded with an "n drafts not included" badge.
* Zero-activity accounts hidden, toggle to show.
* Multi-currency lines shown in functional amounts with a currency footnote.
* Empty comparison shows "n/a", never divides by zero.
* Payments after the aging as-of date ignored so history is reproducible.""",
Deps="""PAP-179 (hard), PAP-180 (hard, aging and bills), PAP-165 and PAP-163 (hard), PAP-173 (number blocks and print), PAP-172 (saved views). Blocks PAP-186.""",
Agent="""Builder: Ledger (Bookkeeper). Reviewer: Sentinel (Code Reviewer, Edge Case Hunter); Quill reviews the derivation docs.""",
Size="""M: SQL and fixtures dominate; UI comes from the views engine.""")

add("PAP-184",
Goal="""Implement the `PayrollProvider` interface chosen in PAP-176 and its first adapter (Check by default) so a tenant onboards employees, previews and approves a payroll run and sees paystubs inside PaperOS, with every approved run posted to the ledger. Sandbox only until Justin approves live. Umbrella for three children.""",
Scope="""Children (M each, same milestone, Backlog):

* {{business-core/payroll/adapter-contract}} Finalised `provider.ts`, the first adapter with idempotency keys, webhook route and signature handling, the adapter contract test suite.
* {{business-core/payroll/onboarding-sync}} Tables, company and employee onboarding via provider links, employee sync from `fin_employee` with a conflict review list, status polling fallback.
* {{business-core/payroll/run-approve-post}} Run flow UI (hours grid, preview, typed-total approval), status transitions from webhooks, `payroll.approved` and `payroll.paid` posting, paystub portal page.

Out: benefits, time tracking, international payroll, live filings.""",
Spec="""Decisions binding all children:

* Adapter methods map to provider REST with the TypeScript SDK if one exists, else `ky` 1.x with Zod responses; every mutation carries idempotency key `paperos:<tenant>:<entity>:<version>`; `capabilities()` drives the UI.
* `payroll_company (tenant_id unique, provider, external_company_id, onboarding_status, pay_frequency, next_pay_date, bank_verified, updated_from_event_id)`; `payroll_employee_link (party_id, external_employee_id, onboarding_status, ssn_last4_masked?, w4_complete)`; `payroll_run (external_run_id, period_start, period_end, pay_date, status: draft|previewed|approved|processing|paid|failed|cancelled, totals jsonb, approved_by, approved_at, ledger_entry_id)`; `payroll_run_item` per employee; `payroll_event` for webhook idempotency.
* Approval needs `payroll.approve` and typing the net total; cancel allowed until the provider cutoff; agents may draft, never approve.
* Posting on `approved`: debit `wages_expense`, `payroll_tax_expense`, `payroll_fees`; credit `payroll_liability` (net) and `payroll_tax_liability`; on `paid` move `payroll_liability` to `cash`; dimensions from employee department.
* No SSNs or bank numbers stored; provider secrets via PAP-17; every approve and cancel audited.""",
Contract="""Provides: `PayrollProvider` implementation registry `payrollProviders[id]`, `payroll.company.*`, `payroll.employees.sync|list`, `payroll.runs.create|preview|approve|cancel|list|get`, `payroll.paystubs.list|url`, webhook route `/api/webhooks/payroll/:provider`, events `payroll.run.approved|paid|failed`, `payroll_run` rows read by PAP-186 (`upcomingPayroll`), contract test `payroll-contract.test.ts` runnable against any adapter. Consumes: interface and ADR (PAP-176), posting (PAP-179), `fin_employee` (PAP-175), notifications (PAP-136 core), portal shell (PAP-64), grid (PAP-165), env (PAP-17).""",
DoD="""* All three children Done.
* Sandbox end-to-end recorded: company onboarded, two employees, preview, approve, webhook to paid, ledger balanced, paystub visible in the portal.
* Playwright run flow and portal; screenshots at 375, 1024, 1920 in three themes; approval replay.
* `docs/finance/payroll.md` (sandbox setup, capability matrix, live checklist); CHANGELOG; Linear comment with demo link and the Needs Justin item for live approval.""",
Test="""Umbrella `payroll.e2e.test.ts` with `nock` fixtures recorded from the sandbox: sync two employees (one conflict resolved in the review list), create a run, enter hours, preview, approve with the typed total, replay `processing` and `paid` webhooks (one duplicated, one with a rotated signature), assert status transitions, `payroll_event` dedupe, both journal entries balanced and `payroll_liability` at zero after `paid`; run the contract suite against the mock adapter and the real adapter in sandbox.""",
Demo="""Reviewer opens `/finance/payroll`, creates the next run, edits hours for one employee in the grid, previews totals, approves by typing the net amount, then triggers the sandbox `paid` webhook and watches the run flip to Paid and the journal entries appear. Under two minutes.""",
Edge="""* Employee missing tax setup at approve: provider rejects; UI lists blocked employees with links.
* Bank-holiday pay date: provider's adjusted date shown.
* Off-cycle bonus run when the capability exists.
* Funding failure after approval: `failed`, liabilities remain, owner alerted.
* Terminated mid-period: final pay by provider rules, excluded from future runs.""",
Deps="""PAP-176 (hard), PAP-179 (hard), PAP-175 (hard), PAP-136 core, PAP-64, PAP-165, sandbox credentials (Needs Justin). Feeds PAP-186.""",
Agent="""Builder: Ledger (Payroll Adapter). Reviewer: Sentinel (Security Auditor primary, Code Reviewer); Bookkeeper checks postings.""",
Size="""L, split into three M children plus a verification spike on webhook signing.""")

add("PAP-185",
Goal="""Turn receipts into journal entries: capture a photo or PDF from web or mobile, extract vendor, date, totals, tax and lines with a vision model, let staff review and categorise, create an expense or vendor bill, and post it to the ledger with duplicate detection and threshold approval.""",
Scope="""In: tables `fin_expense`, `fin_expense_line`, `fin_expense_extraction`; procedures `expenses.*`; extraction worker; `/finance/expenses` inbox and review panel; Tauri mobile capture; posting rules `expense.approved`, `expense.reimbursed`, `bill.created`; vendor-to-account learning; email-in address when PAP-136 inbound exists.

Out: card feeds and bank sync, mileage and per diem, multi-currency reimbursement beyond FX capture.""",
Spec="""* Capture: images and PDF to 20 MB via PAP-37; mobile through `@tauri-apps/plugin-camera` (PAP-260) with client downscale to 2000 px; each upload creates `fin_expense (status: extracting)` and enqueues a PAP-43 job.
* Extraction: Claude API per the `claude-api` skill recommendation, temperature 0, tool `receipt_extraction` returning vendor, tax id, date, currency, subtotal, tax, tip, total, payment method, last four, lines and per-field confidence; PDFs rasterised first page; fallback `tesseract.js` text extraction; raw and parsed output plus `cost_usd` stored in `fin_expense_extraction`; daily spend cap via PAP-111.
* Review panel: zoomable image beside a pre-filled form with low-confidence fields highlighted; vendor fuzzy-matched to `fin_party` (`pg_trgm` above 0.6) or created; category maps to expense accounts; `paidBy: company|employee`; dimensions; approve or reject.
* Duplicates: same file `sha256`, or same vendor, total and date within two days.
* Approval above `fin_settings.expense_approval_threshold_minor` (default 500.00) requires a second user with `expense.approve`; agents extract and propose only.
* Posting: debit expense account, debit `sales_tax_receivable` when recoverable, credit `cash` or `credit_card` or `employee_reimbursements_payable`; `expense.reimbursed` moves the payable to cash.
* Learning: `fin_vendor.default_expense_account_id` set after the same account is chosen twice.""",
Contract="""Provides: `expenses.upload|list|get|review|approve|reject|recordReimbursement`, `ReceiptExtraction` Zod schema, dataset `finance.expenses`, `bill` documents created through PAP-180 for invoice-like receipts, event `expense.approved`. Consumes: posting (PAP-179), files (PAP-37), parties and accounts (PAP-175), camera shim (PAP-259, PAP-260), cost controls and eval harness (PAP-111, PAP-110), jobs (PAP-43), notifications (PAP-136 core). Consumed by PAP-183 AP aging (bills), PAP-186 payables block.""",
DoD="""* Extraction eval set of 40 labelled receipts in `packages/finance/test/receipts/`: totals correct on 90 percent, dates on 95 percent; weekly run through PAP-110.
* Vitest, Playwright and the Android emulator smoke below green.
* `docs/finance/expenses.md` with the privacy note on model data flow; CHANGELOG; Linear comment with demo link and eval scores.""",
Test="""* Unit: duplicate rules, approval routing including submitter-equals-approver, posting outputs for company-paid, employee-paid and recoverable tax, learning threshold.
* Integration: upload to extraction job to review row with recorded model fixtures; fallback path when the vision call fails; spend cap trips.
* E2E: upload, review with one corrected field, approve, journal entry appears; mobile capture on the Android emulator (PAP-258 pipeline).
* Visual: inbox and review panel at 375, 768, 1024, 1440, 1920 in three themes.""",
Demo="""Reviewer drags a sample receipt into `/finance/expenses`, watches it move from extracting to review, corrects the highlighted tax field, approves it and opens the resulting journal entry from the activity tab. Under two minutes.""",
Edge="""* Foreign-currency receipt: FX at receipt date from the rates table or manual entry.
* Total not equal to subtotal plus tax: flagged, reviewer fixes, raw kept.
* Multi-receipt PDF split into expenses with a merge action.
* Illegible image: "needs manual entry".
* Vendor name in another script: transliterated fuzzy match, else create.""",
Deps="""PAP-179 (hard), PAP-37 (hard), PAP-175 (hard), PAP-180 (bills), PAP-260 (mobile capture), PAP-111, PAP-110, PAP-43, PAP-136 core (soft).""",
Agent="""Builder: Ledger (Bookkeeper) with Forge (Tauri Smith) on mobile capture. Reviewer: Sentinel (Security Auditor for uploads and model data flow, Edge Case Hunter with adversarial receipts).""",
Size="""M: extraction is quick to wire; review UX and eval discipline take the time.""")

add("PAP-186",
Goal="""Ship the founder's one screen: cash in and out over time, cash now, runway, upcoming payroll, receivables and payables due and MRR, assembled from finance datasets as the first real consumer of PAP-173. It is the integration test of the finance and views stacks and the default landing page of `/finance`.""",
Scope="""In: seeded dashboard `finance.cash` (`packages/finance/src/dashboards/cash.dashboard.json`) installed on finance module enablement, editable and resettable; datasets and number blocks `finance.cashSeries|runway|upcomingPayroll|arDueSoon|apDueSoon|mrr`; page spec `specs/pages/finance/cash.spec.yaml` with `layout.dashboard`; nightly alerts for runway under three months and payroll not covered by cash.

Out: forecasting scenarios, bank sync (cash comes from `cash` and `stripe_balance` subtypes), budgets.""",
Spec="""* Layout at `lg`: row 1 four number blocks (Cash now, Runway, Net burn 30d, MRR); row 2 "Cash in vs out" stacked weekly bars with a net line (8 cols) and "Upcoming payroll" (4 cols); row 3 AR due 30 days and AP due 30 days grids (6 cols each); row 4 "Cash balance trend" daily line, 90 days. Global date-range filter block at top controls the charts; number blocks pin to now.
* `finance.cashSeries`: ledger lines on `cash` and `stripe_balance` bucketed by `date_trunc('week')` with `inflow, outflow, net, balance_end`; `finance.runway` = cash now over average net burn of the trailing three months, "profitable" when burn is positive; `finance.upcomingPayroll` reads the next `payroll_run` in `draft|previewed|approved` or estimates from the last paid run labelled "estimate"; `finance.mrr` from active subscriptions on the connected account normalised monthly, trials excluded; AR and AP due soon filter the PAP-183 aging datasets to `due_date <= now + 30d`.
* Colour rules: runway red under 3 months, amber under 6; payroll block red when total exceeds cash now; deltas versus previous period and sparklines on every number block.
* Cross-filter: a week bar filters both grids; a party row opens the record panel; number blocks drill to `/finance/reports/*`.
* Alerts via PAP-136 core to owners once per condition change.
* Refresh every 5 minutes with "updated n min ago"; illustrated empty state for new tenants.""",
Contract="""Provides: the six datasets and number blocks, `cash.dashboard.json` as the reference dashboard definition other modules copy, `installFinanceDashboard(tenantId)` on module enablement (PAP-264), notification kinds `finance.runway_low`, `finance.payroll_uncovered`. Consumes: reports and blocks (PAP-183), dashboard engine and print (PAP-173), charts (PAP-170), `payroll_run` (PAP-184, optional), subscriptions on the connected account (PAP-181, optional), notifications (PAP-136 core), demo seed (PAP-208).""",
DoD="""* Vitest, Playwright and performance below green; dashboard settles under 2 s on the seeded tenant.
* Screenshots at 375, 768, 1024, 1440, 1920 in three themes; cross-filter replay; PDF export via the print route; every block has a text summary for screen readers.
* `docs/finance/cash-dashboard.md` explaining each metric; CHANGELOG; Linear comment with demo link and a screenshot for the release digest (PAP-89).""",
Test="""* Unit: weekly bucketing across a year boundary, runway maths (negative burn, profitable, zero history, overdraft), MRR normalisation of yearly and trialing subscriptions, alert thresholds and once-per-change semantics.
* Integration: datasets against the PAP-183 textbook fixture plus seeded subscriptions and a payroll run; `installFinanceDashboard` idempotent; reset keeps the custom copy.
* E2E: render with seed, click a week bar and assert both grids filter, change the date range, drill from Cash now to the cash flow report, fresh tenant shows the empty state.
* Visual: matrix above plus empty state and the red payroll block.""",
Demo="""Reviewer opens `/finance` on the seeded tenant, reads runway and MRR, clicks a red week in the cash chart to filter payables due that week, changes the range to 26 weeks, then prints the dashboard to PDF. Under two minutes.""",
Edge="""* Payroll module disabled: block hidden, layout reflows.
* Negative cash: runway "0 months" with a red banner.
* Multi-currency cash accounts: functional totals with a currency footnote.
* Revenue without Stripe: MRR shows "n/a" with an enable-billing link.
* Reset after edits keeps the user's copy as "Cash (custom)".""",
Deps="""PAP-183 (hard), PAP-173 (hard), PAP-170 (via PAP-173), PAP-184 (optional), PAP-181 (optional), PAP-136 core, PAP-208 seed.""",
Agent="""Builder: Ledger (Bookkeeper) with Nova (Views Engineer) on engine gaps. Reviewer: Sentinel (Visual Inspector, Code Reviewer); Iris reviews metric presentation with the dataviz plugin.""",
Size="""M: composition over existing pieces, but it exercises the whole finance and views stack.""")
