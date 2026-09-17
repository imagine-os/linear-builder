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
blocks: ["PAP-155", "PAP-156", "PAP-158", "PAP-330"]
key: "input/focus-management"
url: "https://linear.app/paperos/issue/PAP-152/implement-robust-focus-management-roving-tabindex-and-skip-links"
source: "Linear snapshot 2026-09-17T15:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T13:41:38.648Z"
model: "claude-sonnet-5"
effort: "high"
---

# PAP-152: Implement robust focus management, roving tabindex and skip links across all layouts

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / high — Build M

**Goal**

Guarantee keyboard users never lose their place: predictable focus order through nav, sidebar, main and inspector, roving tabindex in composite widgets, skip links, and focus restoration after dialogs, route changes and live updates. Screen-reader conformance (PAP-156), spatial navigation (PAP-158) and drag-and-drop (PAP-155) rely on it.

**Scope**

In:

* `packages/input/src/focus/`: `FocusRegion` (landmark region with entry point and `F6` cycling), `useRovingTabIndex(items, { orientation, loop, typeahead })`, `FocusScope` (trap and restore on the PAP-67 focus-scope primitive), `useFocusRestore(key)`, `FocusRing` styles from PAP-66, `useGridFocus` for PAP-165, shared `LiveAnnouncer`.
* Skip links rendered by `AppFrame` (PAP-70); `F6`/`shift+F6` as commands `focus.nextRegion|prevRegion` (PAP-151).
* Route-change policy: focus the `h1` or `[data-focus-entry]`, announce the title; back navigation restores by `data-focus-key`.
* Live-update policy: remote changes never steal focus; removed element → nearest sibling → region entry.
* Audit `pnpm a11y:focus-order <url>` writing JSON and a screenshot strip for PAP-82.

Out: real AT testing (PAP-156), 2D spatial focus (PAP-158), component keyboard behaviour in primitives.

**Spec**

* Roving: one item `tabindex=0`; arrows per orientation, `Home/End`, 500 ms typeahead, virtualised lists via `getItemElement(index)`.
* `FocusScope { trap, restoreFocus, autoFocus: 'first'|'container'|selector }`; nested scopes form a stack; top scope owns `Tab`.
* Ring only on `:focus-visible`; programmatic focus shows the ring after keyboard modality (PAP-150).
* Regions registered by `AppFrame` slots `nav`, `sidebar`, `main`, `inspector`, `commandbar`, `statusbar`; detached windows (PAP-262) form their own region set.
* Grid: `role="grid"`, arrows across cells, `Enter` edits, `Escape` cancels.

**Interface contract**

Exposes: `FocusRegion`, `useFocusRegions()`, `useRovingTabIndex`, `FocusScope`, `useFocusRestore`, `useGridFocus({ rows, cols, getCell })`, `LiveAnnouncer` with `announce(text, { politeness, dedupeKey })` and `useAnnounce()` (single shared instance; PAP-155, PAP-141, PAP-144 and PAP-158 must use it), DOM contracts `data-focus-entry`, `data-focus-key`, `data-focus-region`, commands `focus.*`, CLI `a11y:focus-order` output `{ url, width, order: [{ selector, label, region }] }`. Consumes: `AppFrame` slot names (PAP-70), focus-scope primitive and `Dialog` (PAP-236, PAP-237), ring tokens (PAP-66), `defineCommand` (PAP-151), `useLastInputModality` (PAP-150), `WindowManager` window ids (PAP-262).

**Definition of done**

* Skip links, `F6` cycling and route-change focus work in the template app; focus-order strips at 375 and 1280 attached.
* `useGridFocus` demo keeps focus in a 1,000-row virtual grid across scrolling and remote row insertion.
* `docs/platform/input/focus.md` with the policy table; changelog; Linear comment with demo link and strips.

**Test plan**

* Vitest (jsdom): roving orientation, loop, typeahead buffer, disabled skipping, virtualised `getItemElement`; scope stack push/pop and restore target fallback chain; `LiveAnnouncer` dedupe within 10 s.
* Playwright: `Tab` sequences with `document.activeElement` assertions through nav → main → inspector at 1280 and nav → main → drawer at 375; `F6` cycles; route change focuses `h1` and the live region text equals the title; remote row deletion (via `/__test`, PAP-240) moves focus to the next row with the announcement; dialog close restores to the trigger or falls back to region entry.
* axe: `focus-order-semantics`, `skip-link`, `tabindex` on all Storybook stories.
* Visual: focus-ring states captured in three themes (Gate 3).

**Demo**

Load the template app, press `Tab` once and use “Skip to main content”, press `F6` three times to cycle regions, open a record dialog and `Escape` back to the same row, navigate to another page and hear the title announced (screen reader or the live-region devtools panel). Under two minutes.

**Edge cases**

* Focused row deleted mid-typeahead: next row, announced.
* Menu trigger unmounted: fall back to region entry.
* Detached inspector: `F6` cycles within that window only.
* iframes: single stop, no trap.
* Nested autofocus: only the top scope wins; dev warning.

**Dependencies**

PAP-70 (hard, encoded). Soft: PAP-67, PAP-66, PAP-151, PAP-150, PAP-262, PAP-240. Blocks PAP-156, PAP-158, PAP-155; consumed by PAP-165, PAP-142.

**Agent**

Builder: Iris (Motion and Input Stylist) for regions and ring styling with Nova for hooks. Reviewer: Sentinel (Code Reviewer, Visual Inspector).

**Size**

M: many small behaviours that must agree; testing is the bulk.
