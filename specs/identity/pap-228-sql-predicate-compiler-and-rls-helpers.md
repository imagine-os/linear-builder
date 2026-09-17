---
identifier: "PAP-228"
title: "SQL predicate compiler and RLS helpers"
project: "identity"
projectName: "Identity, Roles & Audiences"
phase: "P0"
type: "Build"
priority: 1
surfaces: ["Developer"]
milestone: "Auth works across web and desktop"
state: "Backlog"
parent: "PAP-59"
children: []
blockedBy: ["PAP-34", "PAP-227"]
blocks: ["PAP-39", "PAP-163", "PAP-335"]
key: "identity/rbac-abac/sql-compiler-rls"
url: "https://linear.app/paperos/issue/PAP-228/sql-predicate-compiler-and-rls-helpers"
source: "Linear snapshot 2026-09-17T13:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T06:22:39.016Z"
---

# PAP-228: SQL predicate compiler and RLS helpers

**Goal**

Compile the same policies to SQL so list endpoints filter in the database and Postgres RLS enforces the boundary even if application code forgets, with a property test proving SQL and `can()` agree.

**Scope**

* In: `compile-sql.ts` with `toPredicate()` and `toRlsPolicy()`, session-variable contract, Drizzle helpers `withPermissionFilter(query, actor, action)`, PGlite property test, migration generator for policies on core tables.
* Out: evaluator (sibling), middleware (sibling).

**Spec**

* `toPredicate(actor, action, resourceType) => SQL` produces a Drizzle `sql` fragment over the resource table's columns; actor attributes are inlined as parameters.
* `toRlsPolicy(resourceType, action) => string` emits `CREATE POLICY` using `current_setting('app.principal_id')`, `app.tenant_id`, `app.role`, `app.attrs::jsonb`; conditions on `actor.attributes.*` compile to `current_setting('app.attrs', true)::jsonb ->> key`; `contains` uses `?`.
* Column mapping: `resource.<field>` resolves through a per-table `permissionColumns` map exported next to the Drizzle table (PAP-33 convention) so renamed columns fail at typecheck.
* `pnpm permissions:rls:generate` writes `packages/db/src/rls/<table>.sql` for tables tagged `rls: true`, applied by PAP-34's harness.

**Interface contract**

* Provides: `toPredicate`, `toRlsPolicy`, `withPermissionFilter`, `permissionColumns` type; session variables `app.principal_id`, `app.tenant_id`, `app.role`, `app.attrs` (set by PAP-58 `withTenant`).
* Requires: sibling evaluator, PAP-34 session-variable harness and PGlite fixtures, PAP-33 tables.

**Definition of done**

* Property test: 10 000 random actor/resource pairs, SQL predicate result equals `can()` on PGlite for `invoices` and `files` fixtures.
* Generated RLS applied in the PAP-34 harness: cross-tenant and cross-owner reads return zero rows; writes fail.
* Unsupported condition shape produces a compile-time error naming the policy id.
* Docs section "SQL compilation".

**Test plan**

* Unit: each op to SQL snapshot; parameter binding (no string interpolation).
* Property: agreement test above.
* Integration: RLS in PGlite and in Postgres 17 (compose) nightly.

**Demo**

`pnpm permissions:rls:generate && pnpm test --filter permissions -t agreement`; open the generated `invoices.sql` and read the policy for `invoice.read`. Under two minutes.

**Edge cases**

* Policy with `in` over an empty list: compiles to `false`.
* jsonb attribute typed number vs string: compare as text with documented casting.
* Table lacks a column a policy references: typecheck failure, not runtime.

**Dependencies**

Sibling evaluator child (hard), PAP-34 (hard for the harness).

**Agent**

Built by Forge (Schema Wright). Reviewed by Sentinel (Security Auditor).

**Size**

M.
