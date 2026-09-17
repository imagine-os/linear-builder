---
identifier: "PAP-155"
title: "Build accessible drag-and-drop (dnd-kit) for tables, kanban and canvas with a keyboard alternative"
project: "input"
projectName: "Multi-Input Control & Accessibility"
phase: "P1"
type: "Build"
priority: 2
surfaces: ["Customer", "Staff"]
milestone: "Touch, pen, gamepad"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-150", "PAP-152"]
blocks: ["PAP-167", "PAP-173"]
key: "input/drag-drop"
url: "https://linear.app/paperos/issue/PAP-155/build-accessible-drag-and-drop-dnd-kit-for-tables-kanban-and-canvas"
source: "plan/specs/bucket-5.json (round-1 canonical spec JSON)"
---

# PAP-155: Build accessible drag-and-drop (dnd-kit) for tables, kanban and canvas with a keyboard alternative

**Goal**

Give every list, table, kanban board and canvas one accessible drag-and-drop system: pointer dragging with smooth previews, a full keyboard alternative (pick up, move, drop with arrow keys), screen-reader announcements, touch and pen support, and cross-window drags between detached panels. Reordering and moving items must work for everyone, and the engine must be the same in every view so agents implement it once.

**Scope**

In:
- `packages/input/src/dnd/` wrapping `@dnd-kit/core` 6.x and `@dnd-kit/sortable` with PaperOS sensors built on `input/input-abstraction` (`PointerSurfaceSensor` handling mouse, touch and pen with the shared thresholds) and dnd-kit's `KeyboardSensor` customised for grid movement.
- High-level components in `packages/ui`: `SortableList`, `SortableGrid` (2D), `KanbanDnd` (columns and cards, cross-column, WIP limit checks via a `canDrop` callback), `DropZone` (files and items), `DragHandle` (visible on hover/focus, always present for keyboard), `DragOverlay` preview with count badge for multi-select drags.
- Keyboard alternative: `Space`/`Enter` on a handle picks up, arrows move (with `PageUp/PageDown` for columns, `Home/End`), `Space` drops, `Escape` cancels; instructions announced on pickup; movement announced ("Moved Task A to position 3 of 8 in Doing").
- Multi-select drag: selected items (from `tables/grid-view` selection) move together; the overlay shows "3 items".
- Cross-window drag between the main window and a detached Tauri panel: pointer leaves the window → a `dnd.transfer` message over `realtime/multi-window-sync` carries the payload; the target window shows a drop hint and completes the drop.
- Auto-scroll near edges, collision strategies per component (`closestCenter` for lists, `rectIntersection` for canvas), and reduced-motion variants.

Out: canvas free-form dragging of shapes (tldraw handles its own; this issue provides the drop-in bridge only), file upload logic (`data-layer/file-storage`), persistence of order (consumers call `onReorder`).

**Spec**

- API: `<SortableList items getId onReorder renderItem strategy />`; `onReorder({ from, to, item, items })` is optimistic and reverts on rejected promise; ordering uses fractional indexing (`fractional-indexing` 3.x) helper `between(a, b)` exported for consumers storing `sort_key`.
- Announcements go through the shared `LiveAnnouncer` from `input/focus-management`; strings in `packages/input/src/copy/dnd.ts` templated with item label, position and container.
- `canDrop(source, target)` returns `true | { reason }`; a denied target renders a "not allowed" cursor and the reason in a tooltip and in the announcement.
- Touch: drag starts after 250 ms long-press with a haptic (`input/touch-gestures`) so lists still scroll; pen drags immediately with the barrel button or after 4 px.
- Performance: dragging within a virtualised 10,000-row `tables/grid-view` keeps 60 fps; only overlay and two neighbours re-render (React Profiler assertion in a test).
- Focus: after drop, focus returns to the moved item's handle; after cancel, to the original handle (`useFocusRestore`).
- Every component registers commands `dnd.pickUp`, `dnd.drop`, `dnd.cancel` in `input/command-registry` so keymaps and voice can trigger them.

**Definition of done**

- `SortableList`, `KanbanDnd` and `DropZone` used in the template's sample pages; Playwright tests for pointer, touch and keyboard paths at 375, 1024 and 1440 px, screenshots of overlay and denied states attached.
- Screen-reader announcement text snapshot-tested; NVDA and VoiceOver spot check recorded for `input/screen-reader`.
- Cross-window drag demonstrated on Tauri Linux with video.
- Vitest tests for fractional indexing, `canDrop` handling, multi-select payloads and revert on failure.
- Storybook stories in three themes with reduced motion variant; axe clean.
- Docs `docs/platform/input/drag-drop.md`; changelog entry; Linear comment with demo and video links.

**Edge cases**

- Item list changes remotely during a drag (`realtime/record-sync`): keep the drag alive; recompute positions on drop; if the item was deleted, cancel with an announcement.
- Drop onto a column at its WIP limit: denied with reason "Doing is at its limit (5)".
- Dragging across a scroll boundary in a nested scroll container: auto-scroll the innermost container first.
- Keyboard drag while the list is virtualised and the target is off-screen: scroll target into view before announcing.
- Window loses focus mid-drag (alt-tab): cancel and restore.
- RTL layouts: arrow semantics flip; test with `dir="rtl"`.

**Dependencies**

- `input/input-abstraction` (sensor), `input/focus-management` (announcer, restore), `input/touch-gestures` (long-press, haptics), `input/command-registry`, `realtime/multi-window-sync` (cross-window transfer), `design-system/primitives`. Consumed by `tables/grid-view`, `tables/kanban-view`, `tables/dashboard-blocks`, `collab/canvas-view`, `pm-linear/board-views`.

**Agent**

Builder: Nova (Views Engineer sub-agent). Reviewer: Sentinel (Code Reviewer, Edge Case Hunter); Iris reviews handle and overlay styling.

**Size**

L: several components, three input modalities, cross-window transfer and accessibility all in one surface.
