---
identifier: "PAP-167"
title: "Build the kanban board view with swimlanes, WIP limits and drag-and-drop"
project: "tables"
projectName: "Table & Views Engine"
phase: "P1"
type: "Build"
priority: 1
surfaces: ["Staff"]
milestone: "All view types"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-155", "PAP-163"]
blocks: ["PAP-102", "PAP-189"]
key: "tables/kanban-view"
url: "https://linear.app/paperos/issue/PAP-167/build-the-kanban-board-view-with-swimlanes-wip-limits-and-drag-and"
source: "plan/specs/bucket-6.json (round-1 canonical spec JSON)"
---

# PAP-167: Build the kanban board view with swimlanes, WIP limits and drag-and-drop

**Goal**

Build the kanban board view so any dataset with a select, status or user field can be worked as a board: columns per group value, optional swimlanes by a second field, WIP limits, accessible drag-and-drop between and within columns, card templates and inline card creation. PM boards (`pm-linear/board-views`) and CRM pipelines (`growth/crm-views`) are the first consumers.

**Scope**

In:
- `packages/views/src/views/kanban/`: `<KanbanView spec onSpecChange datasetRef />`, `<KanbanColumn />`, `<KanbanCard />`, `<CardTemplateEditor />`.
- Kanban options in `ViewSpec.options`: `{ groupField, swimlaneField?, wipLimits: Record<optionId, number>, cardFields: fieldId[], coverField?, colorField?, hideEmptyColumns, collapsedColumns: optionId[], columnOrder?: optionId[] }`.
- Column-level aggregates (count and one numeric sum) in the header.

Out: Gantt/time (`tables/calendar-timeline-gantt`), automation on move (future), swimlane by relation (v2).

**Spec**

- Group field must be `select`, `user` or a relation with `limitOne`; the picker only offers those. Columns come from `views.groups` level 1 with counts; card pages per column via `views.query` with `groupPath`, page size 50 and "Load more" at the column end; the column virtualises cards with `@tanstack/react-virtual`.
- Swimlanes: when `swimlaneField` set, rows per lane value with collapsible lane headers; each cell is a column-lane intersection with its own pagination.
- Drag-and-drop uses `input/drag-drop` (`SortableList` across containers with `canDrop`); dropping into a column writes `{ [groupField]: optionId }` plus `sort_key` via `between()` for custom datasets; for entity datasets with no manual order, position within column is by the view's sort and drop only changes the group value (UI shows a "sorted by X" hint). Moves are optimistic and revert with a toast on rejection.
- WIP limit: header shows `n / limit`, turns warning colour at limit and danger above; `canDrop` returns `{ reason: 'WIP limit reached' }` when a limit would be exceeded unless the user holds Alt (override, audited in the update reason).
- Card: title field (first text field or dataset `titleField`), up to 6 `cardFields` rendered with type cells at `compact` density, cover from an attachment field, left colour bar from `colorField` (select colour), avatar stack for user fields, comment count badge slot for `collab/comments`.
- Inline add: "+ New" at column bottom opens a title input that creates the record with the column's group value; Enter creates and keeps adding, Escape cancels.
- Column ops menu: collapse, hide, set WIP limit, rename option (writes to field options if allowed), sort cards within column by a field.
- Empty column value column "(no value)" always first unless hidden; drop into it clears the field.
- Keyboard: focus a card, Space picks up, arrows move across cards and columns, Space drops, Escape cancels; announcements via `LiveAnnouncer`. Commands `kanban.*` registered.
- Responsive: under 768 px columns become horizontally snapping panes one per viewport with a column pager; under 1024 px card fields are limited to 3.

**Definition of done**

- Vitest for move reducer, WIP evaluation and template config.
- Playwright: drag card between columns, keyboard move, WIP block, inline add, swimlane collapse; runs against seed of 2,000 records across 8 columns.
- Storybook story tagged `visual`; screenshots at 375, 768, 1024, 1440, 1920 in three themes; video replay of a drag flow at each width.
- 60 fps drag verified with the Profiler assertion pattern from `input/drag-drop`.
- `docs/views/kanban.md`; CHANGELOG entry; Linear comment with demo link.

**Edge cases**

- Group field with 200 options: columns virtualised horizontally, hidden by default beyond the first 30 with "Show all".
- Two users move the same card simultaneously: last write wins by server timestamp, the loser's card animates to its actual column (`realtime/record-sync`).
- Card moved into a column the user cannot write (permission condition on status): `canDrop` denied with reason from `decision.explain()`.
- Column option deleted while board open: cards move to "(no value)" after refetch, toast explains.
- Very long titles wrap to 3 lines then truncate with tooltip.
- Offline: moves queue in the offline outbox and cards show a pending badge.

**Dependencies**

- `tables/query-compiler`, `tables/field-types`, `input/drag-drop`, `design-system/data-display` (AvatarStack, Badge), `realtime/record-sync` for live updates (optional at first).

**Agent**

Builder: Nova (Views Engineer). Reviewer: Sentinel (Visual Inspector, Edge Case Hunter); Iris on card design.

**Size**

M: drag infrastructure exists; the work is board semantics, pagination per column and polish.
