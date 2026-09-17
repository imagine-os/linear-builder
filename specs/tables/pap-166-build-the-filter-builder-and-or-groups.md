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
blockedBy: ["PAP-165", "PAP-233", "PAP-279", "PAP-343"]
blocks: ["PAP-174", "PAP-195", "PAP-390"]
key: "tables/filter-sort-group-ui"
url: "https://linear.app/paperos/issue/PAP-166/build-the-filter-builder-andor-groups-multi-sort-and-multi-level"
source: "Linear snapshot 2026-09-17T15:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T13:41:43.463Z"
model: "claude-sonnet-5"
effort: "high"
---

# PAP-166: Build the filter builder (AND/OR groups), multi-sort and multi-level grouping UI with aggregates

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / high — Build M

**Goal**

Give every view Airtable-class controls: a filter builder with nested AND/OR groups and per-type operators, multi-sort, three-level grouping with per-group aggregates, quick-filter chips and a toolbar that hosts them. The panels edit `ViewSpec`; everything re-renders through the compiler.

**Scope**

In: `packages/views/src/controls/`: `ViewToolbar`, `FilterBuilder`, `SortEditor`, `GroupEditor`, `AggregateFooter`, `FieldVisibilityMenu`, `SearchBox`; relative date and dynamic value editors; temporary URL-held filters for users without `view.update`.

Out: saved-view management (PAP-172), grammar definition (PAP-279), formula fields beyond their result type.

**Spec**

* Toolbar: left `[Views] [Search]`, right `[Fields] [Filter n] [Sort n] [Group n] [Row height] [Share]`; under 768 px collapses to one "Options" bottom sheet with tabs.
* `FilterBuilder` renders `FilterTree` rows `[field] [op] [value]`; groups indent with their own and/or toggle; depth max 5; operators from `fieldTypes[type].filterOps`; relative anchors `today, yesterday, tomorrow, oneWeekAgo, oneWeekFromNow, oneMonthAgo, oneMonthFromNow, startOfWeek, startOfMonth, exactDate`; drag reorder via PAP-155.
* Edits apply after 300 ms debounce; toolbar shows "n of N records" from `views.count`.
* `SortEditor` max 5 sorts with nulls-last toggle and manual order for custom datasets; `GroupEditor` max 3 levels with `expandMulti` and per-level aggregate.
* Quick filters: fields with `options.quickFilter` render as chips building `isAnyOf`; overflow into "+n".
* Search: `spec.search` over visible text fields, `ILIKE` until PAP-39 lands, then `tsvector`.
* Temporary filters in `?f=&s=&g=` compressed with `lz-string`; "Save to view" gated by permission.
* Commands `view.filter.add`, `view.sort.add`, `view.group.add`, `view.search.focus`.

**Interface contract**

Provides: the seven components above, `useTempViewState()` for URL-held filters, `FilterBuilder` reused standalone by PAP-195 segments and PAP-174 conditions (`<FilterBuilder tree onChange fields extraOperators? />`). Consumes: `FilterTree` types and `describe()` sentence renderer (PAP-279), `filterOps` and editors (PAP-164), `views.count` (PAP-163), Popover, Sheet, Combobox (PAP-237, PAP-238), `SortableList` (PAP-155), commands (PAP-151). Host: `GridView` toolbar slot (PAP-165).

**Definition of done**

* Vitest for reducers and URL round trip; Playwright flows below green.
* Storybook stories per control; screenshots at 375, 768, 1024, 1440, 1920 in three themes; axe clean; focus returns to the toolbar button on close.
* `docs/views/controls.md` with the operator table per type; CHANGELOG; Linear comment with demo and replay.

**Test plan**

* Unit: add, remove, move, nest conditions; depth 6 rejected; duplicate group field blocked; `lz-string` round trip; sentence renderer snapshots.
* Integration: builder output compiles through PAP-163 for every operator of every type against a 1k-row seed and matches the in-memory oracle.
* E2E: build a three-level nested filter, reorder two sorts, group by two fields, change an aggregate, verify grid counts; repeat keyboard-only; 375 px bottom-sheet variant.
* Visual: the five widths, three themes, panels open and closed.

**Demo**

Reviewer opens the grid demo, adds "Status is any of Open, Blocked" and a nested "or" group, sorts by two fields, groups by owner, switches the footer aggregate to sum, and watches the count badge update. Under two minutes.

**Edge cases**

* Field deleted while the panel is open: row shows "field deleted" with remove.
* Contradictory filters allowed, count 0.
* 40 chips overflow into a popover.
* URL over 2 KB falls back to session storage with a warning.
* Screen reader announces the sentence form on operator change.

**Dependencies**

PAP-165 (hard), PAP-163, PAP-164, PAP-279 (hard), PAP-155 (soft), PAP-67 children. Blocks PAP-174, PAP-195.

**Agent**

Builder: Nova (Views Engineer). Reviewer: Sentinel (Visual Inspector, Edge Case Hunter); Iris on control styling.

**Size**

M: UI over existing primitives; one to two sessions.
