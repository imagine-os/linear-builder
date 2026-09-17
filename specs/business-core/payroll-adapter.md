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
children: []
blockedBy: ["PAP-175", "PAP-176", "PAP-179"]
blocks: []
key: "business-core/payroll-adapter"
url: "https://linear.app/paperos/issue/PAP-184/define-the-payroll-provider-interface-and-implement-the-first-adapter"
source: "plan/specs/bucket-6.json (round-1 canonical spec JSON)"
---

# PAP-184: Define the payroll provider interface and implement the first adapter (Check or Gusto Embedded)

**Goal**

Implement the `PayrollProvider` interface chosen in `business-core/payroll-research` and its first adapter (Check by default, Gusto Embedded if the ADR chose it), so a tenant can onboard employees, preview and approve a payroll run, and see paystubs inside PaperOS, with every approved run posted to the ledger. Sandbox mode only until Justin approves live.

**Scope**

In:
- `packages/finance/src/payroll/`: `provider.ts` (interface from the ADR, finalised), `adapters/check.ts` (or `gusto.ts`), `service.ts`, tables `payroll_company`, `payroll_employee_link`, `payroll_run`, `payroll_run_item`, `payroll_event`.
- Pages `/finance/payroll` (runs list, run detail, approve), `/finance/payroll/employees` (sync and onboarding status), employee-facing paystubs in the customer portal shell for users linked to `fin_employee`.
- Posting rule `payroll.approved`.
- Webhook route `/api/webhooks/payroll/:provider`.

Out: benefits administration, time tracking (hours come from a manual entry or a future integration), international payroll, live filings.

**Spec**

- Adapter contract: `PayrollProvider` from the ADR; each method maps to provider REST calls with the provider SDK if a TypeScript SDK exists, else `ky` 1.x with typed Zod responses; every mutating call carries an idempotency key `paperos:<tenant>:<entity>:<version>`; `capabilities()` drives UI (e.g. hide contractors if unsupported).
- `payroll_company`: `tenant_id unique, provider, external_company_id, onboarding_status, pay_frequency, next_pay_date, bank_verified, updated_from_event_id`. `payroll_employee_link`: `party_id (fin_employee), external_employee_id, onboarding_status, ssn_last4_masked?, w4_complete`. `payroll_run`: `id, tenant_id, external_run_id, period_start, period_end, pay_date, status: draft|previewed|approved|processing|paid|failed|cancelled, totals jsonb (gross, employee_taxes, employer_taxes, deductions, net, provider_fees), approved_by, approved_at, ledger_entry_id`. `payroll_run_item`: per employee amounts (`gross, net, employee_taxes, employer_taxes, deductions, hours, earnings jsonb`).
- Onboarding: company onboarding via provider-hosted component or link (`companies.onboardingLink`) embedded in an iframe with `sandbox` attributes; employee onboarding links emailed via `collab/notifications`; statuses refreshed by webhooks and a 15-minute poll fallback.
- Employee sync: `payroll.syncEmployees` upserts provider employees from `fin_employee` (name, email, start date, employment type, pay rate from `fin_employee.compensation jsonb` added here); conflicts shown in a review list before pushing.
- Run flow: create run for the next pay period → enter hours/adjustments (grid via `tables/grid-view` over `payroll_run_item`) → `payrolls.preview` shows totals per employee and employer cost → `payrolls.approve` requires `payroll.approve` permission and a confirmation typing the net total → status transitions from webhooks (`processing`, `paid`); cancel allowed until the provider's cutoff (shown from `capabilities`).
- Ledger posting on `approved`: debit `wages_expense` (gross), debit `payroll_tax_expense` (employer taxes), debit `payroll_fees` (provider fee), credit `payroll_liability` (net pay until paid), credit `payroll_tax_liability` (all withholdings and employer taxes); on `paid` move `payroll_liability` to `cash`; dimensions from employee department.
- Paystubs: `paystubs.list` cached per run; employee portal page lists their paystubs with PDF links proxied through our API (short-lived signed URLs), access limited to the linked user.
- Security: all provider secrets in `app-shell/env-config`; no SSNs or bank numbers stored (only provider ids and masked last4); audit every approve/cancel; agents can prepare drafts but never approve.

**Definition of done**

- Sandbox end-to-end recorded: onboard company, two employees, preview, approve, webhook to paid, ledger balanced, paystub visible in portal.
- Vitest for adapter mapping with recorded fixtures (`nock`), idempotency, status machine, posting rule totals.
- Contract test suite runnable against any adapter (`packages/finance/test/payroll-contract.test.ts`).
- Playwright: run flow and employee portal; screenshots at 375, 1024, 1920 in three themes; video replay of approve.
- `docs/finance/payroll.md` with sandbox setup, capability matrix and live activation checklist; CHANGELOG entry; Linear comment with demo link and Needs Justin item for live approval.

**Edge cases**

- Employee missing tax setup at approve time: provider rejects; UI lists blocked employees with onboarding links.
- Pay date on a bank holiday: use provider's adjusted date and show it.
- Off-cycle bonus run: supported as `kind: off_cycle` if capability present.
- Webhook signature rotation: two secrets accepted during rotation window.
- Run approved then provider fails funding (NSF): `failed` status, liabilities remain, alert to owner.
- Terminated employee mid-period: final pay handled by provider rules; employee shows `terminated` and excluded from future runs.

**Dependencies**

- `business-core/payroll-research` (ADR, interface), `business-core/ledger` (posting), `business-core/finance-data-model` (`fin_employee`), `collab/notifications`, `identity/customer-portal-shell`, `tables/grid-view`.

**Agent**

Builder: Ledger (Payroll Adapter). Reviewer: Sentinel (Security Auditor primary, Code Reviewer); Bookkeeper checks postings.

**Size**

L: external sandbox dependency and a strict approval flow; two sessions plus a verification spike.
