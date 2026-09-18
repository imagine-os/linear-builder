---
identifier: "PAP-784"
title: "Year-end close and closing entries: retained earnings roll-forward, close checklist, accountant review package and reopening rules"
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
blockedBy: ["PAP-183", "PAP-393"]
blocks: []
key: "r4/business-core/year-end-close"
url: "https://linear.app/paperos/issue/PAP-784/year-end-close-and-closing-entries-retained-earnings-roll-forward"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:42.996Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 2
dueDate: null
cycle: null
---

# PAP-784: Year-end close and closing entries: retained earnings roll-forward, close checklist, accountant review package and reopening rules

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Build S

**Goal**

Deferred to v0.2 by the Execution Schedule (NJ-14 stop-loss 09-27 can reinstate). Not claimable before 10-01.

PAP-393 closes and locks months; PAP-183 computes retained earnings on the fly. A fiscal year still needs closing entries, a checklist and a package an external accountant can review, otherwise the balance sheet drifts from what the accountant files.

**Scope**

In: `ledger.closeYear(fiscalYear)` posting income and expense balances to `retained_earnings` as one closing entry dated the last day (reversible by PAP-393 rules), guarded by a checklist (`fin_close_checklist`: all periods closed, bank reconciled or overridden, unapplied deposits reviewed, AR and AP aging reviewed, FX revaluation noted, chain verified); review package export (trial balance, general ledger, P&L, balance sheet, AR and AP aging, fixed list of open items) as XLSX and PDF via PAP-183 `exportReport`; `ledger.reopenYear` with reason for owners only; year status on the periods page.

Out: tax return preparation, unrealised FX revaluation entries (noted as manual adjustment in the checklist), consolidation.

**Spec**

* Closing entry uses the `adjustment` rule with `source_type: year_close` so it is idempotent per fiscal year.
* Checklist items are computed live from datasets, each with a link to fix and an override with reason recorded in audit.
* Package files are content-addressed in PAP-37 and linked from the year row; regenerating after a reopen creates a new version.

**Interface contract**

Provides: `ledger.closeYear|reopenYear|closeChecklist`, `fin_close_checklist`, review package job, year status UI. Consumes: period close and chain (PAP-393), reports and exports (PAP-183), reconciliation statement (PAP-771, soft), files (PAP-37), permissions.

**Definition of done**

* Demo seed: closing entry brings income and expense accounts to zero and the balance sheet still balances (test); reopen and re-close idempotent.
* Checklist Playwright; screenshots at 375, 1024, 1920 in three themes; `docs/finance/year-end.md`; CHANGELOG.

**Test plan**

* Unit: closing entry composition, fiscal year boundaries with July starts, checklist evaluation, reopen guard.
* E2E: run the checklist, override one item with a reason, close the year, download the package, reopen with a reason.

**Demo**

Reviewer opens Periods, sees the checklist for the seeded year, closes it and downloads the package. Under two minutes.

**Edge cases**

* Post-close import backdated into the closed year: PAP-393 refuses; offered next open period.
* Multiple currencies: closing entry per functional currency only; translation is out of scope and stated.

**Dependencies**

Hard: PAP-393, PAP-183. Soft: PAP-37, PAP-771.

**Agent**

Builder: Ledger (Bookkeeper). Reviewer: Sentinel (Code Reviewer).

**Size**

S: half a session.

*Round 4 critique fix (2026-09-18):* resolved 1 round-4 file key in this description to Linear identifiers: `r4/business-core/bank-reconciliation-matching` = PAP-771.
