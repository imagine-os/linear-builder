---
identifier: "PAP-213"
title: "Survey table, canvas, editor and chart libraries (TanStack, AG Grid, tldraw, Tiptap, ECharts, visx) and recommend"
project: "libraries"
projectName: "Library Discovery & Integration"
phase: "P0"
type: "Research"
priority: 2
surfaces: ["Developer"]
milestone: "Core adoptions decided"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-209"]
blocks: ["PAP-170"]
key: "libraries/data-landscape"
url: "https://linear.app/paperos/issue/PAP-213/survey-table-canvas-editor-and-chart-libraries-tanstack-ag-grid-tldraw"
source: "plan/specs/bucket-8.json (round-1 canonical spec JSON)"
---

# PAP-213: Survey table, canvas, editor and chart libraries (TanStack, AG Grid, tldraw, Tiptap, ECharts, visx) and recommend

**Goal**

Choose the data-heavy foundations of the platform: the table library the views engine renders with, the chart library dashboards use, the map library, and a shortlist for canvas and rich text that `collab/collab-research` decides in depth. Each choice is scored with the shared rubric and recorded as an ADR so `tables/grid-view`, `tables/map-chart-views` and `collab/canvas-view` build without re-litigating.

**Scope**

In:
- Tables: TanStack Table v8 + TanStack Virtual, AG Grid Community (MIT), Glide Data Grid (canvas-rendered), react-data-grid; Handsontable rejected on license.
- Charts: Apache ECharts 5/6, visx, Recharts, Observable Plot, Nivo, Chart.js; measured with the dataviz guidance Iris owns.
- Maps: MapLibre GL JS, Leaflet; tile source options (self-hosted Protomaps PMTiles vs OpenFreeMap).
- Canvas and editor breadth pass only: tldraw, React Flow (`@xyflow/react`), Excalidraw, Konva; Tiptap, BlockNote, Lexical, Plate. Output is a two-candidate shortlist per category handed to `collab/collab-research`, not a decision.
- Spikes under `spikes/data-libs/`: 100k-row virtualized grid with inline edit, column resize, frozen columns and grouping; 10k-point line chart plus a stacked bar with theme switching; a 5k-marker map.
- Three ADRs (table, charts, maps) and registry entries.

Out: building the views (`tables/*`), the field renderers (`design-system/data-display`), the final canvas and editor ADR (`collab/collab-research`), sync engine (`data-layer/sync-research`).

**Spec**

- Time-box 1.5 agent-days: tables 4 hours, charts 3 hours, maps 1.5 hours, canvas and editor shortlist 2 hours.
- Rubric extras for tables: headless vs rendered, virtualization quality at 100k rows (scroll FPS in Playwright trace), inline editing hooks, column pinning, grouping and aggregation primitives, server-side pagination hooks (`tables/query-compiler`), accessibility of grid semantics (`role=grid`, roving cell focus per `input/focus-management`), keyboard drag-and-drop compatibility with dnd-kit (`input/drag-drop`), touch behaviour.
- Rubric extras for charts: tree-shaken size for bar, line, pie, number; theming via CSS variables or theme object driven by `design-system/tokens`; SVG vs canvas (screenshot stability for `quality/playwright-matrix`); accessible descriptions and data tables fallback; large-data performance; dark mode.
- Rubric extras for maps: vector tiles, clustering, offline tiles in Tauri, license of tiles and styles, bundle size.
- Harness: Vite app with a route per candidate; Playwright records traces and screenshots at 375, 1024, 1920; results to `spikes/data-libs/results/*.json`; `pnpm lib score` renders tables.
- Cross-links required: `tables/feature-parity-audit` covers NocoDB and Baserow features, `libraries/oss-products` covers embedding them; this issue must reference both instead of repeating their analysis.
- Each ADR states the fallback candidate and a migration-cost estimate in hours.

**Definition of done**

- Spikes merged under `spikes/` with results JSON and generated comparison tables.
- Three ADRs accepted (table, charts, maps) with Nova and Atlas approval comments; the canvas and editor shortlist posted as a comment on `collab/collab-research`.
- Grid spike shows 100k rows at 55+ FPS scroll in a Playwright trace on the reference laptop profile; chart spike renders 10k points under 200 ms; screenshots at the three widths in light and dark attached.
- Registry entries for adopted and rejected libraries drafted.
- `tables/grid-view` and `tables/map-chart-views` descriptions updated with exact packages and versions.
- CHANGELOG entry; Linear comment linking ADRs and result tables.

**Edge cases**

- AG Grid Community lacks a feature the parity audit needs (row grouping is Enterprise): document the gap explicitly rather than assuming.
- Canvas-rendered grid (Glide) defeats screen readers and Playwright DOM snapshots: score a11y and testability down and note the vision-agent dependency.
- ECharts full bundle is large: measure the tree-shaken `echarts/core` path only.
- Map tiles require a paid key: prefer self-hosted PMTiles; record ops cost.
- Library upgrade in flight (TanStack Table v9 alpha): evaluate the stable major and note the timeline.
- Two candidates tie: apply the rubric tie rule using migration cost, not another spike.

**Dependencies**

`libraries/eval-rubric` (hard; use the draft if unmerged). Soft: `design-system/tokens` for theming tests, `data-layer/sync-research` for the sync engine the grid will bind to. Blocks `tables/grid-view`, `tables/map-chart-views`; informs `collab/collab-research`, `tables/view-model-spec`.

**Agent**

Researched by Scout (Library Evaluator) paired with Nova (Views Engineer) for the grid spike and Iris for chart theming. Reviewed by Nova and Atlas.

**Size**

L: three decisions with performance spikes across many candidates, even time-boxed.
