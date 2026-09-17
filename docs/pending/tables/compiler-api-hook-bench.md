---
key: "tables/compiler/api-hook-bench"
title: "oRPC procedures, useViewQuery hook and the 100k-row benchmark"
project: "tables"
parent: "PAP-163"
phase: "P1"
type: "Build"
priority: 1
size: "M"
surfaces: []
milestone: "Grid with sort, filter, group"
intendedState: "Backlog"
blockedBy: []
blocks: []
source: "round2/agent4/pending-issues.json"
linearDocument: "https://linear.app/paperos/document/round-2-pending-issues-tables-24-86486d9b99cc"
status: "pending"
---

# oRPC procedures, useViewQuery hook and the 100k-row benchmark

**Goal**

Expose the compiler through typed procedures and a React hook with infinite pagination, and prove the p95 budget on a 100k-row seed in CI.

**Scope**

In: `packages/views/src/api.ts` (`views.query|count|groups|distinct`), `useViewQuery`, `vitest bench` suite, seed script. Out: view components.

**Spec**

* Procedures are `tenantProcedure`s (PAP-268) taking `{ spec | viewId, cursor?, limit?, groupPath? }`; `limit` clamped to 200.
* `useViewQuery(spec, { pageSize }) => { pages, fetchNextPage, groups, aggregates, isStale }` on `@orpc/tanstack-query`; invalidates on record mutations, or via the shape change stream when a shape exists.
* Bench seeds 100k rows (entity and custom) and runs filtered, sorted, paginated queries; p95 under 150 ms recorded to the PR.

**Interface contract**

Provides: the four procedures, `useViewQuery`, `seedViews(n)`. Consumes: both sibling children, PAP-268, PAP-271 `useShape` (soft).

**Definition of done**

* Procedures documented in OpenAPI (PAP-269); bench green with the p95 table in the PR; cross-tenant harness on `views.query`.

**Test plan**

* Unit: hook pagination reducer with mocked procedures.
* Integration: bench in CI; `callAs` tests for two tenants; `limit 500` clamped.
* E2E: none (grid child covers it).

**Demo**

Run `pnpm --filter views bench compiler` and read the p95 table.

**Edge cases**

* Stale cursor restarts pagination; shape invalidation falls back to refetch when the stream drops.

**Dependencies**

Both sibling children (hard), PAP-268 (hard), PAP-271 (soft).

**Agent**

Builder: Nova (Views Engineer). Reviewer: Forge (Schema Wright) on the bench.

**Size**

M: bench setup dominates.
