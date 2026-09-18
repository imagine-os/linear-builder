---
identifier: "PAP-183"
title: "Generate P&L, balance sheet, cash flow and AR/AP aging as table views"
project: "business-core"
projectName: "Business Core: Payments, Finance & Payroll"
phase: "P2"
type: "Build"
priority: 2
surfaces: ["Staff"]
milestone: "Ledger and reports"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-163", "PAP-165", "PAP-179", "PAP-180", "PAP-337", "PAP-343", "PAP-394", "PAP-397", "PAP-483", "PAP-630", "PAP-765", "PAP-766", "PAP-767", "PAP-768", "PAP-769"]
blocks: ["PAP-186", "PAP-776", "PAP-780", "PAP-784", "PAP-882"]
key: "business-core/finance-reports"
url: "https://linear.app/paperos/issue/PAP-183/generate-pandl-balance-sheet-cash-flow-and-arap-aging-as-table-views"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:51:29.647Z"
model: "claude-sonnet-5"
effort: "high"
estimate: 3
dueDate: "2026-09-29"
cycle: null
---

# PAP-183: Generate P&L, balance sheet, cash flow and AR/AP aging as table views

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / high — Build M

**Goal**

Produce books a founder can read: P&L, balance sheet, cash flow (indirect), AR and AP aging, general ledger and trial balance, generated from the ledger and documents as datasets in the views engine so they inherit grouping, filtering, drill-down, export and dashboard embedding.

**Scope**

In: `packages/finance/src/reports/` (`defineReport`, SQL builders, dataset registrations `finance.pnl|balanceSheet|cashFlow|arAging|apAging|trialBalance|generalLedger`); `/finance/reports/:key` with a parameter bar and saved report views; drill-down to entries and documents; CSV, XLSX (`exceljs` 4.x) and PDF (dashboard print route); `fin_report_snapshot` cache; number blocks for PAP-186.

Out: budgeting and forecasting, consolidation, a custom report builder (saved views cover it).

**Spec**

* Shared params: `period` presets (`thisMonth|lastMonth|thisQuarter|ytd|lastYear|custom`) resolved with `fiscal_year_start_month`, `comparison` (`none|previousPeriod|previousYear`), `basis` (`accrual|cash`), `dimensions`, functional currency only.
* P&L: revenue and expense accounts grouped by parent with subtotals (Gross profit when `cogs` exists, Operating income, Net income); comparison columns with variance amount and percent; closed periods from `fin_account_balance`, open period from live lines.
* Balance sheet as of `period.end`; retained earnings computed; must balance or shows "Out of balance by X" linking `ledger.verifyChain`.
* Cash flow indirect: net income, non-cash adjustments, working-capital deltas from `ar`, `ap`, `sales_tax_payable`, `payroll_liability` subtypes; reconciles to the change in `cash` plus `stripe_balance`.
* AR aging from open invoices, AP aging from `bill` documents, buckets `current, 1-30, 31-60, 61-90, 90+` as of a chosen date.
* `defineReport({ key, params, build(params, ctx) => SQL, columns, rowKind })` registers a dataset with computed `FieldDef`s; rows carry `drill: { kind, filter }`.
* Snapshots for closed periods in `fin_report_snapshot (tenant_id, key, params_hash, rows, generated_at)`, invalidated on `ledger.entry.posted` into that period.
* `reports.read` for finance staff and owners.

**Interface contract**

Provides: `defineReport`, `ReportParams` type, the seven datasets, number blocks `finance.netIncome|cash|arOutstanding|apOutstanding` via PAP-173 `defineNumberBlock`, `exportReport(key, params, 'csv'|'xlsx'|'pdf')`, route `/finance/reports/:key`. Consumes: balances and entries (PAP-179), documents (PAP-180), grid and compiler (PAP-165, PAP-163), dashboard blocks and print (PAP-173), saved views (PAP-172), `fin_settings` (PAP-175). Consumed by PAP-186, PAP-182 summary rendering, PAP-206 migration verification.

**Definition of done**

* Vitest, property and Playwright below green; P&L on 100k journal lines under 1 s.
* Screenshots at 375, 768, 1024, 1440, 1920 in three themes; P&L PDF snapshot.
* `docs/finance/reports.md` explaining each derivation; CHANGELOG; Linear comment with demo links.

**Test plan**

* Unit: textbook fixture of 60 entries with known answers for all five statements on both bases, to the cent; fiscal year starting July; aging as-of dates.
* Property (`fast-check`): random balanced entries always balance the balance sheet and reconcile cash flow.
* Integration: snapshot invalidation on a new posting; drill filter reproduces the report line total; XLSX opens with `exceljs` and matches CSV.
* E2E: open each report, change period, compare previous year, drill to entries, export CSV.
* Visual: matrix above plus the out-of-balance warning state.

**Demo**

Reviewer opens `/finance/reports/pnl` on the seeded tenant, switches to "this quarter versus previous year", clicks the Revenue line to see its journal entries, exports XLSX, then opens AR aging and clicks a 61-90 bucket to see the invoices. Under two minutes.

**Edge cases**

* Unposted drafts excluded with an "n drafts not included" badge.
* Zero-activity accounts hidden, toggle to show.
* Multi-currency lines shown in functional amounts with a currency footnote.
* Empty comparison shows "n/a", never divides by zero.
* Payments after the aging as-of date ignored so history is reproducible.

**Dependencies**

PAP-179 (hard), PAP-180 (hard, aging and bills), PAP-165 and PAP-163 (hard), PAP-173 (number blocks and print), PAP-172 (saved views). Blocks PAP-186.

*Round 4 amendment (2026-09-18):*
Round 4: the `dimensions` parameter resolves keys and options through PAP-769 (soft; until it lands only free-form `department` from payroll postings is accepted). Textbook expected values come from PAP-767 so PAP-186 and PAP-487 agree to the cent.

*Round 4 amendment (2026-09-18):*

* Soft dependency (round 4): PAP-772 (vendor-bills-and-ap-payments) would block this issue but sits in a later milestone (2026-10-01 > 2026-09-29); no `blocks` relation was created. Build against its interface and reconcile when it lands.

**Agent**

Builder: Ledger (Bookkeeper). Reviewer: Sentinel (Code Reviewer, Edge Case Hunter); Quill reviews the derivation docs.

**Size**

M: SQL and fixtures dominate; UI comes from the views engine.

*Round 4 critique fix (2026-09-18):* resolved 2 round-4 file keys in this description to Linear identifiers: `r4/business-core/finance-demo-seed` = PAP-767, `r4/business-core/ledger-dimensions-registry` = PAP-769.
