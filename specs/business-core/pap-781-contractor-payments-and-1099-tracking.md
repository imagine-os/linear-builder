---
identifier: "PAP-781"
title: "Contractor payments and 1099 tracking: contractor onboarding through the payroll provider, payments via provider or Connect transfers, W-9 status, 1099-NEC threshold tracking and year-end forms"
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
blockedBy: ["PAP-181", "PAP-398", "PAP-399"]
blocks: []
key: "r4/business-core/contractors-and-1099"
url: "https://linear.app/paperos/issue/PAP-781/contractor-payments-and-1099-tracking-contractor-onboarding-through"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:42.497Z"
model: "claude-opus-5"
effort: "high"
estimate: 3
dueDate: null
cycle: null
---

# PAP-781: Contractor payments and 1099 tracking: contractor onboarding through the payroll provider, payments via provider or Connect transfers, W-9 status, 1099-NEC threshold tracking and year-end forms

**Model / Effort:** Opus 5 (`claude-opus-5`) / high — Build M

**Goal**

Deferred to v0.2 by the Execution Schedule (NJ-14 stop-loss 09-27 can reinstate). Not claimable before 10-01.

PAP-175 knows contractors (`employment_type`, `w9_on_file`) and PAP-176 lists `contractors?` as an optional provider capability, but no issue pays a contractor or tracks the 1099 threshold. Agencies, salons, construction and gig businesses are mostly contractors.

**Scope**

In: `payroll_contractor_link (party_id, external_contractor_id, onboarding_status, w9_status, tax_classification)`; onboarding through the provider's hosted link when `capabilities.contractors`, else PaperOS collects only W-9 status flags (never the TIN) and pays via PAP-181 `createTransfer` to the contractor's Connect Express account; `contractorPayments.create|approve|pay` with typed-total approval like PAP-400; postings `contractor.paid` (debit `contractor_expense`, credit cash); YTD paid per contractor with the 1099-NEC threshold (configurable, default 600.00) and a year-end dataset `finance.form1099`; provider filing status surfaced when supported; portal page for contractors to see payments and download forms provided by the provider.

Out: international contractors and withholding (capability flag only), EOR products, W-2 employees (PAP-400).

**Spec**

* No TIN or bank number stored by PaperOS; provider-hosted or Stripe-hosted collection only (PAP-359 rules apply; Semgrep gate).
* Payments are idempotent on `paperos:<tenant>:contractor_payment:<id>`; failures leave `approved` with error.
* Threshold tracking by calendar year in USD only in v0.2; other jurisdictions get a capability note.
* Agents may draft payments, never approve or pay (deny list).

**Interface contract**

Provides: tables, `contractors.*`, `contractorPayments.*`, posting rule, datasets `finance.contractorPayments`, `finance.form1099`, portal route `_portal/contractor`. Consumes: provider adapter and capabilities (PAP-398), onboarding patterns (PAP-399), Connect transfers (PAP-181), approval UX (PAP-400), permissions (PAP-768), portal (PAP-64).

**Definition of done**

* Mock adapter and Stripe test-mode flows recorded: onboard, pay two contractors, one crosses the threshold and appears in the 1099 dataset; postings balance; no live key.
* Screenshots at 375, 1024, 1920 in three themes; `docs/finance/contractors.md` with the year-end checklist; CHANGELOG.

**Test plan**

* Unit: threshold arithmetic across years, idempotency, approval guard, capability branching.
* E2E: onboard via the mock link, approve a payment with the typed total, trigger the paid event, open the 1099 dataset.

**Demo**

Reviewer pays a seeded contractor twice, the second payment crosses 600.00 and the contractor appears in the 1099 list with the YTD total. Under two minutes.

**Edge cases**

* Contractor becomes an employee mid-year: both datasets show the split by date (PAP-175 history).
* Payment reversed: negative row, YTD adjusted.
* Provider lacks contractor support: Connect path only, banner explains filings are the tenant's job.

**Dependencies**

Hard: PAP-398, PAP-399, PAP-181. Soft: PAP-400, PAP-64, PAP-768.

**Agent**

Builder: Ledger (Payroll Adapter with Payments Integrator). Reviewer: Sentinel (Security Auditor, Code Reviewer).

**Size**

M: one session.

*Round 4 critique fix (2026-09-18):* resolved 1 round-4 file key in this description to Linear identifiers: `r4/business-core/finance-permissions-and-roles` = PAP-768.
