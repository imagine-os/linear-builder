---
identifier: "PAP-609"
title: "Unified connection status: `useConnectionStatus()` composing Hocuspocus, Electric, SSE and outbox states, one `ConnectionIndicator`, jittered reconnect policy, token refresh on `4401` and sleep or wake handling"
project: "realtime"
projectName: "Multiplayer & Realtime"
phase: "P1"
type: "Build"
priority: 2
surfaces: ["Customer"]
milestone: "Record sync and conflict UX"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-140", "PAP-272"]
blocks: []
key: "r4/realtime/connection-status"
url: "https://linear.app/paperos/issue/PAP-609/unified-connection-status-useconnectionstatus-composing-hocuspocus"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:16.368Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 2
dueDate: "2026-09-28"
cycle: null
---

# PAP-609: Unified connection status: `useConnectionStatus()` composing Hocuspocus, Electric, SSE and outbox states, one `ConnectionIndicator`, jittered reconnect policy, token refresh on `4401` and sleep or wake handling

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Build S

**Goal**

Four transports each report their own health: PAP-272 `SyncIndicator`, PAP-148 `SyncStatusIndicator`, PAP-140's provider `status$`, and the live channel's SSE fallback. A user on a train would see three pills disagreeing. Linear and Figma show one state; this composes the four into one hook and one indicator, and fixes the reconnect behaviours (backoff jitter, token refresh, laptop wake) in one place instead of four.

**Scope**

In: `packages/sync/src/connection/{status,policy,indicator}.ts(x)`: `useConnectionStatus() -> { state: 'online'|'degraded'|'offline'|'maintenance'|'reconnecting', transports: { collab, shapes, live, outbox }, pending, lastSyncedAt, until? }`; `ConnectionIndicator` replacing the two existing indicators (PAP-272 and PAP-148 keep their queue sheet and details); shared `reconnectPolicy` (exponential 1 s to 60 s with full jitter, reset after 30 s healthy) adopted by the Hocuspocus provider wrapper (PAP-140), the shape client (PAP-271) and SSE; `4401` handling: call `getToken()` (PAP-223 refresh or PAP-225 bearer) once and reconnect without losing edits; sleep and wake: `visibilitychange`, `online`, Tauri `resume` events (PAP-259) trigger an immediate health probe (`HEAD /api/health`) and reconnect; captive-portal detection shared with PAP-148; maintenance state from PAP-575 (soft); docs section with the state diagram.

Out: Outbox semantics and the queue sheet (PAP-148), leader election (PAP-272, PAP-145), server-side health (PAP-269).

**Spec**

* State derivation: `offline` when the browser is offline or the health probe fails; `maintenance` when the API says so; `reconnecting` when any transport is retrying; `degraded` when a transport fell back (SSE instead of shape) or the outbox has failures; `online` otherwise.
* Indicator: `role="status"`, icon plus text, announces at most once per 30 s, click opens a popover with per-transport detail and the queue sheet link; hidden when `online` and nothing pending unless the page spec asks for it.
* Reconnect storms: policy jitter plus a per-tab random start delay after wake so 20 open tabs do not hammer the server at once (PAP-147 scenario (c) measures it).
* Token refresh: on `4401` from Hocuspocus or 401 from the shape proxy, refresh once; if refresh fails, state becomes `offline` with reason `signed-out` and PAP-572 decides about the cache.
* Dev overlay: `?debug=sync` (PAP-328) shows the composed state and each transport's last error.

**Interface contract**

Provides: `useConnectionStatus()`, `ConnectionIndicator`, `reconnectPolicy`, `probeHealth()`, `ConnectionState` type in the realtime contract, wake and online event wiring.

Consumes: Provider status (PAP-140), shape client (PAP-271), outbox status (PAP-272, PAP-148 soft), SSE and live channel (PAP-599, soft), token refresh (PAP-223, PAP-225), Tauri events (PAP-259, soft), maintenance flag (PAP-575, soft), inspector (PAP-328). Consumed by PAP-148, PAP-62, PAP-63 shells, PAP-145 window chip, PAP-234 `OfflineBanner`.

**Definition of done**

* Kill the collab container: indicator goes `reconnecting` then `online` within the policy window; block the shape route: `degraded` with SSE named; go offline: `offline` with pending count (Playwright).
* Expired token: one refresh and reconnect with no lost edit (fake clock); wake event triggers a probe within 1 s (unit with fake events).
* One indicator across the sync demo, grid demo and a doc page; screenshots at 375, 768, 1280 in both themes; docs with the state diagram; changelog.

**Test plan**

* Unit: state derivation table, jitter bounds, refresh-once logic, wake handling, announcement throttle.
* E2E: the three failure injections above on the compose stack; 20 tabs reconnect after a container restart without a thundering herd (connection timestamps spread).

**Demo**

Open the grid demo, stop the collab container and watch the single pill change and recover, then toggle DevTools offline and open the popover to see per-transport detail. Under 90 seconds.

**Edge cases**

* Private tab without `locks` or `BroadcastChannel`: standalone connections; indicator shows the same states.
* Health probe blocked by a captive portal returning 200 HTML: treated as offline (shared detector).
* Tauri sleep for hours: `resume` triggers probe and token refresh before any transport retries.

**Dependencies**

Blocked by PAP-140 and PAP-272 (hard). Soft: PAP-271, PAP-148, PAP-223, PAP-225, PAP-259, PAP-328, PAP-599, PAP-575, PAP-572. Consumed by PAP-148, PAP-62, PAP-63, PAP-145, PAP-234.

**Agent**

Builder: Nova (CRDT Engineer). Reviewer: Sentinel (Edge Case Hunter for network scenarios).

**Size**

S: half a session.

*Round 4 critique fix (2026-09-18):* resolved 3 round-4 file keys in this description to Linear identifiers: `r4/data-layer/local-data-protection` = PAP-572, `r4/data-layer/maintenance-mode` = PAP-575, `r4/realtime/live-events-channel` = PAP-599.
