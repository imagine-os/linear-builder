---
identifier: "PAP-651"
title: "Gesture recognisers and arena: useTap, useLongPress, useSwipe, usePinch, usePan, usePullToRefresh, useEdgeSwipe on the pointer surface with ownership arbitration"
project: "input"
projectName: "Multi-Input Control & Accessibility"
phase: "P1"
type: "Build"
priority: 2
surfaces: ["Customer"]
milestone: "Touch, pen, gamepad"
state: "Backlog"
parent: "PAP-154"
children: []
blockedBy: ["PAP-20", "PAP-150", "PAP-260", "PAP-476"]
blocks: ["PAP-329", "PAP-345", "PAP-652"]
key: "r4/input/gesture-recognisers-and-arena"
url: "https://linear.app/paperos/issue/PAP-651/gesture-recognisers-and-arena-usetap-uselongpress-useswipe-usepinch"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:51:51.012Z"
model: "claude-sonnet-5"
effort: "high"
estimate: 3
dueDate: "2026-09-27"
cycle: null
---

# PAP-651: Gesture recognisers and arena: useTap, useLongPress, useSwipe, usePinch, usePan, usePullToRefresh, useEdgeSwipe on the pointer surface with ownership arbitration

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / high — Build M

**Goal**

First half of PAP-154, testable entirely in Vitest and Playwright on Linux: the recogniser hooks and the `GestureArena` that decides whether a touch is a scroll, a swipe or a pan, so the phone components in the sibling and the views (timeline pinch, kanban drag) share one arbitration model.

**Scope**

In: `packages/input/src/gestures/{arena,useTap,useLongPress,useSwipe,usePinch,usePan,usePullToRefresh,useEdgeSwipe,types}.ts`; `GestureArena` and `useGestureArena()`; `@use-gesture/react` only for pinch and wheel maths if the PAP-150 ADR chose it; `touch-action` guidance table; unit and Playwright suites.

Out: components, haptics and device videos (sibling), pen behaviour (PAP-157), reordering (PAP-155).

**Spec**

* Every recogniser builds on `usePointerSurface` (PAP-150) and emits `start|move|end|cancel` with `GestureState { pointers, delta, velocity, scale, center, direction }`; thresholds from PAP-150 `THRESHOLDS` (tap slop 8/12 px, long-press 500 ms, drag start 4/10 px).
* `GestureArena`: recognisers claim ownership after direction lock (10 px); vertical intent yields to native scroll (`touch-action: pan-y`), horizontal locks to swipe or pan; a third finger is ignored; nested arenas resolve innermost first, and pull-to-refresh is claimed only when the outer scroll container is at top.
* `usePinch`: scale 0.5 to 8 with `ctrl`+wheel desktop equivalent and double-tap toggle, emitting `viewport { scale, x, y }` for PAP-132 and PAP-345; `usePan`: momentum with friction 0.95 and rubber-band at bounds; `useEdgeSwipe`: 20 px edge zones with the OS back gesture respected on iOS.
* Long-press suppresses the native context menu only when a handler claims it; a long-press on a link keeps the native menu.
* All recognisers accept `enabled` and `disabledWhen: 'reducedMotion'`-style options and return spreadable handlers plus state; SSR safe.

**Interface contract**

Provides: recogniser hooks, `GestureArena`, `useGestureArena()`, `GestureState`, `touch-action` table (docs), `viewport` event type. Consumes: `usePointerSurface`, `THRESHOLDS`, capabilities (PAP-150). Consumed by the sibling, PAP-329 (long-press to drag), PAP-345 (pinch zoom), PAP-132 canvas, PAP-619.

**Definition of done**

* Vitest and Playwright suites green on Linux; `docs/platform/input/gestures.md` arbitration table; changelog; Linear comment with the API for PAP-345 and PAP-132.

**Test plan**

* Unit: arena arbitration with synthetic pointer sequences (vertical then horizontal locks direction, third finger ignored, nested pull-to-refresh claimed only at outer scroll top); threshold and velocity maths; momentum and rubber-band; pinch scale clamps; double-tap timing.
* Playwright `hasTouch` at 320, 375 and 768 using `@paperos/input/testing`: swipe reveals a test surface while a vertical drag scrolls; CDP two-finger pinch scales; long-press fires at 500 ms and not at 400 ms.
* E2E: none beyond the Playwright suite (the sibling covers components).

**Demo**

Reviewer opens the Storybook gesture playground at 375 with touch emulation, swipes, pinches and long-presses while the arena panel shows which recogniser owns the gesture. Under two minutes.

**Edge cases**

* Swipe that turns: direction locks after 10 px.
* `pointercancel` from the browser during scroll: gesture cancels cleanly.
* Pinch with one finger lifted: continues as pan from the remaining pointer.
* Landscape 320 px height: edge zones scale to 16 px.

**Dependencies**

PAP-150 (hard). Blocks the sibling, PAP-329 (soft: long-press helper), PAP-345 (soft: pinch).

**Agent**

Builder: Nova (Product Systems Engineer). Reviewer: Sentinel (Edge Case Hunter).

**Size**

M: one session.

*Round 4 critique fix (2026-09-18):* resolved 1 round-4 file key in this description to Linear identifiers: `r4/tables/gallery-and-list-views` = PAP-619.
