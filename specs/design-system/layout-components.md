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
blockedBy: ["PAP-16", "PAP-238", "PAP-67"]
blocks: ["PAP-124", "PAP-152"]
key: "design-system/layout-components"
url: "https://linear.app/paperos/issue/PAP-70/build-layout-components-appframe-splitpane-inspector-commandbar"
source: "plan/specs/bucket-2.json (round-1 canonical spec JSON)"
---

# PAP-70: Build layout components: AppFrame, SplitPane, Inspector, CommandBar, ResponsiveGrid

**Goal**

Build the structural components that page specs place content into: `AppFrame` (the grid the router shell renders), `SplitPane`, `Inspector`, `CommandBar` and `ResponsiveGrid`. They replace the plain divs `app-shell/router-layouts` shipped with, respond to container queries rather than viewport, and give every app the same resizable, collapsible, keyboard-operable frame.

**Scope**

In:
- `packages/ui/src/layout/` components: `AppFrame` (areas nav, sidebar, main, inspector, statusbar, commandbar overlay), `SplitPane` (horizontal/vertical, draggable divider, min/max, collapse, persisted sizes), `Inspector` (right-hand detail panel with header, tabs slot, sticky footer; becomes a drawer under `lg`), `CommandBar` (top overlay container with input slot, results list, footer hints; logic supplied by `input/command-registry`), `ResponsiveGrid` (auto-fit card grid with `minItemWidth` and gap tokens).
- `Drawer` and `Sheet` helpers used by collapse behaviour.
- Persistence of pane sizes and collapsed state in `localStorage` under `pos.layout.<appId>.<routeId>`.
- Container-query utilities via named containers `shell`, `sidebar`, `main`, `inspector` (matching `app-shell/breakpoints-windows`).

Out: window detach (`app-shell/breakpoints-windows`), focus order rules (`input/focus-management`, but ship sane defaults), command execution, table layouts.

**Spec**

- `AppFrame` props: `{ nav?, sidebar?, inspector?, statusbar?, commandbar?, children, sidebarWidth = 280, inspectorWidth = 360, collapse: { sidebar: 'md', inspector: 'lg' } }`; renders `<header>`, `<nav>`, `<aside>`, `<main id="main">` landmarks.
- Below the collapse width a slot renders inside `Drawer` toggled by buttons that `AppFrame` injects into the top bar; state exposed through `useAppFrame()` (`toggle('sidebar')`, `isCollapsed`).
- `SplitPane`: divider is a `role="separator"` with `aria-valuenow`, `aria-orientation`, keyboard arrows move 16px, `Shift` 64px, `Home/End` collapse; double-click resets; pointer events via `pointerdown` capture (works for touch and pen).
- `Inspector`: `title`, `onClose`, `tabs?: {id,label,content}[]`, `footer?`; `Escape` closes when focused; announces open/close via `aria-live` region.
- `CommandBar`: portal overlay, `open` controlled, input with `role="combobox"` and listbox results (`cmdk`-style, but only the shell), `aria-activedescendant` managed, max height 60vh, full-screen under `md`.
- `ResponsiveGrid`: `grid-template-columns: repeat(auto-fill, minmax(min(100%, var(--min)), 1fr))`.
- Everything styled with tokens; no fixed pixel breakpoints, only `@container`.
- Register each with `meta.ts` spec IDs `ui.appFrame`, `ui.splitPane`, `ui.inspector`, `ui.commandBar`, `ui.responsiveGrid` for `design-system/component-spec-mapping`.

**Definition of done**

- `apps/web` `AppShell` from `app-shell/router-layouts` switched to `AppFrame`; example routes still pass their Playwright tests.
- Stories for every component including collapsed and RTL variants; `play` tests for SplitPane keyboard resize and Inspector open/close.
- Screenshots of the frame at all seven widths in light and dark; Inspector drawer proven at 1024 and below.
- Vitest for persistence key and size clamping; axe clean.
- `docs/design/layout.md` with diagrams of slot names; CHANGELOG entry.
- Linear comment with Storybook and Pages preview links.

**Edge cases**

- Both sidebar and inspector open at 768: only one drawer at a time; opening one closes the other.
- Persisted pane size larger than the current container: clamp on mount, never overflow.
- Zoom at 200 percent: container widths shrink so collapse rules still trigger correctly.
- Touch drag on divider must not scroll the page (`touch-action: none` on the handle only).
- Nested `SplitPane` inside `Inspector`: separate persistence keys via `id` prop, required when nested.
- `prefers-reduced-motion`: drawer slides become fades.

**Dependencies**

`design-system/primitives` (Button, Tabs, Sheet), `app-shell/router-layouts` (slot contract) hard. Soft: `app-shell/device-matrix-research` breakpoints, `input/command-registry` (fills CommandBar), `app-shell/breakpoints-windows` (detach buttons). Unblocks `spec-builder/spec-editor-ui`, `identity/staff-console-shell`, `input/focus-management`.

**Agent**

Built by Iris (Component Crafter) with Forge consulting on the router contract. Reviewed by Sentinel (Visual Inspector across the matrix, Code Reviewer).

**Size**

M: five components, but SplitPane and CommandBar carry real interaction complexity.
