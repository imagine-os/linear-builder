---
identifier: "PAP-635"
title: "Pivot summary view: rows and columns from two group fields, aggregate cells, totals, drill-through and CSV export"
project: "tables"
projectName: "Table & Views Engine"
phase: "P2"
type: "Build"
priority: 4
surfaces: ["Staff"]
milestone: "View sharing, formulas, dashboards"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-336", "PAP-621"]
blocks: []
key: "r4/tables/pivot-summary-view"
url: "https://linear.app/paperos/issue/PAP-635/pivot-summary-view-rows-and-columns-from-two-group-fields-aggregate"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:20.554Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 3
dueDate: null
cycle: null
---

# PAP-635: Pivot summary view: rows and columns from two group fields, aggregate cells, totals, drill-through and CSV export

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Build M

**Goal**

Deferred to v0.2 (NJ-19; reinstate via NJ-14). Airtable's Pivot extension, Coda and Smartsheet summaries and every spreadsheet pivot are the fastest way to see revenue by client by month. Build a pivot view kind on the compiler's two-level groups with aggregate cells and drill-through.

**Scope**

In: `views/pivot/{PivotView,register}.tsx`; options `{ rowField, columnField?, bucket?, values: { fieldId?, fn }[] (max 3), showTotals, sortBy }`; sticky row and column headers; drill-through emits `onFilter` for both axes; CSV export via the export issue.

Out: nested row fields beyond two levels, calculated pivot fields, charting (use chart view).

**Spec**

* Data from `views.groups` level 1 (rows) and level 2 (columns) with all `values` aggregates in one query per row page (page 100 rows, 50 columns with "Other"); date `bucket` shares PAP-336 compilation; totals row and column from a separate aggregate query.
* Cells format through the field type (currency per currency: one cell per currency stacked); empty cells render an em dash; clicking a cell emits `onFilter([{ rowField is x }, { columnField is y }])` so a grid block lists the underlying records.
* Keyboard: grid navigation reusing PAP-341's reducer over a static grid; `aria-rowindex|colindex`; copy a range as TSV (PAP-342 clipboard).
* Registered as `kind: 'pivot'` with `supports: { onFilter, embedded, print }`; column count above 200 asks for a filter.

**Interface contract**

Provides: `<PivotView />`, `pivotOptionsSchema`, registration, `buildPivotMatrix(groups)`. Consumes: groups and aggregates (PAP-336), export writers (PAP-625), chart sibling's registration helpers, grid reducer (PAP-341), clipboard (PAP-342).

**Definition of done**

* Pivot green in Vitest and Playwright; screenshots at 768, 1024, 1920 in three themes; axe clean; `docs/views/pivot.md`; CHANGELOG.

**Test plan**

* Unit: matrix building with sparse columns; totals; per-currency stacking; "Other" column.
* Integration: budget by client by month over the 100k seed under 500 ms server time.
* E2E: pivot budget by client by month, click a cell and see the grid block filter, export CSV.

**Demo**

Reviewer builds Budget by Client by Quarter, clicks a cell to drill through, exports. Under two minutes.

**Edge cases**

* Row field with 10k distinct values: paginated rows.
* Column bucket week with ISO week start per tenant setting.

**Dependencies**

PAP-336 (hard), PAP-621 (hard). Deferred; nothing waits on it.

**Agent**

Builder: Nova (Views Engineer). Reviewer: Sentinel (Visual Inspector).

**Size**

M: one session.

*Round 4 critique fix (2026-09-18):* resolved 2 round-4 file keys in this description to Linear identifiers: `r4/tables/chart-view-echarts` = PAP-621, `r4/tables/view-export-csv-xlsx-ics-print` = PAP-625.
