---
identifier: "PAP-181"
title: "Add Stripe Connect so tenants can accept payments and receive payouts"
project: "business-core"
projectName: "Business Core: Payments, Finance & Payroll"
phase: "P2"
type: "Build"
priority: 2
surfaces: ["Customer", "Staff"]
milestone: "Ledger and reports"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-175", "PAP-177", "PAP-179"]
blocks: ["PAP-196"]
key: "business-core/stripe-connect"
url: "https://linear.app/paperos/issue/PAP-181/add-stripe-connect-so-tenants-can-accept-payments-and-receive-payouts"
source: "plan/specs/bucket-6.json (round-1 canonical spec JSON)"
---

# PAP-181: Add Stripe Connect so tenants can accept payments and receive payouts

**Goal**

Enable tenants to accept payments from their own customers and receive payouts through Stripe Connect: onboarding a connected account per tenant, charging on that account with a platform application fee, handling connected-account webhooks, and posting fees, payouts and balances to the ledger so a tenant's books stay complete.

**Scope**

In:
- Table `connect_account`; oRPC `connect.*`; connected-account webhook route `/api/webhooks/stripe-connect`.
- Onboarding UI in `/org/settings/payments` with status, requirements and payout schedule.
- Charge helper `createConnectedCheckout` used by `business-core/invoicing` and `growth/referral-program` (payouts to affiliates).
- Posting rules `payout.paid`, `application_fee.created`, `charge.dispute.*`, `balance_transaction` reconciliation.

Out: card-present/Terminal, Issuing, marketplace splits across multiple connected accounts per charge, live-mode activation (Justin approves separately).

**Spec**

- Account type: Connect Express by default (`controller: { fees: { payer: 'application' }, losses: { payments: 'application' }, stripe_dashboard: { type: 'express' } }`) so Stripe hosts KYC and the dashboard; `Standard` selectable via tenant setting for tenants who already have Stripe. Country from tenant address; capabilities `card_payments`, `transfers`.
- `connect_account`: `tenant_id unique, stripe_account_id, type, country, default_currency, charges_enabled, payouts_enabled, details_submitted, requirements jsonb (currently_due, eventually_due, disabled_reason), payout_schedule jsonb, updated_from_event_id`.
- Onboarding: `connect.start` creates the account and an Account Link (`type: account_onboarding`, refresh and return URLs); `connect.refreshLink` for expired links; `connect.loginLink` opens the Express dashboard; `account.updated` webhook keeps flags current; UI shows a checklist from `requirements.currently_due` with plain-language mapping.
- Charging: direct charges on the connected account (`stripe.checkout.sessions.create({...}, { stripeAccount })`) with `payment_intent_data.application_fee_amount` computed by `platformFee(tenantPlan, amount)` from `plans.ts` (e.g. 1 percent capped); invoice pay links use this helper; refunds via `refunds.create` with `refund_application_fee: true` policy configurable.
- Webhooks: separate endpoint and secret for connected-account events (`account.updated`, `payout.paid|failed`, `charge.succeeded|refunded`, `charge.dispute.created|closed`, `payment_intent.payment_failed`); same `stripe_event` idempotency table with `account` column; handlers create `fin_transaction` rows (`payment`, `refund`, `fee`, `payout`) with `party_id` resolved from `metadata.party_id` and post via `business-core/ledger` (cash-in-transit vs bank: payments debit `stripe_balance` subtype, payouts move `stripe_balance` to `cash`, fees debit `fees` expense).
- Reconciliation: nightly `balance_transactions.list` per connected account; every Stripe balance transaction must map to a `fin_transaction`; discrepancies reported in `/finance/reconciliation` dataset with a "create from Stripe" action.
- Disputes: create a `fin_transaction` `kind: adjustment` and a notification to finance staff with the evidence deadline; posting to `disputes_reserve` subtype.
- Permissions: `payments.manage` (owner/admin); agents read-only.
- Test mode uses Stripe test connected accounts with `4000000000000077` style test cards for payouts; `stripe listen --forward-connect-to` documented.

**Definition of done**

- Test-mode flow recorded: onboard Express account, charge through an invoice pay link, observe application fee and payout events, ledger entries balanced.
- Vitest for fee calculation, handler idempotency, requirements mapping, reconciliation diff.
- Playwright: settings page states (not started, requirements due, enabled, restricted); screenshots at 375, 1024, 1920 in three themes.
- Reconciliation report shows zero discrepancies on the demo tenant after a seeded day of activity.
- `docs/finance/connect.md` (including live-mode activation checklist for Justin); ADR on Express plus direct charges; CHANGELOG entry; Linear comment with video replay.

**Edge cases**

- Account restricted mid-month (`disabled_reason`): charges blocked, invoices fall back to "pay by bank transfer" instructions, banner to finance staff.
- Payout failed (bank details invalid): transaction stays in `stripe_balance`, alert raised, no cash posting.
- Refund exceeding available connected balance: Stripe pulls from platform; post a receivable from tenant, flagged.
- Tenant switches from Express to Standard: new account, old account retained for history and reconciliation.
- Currency of connected account differs from tenant functional currency: FX captured at payout.
- Webhook for an unknown `stripe_account_id` (deleted tenant): acknowledged and logged, not processed.

**Dependencies**

- `business-core/stripe-billing` (client, event table, plans), `business-core/ledger` (posting), `business-core/finance-data-model` (transactions, parties), `collab/notifications` for dispute alerts.

**Agent**

Builder: Ledger (Payments Integrator). Reviewer: Sentinel (Security Auditor, Code Reviewer); Bookkeeper sub-agent checks postings.

**Size**

M: Stripe-hosted onboarding keeps UI small; webhook and reconciliation correctness is the substance.
