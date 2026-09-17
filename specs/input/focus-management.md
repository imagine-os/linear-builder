---
identifier: "PAP-152"
title: "Implement robust focus management, roving tabindex and skip links across all layouts"
project: "input"
projectName: "Multi-Input Control & Accessibility"
phase: "P1"
type: "Build"
priority: 1
surfaces: ["Customer"]
milestone: "Keyboard and command system"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-70"]
blocks: ["PAP-155", "PAP-156", "PAP-158"]
key: "input/focus-management"
url: "https://linear.app/paperos/issue/PAP-152/implement-robust-focus-management-roving-tabindex-and-skip-links"
source: "plan/specs/bucket-5.json (round-1 canonical spec JSON)"
---

# PAP-152: Implement robust focus management, roving tabindex and skip links across all layouts

**Goal**

Guarantee that keyboard users never lose their place: a predictable focus order through nav, sidebar, main content and inspector; roving tabindex inside composite widgets; skip links; focus restoration after dialogs, route changes and live updates. This is the base that screen-reader conformance, gamepad spatial navigation and the command system all rely on.

**Scope**

In:
- `packages/input/src/focus/`: `FocusRegion` (landmark-level region with an id, entry point and `F6` cycling), `useRovingTabIndex(items, { orientation, loop, typeahead })`, `FocusScope` (trap and restore, built on `@radix-ui/react-focus-scope` or Base UI's equivalent chosen in `design-system/primitives`), `useFocusRestore(key)` for route changes, `FocusRing` styles from `design-system/tokens`.
- Skip links: "Skip to main content", "Skip to navigation", "Skip to inspector" rendered by `AppFrame` (`design-system/layout-components`), visible on focus.
- Region cycling: `F6` / `shift+F6` move between regions (registered as commands `focus.nextRegion` / `focus.prevRegion` in `input/command-registry`); `Escape` inside a region returns to its entry point.
- Route-change policy: on navigation, focus the page `h1` (or `[data-focus-entry]`) and announce the page title via a live region; back navigation restores the previously focused element by stable `data-focus-key`.
- Live update policy: remote changes (`realtime/record-sync`) never steal focus; if the focused element is removed, focus moves to its nearest surviving sibling, then the region entry.
- Audit tooling: `pnpm a11y:focus-order <url>` Playwright script that tabs through a page and outputs the focus order as a JSON and screenshot strip, used by `quality/playwright-matrix`.

Out: screen-reader testing on real AT (`input/screen-reader`), spatial 2D focus (`input/gamepad`), component-level keyboard behaviour already in primitives.

**Spec**

- Roving tabindex: one item `tabindex=0`, others `-1`; arrows move per orientation, `Home/End` jump, typeahead over `aria-label`/text with 500 ms buffer; disabled items skipped unless `focusableWhenDisabled`; works with virtualised lists via `getItemElement(index)` and `scrollIntoView`.
- `FocusScope` options: `trap`, `restoreFocus`, `autoFocus: 'first'|'container'|selector`; nested scopes form a stack; the top scope owns `Tab`.
- Focus visibility: `:focus-visible` ring only; programmatic focus after keyboard interaction shows the ring (track last input modality via `input/input-abstraction` capabilities); after pointer interaction it does not.
- Regions registered by `AppFrame` slots (`nav`, `sidebar`, `main`, `inspector`, `commandbar`, `statusbar`) with `aria-label`s; detached Tauri windows (`app-shell/breakpoints-windows`) form their own region set.
- Tables: grid navigation (`role="grid"`, arrow keys across cells, `Enter` edits, `Escape` cancels) is provided as `useGridFocus` for `tables/grid-view`.
- Announcements: one shared `LiveAnnouncer` (`polite` and `assertive` regions) with de-duplication, exported for all packages.
- Tests run in Playwright with `page.keyboard.press('Tab')` sequences and `document.activeElement` assertions.

**Definition of done**

- Skip links, `F6` cycling and route-change focus work in the template app; Playwright tests at 375 (collapsed drawers) and 1280 px; focus-order strips attached for both.
- Vitest tests for roving tabindex (orientation, loop, typeahead, virtualised), scope stack and restore.
- `useGridFocus` demo with a 1,000-row virtual grid keeps focus after scrolling and remote row insertion.
- axe rules `focus-order-semantics`, `skip-link`, `tabindex` pass on all Storybook stories.
- Docs `docs/platform/input/focus.md` with the policy table (route change, dialog, live update, deletion).
- Changelog entry and Linear comment with demo link and focus strips.

**Edge cases**

- Focused row deleted by another user mid-typeahead: focus moves to the next row and announces "Row removed by Ada".
- Dialog opened from a menu item that unmounts: restore target gone → fall back to the menu trigger, then region entry.
- Drawer collapse at narrow widths moves the sidebar into a `Drawer`; region order stays nav → main → drawer.
- Tauri detached inspector: `F6` cycles within that window only; `mod+shift+]` (from `app-shell/breakpoints-windows`) switches windows.
- iframes (embedded views from `tables/view-sharing`): treat as a single stop; do not trap.
- Autofocus fights: only the top `FocusScope` may autofocus; nested autofocus logs a dev warning.

**Dependencies**

- `design-system/layout-components` (AppFrame slots), `design-system/primitives` (focus scope primitive), `design-system/tokens` (ring), `input/command-registry` (F6 commands), `input/input-abstraction` (modality). Consumed by `input/screen-reader`, `input/gamepad`, `input/drag-drop`, `tables/grid-view`.

**Agent**

Builder: Iris (Motion and Input Stylist sub-agent) for regions and ring styling with Nova for hooks. Reviewer: Sentinel (Code Reviewer, Visual Inspector).

**Size**

M: many small behaviours that must agree; testing is the bulk.
