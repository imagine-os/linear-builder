---
identifier: "PAP-165"
title: "Build the virtualized grid view (TanStack Table) with inline edit, column resize/reorder, freeze and cell types"
project: "tables"
projectName: "Table & Views Engine"
phase: "P1"
type: "Build"
priority: 1
surfaces: ["Customer", "Staff"]
milestone: "Grid with sort, filter, group"
state: "Backlog"
parent: null
children: ["PAP-341", "PAP-342", "PAP-343"]
blockedBy: ["PAP-71", "PAP-151", "PAP-163", "PAP-164", "PAP-291", "PAP-337", "PAP-340"]
blocks: ["PAP-135", "PAP-166", "PAP-172", "PAP-173", "PAP-183", "PAP-189", "PAP-332", "PAP-333", "PAP-334", "PAP-386"]
key: "tables/grid-view"
url: "https://linear.app/paperos/issue/PAP-165/build-the-virtualized-grid-view-tanstack-table-with-inline-edit-column"
source: "Linear snapshot 2026-09-17T13:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T13:06:14.604Z"
---

# PAP-165: Build the virtualized grid view (TanStack Table) with inline edit, column resize/reorder, freeze and cell types

**Goal**

Build the workhorse grid view: virtualised, keyboard-first, inline-editable, with column resize, reorder, freeze, hide, density, grouping headers and aggregate footers, rendering any dataset through the compiler and field types, as fast as Airtable at 100k rows. Umbrella for three children.

**Scope**

Children (M each, same milestone, Backlog):

* PAP-341 Grid core: row and column virtualisation, `useViewQuery` binding, selection model, keyboard reducer, `role="grid"` semantics.
* PAP-342 Inline editing with optimistic commit, TSV clipboard in chunks, bulk actions bar.
* PAP-343 Column operations, grouping headers, aggregate footer, `RecordPanel`.

Out: filter, sort and group builders (PAP-166), sharing (PAP-172), formula editing (PAP-171), trash and restore (PAP-334), record detail routes (PAP-333).

**Spec**

Decisions binding all children:

* `@tanstack/react-table` 8.x, `@tanstack/react-virtual` 3.x; column and row reorder through `SortableList` (PAP-155) when merged, native pointer fallback otherwise; `fractional-indexing` for `sort_key`.
* Data via `useViewQuery`, page 100, prefetch within 30 rows of the end; collapsed groups persisted in `spec.groups[].collapsed`.
* Row heights 32, 40, 56, 88 px; widths 60 to 1200 px persisted through `onSpecChange` debounced 500 ms; frozen total capped at 60 percent of viewport.
* Edit opens on Enter, F2, double-click or a printable key; commit through `mutate(orpc.records.update, { optimistic })` (PAP-272), revert and toast on rejection.
* Commands `grid.*` registered in PAP-151; roving tabindex per PAP-153; `aria-rowindex`, `aria-colindex`, `aria-activedescendant`.
* Budgets: first paint under 300 ms for 100 rows; 60 fps scrolling with 30 columns at 1920 px.

**Interface contract**

Provides: `<GridView spec onSpecChange datasetRef embedded? onFilter? />`, `<RecordPanel recordId />`, hooks `useGridSelection`, `useGridKeyboard`, `useClipboardRange`, commands `grid.*`, `GridColumnMenu` slot for PAP-166 and the schema editor. Consumes: `useViewQuery` (PAP-163), `fieldTypes` (PAP-164), `EmptyState` and cells (PAP-71), `SortableList` (PAP-155), `defineCommand` (PAP-151), `mutate` (PAP-272), comments slot (PAP-131), `AuditTrail` (PAP-38). Consumed by PAP-166, PAP-172, PAP-173, PAP-179 journal, PAP-183 reports, PAP-189 contacts, PAP-135.

**Definition of done**

* All three children Done.
* Storybook `views/grid` with 10k rows; screenshots at 375, 768, 1024, 1440, 1920 in three themes and four densities; axe clean; NVDA and VoiceOver spot check.
* Performance trace attached meeting both budgets.
* `docs/views/grid.md` with keyboard map and extension points; CHANGELOG; Linear comment with demo link and video replay.

**Test plan**

Umbrella Playwright `grid.e2e.spec.ts` against the 100k seed: scroll to row 50,000 in under 2 s; edit a cell, reload, value persists; paste a 500-row TSV range and see chunked progress; resize, reorder, freeze a column and verify `spec.fields` after reload; group by status and collapse a group; open `RecordPanel` and edit from it; keyboard-only run of the same flow. Profiler assertion for 60 fps.

**Demo**

Reviewer opens the Pages demo `/demo/grid`, types into a cell and presses Enter, drags a column header, freezes it, pastes three rows from a spreadsheet and expands a row into the side panel. Under two minutes.

**Edge cases**

* 375 px: first column frozen, header menu becomes a bottom sheet.
* Row deleted by another user mid-edit: editor closes, toast, focus to next row (PAP-144).
* 5,000-row paste: batches of 200 with cancel.
* Null group header "(empty)" sorts last.
* Denied `update`: cells render, editors never open.

**Dependencies**

PAP-163 (hard), PAP-164 (hard), PAP-71 (hard), PAP-151 (hard), PAP-155 (soft, fallback reorder), PAP-36 children (soft, optimistic path). Blocks PAP-166, PAP-172, PAP-173, PAP-183, PAP-135, PAP-189.

**Agent**

Builder: Nova (Views Engineer). Reviewer: Sentinel (Code Reviewer, Visual Inspector, Edge Case Hunter).

**Size**

L, split into three M children.

**Pending issues**

Bracketed references above are fully specified work packages that Linear refused to create on 2026-09-17 (`USAGE_LIMIT_EXCEEDED`, free-plan issue cap). Their specs live in the project document(s) [tables](<https://linear.app/paperos/document/round-2-pending-issues-tables-24-86486d9b99cc>) and they are created as issues by `round2/agent4/create_issues.py` once the workspace plan is upgraded.
