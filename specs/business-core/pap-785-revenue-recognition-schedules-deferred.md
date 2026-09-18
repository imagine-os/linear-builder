---
identifier: "PAP-785"
title: "Revenue recognition schedules: deferred revenue for prepaid periods and multi-period services, monthly recognition job and deferred revenue roll-forward report"
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
blockedBy: ["PAP-393", "PAP-397"]
blocks: []
key: "r4/business-core/revenue-recognition"
url: "https://linear.app/paperos/issue/PAP-785/revenue-recognition-schedules-deferred-revenue-for-prepaid-periods-and"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:43.114Z"
model: "claude-opus-5"
effort: "high"
estimate: 3
dueDate: null
cycle: null
---

# PAP-785: Revenue recognition schedules: deferred revenue for prepaid periods and multi-period services, monthly recognition job and deferred revenue roll-forward report

**Model / Effort:** Opus 5 (`claude-opus-5`) / high — Build M

**Goal**

Deferred to v0.2 by the Execution Schedule (NJ-14 stop-loss 09-27 can reinstate). Not claimable before 10-01.

An annual plan invoiced upfront is not a year of revenue in one month. SaaS, gyms, schools and agencies with retainers need deferred revenue; without it the P&L PAP-183 renders is wrong for exactly the businesses that prepay.

**Scope**

In: `fin_recognition_schedule (document_line_id, method: straight_line|on_event|milestones, start_at, end_at, total_minor, recognised_minor, status)` created at `invoice.issued` for lines whose item or line flag sets `recognise_over_period`; posting at issue moves revenue to `deferred_revenue` (liability) for such lines; monthly job (PAP-43) posting `revenue.recognised` (debit `deferred_revenue`, credit revenue) with day-weighted straight line; manual `recognise` for `on_event`; credit notes and voids reverse the unrecognised remainder; report dataset `finance.deferredRevenue` (opening, additions, recognised, closing by month) and a P&L footnote linking deferred balances.

Out: multi-element allocation (SSP), usage-based recognition (metered issue posts on usage), IFRS 15 disclosures beyond the roll-forward.

**Spec**

* Schedules are computed in functional currency at issue; FX differences on later recognition go to `fx_gain_loss`.
* Recognition job is idempotent per `(schedule_id, period_id)`; a locked period defers recognition to the first open period with a note.
* Item catalogue exposes `recognition: { method, period_from: service_dates|invoice_date }` so schedules need no manual setup for standard items.

**Interface contract**

Provides: tables, `recognition.*`, posting rules `revenue.deferred|recognised`, job `recognition.run`, dataset and report. Consumes: postings and issue flow (PAP-397), periods (PAP-393), items (PAP-774, soft), reports (PAP-183), recurring schedules (PAP-765, soft).

**Definition of done**

* Textbook fixture: a 12-month prepaid invoice recognises to the cent across months including February and a leap year; void mid-term reverses the remainder; property test that deferred balance equals unrecognised sum.
* Report screenshots at 375, 1024, 1920 in three themes; `docs/finance/revenue-recognition.md`; CHANGELOG.

**Test plan**

* Unit: day weighting, rounding remainder to the last month, void and credit note reversal, locked period deferral.
* E2E: issue an annual invoice for a recognised item, run the job for three months, open the roll-forward and the P&L.

**Demo**

Reviewer issues a 1,200.00 annual invoice, advances the job three months and reads 300.00 recognised and 900.00 deferred. Under two minutes.

**Edge cases**

* Service dates missing: schedule starts at issue date with a warning.
* Schedule shortened by a cancellation: remaining months re-spread, history untouched.
* Recognition in a currency other than functional: schedule fixed at issue rate.

**Dependencies**

Hard: PAP-397, PAP-393. Soft: PAP-183, PAP-774, PAP-765.

**Agent**

Builder: Ledger (Bookkeeper). Reviewer: Sentinel (Edge Case Hunter for calendars, Code Reviewer).

**Size**

M: one session.

*Round 4 critique fix (2026-09-18):* resolved 2 round-4 file keys in this description to Linear identifiers: `r4/business-core/item-catalogue` = PAP-774, `r4/business-core/recurring-invoices-dunning` = PAP-765.
