---
identifier: "PAP-645"
title: "Virtual keyboard handling on mobile: visualViewport tracking, keyboard-inset CSS, focused-field scroll-into-view and bottom-sheet and toolbar repositioning"
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
blockedBy: ["PAP-152", "PAP-260"]
blocks: ["PAP-154", "PAP-169", "PAP-619", "PAP-652"]
key: "r4/input/virtual-keyboard-viewport"
url: "https://linear.app/paperos/issue/PAP-645/virtual-keyboard-handling-on-mobile-visualviewport-tracking-keyboard"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:20:34.173Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 2
dueDate: "2026-09-27"
cycle: null
---

# PAP-645: Virtual keyboard handling on mobile: visualViewport tracking, keyboard-inset CSS, focused-field scroll-into-view and bottom-sheet and toolbar repositioning

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Build S

**Goal**

Forms, comments, the palette and grid editors are unusable on phones when the on-screen keyboard covers the focused field or the submit button. Own the one place that tracks the virtual keyboard and exposes its inset so every layout, sheet and sticky bar adjusts.

**Scope**

In: `packages/input/src/viewport/{useVirtualKeyboard,KeyboardInsetProvider,scrollIntoViewSafe}.ts`; CSS variable `--pos-keyboard-inset`; `interactive-widget=resizes-content` meta in `apps/web/index.html`; Tauri mobile plugin bridge for keyboard events (PAP-260); focus policy in PAP-152 extended with `ensureVisible`.

Out: custom on-screen keyboards (PAP-158 `SpatialKeyboard`), desktop, IME candidate windows.

**Spec**

* `useVirtualKeyboard()` returns `{ open, height, animating }` from `visualViewport` resize and scroll events (fallback: `innerHeight` delta over 150 px with a focused editable), debounced 50 ms; Tauri iOS and Android report through the plugin `keyboardWillShow|Hide` with the frame height.
* `KeyboardInsetProvider` writes `--pos-keyboard-inset` on `<html>` and toggles `data-keyboard-open`; `BottomSheet` (PAP-154), `CommandBar` full-screen mode (PAP-70), grid `BulkBar` (PAP-342), form sticky actions and toast position read it via `padding-bottom: max(env(safe-area-inset-bottom), var(--pos-keyboard-inset))`.
* `scrollIntoViewSafe(el)` scrolls the nearest scroll container so the element sits above the inset with 16 px margin, after the keyboard animation ends; PAP-152's focus policy calls it on every programmatic focus of an editable.
* `Enter` on a single-line field in a form submits only when `enterKeyHint` says so; `enterkeyhint` and `inputmode` attributes set by PAP-236 inputs from field type (`numeric`, `email`, `tel`, `decimal`).
* Body scroll lock while a sheet is open must not fight the keyboard: lock uses `overflow: hidden` on the scroll container, never `position: fixed` on `body`.

**Interface contract**

Provides: `useVirtualKeyboard`, `KeyboardInsetProvider`, `scrollIntoViewSafe`, CSS variable and data attribute contract, `inputmode` mapping table for field types. Consumes: focus policy (PAP-152), mobile plugin bridge and safe areas (PAP-260), `BottomSheet` (PAP-154), `CommandBar` (PAP-70), inputs (PAP-236). Consumed by PAP-169 forms, PAP-154 sheets, PAP-342 grid editing, PAP-131 comment composer.

**Definition of done**

* Demo form and comment composer stay visible with the keyboard open on iOS Safari, Android Chrome and both Tauri mobile builds (device or emulator video attached).
* Playwright with `hasTouch` and a mocked `visualViewport` proves the inset and scroll; screenshots at 375 with keyboard open and closed; `docs/platform/input/virtual-keyboard.md`; changelog.

**Test plan**

* Unit: height derivation from viewport events; debounce; fallback heuristic; `scrollIntoViewSafe` maths with nested scroll containers.
* Component: `BottomSheet` snap points shrink by the inset; sticky form actions reposition within one frame.
* E2E: focus the last field of the demo form at 375 with a mocked 300 px keyboard, assert it is visible above the inset and the submit button is reachable; palette input stays visible.

**Demo**

Reviewer opens the demo form on the Android emulator, taps the last field, sees it scroll above the keyboard with the submit bar riding on top, then opens the palette. Under two minutes.

**Edge cases**

* Landscape phone with 320 px height: sheet minimum snap adapts (PAP-154 rule) and the inset can exceed 50 percent.
* Keyboard closes while a toast animates: toast repositions after the animation.
* `visualViewport` unsupported (old WebView): fallback heuristic with a dev warning.
* Hardware keyboard on a tablet: no inset, `data-keyboard-open` stays false.

**Dependencies**

PAP-152 (hard, focus policy hook), PAP-260 (hard for the native bridge; web path may land first). Soft: PAP-154, PAP-70, PAP-236. Blocks PAP-169 forms on mobile, PAP-154 sheet behaviour.

**Agent**

Builder: Nova (Product Systems Engineer) with Forge (Tauri Smith) on the plugin. Reviewer: Sentinel (Visual Inspector).

**Size**

S: half a session.
