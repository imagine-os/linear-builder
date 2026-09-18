---
identifier: "PAP-776"
title: "Customer statements and account balances: per-party statement of account with running balance, PDF and portal download, batch send and overdue summary"
project: "business-core"
projectName: "Business Core: Payments, Finance & Payroll"
phase: "P2"
type: "Build"
priority: 4
surfaces: ["Customer"]
milestone: "Ledger and reports"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-183", "PAP-397"]
blocks: []
key: "r4/business-core/customer-statements"
url: "https://linear.app/paperos/issue/PAP-776/customer-statements-and-account-balances-per-party-statement-of"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:41.509Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 2
dueDate: null
cycle: null
---

# PAP-776: Customer statements and account balances: per-party statement of account with running balance, PDF and portal download, batch send and overdue summary

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Build S

**Goal**

Deferred to v0.2 by the Execution Schedule (NJ-14 stop-loss 09-27 can reinstate). Not claimable before 10-01.

Customers with several open invoices ask 'what do I owe you' and finance answers with a spreadsheet. A statement of account per party, rendered with the PAP-235 kit and available in the portal, answers it and doubles as the dunning escalation document.

**Scope**

In: `statements.generate(partyId, range)` building opening balance, invoices, payments, credit notes and closing balance from the ledger `ar` subaccount by party; PDF template `statement`; `statements.send` through PAP-397 templates with `canContact` transactional check; batch send to all parties with balance over zero on a schedule; portal `_portal/statement` page; dataset `finance.customerBalances` (balance, oldest open, last payment) for CRM company pages.

Out: vendor statements reconciliation (v0.3), interest on overdue (dunning issue handles fees).

**Spec**

* Statement lines come from journal lines with `party_id`, so manual payments and FX adjustments appear; totals reconcile to AR aging for the same as-of date (test).
* Range presets `thisMonth|lastMonth|last90|custom`; running balance in functional currency with per-currency subtotals when mixed.
* Batch send skips parties with `do_not_contact` and logs the skip.

**Interface contract**

Provides: `statements.generate|send|batch`, PDF template, portal route, dataset `finance.customerBalances`, activity source `statement.sent`. Consumes: postings and templates (PAP-397), aging (PAP-183), PDF kit (PAP-235, PAP-396), portal shell (PAP-64), consent (PAP-791, soft).

**Definition of done**

* Statement total equals AR aging for every seeded party (integration test); PDF snapshot at two brands; portal Playwright; screenshots at 375, 1024.
* `docs/finance/statements.md`; CHANGELOG.

**Test plan**

* Unit: running balance arithmetic, range presets, currency subtotals, skip rules.
* E2E: generate a statement for a seeded party, download from the portal, batch send and read the sandbox emails.

**Demo**

Reviewer opens a company page, clicks Statement, sees the running balance and downloads the PDF from the portal as that customer. Under two minutes.

**Edge cases**

* Party is both customer and vendor: statement shows AR only; AP netting is out of scope and stated.
* Credit balance (overpayment): shown negative with a 'credit available' note.

**Dependencies**

Hard: PAP-397, PAP-183. Soft: PAP-235, PAP-64, PAP-791.

**Agent**

Builder: Ledger (Bookkeeper). Reviewer: Sentinel (Visual Inspector, Code Reviewer).

**Size**

S: half a session.

*Round 4 critique fix (2026-09-18):* resolved 1 round-4 file key in this description to Linear identifiers: `r4/growth/consent-compliance-centre` = PAP-791.
