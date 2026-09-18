---
identifier: "PAP-782"
title: "Timesheets and time-off: time entries with approval, PTO policies and balances through the provider where supported, and hours flowing into the payroll run grid"
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
blockedBy: ["PAP-175", "PAP-400"]
blocks: []
key: "r4/business-core/timesheets-to-payroll-hours"
url: "https://linear.app/paperos/issue/PAP-782/timesheets-and-time-off-time-entries-with-approval-pto-policies-and"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:42.750Z"
model: "claude-sonnet-5"
effort: "high"
estimate: 3
dueDate: null
cycle: null
---

# PAP-782: Timesheets and time-off: time entries with approval, PTO policies and balances through the provider where supported, and hours flowing into the payroll run grid

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / high — Build M

**Goal**

Deferred to v0.2 by the Execution Schedule (NJ-14 stop-loss 09-27 can reinstate). Not claimable before 10-01.

PAP-400's hours grid is typed by hand. Restaurants, clinics, gyms and agencies already record hours and time off; feeding those into payroll removes the most error-prone step of a run and gives agencies billable-time data for invoices.

**Scope**

In: `fin_time_entry (employee_party_id, date, minutes, kind: regular|overtime|pto|sick|holiday, project_dimension?, billable, customer_party_id?, status: draft|submitted|approved|paid, approved_by)`, weekly timesheet page and mobile-friendly clock in and out; approval by managers (`manager_party_id` from PAP-175) with `timesheets.approve`; `fin_pto_policy` and balances computed locally or read from the provider when `capabilities.timeOff`; time-off request flow with calendar view (PAP-168); `payroll.runs.importHours(runId)` filling the PAP-400 grid from approved entries for the period with overtime rules per tenant (daily over 8, weekly over 40 as defaults); billable entries exposed to invoicing as `documents.linesFromTime`.

Out: geofencing, biometric clocks, shift scheduling (restaurant pack models shifts as a table; sync is v0.3).

**Spec**

* Entries are immutable once `paid`; corrections create adjusting entries in the next period.
* Overtime rules are pure functions with fixtures per jurisdiction preset (US federal default).
* Provider time-off sync is one-way from provider when it owns accruals; otherwise PaperOS accrues per policy nightly (PAP-43).
* Employees see only their own entries and balances in the portal; managers their reports; `timesheets.read|write|approve` registered with the finance permission set.

**Interface contract**

Provides: tables, `timesheets.*`, `timeOff.*`, `payroll.runs.importHours`, `documents.linesFromTime`, portal routes `_portal/timesheet`, `_portal/time-off`, datasets. Consumes: payroll run grid (PAP-400), employees and managers (PAP-175), calendar view (PAP-168), jobs (PAP-43), portal (PAP-64), permissions (PAP-768), provider capabilities (PAP-398).

**Definition of done**

* Overtime fixtures green; import fills a run with the right regular and overtime minutes (integration); portal Playwright; screenshots at 375, 1024, 1920 in three themes.
* `docs/finance/timesheets.md`; CHANGELOG.

**Test plan**

* Unit: overtime rules, accrual maths, immutability after paid, permission scope.
* E2E: clock in and out over a week, submit, approve as manager, import into a payroll run and see the hours grid populated.

**Demo**

Reviewer submits a week with 44 hours, approves it and imports it into the next run, seeing 40 regular and 4 overtime. Under two minutes.

**Edge cases**

* Entry spanning midnight: split at the boundary.
* Time-off over balance: refused unless policy allows negative.
* Employee terminated: entries approved through the end date only.

**Dependencies**

Hard: PAP-400, PAP-175. Soft: PAP-168, PAP-43, PAP-64, PAP-398, PAP-768.

**Agent**

Builder: Ledger (Payroll Adapter). Reviewer: Sentinel (Edge Case Hunter for overtime, Code Reviewer).

**Size**

M: one session.

*Round 4 critique fix (2026-09-18):* resolved 1 round-4 file key in this description to Linear identifiers: `r4/business-core/finance-permissions-and-roles` = PAP-768.
