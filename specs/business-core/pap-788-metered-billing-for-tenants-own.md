---
identifier: "PAP-788"
title: "Metered billing for tenants' own customers: usage meters on items, usage ingestion API, monthly usage invoicing through recurring schedules and Stripe Billing Meters on the connected account"
project: "business-core"
projectName: "Business Core: Payments, Finance & Payroll"
phase: "P2"
type: "Build"
priority: 4
surfaces: ["Customer"]
milestone: "Payroll adapter and cash dashboard"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-181", "PAP-765", "PAP-774"]
blocks: []
key: "r4/business-core/tenant-metered-billing"
url: "https://linear.app/paperos/issue/PAP-788/metered-billing-for-tenants-own-customers-usage-meters-on-items-usage"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:43.346Z"
model: "claude-sonnet-5"
effort: "high"
estimate: 3
dueDate: null
cycle: null
---

# PAP-788: Metered billing for tenants' own customers: usage meters on items, usage ingestion API, monthly usage invoicing through recurring schedules and Stripe Billing Meters on the connected account

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / high — Build M

**Goal**

Deferred to v0.2 by the Execution Schedule (NJ-14 stop-loss 09-27 can reinstate). Not claimable before 10-01.

PAP-391 meters PaperOS's own tenants. A SaaS built on PaperOS (the SaaS pack) needs the same thing for its customers: record usage against a metered item, roll it up per billing period and invoice it, optionally through Stripe Billing Meters on the connected account.

**Scope**

In: `fin_item.sell.metered: { unit, aggregation: sum|max|last, tiers? }`; `usage.record(partyId, itemId, quantity, { idempotencyKey, occurredAt })` via oRPC and the public API (PAP-222 keys, `X-PaperOS-Env: test` honoured), stored in `fin_usage_event` partitioned monthly; hourly rollup `fin_usage_period`; recurring schedule step `usage` that adds a usage line at generation with tiered pricing (`Money.allocate` for graduated tiers); optional Stripe path: `billing.meterEvents.create` on the connected account for imported subscriptions (PAP-423) with `stripe_meter_id` on the item; customer portal usage page; dataset `finance.customerUsage`.

Out: platform metering (PAP-391), real-time entitlements for tenant customers, rating engines beyond tiers.

**Spec**

* Ingestion is idempotent on `idempotencyKey` and fire-and-forget through PAP-43; rollups are recomputable from events.
* Tier pricing: volume or graduated per item; totals to the cent with the remainder on the last tier.
* Usage lines snapshot the quantity and tier table at invoice generation; late events after generation go to the next period with a note.

**Interface contract**

Provides: `usage.record|forParty`, tables, recurring `usage` step, Stripe meter sync, portal route `_portal/usage`, dataset. Consumes: recurring generation (PAP-765), items (PAP-774), Connect (PAP-181), API keys (PAP-222, soft), jobs (PAP-43), portal (PAP-64).

**Definition of done**

* 10k events roll up correctly and generate one usage line with tiered pricing (fixture); duplicate keys ignored; Stripe meter events verified with recorded fixtures in test mode.
* Portal screenshots at 375, 1024; `docs/finance/metered-billing.md`; CHANGELOG.

**Test plan**

* Unit: aggregation modes, graduated versus volume tiers, idempotency, late-event routing.
* E2E: record usage through the API, force a rollup, generate the monthly invoice and read the usage line in the portal.

**Demo**

Reviewer posts 1,500 API-call events for a demo customer, advances the schedule and sees an invoice with two tier lines. Under two minutes.

**Edge cases**

* Meter unit changed mid-period: refused until period end.
* Negative quantity (correction): allowed with reason, floors at zero for the period.
* Customer without a schedule: usage accrues and shows 'unbilled' in the dataset.

**Dependencies**

Hard: PAP-765, PAP-774, PAP-181. Soft: PAP-222, PAP-43, PAP-64, PAP-423.

**Agent**

Builder: Ledger (Payments Integrator). Reviewer: Sentinel (Edge Case Hunter for double counting).

**Size**

M: one session.

*Round 4 critique fix (2026-09-18):* resolved 2 round-4 file keys in this description to Linear identifiers: `r4/business-core/item-catalogue` = PAP-774, `r4/business-core/recurring-invoices-dunning` = PAP-765.
