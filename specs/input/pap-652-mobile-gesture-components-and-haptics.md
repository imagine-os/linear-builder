---
identifier: "PAP-652"
title: "Mobile gesture components and haptics: SwipeableRow, PinchZoomView, PullToRefresh, BottomSheet, haptic() over the Tauri plugin and the touch-target audit"
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
blockedBy: ["PAP-152", "PAP-237", "PAP-260", "PAP-645", "PAP-651"]
blocks: ["PAP-167", "PAP-619", "PAP-671"]
key: "r4/input/mobile-gesture-components-and-haptics"
url: "https://linear.app/paperos/issue/PAP-652/mobile-gesture-components-and-haptics-swipeablerow-pinchzoomview"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:23.199Z"
model: "claude-sonnet-5"
effort: "high"
estimate: 3
dueDate: "2026-09-27"
cycle: null
---

# PAP-652: Mobile gesture components and haptics: SwipeableRow, PinchZoomView, PullToRefresh, BottomSheet, haptic() over the Tauri plugin and the touch-target audit

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / high — Build M

**Goal**

Second half of PAP-154: the four phone components lists, canvases and sheets need, the `haptic()` port mapped to Tauri mobile, and the 44 px touch-target audit, proven on the Android and iOS builds with video.

**Scope**

In: `packages/ui/src/mobile/{SwipeableRow,PinchZoomView,PullToRefresh,BottomSheet}.tsx` with `meta.ts` spec ids; `packages/input/src/haptics.ts` (`haptic(kind)` over `@tauri-apps/plugin-haptics`, `navigator.vibrate`, else no-op); Playwright `touchTargets(page)` audit run over all `packages/ui` stories; device videos.

Out: recognisers and arena (sibling), OS webview navigation gestures, desktop drawers (PAP-70).

**Spec**

* `SwipeableRow leading trailing onCommit`: reveal at 30 percent, commit at 60 percent or velocity over 0.5 px/ms; actions duplicated in an overflow `Menu` (PAP-237) for non-touch and screen readers; announces "Actions revealed" (PAP-152 announcer); `haptic('impact-light')` on commit.
* `PinchZoomView`: single transform layer, scale 0.5 to 8, double-tap toggles 1× and 2×, `ctrl`+wheel on desktop, emits `viewport` for PAP-132 and PAP-141; `PullToRefresh onRefresh`: spinner from PAP-71 `Skeleton` tokens, `haptic('selection')` at threshold, respects reduced motion.
* `BottomSheet snapPoints onDismiss`: drag handle, snap by velocity, focus trap from PAP-152 `FocusScope`, falls back to `Dialog` above `md`; reads `--pos-keyboard-inset` (PAP-645); `inert` on the page behind.
* `haptic(kind)` kinds `selection|impact-light|impact-medium|success|warning|error`; only on commits, at most 10 per second, disabled by the PAP-72 motion setting `never` and by user preference; silent no-op when unavailable.
* Touch-target audit: every interactive element at least 44 × 44 CSS px under `pointer: coarse` (24 px with spacing allowed per WCAG 2.5.8 exception, documented per component); failures fail `storybook:test`.

**Interface contract**

Provides: four components with spec ids `ui.swipeableRow`, `ui.pinchZoomView`, `ui.pullToRefresh`, `ui.bottomSheet`; `haptic()` and `HapticKind` (in `contract-input` as `HapticPort`); `touchTargets(page)` audit results artefact. Consumes: recognisers and arena (sibling), haptics plugin and safe areas (PAP-260), `Menu` and `Dialog` (PAP-237), focus trap and announcer (PAP-152), keyboard inset (PAP-645, soft), motion setting (PAP-72). Consumed by PAP-619 (swipe), PAP-167 (kanban pager), PAP-132 (pinch), PAP-70 (sheet mode).

**Definition of done**

* Tauri Android and iOS builds demonstrate swipe, pinch, long-press menu and pull-to-refresh with haptics; device or emulator video attached; touch-target audit passes on all stories.
* Storybook stories under `iphone14` and `ipad` viewports with axe and a reduced-motion variant; Gate 3 captures at 320, 375 and 768 in both themes; changelog; Linear comment with videos.

**Test plan**

* Unit: swipe commit maths; snap-point selection by velocity; haptic rate limit and no-op path; sheet fallback decision by container width.
* Playwright `hasTouch` via `@paperos/input/testing`: swipe reveals and commits; pinch scales; sheet snaps and dismisses; `context.setOffline` does not break pull-to-refresh error state.
* E2E: on the Android emulator build (nightly, PAP-371 or local): swipe a row to archive and feel the tick, pull to refresh, open a bottom sheet and dismiss by drag.

**Demo**

On the Android emulator, reviewer swipes a row left to reveal Archive, long-presses a card for its menu, pinches the canvas, pulls the list down to refresh; on desktop the same row exposes the actions in its overflow menu. Under two minutes.

**Edge cases**

* Haptics denied or unsupported: silent no-op, no permission prompt loop.
* Sheet at 320 px landscape: minimum snap adapts.
* Swipe on an RTL locale: leading and trailing flip.
* Pull-to-refresh inside a nested scroll: claimed only at outer top (sibling rule).

**Dependencies**

Sibling recognisers (hard), PAP-260 (hard for haptics and device proofs; web fallbacks may land first), PAP-237 (hard), PAP-152 (hard). Soft: PAP-645, PAP-72. Blocks gallery/list swipe actions and PAP-167's phone pager.

**Agent**

Builder: Nova (Product Systems Engineer) with Forge (Tauri Smith) for device builds. Reviewer: Sentinel (Visual Inspector (device videos), Edge Case Hunter).

**Size**

M: one session.

*Round 4 critique fix (2026-09-18):* resolved 2 round-4 file keys in this description to Linear identifiers: `r4/input/virtual-keyboard-viewport` = PAP-645, `r4/tables/gallery-and-list-views` = PAP-619.
