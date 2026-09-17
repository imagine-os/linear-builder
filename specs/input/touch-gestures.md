---
identifier: "PAP-154"
title: "Implement a touch gesture system (swipe, pinch, long-press) with haptics on mobile targets"
project: "input"
projectName: "Multi-Input Control & Accessibility"
phase: "P1"
type: "Build"
priority: 2
surfaces: ["Customer"]
milestone: "Touch, pen, gamepad"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-150", "PAP-20", "PAP-260"]
blocks: []
key: "input/touch-gestures"
url: "https://linear.app/paperos/issue/PAP-154/implement-a-touch-gesture-system-swipe-pinch-long-press-with-haptics"
source: "plan/specs/bucket-5.json (round-1 canonical spec JSON)"
---

# PAP-154: Implement a touch gesture system (swipe, pinch, long-press) with haptics on mobile targets

**Goal**

Make PaperOS feel native on phones and tablets: swipe to reveal row actions, pinch to zoom canvases and images, long-press for context menus, pull to refresh, edge swipe for navigation, all with haptic feedback on Tauri mobile. Gestures are recognised through the shared input abstraction so they compose with mouse and pen without device-specific code in components.

**Scope**

In:
- `packages/input/src/gestures/`: recognisers `useTap`, `useLongPress`, `useSwipe` (direction, velocity, threshold), `usePinch` (scale, origin, rotation), `usePan` with momentum and rubber-banding, `usePullToRefresh`, `useEdgeSwipe`; all built on `usePointerSurface` from `input/input-abstraction`, with `@use-gesture/react` 10.x used only for pinch/wheel maths if the abstraction ADR chose it.
- Gesture arbitration: a `GestureArena` decides ownership when several recognisers see the same pointers (scroll vs swipe vs pan), following the thresholds table (tap slop, long-press 500 ms, drag start 10 px coarse).
- Components in `packages/ui`: `SwipeableRow` (leading/trailing actions, snap points, keyboard and menu fallback), `PinchZoomView`, `PullToRefresh`, `BottomSheet` (drag handle, snap points, dismiss by swipe, falls back to Dialog on desktop).
- Haptics: `packages/input/src/haptics.ts` with `haptic('selection'|'impact-light'|'impact-medium'|'success'|'warning'|'error')` mapped to `@tauri-apps/plugin-haptics` on iOS/Android, `navigator.vibrate` on Android web, no-op elsewhere; respect a user preference and reduced-motion.
- Touch target audit: Playwright check that interactive elements are at least 44×44 CSS px under `pointer: coarse`.

Out: pen-specific behaviour (`input/pen`), drag-and-drop reordering (`input/drag-drop`), native navigation gestures inside the OS webview (documented, not implemented).

**Spec**

- Recogniser API returns handlers to spread and a state object; every gesture emits `start/move/end/cancel` with `{ pointers, delta, velocity, scale, center }`.
- `touch-action` is set per surface (`pan-y` for lists with horizontal swipes, `none` for canvases) and documented; the arena cancels a recogniser when the browser takes over scrolling (`pointercancel`).
- `SwipeableRow`: actions revealed at 30% width, committed at 60% or velocity > 0.5 px/ms, `Escape` or tap elsewhere closes; actions also available via the row's overflow `Menu` so no function is touch-only; announces "Actions revealed" via `LiveAnnouncer`.
- `PinchZoomView`: scale clamp 0.5–8, double-tap toggles 1×/2×, wheel+ctrl zoom on desktop, transform via CSS `transform` on a single layer for 60 fps; emits `viewport` for `collab/canvas-view` and `realtime/presence` viewport sharing.
- `BottomSheet`: snap points as fractions (`[0.4, 0.9]`), backdrop dismiss, `role="dialog"`, focus trap from `input/focus-management`, safe-area insets (`env(safe-area-inset-bottom)`).
- Haptics fire only on gesture commits (snap, threshold crossed), never on every move; at most 10 per second.
- Storybook stories use touch emulation (`viewport` addon `iphone14`, `ipad`) and the Playwright suite runs with `hasTouch: true`.

**Definition of done**

- Tauri Android and iOS builds (from `app-shell/tauri-mobile`) demonstrate swipe, pinch, long-press, pull-to-refresh with haptics; video attached from a device or emulator.
- Playwright touch tests at 320, 375 and 768 px using `page.touchscreen` and CDP `Input.dispatchTouchEvent` for multi-touch pinch; screenshots attached.
- Vitest tests for arena arbitration, thresholds and velocity math with synthetic pointer sequences.
- Touch-target audit passes on all `packages/ui` stories.
- Docs `docs/platform/input/gestures.md` with the arbitration table and `touch-action` guidance.
- Changelog entry and Linear comment with video and Storybook links.

**Edge cases**

- Swipe starts vertically then turns horizontal: arena locks direction after 10 px; no mid-gesture switch.
- Pinch with a third finger resting: use the two most recent pointers; ignore extras.
- Long-press on a link opens the native context menu: suppress only when a long-press handler is attached.
- Pull-to-refresh inside a nested scroll container: only the outermost at scroll top may claim it.
- Haptics API missing or denied: silent no-op, feature still works.
- Landscape phones with 320 px height: bottom sheet minimum snap adapts to viewport height.

**Dependencies**

- `input/input-abstraction` (pointer surface, thresholds), `app-shell/tauri-mobile` (targets, haptics plugin), `design-system/primitives` (Menu, Dialog), `input/focus-management` (trap). Consumed by `collab/canvas-view`, `tables/grid-view`, `tables/kanban-view`, `identity/customer-portal-shell`.

**Agent**

Builder: Nova with Forge (Tauri Smith) for the haptics plugin and device builds. Reviewer: Sentinel (Visual Inspector on device videos, Edge Case Hunter).

**Size**

M: recognisers are standard; device testing and arbitration take the time.
