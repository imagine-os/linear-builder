---
identifier: "PAP-158"
title: "Add gamepad and TV-remote navigation for kiosk and TV modes with spatial focus"
project: "input"
projectName: "Multi-Input Control & Accessibility"
phase: "P2"
type: "Build"
priority: 4
surfaces: ["Customer"]
milestone: "Voice and accessibility certification"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-150", "PAP-152"]
blocks: []
key: "input/gamepad"
url: "https://linear.app/paperos/issue/PAP-158/add-gamepad-and-tv-remote-navigation-for-kiosk-and-tv-modes-with"
source: "Linear snapshot 2026-09-17T13:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T06:23:14.202Z"
model: "claude-sonnet-5"
effort: "low"
---

# PAP-158: Add gamepad and TV-remote navigation for kiosk and TV modes with spatial focus

**Goal**

Deferred to v0.2 by the Execution Schedule (NJ-14 stop-loss 09-27 can reinstate). Not claimable before 10-01.

Make the 10-foot UI work: a PaperOS app in kiosk or TV mode (PAP-23) driven entirely by gamepad, TV remote or arrow keys, using spatial focus that moves to the geometrically nearest element. This also gives motor-impaired users on switch or D-pad devices a working path through every page.

**Scope**

In:

* `packages/input/src/spatial/`: `SpatialNavigationProvider` (2D search over registered focusables), `useFocusable({ group, onEnter, onLongEnter })`, `FocusGroup` (grid, list, menu semantics with last-child memory), `enableSpatialNavigation({ trigger: 'gamepad'|'always' })`.
* Gamepad mapping on PAP-150 events: D-pad and left stick move, `A` activate, `B` back, `X` context menu, `Y` palette, bumpers cycle regions (PAP-152), triggers scroll, `Start` help; stick repeat with acceleration, deadzone 0.25.
* Arrow keys, `Enter`, `Escape`, `Backspace` map to the same actions; commands `spatial.move.*`, `spatial.activate`, `spatial.back` (PAP-151).
* Cursor mode: hold `LB` for a virtual pointer (`gamepad-cursor`) on canvases.
* TV theme with Iris: 4 px focus ring, 48 px targets, 24 px type at the `tv` breakpoint (PAP-14); idle return to home; `SpatialKeyboard` on-screen keyboard.

Out: vibration beyond `haptic()`, remap UI (PAP-153), native TV apps.

**Spec**

* Score = distance to the exit edge centre + 3 × off-axis offset; ties by DOM order; `data-spatial-priority` pins.
* Groups expose `enterFrom(direction)` and `onExit(direction)`; overlays become the active root; `B` calls `onClose`.
* Activation dispatches a real `click`; long `A` (600 ms) fires `contextmenu`; focus scrolls into view with a 10 percent margin.
* Spatial mode enables on first gamepad input or `?input=tv`; a controller glyph appears in the status bar.

**Interface contract**

Exposes: `SpatialNavigationProvider`, `useFocusable`, `FocusGroup`, `useSpatialMode()`, `scoreCandidates(from, direction, candidates)` (pure, tested), DOM attributes `data-spatial-group`, `data-spatial-priority`, gamepad mapping table JSON per controller family, commands `spatial.*`, `SpatialKeyboard` with `DictationTarget`-compatible insertion (shared with PAP-159), help overlay component. Consumes: `gamepad` events and `gamepad-cursor` pointer (PAP-150), `FocusRegion` list and `LiveAnnouncer` (PAP-152), `defineCommand` (PAP-151), kiosk config and TV breakpoint (PAP-23, PAP-14), theme tokens (PAP-75), `Dialog` and `BottomSheet` `onClose` (PAP-237, PAP-154).

**Definition of done**

* Kiosk build drives the template app end to end (PIN sign-in, navigate, open record, edit a select, run a palette command) with an Xbox controller; video attached.
* `SpatialKeyboard` enters text into an input and a Tiptap comment.
* Screenshots of the TV focus ring at 1280 and 1920; `docs/platform/input/spatial-and-gamepad.md` with mapping table; changelog; Linear comment with video and demo links.

**Test plan**

* Vitest: `scoreCandidates` on fixture layouts (ragged grid lands on nearest cell, sticky column, priority pin, hidden and `inert` excluded), group entry memory, deadzone and repeat timing with fake timers, two-controller arbitration.
* Playwright with mocked `navigator.getGamepads` at 1280 and 1920: focus path through a grid, sidebar and dialog matches the expected selector sequence; `B` closes the dialog; disconnect mid-interaction keeps keyboard arrows working and shows a toast; `?input=tv` enables spatial mode without a controller.
* Integration: kiosk compose build boots with `?input=tv` and the smoke flow passes headless.
* Visual: Gate 3 captures of the TV theme ring and help overlay at 1280 and 1920.

**Demo**

Load the template with `?input=tv` at 1920, use the arrow keys to move through the sidebar and grid, `Enter` a record, `Escape` back, hold `Start` (or `?`) for the mapping overlay; plug in a controller and repeat with the D-pad. Under two minutes.

**Edge cases**

* Element appears under focus after a live update: no jump.
* Repeat while a dialog opens: repeat cancels.
* Two controllers: last used wins.
* Carousel ends: `onExit` swallows left and right.

**Dependencies**

PAP-152, PAP-150 (hard, encoded). Soft: PAP-151, PAP-23, PAP-14, PAP-75, PAP-67, PAP-154. Consumed by PAP-159 (hold-space in TV mode).

**Agent**

Builder: Nova with Iris (Motion and Input Stylist) on the TV theme. Reviewer: Sentinel (Visual Inspector, Edge Case Hunter); Forge (Ops Runner) verifies the kiosk build.

**Size**

M: the algorithm is compact; grouping every layout correctly is the work.
