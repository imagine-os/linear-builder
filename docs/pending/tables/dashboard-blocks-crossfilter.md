---
key: "tables/dashboard/blocks-crossfilter"
title: "Block kinds, cross-filter bus, filter bar, params and deep links"
project: "tables"
parent: "PAP-173"
phase: "P2"
type: "Build"
priority: 2
size: "M"
surfaces: []
milestone: "View sharing, formulas, dashboards"
intendedState: "Backlog"
blockedBy: []
blocks: []
source: "round2/agent4/pending-issues.json"
linearDocument: "https://linear.app/paperos/document/round-2-pending-issues-tables-24-86486d9b99cc"
status: "pending"
---

# Block kinds, cross-filter bus, filter bar, params and deep links

**Goal**

Render real views inside blocks and make them talk: a click in one block filters the others, with a filter bar and typed params in the URL.

**Scope**

In: `dashboard/{Block,NumberBlock,TextBlock,FilterBarBlock,filters,params}.tsx`, `defineNumberBlock`. Out: layout (sibling), print and perf (sibling).

**Spec**

* Blocks render views in `embedded` mode with `spec_override` merged; menu edit, duplicate, fullscreen, export, remove.
* `DashboardFilterContext` per the parent; `config.fieldMap` and `ignoreCrossFilter`; chips in the header bar.
* `FilterBarBlock` controls (select chips, date range, user picker, search) write to `global`; `NumberBlock` with delta, sparkline and goal colour; `TextBlock` Markdown with ``param.name``.
* Params in `?p.<name>=` for deep links.

**Interface contract**

Provides: block components, `defineNumberBlock`, `useDashboardFilters`, `FilterCondition` emission contract. Consumes: layout child, `onFilter` emitters (PAP-170, PAP-167, PAP-165), `FilterTree` (PAP-279), sparkline (PAP-170).

**Definition of done**

* Cross-filter merge unit tests; Playwright chart-to-grid filter, filter bar, params; replay; screenshots at five widths.

**Test plan**

* Unit: merge rules, type mismatch ignored, param parsing.
* E2E: click a bar, grid filters, chip removable; global date range refetches two charts.

**Demo**

Click a chart bar in `/demo/dashboard` and watch the grid filter and the chip appear.

**Edge cases**

* Two filter blocks on one field: last wins; deleted view shows a replace tile.

**Dependencies**

Layout child (hard), PAP-170, PAP-165, PAP-167, PAP-279.

**Agent**

Builder: Nova. Reviewer: Sentinel (Code Reviewer).

**Size**

M: cross-filter semantics.
