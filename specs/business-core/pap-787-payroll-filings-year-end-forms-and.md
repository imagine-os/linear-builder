---
identifier: "PAP-787"
title: "Payroll filings, year-end forms and deduction codes: provider filing status, W-2 and 1099 availability in the portal, benefit and garnishment deduction mapping to ledger accounts"
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
blockedBy: ["PAP-398", "PAP-400"]
blocks: []
key: "r4/business-core/payroll-filings-forms-and-deductions"
url: "https://linear.app/paperos/issue/PAP-787/payroll-filings-year-end-forms-and-deduction-codes-provider-filing"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:20:13.018Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 2
dueDate: null
cycle: null
---

# PAP-787: Payroll filings, year-end forms and deduction codes: provider filing status, W-2 and 1099 availability in the portal, benefit and garnishment deduction mapping to ledger accounts

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Build S

**Goal**

Deferred to v0.2 by the Execution Schedule (NJ-14 stop-loss 09-27 can reinstate). Not claimable before 10-01.

PAP-176's interface lists `taxes.filings` and PAP-184 leaves benefits out. Employees ask for W-2s and owners ask whether the quarterly filing went through; a thin surface over provider capabilities answers both and maps every deduction to the right liability account so payroll postings stop lumping them.

**Scope**

In: `payroll.filings.list` over the provider when `capabilities.filings` with a status page and PAP-136 alerts on `rejected|action_required`; year-end form availability (`W-2`, `1099`) surfaced in the PAP-400 paystub portal via provider-hosted links; `payroll_deduction_code (code, label, kind: pre_tax_benefit|post_tax_benefit|garnishment|reimbursement, liability_account_id, employer_match_account_id?)` and mapping of provider deduction ids to codes so `payroll.approved` postings split `payroll_liability` into per-code liabilities; benefits enrolment via provider-hosted link when `capabilities.benefits`; capability matrix rendered in settings.

Out: running filings ourselves, benefits carrier integrations, local tax registrations (provider owns).

**Spec**

* Forms are never downloaded to PaperOS storage; only short-lived provider URLs are proxied, consistent with PAP-359.
* Unmapped deduction ids post to `payroll_liability_unmapped` and raise a finance review item.
* Capability-driven UI: absent capabilities render an explanatory card, never an error.

**Interface contract**

Provides: `payroll.filings.*`, `payroll.deductionCodes.*`, posting split in `payroll.approved`, portal forms card, settings capability matrix. Consumes: adapter capabilities and webhooks (PAP-398), run postings and portal (PAP-400), notifications (PAP-136), accounts (PAP-175).

**Definition of done**

* Mock adapter exposes filings and deductions; postings split per code and balance (fixture); unmapped path tested; screenshots at 375, 1024, 1920.
* `docs/finance/payroll.md` gains filings and deductions sections; CHANGELOG.

**Test plan**

* Unit: deduction split arithmetic, unmapped fallback, capability branching, alert once per status change.
* E2E: map two deduction codes, approve a mock run and see separate liability lines; open the portal forms card as an employee.

**Demo**

Reviewer maps a 401k code, approves a run and reads the split liabilities in the journal, then opens the filings page showing a mock quarterly status. Under two minutes.

**Edge cases**

* Provider changes a deduction id: old mapping kept for history, new id flagged.
* Filing rejected after the period is locked: alert only; corrections are the provider's flow.

**Dependencies**

Hard: PAP-398, PAP-400. Soft: PAP-136, PAP-175.

**Agent**

Builder: Ledger (Payroll Adapter). Reviewer: Sentinel (Security Auditor).

**Size**

S: half a session.
