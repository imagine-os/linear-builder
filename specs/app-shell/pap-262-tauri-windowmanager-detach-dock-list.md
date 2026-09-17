---
identifier: "PAP-262"
title: "Tauri WindowManager: detach, dock, list_displays and topology-hash persistence"
project: "app-shell"
projectName: "Universal App Shell & Repo Template"
phase: "P1"
type: "Build"
priority: 1
surfaces: ["Developer", "Staff"]
milestone: "Desktop and mobile shells build"
state: "Backlog"
parent: "PAP-21"
children: []
blockedBy: ["PAP-16", "PAP-19", "PAP-261"]
blocks: ["PAP-263"]
key: "child/PAP-21/7"
url: "https://linear.app/paperos/issue/PAP-262/tauri-windowmanager-detach-dock-list-displays-and-topology-hash"
source: "Linear snapshot 2026-09-17T13:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T06:22:35.093Z"
model: "claude-sonnet-5"
effort: "high"
---

# PAP-262: Tauri WindowManager: detach, dock, list_displays and topology-hash persistence

**Goal**

Implement the desktop `WindowManager` so any panel can detach into its own OS window, move across monitors, be remembered per display topology and re-dock, using Tauri `WebviewWindowBuilder` and a `list_displays` command.

**Scope**

In: `packages/core/src/windows/manager.ts` (`detach`, `dock`, `list`, `focus`, `moveToDisplay`, `subscribe`); Rust `list_displays` returning `{ id, name, bounds, scale, primary }`; store `{ panels, presets }` Zod-validated with versioned migrations in `localStorage` plus `tauri-plugin-window-state`; route `/_window/$panelId` with a chrome-less layout; cap 12 windows.

Out: web fallback and panel header UI (child 3).

**Spec**

* Topology hash = sorted `${name}:${w}x${h}@${scale}`; mismatch falls back to primary centre.
* Closing a detached window docks it; `dock()` from main closes the child.
* Heartbeat every 5 s detects crashed children and re-docks.
* Events over `BroadcastChannel('paperos-windows')` with `paperos:panel-state` payloads (PAP-145 extends).

**Interface contract**

Provides: `WindowManager`, `PanelState`, `list_displays` command, `/_window/$panelId` route, channel name and event. Consumes: crate (PAP-19), breakpoints (child 1), routes (PAP-16). Consumed by PAP-23 (display enumeration), PAP-145.

**Definition of done**

* Linux and macOS recordings: detach, move to display two, quit, relaunch on display two; unplug and relaunch recovers to primary.
* Vitest for hash, migrations and reducer; Rust test for `list_displays`.
* Two-display composite screenshot.

**Test plan**

* Unit: topology hash ordering; migration v1 to v2 fixture; reducer for detach, dock, crash re-dock; cap at 12.
* Rust: `list_displays` against a mocked monitor list.
* E2E: Tauri WebDriver on Linux for detach and dock.
* Manual recorded: two-display flows on Linux and macOS.

**Demo**

Reviewer clicks Pop out on the inspector (button from child 3 or a temporary dev command), drags it to a second monitor, quits and relaunches; the inspector returns to that monitor. Under 90 seconds.

**Edge cases**

* Scale change at runtime: re-query on `scale-changed`.
* Wayland forbids positioning: persist size only.
* More than 8 windows: memory warning.

**Dependencies**

PAP-19, child 1 (hard), PAP-16. Blocks child 3; feeds PAP-23, PAP-145.

**Agent**

Built by Forge (Tauri Smith) with Nova on the channel contract. Reviewed by Sentinel.

**Size**

M
