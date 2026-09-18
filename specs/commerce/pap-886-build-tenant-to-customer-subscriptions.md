---
identifier: "PAP-886"
title: "Build tenant-to-customer subscriptions: plans and recurring billing on the connected account, trials, proration, usage add-ons, dunning, portal self-service and MRR datasets, distinct from platform billing"
project: "commerce"
projectName: "Commerce, Operations & Vertical Packs"
phase: "P2"
type: "Build"
priority: 4
surfaces: ["Customer"]
milestone: "Operations packs, marketplace and swap"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-177", "PAP-181", "PAP-394", "PAP-397", "PAP-879"]
blocks: []
key: "r4/commerce/customer-subscriptions"
url: "https://linear.app/paperos/issue/PAP-886/build-tenant-to-customer-subscriptions-plans-and-recurring-billing-on"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:30:01.350Z"
model: "claude-opus-5"
effort: "high"
estimate: 3
dueDate: null
cycle: null
---

# PAP-886: Build tenant-to-customer subscriptions: plans and recurring billing on the connected account, trials, proration, usage add-ons, dunning, portal self-service and MRR datasets, distinct from platform billing

**Model / Effort:** Opus 5 (`claude-opus-5`) / high — Build M

**Goal**

Let a tenant sell subscriptions to its own customers (SaaS packs, box subscriptions, service plans, maintenance contracts): plans built from catalog prices on the tenant's connected account, trials and proration, usage add-ons, dunning and retries through PAP-397 reminders, a portal self-service page, and MRR, churn and cohort datasets, kept strictly separate from PAP-177, which bills the tenant for PaperOS.

**Scope**

In: `SubscriptionsPort`: `plans` (catalog variants with recurring prices synced to the connected account), `subscribe` (Checkout in subscription mode PAP-396 pattern on Connect, trial days, coupon), `change` (upgrade, downgrade with proration policy), `cancel` (immediate or period end, reasons), `usage` (metered add-ons via Stripe usage records, reusing the PAP-391 aggregation pattern but for the tenant's customers); webhook mapping to `customer_subscription` status. Portal `/portal/subscriptions` (plan, next invoice, change, cancel, payment method via the Stripe customer portal on the connected account); console `/commerce/subscriptions` (grid, detail with timeline, manual adjustments with approval). Dunning: failed payment → PAP-397 reminder templates and retry schedule; posting rules `subscription.invoice.paid|refunded` (PAP-394) with deferred revenue recognition option (monthly release job). Datasets and dashboard blocks: MRR, new/expansion/contraction/churn, cohort retention, trial conversion; `subscription.customer.*` events for workflows and segments.

Out: Platform billing (PAP-177). Marketplace subscriptions (v0.3). Revenue recognition beyond straight-line deferral.

**Spec**

* Two Stripe contexts never mix: platform-account calls for PAP-177, connected-account calls here; a lint (Semgrep, PAP-359 style) blocks `stripe.` calls in this package without the `stripeAccount` header
* Status is derived from webhooks; the portal shows pending changes until confirmed; proration previews come from Stripe before the change is applied
* Cancellation reasons feed a dataset; win-back workflows trigger on `subscription.customer.cancelled`
* Deferred revenue: invoice paid → deferred liability; monthly job releases straight-line; toggle per tenant with an ADR on when it is required

**Interface contract**

Provides: `SubscriptionsPort` default adapter, tables and datasets, portal and console pages, dunning integration, posting rules, MRR blocks, `subscription.customer.*` events. Consumes: catalog prices, Stripe client (PAP-177) with Connect (PAP-181), reminders and dunning (PAP-397), posting rules (PAP-394), Checkout (PAP-396), metering pattern (PAP-391), approvals (soft). Consumed by: packs (SaaS, box subscriptions, maintenance plans), growth (MRR and churn as segment attributes), assistant (portal subscription questions), engagement memberships (shares the Connect subscription plumbing).

**Definition of done**

* SaaS pack demo: customer subscribes with a trial in test mode, upgrades with proration preview, a failed payment fixture triggers dunning, cancels at period end; MRR block and cohort view render; lint proves no platform-context calls
* Every new page has a `page.spec.yaml` (PAP-114) that passes the validator, declared loading, empty, error and denied states, and Gate 3 screenshots at 375, 768, 1024 and 1920 in light and dark themes.
* Linear comment on the issue with the evidence links (PR, gate artefacts, recording or report) and the module docs page updated where the interface changed.

**Test plan**

* Unit: status mapping from webhook fixtures; MRR math; deferred release schedule.
* Integration: Checkout subscription → webhook → active; change with proration; dunning retries; posting traces.
* Isolation: the PAP-34 cross-tenant harness auto-enrols every new table; one negative case per new oRPC procedure proves `NOT_FOUND` on a foreign tenant row.

**Demo**

Subscribe to the demo SaaS pack's Pro plan with a 14-day trial, upgrade to Team and show the proration preview, simulate a card failure and the dunning email, then open the MRR dashboard.

**Edge cases**

* Connected account not fully onboarded (PAP-181 requirements due): subscriptions cannot be sold; the console shows the Stripe requirements with a link
* Customer disputes a subscription charge: webhook marks the invoice disputed; posting rule holds funds in a dispute account until resolution
* Module disabled for the tenant (PAP-266): routes return `MODULE_DISABLED` (409), slot fills unmount and the manifest declares the dependency so consumers fail closed rather than half-render.

**Dependencies**

PAP-879 (hard), PAP-177, PAP-181 (hard), PAP-397, PAP-394, PAP-396 (hard), PAP-391 (soft: pattern).

**Agent**

Builder: Ledger. Reviewer: Sentinel (Security Auditor).

**Size**

M: one session.

*Round 4 critique fix (2026-09-18):* resolved 1 round-4 file key in this description to Linear identifiers: `r4/commerce/catalog-inventory` = PAP-879.
