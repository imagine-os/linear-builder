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
blocks: ["PAP-151", "PAP-154", "PAP-155", "PAP-157", "PAP-158", "PAP-289", "PAP-329"]
key: "input/input-abstraction"
url: "https://linear.app/paperos/issue/PAP-150/design-a-unified-input-event-abstraction-so-components-handle-mouse"
source: "Linear snapshot 2026-09-17T13:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T04:53:32.024Z"
---

# PAP-150: Design a unified input event abstraction so components handle mouse, touch, pen and gamepad uniformly

**Goal**

Define one input model every PaperOS component uses so mouse, touch, pen and gamepad behave consistently without per-component device checks. Output: a spec plus a small typed core in `packages/input` that gestures (PAP-154), drag-and-drop (PAP-155), pen (PAP-157) and gamepad (PAP-158) build on, fixing the vocabulary once.

**Scope**

In:

* Spec `docs/platform/input/abstraction.md`: event vocabulary, coordinate spaces, capture semantics, capability detection, mapping to Pointer Events, Touch fallback, Gamepad API and keyboard.
* `packages/input/src/core/`: `InputEvent` union (`press | move | release | cancel | wheel | key | gamepad`), `Pointer`, `Modifiers`, `usePointerSurface(ref, handlers, { capture, passive })` translating `pointerdown/move/up/cancel` and `lostpointercapture` with capture handled centrally.
* `useInputCapabilities()` → `{ coarsePointer, finePointer, hover, touchPoints, penSeen, gamepadConnected, keyboardSeen }` from media queries plus observed events, mirrored as `data-input-*` on `<html>`.
* Thresholds table as exported constants: tap slop 8 px fine / 12 px coarse, long-press 500 ms, double-press 300 ms, drag start 4 px / 10 px.
* Library decision: `@use-gesture/react` vs standalone (default: thin standalone layer over Pointer Events; `@use-gesture` only for pinch and wheel maths in PAP-154).

Out: recognisers, drag-and-drop, spatial focus, voice, the command registry.

**Spec**

* Every pointer carries `client`, `page` and `surface` coordinates in CSS pixels.
* `press` calls `setPointerCapture`; `release` or `cancel` fires exactly once per pointer id; `cancel` on `pointercancel`, window blur and hidden tab.
* Keyboard: `key` normalised to `Key { code, key, modifiers, repeat }` and portable chord string `mod+shift+k` (`mod` = Cmd on macOS, Ctrl elsewhere).
* Gamepad: `requestAnimationFrame` polling emits `gamepad` events (standard mapping) and a synthetic `gamepad-cursor` pointer when PAP-158 enables cursor mode.
* Pen: `pressure`, `tiltX/Y`, `twist`, barrel button as `buttons` bit 2; while a pen is active, touch presses on the same surface are ignored for 300 ms.
* Biome rule `no-raw-touch-handlers` flags `onTouchStart`/`onMouseDown` in `packages/ui` and `packages/views`.

**Interface contract**

Exposes (package `@paperos/input`): types `InputEvent`, `Pointer { id, type: 'mouse'|'touch'|'pen'|'gamepad-cursor', client, page, surface, pressure, tiltX, tiltY, twist, buttons, isPrimary }`, `Modifiers`, `Key`, `Chord` (string) with `parseChord()`, `formatChord(platform)`, `matchChord(event, chord)` used verbatim by PAP-151 and PAP-153; `usePointerSurface`, `useInputCapabilities`, `useLastInputModality()` (keyboard vs pointer, used by PAP-152 focus rings); constants `THRESHOLDS`; CSS hooks `[data-input-coarse]`, `[data-input-hover]`; lint rule. Consumes: nothing at runtime; `breakpoints.json` device classes from PAP-14 for the capability playground.

**Definition of done**

* Spec merged and linked from PAP-76 guidelines.
* Storybook "Input Playground" showing active pointers, pressure and capabilities at 375 (touch emulation) and 1280; screenshots attached.
* Biome rule enabled with zero violations; `data-input-*` used by the Button primitive for coarse hit targets (PAP-236).
* Developer changelog entry; Linear comment with the playground link.

**Test plan**

* Vitest with synthetic `PointerEvent`s: capture set on press, exactly one release or cancel per pointer, cancel on blur and hidden tab, slop thresholds by pointer type, palm-rejection window, pressure clamp to \[0, 1\], hover (`buttons === 0`) distinguished from drag.
* Chord tests: `parseChord('mod+shift+k')` on macOS and Linux `navigator.platform` mocks, non-Latin layout matching by `code`, sequence tokens.
* Gamepad: mocked `navigator.getGamepads` yields normalised sticks with deadzone and standard buttons.
* Visual: playground story captured at 375 and 1280 in both themes; axe on the story.
* Lint: fixture file with `onTouchStart` fails `biome check`.

**Demo**

Open Storybook Input Playground at 1280, move the mouse and read the pointer panel; switch to iPhone emulation and tap with two fingers to see two pointers and `coarsePointer: true`; press `mod+shift+k` and see the normalised chord. Under two minutes.

**Edge cases**

* Touch-then-mouse devices: capabilities update live.
* `pointercancel` on scroll: treated as release without action; `touch-action` documented.
* Long-press context menu: suppressed only when a handler claims it.
* iOS Safari missing `pointerrawupdate`: polling covers it.

**Dependencies**

None hard (Ready). Informs PAP-67 hit targets. Blocks PAP-151, PAP-154, PAP-155, PAP-157, PAP-158; consumed by PAP-152, PAP-132.

**Agent**

Builder: Nova (Product Systems Engineer, owner of multi-input). Reviewer: Iris (Motion and Input Stylist) for the component contract; Sentinel (Code Reviewer).

**Size**

S: a spec and a thin core; the value is deciding the vocabulary early.
