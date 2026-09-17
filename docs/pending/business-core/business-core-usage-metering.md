---
key: "gap/business-core/usage-metering"
title: "Build usage metering and metered billing: usage events (agent sessions, storage, seats, API calls) aggregated per tenant, Stripe usage records, limit warnings"
project: "business-core"
parent: null
phase: "P2"
type: "Build"
priority: 2
size: null
surfaces: []
milestone: "Stripe billing live"
intendedState: "Backlog"
blockedBy: ["PAP-177", "PAP-178", "PAP-43"]
blocks: ["PAP-99"]
source: "round2/agent4/pending-issues.json"
linearDocument: "https://linear.app/paperos/document/round-2-pending-issues-business-core-11-7c8c2526b3c9"
identifier: "PAP-391"
status: "created"
createdAt: "2026-09-17"
---

# Build usage metering and metered billing: usage events (agent sessions, storage, seats, API calls) aggregated per tenant, Stripe usage records, limit warnings

**Goal**

Turn PAP-177's "record hooks only" into real metering: one `recordUsage(kind, quantity)` call that every metered surface emits, per-tenant aggregation, limit warnings that feed PAP-178's `used` values, and Stripe usage records for metered prices, so `agentSessionsPerDay` and `storageGb` stop being unmeasured promises.

**Scope**

In: tables `usage_event` (partitioned monthly) and `usage_daily`; `recordUsage`, `usageFor(tenantId, kind, window)`; kinds v1 `agent.session`, `agent.tokens`, `storage.bytes` (gauge), `seats.active` (gauge), `api.calls`, `automation.runs`, `outreach.messages`; hourly rollup job; Stripe usage record sync for prices flagged `metered` in `plans.ts`; warnings at 80 and 100 percent via notifications; usage page section on `/org/settings/billing`. Out: pricing decisions, per-user chargeback reports, external analytics.

**Spec**

* `usage_event (id uuidv7, tenant_id, kind, quantity numeric, unit, actor_id?, source, idempotency_key unique, occurred_at)`; gauges write the current value, counters increment.
* `recordUsage` is fire-and-forget through the PAP-43 queue with idempotency keys so retries never double count; storage gauge computed nightly from PAP-37 `file` rows; active seats from PAP-58 memberships.
* `usage_daily (tenant_id, kind, day, quantity)` rolled up hourly; `usageFor` reads it plus today's live events.
* PAP-178 `assertWithinLimit` uses `usageFor` for `agentSessionsPerDay` and `storageGb`; PAP-99 reads the same value before spawning sessions.
* Stripe: for plans with `metered: true` prices, a nightly job posts `subscriptionItems.createUsageRecord` with `action: 'set'` per kind and stores `stripe_usage_record_id`; failures alert.
* Warnings emitted once per threshold crossing per billing period via `usage.threshold { kind, pct }` and PAP-136 core.

**Interface contract**

Provides: `recordUsage(kind, quantity, { idempotencyKey, actorId })`, `usageFor`, `UsageKind` registry `defineUsageKind`, dataset `billing.usage`, event `usage.threshold`, usage bars on the billing page. Consumes: plans and subscriptions (PAP-177), entitlements (PAP-178), jobs (PAP-43), files (PAP-37), memberships (PAP-58), notifications (PAP-136 core), orchestrator sessions (PAP-96, PAP-98 emit `agent.session` and `agent.tokens`). Consumed by PAP-99 concurrency, PAP-178, PAP-174 `cost_units`.

**Definition of done**

* Vitest, integration and Playwright below green.
* Usage section screenshots at 375, 1024, 1920 in three themes.
* `docs/finance/usage-metering.md` (kinds, adding a kind, Stripe mapping); CHANGELOG; Linear comment with demo link.

**Test plan**

* Unit: counter versus gauge semantics, idempotency, threshold-once logic, rollup arithmetic.
* Integration: 10k events in one hour roll up correctly; duplicate idempotency keys ignored; Stripe usage record posted in test mode and visible on the subscription item; `assertWithinLimit` blocks the sixth agent session when the limit is five.
* E2E: billing page shows storage and agent-session bars; crossing 80 percent produces one notification.
* Visual: matrix above.

**Demo**

Reviewer runs `pnpm tsx scripts/usage-demo.ts` emitting 50 API calls and a storage gauge, forces a rollup, opens `/org/settings/billing` to see the bars move, then runs the Stripe sync and opens the subscription item in the Stripe test dashboard. Under two minutes.

**Edge cases**

* Clock skew between emitters: `occurred_at` from the server on receipt.
* Plan without metered prices: rollups still run, Stripe sync skipped.
* Tenant downgrade mid-period: usage continues to accrue, limits apply from the new plan after the grace period.
* Partition missing for a future month: created ahead by the nightly job.
* Storage gauge stale after a bulk purge: next nightly run corrects it; page shows "as of".

**Dependencies**

PAP-177 (hard), PAP-178 (hard), PAP-43 (hard), PAP-37, PAP-58, PAP-136 core, PAP-98 (emitter). Blocks PAP-99's session cap check.

**Agent**

Builder: Ledger (Payments Integrator). Reviewer: Sentinel (Code Reviewer, Edge Case Hunter for double counting).

**Size**

M: small tables and one Stripe call; correctness of idempotency and rollups is the work.
