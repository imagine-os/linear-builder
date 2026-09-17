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
blocks: ["PAP-36", "PAP-39", "PAP-59", "PAP-228", "PAP-270"]
key: "data-layer/rls-tenancy"
url: "https://linear.app/paperos/issue/PAP-34/implement-postgres-row-level-security-policies-for-multi-tenant"
source: "Linear snapshot 2026-09-17T15:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T13:40:59.138Z"
model: "claude-opus-5"
effort: "medium"
---

# PAP-34: Implement Postgres row-level security policies for multi-tenant isolation with a cross-tenant test harness

**Model / Effort:** Opus 5 (`claude-opus-5`) / medium — Build M, P0 in data-layer

**Goal**

Enforce tenant isolation inside Postgres with row-level security so a buggy agent-written query on the app role cannot touch another tenant's rows, and prove it continuously with a harness that auto-enrols every new table.

**Scope**

In:

* `ENABLE` and `FORCE ROW LEVEL SECURITY` on every table with `tenant_id`; policies generated from one template.
* Session contract `app.tenant_id`, `app.actor_id`, `app.actor_kind`, `app.bypass` set via `SET LOCAL` by `createDb` (PAP-32).
* Generator `packages/db/src/rls/generate.ts` emitting `drizzle/custom/00xx_rls.sql`; global-table read policies for `user` and system `role`.
* Harness `packages/db/test/rls.harness.test.ts` introspecting `information_schema`.
* `docs/data/tenancy.md`.

Out: permission engine (PAP-59), API context (PAP-35).

**Spec**

* `paperos_app` has `NOBYPASSRLS`; `paperos_owner` bypasses only in the migrator connection; `paperos_readonly` is subject to RLS.
* Fail closed: `current_setting('app.tenant_id', true)` coalesced to the nil UUID.
* `user` readable when sharing a tenant with the actor (EXISTS on `membership`) or being the actor; system roles readable by all.
* `app.bypass = 'on'` allowed only for the owner role through an audited API path (PAP-38 records `bypass_read`).
* Electric role reads with RLS bypassed; shapes filtered by `tenant_id` in the proxy (PAP-36).
* Generator idempotent (`DROP POLICY IF EXISTS` then `CREATE`); it also attaches PAP-38's audit trigger to every enrolled table.
* Views require `security_invoker = true`; `SECURITY DEFINER` banned outside the `paperos` schema.

**Interface contract**

Provides:

* Session variables `app.tenant_id`, `app.actor_id`, `app.actor_kind`, `app.request_id`, `app.reason`, `app.bypass` as the single database context contract (PAP-32 sets, PAP-35 supplies, PAP-38 reads, PAP-36 mirrors in the proxy).
* SQL function `paperos.current_tenant()` for use in policies and generated view SQL (PAP-163).
* Generator hook `registerPolicyOverride(table, sql)` for tables needing custom policies (PAP-100, PAP-179).
* Harness exported as a Vitest helper `expectTenantIsolation(db)` that PAP-60 and PAP-80 reuse.

Consumes: tables (PAP-33), roles (PAP-30 in staging, PAP-42 locally).

**Definition of done**

* Harness passes on all core tables and fails when a test table lacks a policy (shown in the PR).
* Vitest: fail-closed with no context; bypass only with owner role; `EXPLAIN` shows the `tenant_id` index used.
* SQL tests committed in `packages/db/test/sql/`.
* Security Auditor sign-off comment.
* Terminal screenshots of harness output and `\d+` policies at 1280; `docs/data/tenancy.md`; ADR `0007-rls-tenancy.md`; CHANGELOG; Linear comment.

**Test plan**

* Harness: for each tenant table, SELECT, INSERT, UPDATE, DELETE as tenant A against tenant B rows; expect zero rows or `42501`.
* Unit: generator output snapshot for a fixture schema including a nullable `tenant_id` table and a partitioned table.
* Negative: `INSERT ... ON CONFLICT` across tenants fails; `SET` (session) rejected by lint.
* Performance: `EXPLAIN ANALYZE` on a 100k-row `load` seed shows index scan; p95 overhead under 10 percent versus RLS off (bench committed).
* Bypass: audited path logs `bypass_read`; non-owner bypass attempt raises.

**Demo**

Reviewer runs `pnpm --filter db test rls.harness` and watches every table pass, then adds a `scratch` table with `tenant_id` and no policy in a branch and reruns to watch the harness name it. Under 2 minutes.

**Edge cases**

* Nullable `tenant_id` handled explicitly; never leaks.
* Partition policies verified on each partition.
* Bulk COPY uses the owner role with explicit `app.tenant_id`.
* Materialised views need `security_invoker`.
* Missing context in a cron job: fail closed, PAP-43 sets `actor_kind = 'system'` with a tenant when needed.

**Dependencies**

PAP-33 (hard). Consumed by PAP-35, PAP-36, PAP-38, PAP-39, PAP-59, PAP-60, PAP-80.

**Agent**

Built by Forge (Schema Wright). Reviewed by Sentinel (Security Auditor).

**Size**

M: one generator, one harness, strong proofs.
