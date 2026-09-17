---
identifier: "PAP-173"
title: "Compose views into dashboard pages with drag-arranged blocks and cross-filters"
project: "tables"
projectName: "Table & Views Engine"
phase: "P2"
type: "Build"
priority: 2
surfaces: ["Staff"]
milestone: "View sharing, formulas, dashboards"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-155", "PAP-165", "PAP-170", "PAP-172"]
blocks: ["PAP-186"]
key: "tables/dashboard-blocks"
url: "https://linear.app/paperos/issue/PAP-173/compose-views-into-dashboard-pages-with-drag-arranged-blocks-and-cross"
source: "plan/specs/bucket-6.json (round-1 canonical spec JSON)"
---

# PAP-173: Compose views into dashboard pages with drag-arranged blocks and cross-filters

**Goal**

Compose views into dashboard pages: a responsive 12-column grid of drag-arranged blocks (any view kind, KPI numbers, text, filter controls) with cross-filtering, so a click on a chart bar filters the grid beside it. This is the "incredible ways to view data on one page" outcome and the surface `business-core/cash-dashboard` and `pm-linear/board-views` build on.

**Scope**

In:
- Tables `dashboard` and `dashboard_block`; oRPC `dashboards.*` and `dashboardBlocks.*`.
- `packages/views/src/dashboard/`: `<Dashboard />`, `<DashboardEditor />`, `<Block />` wrapper, `<FilterBarBlock />`, `<TextBlock />`, `<NumberBlock />`, block picker.
- Cross-filter bus, global date range, dashboard-level parameters, fullscreen block, refresh interval.
- Page spec support: `layout.dashboard: <dashboardId>` in `page.spec.yaml`.

Out: scheduled email snapshots (`collab/notifications` follow-up), per-block permissions beyond inheriting view permissions, dashboard templates marketplace.

**Spec**

- `dashboard`: `id, tenant_id, workspace_id, name, description, layout jsonb (per breakpoint), params jsonb, visibility, owner_user_id, refresh_seconds?, position`. `dashboard_block`: `id, dashboard_id, kind: 'view'|'number'|'text'|'filter'|'divider', view_id?, spec_override jsonb, title, config jsonb, x, y, w, h, min_w, min_h`.
- Grid: 12 columns, row height 40 px, gap from tokens; breakpoints `lg >= 1280` (12 cols), `md >= 768` (8 cols), `sm < 768` (1 col, blocks stack by `y`); each breakpoint layout stored separately, `sm` auto-derived unless customised. Drag and resize via `input/drag-drop` with 8-direction handles; collision pushes blocks down; keyboard: select block, arrows move by one cell, Shift+arrows resize; announcements.
- Blocks render the referenced view in "embedded" mode (no toolbar, compact header with title, view kind icon, menu: edit, duplicate, fullscreen, export, remove) using `spec_override` merged over the view spec (so one saved view can appear twice with different filters).
- Cross-filter bus: `DashboardFilterContext` holds `{ global: FilterGroup, byBlock: Record<blockId, FilterCondition[]> }`; views emit `onFilter` (charts, map, kanban column header, grid group header); each block subscribes and merges applicable conditions where the block's dataset has the same field key or a mapped field (`config.fieldMap`); the active filters render as removable chips in a dashboard header bar; blocks can opt out (`config.ignoreCrossFilter`).
- `FilterBarBlock` exposes chosen fields as controls (select chips, date range, user picker, search) writing to `global`; global date range applies to any block whose dataset has a `dateField` mapping.
- `NumberBlock` shows one aggregate with delta vs previous period, sparkline (ECharts line, no axes) and goal colouring; `TextBlock` Markdown with variables `{{param.name}}`.
- Params: dashboard-level typed params (date range, tenant-scoped picker) bound to filters; URL `?p.range=last30d` for deep links.
- Refresh: optional interval (min 30 s) with a visible "updated n s ago"; Electric shapes make grids live regardless.
- Performance: blocks load lazily as they scroll into view; a 12-block dashboard settles under 2 s on the seed tenant; each block has its own error boundary and skeleton.
- Export: dashboard PDF via Playwright print route `/print/d/:id` (A4 and Letter) used by finance reports.

**Definition of done**

- Vitest for layout collision, breakpoint derivation, cross-filter merge, URL param parsing.
- Playwright: add blocks, drag, resize, cross-filter from chart to grid, fullscreen, keyboard move; screenshots of a 6-block demo dashboard at 375, 768, 1024, 1440, 1920 in three themes; video replay of cross-filtering.
- Performance trace attached showing the 2 s budget.
- Permission tests: viewer sees blocks only for views they may read (others render "No access" tile).
- `docs/views/dashboards.md`; CHANGELOG entry; Linear comment with the demo dashboard link.

**Edge cases**

- Referenced view deleted: block shows a "View removed" tile with replace action, dashboard still loads.
- Cross-filter on a field with different types across datasets (text vs select): mapping validated; mismatch ignored with a tooltip.
- 40 blocks: lazy loading and a warning at 30 that dashboards this large hurt performance.
- Two filter blocks controlling the same field: last change wins, both display the current value.
- Print at A4 with a map block: rendered as a static image; WebGL unavailable in print falls back to list.
- Block owner loses access to the view: block renders "No access" for them, others unaffected.

**Dependencies**

- `tables/map-chart-views` (chart and map blocks), `tables/grid-view`, `input/drag-drop`, `tables/view-sharing` (dashboard visibility mirrors view visibility), `spec-builder/layout-codegen` for the page spec hook.

**Agent**

Builder: Nova (Views Engineer). Reviewer: Sentinel (Visual Inspector, Code Reviewer); Iris on block chrome.

**Size**

L: layout engine plus cross-filter semantics touching every view; two sessions.
