---
identifier: "PAP-34"
title: "Implement Postgres row-level security policies for multi-tenant isolation with a cross-tenant test harness"
project: "data-layer"
projectName: "Data Layer & Database"
phase: "P0"
type: "Build"
priority: 1
surfaces: ["Developer", "Staff"]
milestone: "Postgres + Drizzle baseline"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-33"]
blocks: ["PAP-228", "PAP-270", "PAP-36", "PAP-39", "PAP-59"]
key: "data-layer/rls-tenancy"
url: "https://linear.app/paperos/issue/PAP-34/implement-postgres-row-level-security-policies-for-multi-tenant"
source: "plan/specs/bucket-0.json (round-1 canonical spec JSON)"
---

# PAP-34: Implement Postgres row-level security policies for multi-tenant isolation with a cross-tenant test harness

**Goal**

Enforce tenant isolation inside Postgres with row-level security so that even a buggy agent-written query using the application role cannot read or write another tenant's rows, and prove it continuously with a cross-tenant test harness that any new table is automatically enrolled in.

**Scope**

In:
- RLS enabled and forced (`ENABLE` + `FORCE ROW LEVEL SECURITY`) on every table with a `tenant_id` column; policies generated from a single template.
- Session context contract: `app.tenant_id`, `app.actor_id`, `app.actor_kind`, `app.bypass` (owner-only) set via `SET LOCAL` by the client factory from `data-layer/drizzle-schema`.
- Policy generator `packages/db/src/rls/generate.ts` producing `drizzle/custom/00xx_rls.sql`: `tenant_isolation` (`USING tenant_id = current_setting('app.tenant_id')::uuid`) for SELECT/UPDATE/DELETE and `WITH CHECK` for INSERT/UPDATE; global tables (`user`, system `role`) get explicit read policies.
- Cross-tenant harness `packages/db/test/rls.harness.test.ts`: introspects `information_schema` for tenant tables, and for each attempts SELECT/INSERT/UPDATE/DELETE as tenant A against tenant B rows; expects zero rows/`42501` errors; fails if any table lacks RLS.
- Lint: CI check that every migration adding a `tenant_id` table also includes policies (generator diff).
- Performance guard: `EXPLAIN` test that policy predicate uses the `tenant_id` index on the five largest tables.
- Extension points for `identity/rbac-abac`: a `paperos.can(action, resource)` SQL function stub that policies for sensitive tables call, initially returning true when tenant matches.

Out: fine-grained permissions (`identity/rbac-abac`, `identity/permission-tests`), Electric's own permission layer (`data-layer/local-first-sync`), column-level masking.

**Spec**

- Roles: `paperos_app` has `NOBYPASSRLS`; `paperos_owner` runs migrations and has `BYPASSRLS` only in the migrator connection; `paperos_readonly` subject to RLS.
- Missing context fails closed: policies use `current_setting('app.tenant_id', true)` and `COALESCE(...,'00000000-0000-0000-0000-000000000000')::uuid` so no context means no rows.
- Global tables policy: `user` readable when the user shares a tenant with the actor (EXISTS on `membership`) or is the actor; system roles readable by all.
- Cross-tenant admin (platform staff) uses `app.bypass = 'on'` only through an audited API path (`data-layer/audit-log` records it) and only with the owner role.
- Electric replication role reads with RLS bypassed but shapes filtered by `tenant_id` (documented handoff to `data-layer/local-first-sync`).
- Generator is idempotent and re-runnable (`DROP POLICY IF EXISTS` then `CREATE`).
- Doc `docs/data/tenancy.md`: context contract, how to add a table, how to add a custom policy, bypass rules.

**Definition of done**

- Harness passes on all core tables and fails when a test table is added without a policy (demonstrated in PR).
- Vitest: fail-closed with no context; bypass only with owner role; `EXPLAIN` uses index.
- pgTAP or SQL-level tests for policies committed in `packages/db/test/sql/`.
- Security Auditor sign-off comment on PR.
- Screenshot of harness output and `\d+` showing policies (terminal, 1280).
- `docs/data/tenancy.md`; ADR `0007-rls-tenancy.md`; CHANGELOG; Linear comment with CI run.

**Edge cases**

- Table with `tenant_id` nullable (system-wide records): policy must handle NULL explicitly, never leak.
- Views and materialised views: `security_invoker = true` required; lint enforces.
- Functions with `SECURITY DEFINER`: banned except in `paperos` schema reviewed by Security Auditor.
- Bulk COPY/import (`migration/import-framework`) needs owner role with explicit `app.tenant_id`.
- `INSERT ... ON CONFLICT` across tenants must fail, not update.
- Partitioned `audit_event`: policies applied on parent propagate; verify on each partition.

**Dependencies**

`data-layer/core-entities` (hard). Consumed by `identity/rbac-abac`, `identity/permission-tests`, `data-layer/api-layer` (context setting), `data-layer/local-first-sync`, `quality/security-scans`.

**Agent**

Built by Forge (Schema Wright). Reviewed by Sentinel (Security Auditor primary) and Edge Case Hunter for the harness.

**Size**

M: policies are simple; the harness, fail-closed semantics and lint make it durable.
