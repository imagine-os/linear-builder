---
identifier: "PAP-621"
title: "Chart view on ECharts: bar, stacked bar, line, area, pie, donut and number bound to views.groups with onFilter emission and table fallback"
project: "tables"
projectName: "Table & Views Engine"
phase: "P2"
type: "Build"
priority: 2
surfaces: ["Staff"]
milestone: "All view types"
state: "Backlog"
parent: "PAP-170"
children: []
blockedBy: ["PAP-163", "PAP-213", "PAP-293", "PAP-294", "PAP-337", "PAP-614", "PAP-615", "PAP-665"]
blocks: ["PAP-386", "PAP-622", "PAP-635", "PAP-636"]
key: "r4/tables/chart-view-echarts"
url: "https://linear.app/paperos/issue/PAP-621/chart-view-on-echarts-bar-stacked-bar-line-area-pie-donut-and-number"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:18.531Z"
model: "claude-sonnet-5"
effort: "high"
estimate: 3
dueDate: "2026-09-29"
cycle: null
---

# PAP-621: Chart view on ECharts: bar, stacked bar, line, area, pie, donut and number bound to views.groups with onFilter emission and table fallback

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / high — Build M

**Goal**

Chart half of PAP-170: the analytic view every dashboard block and finance report needs, bound to compiler groups and aggregates, themed from tokens, keyboard-operable and cross-filter aware from day one.

**Scope**

In: `packages/views/src/views/chart/{ChartView,series,theme,register}.tsx`; chart options schema; `buildSeries`, `buildEchartsTheme(tokens)`; PNG and CSV export; "View as table" fallback; Storybook per chart type.

Out: map view and `geo` type (sibling), extended chart types (PAP-636), dashboard block chrome (PAP-386), sparkline micro-charts (design-system dataviz issue).

**Spec**

* Options `{ chartType: 'bar'|'stackedBar'|'line'|'area'|'pie'|'donut'|'number', xField, seriesField?, yAggregate: { fieldId?, fn }, bucket?: 'day'|'week'|'month'|'quarter'|'year', sortBy: 'x'|'y', limit (default 20, remainder "Other"), colorScheme, showLegend, showDataLabels, goal? }`.
* ECharts 5.x via `echarts/core` importing only `BarChart, LineChart, PieChart, GridComponent, TooltipComponent, LegendComponent, CanvasRenderer`; chart chunk under 250 KB gzip (`size-limit`); theme built at runtime from `--pos-color-dataviz-*` tokens (design-system dataviz issue; interim mapping from `--pos-color-*` ramps) and rebuilt on `theme.changed`.
* Data from `views.groups` (one or two levels) with date bucketing compiled in PAP-336; zero-fill of missing buckets; `number` reads `views.query` aggregates with previous-period comparison when `xField` is a date bucket; axes and tooltips format through the field type `format` (currency per series).
* Click emits `onFilter({ fieldId: xField, op: 'is', value })`; active element highlighted; legend toggles series; keyboard: Tab to chart, arrows across categories, Enter filters, `aria-label` summarises min, max and total; "View as table" renders the same aggregates in a static table.
* Export: `getDataURL` PNG at 2x and CSV of aggregated rows; registered as `kind: 'chart'` with `requiredFieldTypes: []`, `supports: { onFilter: true, embedded: true, print: true }`.

**Interface contract**

Provides: `<ChartView spec datasetRef onFilter activeFilter? />`, `buildSeries(groups, options)`, `buildEchartsTheme(tokens)`, `chartOptionsSchema`, `FilterCondition` emission contract shared with PAP-386 and PAP-186, `exportChartPng|Csv`. Consumes: `views.groups|query` (PAP-337), date bucketing (PAP-336), `format` (PAP-338), tokens (PAP-66), theme change event (PAP-75), `ViewHost` registry, ECharts ADR (PAP-293), `EmptyState` (PAP-71). Consumed by PAP-386, PAP-183, PAP-186.

**Definition of done**

* Vitest, Playwright and `size-limit` green; WebGL not required; stories per type at 375, 768, 1024, 1440, 1920 in light, dark and high contrast; palette contrast validated with the dataviz checker.
* `docs/views/chart.md`; CHANGELOG; Linear comment with `/demo/chart`.

**Test plan**

* Unit: series shaping for one and two levels; "Other" bucketing; zero-fill of date gaps; period comparison; per-currency series split; theme mapping.
* Integration: chart bound to the 50k-row seed renders from `views.groups` within 500 ms server time; bundle check.
* E2E: switch bar to stacked bar by owner, click a bar and assert the emitted condition, toggle the legend, open "View as table" and compare totals; keyboard category navigation; number chart shows a delta.

**Demo**

Reviewer opens `/demo/chart`, buckets by month, stacks by status, clicks a bar and sees the filter chip, then exports PNG. Under two minutes.

**Edge cases**

* Negative values in a pie: refused with a bar suggestion.
* Mixed currencies: one series per currency, never summed blindly.
* 10k distinct x values: top 20 plus "Other" with a note.
* Colour-blind users: patterns in high contrast, legend always textual.
* Reduced motion: no entry animation.

**Dependencies**

PAP-337 (hard), PAP-293 (hard, ECharts ADR; default ECharts if not merged by 09-26), PAP-614 (hard). Soft: PAP-66, PAP-75, design-system dataviz tokens. Blocks PAP-386 and the map sibling (shared export and registration helpers).

**Agent**

Builder: Nova (Views Engineer) with Iris (dataviz palette). Reviewer: Sentinel (Visual Inspector, Code Reviewer).

**Size**

M: one session.

*Round 4 critique fix (2026-09-18):* resolved 2 round-4 file keys in this description to Linear identifiers: `r4/tables/extended-chart-types` = PAP-636, `r4/tables/view-renderer-registry-and-host` = PAP-614.
