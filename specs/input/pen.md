---
identifier: "PAP-157"
title: "Support pen and stylus input with pressure for canvas and annotation"
project: "input"
projectName: "Multi-Input Control & Accessibility"
phase: "P2"
type: "Build"
priority: 3
surfaces: ["Staff"]
milestone: "Voice and accessibility certification"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-132", "PAP-150"]
blocks: []
key: "input/pen"
url: "https://linear.app/paperos/issue/PAP-157/support-pen-and-stylus-input-with-pressure-for-canvas-and-annotation"
source: "plan/specs/bucket-5.json (round-1 canonical spec JSON)"
---

# PAP-157: Support pen and stylus input with pressure for canvas and annotation

**Goal**

Make tablets with a stylus first-class for sketching and annotation: pressure-sensitive strokes on the canvas, palm rejection, barrel-button eraser, hover previews, and pen-based markup on screenshots and documents. Pen input flows through the shared abstraction so the canvas, screenshot annotation and any future whiteboard get identical behaviour.

**Scope**

In:
- `packages/input/src/pen/`: `usePenStroke(surface, { smoothing, pressureCurve, minWidth, maxWidth })` producing stroke points `{ x, y, pressure, tiltX, tiltY, t }`, with `perfect-freehand` 1.x for outline generation and a Catmull-Rom smoother; `usePenHover` for hover cursor previews; `usePenButtons` mapping barrel button → eraser, secondary → lasso.
- Palm rejection and pen priority (from `input/input-abstraction`): while a pen is down, touch presses on the same surface are ignored; two-finger touch still pans/zooms.
- Canvas integration: a tldraw (or React Flow, per `collab/collab-research`) tool `PaperOSPenTool` in `collab/canvas-view` that uses `usePenStroke`, stores strokes as a Yjs-synced shape (`type: 'ink'`, points compressed with delta encoding), and renders via SVG path at up to 240 Hz input sampling using `getCoalescedEvents`.
- Annotation layer `InkAnnotationLayer` in `packages/ui` for images and screenshots (used by `collab/screenshot-annotations`): draw, highlight (multiply blend), erase, undo/redo, export as SVG overlay plus flattened PNG.
- Pen settings in `/settings/input`: pressure curve presets (linear, soft, firm), default widths, "pen only draws" toggle, left-handed hover offset.

Out: handwriting recognition, shape recognition, pen-based text input in Tiptap (dictation covers voice, not ink), Wacom driver-specific features.

**Spec**

- Pressure curve `f(p) = minWidth + (maxWidth − minWidth) × curve(p)`; presets as functions; tilt modulates width by up to 30% when `tiltShading` is on.
- Sampling: use `PointerEvent.getCoalescedEvents()` where available, `getPredictedEvents()` for the live preview segment only (never stored).
- Stroke storage: `{ id, tool, color token, width, points: Int16Array deltas (0.1 px units), pressures: Uint8Array }`; a 5,000-point stroke stays under 20 KB; strokes over 20,000 points are split.
- Rendering: live stroke on a dedicated `<canvas>` layer for latency; committed strokes as SVG paths; target under 16 ms from pen sample to paint (measured with `PerformanceObserver` in the Playwright test using CDP-synthesised pen events).
- Eraser: barrel button or tool switch; whole-stroke erase by default, segment erase with `alt`.
- Undo/redo through `y-undo-manager` scoped to the local user (`realtime/collab-text` pattern) and registry commands `edit.undo/redo`.
- Accessibility: ink is decorative unless the author adds an alt text via the annotation panel; the annotation list is navigable by keyboard and exposes each stroke group as a list item with its alt text.

**Definition of done**

- Drawing with a pen on a Windows Surface or Android tablet (Tauri build) shows pressure-varying strokes, palm rejection and eraser; video attached.
- Playwright tests using CDP `Input.dispatchMouseEvent` with `pointerType: 'pen'` and pressure values assert width variation and latency budget; screenshots at 768 and 1280 px (tablet widths).
- Vitest tests for pressure curves, delta encoding round-trip, stroke splitting and palm-rejection timing.
- Annotation layer used by `collab/screenshot-annotations` demo to mark up a screenshot and export PNG+SVG.
- Two browsers see each other's strokes live via Yjs within 100 ms on localhost.
- Docs `docs/platform/input/pen.md`; changelog entry; Linear comment with video and demo link.

**Edge cases**

- Pen leaves the digitiser mid-stroke (`pointerleave` without `up`): commit the stroke on `pointercancel` or 500 ms timeout.
- Pressure always 0.5 (unsupported hardware): detect constant pressure over 20 samples and switch to fixed width.
- Mouse users on the ink tool: constant pressure, `shift` for straight lines so the tool is not pen-only.
- 100k-point document (a long session): render committed strokes into a cached bitmap tile layer; SVG only for the last 200 strokes.
- Left-handed users: hover preview offset mirrors; setting persists per user.
- Zoomed canvas at 8×: widths scale with zoom; minimum on-screen width 1 px.

**Dependencies**

- `input/input-abstraction` (pen fields, palm rule), `collab/canvas-view` (tool host), `realtime/yjs-server` (stroke sync), `collab/screenshot-annotations` (consumer), `input/touch-gestures` (two-finger pan while drawing), `design-system/tokens` (ink colours).

**Agent**

Builder: Nova (Canvas Cartographer sub-agent). Reviewer: Sentinel (Visual Inspector for stroke rendering, Code Reviewer); Iris for settings UI.

**Size**

M: rendering and encoding are contained; device testing adds time.
