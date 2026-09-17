---
identifier: "PAP-335"
title: "Compiler core: dataset resolution, per-type filter ops, sorts and signed keyset cursors"
project: "tables"
projectName: "Table & Views Engine"
phase: "P1"
type: "Build"
priority: 1
surfaces: ["Developer"]
milestone: "Grid with sort, filter, group"
state: "Backlog"
parent: "PAP-163"
children: []
blockedBy: ["PAP-35", "PAP-59", "PAP-161", "PAP-228", "PAP-229", "PAP-269", "PAP-279"]
blocks: ["PAP-336"]
key: "tables/compiler/core"
url: "https://linear.app/paperos/issue/PAP-335/compiler-core-dataset-resolution-per-type-filter-ops-sorts-and-signed"
source: "Linear snapshot 2026-09-17T13:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T13:05:32.030Z"
---

# PAP-335: Compiler core: dataset resolution, per-type filter ops, sorts and signed keyset cursors

**Goal**

Produce correct, parameterised SQL for the rows and count of any `ViewSpec` on entity and custom datasets, with keyset pagination that clients cannot forge.

**Scope**

In: `packages/views/src/compiler/{index,dataset,ops/*,sort,cursor}.ts`; `compileView` returning `rows` and `count`; casts per field type; `views.ensureIndex` job. Out: groups, aggregates, shapes, procedures, hook (siblings).

**Spec**

* `resolveDataset(ref)` returns columns for entity datasets and `record.data -> 'key'` expressions with casts (`::numeric`, `::timestamptz`, `::boolean`, `::text[]`) for custom ones.
* One op module per field type exporting `ops: Record<FilterOp, (col, value, ctx) => SQL>`; relative dates resolved server-side in the actor timezone; `{ ref: 'currentUser' }` to `ctx.actor.id`; relations to `EXISTS`; lookups and rollups to lateral joins.
* Sort compiles `ORDER BY` with `NULLS LAST` and `id` tiebreaker; cursor is base64url JSON of last values, HMAC-SHA256 signed with a server key and the spec `version`; invalid signature `CURSOR_INVALID`, version mismatch `CURSOR_STALE`.
* `toPredicate(actor, action)` (PAP-228) ANDed into every statement.
* `ensureIndex` creates expression indexes for sorted custom fields, capped at 10 per dataset.

**Interface contract**

Provides: `compileView` (rows and count), `compileFilter`, `compileSort`, `encodeCursor`, `decodeCursor`, `ops` registry. Consumes: `ViewSpec` (PAP-161), `FilterTree` SQL evaluator (PAP-279), field casts (PAP-164), `toPredicate` (PAP-228).

**Definition of done**

* Table-driven tests per op per type; golden SQL snapshots for ten fixture views; cursor tamper test; cross-tenant test.
* `docs/views/query-compiler.md` sections for pipeline and cursor format.

**Test plan**

* Unit: every `(type, op)` pair compiles and matches the in-memory oracle on a 1k-row PGlite seed; cursor round trip, tamper and stale cases.
* Integration: `EXPLAIN` on the 100k seed shows index use for sorted custom fields after `ensureIndex`.
* E2E and visual: none.

**Demo**

Run `pnpm tsx scripts/explain-view.ts fixtures/grid.view.json` and read the SQL, bound parameters and plan.

**Edge cases**

* Null boundaries in cursors; deleted field in filter flagged `orphaned`; relation to unreadable record simply does not match.

**Dependencies**

PAP-161, PAP-279, PAP-228 (hard). Blocks the two sibling children.

**Agent**

Builder: Nova (Views Engineer). Reviewer: Sentinel (Security Auditor).

**Size**

M: the op matrix is wide but mechanical.
