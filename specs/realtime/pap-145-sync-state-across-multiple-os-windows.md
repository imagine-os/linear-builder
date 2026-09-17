---
identifier: "PAP-145"
title: "Sync state across multiple OS windows and tabs of the same user via BroadcastChannel and Yjs"
project: "realtime"
projectName: "Multiplayer & Realtime"
phase: "P1"
type: "Build"
priority: 2
surfaces: ["Staff"]
milestone: "Record sync and conflict UX"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-21", "PAP-140", "PAP-263"]
blocks: ["PAP-23"]
key: "realtime/multi-window-sync"
url: "https://linear.app/paperos/issue/PAP-145/sync-state-across-multiple-os-windows-and-tabs-of-the-same-user-via"
source: "Linear snapshot 2026-09-17T15:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T13:41:37.103Z"
model: "claude-sonnet-5"
effort: "high"
---

# PAP-145: Sync state across multiple OS windows and tabs of the same user via BroadcastChannel and Yjs

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / high — Build M

**Goal**

Keep every window and tab of one user coherent: a record edited in a detached inspector on monitor two reflects instantly in the main window, selection and navigation can be shared, and the app never fights itself with duplicate connections. This makes the PAP-21 window manager feel like one application.

**Scope**

In:

* `packages/collab/src/windows/`: `WindowBus` over `BroadcastChannel` (same-origin web and Tauri webviews) with a Tauri `emit`/`listen` fallback; Zod message schema.
* Leader election reusing PAP-272's `navigator.locks` election: one window holds Hocuspocus and Electric connections, followers proxy through it; re-election within 2 s.
* Channels: `selection`, `navigation` (with `follow` flag), `presence` (single awareness entry per user for PAP-141), `auth` (sign-out), `theme`, `keymap` (PAP-153), `dnd.transfer` (PAP-155).
* Yjs relay: leader forwards `encodeStateAsUpdate` diffs over the bus; every window keeps `y-indexeddb`.
* UI: `WindowChip` in the status bar listing detached windows with focus and dock; "Follow main window selection" toggle in detached windows; dev overlay.

Out: cross-device sync, cross-user follow (PAP-149), OS window placement (PAP-262).

**Spec**

* Channel `paperos:<tenantId>:<userId>`; messages `{ type, from: windowId, ts, payload }`; `windowId` in `sessionStorage`.
* Followers send writes to the leader, which forwards to the API; if the bus is unavailable each window uses its own connections (logged degraded).
* Rich text in two windows shares one Yjs doc; form fields use last-blur-wins and show `RemoteChangeFlash` (PAP-144).
* Mobile: single window, bus is a no-op.
* Relaying 1,000 Yjs updates/s across three windows under 10 percent leader CPU.

**Interface contract**

Exposes: `WindowBus` with `publish(type, payload)`, `subscribe(type, cb)`, `useWindowBus()`, `useIsLeader()`, `useWindows() -> { id, title, route, isLeader }[]`, message types above with Zod schemas in `packages/collab/windows/messages.ts` (other packages add types via `declare module` augmentation), `WindowChip`. Consumes: `WindowManager` `detach`, `dock`, `list_displays` and `panel-<id>` naming (PAP-262), leader election helper (PAP-272), `createDocProvider` (PAP-140), shape subscriptions (PAP-143), `PresenceProvider` aggregation hook (PAP-141), sign-out event (PAP-223), `RemoteChangeFlash` (PAP-144).

**Definition of done**

* Three same-context pages hold one WebSocket to the collab server; edits propagate under 50 ms; closing the leader re-elects without loss.
* Tauri Linux run with a detached inspector on a second display recorded (PAP-83).
* Screenshots at 1280 and 1920 with `WindowChip`; `docs/platform/realtime/multi-window.md` with election and relay diagram; changelog; Linear comment with video.

**Test plan**

* Vitest: message schema (valid, unknown type), leader election with simulated lock loss, heartbeat conflict picks lowest `windowId`, fallback when `BroadcastChannel` is undefined, tenant-scoped channel isolation.
* Playwright: three pages in one context; count WebSocket connections via CDP `Network.webSocketCreated` equals one; edit propagation under 50 ms measured with `performance.now()`; close the leader page and assert re-election within 2 s and a queued follower write lands; sign-out in one page redirects all three within 500 ms.
* Performance: CDP profiler while relaying 1,000 updates/s for 10 s, leader CPU under 10 percent.
* Visual: main window plus detached panel captured at 1280 and 1920, both themes.

**Demo**

Detach the inspector to a second window, edit a record there and watch the main grid update; enable “Follow main window selection” and click rows in the main window; close the main window and keep editing in the panel. Under two minutes.

**Edge cases**

* Two leaders after sleep: lowest `windowId` wins within one heartbeat.
* Private tab without `locks`: standalone with a warning.
* Follower writes during leader reconnect: queue 1,000 then `PendingWriteBadge`.
* Second window on another tenant: bus does not talk; switcher warns.

**Dependencies**

PAP-21, PAP-140 (hard, encoded). Soft: PAP-262, PAP-272, PAP-143, PAP-141, PAP-223, PAP-144. Blocks PAP-23; consumed by PAP-153, PAP-155, PAP-149.

**Agent**

Builder: Nova (CRDT Engineer) with Forge (Tauri Smith) for the Tauri fallback. Reviewer: Sentinel (Code Reviewer, Edge Case Hunter).

**Size**

M: election and relay are subtle but bounded.
