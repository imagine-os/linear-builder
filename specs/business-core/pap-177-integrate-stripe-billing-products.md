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
blockedBy: ["PAP-58", "PAP-175", "PAP-303", "PAP-556", "PAP-578", "PAP-579"]
blocks: ["PAP-178", "PAP-180", "PAP-181", "PAP-182", "PAP-196", "PAP-359", "PAP-391", "PAP-396", "PAP-407", "PAP-490", "PAP-765", "PAP-778", "PAP-871", "PAP-878", "PAP-879", "PAP-886"]
key: "business-core/stripe-billing"
url: "https://linear.app/paperos/issue/PAP-177/integrate-stripe-billing-products-prices-subscriptions-customer-portal"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T13:56:23.551Z"
model: "claude-sonnet-5"
effort: "high"
estimate: 3
dueDate: "2026-09-27"
cycle: null
---

# PAP-177: Integrate Stripe Billing: products, prices, subscriptions, customer portal and webhooks

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / high — Build M

**Goal**

Charge tenants for plans: declare plans in code, sync them to Stripe Products and Prices, run Checkout for upgrades, expose the Customer Portal, and ingest webhooks idempotently into a local `subscription` model that PAP-178 reads. Platform billing only; tenant-to-customer payments arrive with PAP-181.

**Scope**

In: `packages/finance/src/billing/` (`plans.ts`, `stripe.ts`, `sync-catalog.ts`, procedures `billing.*`, webhook route `/api/webhooks/stripe`, tables `billing_customer`, `subscription`, `stripe_event`); `/org/settings/billing` page and the portal billing entry (PAP-64); Stripe CLI scripts for local webhooks; nightly reconciliation job.

Out: usage metering (PAP-391), tax (PAP-182), tenant invoices (PAP-180), dunning copy beyond Stripe defaults.

**Spec**

* `stripe` SDK 17.x, one pinned `apiVersion`; keys `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`, `STRIPE_PUBLISHABLE_KEY` from PAP-17; test keys until Justin approves live.
* `plans.ts`: `{ key: 'free'|'pro'|'business'|'enterprise', name, prices: { monthly, yearly } minor units, trialDays, entitlements: Record<EntitlementKey, boolean | number>, platformFeeBps }`; `pnpm billing:sync` upserts Products (`metadata.paperos_plan_key`) and Prices (lookup keys like `pro_monthly`), archives removed prices, never deletes.
* `billing_customer (tenant_id unique, stripe_customer_id, email, default_payment_method?)` created lazily with `metadata.tenant_id`.
* `subscription (id, tenant_id, stripe_subscription_id, plan_key, price_lookup_key, status, current_period_start|end, cancel_at_period_end, trial_end, seats, latest_invoice_id, updated_from_event_id)`.
* `billing.createCheckoutSession({ planKey, interval, seats })` and `billing.createPortalSession()`; portal configured by `billing:sync` for plan switches, payment methods, cancel at period end.
* Webhooks: `constructEvent`, insert `stripe_event (id pk, type, payload, received_at, processed_at, error)` first (duplicate returns 200), handlers for `checkout.session.completed`, `customer.subscription.*`, `invoice.paid|payment_failed`, `customer.updated`; apply only when `event.created` is newer than the stored one; 500 on failure so Stripe retries; alert after three failures.
* Each billing event creates a `fin_transaction` (`payment|refund`, source `stripe`) for later posting.
* `billing.manage` for owner and admin; agents denied (PAP-60).

**Interface contract**

Provides: `plans`, `Plan`, `getPlan(tenantId)`, `subscription` row shape, event `billing.subscription.changed { tenantId, planKey, status }` on the outbox, `stripe_event` table reused by PAP-181 (with `account` column), `stripeClient()`, procedures `billing.*`, Stripe CLI scripts. Consumes: tenant and active org (PAP-58), `fin_transaction` (PAP-175), env (PAP-17), portal shell (PAP-64), notifications for failures (PAP-136 core). Consumed by PAP-178, PAP-180, PAP-181, PAP-182, PAP-196, PAP-194 revenue join, PAP-391.

* Contract source: [Interface & Data Contracts](<https://linear.app/paperos/document/paperos-interface-and-data-contracts-d40e6a4d227c>) §3 (`stripe_event` is an inbox whose rows are normalised into the §3 envelope with `actor.type='service'`; the catalogue topics are `subscription.updated` and `payment.succeeded|failed|refunded`, so register `billing.subscription.changed` under `subscription.updated` or declare the alias in `defineTopic`); §4 (idempotency keys and rate limits are owned by pending contracts issue C; interim: idempotent on `stripe_event.id`); §6 rows "Finance model and ledger posting" and "Idempotency keys, rate limits, batch". Also [Security & Threat Model](<https://linear.app/paperos/document/paperos-security-and-threat-model-51fd5fd8929c>) §8 (PCI SAQ-A: card data only in Checkout, Elements and the Customer Portal; restricted test keys; live mode is a hard-block Needs Justin decision).

**Definition of done**

* Test-mode flow recorded: `4242` checkout, plan visible on the billing page within 5 s of the webhook, portal downgrade updates `subscription`.
* Vitest, integration and Playwright below green.
* `docs/finance/billing.md` with webhook runbook; ADR naming Stripe as processor; CHANGELOG; Linear comment with checkout replay.

**Test plan**

* Unit: each handler with fixture events; duplicate delivery; out-of-order `event.created`; bad signature; plan sync diff is idempotent.
* Integration: `stripe trigger checkout.session.completed` against the dev server produces `subscription` and `fin_transaction`; reconciliation job repairs a deliberately mutated row from Stripe.
* E2E: billing page states `trialing`, `active`, `past_due` from seeded rows; upgrade button opens Checkout URL.
* Visual: 375, 1024, 1920 in three themes for the three states.

**Demo**

Reviewer runs `stripe listen` and `pnpm dev`, upgrades the demo tenant with card `4242`, returns to `/org/settings/billing` showing Pro within seconds, then opens the portal and cancels at period end, seeing the banner update. Under two minutes.

**Edge cases**

* Webhook before the session is known: handler creates `billing_customer` from metadata.
* Tenant in deletion grace with an active subscription: cancel at period end, audited.
* Renewal decline: `past_due` banner; entitlements downgrade only at `unpaid` or `canceled`.
* Plan removed from `plans.ts`: price archived, subscribers keep working.
* Two admins upgrade concurrently: second completion detected and refunded with a notice.

*Round 4 amendment (2026-09-18):*
Round 4: the concurrent-upgrade refund is executed by the webhook worker with the restricted key that has refund scope, never by an agent session (deny list, PAP-298) and never in live mode without the PAP-359 custody card; the integration test uses a Stripe test clock and `stripe trigger` only.

**Dependencies**

PAP-175 (hard), PAP-58 (hard), PAP-17, PAP-64, PAP-136 (soft). Blocks PAP-178, PAP-180, PAP-181, PAP-182, PAP-196.

**Agent**

Builder: Ledger (Payments Integrator). Reviewer: Sentinel (Security Auditor for webhooks and secrets, Code Reviewer).

**Size**

M: Stripe does the heavy lifting; ordering and idempotency are the work.

**Pending issues**

Bracketed references above are fully specified work packages that Linear refused to create on 2026-09-17 (`USAGE_LIMIT_EXCEEDED`, free-plan issue cap). Their specs live in the project document(s) [business-core](<https://linear.app/paperos/document/round-2-pending-issues-business-core-11-7c8c2526b3c9>) and they are created as issues by `round2/agent4/create_issues.py` once the workspace plan is upgraded.
