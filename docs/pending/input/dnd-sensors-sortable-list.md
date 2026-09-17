---
key: "input/dnd/sensors-sortable-list"
title: "dnd-kit sensors on the input abstraction and SortableList"
project: "input"
parent: "PAP-155"
phase: "P1"
type: "Build"
priority: 2
size: null
surfaces: ["Customer", "Staff"]
milestone: "Touch, pen, gamepad"
intendedState: "Backlog"
blockedBy: []
blocks: []
source: "round2/agent3/pending-issues.json"
linearDocument: null
identifier: "PAP-329"
status: "created"
createdAt: "2026-09-17"
---

# dnd-kit sensors on the input abstraction and SortableList

**Goal**

Start PAP-155 with the engine: a dnd-kit wrapper whose sensors come from the input abstraction so mouse, touch and pen behave consistently, a `SortableList` with optimistic reorder and revert, and the fractional-indexing helper consumers use for `sort_key`.

**Scope**

In:

* `packages/input/src/dnd/`: `@dnd-kit/core` 6.x and `@dnd-kit/sortable` wrapper; `PointerSurfaceSensor` on `usePointerSurface` (PAP-150): mouse drag after 4 px, touch after 250 ms long-press with `haptic('selection')` (PAP-154), pen immediately with barrel button or after 4 px.
* `SortableList items getId onReorder renderItem strategy`; `onReorder({ from, to, item, items })` optimistic with revert on rejected promise; `DragHandle`, `DragOverlay`.
* `between(a, b)` from `fractional-indexing` 3.x exported for `sort_key` storage.
* Auto-scroll near edges; `closestCenter` collision.

Out: keyboard grammar (sibling 2), kanban, grid, drop zone, cross-window (sibling 3).

**Spec**

* Overlay and two neighbours are the only re-rendering items during a drag (React Profiler assertion).
* Reduced motion: no transform animation.

**Interface contract**

Exposes `DndProvider`, `PointerSurfaceSensor`, `SortableList`, `DragHandle`, `DragOverlay`, `between()`, `ReorderEvent` type. Consumes `usePointerSurface` and `THRESHOLDS` (PAP-150), `haptic()` and long-press (PAP-154), primitives (PAP-67).

**Definition of done**

* Sample list reorders by mouse, touch and pen; Storybook stories; Linear comment with screenshots at 375 and 1280.

**Test plan**

* Vitest: `between()` ordering across 1,000 inserts without precision loss, revert on rejected promise, sensor activation thresholds per pointer type.
* Playwright: pointer drag at 1280; touch long-press drag on `hasTouch` while a plain swipe scrolls at 375.
* Performance: profiler assertion in a 10,000-row virtual list.

**Demo**

Drag an item with the mouse, then long-press and drag on the touch emulator, watch the order persist via the mocked callback. Under two minutes.

**Edge cases**

* Drag within nested scroll containers: innermost auto-scrolls first.
* Alt-tab mid-drag: cancel and restore.

**Dependencies**

PAP-150 (hard). PAP-154, PAP-67 (soft). Blocks siblings 2 and 3.

**Agent**

Built by Nova (Views Engineer). Reviewed by Sentinel (Code Reviewer).

**Size**

M: sensors plus one component with performance constraints.
