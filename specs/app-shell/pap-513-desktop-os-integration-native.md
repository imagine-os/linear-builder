---
identifier: "PAP-513"
title: "Desktop OS integration: native notifications with actions, dock and taskbar badge counts, jump-list and dock-menu recents, and a global shortcut that summons the command bar"
project: "app-shell"
projectName: "Universal App Shell & Repo Template"
phase: "P2"
type: "Build"
priority: 4
surfaces: ["Staff"]
milestone: "Multi-monitor and PWA polish"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-136", "PAP-255", "PAP-725"]
blocks: []
key: "r4/app-shell/desktop-os-integration"
url: "https://linear.app/paperos/issue/PAP-513/desktop-os-integration-native-notifications-with-actions-dock-and"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:00.329Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 2
dueDate: null
cycle: null
---

# PAP-513: Desktop OS integration: native notifications with actions, dock and taskbar badge counts, jump-list and dock-menu recents, and a global shortcut that summons the command bar

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Build S

**Goal**

Deferred to v0.2 (past 2026-10-01). Linear and Slack desktop feel native because notifications, badges and recents come from the OS. PAP-255 ships menu and tray, PAP-136 the notification centre and PAP-151 shortcuts; the OS-level glue between them has no owner. This issue adds it once the notification centre exists.

**Scope**

In:

* `tauri-plugin-notification` bridge: PAP-136 in-app notifications mirrored to OS notifications when the window is unfocused, with `Open` and `Mark read` actions routed through `paperos://open/<route>` (PAP-257).
* Badge: unread count on the dock icon (macOS), taskbar overlay (Windows) and Unity launcher (Linux) through the window API; cleared when the inbox is opened.
* Recents: last five records or pages in the macOS dock menu and Windows jump list, fed by PAP-511 last-route history.
* `tauri-plugin-global-shortcut`: `Ctrl/Cmd+Shift+Space` shows the window and opens the command bar (PAP-151); configurable in `/settings/shortcuts` (PAP-153).

Out: mobile push (PAP-516), tray (PAP-255), notification preferences (PAP-136).

**Spec**

* OS notifications respect `notification_preference` (PAP-136) and quiet hours (PAP-324); never shown while the window is focused.
* Badge counts come from the same `notifications.unreadCount` query the bell uses; no second source of truth.
* Global shortcut registration failure (already taken) is logged and shown once in settings, never fatal.
* Capabilities limited to the main window; no wildcard permissions (PAP-255 rule).

**Interface contract**

Provides: `useOsNotifications`, badge updater, recents feed, global shortcut registration; consumed by PAP-136 (delivery channel `os`), PAP-151, PAP-153.

Consumes: crate and plugins (PAP-255), notification centre (PAP-136), deep links (PAP-257), command registry (PAP-151), recents (PAP-511).

**Definition of done**

* Linux and macOS recordings: comment mention while unfocused shows an OS notification; clicking opens the record; badge shows 1 then clears.
* Global shortcut summons the command bar from another app; Rust and TS tests; `docs/shell/desktop.md` section; CHANGELOG; Linear comment.

**Test plan**

* Unit: focus gating; badge count mapping; recents dedupe.
* E2E: PAP-508: unfocused notification path with a fake notification provider.

**Demo**

Reviewer switches to another app, a teammate mentions them, the OS notification appears; clicking it brings PaperOS forward on the comment; `Cmd+Shift+Space` from the desktop opens the command bar. Under a minute.

**Edge cases**

* Do Not Disturb enabled at OS level: notifications suppressed, badge still updates.
* Wayland has no global shortcut API: feature hidden on Wayland with a note.
* Windows jump list limited to 10 items; recents capped.

**Dependencies**

Hard: PAP-255, PAP-136. Soft: PAP-257, PAP-151, PAP-153, PAP-324, PAP-511.

**Agent**

Builder: Forge (Tauri Smith). Reviewer: Sentinel (Visual Inspector).

**Size**

S: half a session.

*Round 4 critique fix (2026-09-18):* resolved 3 round-4 file keys in this description to Linear identifiers: `r4/app-shell/native-push-registration` = PAP-516, `r4/app-shell/shell-layout-presets` = PAP-511, `r4/app-shell/tauri-e2e-harness` = PAP-508.
