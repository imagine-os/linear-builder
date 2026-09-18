---
identifier: "PAP-777"
title: "Deposits, retainers and installment plans: partial payment schedules on quotes and invoices, retainer balances with drawdown, deferred liability postings"
project: "business-core"
projectName: "Business Core: Payments, Finance & Payroll"
phase: "P2"
type: "Build"
priority: 4
surfaces: ["Customer"]
milestone: "Payroll adapter and cash dashboard"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-395", "PAP-396", "PAP-397"]
blocks: []
key: "r4/business-core/deposits-retainers-installments"
url: "https://linear.app/paperos/issue/PAP-777/deposits-retainers-and-installment-plans-partial-payment-schedules-on"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:41.597Z"
model: "claude-opus-5"
effort: "high"
estimate: 3
dueDate: null
cycle: null
---

# PAP-777: Deposits, retainers and installment plans: partial payment schedules on quotes and invoices, retainer balances with drawdown, deferred liability postings

**Model / Effort:** Opus 5 (`claude-opus-5`) / high — Build M

**Goal**

Deferred to v0.2 by the Execution Schedule (NJ-14 stop-loss 09-27 can reinstate). Not claimable before 10-01.

Agencies take retainers, contractors take deposits, clinics take instalments. PAP-180 handles a whole invoice paid at once or partially by hand; this adds payment schedules, deposit requests on quotes and retainer balances drawn down by later invoices, with the liability accounting done right.

**Scope**

In: `fin_payment_schedule (document_id, installments jsonb [{ due_date, amount_minor, status, stripe_checkout_session_id? }])` on quotes and invoices; deposit request on quote acceptance (PAP-395 `accept` creates the deposit checkout via PAP-396); `fin_retainer (party_id, balance_minor, currency, terms)` funded by a `retainer` document kind and drawn down by `documents.applyRetainer`; postings `deposit.received` (debit cash, credit `customer_deposits` liability), `deposit.applied` (debit liability, credit `ar`), retainer analogues; pay page shows the schedule with one Pay button per due instalment; portal Upcoming integration with the recurring issue.

Out: financing or BNPL providers, interest, refunds of deposits beyond the refund issue.

**Spec**

* Instalment sums must equal the document total (`Money.allocate` for even splits); editing a schedule after any payment only touches unpaid instalments.
* Each instalment payment is idempotent on `stripe_event.id`; the document becomes `partial` until the last instalment, then `paid`.
* Retainer drawdown is capped at the balance; the remainder of an invoice stays open on `ar`.
* Unapplied deposits older than a tenant-set number of days appear in a review dataset.

**Interface contract**

Provides: `schedules.*`, `retainers.*`, `documents.applyRetainer`, posting rules `deposit.*`, `retainer.*`, pay-page schedule component, dataset `finance.unappliedDeposits`. Consumes: documents (PAP-395), pay page and Checkout (PAP-396), postings and receipts (PAP-397), portal (PAP-64), recurring Upcoming list (PAP-765, soft).

**Definition of done**

* Test-mode flow recorded: quote with 30 percent deposit accepted and paid, invoice issued, two instalments paid, liability at zero; no live key.
* Rule fixtures balance; Playwright schedule editor and pay page; screenshots at 375, 1024, 1920 in three themes.
* `docs/finance/deposits-retainers.md`; CHANGELOG.

**Test plan**

* Unit: allocation, schedule edit rules, drawdown cap, status transitions, liability arithmetic.
* E2E: accept a quote with a deposit, pay it with `4242`, issue the invoice, apply the deposit and pay the remaining instalment.

**Demo**

Reviewer funds a retainer, issues an invoice larger than the balance, applies the retainer and sees the remaining AR and the liability entries. Under two minutes.

**Edge cases**

* Instalment paid early: allowed; later instalments unchanged.
* Deposit on a quote that is later declined: stays as an unapplied deposit awaiting refund or credit.
* Currency of retainer differs from invoice: refused with the currency named.

**Dependencies**

Hard: PAP-395, PAP-396, PAP-397. Soft: PAP-64, PAP-765, PAP-786.

**Agent**

Builder: Ledger (Payments Integrator with Bookkeeper). Reviewer: Sentinel (Security Auditor for the pay page, Code Reviewer).

**Size**

M: one session.

*Round 4 critique fix (2026-09-18):* resolved 2 round-4 file keys in this description to Linear identifiers: `r4/business-core/document-refunds-and-credit-balance` = PAP-786, `r4/business-core/recurring-invoices-dunning` = PAP-765.
