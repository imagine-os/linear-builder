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
blockedBy: ["PAP-163", "PAP-213"]
blocks: ["PAP-173"]
key: "tables/map-chart-views"
url: "https://linear.app/paperos/issue/PAP-170/build-map-view-and-chart-view-bar-line-pie-number-bound-to-view"
source: "plan/specs/bucket-6.json (round-1 canonical spec JSON)"
---

# PAP-170: Build map view and chart view (bar, line, pie, number) bound to view aggregations

**Goal**

Add the two analytic views: a map view plotting records with coordinates on vector tiles, and a chart view (bar, line, area, pie, number/KPI) bound to the compiler's group and aggregate output. Both are the building blocks `tables/dashboard-blocks` arranges, so their props must be data-driven and cross-filter aware from day one.

**Scope**

In:
- `packages/views/src/views/map/` and `views/chart/`, plus a new `geo` field type `{ lat, lng, label? }` registered in `tables/field-types`.
- Chart options `{ chartType: 'bar'|'stackedBar'|'line'|'area'|'pie'|'donut'|'number', xField (group), seriesField?, yAggregate: { fieldId?, fn }, sortBy, limit, colorScheme, showLegend, showDataLabels, goal? }`.
- Map options `{ geoField, labelField?, colorField?, cluster: boolean, fitToData, basemap: 'light'|'dark'|'auto' }`.
- Click-to-filter events emitted as `onFilter(FilterCondition)` for dashboards.

Out: geocoding addresses (a follow-up using an integration connector), choropleths, custom tile hosting, drill-through beyond one level.

**Spec**

- Chart library: Apache ECharts 5.x imported per-chart (`echarts/core` with only needed renderers) to keep bundle under 250 KB gzip for the chart view; render into a `ResizeObserver`-driven container; theme built from design tokens at runtime (categorical palette from the `dataviz` skill's validated palette mapped onto `--pos-color-*` variables; sequential ramps for stacked series), regenerated on theme change.
- Data: `views.groups` provides x categories and aggregates; two-level grouping (`xField`, `seriesField`) yields series; `limit` caps categories (default 20, remainder bucketed into "Other"); number chart uses `views.query` aggregates with an optional comparison to the previous period when `xField` is a date bucket (`day|week|month|quarter|year` set in `options.bucket`).
- Formatting uses the field type `format` (currency in minor units, percent) for axes and tooltips; tooltips show category, series, value and count; data labels optional.
- Interaction: click a bar/slice emits `onFilter({ fieldId: xField, op: 'is', value })`; active filter highlights the element and dims others; legend toggles series; keyboard: Tab to chart, arrows move focus across categories with an accessible description, Enter filters. Provide `aria-label` summary and a "View as table" toggle rendering the same data in a grid (accessibility fallback).
- Map: MapLibre GL JS 4.x with vector tiles from OpenFreeMap (`https://tiles.openfreemap.org/styles/liberty`) and a config hook for self-hosted Protomaps PMTiles later; records loaded through the compiler with a bounding-box filter on `geo` (stored as jsonb; compiler adds `lat/lng` casts and a btree on both); clustering via MapLibre `cluster: true`, cluster click zooms; marker colour from `colorField` select colour; hover popup shows `labelField` and up to 3 fields; click opens the record panel; draw a rectangle (Shift+drag) to emit `onFilter` with `isWithin` bounds.
- Empty states: chart without a numeric aggregate defaults to count; map with no geo records shows an `EmptyState` with a "Add a location field" action.
- Export: PNG via ECharts `getDataURL` and MapLibre canvas `preserveDrawingBuffer`, and CSV of the aggregated data.

**Definition of done**

- Vitest for series shaping, "Other" bucketing, period comparison and bounds filter compilation.
- Playwright: click-to-filter round trip, legend toggle, map cluster zoom, rectangle select; WebGL enabled in the Playwright image.
- Storybook stories for each chart type and the map tagged `visual`; screenshots at 375, 768, 1024, 1440, 1920 in light, dark and high-contrast (palette contrast validated with the dataviz checker).
- Bundle size check in CI: chart chunk under 250 KB gzip, map chunk lazy-loaded.
- `docs/views/map-chart.md`; CHANGELOG entry; Linear comment with demo link.

**Edge cases**

- 10,000 points on the map: clustering on; above 50,000 the view asks the user to filter first.
- Negative values in a pie chart: refuse with a message and suggest bar.
- Mixed-currency sums: one series per currency, never summed.
- Date bucket with gaps: fill zero buckets so lines do not connect across missing months.
- Browsers without WebGL (some kiosks): map shows a static list with coordinates and an explanation.
- Colour-blind users: patterns/dashes for series in high-contrast theme, legend always includes text.

**Dependencies**

- `tables/query-compiler` (groups, aggregates, bounds filter), `tables/field-types` (geo type), `design-system/tokens` (palette), `design-system/theming` (runtime theme switch), `libraries/data-landscape` (ECharts choice confirmed via ADR).

**Agent**

Builder: Nova (Views Engineer) with Iris (dataviz plugin) on palette and chart styling. Reviewer: Sentinel (Visual Inspector, Code Reviewer).

**Size**

M: both views sit on mature libraries; the work is data binding, theming and interaction.
