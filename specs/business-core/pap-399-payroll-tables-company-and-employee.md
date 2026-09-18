---
identifier: "PAP-399"
title: "Payroll tables, company and employee onboarding via provider links, employee sync from fin_employee and status polling"
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
blockedBy: ["PAP-175", "PAP-398"]
blocks: ["PAP-400", "PAP-781", "PAP-884"]
key: "business-core/payroll/onboarding-sync"
url: "https://linear.app/paperos/issue/PAP-399/payroll-tables-company-and-employee-onboarding-via-provider-links"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T13:55:54.768Z"
model: "claude-sonnet-5"
effort: "high"
estimate: 3
dueDate: "2026-10-01"
cycle: null
---

# PAP-399: Payroll tables, company and employee onboarding via provider links, employee sync from fin_employee and status polling

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / high — Build M

**Goal**

Get a tenant and its employees onboarded with the provider and kept in sync with `fin_employee`, without storing sensitive data.

**Scope**

In: `payroll_company`, `payroll_employee_link`; `payroll.company.start|status`, `payroll.employees.sync|list|onboardingLink`; `/finance/payroll/employees` page; 15-minute poll fallback; onboarding emails via PAP-136 core. Out: runs and postings (sibling).

**Spec**

* Company onboarding via provider-hosted component or link in a sandboxed iframe; employee links emailed; statuses updated by webhooks or poll.
* `syncEmployees` upserts from `fin_employee` (name, email, start date, type, `compensation jsonb`); conflicts shown in a review list before pushing; no SSNs or bank numbers stored, only provider ids and masked last four.

**Interface contract**

Provides: the two tables, procedures above, employees page, event `payroll.employee.onboarded`. Consumes: adapter child, `fin_employee` (PAP-175), notifications (PAP-136 core), grid (PAP-165).

**Definition of done**

* Sync conflict tests; Playwright onboarding status page; screenshots at 375, 1024, 1920; audit rows for every sync.

*Round 4 amendment (2026-09-18):*
Round 4: the CI gate is the mock adapter path (onboarding, sync, conflict review) with recorded fixtures; the sandbox recording is attached when `PAYROLL_SANDBOX_KEY` exists and otherwise the test reports `skipped: no-credentials`, so this child is mergeable before NJ-12 resolves.

**Test plan**

* Unit: upsert mapping, conflict detection, masking.
* Integration: sandbox onboarding of a company and two employees recorded; poll fallback marks status when webhooks are disabled.

**Demo**

Open `/finance/payroll/employees`, sync two seeded employees, resolve one conflict, send an onboarding link.

**Edge cases**

* Employee without email cannot be synced and is listed; terminated employee marked and excluded.

**Dependencies**

Adapter child (hard), PAP-175, PAP-136 core, PAP-165.

**Agent**

Builder: Ledger (Payroll Adapter). Reviewer: Sentinel (Security Auditor).

**Size**

M: one session.
