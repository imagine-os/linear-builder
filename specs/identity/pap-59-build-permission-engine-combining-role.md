---
identifier: "PAP-59"
title: "Build permission engine combining role-based grants with attribute policies declared in page specs"
project: "identity"
projectName: "Identity, Roles & Audiences"
phase: "P0"
type: "Build"
priority: 1
surfaces: ["Developer"]
milestone: "Auth works across web and desktop"
state: "Backlog"
parent: null
children: ["PAP-227", "PAP-228", "PAP-229"]
blockedBy: ["PAP-34", "PAP-55", "PAP-279"]
blocks: ["PAP-39", "PAP-60", "PAP-61", "PAP-64", "PAP-116", "PAP-131", "PAP-140", "PAP-163", "PAP-172", "PAP-178", "PAP-222", "PAP-317", "PAP-335", "PAP-501", "PAP-538", "PAP-566", "PAP-586", "PAP-623", "PAP-768", "PAP-835", "PAP-849", "PAP-884", "PAP-902", "PAP-912"]
key: "identity/rbac-abac"
url: "https://linear.app/paperos/issue/PAP-59/build-permission-engine-combining-role-based-grants-with-attribute"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T12:56:50.654Z"
model: null
effort: null
estimate: null
dueDate: "2026-09-23"
cycle: null
---

# PAP-59: Build permission engine combining role-based grants with attribute policies declared in page specs

**Model / Effort:** set on children (umbrella is never claimed)

**Goal**

Build the permission engine every layer shares: one `can(actor, action, resource, ctx)` combining role grants with attribute policies from page specs, evaluated identically in the API, compiled to SQL for RLS and list filters, and driving UI affordances through `useCan`. Deny by default, explainable on request. This issue is the umbrella for three children.

**Children**

1. PAP-227 Policy model, evaluator and explain mode (M) - blocks the other two.
2. PAP-228 SQL predicate compiler and RLS helpers (M).
3. PAP-229 Spec adapter, oRPC middleware and `useCan` hook (M).

**Scope**

* In (across children): `packages/permissions` model, evaluator, built-in role policies, explain CLI, SQL compiler, RLS generator, spec adapter, `authorize()` middleware, `PermissionProvider` and `useCan`, design-system `can` props, docs and benchmarks.
* Out: the access-section YAML format (PAP-116 defines it; PAP-229 adapts), agent keys and scopes (PAP-60), generated matrix tests (PAP-64), entitlements (PAP-178 adds policies).

**Spec**

Detailed specs live in the children. Cross-child invariants:

* One semantics: `can()` and `toPredicate()` must agree on every input; the property test in PAP-228 is the contract.
* Deny wins over allow regardless of specificity; no precedence rules.
* Policies carry `source: { specPath, line }` so every 403 and every matrix diff can point at a file.
* Actor is the PAP-55 `Principal`; audiences are resolved with `matches()`.

**Interface contract**

* Provides (from `@paperos/permissions`): types `Policy`, `Action`, `Condition`, `Decision`, `ResourceRef`; `can()`, `explain()`, `BUILTIN_POLICIES`; `toPredicate()`, `toRlsPolicy()`, `withPermissionFilter()`, `permissionColumns`; `accessToPolicies()`; `authorize()` middleware; procedure `permissions.mine`; `PermissionProvider`, `useCan()`; `can` prop on Button, IconButton, Menu.Item.
* Requires: PAP-55 audience model, PAP-34 session variables and harness, PAP-58 `withTenant`, PAP-35 oRPC, PAP-67 components, PAP-116 final access shape (soft).
* Consumers: PAP-60 `withScopes`, PAP-61 impersonation actions, PAP-64, PAP-116, PAP-140 Yjs auth hook, PAP-39 search filters, PAP-131, PAP-172, PAP-178.
* Contract source: [Interface & Data Contracts](<https://linear.app/paperos/document/paperos-interface-and-data-contracts-d40e6a4d227c>) §1 (`Principal` is the `actor` argument of `can()`; `Condition` is an alias of `FilterTree` from `@paperos/core/filter` (PAP-279), with `{ $var: 'principal.id' }` variables resolved at evaluation; identity adds `app.principal_id, app.role, app.attrs` to the RLS session variables); §4 (non-production error bodies carry `explain` from `can()`); §6 rows "`can()` and SQL predicates" and "`Principal` and audiences".

**Definition of done**

* All three children Done.
* Integration test below green; benchmark table and RLS harness results in the PR.
* `docs/platform/permissions.md` complete (algorithm, verb table, three worked examples: customer sees own invoices, support may impersonate, agents may not delete); changelog under "Identity".
* Quill confirms the adapter matches PAP-116; Sentinel Security Auditor signs off.

**Test plan**

Integration test `packages/permissions/test/umbrella.test.ts` on PGlite:

* Load the three example specs (PAP-125) plus built-ins; for each of the twelve fixture principals and each declared action, assert `can()` equals the row count of `toPredicate()` applied to a two-tenant fixture, and that `toRlsPolicy()` installed in the harness yields the same visible rows.
* `authorize()` returns 403 with explain text in dev and generic text in production build.
* `useCan` story matrix screenshots at 375 and 1280.
* Bench: `can` median under 20 µs with 200 policies.

**Demo**

Run `pnpm permissions explain --actor fixtures/staff-support.json --action invoice.update --resource invoice:123` and read the matched policy with its spec line; open Storybook "Permissions" and switch the actor control to watch Delete hide; open the generated `invoices.sql`. Under two minutes.

**Edge cases**

Cross-child: a policy referencing an undeclared audience fails at load in every child identically (shared validator); resources without `tenantId` only match `global: true` policies in both engines; attribute changes mid-session are seen by the server immediately and by the client after `session.updated`.

**Dependencies**

PAP-55, PAP-34 (hard). Soft: PAP-116, PAP-35, PAP-58, PAP-67.

**Agent**

Forge leads (Schema Wright on PAP-228); Iris on component props. Sentinel (Security Auditor mandatory, Edge Case Hunter on property tests) reviews.

**Size**

L, split into 3 children (M, M, M).

**Module boundary**

This umbrella is the Identity, Roles & Audiences half of the PaperOS Module System (`docs/module-system.md`). The `identity` module implements `@paperos/contract-identity` (`Principal`, auth, permission, tenant, impersonation ports, audience segments). Every other module checks permissions only through `PermissionPort.can()` and reads the actor only from the request scope; the module may import `@paperos/core`, `@paperos/contract-data-layer` and its own packages, and never the Better Auth client from anywhere else. Its manifest declares `provides: [{ contract: '@paperos/contract-identity', version: '0.1.0' }]`, `owner: { agent: 'Forge', project: 'identity' }` and `swapRisk: 'critical'`. The contract package is published by `PAP-456`, proven by `PAP-457` and bound into `@paperos/kernel` by `PAP-458`; children of this issue inherit this boundary and may not add a dependency the manifest does not declare (lint rules R7 to R11).
