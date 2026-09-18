---
identifier: "PAP-155"
title: "Build accessible drag-and-drop (dnd-kit) for tables, kanban and canvas with a keyboard alternative"
project: "input"
projectName: "Multi-Input Control & Accessibility"
phase: "P1"
type: "Build"
priority: 2
surfaces: ["Staff"]
milestone: "Touch, pen, gamepad"
state: "Backlog"
parent: null
children: ["PAP-330", "PAP-331", "PAP-329"]
blockedBy: ["PAP-150", "PAP-152", "PAP-644"]
blocks: ["PAP-167", "PAP-173", "PAP-344", "PAP-385"]
key: "input/drag-drop"
url: "https://linear.app/paperos/issue/PAP-155/build-accessible-drag-and-drop-dnd-kit-for-tables-kanban-and-canvas"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T13:48:17.924Z"
model: null
effort: null
estimate: null
dueDate: "2026-09-27"
cycle: null
---

# PAP-155: Build accessible drag-and-drop (dnd-kit) for tables, kanban and canvas with a keyboard alternative

**Model / Effort:** set on children (umbrella is never claimed)

**Goal**

Umbrella: one accessible drag-and-drop system for lists, tables, kanban and canvas: pointer dragging with previews, a full keyboard alternative, screen-reader announcements, touch and pen support, and cross-window drags between detached panels. Planned as three work packages; the umbrella owns the integration test, docs and the screen-reader spot check hand-off to PAP-156.

**Scope**

Work packages (build in order; each becomes a child issue once the Linear issue limit is lifted, see the pinned comment):

1. **dnd-kit sensors on the input abstraction and** `SortableList` — `@dnd-kit/core` 6.x wrapper, `PointerSurfaceSensor` (mouse, touch with 250 ms long-press and haptic, pen) on PAP-150, `SortableList` with `onReorder`, fractional indexing helper `between(a, b)`, optimistic revert.
2. **Keyboard alternative, announcements and focus restore** — customised `KeyboardSensor` (`Space`/`Enter` pick up, arrows and `PageUp/PageDown` move, `Space` drop, `Escape` cancel), `LiveAnnouncer` strings in `packages/input/src/copy/dnd.ts`, `useFocusRestore` after drop or cancel, commands `dnd.pickUp|drop|cancel`.
3. `KanbanDnd`**,** `SortableGrid`**,** `DropZone` **and cross-window drag** — cross-column moves with `canDrop` reasons and WIP limits, multi-select overlay with count, `DropZone` for files and items, `dnd.transfer` over PAP-145 with target drop hint, auto-scroll and collision strategies.

Parent owns `docs/platform/input/drag-drop.md`, Storybook stories, integration test, template sample pages.

Out: tldraw's own shape dragging (bridge only), upload logic (PAP-37), order persistence (consumers).

**Spec**

* `canDrop(source, target)` returns `true | { reason }`; denied targets show a not-allowed cursor, tooltip and announcement.
* Dragging inside a virtualised 10,000-row grid stays at 60 fps; only overlay and two neighbours re-render.
* Collision `closestCenter` for lists, `rectIntersection` for canvas; reduced-motion variants.

**Interface contract**

Exposes (owned by the work packages): `<SortableList items getId onReorder renderItem strategy />`, `<SortableGrid />`, `<KanbanDnd columns cards onMove canDrop />`, `<DropZone accept onDrop />`, `DragHandle`, `DragOverlay`, `onReorder({ from, to, item, items })`, `between(a, b)` from `fractional-indexing`, `CanDropResult`, announcement copy keys, window message `dnd.transfer { payload, sourceWindowId }`, commands `dnd.*`. Consumes: `usePointerSurface` and `THRESHOLDS` (PAP-150), `LiveAnnouncer`, `useFocusRestore` (PAP-152), long-press and `haptic()` (PAP-154), `defineCommand` (PAP-151), `WindowBus` (PAP-145), primitives (PAP-67), grid selection state (PAP-165).

**Definition of done**

* All three work packages merged; `SortableList`, `KanbanDnd` and `DropZone` used in template sample pages.
* Cross-window drag on Tauri Linux recorded; NVDA and VoiceOver spot check recorded and handed to PAP-156.
* Storybook stories in three themes with reduced motion, axe clean; screenshots at 375, 1024 and 1440; docs; changelog; Linear comment with demo and video links.

**Test plan**

* Integration (parent): Playwright at 375, 1024 and 1440: pointer drag reorders and persists via mocked `onReorder`; touch long-press drag on a `hasTouch` context while a plain swipe still scrolls; keyboard path picks up a card, moves it two columns with `PageDown`, drops, and the announcement text matches the snapshot; drop onto a full column is denied with the reason; detach a panel (Tauri or web pop-out fallback) and drag across windows.
* Unit tests per work package (fractional indexing ordering and precision, `canDrop` handling, multi-select payload, revert on rejected promise, keyboard grammar state machine, announcement templates).
* Performance: React Profiler assertion that a drag in a 10,000-row virtual grid re-renders at most three items per frame.
* Visual: Gate 3 captures of overlay, denied state and handles, three themes.

**Demo**

On the kanban sample, drag a card between columns with the mouse; press `Tab` to a handle, `Space`, `PageDown`, `Space` and hear “Moved Task A to position 3 of 8 in Doing”; drop a file on the `DropZone`; detach the inspector and drag a row into it. Under two minutes.

**Edge cases**

* List changes remotely mid-drag: keep alive, recompute on drop; deleted item cancels with announcement.
* WIP limit: "Doing is at its limit (5)".
* Off-screen keyboard target: scroll into view before announcing.
* Alt-tab mid-drag: cancel and restore.
* RTL: arrow semantics flip.

**Dependencies**

PAP-150, PAP-152 (hard, encoded). Soft: PAP-154, PAP-151, PAP-145, PAP-67, PAP-165. Blocks PAP-167, PAP-173; consumed by PAP-165, PAP-132, PAP-102.

**Agent**

Builder: Nova (Views Engineer). Reviewer: Sentinel (Code Reviewer, Edge Case Hunter); Iris reviews handle and overlay styling.

**Size**

L, planned as three M work packages (child issues pending the issue limit).
