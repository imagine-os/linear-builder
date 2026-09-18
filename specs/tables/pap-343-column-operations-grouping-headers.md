---
identifier: "PAP-343"
title: "Column operations, grouping headers, aggregate footer and RecordPanel"
project: "tables"
projectName: "Table & Views Engine"
phase: "P1"
type: "Build"
priority: 1
surfaces: ["Staff"]
milestone: "Grid with sort, filter, group"
state: "Backlog"
parent: "PAP-165"
children: []
blockedBy: ["PAP-342", "PAP-642"]
blocks: ["PAP-135", "PAP-166", "PAP-172", "PAP-173", "PAP-183", "PAP-189", "PAP-489", "PAP-617", "PAP-618", "PAP-623", "PAP-625", "PAP-626", "PAP-633"]
key: "tables/grid/columns-groups-panel"
url: "https://linear.app/paperos/issue/PAP-343/column-operations-grouping-headers-aggregate-footer-and-recordpanel"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:21:20.748Z"
model: "claude-sonnet-5"
effort: "high"
estimate: 3
dueDate: "2026-09-28"
cycle: null
---

# PAP-343: Column operations, grouping headers, aggregate footer and RecordPanel

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / high — Build M

**Goal**

Complete the grid with column resize, reorder, hide and freeze, sticky grouping headers with collapse, an aggregate footer and the record side panel.

**Scope**

In: `views/grid/{ColumnMenu,columns,GroupHeader,AggregateFooter,RecordPanel}.tsx`. Out: the filter, sort and group builders (PAP-166), record detail routes and history (PAP-333).

**Spec**

* Resize handle 8 px, double-click auto-fit; widths persisted via `onSpecChange` debounced 500 ms; reorder via `SortableList` (PAP-155) or pointer fallback; header menu: sort, filter, group, hide, freeze, edit field (opens `FieldSettingsPanel`), insert, delete for custom datasets.
* Group headers sticky with counts and per-level aggregates from `views.groups`; collapse persisted in `spec.groups[].collapsed`; "(empty)" last.
* `AggregateFooter` per column with the type's allowed functions.
* `RecordPanel` on row expand or `?r=<id>`: all fields as editors, comments slot (PAP-131), `AuditTrail` (PAP-38).

**Interface contract**

Provides: `ColumnMenu` slot API, `<RecordPanel recordId slots />`, `useColumnLayout`. Consumes: core child, `FieldSettingsPanel` (PAP-164 sibling), `views.groups` (PAP-163), `SortableList` (PAP-155), comments (PAP-131), audit (PAP-38).

**Definition of done**

* Playwright for resize, reorder, freeze, hide, group collapse, panel edit; screenshots at 375, 1024, 1920; axe clean.

**Test plan**

* Unit: width and order persistence reducer; group collapse state.
* E2E: the flows above plus `?r=` deep link.
* Visual: grouped grid with footer at three widths.

**Demo**

Group `/demo/grid` by status from the header menu, collapse a group, change the footer to sum, open a row in the panel.

**Edge cases**

* Auto-fit on 100k rows samples visible rows only; panel for a deleted record shows a removed state.

**Dependencies**

Core child (hard), PAP-163, PAP-155 (soft), PAP-131 and PAP-38 (soft slots).

**Agent**

Builder: Nova. Reviewer: Sentinel (Visual Inspector).

**Size**

M: one session.
