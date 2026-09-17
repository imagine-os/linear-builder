---
key: "growth/referral/rewards-payouts-ledger"
title: "Reward rules, fraud rules, approval, Stripe Connect transfers, ledger postings and monthly statements"
project: "growth"
parent: "PAP-196"
phase: "P2"
type: "Build"
priority: 4
size: "M"
surfaces: []
milestone: "Acquisition analytics"
intendedState: "Backlog"
blockedBy: []
blocks: []
source: "round2/agent4/pending-issues.json"
linearDocument: "https://linear.app/paperos/document/round-2-pending-issues-growth-13-3fd4406e8012"
identifier: "PAP-408"
status: "created"
createdAt: "2026-09-17"
---

# Reward rules, fraud rules, approval, Stripe Connect transfers, ledger postings and monthly statements

**Goal**

Turn qualified referrals into correct, fraud-checked rewards and pay cash rewards with balanced books.

**Scope**

In: `referral_reward`, `affiliate_account`; reward rule evaluation for the three triggers; fraud flags; `referrals.rewards.approve|void`; Connect transfers via PAP-181; postings; statement PDFs via PAP-180 renderer. Deferred with the parent.

**Spec**

* Cash rewards `pending` until 30 days past the refund window; credit and discount via Stripe coupons or customer balance.
* Fraud: self-referral, disposable emails, more than five signups per `ip_hash` per day, refunded first invoice voids; flags block payout until review.
* Postings debit `marketing_referral`, credit `affiliate_payable`, then payable to cash; idempotent by reward id; refunds create negative rewards netted against future payouts.

**Interface contract**

Provides: `referrals.rewards.*`, `affiliate_account`, events `referral.reward.paid`, statements. Consumes: codes child, PAP-181 `createTransfer`, PAP-179, PAP-180 (soft), PAP-177 coupons.

**Definition of done**

* Rule and fraud fixtures; test-mode transfer recorded; postings balance; refund netting test.

**Test plan**

* Unit: rules, fraud, netting.
* Integration: approve to transfer to journal entry; refund reversal.

**Demo**

Approve a pending reward and open the transfer in Stripe and the entry in the journal.

**Edge cases**

* No Connect account: `approved` with CTA, voided at 180 days; transfer failure returns to `approved`.

**Dependencies**

Codes child (hard), PAP-181, PAP-179 (hard), PAP-180 (soft).

**Agent**

Builder: Beacon with Ledger (Payments Integrator). Reviewer: Sentinel (Security Auditor), Bookkeeper.

**Size**

M: deferred.
