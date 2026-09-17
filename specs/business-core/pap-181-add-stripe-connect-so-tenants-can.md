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
blockedBy: ["PAP-175", "PAP-177", "PAP-179", "PAP-359", "PAP-394"]
blocks: ["PAP-196", "PAP-408"]
key: "business-core/stripe-connect"
url: "https://linear.app/paperos/issue/PAP-181/add-stripe-connect-so-tenants-can-accept-payments-and-receive-payouts"
source: "Linear snapshot 2026-09-17T13:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T13:05:45.105Z"
---

# PAP-181: Add Stripe Connect so tenants can accept payments and receive payouts

**Goal**

Let tenants accept payments from their own customers and receive payouts through Stripe Connect: one connected account per tenant, direct charges with a platform application fee, connected-account webhooks, and ledger postings for fees, payouts and balances so a tenant's books stay complete.

**Scope**

In: table `connect_account`; procedures `connect.*`; webhook route `/api/webhooks/stripe-connect`; `/org/settings/payments` onboarding UI; `createConnectedCheckout` helper used by PAP-180 and PAP-196; posting rules `payout.paid`, `application_fee.created`, `charge.dispute.*`; nightly balance-transaction reconciliation and the `/finance/reconciliation` dataset.

Out: Terminal, Issuing, multi-account splits per charge, live-mode activation (Justin approves separately).

**Spec**

* Express by default (`controller: { fees: { payer: 'application' }, losses: { payments: 'application' }, stripe_dashboard: { type: 'express' } }`); Standard selectable per tenant; capabilities `card_payments`, `transfers`; country from the tenant address.
* `connect_account (tenant_id unique, stripe_account_id, type, country, default_currency, charges_enabled, payouts_enabled, details_submitted, requirements jsonb, payout_schedule jsonb, updated_from_event_id)`.
* `connect.start` creates the account and an Account Link; `connect.refreshLink`, `connect.loginLink`; `account.updated` keeps flags current; UI maps `requirements.currently_due` to plain language.
* Direct charges: `stripe.checkout.sessions.create({...}, { stripeAccount })` with `application_fee_amount = platformFee(plan, amount)` from `plans.platformFeeBps` (PAP-177); refunds with a configurable `refund_application_fee` policy.
* Connected webhooks share `stripe_event` with an `account` column; handlers create `fin_transaction` rows (`payment|refund|fee|payout|adjustment`) and post: payments debit `stripe_balance`, payouts move `stripe_balance` to `cash`, fees debit `fees`, disputes to `disputes_reserve`.
* Reconciliation: nightly `balance_transactions.list` per account; every Stripe balance transaction maps to a `fin_transaction` or appears in the discrepancy dataset with "create from Stripe".
* `payments.manage` for owner and admin; agents read-only.

**Interface contract**

Provides: `connect.start|refreshLink|loginLink|status`, `createConnectedCheckout({ tenantId, amountMinor, currency, metadata, successUrl, cancelUrl })`, `createTransfer({ tenantId, destinationAccountId, amountMinor })` for PAP-196, `connectedAccountFor(tenantId)`, events `connect.account.updated`, `connect.payout.paid`, `connect.dispute.opened`, dataset `finance.reconciliation`. Consumes: Stripe client, `stripe_event`, plans (PAP-177), posting (PAP-179), transactions and parties (PAP-175), notifications for disputes and restrictions (PAP-136 core). Consumed by PAP-180, PAP-182 (per-account tax settings), PAP-186 MRR, PAP-196.

**Definition of done**

* Test-mode flow recorded: onboard an Express account, pay an invoice link, observe fee and payout events, balanced ledger entries.
* Vitest, integration and Playwright below green; reconciliation shows zero discrepancies on the demo tenant after a seeded day.
* `docs/finance/connect.md` with the live activation checklist for Justin; ADR on Express plus direct charges; CHANGELOG; Linear comment with replay.

**Test plan**

* Unit: `platformFee` per plan and cap; handler idempotency and ordering; requirements mapping; reconciliation diff on fixtures.
* Integration: `stripe trigger` for `account.updated`, `payout.paid`, `charge.dispute.created` against a test connected account; each yields the expected `fin_transaction` and posting; unknown `stripe_account_id` acknowledged and logged.
* E2E: settings page in not-started, requirements-due, enabled and restricted states from seeded rows.
* Visual: 375, 1024, 1920 in three themes for the four states.

**Demo**

Reviewer clicks "Accept payments" on the demo tenant, completes Stripe's test onboarding, returns to see `charges_enabled`, pays a seeded invoice with `4242`, then opens `/finance/journal` to see the payment, fee and (after `stripe trigger payout.paid`) payout entries. Under two minutes.

**Edge cases**

* Account restricted mid-month: charges blocked, invoices show bank-transfer instructions, banner to finance.
* Payout failed: amount stays in `stripe_balance`, alert, no cash posting.
* Refund exceeding connected balance: receivable from tenant posted and flagged.
* Express to Standard switch: new account, old one kept for history.
* Connected currency differs from functional: FX captured at payout.

**Dependencies**

PAP-177 (hard), PAP-179 (hard), PAP-175 (hard), PAP-136 core (soft). Blocks PAP-196; optional for PAP-180, PAP-182, PAP-186.

**Agent**

Builder: Ledger (Payments Integrator). Reviewer: Sentinel (Security Auditor, Code Reviewer); Bookkeeper checks postings.

**Size**

M: Stripe hosts onboarding; webhook and reconciliation correctness is the substance.
