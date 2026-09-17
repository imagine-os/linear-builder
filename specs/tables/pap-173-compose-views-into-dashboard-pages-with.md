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
children: ["PAP-385", "PAP-386", "PAP-387"]
blockedBy: ["PAP-155", "PAP-165", "PAP-170", "PAP-172", "PAP-331", "PAP-343"]
blocks: ["PAP-186"]
key: "tables/dashboard-blocks"
url: "https://linear.app/paperos/issue/PAP-173/compose-views-into-dashboard-pages-with-drag-arranged-blocks-and-cross"
source: "Linear snapshot 2026-09-17T13:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T13:06:14.115Z"
model: null
effort: null
---

# PAP-173: Compose views into dashboard pages with drag-arranged blocks and cross-filters

**Goal**

Compose views into dashboard pages: a responsive 12-column grid of drag-arranged blocks (any view kind, KPI numbers, text, filter controls) with cross-filtering, so a click on a chart bar filters the grid beside it. PAP-186 and PAP-102 build on it. Umbrella for three children.

**Scope**

Children (same milestone, Backlog):

* PAP-385 (M) Tables, layout engine, breakpoint layouts, drag and resize with keyboard moves.
* PAP-386 (M) Block kinds (`view`, `number`, `text`, `filter`, `divider`), cross-filter bus, filter bar, params and deep links.
* PAP-387 (S) Lazy loading and error boundaries, print route `/print/d/:id`, `layout.dashboard` page-spec hook, permission tiles.

Out: scheduled email snapshots, per-block permissions beyond view inheritance, templates marketplace.

**Spec**

Decisions binding all children:

* `dashboard (id, tenant_id, workspace_id, name, description, layout jsonb per breakpoint, params jsonb, visibility, owner_user_id, refresh_seconds?, position)`; `dashboard_block (id, dashboard_id, kind, view_id?, spec_override jsonb, title, config jsonb, x, y, w, h, min_w, min_h)`.
* Grid: 12 columns at `lg >= 1280`, 8 at `md >= 768`, 1 at `sm`; row height 40 px; `sm` auto-derived from `y` unless customised; collisions push down.
* Blocks render views in `embedded` mode with `spec_override` merged over the saved spec.
* `DashboardFilterContext = { global: FilterTree, byBlock: Record<blockId, FilterCondition[]> }`; blocks merge conditions whose field key exists or is mapped in `config.fieldMap`; `config.ignoreCrossFilter` opts out; chips in the header bar.
* Params typed (date range, tenant-scoped picker) and mirrored in `?p.<name>=`.
* Budget: 12-block dashboard settles under 2 s on the seed tenant; each block has its own error boundary and skeleton.

**Interface contract**

Provides: `<Dashboard id />`, `<DashboardEditor />`, `<Block />`, `<NumberBlock />`, `<TextBlock />`, `<FilterBarBlock />`, `defineNumberBlock({ key, query, format })` registry used by PAP-183 and PAP-186, `useDashboardFilters()`, procedures `dashboards.*`, `dashboardBlocks.*`, print route, `layout.dashboard` in `page.spec.yaml` (PAP-120). Consumes: `onFilter` from charts, map, kanban and grid group headers (PAP-170, PAP-167, PAP-165), `FilterTree` (PAP-279), drag (PAP-155), visibility (PAP-172), ECharts sparkline (PAP-170), Playwright print (PAP-82 image).

**Definition of done**

* All three children Done.
* Permission tests: a viewer without access to one view sees a "No access" tile, others render.
* Screenshots of a six-block demo at 375, 768, 1024, 1440, 1920 in three themes; cross-filter replay; performance trace under 2 s.
* `docs/views/dashboards.md`; CHANGELOG; Linear comment with the demo dashboard link.

**Test plan**

Umbrella `dashboard.e2e.spec.ts`: build a six-block dashboard (chart, grid, number, filter bar, text, map) via the editor; click a chart bar and assert the grid's row count and the header chip; clear the chip; set the global date range and assert both charts refetch; move a block with keyboard and assert `layout.lg`; resize the viewport to 700 px and assert single-column order; print `/print/d/:id` to PDF and assert page count; measure settle time on the seed tenant.

**Demo**

Reviewer opens `/demo/dashboard`, clicks a bar in the chart, watches the grid filter and a chip appear, drags the chart wider, opens fullscreen on the number block, then prints to PDF. Under two minutes.

**Edge cases**

* Referenced view deleted: "View removed" tile with replace action.
* Cross-filter type mismatch across datasets: ignored with a tooltip.
* 40 blocks: lazy loading and a warning at 30.
* Two filter blocks on one field: last change wins, both display it.
* Print with a map block: static image, list fallback without WebGL.

**Dependencies**

PAP-170 (hard), PAP-165 (hard), PAP-155 (hard), PAP-172 (hard, visibility), PAP-120 (page-spec hook, soft), PAP-279. Blocks PAP-186.

**Agent**

Builder: Nova (Views Engineer). Reviewer: Sentinel (Visual Inspector, Code Reviewer); Iris on block chrome.

**Size**

L, split into two M children and one S child.

**Pending issues**

Bracketed references above are fully specified work packages that Linear refused to create on 2026-09-17 (`USAGE_LIMIT_EXCEEDED`, free-plan issue cap). Their specs live in the project document(s) [tables](<https://linear.app/paperos/document/round-2-pending-issues-tables-24-86486d9b99cc>) and they are created as issues by `round2/agent4/create_issues.py` once the workspace plan is upgraded.
