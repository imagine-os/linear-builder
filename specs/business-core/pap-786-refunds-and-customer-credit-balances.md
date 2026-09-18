---
identifier: "PAP-786"
title: "Refunds and customer credit balances: refund a paid document through Stripe or manually, credit note application to future invoices, credit balance tracking and postings"
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
blockedBy: ["PAP-181", "PAP-396", "PAP-397"]
blocks: []
key: "r4/business-core/document-refunds-and-credit-balance"
url: "https://linear.app/paperos/issue/PAP-786/refunds-and-customer-credit-balances-refund-a-paid-document-through"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:43.233Z"
model: "claude-opus-5"
effort: "high"
estimate: 3
dueDate: null
cycle: null
---

# PAP-786: Refunds and customer credit balances: refund a paid document through Stripe or manually, credit note application to future invoices, credit balance tracking and postings

**Model / Effort:** Opus 5 (`claude-opus-5`) / high — Build M

**Goal**

Deferred to v0.2 by the Execution Schedule (NJ-14 stop-loss 09-27 can reinstate). Not claimable before 10-01.

PAP-395 issues credit notes against paid balances but money never goes back. Refunds and credit balances are how every business fixes a wrong charge; the flow must be idempotent, permission-gated and correctly posted on both the platform and connected accounts.

**Scope**

In: `documents.refund({ documentId, amountMinor, method: stripe|manual, reason })` creating a `refund` `fin_transaction`, calling `stripe.refunds.create` on the right account with `refund_application_fee` per the PAP-181 policy and idempotency key `refund:<document>:<n>`, or recording a manual refund with reference; webhook `charge.refunded` reconciles; postings `refund.issued` (debit revenue or `refunds_contra`, credit cash or `stripe_balance`; sales tax reversal via PAP-182 `createReversal` when enabled); `fin_customer.credit_balance_minor` maintained from credit notes and overpayments; `documents.applyCredit` on issue; portal shows credit available and refund status; approval above `fin_settings.refund_approval_threshold_minor`.

Out: chargebacks (PAP-779), refunds of platform subscriptions (Stripe Billing and PAP-177 portal), gift cards.

**Spec**

* A refund may not exceed the document's `paid_minor` minus prior refunds (checked under a document lock).
* Manual refunds require `payments.manage`; Stripe refunds additionally require the restricted key with refund scope, held by the worker, never by a session (deny list PAP-298).
* Credit balance application creates a `credit_applied` line and posts liability to `ar`; balances are `Money` per currency.
* Receipts for refunds render with the PAP-396 template variant `refund-receipt`.

**Interface contract**

Provides: `documents.refund|applyCredit`, `fin_refund` rows, posting rules `refund.*`, `credit.applied`, portal credit display, notification kind `document.refunded`. Consumes: pay page and receipts (PAP-396), postings and templates (PAP-397), Connect (PAP-181), tax reversal (PAP-182, optional), permissions (PAP-768), audit (PAP-38).

**Definition of done**

* Test-mode flow recorded: full and partial Stripe refunds via `stripe trigger charge.refunded`, one manual refund, one credit note applied to the next invoice; postings balance; duplicate webhook idempotent; no live key.
* Screenshots at 375, 1024, 1920 in three themes; `docs/finance/refunds.md`; CHANGELOG.

**Test plan**

* Unit: over-refund guard, allocation across lines, credit balance maths, approval routing, idempotency.
* E2E: pay an invoice with `4242`, refund half, see the refund receipt and journal, then issue a credit note and apply it to a new invoice.

**Demo**

Reviewer refunds part of a paid invoice, watches the webhook reconcile it and applies a credit note to the next invoice. Under two minutes.

**Edge cases**

* Refund after payout already left the connected balance: Stripe debits the next payout; posting to `stripe_balance` may go negative with a banner.
* Refund in a different currency than paid: refused; refund in payment currency only.
* Approver equals requester: separation-of-duties rule applies.

**Dependencies**

Hard: PAP-396, PAP-397, PAP-181. Soft: PAP-182, PAP-38, PAP-768.

**Agent**

Builder: Ledger (Payments Integrator). Reviewer: Sentinel (Security Auditor, Code Reviewer).

**Size**

M: one session.

*Round 4 critique fix (2026-09-18):* resolved 2 round-4 file keys in this description to Linear identifiers: `r4/business-core/disputes-radar-evidence` = PAP-779, `r4/business-core/finance-permissions-and-roles` = PAP-768.
