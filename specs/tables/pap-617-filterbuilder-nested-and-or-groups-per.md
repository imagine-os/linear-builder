---
identifier: "PAP-617"
title: "FilterBuilder: nested AND/OR groups, per-type operators, relative dates, dynamic values and the sentence renderer, reusable by segments and automations"
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
blockedBy: ["PAP-165", "PAP-233", "PAP-279", "PAP-343", "PAP-630", "PAP-659", "PAP-660"]
blocks: ["PAP-174", "PAP-195", "PAP-390", "PAP-618", "PAP-626"]
key: "r4/tables/filter-builder-component"
url: "https://linear.app/paperos/issue/PAP-617/filterbuilder-nested-andor-groups-per-type-operators-relative-dates"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:17.352Z"
model: "claude-opus-5"
effort: "high"
estimate: 3
dueDate: "2026-09-28"
cycle: null
---

# PAP-617: FilterBuilder: nested AND/OR groups, per-type operators, relative dates, dynamic values and the sentence renderer, reusable by segments and automations

**Model / Effort:** Opus 5 (`claude-opus-5`) / high — Build M

**Goal**

Split PAP-166 so the zero-slack chain (PAP-163 → 165 → 166 → 173/174) gets its widest-consumed component first: the standalone `FilterBuilder` that edits a `FilterTree` for views, segments (PAP-195) and automation conditions (PAP-174), with per-type operators from the field registry, relative-date and dynamic-value editors and a screen-reader sentence renderer.

**Scope**

In: `packages/views/src/controls/filter/{FilterBuilder,ConditionRow,GroupRow,ValueEditor,RelativeDateEditor,sentence}.tsx`; `useFilterTreeReducer`; quick-filter chips; URL compression helper `encodeTempFilter` with `lz-string`.

Out: toolbar, sort, group and aggregate editors (sibling PAP-618), grammar (PAP-279), saved views (PAP-172).

**Spec**

* Renders `FilterTree` rows `[field] [op] [value]`; groups indent with their own and/or toggle; depth max 5; operators from `fieldTypes[type].filterOps` (PAP-338) plus `extraOperators` prop for hosts.
* Value editors by type: text input, number, currency with code, date with `RelativeDatePicker` (PAP-233) emitting `{ kind: 'relative', unit, amount, anchor }`, select and multiSelect via Combobox with option colours, user picker with `{ ref: 'currentUser' }`, relation picker searching the target dataset, checkbox tri-state, empty/not-empty need no value.
* Reducer actions `add|remove|move|nest|unnest|setField|setOp|setValue|toggleConjunction`; changing a field resets op to the first valid op and clears an incompatible value; edits debounced 300 ms before `onChange`.
* Drag reorder through `SortableList` (PAP-329) with keyboard fallback (PAP-330); every row has a remove button and an accessible name from `describe(tree)` (PAP-279).
* Quick filters: fields with `options.quickFilter` render as chips building `isAnyOf`; overflow into "+n".
* `encodeTempFilter(tree)` produces the `?f=` param under 2 KB, else falls back to session storage with a warning.

**Interface contract**

Provides: `<FilterBuilder tree onChange fields extraOperators? maxDepth? compact? />`, `useFilterTreeReducer`, `<QuickFilterChips />`, `encodeTempFilter|decodeTempFilter`, `<RelativeDateEditor />`. Consumes: `FilterTree`, `describe()` and in-memory evaluator (PAP-279), `filterOps` and editors (PAP-338, PAP-339, PAP-340), `RelativeDatePicker` (PAP-233), Popover, Combobox (PAP-237, PAP-238), drag (PAP-329, PAP-330). Host: grid toolbar (PAP-343 `ColumnMenu` filter entry). Consumed by PAP-195 segments, PAP-174 conditions (PAP-390 builder), PAP-172 share dialog preview.

**Definition of done**

* Vitest and Playwright below green; Storybook stories (empty, nested, every value editor) at 375, 768, 1280 in three themes; axe clean; focus returns to the trigger on close.
* Builder output compiles through PAP-335 for every operator of every type against the 1k-row seed and matches the oracle.
* `docs/views/controls.md` operator table generated from the registry; CHANGELOG; Linear comment on PAP-195 and PAP-390 with the props.

**Test plan**

* Unit: reducer transitions; depth 6 rejected; field change resets op and value; relative date payload shape; `lz-string` round trip; sentence snapshots for ten trees.
* Integration: every `(type, op)` pair from the registry produces a tree that compiles and returns the oracle's row set.
* E2E: build a three-level nested filter with a relative date and a `currentUser` condition, reorder two rows by keyboard, verify the grid count; 375 px sheet variant.

**Demo**

Reviewer adds "Status is any of Open, Blocked", nests an "or" group with "Due is within next 7 days" and "Owner is me", reorders with the keyboard and hears the sentence announced. Under two minutes.

**Edge cases**

* Field deleted while open: row shows "field deleted" with remove; tree stays valid with `orphaned`.
* Contradictory filters allowed, count 0 shown by the host.
* Formula field: ops from its result type; `#ERROR` rows never match.
* RTL: indentation and drag semantics flip.

**Dependencies**

PAP-343 (hard, host menu), PAP-279 (hard), PAP-233 (hard, relative dates). Soft: PAP-329, PAP-330. Blocks the toolbar sibling, PAP-174, PAP-390, PAP-195.

**Agent**

Builder: Nova (Views Engineer). Reviewer: Sentinel (Edge Case Hunter, Visual Inspector).

**Size**

M: one session.

*Round 4 critique fix (2026-09-18):* resolved 1 round-4 file key in this description to Linear identifiers: `r4/tables/view-toolbar-sort-group-aggregates` = PAP-618.
