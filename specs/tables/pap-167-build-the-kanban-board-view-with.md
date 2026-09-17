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
blockedBy: ["PAP-155", "PAP-163", "PAP-331", "PAP-337"]
blocks: ["PAP-102", "PAP-189"]
key: "tables/kanban-view"
url: "https://linear.app/paperos/issue/PAP-167/build-the-kanban-board-view-with-swimlanes-wip-limits-and-drag-and"
source: "Linear snapshot 2026-09-17T13:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T13:05:34.130Z"
---

# PAP-167: Build the kanban board view with swimlanes, WIP limits and drag-and-drop

**Goal**

Build the kanban view so any dataset with a select, status or single-relation field works as a board: columns per group value, optional swimlanes, WIP limits, accessible drag-and-drop, card templates and inline creation. PM boards (PAP-102) and CRM pipelines (PAP-189) are the first consumers.

**Scope**

In: `packages/views/src/views/kanban/`: `KanbanView`, `KanbanColumn`, `KanbanCard`, `CardTemplateEditor`; options `{ groupField, swimlaneField?, wipLimits, cardFields, coverField?, colorField?, hideEmptyColumns, collapsedColumns, columnOrder? }`; column aggregates (count plus one sum).

Out: time views (PAP-168), automation on move (PAP-174), swimlane by multi-relation.

**Spec**

* Group field must be `select`, `user` or relation with `limitOne`. Columns from `views.groups` level 1; cards per column via `views.query` with `groupPath`, page 50, "Load more"; each column virtualised.
* Swimlanes: lane per `swimlaneField` value, each cell paginated independently.
* Drop writes `{ [groupField]: optionId }` plus `sort_key` via `between()` for custom datasets; entity datasets without manual order change only the group value and show a "sorted by X" hint; optimistic with revert toast.
* WIP: header `n / limit`, warning at limit, danger above; `canDrop` returns `{ reason }` unless Alt override (audited).
* Card: title, up to six `cardFields` at compact density, cover, colour bar, avatar stack, comment badge slot (PAP-131).
* Inline "+ New" creates with the column value; Enter keeps adding.
* Keyboard: Space pick up, arrows move, Space drop, Escape cancel; `LiveAnnouncer`; commands `kanban.*`.
* Under 768 px: horizontally snapping single-column panes with a pager; under 1024 px max three card fields.

**Interface contract**

Provides: `<KanbanView spec onSpecChange datasetRef onMove? onFilter? />`, `KanbanCard` template API, `onMove(recordId, from, to, index)` hook used by PAP-189 for won/lost dialogs and PAP-102 for Linear sync, `canDrop` extension. Consumes: `views.groups|query` (PAP-163), cells (PAP-164), `KanbanDnd` (PAP-155), `AvatarStack`, `Badge` (PAP-71), `LiveAnnouncer` (PAP-153), record sync (PAP-143, optional).

**Definition of done**

* Vitest for move reducer, WIP evaluation, template config; Playwright flows below on a 2,000-record, eight-column seed.
* Storybook story; screenshots at 375, 768, 1024, 1440, 1920 in three themes; video replay of a drag at each width; 60 fps drag assertion.
* `docs/views/kanban.md`; CHANGELOG; Linear comment with demo link.

**Test plan**

* Unit: move reducer including same-column reorder; WIP maths; Alt override flag; template config validation.
* Integration: `onMove` writes group value and `sort_key`; two clients moving the same card converge (PAP-143 harness).
* E2E: pointer drag between columns, keyboard move, WIP block with reason, inline add, swimlane collapse, 375 px pager; axe run per state.
* Visual: matrix above plus collapsed columns and empty "(no value)" column.

**Demo**

Reviewer opens `/demo/kanban`, drags a card into a column at its WIP limit and reads the refusal, holds Alt to override, adds a card inline, then uses keyboard only to move another card. Under two minutes.

**Edge cases**

* 200 options: columns virtualised, first 30 shown with "Show all".
* Concurrent moves: last write wins, loser animates to the real column.
* Drop into a column the user cannot write: refused with `explain()` reason.
* Option deleted while open: cards move to "(no value)" after refetch, toast.
* Offline: moves queue in the outbox with a pending badge.

**Dependencies**

PAP-163 (hard), PAP-155 (hard for cross-container drag), PAP-164, PAP-71, PAP-143 (soft). Blocks PAP-102, PAP-189.

**Agent**

Builder: Nova (Views Engineer). Reviewer: Sentinel (Visual Inspector, Edge Case Hunter); Iris on card design.

**Size**

M: drag infrastructure exists; the work is board semantics, per-column pagination and polish.
