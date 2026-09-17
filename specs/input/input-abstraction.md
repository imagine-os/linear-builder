---
identifier: "PAP-150"
title: "Design a unified input event abstraction so components handle mouse, touch, pen and gamepad uniformly"
project: "input"
projectName: "Multi-Input Control & Accessibility"
phase: "P0"
type: "Spec"
priority: 2
surfaces: ["Developer"]
milestone: "Keyboard and command system"
state: "Ready for Claude"
parent: null
children: []
blockedBy: []
blocks: ["PAP-151", "PAP-154", "PAP-155", "PAP-157", "PAP-158"]
key: "input/input-abstraction"
url: "https://linear.app/paperos/issue/PAP-150/design-a-unified-input-event-abstraction-so-components-handle-mouse"
source: "plan/specs/bucket-5.json (round-1 canonical spec JSON)"
---

# PAP-150: Design a unified input event abstraction so components handle mouse, touch, pen and gamepad uniformly

**Goal**

Define one input model that every PaperOS component uses so that mouse, touch, pen and gamepad behave consistently without each component re-implementing device checks. The output is a spec plus a small typed core in `packages/input` that later issues (gestures, drag-and-drop, pen, gamepad) build on; it decides the vocabulary (press, move, release, cancel, modifiers, pointer type, pressure) once.

**Scope**

In:
- Spec `docs/platform/input/abstraction.md`: event vocabulary, coordinate spaces, capture semantics, device capability detection, how the model maps to DOM Pointer Events, Touch Events fallback, Gamepad API and keyboard.
- `packages/input/src/core/`: `InputEvent` union (`press | move | release | cancel | wheel | key | gamepad`), `Pointer` (`id, type: 'mouse'|'touch'|'pen'|'gamepad-cursor', x, y, pressure, tilt, twist, buttons, isPrimary`), `Modifiers`, `usePointerSurface(ref, handlers, { capture, passive })` hook translating `pointerdown/move/up/cancel` and `lostpointercapture` into the union with pointer capture handled centrally.
- Capability detection `useInputCapabilities()` → `{ coarsePointer, finePointer, hover, touchPoints, penSeen, gamepadConnected, keyboardSeen }` from media queries (`pointer`, `hover`, `any-pointer`) plus observed events; exposed as `data-input-*` attributes on `<html>` for CSS (`[data-input-coarse] .btn { min-height: 44px }`).
- Hit-target and gesture thresholds table (tap slop 8 px fine / 12 px coarse, long-press 500 ms, double-press 300 ms, drag start 4 px / 10 px) as exported constants.
- Decision on library: evaluate `@use-gesture/react` 10.x and `interactjs`; the spec must say whether the surface hook wraps `@use-gesture` or stands alone (default recommendation: standalone thin layer over Pointer Events, `@use-gesture` only for pinch/wheel math in `input/touch-gestures`).

Out: gesture recognisers, drag-and-drop, spatial focus, voice, the command registry (`input/command-registry` handles keyboard commands).

**Spec**

- Coordinates: every pointer carries `client`, `page` and `surface` (relative to the hooked element, in CSS pixels, scaled by `devicePixelRatio` only where the consumer asks) coordinates.
- Capture: on `press` the hook calls `setPointerCapture`; `release`/`cancel` always fire once per pointer id; `cancel` fires on `pointercancel`, window blur, and `visibilitychange` hidden.
- Multi-pointer: handlers receive the full active pointer map for pinch/rotate consumers.
- Keyboard: `key` events normalised to a `Key` (`code`, `key`, modifiers, `repeat`) and a portable chord string `mod+shift+k` shared with `input/command-registry` (`mod` = Cmd on macOS, Ctrl elsewhere).
- Gamepad: a polling loop (`requestAnimationFrame`) emits `gamepad` events with normalised sticks and buttons (standard mapping) and a synthetic `gamepad-cursor` pointer when cursor mode is enabled by `input/gamepad`.
- Pen: `pressure`, `tiltX/Y`, `twist` pass through; `pointerType === 'pen'` with barrel button maps to `buttons` bit 2; palm rejection rule: while a pen is active, touch presses on the same surface are ignored for 300 ms.
- Component contract: all `packages/ui` interactive components must use `usePointerSurface` or native elements; a Biome lint rule (`no-raw-touch-handlers`) flags `onTouchStart`/`onMouseDown` in `packages/ui` and `packages/views`.

**Definition of done**

- Spec merged and linked from `design-system/guidelines-docs`.
- `packages/input` core with Vitest tests using synthetic `PointerEvent`s for capture, cancel-on-blur, slop thresholds and chord normalisation on macOS and Linux `navigator.platform` mocks.
- Storybook "Input Playground" story visualising active pointers, pressure and capabilities at 375 (touch emulation) and 1280 px, screenshots attached.
- Biome rule enabled with zero violations in `packages/ui`.
- `data-input-*` attributes documented and used by at least the Button primitive for coarse hit targets.
- Changelog entry (developer) and Linear comment with the playground link.

**Edge cases**

- Touch-then-mouse devices (Surface): capabilities update live when a new pointer type is observed; do not freeze on first paint.
- `pointercancel` on scroll: consumers must treat `cancel` like release without action; document `touch-action` requirements.
- Right-click on touch (long-press context menu): suppress native menu only when a handler claims the long-press.
- iOS Safari missing `pointerrawupdate` and gamepad quirks: polling handles both.
- High pressure values > 1 from some drivers: clamp to [0, 1].
- Windows with pen hover: `move` with `buttons === 0` must be distinguishable (hover) from a drag.

**Dependencies**

- None to start (readyNow). Informs `design-system/primitives` (hit targets), `input/command-registry` (chord format), `input/touch-gestures`, `input/drag-drop`, `input/pen`, `input/gamepad`, `collab/canvas-view`.

**Agent**

Builder: Nova (Product Systems Engineer, owner of multi-input). Reviewer: Iris (Motion and Input Stylist) for the component contract; Sentinel (Code Reviewer).

**Size**

S: a spec and a thin core; the value is in deciding the vocabulary early.
