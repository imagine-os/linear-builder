---
identifier: "PAP-789"
title: "Cash forecast scenarios: 13-week projection from open AR and AP, recurring schedules, payroll calendar and manual assumptions with best, base and worst cases"
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
blockedBy: ["PAP-186", "PAP-765"]
blocks: []
key: "r4/business-core/cash-forecast-scenarios"
url: "https://linear.app/paperos/issue/PAP-789/cash-forecast-scenarios-13-week-projection-from-open-ar-and-ap"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:43.449Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 3
dueDate: null
cycle: null
---

# PAP-789: Cash forecast scenarios: 13-week projection from open AR and AP, recurring schedules, payroll calendar and manual assumptions with best, base and worst cases

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Build M

**Goal**

Deferred to v0.2 by the Execution Schedule (NJ-14 stop-loss 09-27 can reinstate). Not claimable before 10-01.

PAP-186 shows runway from history. Founders decide with a forward view: when do open invoices land, what bills and payroll leave, and what if a customer pays late. A deterministic 13-week forecast from data the ledger already has, plus editable assumptions, is the natural next block.

**Scope**

In: `fin_forecast_scenario (name, assumptions jsonb { collectionDelayDays, collectionRatePct, growthPct, oneOffs[] })`; projection engine `forecast.project(scenarioId, weeks=13)` combining open AR by due date and historical days-to-pay per party, open AP and scheduled payments, recurring schedules and expected usage, payroll calendar (next runs estimated from the last paid run), platform subscription costs, and manual one-offs; three default scenarios; chart block (PAP-170 line with band) and weekly table on `/finance/forecast` with a scenario switcher and assumption sliders; alert when any week's projected balance drops below zero; export CSV.

Out: ML forecasting, bank-feed-based categorisation (reconciliation issue feeds actuals), budgeting (separate issue).

**Spec**

* Engine is pure and deterministic given inputs; fixtures assert week-by-week balances.
* Days-to-pay per party is the median over the last six paid invoices, falling back to terms plus the tenant default delay.
* Actuals replace projections as weeks pass; variance between last week's projection and actual is shown.

**Interface contract**

Provides: tables, `forecast.*`, block `finance.cashForecast`, route, alert kind `finance.forecast_negative`, CSV export. Consumes: cash series and runway (PAP-186), aging (PAP-183), recurring schedules, payroll runs (PAP-400), subscriptions (PAP-177), bills (PAP-772, soft), charts (PAP-170), notifications (PAP-136).

**Definition of done**

* Fixture forecast matches hand-computed weeks; scenario switch re-renders under 500 ms; screenshots at 375, 1024, 1920 in three themes.
* `docs/finance/forecast.md`; CHANGELOG.

**Test plan**

* Unit: days-to-pay median, collection rate application, one-off placement, negative week detection.
* E2E: open the forecast, drag collection delay to 30 days, see the band widen and a negative week alert appear.

**Demo**

Reviewer switches from base to worst case and reads which week cash goes negative, then adds a one-off inflow and watches it recover. Under two minutes.

**Edge cases**

* No history for a new tenant: terms-based projection with an 'estimate' badge.
* Payroll module disabled: payroll line hidden.
* Multi-currency: functional totals with a footnote.

**Dependencies**

Hard: PAP-186, PAP-765. Soft: PAP-183, PAP-400, PAP-177, PAP-170, PAP-136, PAP-772.

**Agent**

Builder: Ledger (Bookkeeper) with Iris on the chart. Reviewer: Sentinel (Visual Inspector, Code Reviewer).

**Size**

M: one session.

*Round 4 critique fix (2026-09-18):* resolved 2 round-4 file keys in this description to Linear identifiers: `r4/business-core/recurring-invoices-dunning` = PAP-765, `r4/business-core/vendor-bills-and-ap-payments` = PAP-772.
