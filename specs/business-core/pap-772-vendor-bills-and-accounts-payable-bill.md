---
identifier: "PAP-772"
title: "Vendor bills and accounts payable: bill entry and approval, due-date scheduling, payment batches via Stripe or manual, remittance advice and AP postings"
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
blockedBy: ["PAP-43", "PAP-181", "PAP-395", "PAP-397", "PAP-565"]
blocks: ["PAP-773"]
key: "r4/business-core/vendor-bills-and-ap-payments"
url: "https://linear.app/paperos/issue/PAP-772/vendor-bills-and-accounts-payable-bill-entry-and-approval-due-date"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:51:46.522Z"
model: "claude-opus-5"
effort: "high"
estimate: 3
dueDate: null
cycle: null
---

# PAP-772: Vendor bills and accounts payable: bill entry and approval, due-date scheduling, payment batches via Stripe or manual, remittance advice and AP postings

**Model / Effort:** Opus 5 (`claude-opus-5`) / high — Build M

**Goal**

Deferred to v0.2 by the Execution Schedule (NJ-14 stop-loss 09-27 can reinstate). Not claimable before 10-01.

PAP-180 defines a `bill` kind and PAP-183 an AP aging, but nobody owns entering, approving and paying vendor bills. Every business pays suppliers; this closes the payable half of the ledger.

**Scope**

In: `packages/finance/src/payables/`: bill editor on `fin_document kind bill` (vendor, lines to expense accounts, due date from vendor terms, attachment), approval flow with `fin_settings.bill_approval_threshold_minor`, `bills.schedulePayment`, payment batches `fin_payment_batch (method: stripe_transfer|ach_manual|check|wire|card, status, total_minor, executed_at)`, execution through PAP-181 `createTransfer` to vendor Connect accounts when both sides are onboarded, else `mark paid` with reference; remittance advice email (PAP-397 templates); postings `bill.approved` (debit expense per line, credit `ap`), `bill.paid` (debit `ap`, credit `cash`), partial payments; vendor portal-less: remittance PDF only.

Out: purchase orders and three-way matching (PAP-773), receipt OCR (PAP-185, which creates bills here), payroll (PAP-184).

**Spec**

* Bill statuses `draft|pending_approval|approved|scheduled|partial|paid|void`; transitions are the only writes; approval by a second user above threshold (reuses PAP-768 separation rules).
* Payment execution is a PAP-43 job with idempotency key `bill:<id>:<attempt>`; Stripe transfers use the restricted `payouts` key from PAP-359; failures leave the bill `scheduled` with the error.
* Early-payment discount terms (`2/10 net 30`) compute the discount line when paid inside the window.
* Agents may draft and propose payments, never execute (deny list: payouts and transfers).

**Interface contract**

Provides: `bills.*`, `paymentBatches.*`, posting rules `bill.*`, dataset `finance.bills` (AP aging source), notification kinds `bill.approval_requested|paid`. Consumes: documents (PAP-395), templates and postings (PAP-397), Connect transfers (PAP-181), jobs (PAP-43), permissions (PAP-768), files (PAP-37).

**Definition of done**

* Test-mode flow recorded: bill entered, approved by a second user, scheduled, executed through a Stripe test transfer, `ap` at zero; no live key.
* Rule fixtures balance; Playwright bill editor and batch approval; screenshots at 375, 1024, 1920 in three themes.
* `docs/finance/payables.md`; CHANGELOG.

**Test plan**

* Unit: transitions, threshold routing, discount window maths, partial payment allocation with `Money.allocate`, idempotency.
* E2E: enter a bill from a PDF attachment, approve as a second user, add to a batch, execute in test mode, see remittance email in the sandbox and the journal entries.

**Demo**

Reviewer creates a bill over the threshold, sees approval requested, approves as the seeded accountant, pays it in a test batch and opens the AP aging showing it gone. Under two minutes.

**Edge cases**

* Vendor without a Connect account: batch offers manual methods only.
* Bill in a foreign currency: FX at approval and payment via PAP-766.
* Duplicate bill (same vendor, number, total): warned before save.
* Void after partial payment: refused; credit note path instead.

**Dependencies**

Hard: PAP-395, PAP-397, PAP-181, PAP-43. Soft: PAP-768, PAP-766, PAP-185. Blocks PAP-183 AP aging completeness (soft).

* Soft dependency (round 4): PAP-183 is a soft dependency, not a `blocks` relation, because this issue's milestone (2026-10-01) is later than PAP-183's (2026-09-29); build against its interface and reconcile when it lands.
  **Agent**

Builder: Ledger (Payments Integrator with Bookkeeper). Reviewer: Sentinel (Security Auditor for money movement, Code Reviewer).

**Size**

M: one session.

*Round 4 critique fix (2026-09-18):* resolved 3 round-4 file keys in this description to Linear identifiers: `r4/business-core/finance-permissions-and-roles` = PAP-768, `r4/business-core/fx-rates-and-conversion` = PAP-766, `r4/business-core/purchase-orders-and-receiving` = PAP-773.
