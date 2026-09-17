---
identifier: "PAP-170"
title: "Build map view and chart view (bar, line, pie, number) bound to view aggregations"
project: "tables"
projectName: "Table & Views Engine"
phase: "P2"
type: "Build"
priority: 2
surfaces: ["Staff"]
milestone: "All view types"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-163", "PAP-213", "PAP-294", "PAP-337"]
blocks: ["PAP-173", "PAP-386"]
key: "tables/map-chart-views"
url: "https://linear.app/paperos/issue/PAP-170/build-map-view-and-chart-view-bar-line-pie-number-bound-to-view"
source: "Linear snapshot 2026-09-17T13:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T13:05:34.130Z"
---

# PAP-170: Build map view and chart view (bar, line, pie, number) bound to view aggregations

**Goal**

Add the two analytic views: a map plotting records with coordinates on vector tiles and a chart view (bar, stacked bar, line, area, pie, donut, number) bound to compiler groups and aggregates. Both are the blocks PAP-173 arranges and must be data-driven and cross-filter aware from day one.

**Scope**

In: `packages/views/src/views/map/`, `views/chart/`, the `geo` field type `{ lat, lng, label? }` registered in PAP-164, chart and map options, `onFilter` emission, PNG and CSV export.

Out: geocoding, choropleths, custom tile hosting, drill-through beyond one level.

**Spec**

* Chart options `{ chartType, xField, seriesField?, yAggregate: { fieldId?, fn }, bucket?: 'day'|'week'|'month'|'quarter'|'year', sortBy, limit (default 20, remainder "Other"), colorScheme, showLegend, showDataLabels, goal? }`; map options `{ geoField, labelField?, colorField?, cluster, fitToData, basemap: 'light'|'dark'|'auto' }`.
* ECharts 5.x via `echarts/core` with only the needed renderers; chart chunk under 250 KB gzip; theme built at runtime from tokens using the dataviz palette mapped onto `--pos-color-*`, regenerated on theme change.
* Data from `views.groups` (one or two levels); number chart from `views.query` aggregates with previous-period comparison when `xField` is a date bucket; axes and tooltips format through the field type `format`.
* Click emits `onFilter({ fieldId: xField, op: 'is', value })`; active element highlighted; legend toggles series; keyboard: Tab to chart, arrows across categories, Enter filters; "View as table" fallback.
* MapLibre GL JS 4.x, OpenFreeMap `liberty` style with a hook for self-hosted PMTiles; bounding-box filter compiled on `geo` casts with btree indexes; `cluster: true`; Shift+drag rectangle emits `isWithin` bounds.
* Export: `getDataURL` and MapLibre canvas PNG; CSV of aggregated rows.

**Interface contract**

Provides: `<ChartView spec datasetRef onFilter activeFilter? />`, `<MapView />`, `buildSeries(groups, options)`, `buildEchartsTheme(tokens)`, `geo` field type, `FilterCondition` emission contract shared with PAP-173 and PAP-186. Consumes: groups and aggregates (PAP-163), `format` and field registry (PAP-164), tokens and theming (PAP-66, PAP-74), `EmptyState` (PAP-71), ECharts choice confirmed by PAP-213 ADR.

**Definition of done**

* Vitest, Playwright and bundle check below green; WebGL enabled in the Playwright image.
* Storybook stories per chart type and the map; screenshots at 375, 768, 1024, 1440, 1920 in light, dark and high-contrast; palette contrast validated with the dataviz checker.
* `docs/views/map-chart.md`; CHANGELOG; Linear comment with demo link.

**Test plan**

* Unit: series shaping for one and two levels, "Other" bucketing, zero-fill of date gaps, period comparison, bounds-filter compilation, per-currency series split.
* Integration: chart bound to a 50k-row seed renders from `views.groups` within 500 ms server time; map bounds query uses the btree index (`EXPLAIN`).
* E2E: click a bar and assert the emitted condition; legend toggle; cluster click zoom; rectangle select; keyboard category navigation; "View as table" shows identical totals.
* Bundle: `size-limit` chart chunk under 250 KB gzip; map chunk lazy.
* Visual: matrix above.

**Demo**

Reviewer opens `/demo/chart`, switches bar to stacked bar by owner, clicks a bar and sees the emitted filter chip, toggles "View as table", then opens `/demo/map`, clicks a cluster and Shift-drags a rectangle. Under two minutes.

**Edge cases**

* 10,000 points cluster; above 50,000 the view asks for a filter first.
* Negative values in a pie: refused with a bar suggestion.
* Mixed currencies: one series per currency.
* No WebGL (kiosks): static coordinate list with explanation.
* Colour-blind users: patterns in high-contrast, legend always textual.

**Dependencies**

PAP-163 (hard), PAP-164 (hard for `geo`), PAP-66, PAP-74, PAP-213 (ADR, soft). Blocks PAP-173, and through it PAP-186.

**Agent**

Builder: Nova (Views Engineer) with Iris (dataviz plugin) on palette. Reviewer: Sentinel (Visual Inspector, Code Reviewer).

**Size**

M: mature libraries; the work is binding, theming and interaction.
