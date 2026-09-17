---
key: "tables/compiler/groups-shapes"
title: "Groups, aggregates and Electric shape eligibility"
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

# Groups, aggregates and Electric shape eligibility

**Goal**

Add level-by-level grouping, aggregates and Electric shape emission to the compiler so grouped views and live grids work without client-side computation.

**Scope**

In: `compiler/groups.ts`, `compiler/aggregates.ts`, `compiler/shape.ts`; `views.groups` and `views.distinct` SQL; shape registration. Out: procedures and hook (sibling).

**Spec**

* `compileGroups(spec, groupPath)` returns group keys, counts and aggregates for one level (three-level grouping is three cheap queries); `unnest` when `expandMulti`; group pages of 100.
* Aggregates: `count`, `sum`, `avg`, `min`, `max`, `percentile_cont(0.5)`, `count(distinct)`, empty and filled via `count(*) filter (where ...)`; currency sums grouped by currency.
* Shape eligible only for a flat AND of `is|isAnyOf|isEmpty` on indexed columns with no groups; `ShapeDef` registered through PAP-270 with a server-set `where`; otherwise `shape` undefined.

**Interface contract**

Provides: `compileGroups`, `compileAggregates`, `shapeFor(spec)`, `ShapeDef`. Consumes: core child, shape registry (PAP-270).

**Definition of done**

* Unit tests for each aggregate and for `expandMulti`; shape eligibility table test; docs section on shape eligibility.

**Test plan**

* Unit: aggregates versus oracle on fixtures; eligibility matrix; group pagination.
* Integration: shape registered in the PAP-270 proxy returns the same rows as `views.query` for an eligible view.

**Demo**

Run `pnpm tsx scripts/groups-demo.ts` printing three levels of groups with counts and sums for the seed dataset.

**Edge cases**

* 10k distinct group values paginated; mixed currencies never summed blindly.

**Dependencies**

Core child (hard), PAP-270 (soft). Blocks the api child.

**Agent**

Builder: Nova (Views Engineer). Reviewer: Sentinel (Code Reviewer).

**Size**

M: one session.
