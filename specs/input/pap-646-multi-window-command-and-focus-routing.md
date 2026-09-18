---
identifier: "PAP-646"
title: "Multi-window command and focus routing: per-window scope roots, global command forwarding over the WindowBus, focus.nextWindow and palette in detached panels"
project: "input"
projectName: "Multi-Input Control & Accessibility"
phase: "P1"
type: "Build"
priority: 2
surfaces: ["Staff"]
milestone: "Voice and accessibility certification"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-145", "PAP-152", "PAP-262", "PAP-289"]
blocks: []
key: "r4/input/multi-window-command-and-focus-routing"
url: "https://linear.app/paperos/issue/PAP-646/multi-window-command-and-focus-routing-per-window-scope-roots-global"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:20.947Z"
model: "claude-sonnet-5"
effort: "high"
estimate: 3
dueDate: "2026-09-30"
cycle: null
---

# PAP-646: Multi-window command and focus routing: per-window scope roots, global command forwarding over the WindowBus, focus.nextWindow and palette in detached panels

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / high — Build M

**Goal**

Justin's brief puts multi-monitor first. PAP-262 detaches panels into OS windows and PAP-145 syncs state, but nothing says what `mod+k`, `F6` or a page-scoped command does in a detached inspector. Define and build the routing so every window has a working palette, shortcuts fire in the focused window, and global commands reach the right place.

**Scope**

In: `packages/input/src/windows/{WindowScopeRoot,commandRouter,focusWindows}.ts`; a `CommandScopeProvider` root per window with `windowId` from PAP-262; `WindowBus` messages `command.forward { id, args, targetWindowId | 'main' | 'focused' }` and `focus.request`; commands `focus.nextWindow|prevWindow`, `window.detach|dock|list`; palette mounting in every window (PAP-290); shortcut sheet per window; docs section.

Out: window manager itself (PAP-262), web pop-out fallback mechanics (PAP-263; this issue only consumes its `windowId`), cross-window drag payloads (PAP-331 uses the bus directly).

**Spec**

* Each window mounts `WindowScopeRoot` which registers the window's commands under `window:<id>`; `registry.list(ctx)` in a detached window shows global commands plus that window's page and component scopes; commands flagged `windowScope: 'main'` (for example `nav.*`, `ui.toggleSidebar`) are forwarded to the main window over the bus and the result echoed back; `windowScope: 'any'` runs locally.
* Shortcuts fire only in the OS-focused window (document `visibilityState` and `hasFocus`); the palette opens in the window that received `mod+k`; `?` shows that window's effective commands.
* `focus.nextWindow` cycles PaperOS windows via PAP-262 `WindowManager.focus(id)` (Tauri) or `window.focus()` on pop-outs (PAP-263), announcing the window title (PAP-152 `LiveAnnouncer`); `F6` cycles regions within a window only (PAP-152 rule).
* Undo stacks (PAP-641) and keymaps (PAP-153 `keymap.changed`) stay per window; the router carries `sourceWindowId` so telemetry can attribute commands.
* Window loss: if the main window closes, the oldest detached window becomes `main` (bus election reuses PAP-272 leader election); forwarded commands time out after 2 s with a toast.

**Interface contract**

Provides: `WindowScopeRoot`, `useWindowId()`, `forwardCommand`, `windowScope` extension on `CommandDef`, bus message schemas `command.forward|result`, `focus.request`, commands `focus.nextWindow|prevWindow`, `window.*`. Consumes: registry and scopes (PAP-289), palette (PAP-290), focus regions and announcer (PAP-152), `WindowBus` (PAP-145), `WindowManager` ids and `focus` (PAP-262), pop-out ids (PAP-263), leader election (PAP-272, soft). Consumed by PAP-263, PAP-331, PAP-153, PAP-641.

**Definition of done**

* Detach the inspector on Tauri Linux and on the web pop-out fallback: palette opens in both windows, `nav.goToInbox` from the detached window navigates the main window, `focus.nextWindow` cycles with announcements; recording attached.
* `docs/platform/input/multi-window.md` with the routing table; changelog; Linear comment on PAP-262, PAP-263, PAP-145.

**Test plan**

* Unit: routing decision table (`windowScope` × focused window); election on main loss; timeout handling; per-window registry isolation.
* Integration: two Playwright pages in one context using the pop-out fallback exchange `command.forward` and `result` within 100 ms; a shortcut pressed in the unfocused page does not fire.
* E2E: pop out the inspector, press `mod+k` there, run "Toggle theme" (any) and "Go to inbox" (main), press `focus.nextWindow` back to main, close main and confirm the pop-out becomes main.

**Demo**

Reviewer detaches the record inspector to a second monitor, presses `mod+k` in it, runs a navigation that changes the main window, then cycles windows with the keyboard hearing each title. Under two minutes.

**Edge cases**

* Bus unavailable (BroadcastChannel blocked): forwarded commands fall back to running locally with a warning.
* Same chord bound to a window command and a main command: focused window wins.
* Detached window in a different tenant (PAP-58 switch): commands refused with `TENANT_MISMATCH`.
* Kiosk parallel-browser mode (PAP-23): every window is `main` for its display; documented.

**Dependencies**

PAP-289 (hard), PAP-152 (hard), PAP-145 (hard), PAP-262 (hard for Tauri; the pop-out path via PAP-263 is soft and may land first). Soft: PAP-290, PAP-272. Feeds PAP-263 and PAP-331 softly (their milestones are earlier; they ship without routing and adopt it).

**Agent**

Builder: Nova (Product Systems Engineer) with Forge (Tauri Smith). Reviewer: Sentinel (Edge Case Hunter).

**Size**

M: one session.

*Round 4 critique fix (2026-09-18):* resolved 1 round-4 file key in this description to Linear identifiers: `r4/input/undo-manager` = PAP-641.
