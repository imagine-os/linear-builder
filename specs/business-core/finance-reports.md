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
blockedBy: ["PAP-165", "PAP-179", "PAP-180"]
blocks: ["PAP-186"]
key: "business-core/finance-reports"
url: "https://linear.app/paperos/issue/PAP-183/generate-pandl-balance-sheet-cash-flow-and-arap-aging-as-table-views"
source: "plan/specs/bucket-6.json (round-1 canonical spec JSON)"
---

# PAP-183: Generate P&L, balance sheet, cash flow and AR/AP aging as table views

**Goal**

Produce books a founder can read: profit and loss, balance sheet, cash flow (indirect method) and AR/AP aging, generated from the ledger and documents as datasets in the views engine, so they get grouping, filtering, drill-down and export for free and can be dropped into dashboards.

**Scope**

In:
- `packages/finance/src/reports/`: report definitions, SQL builders, dataset registrations `finance.pnl`, `finance.balanceSheet`, `finance.cashFlow`, `finance.arAging`, `finance.apAging`, `finance.trialBalance`, `finance.generalLedger`.
- Report page `/finance/reports/:key` with parameter bar (period, comparison, basis, dimensions) and saved report views.
- Drill-down from any report line to journal entries and documents.
- Exports: CSV, XLSX (`exceljs` 4.x), PDF via the dashboard print route.

Out: budgeting and forecasting, consolidation across tenants, custom report builder UI (saved views over these datasets cover most needs).

**Spec**

- Parameters (typed, shared): `period` (preset `thisMonth|lastMonth|thisQuarter|ytd|lastYear|custom` resolved with fiscal year from `fin_settings`), `comparison` (`none|previousPeriod|previousYear`), `basis` (`accrual|cash`; cash basis recognises revenue/expenses on payment transactions), `dimensions` (department, location, project), `currency` (functional only in v1).
- P&L: rows are accounts of type revenue and expense grouped by parent account, with subtotals (Gross profit when `cogs` subtype exists, Operating income, Net income); columns per period and comparison with variance amount and percent; built from `fin_account_balance` for closed periods and live lines for the open period.
- Balance sheet: assets, liabilities, equity as of `period.end`; retained earnings computed as cumulative net income of prior periods plus current; must balance or the report shows a red "Out of balance by X" with a link to `ledger.verifyChain`.
- Cash flow (indirect): net income, adjustments (non-cash), changes in working capital derived from AR, AP, tax payable and payroll liability subtypes, investing and financing sections from account subtypes; reconciles to the change in `cash` and `stripe_balance` subtypes; mismatch shown explicitly.
- AR aging: open invoices from `fin_document` grouped by party with buckets `current, 1-30, 31-60, 61-90, 90+` days past due as of a chosen date; AP aging mirrors it over vendor bills (bills modelled as `fin_document` kind `bill`, added here with a minimal entry form since `business-core/expense-capture` produces them).
- General ledger and trial balance datasets list entries and balances for a period with account filters.
- Implementation: each report is a `defineReport({ key, params, build: (params, ctx) => SQL, columns, rowKind })` registering a dataset with computed `FieldDef`s so `tables/grid-view` renders it; rows carry `drill: { kind: 'entries'|'documents', filter }` used by the row action "View entries".
- Materialisation: reports for closed periods cached in `fin_report_snapshot (tenant_id, key, params_hash, rows jsonb, generated_at)` invalidated on any posting into that period.
- Dashboard blocks: register number blocks `finance.netIncome`, `finance.cash`, `finance.arOutstanding`, `finance.apOutstanding` for `business-core/cash-dashboard`.
- Permissions: `reports.read` for finance staff and owners; customers never.

**Definition of done**

- Vitest against a fixture ledger with known answers (textbook set of 60 entries): P&L, balance sheet, cash flow and aging match to the cent, both bases.
- Property test: for random balanced entries, balance sheet always balances and cash flow reconciles.
- Playwright: open each report, change period, drill down, export CSV; screenshots at 375, 768, 1024, 1440, 1920 in three themes; PDF export snapshot for P&L.
- Performance: P&L for a tenant with 100k journal lines under 1 s (snapshots plus indexed balances).
- `docs/finance/reports.md` explaining each report's derivation; CHANGELOG entry; Linear comment with demo links.

**Edge cases**

- Fiscal year starting in July: presets and YTD follow `fiscal_year_start_month`.
- Unposted drafts: excluded, with a count badge "n drafts not included".
- Accounts with no activity: hidden by default, toggle "show zero rows".
- Multi-currency lines: functional amounts only; a footnote lists currencies present.
- Comparison period with no data: variance shows "n/a" not division by zero.
- Aging as-of date earlier than some payments: payments after the date are ignored so historical aging is reproducible.

**Dependencies**

- `business-core/ledger` (balances, entries), `business-core/invoicing` (documents for aging), `tables/grid-view` and `tables/query-compiler` (dataset rendering), `tables/dashboard-blocks` (number blocks), `tables/view-sharing` (saved report views).

**Agent**

Builder: Ledger (Bookkeeper). Reviewer: Sentinel (Code Reviewer, Edge Case Hunter) with an accounting fixture review by Quill for the docs.

**Size**

M: SQL and fixtures dominate; UI comes from the views engine.
