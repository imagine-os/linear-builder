---
identifier: "PAP-618"
title: "ViewToolbar, SortEditor, GroupEditor, AggregateFooter picker, FieldVisibilityMenu, SearchBox and temporary URL view state"
project: "tables"
projectName: "Table & Views Engine"
phase: "P1"
type: "Build"
priority: 1
surfaces: ["Staff"]
milestone: "Grid with sort, filter, group"
state: "Backlog"
parent: "PAP-166"
children: []
blockedBy: ["PAP-343", "PAP-617", "PAP-662"]
blocks: ["PAP-172", "PAP-173", "PAP-174", "PAP-195", "PAP-390", "PAP-623", "PAP-839"]
key: "r4/tables/view-toolbar-sort-group-aggregates"
url: "https://linear.app/paperos/issue/PAP-618/viewtoolbar-sorteditor-groupeditor-aggregatefooter-picker"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:17.507Z"
model: "claude-sonnet-5"
effort: "high"
estimate: 3
dueDate: "2026-09-28"
cycle: null
---

# PAP-618: ViewToolbar, SortEditor, GroupEditor, AggregateFooter picker, FieldVisibilityMenu, SearchBox and temporary URL view state

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / high — Build M

**Goal**

Complete PAP-166: the toolbar every view kind hosts, with the sort, group, field-visibility and row-height controls, the aggregate picker for the footer, the search box and the temporary URL-held view state for people without `view.update`.

**Scope**

In: `packages/views/src/controls/{ViewToolbar,SortEditor,GroupEditor,AggregatePicker,FieldVisibilityMenu,RowHeightMenu,SearchBox}.tsx`; `useTempViewState()`; toolbar slot registration for `ViewHost`; commands `view.sort.add`, `view.group.add`, `view.search.focus`, `view.fields.toggle`.

Out: `FilterBuilder` (sibling), saved-view switcher and share button contents (PAP-172), automation and segment hosts.

**Spec**

* Toolbar layout: left `[Views] [Search]`, right `[Fields] [Filter n] [Sort n] [Group n] [Row height] [Share]`; under 768 px collapses to one "Options" bottom sheet with tabs; badge counts from the spec.
* `SortEditor`: max 5 sorts, per-row direction, nulls-last toggle, "manual order" option for custom datasets (uses `position`); `GroupEditor`: max 3 levels, `expandMulti` for multiSelect, per-level aggregate function, collapse-all.
* `AggregatePicker` lists `fieldTypes[type].aggregations` for the column and writes `spec.aggregations[fieldId]`; `FieldVisibilityMenu` toggles `fields[].visible`, drag reorders `fields[].order` (PAP-329), "hide all / show all", search.
* `SearchBox` writes `spec.search` over visible text fields (`ILIKE` until PAP-39, then `tsvector`), debounced 300 ms, `Escape` clears, `/` focuses via command.
* `useTempViewState()` layers `?f=&s=&g=&q=` over the saved spec for users without `view.update`; "Save to view" button appears only with permission; the count badge reads `views.count`.
* Toolbar registers into `ViewHost`'s `toolbarSlot` so every kind gets the same controls; kinds declare which controls they support (`supports.groups`).

**Interface contract**

Provides: the seven components, `useTempViewState`, toolbar slot fill, commands above, `ToolbarControl` extension type for other modules (PAP-172 adds Share). Consumes: `FilterBuilder` (sibling), grid column layout and footer (PAP-343), `views.count|groups` (PAP-337), `aggregations` per type (PAP-338), Popover, Sheet, Menu (PAP-237), drag (PAP-329), `ViewHost` slot (PAP-614, soft), search (PAP-39, soft). Consumed by PAP-172 and PAP-173.

**Definition of done**

* Playwright flows below green; Storybook per control at 375, 768, 1024, 1440, 1920 in three themes; axe clean.
* URL round trip and permission gating tested; `docs/views/controls.md` toolbar section; CHANGELOG; Linear comment with demo and replay.

**Test plan**

* Unit: sort and group reducers (limits, duplicates blocked, manual order only on custom datasets); aggregate options per type; URL codec; permission gating of Save.
* Integration: toolbar changes flow through `onSpecChange` and re-render the grid via the compiler with matching counts.
* E2E: sort by two fields, group by owner then status, change the footer to sum, hide three fields and reorder one, search, then reload as a viewer and confirm the URL state persists without a Save button; 375 px sheet variant; keyboard-only run.

**Demo**

Reviewer groups the demo grid by owner, adds a second sort, switches the budget footer to sum, searches "invoice" and watches the count badge update. Under two minutes.

**Edge cases**

* Group field archived: level removed with a toast, spec migrated.
* 40 quick chips overflow into a popover.
* URL over 2 KB falls back to session storage with a warning.
* Search on a dataset with no text fields: box disabled with tooltip.

**Dependencies**

PAP-617 (hard), PAP-343 (hard). Soft: PAP-329, PAP-39, PAP-614. Blocks PAP-172, PAP-173.

**Agent**

Builder: Nova (Views Engineer); Iris on control styling. Reviewer: Sentinel (Visual Inspector).

**Size**

M: one session.

*Round 4 critique fix (2026-09-18):* resolved 2 round-4 file keys in this description to Linear identifiers: `r4/tables/filter-builder-component` = PAP-617, `r4/tables/view-renderer-registry-and-host` = PAP-614.
