---
identifier: "PAP-386"
title: "Block kinds, cross-filter bus, filter bar, params and deep links"
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
blockedBy: ["PAP-165", "PAP-170", "PAP-385"]
blocks: ["PAP-387"]
key: "tables/dashboard/blocks-crossfilter"
url: "https://linear.app/paperos/issue/PAP-386/block-kinds-cross-filter-bus-filter-bar-params-and-deep-links"
source: "Linear snapshot 2026-09-17T13:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T13:05:44.007Z"
model: "claude-sonnet-5"
effort: "high"
---

# PAP-386: Block kinds, cross-filter bus, filter bar, params and deep links

**Goal**

Render real views inside blocks and make them talk: a click in one block filters the others, with a filter bar and typed params in the URL.

**Scope**

In: `dashboard/{Block,NumberBlock,TextBlock,FilterBarBlock,filters,params}.tsx`, `defineNumberBlock`. Out: layout (sibling), print and perf (sibling).

**Spec**

* Blocks render views in `embedded` mode with `spec_override` merged; menu edit, duplicate, fullscreen, export, remove.
* `DashboardFilterContext` per the parent; `config.fieldMap` and `ignoreCrossFilter`; chips in the header bar.
* `FilterBarBlock` controls (select chips, date range, user picker, search) write to `global`; `NumberBlock` with delta, sparkline and goal colour; `TextBlock` Markdown with `{{param.name}}`.
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
