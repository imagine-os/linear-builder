---
identifier: "PAP-331"
title: "KanbanDnd, SortableGrid, DropZone and cross-window drag"
project: "input"
projectName: "Multi-Input Control & Accessibility"
phase: "P1"
type: "Build"
priority: 2
surfaces: ["Staff"]
milestone: "Touch, pen, gamepad"
state: "Backlog"
parent: "PAP-155"
children: []
blockedBy: ["PAP-330", "PAP-643"]
blocks: ["PAP-167", "PAP-173", "PAP-344", "PAP-385", "PAP-633", "PAP-853"]
key: "input/dnd/kanban-grid-dropzone-crosswindow"
url: "https://linear.app/paperos/issue/PAP-331/kanbandnd-sortablegrid-dropzone-and-cross-window-drag"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:28:51.354Z"
model: "claude-sonnet-5"
effort: "high"
estimate: 3
dueDate: "2026-09-27"
cycle: null
---

# PAP-331: KanbanDnd, SortableGrid, DropZone and cross-window drag

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / high — Build M

**Goal**

Finish PAP-155 with the components views use: cross-column kanban moves with `canDrop` reasons and WIP limits, a 2D sortable grid, a drop zone for files and items, multi-select drags with a count overlay, and drags between the main window and a detached panel.

**Scope**

In:

* `KanbanDnd columns cards onMove canDrop` with `rectIntersection`, WIP limit check, denied cursor plus tooltip plus announcement.
* `SortableGrid` (2D) and `DropZone accept onDrop` (files and items).
* Multi-select: selected items from PAP-165 move together; overlay shows "3 items".
* Cross-window: pointer leaves the window → `dnd.transfer { payload, sourceWindowId }` over PAP-145 `WindowBus`; target shows a drop hint and completes; web pop-out fallback (PAP-263) supported.
* Template sample pages using all three; Storybook stories with reduced motion.

Out: sensors and keyboard (siblings).

**Spec**

* `canDrop(source, target) -> true | { reason }`; reason shown in tooltip and announcement.
* Remote list changes during a drag keep it alive and recompute on drop.

*Round 4 amendment (2026-09-18):*

* Round 4: `DropZone` also accepts native OS file drops in Tauri through `getCurrentWebview().onDragDropEvent` (paths converted with `convertFileSrc` and read through the fs plugin scope), showing the same hover state as web `dragover`; on web the `DataTransfer` files path is unchanged. Items dropped from another PaperOS window prefer the `dnd.transfer` bus message and fall back to the typed clipboard payload (PAP-643) when the bus is unavailable.

**Interface contract**

Exposes `KanbanDnd`, `SortableGrid`, `DropZone`, `CanDropResult`, window message `dnd.transfer`. Consumes siblings 1 and 2, `WindowBus` (PAP-145), grid selection (PAP-165), file upload hooks (PAP-37), primitives (PAP-67).

**Definition of done**

* Kanban, grid and drop zone in template pages; cross-window drag on Tauri Linux recorded; screenshots at 375, 1024 and 1440; docs `docs/platform/input/drag-drop.md`; changelog; Linear comment.

**Test plan**

* Vitest: `canDrop` handling, multi-select payloads, WIP limit reason, transfer message schema.
* Playwright: cross-column move, denied drop onto a full column with reason, file drop onto `DropZone`, multi-select drag overlay count, cross-window drag via two pages in one context using the web fallback.
* Visual: Gate 3 captures of overlay and denied state, three themes.

**Demo**

Drag a card into a full column and read the reason, select three rows and drag them together, drop a file on the zone, pop out the inspector and drag a row into it. Under two minutes.

**Edge cases**

* Target window closes mid-transfer: source shows "drop target closed".
* File over 25 MB: rejected with a notice (PAP-37 limit).

**Dependencies**

Siblings 1 and 2 (hard). PAP-145, PAP-165, PAP-37 (soft). Consumed by PAP-167, PAP-173, PAP-102.

**Agent**

Built by Nova (Views Engineer). Reviewed by Sentinel (Code Reviewer); Iris reviews overlay styling.

**Size**

M: three components and the cross-window path.

*Round 4 critique fix (2026-09-18):* resolved 1 round-4 file key in this description to Linear identifiers: `r4/input/clipboard-port` = PAP-643.
