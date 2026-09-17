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
blockedBy: ["PAP-140", "PAP-21", "PAP-263"]
blocks: ["PAP-23"]
key: "realtime/multi-window-sync"
url: "https://linear.app/paperos/issue/PAP-145/sync-state-across-multiple-os-windows-and-tabs-of-the-same-user-via"
source: "plan/specs/bucket-5.json (round-1 canonical spec JSON)"
---

# PAP-145: Sync state across multiple OS windows and tabs of the same user via BroadcastChannel and Yjs

**Goal**

Keep every window and tab of the same user coherent: a record edited in a detached inspector window on monitor two is instantly reflected in the main window on monitor one, selection and navigation can be shared, and the app never fights itself with duplicate connections. This is what makes the multi-monitor window manager from `app-shell/breakpoints-windows` feel like one application.

**Scope**

In:
- `packages/collab/src/windows/`: a `WindowBus` over `BroadcastChannel` (web and Tauri webviews sharing an origin) with a Tauri fallback via `@tauri-apps/api` `emit`/`listen` when webviews have different origins; typed message schema (Zod).
- Leader election (one window holds the Hocuspocus and Electric connections; followers proxy through the leader) using `navigator.locks` with a heartbeat fallback; re-election within 2 s when the leader closes.
- Shared state channels: `selection` (current entity/record), `navigation` (route changes with `follow` flag), `presence` (single awareness entry per user, aggregated across windows as required by `realtime/presence`), `auth` (sign-out propagates), `theme` and `keymap` changes.
- Yjs: followers connect to the leader's `Y.Doc` via `y-webrtc`-free in-process relay: leader forwards updates over the bus; each window still keeps `y-indexeddb` for cold start.
- UI: `WindowChip` in the main window status bar lists detached windows with "focus" and "dock" actions; each detached window has a "Follow main window selection" toggle.
- Dev overlay showing leader id, window count and message rate.

Out: cross-device sync (that is ordinary realtime), cross-user follow (`realtime/followmode`), OS-level window placement (`app-shell/breakpoints-windows`).

**Spec**

- Channel name `paperos:<tenantId>:<userId>`; messages `{ type, from: windowId, ts, payload }`; `windowId` is a UUID stored in `sessionStorage`.
- Leader duties: hold one `createDocProvider` per room and one Electric shape set; relay Yjs updates (`Y.encodeStateAsUpdate` diffs) and shape rows to followers; followers send writes to the leader, which forwards to the API; if the bus is unavailable, each window falls back to its own connections (logged as degraded).
- Navigation follow: when enabled, a follower window mirrors the main window's selected record into its own route (`/records/:id` inside an inspector layout) but keeps independent scroll and zoom.
- Conflict avoidance: the same record open for editing in two windows uses the same Yjs doc for rich text; for form fields the last window to blur wins and the other window shows the `RemoteChangeFlash` from `realtime/conflict-ux`.
- Tauri: `panel-<id>` windows from `app-shell/breakpoints-windows` load the same origin, so `BroadcastChannel` works; Android/iOS have a single window and the bus is a no-op.
- Performance: relaying 1,000 Yjs updates per second between three windows must not exceed 10% CPU on the leader (measured with the Playwright CDP profiler).

**Definition of done**

- Playwright test with three pages (same context) proving: one WebSocket connection to the collab server, edits propagate under 50 ms, closing the leader re-elects and reconnects without data loss.
- Tauri desktop manual run on Linux with a detached inspector on a second display, recorded as a video via `quality/video-replays`.
- Vitest tests for message schema, leader election and fallback.
- Screenshots at 1280 and 1920 px of main window plus detached panel; `WindowChip` visible.
- Docs `docs/platform/realtime/multi-window.md` with a sequence diagram of election and relay.
- Changelog entry and Linear comment with the video link.

**Edge cases**

- Two leaders after a laptop sleep: heartbeat conflict resolution picks the lowest `windowId` and the other demotes within one heartbeat.
- Private-browsing tab where `BroadcastChannel` or `navigator.locks` is unavailable: run standalone with a console warning.
- Sign-out in one window: all windows clear state and navigate to sign-in within 500 ms.
- Follower sends a write while leader is mid-reconnect: queue locally up to 1,000 messages then surface `PendingWriteBadge`.
- Different tenant selected in a second window: the bus is tenant-scoped, so windows simply do not talk; the tenant switcher warns when other windows exist.
- Window closed via task manager (no `beforeunload`): heartbeat timeout handles it.

**Dependencies**

- `realtime/yjs-server`, `app-shell/breakpoints-windows` (detached windows, `list_displays`), `realtime/record-sync` (shape relay), `realtime/presence` (aggregation), `identity/better-auth` (sign-out event).

**Agent**

Builder: Nova (CRDT Engineer sub-agent) with Forge (Tauri Smith) for the Tauri event fallback. Reviewer: Sentinel (Code Reviewer, Edge Case Hunter).

**Size**

M: leader election and relay are subtle but bounded in scope.
