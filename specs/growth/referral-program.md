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
children: []
blockedBy: ["PAP-177", "PAP-179", "PAP-181"]
blocks: []
key: "growth/referral-program"
url: "https://linear.app/paperos/issue/PAP-196/implement-a-referral-and-affiliate-program-with-stripe-connect-payouts"
source: "plan/specs/bucket-7.json (round-1 canonical spec JSON)"
---

# PAP-196: Implement a referral and affiliate program with Stripe Connect payouts

**Goal**

Let customers and partners recruit customers: referral codes and affiliate links that attribute signups and paid conversions, calculate rewards (credit, discount or cash), and pay cash rewards through Stripe Connect transfers with ledger postings, all with fraud checks and a customer-facing referral page in the portal.

**Scope**

In:
- Schema `packages/growth/src/referral/schema.ts`: `referral_program` (`name`, `kind: referral|affiliate`, `reward jsonb` `{ referrer: { type: credit|discount|cash, amount, currency|percent, trigger: signup|first_payment|each_payment, months? }, referee: {...} }`, `terms_url`, `status`), `referral_code` (`program_id`, `owner_contact_id|owner_user_id`, `code` unique per tenant, `landing_url`, `clicks`), `referral` (`code_id`, `referee_contact_id`, `referee_customer_id` (Stripe), `status: clicked|signed_up|qualified|rewarded|rejected`, `qualified_at`, `fraud_flags jsonb`), `referral_reward` (`referral_id`, `beneficiary`, `type`, `amount_cents`, `status: pending|approved|paid|voided`, `stripe_transfer_id`, `ledger_entry_id`, `paid_at`), `affiliate_account` (`contact_id`, `stripe_connect_account_id`, `onboarding_status`, `tax_form_status`).
- Link handling: `/r/{code}` route records a click event (`growth/attribution` channel `affiliate`), sets `localStorage` referral token, redirects to `landing_url`; signup and Stripe checkout read the token and stamp `referral`.
- Qualification worker: listens to `identity` signup events and `business-core/stripe-billing` webhooks (`invoice.paid`), moves referrals to `qualified`, creates rewards per program rules, applies credit or discount via Stripe coupons or customer balance, and queues cash rewards.
- Payouts: cash rewards approved by staff (or auto under a threshold) create Stripe Connect `transfers` to the affiliate's connected account (`business-core/stripe-connect`), post a journal entry (`business-core/ledger`: debit marketing expense, credit payable then cash), monthly statement PDF (`business-core/invoicing` renderer).
- Portal page `_portal/referrals` (`identity/customer-portal-shell`): your code and link, share buttons, referral status list, rewards earned, Connect onboarding CTA for cash programs; console pages: programs, referrals grid, rewards approval queue.

Out: multi-level marketing, coupon marketplaces, tax form generation beyond storing Stripe's 1099 status, non-Stripe payout rails.

**Spec**

- Codes: 8 characters, Crockford base32, case-insensitive, customisable vanity codes with profanity filter.
- Attribution window 30 days from click (per program); last click wins unless a code was entered manually at checkout.
- Fraud rules: self-referral (same email domain plus same payment fingerprint), disposable emails, more than 5 signups from one `ip_hash` per day, refunded first invoice voids the reward; flags require staff review before payout.
- Cash rewards accrue in `pending` until the referee's first invoice is 30 days past refund window; then `approved`.
- Ledger accounts used: `6200 Marketing - Referral rewards`, `2100 Affiliate payables`, `1000 Cash`; all postings idempotent by `referral_reward.id`.
- Terms acceptance recorded per affiliate with version and timestamp.

**Definition of done**

- Vitest: code generation and normalisation, attribution window and precedence, reward rule evaluation for the three trigger types, fraud rules against fixtures, ledger posting balances.
- Stripe test mode integration: signup with code, pay first invoice, reward approved after fast-forward, transfer created to a test Connect account; recording attached.
- Playwright: portal referral page share flow and status list; console approval queue; screenshots at 320, 375, 768, 1024, 1280, 1536 and 1920 in light and dark for portal page and approval queue.
- Permission tests: customer sees only own referrals; staff `referral.approve` required for payouts.
- `docs/growth/referrals.md` incl. fraud and accounting notes reviewed by Ledger; CHANGELOG entry; Linear comment with recording.

**Edge cases**

- Referee already an existing customer: referral `rejected` with reason, referrer notified politely.
- Referrer without a Connect account earns cash: reward stays `approved`, portal shows onboarding CTA; expires after 180 days to `voided` with notice.
- Currency mismatch between program and referee invoice: convert at invoice-day rate from finance rates; store both amounts.
- Refund after payout: negative reward created and netted against future payouts; ledger reversal posted.
- Code shared publicly and hits 1,000 signups a day: program-level daily cap pauses rewards, not signups.
- Stripe transfer fails (account restricted): reward back to `approved` with error surfaced; retry manual.

**Dependencies**

`business-core/stripe-connect` (hard). `business-core/stripe-billing` (webhooks), `business-core/ledger` (postings), `business-core/invoicing` (statement PDF, soft), `identity/customer-portal-shell`, `growth/attribution` (click channel), `growth/crm-model` (contacts).

**Agent**

Built by Beacon (CRM Builder) with Ledger (Payments Integrator) pairing on Connect and postings. Reviewed by Sentinel (Security Auditor for fraud and money paths, Visual Inspector) and Ledger (Bookkeeper) for accounting.

**Size**

L: money movement, fraud logic, ledger integration and two audiences' UI.
