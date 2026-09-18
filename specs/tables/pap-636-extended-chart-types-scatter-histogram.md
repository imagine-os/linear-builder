---
identifier: "PAP-636"
title: "Extended chart types: scatter, histogram, funnel, gauge, heatmap and combo bar-line with shared series builder"
project: "tables"
projectName: "Table & Views Engine"
phase: "P2"
type: "Build"
priority: 4
surfaces: ["Staff"]
milestone: "All view types"
state: "Backlog"
parent: "PAP-170"
children: []
blockedBy: ["PAP-621"]
blocks: []
key: "r4/tables/extended-chart-types"
url: "https://linear.app/paperos/issue/PAP-636/extended-chart-types-scatter-histogram-funnel-gauge-heatmap-and-combo"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:30:21.427Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 2
dueDate: null
cycle: null
---

# PAP-636: Extended chart types: scatter, histogram, funnel, gauge, heatmap and combo bar-line with shared series builder

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Build S

**Goal**

Deferred to v0.2 (NJ-19; reinstate via NJ-14). ClickUp, Monday and Airtable dashboards offer scatter, funnel, gauge and heatmap widgets beyond bars and lines. Extend the chart view with six more types on the same series builder and theme.

**Scope**

In: `views/chart/types/{scatter,histogram,funnel,gauge,heatmap,combo}.ts`; options additions `{ yField2?, bins?, stages?, min, max, thresholds? }`; ECharts modules added lazily; stories.

Out: 3D charts, geographic charts (map view), custom ECharts option passthrough.

**Spec**

* `scatter`: two number fields per record (no aggregation, cap 5,000 points, sample with note); `histogram`: `bins` over a number field compiled as `width_bucket` in PAP-336; `funnel`: ordered `stages` from a select field's option order with conversion percentages; `gauge`: single aggregate against `min|max|thresholds`; `heatmap`: two group fields with a `sum|count` intensity and a sequential dataviz palette; `combo`: bars for `yAggregate` and a line for `yField2` aggregate on a second axis.
* All types emit `onFilter` on click where an axis maps to a field; keyboard navigation per category as in the base issue; `View as table` fallback for each.
* Chunk budget: each type is a separate `import()` so the base chart chunk stays under 250 KB.

**Interface contract**

Provides: six chart types registered into `chartTypes`, `histogramBins(field, bins)` compiler helper, sequential palette usage contract. Consumes: chart base (PAP-621), compiler aggregates (PAP-336), dataviz tokens (design-system).

**Definition of done**

* Six types with stories at 375, 1024, 1920 in three themes; palette contrast validated; `size-limit` per chunk; `docs/views/chart.md` updated; CHANGELOG.

**Test plan**

* Unit: bins compilation; funnel ordering and percentages; gauge thresholds; heatmap matrix; combo dual axis.
* Integration: histogram over 100k rows via `width_bucket` under 300 ms.
* E2E: switch a chart through all six types, click a funnel stage and see the filter chip.

**Demo**

Reviewer turns the demo chart into a funnel by status and a heatmap of client by month. Under two minutes.

**Edge cases**

* Funnel with stages missing records: zero bars kept for order.
* Heatmap over 50 by 50 cells: labels thinned.

**Dependencies**

PAP-621 (hard). Deferred; nothing waits on it.

**Agent**

Builder: Nova (Views Engineer). Reviewer: Sentinel (Visual Inspector).

**Size**

S: half a session.

*Round 4 critique fix (2026-09-18):* resolved 1 round-4 file key in this description to Linear identifiers: `r4/tables/chart-view-echarts` = PAP-621.
