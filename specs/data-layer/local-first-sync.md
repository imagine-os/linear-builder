---
identifier: "PAP-36"
title: "Integrate PGlite and ElectricSQL shapes for local-first reads with an offline write queue"
project: "data-layer"
projectName: "Data Layer & Database"
phase: "P1"
type: "Build"
priority: 1
surfaces: ["Customer", "Developer"]
milestone: "Local-first sync working"
state: "Backlog"
parent: null
children: ["PAP-270", "PAP-272", "PAP-271"]
blockedBy: ["PAP-269", "PAP-30", "PAP-31", "PAP-34", "PAP-35"]
blocks: ["PAP-143"]
key: "data-layer/local-first-sync"
url: "https://linear.app/paperos/issue/PAP-36/integrate-pglite-and-electricsql-shapes-for-local-first-reads-with-an"
source: "plan/specs/bucket-0.json (round-1 canonical spec JSON)"
---

# PAP-36: Integrate PGlite and ElectricSQL shapes for local-first reads with an offline write queue

**Goal**

Give every target instant, offline-capable reads and queued writes: the engine chosen in `data-layer/sync-research` (default ElectricSQL shapes + PGlite) streams tenant-scoped shapes into a local database in the browser or Tauri WebView, React hooks read locally, and writes go to the oRPC API through an outbox that replays when connectivity returns.

**Scope**

In:
- `packages/sync/`: shape definitions (`defineShape(table, where, columns)`), `SyncClient` lifecycle (start/stop/reset), `useShape()` and `useLiveQuery()` hooks over PGlite live queries, `Outbox` for writes.
- Electric sync service deployed via Coolify (`ops/compose/electric.yml`) connected directly to Postgres with the `electric` replication role; shapes gated by an auth proxy route in `apps/api` (`/api/sync/shape`) that validates the session and injects `tenant_id = <actor tenant>` into the `where` clause so clients cannot request other tenants' data.
- PGlite 0.3 with IndexedDB persistence in browsers and file persistence in Tauri (`apps/desktop` data dir), schema mirrored from Drizzle via a generated `pglite-schema.sql`.
- Outbox: local `_outbox` table `{ id uuidv7, procedure, input jsonb, created_at, attempts, last_error, status }`; optimistic local mutation applied to PGlite, replayed FIFO through `packages/api-client`; conflicts resolved server-wins with a `ConflictEvent` emitted for `realtime/conflict-ux`.
- Status surface: `useSyncStatus()` returning `{ state: 'offline'|'syncing'|'live'|'error', pending, lastSyncedAt }` and a `<SyncIndicator/>` in the status bar slot (`app-shell/router-layouts`).
- Reset and re-sync on logout, tenant switch or schema version change.

Out: CRDT documents (Yjs, `realtime/yjs-server`), presence, live record push UX (`realtime/record-sync` builds on this), multi-window coordination (`realtime/multi-window-sync`).

**Spec**

- Shapes for core entities: `workspaces`, `memberships` (own tenant), `users` (members of tenant, limited columns), `files` (metadata only). Additional projects register shapes in their packages.
- Shape proxy: `GET /api/sync/shape?table=&offset=&handle=&live=` forwards to Electric with server-set `where`; deny tables not in the registry; response streamed.
- PGlite schema generation: `pnpm gen:pglite` produces `packages/sync/generated/schema.sql` from Drizzle (tables in shape registry only); versioned with a hash; mismatch triggers reset.
- Write path: `mutate(orpc.tasks.update, input, { optimistic: (db) => ... })`; when online and outbox empty, call directly; otherwise enqueue.
- Replay: exponential backoff 1s..60s, max 20 attempts, then `status:'failed'` with UI to retry/discard.
- Storage limits: warn when local DB above 200 MB; shapes support `columns` to trim.
- Tauri: PGlite via Node-less WASM in WebView; on Android fall back to memory + IndexedDB per sync-research findings.

**Definition of done**

- Demo route `/_app/sync-demo` lists workspaces from PGlite; editing a name offline, reloading, going online replays the write (Playwright test with `setOffline`; recording).
- Cross-tenant shape request through the proxy returns 403 (test).
- Vitest: outbox state machine, backoff, schema-hash reset; bench of initial shape load for 2k rows under 1.5 s on CI runner.
- Electric deployed on staging; health checked from `/api/health`.
- Screenshots of `<SyncIndicator/>` states at 375, 768, 1280, 1920 and of the demo route at all 7 widths.
- `docs/data/sync.md`; CHANGELOG; Linear comment with recording and preview URL.

**Edge cases**

- Two tabs both replaying the outbox: leader election via `navigator.locks`.
- Server rejects replayed write with `FORBIDDEN` (permission changed while offline): mark failed, surface reason, roll back optimistic row.
- Shape handle expired after long offline: full re-fetch, preserve outbox.
- IndexedDB blocked (Safari private mode): fall back to in-memory PGlite with banner.
- Deleted rows while offline: tombstones arrive via shape; local rows removed; outbox writes to them fail cleanly.
- Clock skew affecting `updated_at` comparisons: server timestamps only.

**Dependencies**

`data-layer/api-layer` and `data-layer/sync-research` (hard), `data-layer/rls-tenancy` (proxy semantics), `data-layer/postgres-provision` (logical replication on). Unblocks `realtime/record-sync`, `realtime/offline-queue`, `tables/query-compiler` (local execution), `app-shell/linux-kiosk` resilience.

**Agent**

Built by Forge with Nova (CRDT Engineer) pairing on the outbox and conflict events. Reviewed by Sentinel (Security Auditor for proxy, Edge Case Hunter for offline scenarios).

**Size**

L: a new service, a local database, an outbox and a proxy that must all be secure and resilient.
