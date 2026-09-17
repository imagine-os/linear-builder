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
children: ["PAP-261", "PAP-262", "PAP-263"]
blockedBy: ["PAP-14", "PAP-16", "PAP-19", "PAP-257"]
blocks: ["PAP-23", "PAP-145"]
key: "app-shell/breakpoints-windows"
url: "https://linear.app/paperos/issue/PAP-21/build-responsive-breakpoint-matrix-and-multi-monitor-window-manager"
source: "Linear snapshot 2026-09-17T13:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T06:22:43.005Z"
model: null
effort: null
---

# PAP-21: Build responsive breakpoint matrix and multi-monitor window manager that detaches panels into OS windows

**Goal**

Umbrella: implement the responsive layer from PAP-14 as container queries and a window manager that lets any panel detach into its own OS window, move across monitors, remember placement and re-dock, so staff can spread one app over several screens. Three children; closes on the two-display integration test.

**Scope**

Children:

1. **PAP-261** — Container-query breakpoints and hooks (`breakpoints.css`, Tailwind v4 theme variables, `useBreakpoint`, `useContainerSize`; replaces PAP-16 interim media queries).
2. **PAP-262** — Tauri `WindowManager` (detach, dock, list, focus, `moveToDisplay`, `list_displays` command, topology-hash persistence).
3. **PAP-263** — Web pop-out fallback and panel affordances (`window.open`, `BroadcastChannel` mirror, "Pop out" button, chips, `/_window/<panelId>` route, docs).

Out: cross-window data coherence (PAP-145), kiosk launch (PAP-23).

**Spec**

* `@container` names `shell`, `sidebar`, `main`, `inspector`, `panel`; Tailwind utilities `cq-md:` via plugin.
* `WebviewWindowBuilder` per detached panel, label `panel-<id>`; `list_displays` returns `{ id, name, bounds, scale, primary }`.
* Topology hash = sorted `${name}:${w}x${h}@${scale}`; mismatch falls back to primary centre.
* Store `{ panels: { [id]: { state, bounds?, display? } }, presets }`, Zod-validated with `version` migrations, in `localStorage` plus `tauri-plugin-window-state`.
* Closing a detached window docks it; `dock()` closes the child; cap 12 detached windows.
* Keyboard `Ctrl/Cmd+Shift+P` toggles pop-out on the focused panel.

**Interface contract**

Provides (from `@paperos/core/layout` and `@paperos/core/windows`):

* `useBreakpoint(): BreakpointName`, `useContainerSize(ref)`, CSS custom properties `--bp-xs..--bp-3xl`.
* `WindowManager` with `detach(panelId)`, `dock(panelId)`, `list()`, `focus(id)`, `moveToDisplay(id, displayId)`, `subscribe(cb)`; type `PanelState`.
* Route `/_window/$panelId` in PAP-16's tree with a chrome-less layout.
* Event `paperos:panel-state` on `BroadcastChannel('paperos-windows')`, the channel PAP-145 extends.
* `ops/ci/breakpoints.json` unchanged; PAP-82 switches to it here.

Consumes: `BREAKPOINTS` (PAP-14), Tauri crate and `list_displays` stub (PAP-19), `AppShell` slots (PAP-16).

**Definition of done**

* All three children Done.
* Integration test on Linux and macOS: detach inspector, move to display two, quit, relaunch; window returns to display two; unplug display two, relaunch; window recovers to primary (recordings).
* Web: pop-out popup mirrors state via BroadcastChannel (Playwright multi-page).
* Screenshots at all seven widths plus a two-display composite; `docs/shell/windows.md`; CHANGELOG; Linear comment.

**Test plan**

* Unit: topology hash, store migrations v1 to v2, dock and detach reducer, breakpoint mapping from container width.
* Rust: `list_displays` against a mocked monitor list.
* Integration: Testing Library asserting `AppShell` switches `data-layout` by container width, not viewport.
* E2E: Playwright multi-page pop-out test; Tauri WebDriver test for detach and dock on Linux.
* Visual: seven widths plus 2560 ultra-wide; two-display composite from the recording.

**Demo**

Reviewer launches the desktop build, clicks "Pop out" on the inspector, drags it to a second monitor, quits and relaunches; the inspector reopens where it was. Closing the popped-out window docks it back. Under 2 minutes.

**Edge cases**

* Popup blockers on web: inline hint, panel stays docked.
* Scale change while running: re-query on `scale-changed`.
* Child window crash: main re-docks via `onCloseRequested` or heartbeat.
* Panel needing main-window selection opens with an empty state and message.
* Wayland forbids positioning: persist size only, documented.

**Dependencies**

PAP-14, PAP-19 (hard), PAP-16 (window route, now encoded). Pairs with PAP-145; consumed by PAP-23, PAP-70.

**Agent**

Built by Forge (Tauri Smith) with Nova consulting on the sync boundary. Reviewed by Sentinel.

**Size**

L as an umbrella; children are S, M, M.
