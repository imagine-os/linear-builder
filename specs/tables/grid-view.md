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
children: []
blockedBy: ["PAP-151", "PAP-163", "PAP-164", "PAP-71"]
blocks: ["PAP-135", "PAP-166", "PAP-172", "PAP-173", "PAP-183", "PAP-189"]
key: "tables/grid-view"
url: "https://linear.app/paperos/issue/PAP-165/build-the-virtualized-grid-view-tanstack-table-with-inline-edit-column"
source: "plan/specs/bucket-6.json (round-1 canonical spec JSON)"
---

# PAP-165: Build the virtualized grid view (TanStack Table) with inline edit, column resize/reorder, freeze and cell types

**Goal**

Build the workhorse grid view: a virtualised, keyboard-first, inline-editable table on TanStack Table with column resize, reorder, freeze, hide, row density, grouping headers and aggregate footers, rendering any dataset through the query compiler and field types. It must feel as fast as Airtable at 100k rows.

**Scope**

In:
- `packages/views/src/views/grid/` exporting `<GridView spec onSpecChange datasetRef />` and the record side panel `<RecordPanel />`.
- Column header menu (sort, filter, group, hide, freeze, edit field, insert left/right, delete for custom datasets).
- Row selection, bulk actions bar (delete, duplicate, set field value), copy/paste of cell ranges as TSV.
- Add row, expand row, row reorder for custom datasets with a manual sort field.

Out: filter/sort/group builder panels (`tables/filter-sort-group-ui`, this issue exposes the hooks), sharing controls, formula editing.

**Spec**

- Libraries: `@tanstack/react-table` 8.x, `@tanstack/react-virtual` 3.x (rows and columns virtualised), `input/drag-drop` `SortableList` for column reorder and row reorder, `fractional-indexing` for `sort_key`.
- Data: `useViewQuery` from `tables/query-compiler`; page size 100; prefetch next page when the last rendered row is within 30 rows of the end; groups rendered as sticky headers with collapse state persisted in `spec.groups[].collapsed`.
- Layout: header sticky; frozen columns via `position: sticky` with a shadow when scrolled; row heights 32/40/56/88 px for the four `rowHeight` values; column widths from `spec.fields[].width` (min 60, max 1200), persisted through `onSpecChange` debounced 500 ms; resize handle 8 px hit area, double-click auto-fits from the visible rows.
- Cells: rendered via field type `Cell`; edit mode opens `Editor` on Enter, F2, double-click or typing a printable character; commit writes through `mutate(orpc.records.update, ..., { optimistic })` from `data-layer/local-first-sync`, reverting and toasting on rejection.
- Keyboard: arrow keys move the active cell; Shift+arrows extend range; Tab/Shift+Tab move across columns; Home/End, PageUp/PageDown, Ctrl+Home/End; Space toggles checkbox/selection; Delete clears; Ctrl+C/V copy and paste TSV ranges with per-field `parse`; Escape cancels. Commands registered in `input/command-registry` (`grid.*`) so keymaps and voice can invoke them. Roving tabindex per `input/focus-management`; grid uses `role="grid"` with `aria-rowindex/aria-colindex` and `aria-activedescendant`.
- Selection model: `{ anchor, focus }` ranges plus checkbox row selection; bulk bar shows count and actions; "Select all N matching" runs server-side actions by filter with a confirm dialog when N > 500.
- Record panel: opens on row expand or `/r/:id` search param; renders all fields as a form using field editors; shows comments slot for `collab/comments` and audit trail from `data-layer/audit-log`.
- Empty/error/offline states from `design-system/data-display` `EmptyState`; skeleton rows during first load.
- Performance budgets: first paint under 300 ms for 100 rows, 60 fps scrolling with 30 columns at 1920 px, measured with Playwright tracing in CI.

**Definition of done**

- Vitest for selection model, keyboard reducer, clipboard parsing; Playwright interaction tests for edit, resize, reorder, freeze and paste.
- Storybook story `views/grid` with 10k rows tagged `visual`; screenshots at 375, 768, 1024, 1440, 1920 across three themes and four densities.
- axe clean; screen reader announces row/column and edit state (NVDA and VoiceOver spot check per `input/screen-reader` checklist).
- Performance trace attached to the PR meeting the budgets.
- `docs/views/grid.md` covering keyboard map and extension points.
- CHANGELOG entry; Linear comment with Pages demo link and video replay from `quality/video-replays`.

**Edge cases**

- 375 px width: horizontal scroll with first column frozen, header menu becomes a bottom sheet.
- Row deleted by another user while being edited: editor closes, toast "record removed", focus moves to the next row (`realtime/conflict-ux`).
- Paste of 5,000 rows: chunk into batches of 200 mutations with progress and cancel.
- Column widths exceed viewport with frozen columns wider than viewport: cap frozen total at 60 percent.
- Group header for a null value labelled "(empty)" and sorts last.
- Read-only dataset or denied `update`: cells render but editors do not open, cursor indicates read-only.

**Dependencies**

- `tables/query-compiler`, `tables/field-types`, `design-system/data-display`, `input/drag-drop`, `input/command-registry`, `input/focus-management`, `data-layer/local-first-sync`.

**Agent**

Builder: Nova (Views Engineer). Reviewer: Sentinel (Code Reviewer, Visual Inspector, Edge Case Hunter).

**Size**

L: the most interaction-dense component in the platform; two to three sessions.
