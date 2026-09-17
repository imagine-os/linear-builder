---
identifier: "PAP-400"
title: "Payroll run flow, typed-total approval, webhook status transitions, ledger posting and the paystub portal page"
project: "business-core"
projectName: "Business Core: Payments, Finance & Payroll"
phase: "P2"
type: "Build"
priority: 2
surfaces: ["Staff"]
milestone: "Payroll adapter and cash dashboard"
state: "Backlog"
parent: "PAP-184"
children: []
blockedBy: ["PAP-179", "PAP-399"]
blocks: []
key: "business-core/payroll/run-approve-post"
url: "https://linear.app/paperos/issue/PAP-400/payroll-run-flow-typed-total-approval-webhook-status-transitions"
source: "Linear snapshot 2026-09-17T13:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T13:05:47.457Z"
---

# PAP-400: Payroll run flow, typed-total approval, webhook status transitions, ledger posting and the paystub portal page

**Goal**

Run payroll end to end inside PaperOS: hours entry, preview, a deliberate approval, provider processing tracked by webhooks, balanced ledger postings and paystubs for employees.

**Scope**

In: `payroll_run`, `payroll_run_item`; `payroll.runs.*`, `payroll.paystubs.*`; `/finance/payroll` pages with the hours grid; posting rules `payroll.approved`, `payroll.paid`; portal paystubs page. Out: benefits, time tracking.

**Spec**

* Flow: create run for next period, edit hours in a PAP-165 grid, `preview`, `approve` with `payroll.approve` and the typed net total, transitions `processing` and `paid` from webhooks, cancel until cutoff from `capabilities`.
* Postings per the parent; `paid` moves `payroll_liability` to `cash`; dimensions from department.
* Paystub PDFs proxied through short-lived signed URLs, visible only to the linked user.

**Interface contract**

Provides: run tables, procedures, pages, posting rules, event `payroll.run.approved|paid|failed`, portal route `_portal/paystubs`, `payroll_run` rows for PAP-186. Consumes: both siblings, posting (PAP-179), grid (PAP-165), portal shell (PAP-64), audit (PAP-38).

**Definition of done**

* Status machine and posting tests; sandbox run recorded to `paid`; Playwright approve flow with replay; screenshots at 375, 1024, 1920; live checklist in docs and Needs Justin item.

**Test plan**

* Unit: transitions, posting totals, typed-total guard.
* Integration: webhook replay and rotation; liabilities net to zero after `paid`.
* E2E: full run flow; employee sees the paystub.

**Demo**

Create and approve a run, trigger the sandbox `paid` webhook, open the journal and the portal paystub.

**Edge cases**

* NSF after approval: `failed`, liabilities remain, owner alerted; off-cycle run when capable.

**Dependencies**

Both siblings (hard), PAP-179, PAP-165, PAP-64, PAP-38.

**Agent**

Builder: Ledger (Payroll Adapter). Reviewer: Sentinel (Security Auditor), Bookkeeper on postings.

**Size**

M: one session.
