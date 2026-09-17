---
identifier: "PAP-158"
title: "Add gamepad and TV-remote navigation for kiosk and TV modes with spatial focus"
project: "input"
projectName: "Multi-Input Control & Accessibility"
phase: "P2"
type: "Build"
priority: 3
surfaces: ["Customer"]
milestone: "Voice and accessibility certification"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-150", "PAP-152"]
blocks: []
key: "input/gamepad"
url: "https://linear.app/paperos/issue/PAP-158/add-gamepad-and-tv-remote-navigation-for-kiosk-and-tv-modes-with"
source: "plan/specs/bucket-5.json (round-1 canonical spec JSON)"
---

# PAP-158: Add gamepad and TV-remote navigation for kiosk and TV modes with spatial focus

**Goal**

Make the 10-foot UI work: a PaperOS app running in kiosk or TV mode (from `app-shell/linux-kiosk`) can be driven entirely with a gamepad, TV remote or the arrow keys of a keyboard, using spatial focus that moves to the geometrically nearest element instead of DOM order. This also gives motor-impaired users who rely on switch or D-pad devices a working path through every page.

**Scope**

In:
- `packages/input/src/spatial/`: `SpatialNavigationProvider` implementing 2D focus search over registered focusable elements (weighted by distance and axis alignment, with "sticky" columns), `useFocusable({ group, onEnter, onLongEnter })`, `FocusGroup` (grid/list/menu semantics, memory of last focused child), `enableSpatialNavigation({ trigger: 'gamepad'|'always' })`.
- Gamepad layer: polling from `input/input-abstraction` (`gamepad` events, standard mapping) mapped to actions: D-pad/left stick → move, `A` → activate, `B` → back, `X` → context menu, `Y` → command palette, bumpers → region cycling (`F6` equivalent), triggers → page scroll, `Start` → help overlay; stick repeat with acceleration; deadzone 0.25.
- TV remote and keyboard: arrow keys plus `Enter`/`Escape`/`Backspace` map to the same actions when spatial mode is active; `input/command-registry` commands `spatial.move.*`, `spatial.activate`, `spatial.back` so keymaps can remap.
- Cursor mode: holding `LB` shows a virtual pointer (`gamepad-cursor` pointer type) for canvases and maps where spatial focus makes no sense.
- Kiosk/TV theme adjustments with Iris: larger focus ring (4 px, high contrast), minimum 48 px targets and 24 px type at `tv` breakpoint from `app-shell/device-matrix-research`; screensaver/idle return to home after a configurable timeout.
- On-screen keyboard `SpatialKeyboard` for text fields when no physical keyboard is detected.

Out: controller vibration beyond `haptic()` no-op, custom button remapping UI (covered by `input/keymaps` later), Smart TV native apps.

**Spec**

- Search algorithm: candidates are visible focusables in the current group, then parent groups; score = Euclidean distance to the exit edge centre + 3× off-axis offset; ties break by DOM order; `data-spatial-priority` can pin an element.
- Groups expose `enterFrom(direction)` returning the child to focus (last-focused, first, or nearest), and `onExit(direction)` may block (e.g., a horizontal carousel swallows left/right at its ends).
- Scroll handling: focusing an element scrolls it into view with a 10% margin using `scrollIntoView({ block: 'nearest' })`; virtualised lists expose `scrollToIndex` for off-screen movement.
- Activation dispatches a real `click` on the focused element so existing components need no changes; long-press `A` (600 ms) fires `contextmenu`.
- Overlays: a `Dialog` or `BottomSheet` becomes the active root group; `B` closes it (through the component's `onClose`).
- Detection: spatial mode enables automatically on the first gamepad input or when `?input=tv`/kiosk config is set; a small controller glyph appears in the status bar; mouse movement disables cursor lock but keeps spatial mode until a preference changes it.
- Help overlay lists controller mappings with glyphs (Xbox, PlayStation, generic) chosen from `gamepad.id`.

**Definition of done**

- Kiosk build (`app-shell/linux-kiosk`) drives the template app end to end (sign in with PIN, navigate, open record, edit a select field, run a palette command) using an Xbox controller; video attached.
- Playwright tests with a mocked `navigator.getGamepads` at 1280 and 1920 px asserting focus paths through a grid, a sidebar and a dialog; screenshots of the TV theme focus ring.
- Vitest tests for the scoring function (deterministic fixtures), group entry memory and deadzone/repeat timing.
- `SpatialKeyboard` enters text into an input and a Tiptap comment field.
- Docs `docs/platform/input/spatial-and-gamepad.md` with the mapping table and a guide to grouping pages.
- Changelog entry and Linear comment with video and demo links.

**Edge cases**

- Two controllers connected: the last one used is active; input from the other is ignored until it moves.
- Focusable element appears under the current focus after a live update: no jump; the next move re-evaluates.
- Grid with ragged rows: moving down from the last cell of a longer row lands on the nearest cell, not nothing.
- Disconnected controller mid-interaction: spatial mode stays, keyboard arrows keep working; a toast notes the disconnect.
- Elements with `visibility: hidden` or inside `inert` containers are excluded from search.
- Hold-to-repeat on a stick while a dialog opens: repeat cancels to avoid skipping through the dialog.

**Dependencies**

- `input/focus-management` (focus ring, regions, announcer), `input/input-abstraction` (gamepad events, cursor pointer), `input/command-registry`, `app-shell/linux-kiosk` and `app-shell/device-matrix-research` (TV breakpoint), `design-system/theming` (TV theme), `design-system/primitives` (Dialog `onClose`).

**Agent**

Builder: Nova, with Iris (Motion and Input Stylist) on the TV theme. Reviewer: Sentinel (Visual Inspector, Edge Case Hunter); Forge (Ops Runner) verifies the kiosk build.

**Size**

M: the spatial algorithm is compact; grouping every layout correctly is the work.
