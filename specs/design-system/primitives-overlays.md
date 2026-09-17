---
identifier: "PAP-237"
title: "Overlay components: Dialog, AlertDialog, Popover, Tooltip, Menu, Toast"
project: "design-system"
projectName: "Design System"
phase: "P0"
type: "Build"
priority: 1
surfaces: ["Developer"]
milestone: "Tokens and primitives"
state: "Backlog"
parent: "PAP-67"
children: []
blockedBy: ["PAP-236"]
blocks: ["PAP-238"]
key: "design-system/primitives/overlays"
url: "https://linear.app/paperos/issue/PAP-237/overlay-components-dialog-alertdialog-popover-tooltip-menu-toast"
source: "Linear snapshot 2026-09-17T06:03Z (round-2 issue)"
---

# PAP-237: Overlay components: Dialog, AlertDialog, Popover, Tooltip, Menu, Toast

**Goal**

Ship the layered components with correct focus, dismiss and stacking behaviour: Dialog, AlertDialog, Popover, Tooltip, Menu (dropdown and context) and Toast with its provider.

**Scope**

* In: six components on the headless primitives, `ToastProvider` and `useToast`, portal root resolution per document (Tauri multi-window), dismiss layers that do not close parents, full-screen sheet mode under `md`, stories and interaction tests.
* Out: Drawer and Sheet layout helpers (PAP-70), motion presets (PAP-72; use opacity only here).

**Spec**

* Dialog: focus trap, `Escape` closes unless `preventClose`, scroll lock, returns focus to trigger, `role="dialog"` with `aria-labelledby`; sheet mode under 768 px via container query.
* AlertDialog: destructive tone, initial focus on cancel, `confirmLabel` required.
* Popover: anchored with collision handling, `modal` option, arrow optional.
* Tooltip: 500 ms delay, instant on group, never for essential content; `IconButton` gets Tooltip automatically from `label`.
* Menu: keyboard navigation, typeahead, submenus, checkbox and radio items, `shortcut` slot, context-menu trigger.
* Toast: queue of max 3, `push({ title, body?, tone, action?, durationMs = 6000 })`, pause on hover and focus, `role="status"`, bottom-right on desktop and top on mobile.

**Interface contract**

* Provides: components with spec IDs `ui.dialog`, `ui.alertDialog`, `ui.popover`, `ui.tooltip`, `ui.menu`, `ui.toast`; `ToastProvider`, `useToast()`; `getPortalRoot(doc)` used by PAP-70 and PAP-21 windows.
* Requires: sibling infrastructure child (`cn`, variants, Button); PAP-66 tokens.

**Definition of done**

* Six components merged; `play` tests for Dialog, Menu and Toast pass in `storybook:test`.
* Nested Dialog inside Popover inside Menu closes only the innermost on Escape (test).
* Screenshots of each overlay at 375 and 1280 light and dark; sheet mode at 375.
* `vitest-axe` clean including portal content.

**Test plan**

* Interaction: focus trap cycle, focus return, Escape and outside-click rules, Toast pause on hover.
* Unit: queue overflow, duration, `preventClose`.
* Visual: overlays at two widths; high-contrast borders.

**Demo**

Open Storybook "Overlays/Nested": open a Menu, then a Popover, then a Dialog, press Escape three times and watch each close in order; push four toasts and see the queue cap at three. Under one minute.

**Edge cases**

* Portal target in a detached Tauri window: resolved via the trigger's `ownerDocument`.
* Tooltip on touch: long-press shows, tap outside hides.
* Toast while a Dialog is open: rendered above the dialog, still announced.

**Dependencies**

Sibling infrastructure child (hard).

**Agent**

Built by Iris (Component Crafter). Reviewed by Sentinel (Visual Inspector, Code Reviewer).

**Size**

M.
