---
identifier: "PAP-177"
title: "Integrate Stripe Billing: products, prices, subscriptions, customer portal and webhooks"
project: "business-core"
projectName: "Business Core: Payments, Finance & Payroll"
phase: "P1"
type: "Build"
priority: 1
surfaces: ["Customer"]
milestone: "Stripe billing live"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-175", "PAP-58"]
blocks: ["PAP-178", "PAP-180", "PAP-181", "PAP-182", "PAP-196"]
key: "business-core/stripe-billing"
url: "https://linear.app/paperos/issue/PAP-177/integrate-stripe-billing-products-prices-subscriptions-customer-portal"
source: "plan/specs/bucket-6.json (round-1 canonical spec JSON)"
---

# PAP-177: Integrate Stripe Billing: products, prices, subscriptions, customer portal and webhooks

**Goal**

Let PaperOS charge tenants for plans: define plans in code, sync them to Stripe Products and Prices, run Checkout for upgrades, expose the Stripe Customer Portal for self-service, and ingest webhooks idempotently into a local `subscription` model that `business-core/entitlements` reads. This is platform billing (PaperOS to tenant); tenant-to-customer payments arrive with Connect.

**Scope**

In:
- `packages/finance/src/billing/`: `plans.ts`, `stripe.ts` client, `sync-catalog.ts`, oRPC `billing.*`, webhook route `/api/webhooks/stripe`, tables `billing_customer`, `subscription`, `stripe_event`.
- Pages `/org/settings/billing` (staff console) and the billing entry in `identity/customer-portal-shell`.
- Stripe test mode end to end with the Stripe CLI for local webhooks; Vitest against `stripe-mock` is optional, real test mode is required.

Out: usage-based metering (record hooks only), tax (`business-core/tax-compliance`), invoices to tenant customers (`business-core/invoicing`), dunning email copy beyond Stripe defaults.

**Spec**

- Library `stripe` Node SDK 17.x pinned with `apiVersion` fixed in one constant; keys from `app-shell/env-config` (`STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`, `STRIPE_PUBLISHABLE_KEY`), test keys only until Justin approves live.
- Plans declared in `plans.ts`: `{ key: 'free'|'pro'|'business'|'enterprise', name, prices: { monthly, yearly } in minor units, trialDays, entitlements: Record<EntitlementKey, boolean | number> }`; `pnpm billing:sync` upserts Products (metadata `paperos_plan_key`) and Prices (lookup keys `pro_monthly`), never deletes, archives removed prices; idempotent.
- `billing_customer`: `tenant_id unique, stripe_customer_id, email, default_payment_method?`; created lazily on first checkout with `metadata.tenant_id`.
- `subscription`: `id, tenant_id, stripe_subscription_id, plan_key, price_lookup_key, status (Stripe statuses), current_period_start/end, cancel_at_period_end, trial_end, seats, latest_invoice_id, updated_from_event_id`.
- `billing.createCheckoutSession({ planKey, interval, seats })` returns a Checkout URL with `client_reference_id = tenantId`, `success_url` to `/org/settings/billing?session_id=`, `allow_promotion_codes`; `billing.createPortalSession()` returns the Customer Portal URL configured (via `billing:sync`) to allow plan switches among our prices, payment method updates, cancellation at period end.
- Webhooks: verify signature with `stripe.webhooks.constructEvent`; insert into `stripe_event (id pk, type, payload, received_at, processed_at, error)` first (duplicate id returns 200 immediately); process handlers for `checkout.session.completed`, `customer.subscription.created|updated|deleted`, `invoice.paid|payment_failed`, `customer.updated`; each handler is a pure function of `(event, db)` and updates `subscription` only if `event.created` is newer than `updated_from_event_id`'s timestamp; failures return 500 so Stripe retries, with an alert after 3 failures.
- Every processed billing event also creates a `fin_transaction` (`kind: payment|refund`, source `stripe`) so the ledger can post platform revenue later.
- Billing page: current plan card, seats, renewal date, payment method (brand and last4 from Stripe, never stored), invoice history list (from Stripe API, paginated), buttons Upgrade/Manage/Cancel; states for `past_due` (banner) and `trialing` (days left).
- Permissions: `billing.manage` for owner and admin only; agents cannot call billing procedures (`identity/agent-principals`).
- Reconciliation job nightly: list active subscriptions from Stripe and diff against `subscription`; discrepancies logged and fixed from Stripe as source of truth.

**Definition of done**

- Test-mode flow recorded: checkout with `4242` card, plan appears in the billing page within 5 s of the webhook, portal downgrade updates `subscription`.
- Vitest for handlers with fixture events, idempotency (duplicate delivery), out-of-order events, signature failure.
- Stripe CLI `stripe trigger` scripts in `packages/finance/scripts/` documented for local development.
- Playwright e2e of the billing page states (trialing, active, past_due) using seeded rows; screenshots at 375, 1024, 1920 in three themes.
- `docs/finance/billing.md` including webhook runbook; ADR noting Stripe as processor; CHANGELOG entry; Linear comment with a video replay of the checkout flow.

**Edge cases**

- Webhook arrives before the DB knows the checkout session: handler creates `billing_customer` from `metadata.tenant_id`.
- Tenant deleted (grace period) with an active subscription: cancel at period end automatically, audited.
- Card declines at renewal: `past_due` banner with portal link; entitlements downgrade only after Stripe marks `unpaid` or `canceled`.
- Plan removed from `plans.ts` while tenants still subscribe: price archived, existing subscriptions keep working, upgrade path shown.
- Clock skew between Stripe and server: use `event.created`, not receipt time.
- Two admins click Upgrade concurrently: two Checkout sessions, Stripe allows one subscription per customer per our metadata guard; second completion is detected and refunded automatically with a notice.

**Dependencies**

- `identity/org-tenancy` (tenant, active org), `business-core/finance-data-model` (`fin_transaction`), `app-shell/env-config`, `identity/customer-portal-shell` for the customer entry point.

**Agent**

Builder: Ledger (Payments Integrator). Reviewer: Sentinel (Security Auditor for webhooks and secrets, Code Reviewer).

**Size**

M: Stripe does the heavy lifting; correctness of webhook ordering and idempotency is the work.
