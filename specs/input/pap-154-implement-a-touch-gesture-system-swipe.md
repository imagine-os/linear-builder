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
blockedBy: ["PAP-20", "PAP-150", "PAP-260", "PAP-476"]
blocks: []
key: "input/touch-gestures"
url: "https://linear.app/paperos/issue/PAP-154/implement-a-touch-gesture-system-swipe-pinch-long-press-with-haptics"
source: "Linear snapshot 2026-09-17T15:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T14:58:05.711Z"
model: "claude-sonnet-5"
effort: "high"
---

# PAP-154: Implement a touch gesture system (swipe, pinch, long-press) with haptics on mobile targets

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / high — Build M

**Goal**

Make PaperOS feel native on phones and tablets: swipe to reveal row actions, pinch to zoom, long-press for context menus, pull to refresh and edge swipe, with haptics on Tauri mobile. Gestures are recognised through the shared abstraction so they compose with mouse and pen.

**Scope**

In:

* `packages/input/src/gestures/`: `useTap`, `useLongPress`, `useSwipe`, `usePinch`, `usePan` (momentum, rubber-band), `usePullToRefresh`, `useEdgeSwipe`, all on `usePointerSurface` (PAP-150); `@use-gesture/react` only for pinch and wheel maths if the ADR chose it.
* `GestureArena` arbitrating ownership (scroll vs swipe vs pan) with the PAP-150 thresholds.
* `packages/ui`: `SwipeableRow`, `PinchZoomView`, `PullToRefresh`, `BottomSheet` (snap points, focus trap from PAP-152, falls back to `Dialog` on desktop).
* `haptic('selection'|'impact-light'|'impact-medium'|'success'|'warning'|'error')` mapped to `@tauri-apps/plugin-haptics` (PAP-260), `navigator.vibrate`, else no-op; respects preference and reduced motion.
* Touch-target audit: interactive elements at least 44 × 44 CSS px under `pointer: coarse`.

Out: pen behaviour (PAP-157), reordering (PAP-155), OS webview navigation gestures.

**Spec**

* Recognisers return spreadable handlers and state; every gesture emits `start/move/end/cancel` with `{ pointers, delta, velocity, scale, center }`.
* `touch-action` per surface (`pan-y` for lists, `none` for canvases); arena cancels when the browser scrolls.
* `SwipeableRow`: reveal at 30 percent, commit at 60 percent or velocity over 0.5 px/ms; actions also in the overflow `Menu`; announces "Actions revealed".
* `PinchZoomView`: scale 0.5 to 8, double-tap toggles 1× and 2×, `ctrl`+wheel on desktop, single transform layer; emits `viewport` for PAP-132 and PAP-141.
* Haptics only on commits, at most 10 per second.

**Interface contract**

Exposes: recogniser hooks above with `GestureState` type, `GestureArena` and `useGestureArena()`, components above (`BottomSheet` `snapPoints`, `onDismiss`; `SwipeableRow` `leading`, `trailing`, `onCommit`), `haptic()` and `HapticKind`, `viewport` event `{ scale, x, y }`, Playwright fixture `touchTargets(page)` for PAP-82. Consumes: `usePointerSurface`, `THRESHOLDS`, capabilities (PAP-150), haptics plugin and safe-area insets (PAP-259, PAP-260), `Menu` and `Dialog` (PAP-237), focus trap (PAP-152), `LiveAnnouncer` (PAP-152).

**Definition of done**

* Tauri Android and iOS builds demonstrate swipe, pinch, long-press and pull-to-refresh with haptics; device or emulator video attached.
* Touch-target audit passes on all `packages/ui` stories.
* `docs/platform/input/gestures.md` with the arbitration table; changelog; Linear comment with video and Storybook links.

**Test plan**

* Vitest: arena arbitration with synthetic pointer sequences (vertical then horizontal locks direction, third finger ignored, nested pull-to-refresh claimed only at outer scroll top), thresholds and velocity maths, haptic rate limit and no-op path.
* Playwright with `hasTouch: true` at 320, 375 and 768: `page.touchscreen` swipe reveals and commits; CDP `Input.dispatchTouchEvent` two-finger pinch scales the view; long-press opens the context menu and suppresses the native one; bottom sheet snaps and dismisses; screenshots attached.
* Storybook: stories under `iphone14` and `ipad` viewports with axe; reduced-motion variant.
* Visual: Gate 3 captures of the four components at 320, 375 and 768, both themes.

**Demo**

On the Android emulator build, swipe a row left to reveal Archive and feel the tick, long-press a card for its menu, pinch the canvas, pull the list down to refresh; on desktop the same row exposes the actions in its overflow menu. Under two minutes.

**Edge cases**

* Swipe that turns: direction locks after 10 px.
* Haptics denied: silent no-op.
* Landscape 320 px height: sheet minimum snap adapts.
* Long-press on a link: native menu kept unless a handler exists.

**Dependencies**

PAP-150, PAP-20 (hard, encoded; children PAP-258 to PAP-260). Soft: PAP-67, PAP-152. Consumed by PAP-132, PAP-165, PAP-167, PAP-62, PAP-155.

**Agent**

Builder: Nova with Forge (Tauri Smith) for haptics and device builds. Reviewer: Sentinel (Visual Inspector on device videos, Edge Case Hunter).

**Size**

M: recognisers are standard; device testing and arbitration take the time.
