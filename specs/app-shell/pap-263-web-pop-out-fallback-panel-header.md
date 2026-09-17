---
identifier: "PAP-263"
title: "Web pop-out fallback, panel header affordances and windows documentation"
project: "app-shell"
projectName: "Universal App Shell & Repo Template"
phase: "P1"
type: "Build"
priority: 1
surfaces: ["Staff", "Customer"]
milestone: "Desktop and mobile shells build"
state: "Backlog"
parent: "PAP-21"
children: []
blockedBy: ["PAP-262"]
blocks: ["PAP-23", "PAP-145"]
key: "child/PAP-21/8"
url: "https://linear.app/paperos/issue/PAP-263/web-pop-out-fallback-panel-header-affordances-and-windows"
source: "Linear snapshot 2026-09-17T15:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T13:42:11.827Z"
model: "claude-sonnet-5"
effort: "high"
---

# PAP-263: Web pop-out fallback, panel header affordances and windows documentation

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / high — Build M

**Goal**

Give browsers the same pop-out experience with `window.open` popups mirrored over `BroadcastChannel`, add the Pop out and Dock affordances, keyboard shortcut and detached-window chips to the shell, and write `docs/shell/windows.md`.

**Scope**

In: web `WindowManager` backend using popups and the shared channel; panel header buttons; `Ctrl/Cmd+Shift+P`; chips per detached panel in the main window; popup-blocked hint; docs.

Out: data coherence beyond panel state (PAP-145).

**Spec**

* Same `WindowManager` interface, backend chosen by `getTarget()`.
* Popups open `/_window/<panelId>` with `noopener` off so the channel works; closing docks.
* Chips list detached panels with focus and dock actions.
* Shortcut registered through PAP-151 once it exists; plain listener until then.

**Interface contract**

Provides: web backend, header components `PanelHeader` with `PopOutButton` in `@paperos/ui`, docs. Consumes: manager (child 2), breakpoints (child 1), `AppShell` (PAP-16).

**Definition of done**

* Playwright multi-page test: pop out, change a filter in the popup, main window mirrors it.
* Screenshots at seven widths with a detached chip visible; `docs/shell/windows.md` complete; CHANGELOG.

**Test plan**

* Unit: chip list reducer; popup-blocked detection.
* E2E: Playwright multi-page mirror test; blocked popup shows inline hint.
* Visual: seven widths, light and dark; keyboard shortcut announced to screen readers.

**Demo**

Reviewer clicks Pop out on the sidebar in Chrome, a popup opens with the sidebar, changes a filter there and sees the main window follow; closing the popup docks it. Under a minute.

**Edge cases**

* Popup blockers: hint, panel stays docked.
* Popup navigated away by the user: main detects channel silence and docks.

**Dependencies**

Children 1 and 2 (hard). Soft: PAP-151.

**Agent**

Built by Forge with Iris on affordances. Reviewed by Sentinel (Visual Inspector).

**Size**

M
