---
identifier: "PAP-844"
title: "Add assistant metering and limits: usage kinds, per-tenant daily limits and entitlements, cost dashboard section and BYO-key accounting"
project: "assistant"
projectName: "Tenant AI Assistant & Business Agents"
phase: "P2"
type: "Build"
priority: 4
surfaces: ["Staff"]
milestone: "Business characters, evals and swap"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-98", "PAP-178", "PAP-391", "PAP-836"]
blocks: []
key: "r4/assistant/metering-limits"
url: "https://linear.app/paperos/issue/PAP-844/add-assistant-metering-and-limits-usage-kinds-per-tenant-daily-limits"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:53.444Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 2
dueDate: null
cycle: null
---

# PAP-844: Add assistant metering and limits: usage kinds, per-tenant daily limits and entitlements, cost dashboard section and BYO-key accounting

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Build S

**Goal**

Make the assistant affordable and predictable: every message and token is a usage event, plans carry `assistantMessagesPerDay` and `assistantTokensPerMonth` entitlements, tenants see spend and remaining allowance on the billing page, BYO-key tenants are metered for limits but not billed for tokens, and the platform's own credit report (PAP-98) separates assistant spend from builder spend.

**Scope**

In: Register kinds with PAP-391: `assistant.messages`, `assistant.tokens.in`, `assistant.tokens.out`, `assistant.actions`; `recordUsage` calls in the runtime with `billable: !byoKey`; hourly rollups feed PAP-178 `used`. Entitlement keys in `plans.ts` (PAP-178): `assistant`, `assistantPortal`, `assistantMessagesPerDay`, `assistantTokensPerMonth`; `<EntitlementGate/>` on the panel and widget with the upgrade prompt; hard stop at 100 percent with a friendly message and escalation-only mode for the portal. Billing page section `/org/settings/billing#assistant`: messages today, tokens this month, cost estimate (platform key) or provider cost estimate (BYO), per-character breakdown, export CSV. PAP-98 burn report gains an `assistant` line per tenant; Stripe metered price sync for `assistant.tokens.out` when a plan flags it metered.

Out: Pricing decisions (Needs Justin item filed with a proposed table). Per-user chargeback.

**Spec**

* Limits are evaluated before the model call from the hourly rollup plus an in-memory counter for the current hour; a tenant cannot exceed the daily cap by more than one hour's burst
* Warnings at 80 and 100 percent go through the notification kinds registry (PAP-136) to org admins
* Token accounting uses provider-reported counts when available and `countTokens` estimates otherwise, flagged `estimated`
* BYO key tenants see provider cost estimates from a public price table in `packages/assistant/prices.yaml` reviewed monthly by Scout (PAP-218 routine)

**Interface contract**

Provides: usage kinds, entitlement keys, billing page section, burn report line, `prices.yaml`. Consumes: usage metering (PAP-391), entitlements (PAP-178), credit spend report (PAP-98), notification kinds (PAP-136), the conversation runtime. Consumed by: platform-ops tenant health, business-core billing page, agents budgets (PAP-111 kill switch reads the same counters).

**Definition of done**

* Demo tenant hits a 50-message test cap and the panel shows the limit and upgrade prompt; billing section renders with real rollups; burn report separates assistant spend
* Metered Stripe price sync verified in test mode for one plan
* Every new page has a `page.spec.yaml` (PAP-114) that passes the validator, declared loading, empty, error and denied states, and Gate 3 screenshots at 375, 768, 1024 and 1920 in light and dark themes.
* Linear comment on the issue with the evidence links (PR, gate artefacts, recording or report) and the module docs page updated where the interface changed.

**Test plan**

* Unit: limit evaluation at hour boundaries; `estimated` flag path; BYO not billed but counted.
* Integration: rollup → entitlement `used` → gate; notification at 80 percent once per day.
* Isolation: the PAP-34 cross-tenant harness auto-enrols every new table; one negative case per new oRPC procedure proves `NOT_FOUND` on a foreign tenant row.

**Demo**

Set the demo plan to 20 messages a day, send 21, watch the gate and the admin notification, then open the billing page section and export the CSV.

**Edge cases**

* Clock skew between worker and API: limits use database time; the in-memory counter resets on the database hour
* Plan downgrade mid-month below current usage: assistant enters read-only history mode until the next period; no retroactive charge
* Module disabled for the tenant (PAP-266): routes return `MODULE_DISABLED` (409), slot fills unmount and the manifest declares the dependency so consumers fail closed rather than half-render.

**Dependencies**

PAP-836 (hard), PAP-391 and PAP-178 (hard), PAP-98 and PAP-136 (soft).

**Agent**

Builder: Ledger. Reviewer: Sentinel (Code Reviewer).

**Size**

S: half a session.

*Round 4 critique fix (2026-09-18):* resolved 1 round-4 file key in this description to Linear identifiers: `r4/assistant/conversation-runtime` = PAP-836.
