---
identifier: "PAP-196"
title: "Implement a referral and affiliate program with Stripe Connect payouts"
project: "growth"
projectName: "Growth: Marketing, Outreach & CRM"
phase: "P2"
type: "Build"
priority: 4
surfaces: ["Customer"]
milestone: "Acquisition analytics"
state: "Backlog"
parent: null
children: ["PAP-407", "PAP-408", "PAP-409"]
blockedBy: ["PAP-177", "PAP-179", "PAP-181", "PAP-394"]
blocks: []
key: "growth/referral-program"
url: "https://linear.app/paperos/issue/PAP-196/implement-a-referral-and-affiliate-program-with-stripe-connect-payouts"
source: "Linear snapshot 2026-09-17T15:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T13:41:54.136Z"
model: null
effort: null
---

# PAP-196: Implement a referral and affiliate program with Stripe Connect payouts

**Model / Effort:** set on children (umbrella is never claimed)

**Goal**

Deferred to v0.2 by the Execution Schedule (NJ-14 stop-loss 09-27 can reinstate). Not claimable before 10-01.

Let customers and partners recruit customers: referral codes and affiliate links that attribute signups and paid conversions, calculate rewards (credit, discount or cash), pay cash through Stripe Connect transfers with ledger postings, with fraud checks and a portal referral page. Deferred per the round-2 audit: lowest priority, built only if P2 finishes early. Umbrella for three children.

**Scope**

Children (same milestone, Backlog):

* PAP-407 (M) Programs, codes, `/r/{code}` route, attribution window, qualification worker on signup and `invoice.paid` events.
* PAP-408 (M) Reward rules, fraud rules, approval, Connect transfers, ledger postings, monthly statements.
* PAP-409 (S) Portal referral page, console programs and referrals grids, approval queue.

Out: multi-level marketing, coupon marketplaces, tax forms beyond storing Stripe's 1099 status, non-Stripe rails.

**Spec**

Decisions binding all children:

* `referral_program (name, kind: referral|affiliate, reward jsonb { referrer, referee }, terms_url, status, daily_cap)`, `referral_code (program_id, owner_contact_id|owner_user_id, code, landing_url, clicks)`, `referral (code_id, referee_contact_id, referee_customer_id, status: clicked|signed_up|qualified|rewarded|rejected, qualified_at, fraud_flags jsonb)`, `referral_reward (referral_id, beneficiary, type, amount_minor, status: pending|approved|paid|voided, stripe_transfer_id, ledger_entry_id, paid_at)`, `affiliate_account (contact_id, stripe_connect_account_id, onboarding_status, tax_form_status, terms_version, accepted_at)`.
* Codes: 8-character Crockford base32, case-insensitive, vanity codes with a profanity filter; attribution window 30 days, last click wins unless a code was entered at checkout.
* Fraud: self-referral (domain plus payment fingerprint), disposable emails, more than 5 signups per `ip_hash` per day, refunded first invoice voids the reward; flags require staff review.
* Cash rewards `pending` until 30 days past the refund window, then `approved`; payouts through PAP-181 `createTransfer`; postings debit `marketing_referral` expense, credit `affiliate_payable`, then payable to cash; idempotent by `referral_reward.id`.

**Interface contract**

Provides: `referrals.programs|codes|referrals|rewards.*`, route `/r/{code}`, `referralTokenFromRequest()` used by signup (PAP-57 children) and checkout (PAP-177), events `referral.qualified`, `referral.reward.paid`, channel `affiliate` for PAP-194, portal route `_portal/referrals`. Consumes: Connect transfers (PAP-181), billing webhooks (PAP-177), posting (PAP-179), statement PDFs (PAP-180, soft), portal shell (PAP-64), attribution click events (PAP-194), contacts (PAP-187).

**Definition of done**

* All three children Done.
* Stripe test-mode integration: signup with code, first invoice paid, reward approved after a test-clock advance, transfer to a test Connect account; recording attached.
* Permission tests: customers see only their referrals; `referral.approve` required for payouts.
* Screenshots at 320, 375, 768, 1024, 1280, 1536, 1920 in light and dark for the portal page and approval queue.
* `docs/growth/referrals.md` with fraud and accounting notes reviewed by Ledger; CHANGELOG; Linear comment with recording.

**Test plan**

Umbrella `referrals.e2e.spec.ts` with a test clock: click `/r/CODE`, sign up, pay the first invoice through `stripe trigger`, assert `qualified` and a `pending` reward; advance 31 days past the refund window and assert `approved`; approve payout as staff and assert the transfer id and balanced postings; refund the invoice and assert a negative reward netted against the next payout with a ledger reversal; run the fraud fixtures (self-referral, disposable email, 6 signups from one hash) and assert flags block payout.

**Demo**

Reviewer copies their code from the portal referral page, signs up a second test user through the link, pays the first invoice with `4242`, then as staff approves the reward in the console queue and sees the Connect transfer and journal entry. Under two minutes.

**Edge cases**

* Referee already a customer: `rejected` with a polite notice.
* Cash reward without a Connect account: stays `approved` with an onboarding CTA, voided after 180 days.
* Currency mismatch: converted at invoice-day rate, both stored.
* Public code hitting 1,000 signups a day: program cap pauses rewards, not signups.
* Transfer failure: reward back to `approved` with error and manual retry.

**Dependencies**

PAP-181 (hard), PAP-177 (hard), PAP-179 (hard), PAP-180 (soft), PAP-64, PAP-194 (soft), PAP-187. Deferred: schedule only after every other P2 issue in growth and business-core is In Review.

**Agent**

Builder: Beacon (CRM Builder) with Ledger (Payments Integrator) on Connect and postings. Reviewer: Sentinel (Security Auditor for fraud and money paths, Visual Inspector), Ledger (Bookkeeper) for accounting.

**Size**

L, split into two M children and one S child; deferred.

**Pending issues**

Bracketed references above are fully specified work packages that Linear refused to create on 2026-09-17 (`USAGE_LIMIT_EXCEEDED`, free-plan issue cap). Their specs live in the project document(s) [growth](<https://linear.app/paperos/document/round-2-pending-issues-growth-13-3fd4406e8012>) and they are created as issues by `round2/agent4/create_issues.py` once the workspace plan is upgraded.
