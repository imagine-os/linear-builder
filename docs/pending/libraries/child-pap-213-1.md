---
key: "child/PAP-213/1"
title: "Chart and map library spikes and ADRs: ECharts, visx, Recharts, Observable Plot, Nivo, Chart.js; MapLibre GL and Leaflet with self-hosted tiles"
project: "libraries"
parent: "PAP-213"
phase: "P0"
type: "Research"
priority: 2
size: "M"
surfaces: ["Developer"]
milestone: "Core adoptions decided"
intendedState: "Backlog"
blockedBy: []
blocks: []
source: "round2/agent5/pending-issues.json"
linearDocument: "https://linear.app/paperos/document/round-2-pending-issues-libraries-9-63c73eed632d"
status: "pending"
---

# Chart and map library spikes and ADRs: ECharts, visx, Recharts, Observable Plot, Nivo, Chart.js; MapLibre GL and Leaflet with self-hosted tiles

**Goal**

Decide the chart library dashboards use and the map library the map view uses, measured on theming from tokens, tree-shaken size, screenshot stability, accessibility fallbacks and large-data performance, and record two ADRs so `tables/map-chart-views` builds directly.

**Scope**

In: `spikes/data-libs/charts/` (10k-point line, stacked bar, pie, number tile with theme switch per candidate) and `spikes/data-libs/maps/` (5k clustered markers; MapLibre with Protomaps PMTiles versus OpenFreeMap tiles, Leaflet); scorecards with chart extras (tree-shaken size for four chart kinds, CSS-variable theming, SVG vs canvas for PAP-82 stability, accessible descriptions and data-table fallback, dark mode) and map extras (vector tiles, clustering, offline tiles in Tauri, tile licenses, bundle); ADRs for charts and maps; registry drafts. Time-box 4.5 hours.

Out: tables, canvas, editor (siblings); dashboard build (PAP-170, PAP-172).

**Spec**

* ECharts measured via `echarts/core` tree-shaken path only.
* Charts follow the dataviz guidance Iris owns (palette from tokens, accessible legends).
* Map tiles must not require a paid key; ops cost of PMTiles hosting recorded.

**Interface contract**

Provides: two ADRs with fallback and migration hours, `results/charts.json`, `results/maps.json`, registry entries, comments on PAP-170 with exact packages. Consumes: PAP-209 rubric, PAP-66 tokens, PAP-82 screenshot stability requirements.

**Definition of done**

* Chart winner renders 10k points under 200 ms in a committed trace; theme switch screenshots at 375, 1024, 1920 in light and dark.
* Map spike clusters 5k markers with self-hosted tiles offline in the Tauri shell or a minimal scaffold.
* ADRs accepted with Nova and Atlas approvals; PAP-170 description updated.

**Test plan**

* Playwright: render timing per candidate, screenshot diff stability across three runs (SVG vs canvas), axe with data-table fallback present.
* Bundle analysis per candidate committed.
* `pnpm lib score` validation of scorecards.

**Demo**

Reviewer runs `pnpm spike charts --lib echarts`, toggles dark mode and watches the chart re-theme from tokens, then opens the map route and pans a clustered 5k-marker map with local tiles. Under two minutes.

**Edge cases**

* Canvas charts produce nondeterministic screenshots: record and weigh against Gate 3.
* Library needs a global CSS import: scored under composability.
* Tile style license (ODbL attribution): recorded in the registry entry.

**Dependencies**

PAP-209 (hard; draft acceptable), PAP-66 (soft). Informs PAP-170, PAP-172.

**Agent**

Researched by Scout (Library Evaluator) with Iris for chart theming. Reviewed by Nova and Atlas.

**Size**

M
