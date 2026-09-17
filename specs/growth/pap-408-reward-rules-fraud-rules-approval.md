---
identifier: "PAP-408"
title: "Reward rules, fraud rules, approval, Stripe Connect transfers, ledger postings and monthly statements"
project: "growth"
projectName: "Growth: Marketing, Outreach & CRM"
phase: "P2"
type: "Build"
priority: 4
surfaces: ["Customer"]
milestone: "Acquisition analytics"
state: "Backlog"
parent: "PAP-196"
children: []
blockedBy: ["PAP-179", "PAP-181", "PAP-407"]
blocks: ["PAP-409"]
key: "growth/referral/rewards-payouts-ledger"
url: "https://linear.app/paperos/issue/PAP-408/reward-rules-fraud-rules-approval-stripe-connect-transfers-ledger"
source: "Linear snapshot 2026-09-17T15:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T13:42:51.916Z"
model: "claude-sonnet-5"
effort: "low"
---

# PAP-408: Reward rules, fraud rules, approval, Stripe Connect transfers, ledger postings and monthly statements

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / low — Deferred label (excluded from Oct-1 scope)

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
