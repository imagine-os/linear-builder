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
blockedBy: ["PAP-173", "PAP-183"]
blocks: []
key: "business-core/cash-dashboard"
url: "https://linear.app/paperos/issue/PAP-186/build-the-cash-flow-dashboard-in-out-runway-upcoming-payroll-as-the"
source: "plan/specs/bucket-6.json (round-1 canonical spec JSON)"
---

# PAP-186: Build the cash-flow dashboard (in, out, runway, upcoming payroll) as the first dashboard-blocks consumer

**Goal**

Ship the founder's one screen: a cash-flow dashboard showing cash in and out over time, current cash, runway, upcoming payroll, receivables and payables due, and subscription revenue, assembled from finance report datasets as the first real consumer of `tables/dashboard-blocks`. It proves the dashboard engine end to end and becomes the default landing page of the finance area.

**Scope**

In:
- Seeded dashboard definition `finance.cash` (JSON in `packages/finance/src/dashboards/cash.dashboard.json`) installed per tenant on finance module enablement, editable by finance staff, resettable to default.
- Datasets and number blocks: `finance.cashSeries` (weekly in/out/net), `finance.runway`, `finance.upcomingPayroll`, `finance.arDueSoon`, `finance.apDueSoon`, `finance.mrr`.
- Page spec `specs/pages/finance/cash.spec.yaml` and route `/finance` using `layout.dashboard`.
- Alerts: runway below 3 months and payroll uncovered by cash produce notifications.

Out: forecasting scenarios, bank account sync (cash comes from ledger `cash` and `stripe_balance` subtypes), budgets.

**Spec**

- Layout (12-col, `lg`): row 1 four number blocks (Cash now, Runway, Net burn 30d, MRR); row 2 chart block "Cash in vs out" (stacked bar weekly, 13 weeks, net line) spanning 8 cols and number block "Upcoming payroll" with date (4 cols); row 3 grid block "Receivables due next 30 days" (AR aging dataset filtered) and grid block "Payables due next 30 days" (6 cols each); row 4 chart "Cash balance trend" (line, daily, 90 days) 12 cols. `md` collapses to 8 cols two per row; `sm` stacks. A global date-range filter block at top controls the charts; the number blocks pin to "now".
- `finance.cashSeries` builds from ledger lines on `cash` and `stripe_balance` accounts bucketed by `date_trunc('week')` with columns `inflow, outflow, net, balance_end`; `finance.runway` = cash now divided by average net burn over the trailing 3 months (only when burn is negative, else "profitable"); `finance.upcomingPayroll` reads the next `payroll_run` in `draft|previewed|approved` or estimates from the last paid run when none exists (labelled "estimate"); `finance.mrr` derives from active Stripe subscriptions on the connected account normalised to monthly (yearly divided by 12), excluding trials; AR/AP due soon come from `finance.arAging` and `finance.apAging` datasets with `due_date <= now + 30d`.
- Number blocks show delta versus previous period and sparklines; colour rules: runway red under 3 months, amber under 6; payroll block red when `upcomingPayroll.total > cash now`.
- Cross-filter: clicking a week bar filters the AR/AP grids to documents due that week; clicking a party row opens the record panel.
- Drill-down: each number block links to the underlying report (`/finance/reports/cashFlow` etc.).
- Alerts: nightly job evaluates runway and payroll coverage and sends notifications via `collab/notifications` to owners (in-app and email) once per condition change.
- Empty state for new tenants: illustrated "Connect payments and post your first entry" with actions to Stripe onboarding, invoice creation and expense capture; demo tenant seeds 6 months of plausible activity via the business templates (`migration/business-templates`).
- Refresh: 5-minute interval; Electric shapes not used (aggregates), so "updated n min ago" is visible.

**Definition of done**

- Vitest for series bucketing, runway maths (including profitable and zero-history cases), MRR normalisation, alert thresholds.
- Playwright: dashboard renders with seeded data, cross-filter from chart to AR grid, date range change, empty state for a fresh tenant; screenshots at 375, 768, 1024, 1440, 1920 in three themes; video replay of cross-filtering; PDF export via the print route.
- Performance: dashboard settles under 2 s on the seeded tenant (trace attached).
- Accessibility: every block has a text summary; number blocks readable by screen reader.
- `docs/finance/cash-dashboard.md` explaining each metric's derivation; CHANGELOG entry; Linear comment with demo link and a screenshot for Justin's release digest (`quality/review-report`).

**Edge cases**

- No payroll module enabled: payroll block hidden, layout reflows.
- Cash negative (overdraft): runway shows "0 months" with a red banner.
- Multi-currency cash accounts: functional currency totals with a footnote of currencies; no blind summation.
- Tenant with revenue but no Stripe: MRR block shows "n/a" with a link to enable billing.
- Week boundary across fiscal year change: buckets by calendar week, labels include year.
- Dashboard edited by staff then reset: reset restores the seeded JSON but keeps their saved copy as "Cash (custom)".

**Dependencies**

- `business-core/finance-reports` (datasets, number blocks), `tables/dashboard-blocks` (engine), `tables/map-chart-views` (charts), `business-core/payroll-adapter` (upcoming payroll, optional), `business-core/stripe-connect` (MRR), `collab/notifications`.

**Agent**

Builder: Ledger (Bookkeeper) with Nova (Views Engineer) on any dashboard engine gaps found. Reviewer: Sentinel (Visual Inspector, Code Reviewer); Iris reviews metric presentation using the dataviz plugin.

**Size**

M: composition over existing pieces, but it is the integration test of the whole finance and views stack.
