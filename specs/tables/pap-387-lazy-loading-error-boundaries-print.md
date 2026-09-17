---
identifier: "PAP-387"
title: "Lazy loading, error boundaries, print route, page-spec hook and permission tiles"
project: "tables"
projectName: "Table & Views Engine"
phase: "P2"
type: "Build"
priority: 2
surfaces: ["Staff"]
milestone: "View sharing, formulas, dashboards"
state: "Backlog"
parent: "PAP-173"
children: []
blockedBy: ["PAP-386"]
blocks: ["PAP-186"]
key: "tables/dashboard/print-perf-spec"
url: "https://linear.app/paperos/issue/PAP-387/lazy-loading-error-boundaries-print-route-page-spec-hook-and"
source: "Linear snapshot 2026-09-17T13:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T13:05:42.311Z"
---

# PAP-387: Lazy loading, error boundaries, print route, page-spec hook and permission tiles

**Goal**

Make dashboards fast, printable and embeddable from page specs, with graceful failure per block.

**Scope**

In: lazy block loading, per-block error boundary and skeleton, `/print/d/:id` (A4 and Letter), `layout.dashboard` in `page.spec.yaml` (PAP-120), "No access" tiles, refresh interval.

**Spec**

* Blocks load as they scroll into view; 12-block dashboard settles under 2 s on the seed tenant; refresh min 30 s with "updated n s ago".
* Print route renders without chrome; map blocks as static images; used by PAP-183 exports.
* Viewers see "No access" tiles for views they cannot read.

**Interface contract**

Provides: print route, `layout.dashboard` codegen hook, `BlockErrorBoundary`. Consumes: both sibling children, PAP-120, Playwright print (PAP-82 image).

**Definition of done**

* Performance trace attached; permission test; PDF snapshot; docs `docs/views/dashboards.md`.

**Test plan**

* Integration: settle time on seed; PDF page count.
* E2E: viewer without access sees the tile; block error does not break the page.

**Demo**

Print `/demo/dashboard` to PDF and open it.

**Edge cases**

* WebGL absent in print: list fallback.

**Dependencies**

Sibling children (hard), PAP-120 (soft).

**Agent**

Builder: Nova. Reviewer: Sentinel.

**Size**

S: half a session.
