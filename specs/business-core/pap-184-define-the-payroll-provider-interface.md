---
identifier: "PAP-184"
title: "Define the payroll provider interface and implement the first adapter (Check or Gusto Embedded)"
project: "business-core"
projectName: "Business Core: Payments, Finance & Payroll"
phase: "P2"
type: "Build"
priority: 2
surfaces: ["Staff"]
milestone: "Payroll adapter and cash dashboard"
state: "Backlog"
parent: null
children: ["PAP-398", "PAP-399", "PAP-400"]
blockedBy: ["PAP-175", "PAP-176", "PAP-179", "PAP-359", "PAP-394"]
blocks: []
key: "business-core/payroll-adapter"
url: "https://linear.app/paperos/issue/PAP-184/define-the-payroll-provider-interface-and-implement-the-first-adapter"
source: "Linear snapshot 2026-09-17T15:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T13:41:49.306Z"
model: null
effort: null
---

# PAP-184: Define the payroll provider interface and implement the first adapter (Check or Gusto Embedded)

**Model / Effort:** set on children (umbrella is never claimed)

**Goal**

Implement the `PayrollProvider` interface chosen in PAP-176 and its first adapter (Check by default) so a tenant onboards employees, previews and approves a payroll run and sees paystubs inside PaperOS, with every approved run posted to the ledger. Sandbox only until Justin approves live. Umbrella for three children.

**Scope**

Children (M each, same milestone, Backlog):

* PAP-398 Finalised `provider.ts`, the first adapter with idempotency keys, webhook route and signature handling, the adapter contract test suite.
* PAP-399 Tables, company and employee onboarding via provider links, employee sync from `fin_employee` with a conflict review list, status polling fallback.
* PAP-400 Run flow UI (hours grid, preview, typed-total approval), status transitions from webhooks, `payroll.approved` and `payroll.paid` posting, paystub portal page.

Out: benefits, time tracking, international payroll, live filings.

**Spec**

Decisions binding all children:

* Adapter methods map to provider REST with the TypeScript SDK if one exists, else `ky` 1.x with Zod responses; every mutation carries idempotency key `paperos:<tenant>:<entity>:<version>`; `capabilities()` drives the UI.
* `payroll_company (tenant_id unique, provider, external_company_id, onboarding_status, pay_frequency, next_pay_date, bank_verified, updated_from_event_id)`; `payroll_employee_link (party_id, external_employee_id, onboarding_status, ssn_last4_masked?, w4_complete)`; `payroll_run (external_run_id, period_start, period_end, pay_date, status: draft|previewed|approved|processing|paid|failed|cancelled, totals jsonb, approved_by, approved_at, ledger_entry_id)`; `payroll_run_item` per employee; `payroll_event` for webhook idempotency.
* Approval needs `payroll.approve` and typing the net total; cancel allowed until the provider cutoff; agents may draft, never approve.
* Posting on `approved`: debit `wages_expense`, `payroll_tax_expense`, `payroll_fees`; credit `payroll_liability` (net) and `payroll_tax_liability`; on `paid` move `payroll_liability` to `cash`; dimensions from employee department.
* No SSNs or bank numbers stored; provider secrets via PAP-17; every approve and cancel audited.

**Interface contract**

Provides: `PayrollProvider` implementation registry `payrollProviders[id]`, `payroll.company.*`, `payroll.employees.sync|list`, `payroll.runs.create|preview|approve|cancel|list|get`, `payroll.paystubs.list|url`, webhook route `/api/webhooks/payroll/:provider`, events `payroll.run.approved|paid|failed`, `payroll_run` rows read by PAP-186 (`upcomingPayroll`), contract test `payroll-contract.test.ts` runnable against any adapter. Consumes: interface and ADR (PAP-176), posting (PAP-179), `fin_employee` (PAP-175), notifications (PAP-136 core), portal shell (PAP-64), grid (PAP-165), env (PAP-17).

**Definition of done**

* All three children Done.
* Sandbox end-to-end recorded: company onboarded, two employees, preview, approve, webhook to paid, ledger balanced, paystub visible in the portal.
* Playwright run flow and portal; screenshots at 375, 1024, 1920 in three themes; approval replay.
* `docs/finance/payroll.md` (sandbox setup, capability matrix, live checklist); CHANGELOG; Linear comment with demo link and the Needs Justin item for live approval.

**Test plan**

Umbrella `payroll.e2e.test.ts` with `nock` fixtures recorded from the sandbox: sync two employees (one conflict resolved in the review list), create a run, enter hours, preview, approve with the typed total, replay `processing` and `paid` webhooks (one duplicated, one with a rotated signature), assert status transitions, `payroll_event` dedupe, both journal entries balanced and `payroll_liability` at zero after `paid`; run the contract suite against the mock adapter and the real adapter in sandbox.

**Demo**

Reviewer opens `/finance/payroll`, creates the next run, edits hours for one employee in the grid, previews totals, approves by typing the net amount, then triggers the sandbox `paid` webhook and watches the run flip to Paid and the journal entries appear. Under two minutes.

**Edge cases**

* Employee missing tax setup at approve: provider rejects; UI lists blocked employees with links.
* Bank-holiday pay date: provider's adjusted date shown.
* Off-cycle bonus run when the capability exists.
* Funding failure after approval: `failed`, liabilities remain, owner alerted.
* Terminated mid-period: final pay by provider rules, excluded from future runs.

**Dependencies**

PAP-176 (hard), PAP-179 (hard), PAP-175 (hard), PAP-136 core, PAP-64, PAP-165, sandbox credentials (Needs Justin). Feeds PAP-186.

**Agent**

Builder: Ledger (Payroll Adapter). Reviewer: Sentinel (Security Auditor primary, Code Reviewer); Bookkeeper checks postings.

**Size**

L, split into three M children plus a verification spike on webhook signing.

**Pending issues**

Bracketed references above are fully specified work packages that Linear refused to create on 2026-09-17 (`USAGE_LIMIT_EXCEEDED`, free-plan issue cap). Their specs live in the project document(s) [business-core](<https://linear.app/paperos/document/round-2-pending-issues-business-core-11-7c8c2526b3c9>) and they are created as issues by `round2/agent4/create_issues.py` once the workspace plan is upgraded.
