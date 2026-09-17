---
identifier: "PAP-178"
title: "Map plans to feature entitlements enforced by the permission engine"
project: "business-core"
projectName: "Business Core: Payments, Finance & Payroll"
phase: "P2"
type: "Build"
priority: 1
surfaces: ["Customer", "Developer"]
milestone: "Stripe billing live"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-59", "PAP-177", "PAP-229", "PAP-484"]
blocks: ["PAP-391"]
key: "business-core/entitlements"
url: "https://linear.app/paperos/issue/PAP-178/map-plans-to-feature-entitlements-enforced-by-the-permission-engine"
source: "Linear snapshot 2026-09-17T15:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T15:00:32.576Z"
model: "claude-sonnet-5"
effort: "high"
---

# PAP-178: Map plans to feature entitlements enforced by the permission engine

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / high — Build M

**Goal**

Make paid features gate themselves: map each plan to typed entitlements (booleans and limits), expose them through the permission engine so specs can declare `requires: [entitlement.sso]`, enforce limits inside the creating transaction, and show one consistent upgrade prompt instead of silent failures.

**Scope**

In: `packages/finance/src/entitlements/` (registry, resolver, oRPC middleware, hooks, `<EntitlementGate />`, `<UpgradePrompt />`); keys v1 `seats, publicViews, dashboards, storageGb, apiRateLimit, whiteLabel, sso, payroll, connectPayments, auditRetentionDays, agentSessionsPerDay`; hook points in PAP-58 `beforeInvite`, PAP-172, PAP-173, PAP-37, PAP-65, PAP-99; usage bars on the billing page.

Out: proration (Stripe), enterprise override UI beyond a JSON field, metering of usage (PAP-391 supplies `used` for `storageGb` and `agentSessionsPerDay`).

**Spec**

* `defineEntitlement({ key, type: 'boolean'|'limit', label, description, unit?, upgradeCopy })`; values from `plans.ts`; `tenant.entitlement_overrides jsonb` (platform admins) merge last; free plan is the floor.
* `resolveEntitlements(tenantId)` cached per request, invalidated on `billing.subscription.changed` and override writes; `entitlements.mine` procedure; pushed in the session payload at login and tenant switch.
* Resolver injects `actor.attributes.entitlements` so PAP-227 conditions work; PAP-116 access sections accept `requires: [entitlement.<key>]`.
* `assertWithinLimit(tenantId, key, currentCountFn, increment = 1)` inside the creating transaction with an advisory lock per tenant and key; error `ORPCError('FORBIDDEN', { code: 'ENTITLEMENT_LIMIT', key, limit, current })`.
* `useEntitlement(key) => { allowed, limit, used, remaining, plan, upgradeUrl }`; `<EntitlementGate key fallback="prompt"|"hide"|"disable">`; prompt shows the smallest plan including the feature and links Checkout for admins.
* Downgrade: nothing deleted; over-limit resources read-only with a banner; 14-day grace configurable.
* Applies to agent principals; `agentSessionsPerDay` read by PAP-99.

**Interface contract**

Provides: `Entitlements` type, `EntitlementKey`, `resolveEntitlements`, `assertWithinLimit`, `useEntitlement`, `EntitlementGate`, `UpgradePrompt`, procedure `entitlements.mine`, error code `ENTITLEMENT_LIMIT`, `requires: [entitlement.*]` spec shorthand, `docs/finance/entitlements.md` generated matrix. Consumes: `plans` and `billing.subscription.changed` (PAP-177), attribute conditions (PAP-227), spec access adapter (PAP-229, PAP-116), `beforeInvite` (PAP-58), session payload (PAP-223). Consumed by PAP-172, PAP-173, PAP-37, PAP-65, PAP-99, PAP-169, PAP-195 plan clauses.

**Definition of done**

* Vitest, permission-matrix, Playwright and Storybook below green.
* `docs/finance/entitlements.md` generated from the registry with the plan matrix.
* CHANGELOG; Linear comment with demo link and matrix.

**Test plan**

* Unit: precedence free < plan < override; `limit 0` versus boolean false; `useEntitlement` derived values.
* Integration: 20 parallel creates against limit 5 yield exactly 5 successes; downgrade makes the sixth public view return the read-only page; resolver cache invalidates on the outbox event; PAP-63 matrix includes an entitlement-gated page for each audience.
* E2E: free tenant hits the public-view limit, sees the prompt, seeded upgrade flips access without reload.
* Visual: gate and prompt at 375, 1024, 1920 in three themes.

**Demo**

Reviewer, on the free demo tenant, creates public views until the fourth attempt shows the upgrade prompt naming Pro, runs `pnpm tsx scripts/set-plan.ts demo pro`, and creates the view without reloading. Under two minutes.

**Edge cases**

* Webhook delayed after checkout: client polls `entitlements.mine` for 30 s with "activating".
* Override grants a feature the plan lacks: allowed, labelled "included by agreement".
* Trial ends over the free limit: read-only rules, no deletion.
* Spec references an unknown key: PAP-117 validator fails the PR.
* Platform admin viewing a tenant: the tenant's entitlements apply, never their own.

**Dependencies**

PAP-177 (hard), PAP-59 children (hard), PAP-116, PAP-58, PAP-223 (session payload). Blocks (soft) PAP-172, PAP-173, PAP-65, PAP-99.

**Agent**

Builder: Ledger (Payments Integrator). Reviewer: Sentinel (Security Auditor on bypass attempts, Code Reviewer).

**Size**

M: small core, many touchpoints.

**Pending issues**

Bracketed references above are fully specified work packages that Linear refused to create on 2026-09-17 (`USAGE_LIMIT_EXCEEDED`, free-plan issue cap). Their specs live in the project document(s) [business-core](<https://linear.app/paperos/document/round-2-pending-issues-business-core-11-7c8c2526b3c9>) and they are created as issues by `round2/agent4/create_issues.py` once the workspace plan is upgraded.
