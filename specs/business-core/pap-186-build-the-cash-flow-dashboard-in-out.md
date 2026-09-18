---
identifier: "PAP-186"
title: "Build the cash-flow dashboard (in, out, runway, upcoming payroll) as the first dashboard-blocks consumer"
project: "business-core"
projectName: "Business Core: Payments, Finance & Payroll"
phase: "P2"
type: "Build"
priority: 2
surfaces: ["Staff"]
milestone: "Payroll adapter and cash dashboard"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-173", "PAP-183", "PAP-387", "PAP-765", "PAP-767"]
blocks: ["PAP-789"]
key: "business-core/cash-dashboard"
url: "https://linear.app/paperos/issue/PAP-186/build-the-cash-flow-dashboard-in-out-runway-upcoming-payroll-as-the"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:28:44.935Z"
model: "claude-sonnet-5"
effort: "high"
estimate: 3
dueDate: "2026-10-01"
cycle: null
---

# PAP-186: Build the cash-flow dashboard (in, out, runway, upcoming payroll) as the first dashboard-blocks consumer

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / high — Build M

**Goal**

Ship the founder's one screen: cash in and out over time, cash now, runway, upcoming payroll, receivables and payables due and MRR, assembled from finance datasets as the first real consumer of PAP-173. It is the integration test of the finance and views stacks and the default landing page of `/finance`.

**Scope**

In: seeded dashboard `finance.cash` (`packages/finance/src/dashboards/cash.dashboard.json`) installed on finance module enablement, editable and resettable; datasets and number blocks `finance.cashSeries|runway|upcomingPayroll|arDueSoon|apDueSoon|mrr`; page spec `specs/pages/finance/cash.spec.yaml` with `layout.dashboard`; nightly alerts for runway under three months and payroll not covered by cash.

Out: forecasting scenarios, bank sync (cash comes from `cash` and `stripe_balance` subtypes), budgets.

**Spec**

* Layout at `lg`: row 1 four number blocks (Cash now, Runway, Net burn 30d, MRR); row 2 "Cash in vs out" stacked weekly bars with a net line (8 cols) and "Upcoming payroll" (4 cols); row 3 AR due 30 days and AP due 30 days grids (6 cols each); row 4 "Cash balance trend" daily line, 90 days. Global date-range filter block at top controls the charts; number blocks pin to now.
* `finance.cashSeries`: ledger lines on `cash` and `stripe_balance` bucketed by `date_trunc('week')` with `inflow, outflow, net, balance_end`; `finance.runway` = cash now over average net burn of the trailing three months, "profitable" when burn is positive; `finance.upcomingPayroll` reads the next `payroll_run` in `draft|previewed|approved` or estimates from the last paid run labelled "estimate"; `finance.mrr` from active subscriptions on the connected account normalised monthly, trials excluded; AR and AP due soon filter the PAP-183 aging datasets to `due_date <= now + 30d`.
* Colour rules: runway red under 3 months, amber under 6; payroll block red when total exceeds cash now; deltas versus previous period and sparklines on every number block.
* Cross-filter: a week bar filters both grids; a party row opens the record panel; number blocks drill to `/finance/reports/*`.
* Alerts via PAP-136 core to owners once per condition change.
* Refresh every 5 minutes with "updated n min ago"; illustrated empty state for new tenants.

*Round 4 amendment (2026-09-18):*
Round 4 clarification: `finance.mrr` cannot read 'active subscriptions on the connected account' because PAP-181 creates no subscription model and PAP-177 subscriptions are PaperOS's own plans. Compute tenant MRR from active `fin_recurring_schedule` rows (PAP-765, normalised monthly) plus imported Stripe subscriptions when PAP-423 has run; show 'n/a' with an enable link when neither exists.

**Interface contract**

Provides: the six datasets and number blocks, `cash.dashboard.json` as the reference dashboard definition other modules copy, `installFinanceDashboard(tenantId)` on module enablement (PAP-264), notification kinds `finance.runway_low`, `finance.payroll_uncovered`. Consumes: reports and blocks (PAP-183), dashboard engine and print (PAP-173), charts (PAP-170), `payroll_run` (PAP-184, optional), subscriptions on the connected account (PAP-181, optional), notifications (PAP-136 core), demo seed (PAP-208).

**Definition of done**

* Vitest, Playwright and performance below green; dashboard settles under 2 s on the seeded tenant.
* Screenshots at 375, 768, 1024, 1440, 1920 in three themes; cross-filter replay; PDF export via the print route; every block has a text summary for screen readers.
* `docs/finance/cash-dashboard.md` explaining each metric; CHANGELOG; Linear comment with demo link and a screenshot for the release digest (PAP-89).

**Test plan**

* Unit: weekly bucketing across a year boundary, runway maths (negative burn, profitable, zero history, overdraft), MRR normalisation of yearly and trialing subscriptions, alert thresholds and once-per-change semantics.
* Integration: datasets against the PAP-183 textbook fixture plus seeded subscriptions and a payroll run; `installFinanceDashboard` idempotent; reset keeps the custom copy.
* E2E: render with seed, click a week bar and assert both grids filter, change the date range, drill from Cash now to the cash flow report, fresh tenant shows the empty state.
* Visual: matrix above plus empty state and the red payroll block.

**Demo**

Reviewer opens `/finance` on the seeded tenant, reads runway and MRR, clicks a red week in the cash chart to filter payables due that week, changes the range to 26 weeks, then prints the dashboard to PDF. Under two minutes.

**Edge cases**

* Payroll module disabled: block hidden, layout reflows.
* Negative cash: runway "0 months" with a red banner.
* Multi-currency cash accounts: functional totals with a currency footnote.
* Revenue without Stripe: MRR shows "n/a" with an enable-billing link.
* Reset after edits keeps the user's copy as "Cash (custom)".

**Dependencies**

PAP-183 (hard), PAP-173 (hard), PAP-170 (via PAP-173), PAP-184 (optional), PAP-181 (optional), PAP-136 core, PAP-208 seed.

**Agent**

Builder: Ledger (Bookkeeper) with Nova (Views Engineer) on engine gaps. Reviewer: Sentinel (Visual Inspector, Code Reviewer); Iris reviews metric presentation with the dataviz plugin.

**Size**

M: composition over existing pieces, but it exercises the whole finance and views stack.

*Round 4 critique fix (2026-09-18):* resolved 1 round-4 file key in this description to Linear identifiers: `r4/business-core/recurring-invoices-dunning` = PAP-765.
