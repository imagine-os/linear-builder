---
identifier: "PAP-148"
title: "Implement the offline write queue with retry, ordering and user-visible sync status"
project: "realtime"
projectName: "Multiplayer & Realtime"
phase: "P2"
type: "Build"
priority: 2
surfaces: ["Customer"]
milestone: "Scale and offline tested"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-143", "PAP-144", "PAP-304", "PAP-328"]
blocks: []
key: "realtime/offline-queue"
url: "https://linear.app/paperos/issue/PAP-148/implement-the-offline-write-queue-with-retry-ordering-and-user-visible"
source: "Linear snapshot 2026-09-17T13:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T13:05:30.221Z"
---

# PAP-148: Implement the offline write queue with retry, ordering and user-visible sync status

**Goal**

Let customers keep working on a train or a flaky connection: writes queue locally in order, retry intelligently, and the UI always tells the truth about what has reached the server. This hardens the PAP-272 outbox into a product-grade feature with visible sync status.

**Scope**

In:

* `packages/sync/src/outbox/` hardening of PAP-272: PGlite table `outbox(id, seq, mutation_id, procedure, input jsonb, depends_on, status: queued|sending|failed|conflict, attempts, last_error, created_at)`, strict FIFO per entity, concurrency 4 across entities.
* Retry: exponential 1 s → 60 s with jitter, 20 attempts then `failed`; network errors while offline retry forever; 4xx other than 409 and 429 fail immediately; 429 honours `Retry-After`.
* Dependency tracking: create-then-update chains; `tmp_` ids remapped from server responses.
* `SyncStatusIndicator` (synced, syncing n, offline n queued, attention n failed) and `SyncQueueSheet` (retry, discard, copy details); `useSyncStatus()`; captive-portal detection via `HEAD /api/health`.
* Tauri and PWA: queue survives restart; flush on `visibilitychange` and via the PAP-20 background shim.

Out: conflict UI (PAP-144, consumed), Yjs offline (`y-indexeddb`), uploads over 25 MB (PAP-37).

**Spec**

* Server idempotency: `idempotency_keys(tenant_id, mutation_id, response, expires_at 24h)` middleware in PAP-35 (the planned shared rate-limit and idempotency issue owns the table; this issue ships the middleware call) replays stored responses; batches of up to 25 via `POST /api/rpc/batch`.
* 409 carries `{ code: 'conflict', server: row }` → item `conflict`, emits `sync.conflict`.
* Indicator `role="status"`, icon plus text, announces at most once per 30 s.
* Storage guard: refuse new writes above 5,000 items or 50 MB with a blocking dialog.
* Spans `sync.flush` with queue depth (PAP-40).

**Interface contract**

Exposes: `enqueue({ procedure, input, entity: { table, id }, optimistic })`, `flush()`, `retry(id)`, `discard(id)`, `subscribe(cb)`, `useSyncStatus() -> { state, queued, failed, lastSyncedAt }`, `SyncStatusIndicator`, `SyncQueueSheet`, `OutboxItem` type, copy in `packages/collab/src/copy/sync.ts`; header `Idempotency-Key: <mutation_id>` and batch endpoint contract `{ calls: [{ id, procedure, input }] } -> { results: [{ id, ok, data | error }] }`. Consumes: PGlite and existing outbox (PAP-271, PAP-272), oRPC client and middleware (PAP-267, PAP-268), reconciler and events (PAP-143), `PendingWriteBadge` and `FailedWriteDialog` definitions (PAP-144), PWA lifecycle (PAP-18), mobile background shim (PAP-259), session refresh (PAP-223).

**Definition of done**

* Screenshots of the four indicator states and the sheet at 320, 768 and 1280.
* Tauri desktop restart test: queued writes persist and flush on relaunch (video).
* `docs/platform/realtime/offline.md` with state diagram; changelog; Linear comment with demo link.

**Test plan**

* Vitest: backoff schedule with jitter bounds, attempt counting only when online, dependency chaining and `tmp_` remap, 4xx classification, storage guard thresholds, monotonic timers under a clock jump.
* Integration: mock server replays a stored response for a duplicate `mutation_id`; a 409 moves the item to `conflict` and emits the event; batch of 25 splits correctly.
* Playwright: go offline, make 20 edits across 3 entities including create-then-update, reconnect, assert order and remapped ids in the DOM; captive portal (200 with HTML body) treated as offline; sign-out with queued writes prompts confirmation; run at 375 and 1280.
* Visual: indicator states and sheet captured at 320, 768 and 1280, both themes.

**Demo**

Toggle devtools offline, create a record and edit it twice, watch the indicator show “offline (3 queued)”, open the sheet, go online and see items drain with the real id appearing in the grid; kill one call with a 500 mock and retry from the sheet. Under two minutes.

**Edge cases**

* Session expired offline: refresh first, else "Sign in to sync" with the queue kept.
* Schema rejects an old write: `failed` with message, never dropped.
* Two devices offline: server arrival order; later one gets 409.
* Failed create: optimistic row stays with an error badge until discarded.

**Dependencies**

PAP-143, PAP-144 (hard, encoded). Soft: PAP-272, PAP-35, PAP-18, PAP-259, PAP-223, planned shared idempotency middleware (data-layer).

**Agent**

Builder: Nova (CRDT Engineer). Reviewer: Sentinel (Edge Case Hunter for network scenarios, Code Reviewer).

**Size**

M: focused package with many failure paths to test.
