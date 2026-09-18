---
identifier: "PAP-511"
title: "Shell layout presets and session restore: persisted panel sizes and collapse state per device, last route on launch, named presets synced per user and a Reset layout command"
project: "app-shell"
projectName: "Universal App Shell & Repo Template"
phase: "P1"
type: "Build"
priority: 2
surfaces: ["Customer"]
milestone: "Multi-monitor and PWA polish"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-16", "PAP-57", "PAP-226", "PAP-261"]
blocks: []
key: "r4/app-shell/shell-layout-presets"
url: "https://linear.app/paperos/issue/PAP-511/shell-layout-presets-and-session-restore-persisted-panel-sizes-and"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:51:43.804Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 3
dueDate: "2026-09-29"
cycle: null
---

# PAP-511: Shell layout presets and session restore: persisted panel sizes and collapse state per device, last route on launch, named presets synced per user and a Reset layout command

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Build M

**Goal**

VS Code, Linear and Arc reopen exactly where you left them; PaperOS today forgets sidebar width, inspector state and the last route on every launch. PAP-262 persists detached windows and PAP-260 restores the mobile route, but the everyday layout state of the main window has no owner. This issue gives the shell a `LayoutStore` with per-device persistence, per-user synced presets and session restore.

**Scope**

In:

* `packages/core/src/shell/layoutStore.ts`: Zod-validated `{ version, panels: { sidebar: { width, collapsed }, inspector: { width, open } }, lastRoute, presets: { [name]: PanelState } }` in `localStorage` (web) and the PAP-262 store (desktop), with versioned migrations.
* Sync: presets and the default preset saved to `user.settings.layout` through `settings.update` (PAP-57 profile) and merged on sign-in; device-local sizes stay local.
* Session restore: on launch, if the last route is still valid and the user is signed in, navigate there (desktop and PWA standalone only; browsers keep URL semantics); a `Continue where you left off` toast when the route needs data.
* Commands registered with PAP-151: `layout.savePreset`, `layout.applyPreset`, `layout.reset`; `Reset layout` in the user menu slot; keyboard `Ctrl/Cmd+Shift+L` cycles presets.
* Resize handles on sidebar and inspector (PAP-70 `SplitPane`) writing to the store with debounce.

Out: detached window persistence (PAP-262), tabs or split main area (deferred), server-side layout for kiosk (PAP-23).

**Spec**

* Store writes are debounced 250 ms and never block paint; reads are synchronous at boot to avoid layout shift.
* Container queries (PAP-261) still win: a saved 400 px sidebar collapses under `md` and restores above.
* Presets are named, at most 10 per user, and include slot visibility but never record data or search params other than `ShellSearch`.
* Sign-out clears synced presets from the device; demo users (PAP-363) never sync.

**Interface contract**

Provides: `useLayoutStore`, `LayoutState` schema, commands `layout.*`, `user.settings.layout` shape; consumed by PAP-70 (`SplitPane` handles), PAP-262 (shares the store file), PAP-23 (kiosk presets), PAP-151 (commands), PAP-63 (console default preset).

Consumes: `AppShell` and `ShellSearch` (PAP-16), container hooks (PAP-261), sessions and settings (PAP-57), command registry (PAP-151, soft), `SplitPane` (PAP-70, soft).

**Definition of done**

* Resize the sidebar, reload: width restored; quit the desktop app on `/settings`, relaunch: lands on `/settings` (recordings).
* Save a preset on one browser, sign in on another: preset available; `layout.reset` restores defaults.
* Vitest for migrations and merge; Playwright at 375 and 1280; screenshots; `docs/shell/layout.md`; CHANGELOG; Linear comment.

**Test plan**

* Unit: store migrations v1 to v2; merge of synced presets with local sizes; preset cap; container-query override.
* E2E: Playwright: resize, reload, restore; save and apply preset; desktop restore via PAP-508.

**Demo**

Reviewer drags the inspector wider, opens the grid, quits the desktop app, relaunches and is back on the grid with the wide inspector; `Ctrl+Shift+L` switches to the "Review" preset with the sidebar hidden. Under 90 seconds.

**Edge cases**

* Last route no longer exists after an upgrade: fall back to the audience home with a toast.
* Store corrupted: schema failure resets to defaults and reports through PAP-368.
* Two tabs open: last writer wins via the `BroadcastChannel` used by PAP-145.

**Dependencies**

Hard: PAP-16, PAP-261, PAP-57. Soft: PAP-70, PAP-151, PAP-262, PAP-145. Feeds PAP-23, PAP-63.

**Agent**

Builder: Forge (Platform Engineer) with Iris on handles. Reviewer: Sentinel (Visual Inspector).

**Size**

M: one session.

*Round 4 critique fix (2026-09-18):* resolved 1 round-4 file key in this description to Linear identifiers: `r4/app-shell/tauri-e2e-harness` = PAP-508.
