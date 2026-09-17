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
blockedBy: ["PAP-177", "PAP-229", "PAP-59"]
blocks: []
key: "business-core/entitlements"
url: "https://linear.app/paperos/issue/PAP-178/map-plans-to-feature-entitlements-enforced-by-the-permission-engine"
source: "plan/specs/bucket-6.json (round-1 canonical spec JSON)"
---

# PAP-178: Map plans to feature entitlements enforced by the permission engine

**Goal**

Make paid features gate themselves: map each plan to typed entitlements (booleans and limits), expose them through the permission engine so page specs and components can declare `requires: entitlement.publicViews`, enforce limits server-side at the point of creation, and show consistent upgrade prompts instead of silent failures.

**Scope**

In:
- `packages/finance/src/entitlements/`: registry, resolver, oRPC middleware, React hooks, `<UpgradePrompt />`, `<EntitlementGate />`.
- Entitlement keys v1: `seats` (number), `publicViews` (number), `dashboards` (number), `storageGb` (number), `apiRateLimit` (number), `whiteLabel` (bool), `sso` (bool), `payroll` (bool), `connectPayments` (bool), `auditRetentionDays` (number), `agentSessionsPerDay` (number).
- Hook points in `identity/org-tenancy` (`beforeInvite`), `tables/view-sharing` (public view count), `tables/dashboard-blocks`, `data-layer/file-storage` (storage), `identity/sso-scim`, `pm-linear/concurrency` (agent sessions).

Out: per-seat proration logic (Stripe handles quantity), custom enterprise overrides UI beyond a JSON field, metering of usage-based prices.

**Spec**

- Registry `defineEntitlement({ key, type: 'boolean'|'limit', label, description, unit?, upgradeCopy })`; plans in `business-core/stripe-billing` `plans.ts` supply values; `tenant.entitlement_overrides jsonb` (set by platform admins only) merges last. Free plan defaults are the floor when no subscription exists.
- Resolver `resolveEntitlements(tenantId) => Entitlements` cached per request and invalidated on `subscription` change events and override writes; exposed via `orpc.entitlements.mine` to the client and pushed through the session payload at login and tenant switch.
- Permission integration: the resolver injects `actor.attributes.entitlements` so `identity/rbac-abac` conditions like `{ path: 'actor.attributes.entitlements.whiteLabel', op: 'eq', value: true }` work; spec builder access sections accept a shorthand `requires: [entitlement.sso]` that compiles to that condition (`spec-builder/access-section`).
- Limits: `assertWithinLimit(tenantId, key, currentCountFn, increment = 1)` used inside the creating transaction (advisory lock per tenant and key) so concurrent creates cannot exceed the limit; returns `ORPCError('FORBIDDEN', { code: 'ENTITLEMENT_LIMIT', key, limit, current })`.
- Client: `useEntitlement(key) => { allowed, limit, used, remaining, plan, upgradeUrl }`; `<EntitlementGate key fallback="prompt"|"hide"|"disable">` wraps UI; `<UpgradePrompt>` explains the feature, shows the smallest plan that includes it and links to Checkout (`billing.createCheckoutSession`) for admins or "Ask an admin" for others.
- Usage display in `/org/settings/billing`: progress bars for limit entitlements with `used/limit`.
- Downgrade behaviour: when a plan drops below current usage, nothing is deleted; over-limit resources become read-only (public views return 402-styled page, extra dashboards locked) with a banner listing what to remove; grace period 14 days configurable.
- Agents: entitlement checks apply to agent principals too; `agentSessionsPerDay` is read by the orchestrator (`pm-linear/concurrency`).

**Definition of done**

- Vitest for resolver precedence (free < plan < override), limit assertion under concurrency (spawn 20 parallel creates against limit 5, exactly 5 succeed), downgrade read-only behaviour.
- Permission matrix tests (`identity/permission-tests`) include an entitlement-gated page.
- Playwright: free tenant hits the public-view limit, sees the prompt, seeded upgrade flips access without reload (session refresh).
- Storybook for gate and prompt tagged `visual`; screenshots at 375, 1024, 1920 in three themes.
- `docs/finance/entitlements.md` listing keys and plan matrix, generated from the registry.
- CHANGELOG entry; Linear comment with demo link and the plan matrix table.

**Edge cases**

- Subscription webhook delayed after checkout: client polls `entitlements.mine` for 30 s after return from Stripe and shows "activating".
- Override grants a feature the plan lacks: allowed, shown as "included by agreement" in billing.
- Limit of 0 vs boolean false: registry forbids limits below 0; 0 means "none allowed" and renders as boolean-off in UI.
- Trial ends with usage over the free limit: read-only rules apply, no deletion.
- Entitlement key referenced in a spec but missing from the registry: validator (`spec-builder/validator`) fails the PR.
- Platform admin (PaperOS staff) viewing a tenant: their own entitlements never apply, the tenant's do.

**Dependencies**

- `business-core/stripe-billing` (plans and subscription), `identity/rbac-abac` (attribute conditions), `spec-builder/access-section` (shorthand), `identity/org-tenancy` (`beforeInvite` hook).

**Agent**

Builder: Ledger (Payments Integrator). Reviewer: Sentinel (Security Auditor on bypass attempts, Code Reviewer).

**Size**

M: small core, but many integration touchpoints across projects.
