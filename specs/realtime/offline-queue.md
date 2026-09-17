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
blockedBy: ["PAP-143", "PAP-144"]
blocks: []
key: "realtime/offline-queue"
url: "https://linear.app/paperos/issue/PAP-148/implement-the-offline-write-queue-with-retry-ordering-and-user-visible"
source: "plan/specs/bucket-5.json (round-1 canonical spec JSON)"
---

# PAP-148: Implement the offline write queue with retry, ordering and user-visible sync status

**Goal**

Let customers keep working on a train, in a basement or on a flaky mobile connection: writes queue locally in order, retry intelligently, and the UI always tells the truth about what has and has not reached the server. This hardens the outbox that `data-layer/local-first-sync` introduced into a product-grade feature with visible sync status.

**Scope**

In:
- `packages/sync/src/outbox/` rewrite: durable queue in PGlite table `outbox(id, seq, mutation_id, procedure, input jsonb, depends_on, status: queued|sending|failed|conflict, attempts, last_error, created_at)` with strict FIFO per entity and parallelism across independent entities.
- Retry policy: exponential backoff 1 s → 60 s with jitter, 20 attempts, then `failed`; network errors retry forever while offline (no attempt counted); 4xx other than 409/429 fail immediately.
- Dependency tracking: a create followed by an update of the same temp ID are chained; temp IDs (`tmp_` UUID) are remapped when the server returns the real ID.
- `SyncStatusIndicator` in `packages/ui` for the status bar: states `synced`, `syncing (n)`, `offline (n queued)`, `attention (n failed)`; click opens `SyncQueueSheet` listing items with retry, discard, and "copy details".
- `useSyncStatus()` hook and `navigator.onLine` plus heartbeat (`HEAD /api/health` every 15 s when suspicious) to detect captive portals.
- Tauri and PWA: queue survives app restart; background flush on `visibilitychange` and, on mobile, via the Tauri background task shim from `app-shell/tauri-mobile` where the OS allows.

Out: conflict resolution UI (`realtime/conflict-ux`, consumed here), Yjs offline (handled by `y-indexeddb`), file uploads over 25 MB (deferred, `data-layer/file-storage`).

**Spec**

- API: `enqueue({ procedure, input, entity: { table, id }, optimistic })`, `flush()`, `retry(id)`, `discard(id)`, `subscribe(cb)`; the existing `mutate()` becomes a thin wrapper.
- Server idempotency: oRPC middleware in `data-layer/api-layer` stores `mutation_id` in `idempotency_keys(tenant_id, mutation_id, response, expires_at 24h)` and replays the stored response on duplicates.
- Ordering: single in-flight request per entity; independent entities flush with concurrency 4; batches up to 25 mutations use `POST /api/rpc/batch`.
- 409 responses carry `{ code: 'conflict', server: row }` and move the item to `conflict`, emitting the event `realtime/conflict-ux` consumes; 429 honours `Retry-After`.
- Copy in `packages/collab/src/copy/sync.ts`; indicator uses icon plus text, never colour only; `role="status"`, announces transitions at most once per 30 s.
- Storage guard: refuse new writes when the queue exceeds 5,000 items or 50 MB, with a blocking dialog explaining why.
- Telemetry: `sync.flush` spans via `data-layer/observability` with queue depth and attempt count.

**Definition of done**

- Playwright tests: go offline, make 20 edits across 3 entities including create-then-update, come back online, all land in order with remapped IDs; captive-portal simulation (200 with HTML body) treated as offline.
- Vitest tests for backoff, dependency chaining, idempotent replay and storage guard.
- Screenshots of all four indicator states and the queue sheet at 320, 768 and 1280 px.
- Tauri desktop restart test: queued writes persist and flush on relaunch (video).
- Docs `docs/platform/realtime/offline.md` with a state diagram.
- Changelog entry and Linear comment with the demo link.

**Edge cases**

- Session expired while offline: on reconnect, refresh the session first; if that fails, keep the queue and show "Sign in to sync".
- Server-side validation now rejects an old queued write (schema changed): mark `failed` with the message; never drop silently.
- User signs out with queued writes: warn and require confirmation; discard on confirm.
- Two devices edit offline, both come online: ordering by server arrival; conflicts surface via 409 to the later one.
- Clock jump (device time changed) must not break backoff timers; use monotonic `performance.now()`.
- Optimistic row for a failed create remains visible with an error badge until discarded.

**Dependencies**

- `data-layer/local-first-sync` (PGlite, existing outbox), `data-layer/api-layer` (idempotency middleware, batch), `realtime/record-sync` (reconciliation), `realtime/conflict-ux` (conflict handling), `app-shell/pwa` and `app-shell/tauri-mobile` (background flush).

**Agent**

Builder: Nova (CRDT Engineer sub-agent). Reviewer: Sentinel (Edge Case Hunter for network scenarios, Code Reviewer).

**Size**

M: focused package with well-defined states, but many failure paths to test.
