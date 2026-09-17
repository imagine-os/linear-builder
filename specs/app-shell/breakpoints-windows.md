---
identifier: "PAP-21"
title: "Build responsive breakpoint matrix and multi-monitor window manager that detaches panels into OS windows"
project: "app-shell"
projectName: "Universal App Shell & Repo Template"
phase: "P1"
type: "Build"
priority: 1
surfaces: ["Customer", "Staff"]
milestone: "Desktop and mobile shells build"
state: "Backlog"
parent: null
children: ["PAP-263", "PAP-261", "PAP-262"]
blockedBy: ["PAP-14", "PAP-16", "PAP-19", "PAP-257"]
blocks: ["PAP-145", "PAP-23"]
key: "app-shell/breakpoints-windows"
url: "https://linear.app/paperos/issue/PAP-21/build-responsive-breakpoint-matrix-and-multi-monitor-window-manager"
source: "plan/specs/bucket-0.json (round-1 canonical spec JSON)"
---

# PAP-21: Build responsive breakpoint matrix and multi-monitor window manager that detaches panels into OS windows

**Goal**

Implement the responsive layer from the device matrix as container queries and a window manager that lets any panel detach into its own OS window on desktop, drag across monitors, remember placement, and re-dock, so staff can spread one app over several screens.

**Scope**

In:
- `packages/core/src/layout/breakpoints.css` and Tailwind v4 theme variables generated from `BREAKPOINTS` (`app-shell/device-matrix-research`); `@container` names for `shell`, `sidebar`, `main`, `inspector`, `panel`.
- `useBreakpoint()` and `useContainerSize(ref)` hooks (ResizeObserver based).
- `packages/core/src/windows/`: `WindowManager` with `detach(panelId)`, `dock(panelId)`, `list()`, `focus(id)`, `moveToDisplay(id, displayId)`; persistence in `tauri-plugin-window-state` plus our own `layouts` store in `localStorage` keyed by display topology hash.
- Detached window renders route `/_window/<panelId>` inside a minimal chrome shell (no nav) via `app-shell/router-layouts`.
- Web fallback: `window.open` popups with the same route; `BroadcastChannel` for state (full sync via `realtime/multi-window-sync`).
- Panel header affordance: "Pop out" / "Dock" button, keyboard `Ctrl/Cmd+Shift+P`.
- Layout presets: save/restore named window arrangements.

Out: kiosk auto-launch (`app-shell/linux-kiosk`), data synchronisation between windows beyond UI state (realtime project), mobile.

**Spec**

- Tauri side: `WebviewWindowBuilder` per detached panel, label `panel-<id>`, `parent` unset, `decorations true`, remembers `outerPosition/size`; `monitor()`/`available_monitors()` exposed via command `list_displays` returning `{ id, name, bounds, scale, primary }`.
- Display topology hash = sorted `${name}:${w}x${h}@${scale}` joined; on mismatch fall back to primary display centre.
- Store shape: `{ panels: { [id]: { state: 'docked'|'detached', bounds?, display? } }, presets: { [name]: PanelsState } }`; Zod-validated; migrations by `version`.
- Docking: closing a detached window docks it; `dock()` from the main window closes the child.
- Focus and z-order: `focus(id)` brings window forward; main window shows a chip per detached panel.
- Container query classes: `@container shell (min-width: 1024px)` etc.; utilities `cq-md:` mapped in Tailwind via plugin.
- Breakpoints also drive `AppShell` collapse rules defined in `app-shell/router-layouts` (replace the interim media queries).

**Definition of done**

- On Linux and macOS: detach inspector, move to a second display, quit, relaunch; window reappears on the same display (recording).
- Unplug the second display and relaunch: window recovers to primary (recording).
- Web: pop-out opens popup, state mirrors via BroadcastChannel (Playwright multi-page test).
- Vitest: topology hash, store migrations, dock/detach reducer.
- Screenshots of the shell at all 7 widths plus a two-display composite; `quality/playwright-matrix` config updated to use `breakpoints.json`.
- `docs/shell/windows.md`; CHANGELOG; Linear comment with recordings and preview.

**Edge cases**

- Popup blockers on web: show inline hint, keep panel docked.
- Display scale changes (1x to 2x) while running: re-query bounds on `scale-changed`.
- Detached window closed by OS (crash): main detects via `onCloseRequested`/heartbeat and re-docks.
- Panel that requires main-window context (selection) opens with empty state and a message.
- More than 8 detached windows: warn about memory; cap at 12.
- Wayland does not allow apps to position windows: persist size only, document.

**Dependencies**

`app-shell/tauri-desktop`, `app-shell/device-matrix-research` (hard), `app-shell/router-layouts` (window route). Pairs with `realtime/multi-window-sync` for data coherence; consumed by `app-shell/linux-kiosk`, `design-system/layout-components`.

**Agent**

Built by Forge (Tauri Smith) with Nova consulting on sync boundaries. Reviewed by Sentinel (Visual Inspector across the matrix, Edge Case Hunter for topology changes).

**Size**

L: cross-platform window APIs behave differently and persistence must survive topology changes.
