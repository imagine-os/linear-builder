---
identifier: "PAP-322"
title: "Filters, deep links, export and 300-node performance run"
project: "collab"
projectName: "In-App Collaboration & Knowledge"
phase: "P1"
type: "Build"
priority: 1
surfaces: ["Staff", "Developer"]
milestone: "Comments and canvas"
state: "Backlog"
parent: "PAP-132"
children: []
blockedBy: ["PAP-321"]
blocks: ["PAP-113", "PAP-157"]
key: "collab/canvas/filters-export-perf"
url: "https://linear.app/paperos/issue/PAP-322/filters-deep-links-export-and-300-node-performance-run"
source: "Linear snapshot 2026-09-17T15:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T13:42:26.083Z"
model: "claude-sonnet-5"
effort: "high"
---

# PAP-322: Filters, deep links, export and 300-node performance run

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / high — Build M

**Goal**

Finish the canvas view (PAP-132) as a usable tool: audience and surface filters, edge-kind toggles, search and focus, minimap, deep links, PNG and SVG export, a stale banner when specs changed, and measured 55 fps or better on a 300-node graph.

**Scope**

In:

* Route `/_app/dev/canvas` toolbar: audience filter, surface filter, edge kind toggles (`reads` hidden by default above 500 edges), search and focus node, fit view, minimap, reset layout, export.
* Deep link `?node=<id>&audience=<id>` restoring filter and focus; keyboard: arrows move selection, `Enter` opens spec, `/` search.
* Export via `html-to-image`: current viewport or selected region, capped at 8k pixels.
* Stale banner when `specHash` differs from the loaded graph with a reload action.
* Performance: `onlyRenderVisibleElements`, memoised nodes, edge simplification below zoom 0.4; CDP fps trace committed.
* Comment anchors on nodes (`canvas_node`) via PAP-131.

Out: pen tool (PAP-157), org chart (PAP-113).

**Spec**

* Filters compose (audience AND surface AND edge kinds); URL is the single source of filter state.
* 320 and 375 render read-only with a "larger screen recommended" notice.
* Export file name `<app>-canvas-<date>.png|svg`.

**Interface contract**

Exposes route, `CanvasToolbar`, `useCanvasFilters()` (URL-backed), `exportCanvas({ format, region })`, comment anchor `canvas:<canvasId>:<nodeId>`. Consumes siblings 1 and 2, `useThreads` (PAP-131), touch pan and pinch (PAP-154), thumbnails from PAP-82 when present.

**Definition of done**

* Filters, deep links, export and stale banner work; fps ≥ 55 on a generated 300-node graph with numbers in the comment.
* Screenshots at 768, 1024, 1280, 1536 and 1920 in light and dark; `docs/collab/canvas.md`; CHANGELOG entry.

**Test plan**

* Vitest: filter composition, URL round-trip, stale detection, export bounds clamp.
* Playwright: filter by audience and assert hidden nodes; open a deep link and assert focus; export PNG and assert non-empty file; mock a new `specHash` and assert the banner; run at 1280 and 1920, read-only notice at 375.
* Performance: CDP trace while panning 5 s on a 300/600 generated graph, mean fps ≥ 55.
* Visual: Gate 3 baselines at five widths, both themes.

**Demo**

Filter to customer pages, hide `reads` edges, search “Invoice” and focus it, copy the URL and open it in a new tab, export PNG. Under two minutes.

**Edge cases**

* Thousands of `reads` edges: hidden by default.
* 20k-pixel export: viewport or selection only.
* Deep link to a filtered-out node: filter widened with a notice.

**Dependencies**

Siblings 1 and 2 (hard). PAP-131, PAP-154, PAP-82 (soft).

**Agent**

Built by Nova (Canvas Cartographer). Reviewed by Sentinel (Visual Inspector, Code Reviewer).

**Size**

M: toolbar features plus the performance pass.
