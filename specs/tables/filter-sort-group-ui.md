---
identifier: "PAP-166"
title: "Build the filter builder (AND/OR groups), multi-sort and multi-level grouping UI with aggregates"
project: "tables"
projectName: "Table & Views Engine"
phase: "P1"
type: "Build"
priority: 1
surfaces: ["Staff"]
milestone: "Grid with sort, filter, group"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-165", "PAP-233", "PAP-279"]
blocks: ["PAP-174", "PAP-195"]
key: "tables/filter-sort-group-ui"
url: "https://linear.app/paperos/issue/PAP-166/build-the-filter-builder-andor-groups-multi-sort-and-multi-level"
source: "plan/specs/bucket-6.json (round-1 canonical spec JSON)"
---

# PAP-166: Build the filter builder (AND/OR groups), multi-sort and multi-level grouping UI with aggregates

**Goal**

Give every view Airtable-class controls: a filter builder with nested AND/OR groups and per-type operators, a multi-sort editor, up to three levels of grouping with per-group aggregates, and a view toolbar that hosts them. The panels edit the `ViewSpec` and everything else re-renders through the compiler.

**Scope**

In:
- `packages/views/src/controls/`: `<ViewToolbar />`, `<FilterBuilder />`, `<SortEditor />`, `<GroupEditor />`, `<AggregateFooter />`, `<FieldVisibilityMenu />`, `<SearchBox />`.
- Relative date pickers, dynamic values (`currentUser`, `today`), quick filters (chips) for select and user fields.
- Aggregate selection per column footer and per group header.

Out: saved-view management (`tables/view-sharing`), formula fields in filters beyond their result type.

**Spec**

- Toolbar layout: left `[Views ▾] [Search]`, right `[Fields] [Filter n] [Sort n] [Group n] [Row height] [Share]`; each control shows a count badge when active; below 768 px it collapses to a single "Options" button opening a bottom sheet with tabs.
- `FilterBuilder` renders `spec.filter` as rows: `[field ▾] [op ▾] [value editor]`; a group renders indented with its own `and/or` toggle; "Add condition", "Add group" (max depth 5); drag handles reorder via `input/drag-drop`. Operators come from `fieldTypes[type].filterOps`; value editor comes from the field type `Editor` or a dedicated filter editor (`isWithin` shows unit and amount; relative anchors: `today, yesterday, tomorrow, oneWeekAgo, oneWeekFromNow, oneMonthAgo, oneMonthFromNow, startOfWeek, startOfMonth, exactDate`).
- Edits are applied optimistically to the spec after 300 ms debounce; the compiler query runs and the toolbar shows "n of N records" from `views.count`.
- `SortEditor`: ordered list `[field ▾] [A→Z | Z→A] [nulls last]`, drag to reorder, max 5 sorts; manual order option for custom datasets toggles the `sort_key` column.
- `GroupEditor`: up to 3 levels, each `[field ▾] [order]` and `expandMulti` toggle for multi-select; "collapse all / expand all"; per-level aggregate choice reused by group headers.
- `AggregateFooter`: per column dropdown with the type's allowed aggregations; results from `views.query` `aggregates`; currency aggregates render per-currency.
- Quick filters: select and user fields marked `quickFilter: true` in field options render as chips above the grid; multi-select of chips builds `isAnyOf`.
- Search: full-text over visible text fields via `spec.search`, debounced 300 ms; compiler uses `ILIKE` fallback until `data-layer/search` is wired, then `tsvector`.
- Permissions: users without `view.update` see controls but changes are "temporary" (kept in URL search params `?f=…&s=…&g=…` compressed with `lz-string`), with a "Save to view" button gated by permission.
- All controls are keyboard operable and register commands `view.filter.add`, `view.sort.add`, `view.group.add`, `view.search.focus` in `input/command-registry`.

**Definition of done**

- Vitest for spec reducers (add/remove/move condition, depth limit, URL round-trip).
- Playwright interaction tests: build a 3-level nested filter, reorder sorts, group by two fields, change aggregate, verify grid counts.
- Storybook stories for each control tagged `visual`; screenshots at 375, 768, 1024, 1440, 1920, three themes.
- axe clean; focus returns to the toolbar button when a panel closes.
- `docs/views/controls.md` with operator table per field type.
- CHANGELOG entry; Linear comment with demo link and video replay.

**Edge cases**

- Field removed while the panel is open: row shows "field deleted" and a remove button.
- Contradictory filters (`is empty` and `is not empty`) allowed, count shows 0, no error.
- Grouping by the same field twice is blocked in the picker.
- 40 quick-filter chips: overflow into a "+n" popover.
- URL temporary filters exceeding 2 KB: fall back to session storage with a warning.
- Screen reader: operator changes announce the new sentence form ("Status is any of Open, Blocked").

**Dependencies**

- `tables/grid-view` (hosts the toolbar), `tables/query-compiler` (count and aggregates), `tables/field-types` (operators, editors), `input/drag-drop`, `design-system/primitives` (Popover, Sheet, Combobox).

**Agent**

Builder: Nova (Views Engineer). Reviewer: Sentinel (Visual Inspector, Edge Case Hunter) and Iris for control styling.

**Size**

M: well-defined UI over existing primitives; one to two sessions.
