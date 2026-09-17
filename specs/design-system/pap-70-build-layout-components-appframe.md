---
identifier: "PAP-70"
title: "Build layout components: AppFrame, SplitPane, Inspector, CommandBar, ResponsiveGrid"
project: "design-system"
projectName: "Design System"
phase: "P1"
type: "Build"
priority: 1
surfaces: ["Developer"]
milestone: "Tokens and primitives"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-16", "PAP-67", "PAP-238", "PAP-447"]
blocks: ["PAP-124", "PAP-152", "PAP-376"]
key: "design-system/layout-components"
url: "https://linear.app/paperos/issue/PAP-70/build-layout-components-appframe-splitpane-inspector-commandbar"
source: "Linear snapshot 2026-09-17T15:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T14:54:02.243Z"
model: "claude-sonnet-5"
effort: "high"
---

# PAP-70: Build layout components: AppFrame, SplitPane, Inspector, CommandBar, ResponsiveGrid

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / high — Build M

**Goal**

Build the structural components page specs place content into: `AppFrame`, `SplitPane`, `Inspector`, `CommandBar` and `ResponsiveGrid`. They replace the plain divs PAP-16 shipped with, respond to container queries rather than the viewport, and give every app the same resizable, collapsible, keyboard-operable frame. Milestone moved to "Tokens and primitives" because PAP-152 and PAP-63 need it by 2026-09-23.

**Scope**

* In: `packages/ui/src/layout/` components, `Drawer` and `Sheet` helpers, pane-size persistence, named containers `shell`, `sidebar`, `main`, `inspector`, `meta.ts` for each, stories with `play` tests, docs.
* Out: window detach (PAP-21), focus-order rules (PAP-152; sane defaults here), command execution (PAP-151), table layouts.

**Spec**

* `AppFrame` props `{ nav?, sidebar?, inspector?, statusbar?, commandbar?, banner?, children, sidebarWidth = 280, inspectorWidth = 360, collapse: { sidebar: 'md', inspector: 'lg' } }`; renders `<header>`, `<nav>`, `<aside>`, `<main id="main">` landmarks; below the collapse width a slot renders in `Drawer`, toggles injected into the top bar; `useAppFrame()` exposes `toggle(slot)`, `isCollapsed(slot)`.
* `SplitPane`: horizontal or vertical, divider `role="separator"` with `aria-valuenow` and `aria-orientation`, arrows move 16 px, Shift 64 px, Home/End collapse, double-click resets, `pointerdown` capture for touch and pen, `touch-action: none` on the handle only.
* `Inspector`: `title`, `onClose`, `tabs?`, `footer?`; Escape closes when focused; open/close announced via `aria-live`; drawer under `lg`.
* `CommandBar`: portal overlay, controlled `open`, `role="combobox"` input with listbox results and managed `aria-activedescendant`, max height 60vh, full screen under `md`; logic injected by PAP-151.
* `ResponsiveGrid`: `grid-template-columns: repeat(auto-fill, minmax(min(100%, var(--min)), 1fr))`.
* Persistence in `localStorage` under `pos.layout.<appId>.<routeId>`; clamp on mount. Styling via tokens and `@container` only.

**Interface contract**

* Provides: components with spec IDs `ui.appFrame`, `ui.splitPane`, `ui.inspector`, `ui.commandBar`, `ui.responsiveGrid`, `ui.drawer`, `ui.sheet`; `useAppFrame()`; slot names `nav`, `sidebar`, `main`, `inspector`, `statusbar`, `commandbar`, `banner` (the contract PAP-16 layouts and PAP-120 codegen `useLayout` use); container names; persistence key format.
* Requires: PAP-236 Button, PAP-238 Tabs, PAP-237 Sheet behaviour, PAP-16 slot contract, PAP-14 breakpoints (soft).
* Consumers: PAP-63 console, PAP-62 portal, PAP-124 spec editor, PAP-152 focus rules, PAP-21 detach buttons, PAP-151 palette, PAP-165 record panel.

**Definition of done**

* `apps/web` `AppShell` switched to `AppFrame`; example routes still pass their Playwright tests.
* Stories for every component including collapsed and RTL; `play` tests for SplitPane keyboard resize and Inspector open/close.
* Screenshots of the frame at all seven widths in light and dark; Inspector drawer proven at 1024 and below.
* Vitest for persistence key and clamping; axe clean.
* `docs/design/layout.md` with slot diagrams; changelog entry; Linear comment with Storybook and Pages links.

**Test plan**

* Unit: persistence key format, clamp to container, collapse threshold resolution at 200 percent zoom (container widths).
* Interaction: divider keyboard steps and Home/End, double-click reset, Inspector Escape, one-drawer-at-a-time at 768.
* Visual: frame at seven widths × two themes; RTL at 1280.
* Touch: drag divider on an emulated touch device does not scroll the page.

**Demo**

Open Storybook "Layout/AppFrame playground", resize the browser from 1920 to 375 watching sidebar then inspector collapse into drawers, drag and keyboard-resize the split, reload and see sizes persist. Under one minute.

**Edge cases**

* Sidebar and inspector both open at 768: one drawer at a time.
* Persisted size larger than container: clamped on mount.
* Nested SplitPane inside Inspector: `id` prop required for a separate key.
* Reduced motion: drawer slides become fades.

**Dependencies**

PAP-67 children (hard), PAP-16 (hard). Soft: PAP-14, PAP-151, PAP-21.

**Agent**

Iris (Component Crafter) with Forge consulting on the router contract. Reviewed by Sentinel (Visual Inspector across the matrix, Code Reviewer).

**Size**

M.
