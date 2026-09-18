---
identifier: "PAP-163"
title: "Build the view query compiler from view model to SQL and Electric shapes with server-side pagination"
project: "tables"
projectName: "Table & Views Engine"
phase: "P1"
type: "Build"
priority: 1
surfaces: ["Developer"]
milestone: "Grid with sort, filter, group"
state: "Backlog"
parent: null
children: ["PAP-337", "PAP-336", "PAP-335"]
blockedBy: ["PAP-35", "PAP-59", "PAP-161", "PAP-228", "PAP-229", "PAP-269", "PAP-279"]
blocks: ["PAP-165", "PAP-167", "PAP-168", "PAP-169", "PAP-170", "PAP-171", "PAP-183", "PAP-194", "PAP-195", "PAP-341", "PAP-344", "PAP-619", "PAP-621", "PAP-629"]
key: "tables/query-compiler"
url: "https://linear.app/paperos/issue/PAP-163/build-the-view-query-compiler-from-view-model-to-sql-and-electric"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T12:57:10.625Z"
model: null
effort: null
estimate: null
dueDate: "2026-09-28"
cycle: null
---

# PAP-163: Build the view query compiler from view model to SQL and Electric shapes with server-side pagination

**Model / Effort:** set on children (umbrella is never claimed)

**Goal**

Turn any `ViewSpec` into an RLS-respecting Postgres query and, where eligible, an Electric shape, so every view kind renders server-paginated rows, groups and aggregates without writing SQL. Umbrella for three children; this issue is Done when all three are Done and the integration bench below passes.

**Scope**

Children (M each, same milestone, Backlog):

* PAP-335 Compiler core: dataset resolution, per-type filter ops, sorts and signed keyset cursors.
* PAP-336 Groups, aggregates and Electric shape eligibility.
* PAP-337 oRPC procedures, `useViewQuery` hook and the 100k-row benchmark.

Out: filter UI (PAP-166), formula evaluation (PAP-171; formula fields opaque until then), full-text ranking (PAP-39).

**Spec**

Decisions binding all children:

* `compileView(spec, ctx: { actor, tenantId, dataset, cursor?, limit, groupPath? }) => { rows: SQL, count: SQL, groups?: SQL, aggregates?: SQL, shape?: ShapeDef }` using Drizzle `sql` fragments; all literals bound, never concatenated.
* Custom datasets compile `record.data -> 'key'` with casts from the field type; expression indexes created on demand by `views.ensureIndex` (cap 10 per dataset); GIN on `data`.
* Filters compile through the shared evaluator of PAP-279 with per-type op modules in `compiler/ops/<type>.ts`; relations to `EXISTS`; lookups and rollups to lateral joins.
* Keyset cursors: base64url JSON of last sort values plus `id`, HMAC-signed; `limit` max 200, default 50.
* `toPredicate(actor, '<entity>.list')` from PAP-228 ANDed into every query; RLS is the backstop.
* Shapes only for flat AND of `is|isAnyOf|isEmpty` on indexed columns with no groups (PAP-270 registry).

**Interface contract**

Provides: `compileView`, `compileFilter`, `compileSort`, `compileGroups`, `compileAggregates`, `ShapeDef`, procedures `views.query|count|groups|distinct`, hook `useViewQuery(spec, { pageSize }) => { pages, fetchNextPage, groups, aggregates, isStale }`, error codes `CURSOR_INVALID`, `CURSOR_STALE`. Consumes: `ViewSpec` (PAP-161), `FilterTree` evaluators (PAP-279), `toPredicate` (PAP-228), `tenantProcedure` and error mapping (PAP-267, PAP-268), shape registry (PAP-270), field casts (PAP-164). Consumed by every view kind, PAP-183 reports, PAP-194 rollups, PAP-195 segments.

**Definition of done**

* All three children Done.
* Integration bench: 100k-row seed, filtered plus sorted plus paginated query p95 under 150 ms in CI (`vitest bench`), `EXPLAIN` shows index use, no sequential scan on `record`.
* Golden SQL snapshots for the ten fixture views; cross-tenant harness extended with view queries.
* `docs/views/query-compiler.md` (pipeline, cursor format, shape eligibility); CHANGELOG; Linear comment with the benchmark table.

**Test plan**

Umbrella integration test `packages/views/test/compiler.e2e.test.ts`: seed 100k rows across an entity and a custom dataset; run each fixture view through `views.query`, `views.groups` (3 levels) and `views.count`; assert row counts against an in-memory oracle from PAP-279's evaluator; tamper a cursor and expect `CURSOR_INVALID`; run as two tenants and assert zero leakage; record p95 timings. Visual: none.

**Demo**

Reviewer runs `pnpm --filter views bench compiler` and sees the p95 table, then `pnpm tsx scripts/explain-view.ts fixtures/grid.view.json` printing generated SQL and the `EXPLAIN` plan with the index scan highlighted. Under two minutes.

**Edge cases**

* All-null sort field: `nullsLast` honoured, cursor handles null boundaries.
* Group key with 10k distinct values: `views.groups` paginates at 100.
* Field type changed after a cursor was issued: `CURSOR_STALE`, client restarts.
* Currency `sum` across currencies returns a per-currency map.
* Actor and tenant timezones differ for `today`: actor wins, documented.

**Dependencies**

PAP-161 (hard), PAP-35 children (hard), PAP-59 via PAP-228 (hard), PAP-279 (hard), PAP-36 children (soft: shapes optional), PAP-164 (casts, either order). Blocks PAP-165, PAP-167, PAP-168, PAP-169, PAP-170, PAP-194, PAP-195.

**Agent**

Builder: Nova (Views Engineer). Reviewer: Sentinel (Security Auditor for injection and cursor forgery), Forge (Schema Wright) for indexes.

**Size**

L, split into three M children; the umbrella carries only the integration bench.

**Pending issues**

Bracketed references above are fully specified work packages that Linear refused to create on 2026-09-17 (`USAGE_LIMIT_EXCEEDED`, free-plan issue cap). Their specs live in the project document(s) [tables](<https://linear.app/paperos/document/round-2-pending-issues-tables-24-86486d9b99cc>) and they are created as issues by `round2/agent4/create_issues.py` once the workspace plan is upgraded.

**Module boundary**

This umbrella is the Table & Views Engine half of the PaperOS Module System (`docs/module-system.md`). The `tables` module implements `@paperos/contract-tables` (`ViewSpec`, `FieldDef`, dataset registration, view query, renderer registry, field type plugin, formula, automation trigger and record ports). PM, finance, CRM, import and dashboards register datasets and render views only through these ports; the module may import `@paperos/core`, `contract-data-layer`, `contract-identity`, `contract-design-system`, `contract-input` and its own package. Its manifest declares `provides: [{ contract: '@paperos/contract-tables', version: '0.1.0' }]`, `owner: { agent: 'Nova', project: 'tables' }` and `swapRisk: 'high'`. The contract package is published by PAP-483 (`module/tables/contract`), proven by PAP-486 (`module/tables/conformance`) and bound into `@paperos/kernel` by PAP-489 (`module/tables/wire`); children of this issue inherit this boundary and may not add a dependency the manifest does not declare (lint rules R7 to R11).
