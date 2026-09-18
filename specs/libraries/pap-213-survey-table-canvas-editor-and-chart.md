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
children: ["PAP-293", "PAP-294", "PAP-292"]
blockedBy: ["PAP-209"]
blocks: ["PAP-170", "PAP-621"]
key: "libraries/data-landscape"
url: "https://linear.app/paperos/issue/PAP-213/survey-table-canvas-editor-and-chart-libraries-tanstack-ag-grid-tldraw"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T12:57:19.148Z"
model: null
effort: null
estimate: null
dueDate: "2026-09-24"
cycle: null
---

# PAP-213: Survey table, canvas, editor and chart libraries (TanStack, AG Grid, tldraw, Tiptap, ECharts, visx) and recommend

**Model / Effort:** set on children (umbrella is never claimed)

**Goal**

Choose the data-heavy foundations: the table library the views engine renders with, the chart and map libraries dashboards and map views use, and a shortlist for canvas and rich text that PAP-127 decides in depth. Each choice is rubric-scored and recorded as an ADR so PAP-165, PAP-170 and PAP-132 build without re-litigating. Umbrella for three work packages.

**Scope**

Work packages (full specs in the project document):

* **WP1 Table library** (M, 4 hours): TanStack Table v8 plus Virtual, AG Grid Community, Glide Data Grid, react-data-grid at 100k rows with inline edit, resize, frozen columns, grouping; extras for headless versus rendered, virtualization FPS, editing hooks, pinning, server-side pagination hooks for PAP-163, `role=grid` semantics per PAP-152, dnd-kit compatibility, touch; ADR. PAP-165 proceeds with TanStack Table v8 if this is not merged by 2026-09-21.
* **WP2 Charts and maps** (M, 4.5 hours): ECharts core path, visx, Recharts, Observable Plot, Nivo, Chart.js on a 10k-point line, stacked bar, pie and number tile with token theming; MapLibre GL with Protomaps PMTiles versus OpenFreeMap, Leaflet, on 5k clustered markers; two ADRs.
* **WP3 Canvas and editor shortlist** (S, 2 hours): tldraw, React Flow, Excalidraw, Konva; Tiptap, BlockNote, Lexical, Plate; facts-only pre-scores and license tiers; two candidates per category commented on PAP-127.

Out: building views (PAP-165, PAP-170), cell renderers (PAP-71), final canvas and editor ADR (PAP-127), sync engine (PAP-31).

**Spec**

* Harness: Vite app with a route per candidate under `spikes/data-libs/`; Playwright traces and screenshots at 375, 1024, 1920; results to `results/*.json`; `pnpm lib score` renders tables.
* Cross-links required to PAP-162 (NocoDB and Baserow features) and PAP-215 (embedding them); never repeat their analysis.
* Every ADR states the fallback candidate and migration hours; ties resolved by the rubric tie rule.
* Order WP1 -> WP2 -> WP3 on `PAP-213/wp<n>-<slug>`; total time-box 1.5 agent-days.

**Interface contract**

Provides: ADRs `table-library`, `chart-library`, `map-library` with exact packages and versions, `results/{tables,charts,maps,shortlist}.json`, registry drafts, comments on PAP-165, PAP-163, PAP-170, PAP-172, PAP-127 with the decisions. Consumes: PAP-209 rubric and `pnpm lib score` (draft acceptable), PAP-66 tokens (soft), PAP-211 tiers, PAP-162 and PAP-188 findings by link, PAP-82 screenshot stability requirements.

**Definition of done**

* Three work packages merged and reported.
* Integration check: grid winner at 55+ FPS scrolling 100k rows in a committed Playwright trace on the CI profile; chart winner renders 10k points under 200 ms; map spike clusters 5k markers with self-hosted tiles offline.
* Three ADRs accepted with Nova and Atlas approval comments; shortlist commented on PAP-127.
* Screenshots at 375, 1024, 1920 in light and dark for grid, charts and map.
* PAP-165 and PAP-170 descriptions updated; registry drafts; CHANGELOG; Linear comment linking ADRs and tables.

**Test plan**

* Playwright per candidate: scroll trace and FPS extraction, inline edit, resize, pin, group; chart render timing and three-run screenshot stability; map cluster and pan; axe with data-table fallback for charts.
* Bundle analysis per route committed.
* `pnpm lib score` validates every scorecard; a Vitest lint asserts the shortlist has two candidates per category.

**Demo**

Reviewer opens the table ADR and its comparison table, runs `pnpm spike tables --lib tanstack` to scroll 100k rows while editing a cell, then toggles dark mode on the chart route and sees the chart re-theme from tokens. Under two minutes.

**Edge cases**

* AG Grid Community lacks row grouping (Enterprise): documented gap, not assumed.
* Canvas-rendered grid defeats screen readers and DOM snapshots: a11y and testability scored down.
* ECharts full bundle: measure `echarts/core` only.
* Paid tile keys: prefer PMTiles; record ops cost.
* TanStack Table v9 alpha: evaluate v8 stable.
* Tie: migration-cost rule, no second spike.

**Dependencies**

PAP-209 (hard; draft acceptable). Soft: PAP-66, PAP-31, PAP-162, PAP-211. Blocks PAP-170 (map and chart views); informs PAP-165 (default TanStack after 2026-09-21), PAP-163, PAP-127, PAP-161.

**Agent**

Researched by Scout (Library Evaluator) paired with Nova (Views Engineer) for the grid and Iris for chart theming. Reviewed by Nova and Atlas.

**Size**

L umbrella; two M and one S work package. Pending sub-issue specs: [Round 2 pending issues: libraries (9)](https://linear.app/paperos/document/round-2-pending-issues-libraries-9-63c73eed632d)
