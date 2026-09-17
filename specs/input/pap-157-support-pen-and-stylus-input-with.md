---
identifier: "PAP-157"
title: "Support pen and stylus input with pressure for canvas and annotation"
project: "input"
projectName: "Multi-Input Control & Accessibility"
phase: "P2"
type: "Build"
priority: 4
surfaces: ["Staff"]
milestone: "Voice and accessibility certification"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-132", "PAP-150", "PAP-322"]
blocks: []
key: "input/pen"
url: "https://linear.app/paperos/issue/PAP-157/support-pen-and-stylus-input-with-pressure-for-canvas-and-annotation"
source: "Linear snapshot 2026-09-17T13:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T13:05:28.589Z"
model: "claude-sonnet-5"
effort: "low"
---

# PAP-157: Support pen and stylus input with pressure for canvas and annotation

**Goal**

Deferred to v0.2 by the Execution Schedule (NJ-14 stop-loss 09-27 can reinstate). Not claimable before 10-01.

Make tablets with a stylus first-class for sketching and annotation: pressure-sensitive strokes on the canvas, palm rejection, barrel-button eraser, hover previews and pen markup on screenshots. Pen flows through the shared abstraction so canvas, screenshot annotation and future whiteboards behave identically.

**Scope**

In:

* `packages/input/src/pen/`: `usePenStroke(surface, { smoothing, pressureCurve, minWidth, maxWidth })` producing `{ x, y, pressure, tiltX, tiltY, t }` points with `perfect-freehand` outlines and Catmull-Rom smoothing; `usePenHover`; `usePenButtons` (barrel → eraser, secondary → lasso).
* Palm rejection and pen priority from PAP-150; two-finger touch still pans.
* Canvas tool `PaperOSPenTool` in PAP-132 storing strokes as a Yjs shape `type: 'ink'` with delta encoding; live stroke on a `<canvas>` layer, committed strokes as SVG; `getCoalescedEvents` up to 240 Hz.
* `InkAnnotationLayer` in `packages/ui` for images and screenshots (PAP-137): draw, highlight (multiply), erase, undo and redo, export SVG overlay and flattened PNG.
* Pen settings `/settings/input`: pressure presets, widths, "pen only draws", left-handed offset.

Out: handwriting or shape recognition, ink text input, driver-specific features.

**Spec**

* Width `f(p) = min + (max − min) × curve(p)`; tilt modulates up to 30 percent when enabled.
* `getPredictedEvents` for the preview segment only, never stored.
* Stroke `{ id, tool, color, width, points: Int16Array deltas (0.1 px), pressures: Uint8Array }`; 5,000 points under 20 KB; split over 20,000.
* Under 16 ms sample to paint; eraser whole-stroke by default, segment with `alt`.
* Undo via `y-undo-manager` scoped to the user; ink decorative unless alt text is added; annotation list keyboard navigable.

**Interface contract**

Exposes: `usePenStroke`, `usePenHover`, `usePenButtons`, `InkStroke` type and `encodeStroke()`/`decodeStroke()`, `InkAnnotationLayer` (`onChange(strokes)`, `exportSvg()`, `exportPng()`), canvas node type `ink` registered through PAP-132's `registerNodeType`, `PressureCurve` presets, settings keys `input.pen.*` in `user_preferences`. Consumes: pen fields, palm rule and `getCoalescedEvents` plumbing (PAP-150), canvas tool host and overlay doc (PAP-132), room persistence (PAP-140), two-finger pan (PAP-154), annotation viewer slot (PAP-137), ink colour tokens (PAP-66), y-undo pattern (PAP-142).

**Definition of done**

* Pen on a Windows Surface or Android tablet (Tauri) shows pressure-varying strokes, palm rejection and eraser; video attached.
* Two browsers see each other's strokes within 100 ms on localhost; PAP-137 demo marks up a screenshot and exports PNG and SVG.
* Screenshots at 768 and 1280; `docs/platform/input/pen.md`; changelog; Linear comment with video and demo link.

**Test plan**

* Vitest: pressure curves at p = 0, 0.5, 1 for each preset, delta encoding round-trip, stroke splitting at 20,000 points, palm-rejection timing window, constant-pressure detection over 20 samples.
* Playwright: CDP `Input.dispatchMouseEvent` with `pointerType: 'pen'` and varying `force` asserts width variation in the SVG path; `PerformanceObserver` latency budget under 16 ms p95; mouse on the ink tool draws constant width and `shift` makes a straight line; run at 768 and 1280.
* Integration: two contexts on a canvas room converge on the ink shape within 100 ms.
* Visual: Gate 3 captures of strokes in light and dark and the settings page; axe on the annotation list.

**Demo**

Open the canvas on a tablet, pick the pen, draw with varying pressure, rest your palm, flip to the barrel button and erase; open a QA screenshot, highlight a region and export PNG. Under two minutes.

**Edge cases**

* Pen leaves mid-stroke: commit on `pointercancel` or 500 ms.
* Constant pressure hardware: fixed width.
* 100k-point session: bitmap tiles for old strokes, SVG for the last 200.
* 8× zoom: widths scale, minimum 1 px.

**Dependencies**

PAP-150, PAP-132 (hard, encoded). Soft: PAP-140, PAP-154, PAP-137, PAP-66.

**Agent**

Builder: Nova (Canvas Cartographer). Reviewer: Sentinel (Visual Inspector, Code Reviewer); Iris for settings UI.

**Size**

M: rendering and encoding are contained; device testing adds time.
