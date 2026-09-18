---
identifier: "PAP-780"
title: "Budgets and variance: per-account and per-dimension budgets by period, budget import from spreadsheet, variance columns in the P&L and threshold alerts"
project: "business-core"
projectName: "Business Core: Payments, Finance & Payroll"
phase: "P2"
type: "Build"
priority: 4
surfaces: ["Staff"]
milestone: "Payroll adapter and cash dashboard"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-183", "PAP-769"]
blocks: []
key: "r4/business-core/budgets-and-variance"
url: "https://linear.app/paperos/issue/PAP-780/budgets-and-variance-per-account-and-per-dimension-budgets-by-period"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:42.375Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 3
dueDate: null
cycle: null
---

# PAP-780: Budgets and variance: per-account and per-dimension budgets by period, budget import from spreadsheet, variance columns in the P&L and threshold alerts

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Build M

**Goal**

Deferred to v0.2 by the Execution Schedule (NJ-14 stop-loss 09-27 can reinstate). Not claimable before 10-01.

PAP-183 explicitly leaves budgeting out and PAP-186 leaves forecasting out. A founder who can read the P&L next wants to compare it with a plan; budgets per account and department with variance in the same report close that loop cheaply because the report engine already exists.

**Scope**

In: `fin_budget (name, fiscal_year, status: draft|active|archived, basis)`, `fin_budget_line (budget_id, account_id, dimension jsonb?, period_id, amount_minor)`; budget editor grid (PAP-165 with inline edit and fill-right); `budgets.import` via PAP-200 CSV preset (account code by month columns); `comparison: budget` option in PAP-183 `ReportParams` adding Budget, Variance and Variance percent columns; alerts when actuals exceed budget by a threshold (PAP-136, once per period per line); dataset `finance.budgetVsActual`; dashboard block for PAP-186.

Out: driver-based forecasting, rolling reforecasts (PAP-789), approval workflows on budgets.

**Spec**

* Budget amounts are `Money` in functional currency; lines without a dimension apply to the account total, dimension lines to that slice; both can coexist and the report shows the finer one where present.
* Copying last year's actuals into a draft budget with a percentage uplift is one action (`budgets.seedFromActuals`).
* Variance sign convention: favourable positive for revenue and negative for expense, stated in the column header tooltip.

**Interface contract**

Provides: tables, `budgets.*`, report comparison `budget`, dataset, block `finance.budgetVariance`, CSV preset `budget`. Consumes: reports (PAP-183), dimensions (PAP-769), grid (PAP-165), CSV importer (PAP-200), notifications (PAP-136), dashboards (PAP-173).

**Definition of done**

* Variance on the demo seed equals a brute-force calculation; alert fires once; Playwright editor and report; screenshots at 375, 1024, 1920 in three themes.
* `docs/finance/budgets.md`; CHANGELOG.

**Test plan**

* Unit: line precedence (dimension over account), variance signs, uplift seeding, alert once-per-period.
* E2E: seed a budget from actuals plus 10 percent, edit two cells, open the P&L with budget comparison and click a variance to drill.

**Demo**

Reviewer seeds next year's budget from actuals, edits marketing, opens the P&L with the Budget comparison and reads the variance. Under two minutes.

**Edge cases**

* Fiscal year starting July: periods align to `fiscal_year_start_month`.
* Account deactivated mid-year: budget line kept, flagged.
* Budget in a locked fiscal year: read-only.

**Dependencies**

Hard: PAP-183, PAP-769. Soft: PAP-165, PAP-200, PAP-136, PAP-173.

**Agent**

Builder: Ledger (Bookkeeper). Reviewer: Sentinel (Code Reviewer).

**Size**

M: one session.

*Round 4 critique fix (2026-09-18):* resolved 2 round-4 file keys in this description to Linear identifiers: `r4/business-core/cash-forecast-scenarios` = PAP-789, `r4/business-core/ledger-dimensions-registry` = PAP-769.
