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
children: ["PAP-270", "PAP-271", "PAP-272"]
blockedBy: ["PAP-30", "PAP-31", "PAP-34", "PAP-35", "PAP-269"]
blocks: ["PAP-143", "PAP-326"]
key: "data-layer/local-first-sync"
url: "https://linear.app/paperos/issue/PAP-36/integrate-pglite-and-electricsql-shapes-for-local-first-reads-with-an"
source: "Linear snapshot 2026-09-17T15:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T13:40:59.316Z"
model: null
effort: null
---

# PAP-36: Integrate PGlite and ElectricSQL shapes for local-first reads with an offline write queue

**Model / Effort:** set on children (umbrella is never claimed)

**Goal**

Umbrella: give every target instant, offline-capable reads and queued writes with the engine PAP-31 chose (default ElectricSQL shapes plus PGlite). Tenant-scoped shapes stream into a local database, React hooks read locally, writes go through oRPC via an outbox that replays on reconnect. Three children; closes on the offline edit demo.

**Scope**

Children:

1. **PAP-270** — Electric service deployment and tenant-scoped shape proxy (`ops/compose/electric.yml`, `electric` role, `GET /api/sync/shape` with server-set `where`, table allowlist).
2. **PAP-271** — PGlite client, schema generation and read hooks (`pnpm gen:pglite`, `defineShape`, `SyncClient`, `useShape`, `useLiveQuery`, IndexedDB and Tauri file persistence).
3. **PAP-272** — Offline write outbox and sync indicator (`_outbox` table, `mutate()` with optimistic updater, replay with backoff, leader election, `<SyncIndicator/>`, demo route).

Out: multi-client conflict UX (PAP-143), full offline queue semantics and ordering (PAP-148 extends this outbox), view compilation (PAP-163).

**Spec**

* Core shapes: `workspaces`, `memberships`, `users` (tenant members, limited columns), `files` (metadata); other packages register their own.
* Proxy `GET /api/sync/shape?table=&offset=&handle=&live=` forwards to Electric with `where tenant_id = <principal tenant>` appended; non-registered tables denied; response streamed.
* `gen:pglite` emits `packages/sync/generated/schema.sql` for registered tables, versioned by hash; mismatch resets the local database but keeps the outbox.
* Outbox rows `{ id uuidv7, procedure, input, createdAt, attempts, lastError, status }`; backoff 1 s to 60 s, 20 attempts, then `failed` with retry or discard UI.
* Warn above 200 MB local storage; shapes support `columns`.

**Interface contract**

Provides (from `@paperos/sync`):

* `defineShape({ table, where?, columns? })`, `registerShape(shape)`, `useShape(shape)`, `useLiveQuery(sql, params)`, `mutate(procedure, input, { optimistic })`, `useSyncStatus(): { state: 'online'|'offline'|'syncing'|'error', pending: number }`.
* Shape registry consumed by PAP-143 (record sync), PAP-163 (shape eligibility), PAP-148 (queue extension).
* Route `GET /api/sync/shape` and error `SHAPE_FORBIDDEN` (403); header `x-sync-schema-hash`.
* Local tables `_outbox`, `_sync_meta`.
* Component `SyncIndicator` in `@paperos/ui`.

Consumes: publication and `electric` role (PAP-30), RLS context semantics for the proxy (PAP-34), oRPC client and `Principal` (PAP-35), ADR decision block (PAP-31), `useOnline` (PAP-18).

**Definition of done**

* All three children Done.
* Integration test: `/_app/sync-demo` lists workspaces from PGlite; rename one offline, reload, go online, the write replays (Playwright with `setOffline`; recording); cross-tenant shape request returns 403; 2k-row initial shape under 1.5 s on CI.
* Electric on staging, health checked from `/api/health`; `docs/data/sync.md`; CHANGELOG; Linear comment with recording and preview.

**Test plan**

* Unit: outbox state machine, backoff schedule, schema-hash reset preserving the outbox, leader election with two fake tabs.
* Integration (CI compose with Electric): shape proxy appends `where`, denies unknown tables, streams `live` responses; PGlite schema generated matches Drizzle for registered tables.
* E2E: offline edit and replay; two tabs open, only one replays (`navigator.locks`).
* Bench: initial 2k-row load timed in CI, committed.
* Visual: `<SyncIndicator/>` four states at 375, 768, 1280, 1920; demo route at seven widths.

**Demo**

Reviewer opens `/_app/sync-demo` on staging, toggles DevTools offline, renames a workspace (indicator shows one pending), reloads (edit persists locally), goes online and watches the indicator clear while the server row updates. Under 2 minutes.

**Edge cases**

* Server rejects a replayed write with `FORBIDDEN`: mark failed, surface reason, roll back the optimistic row.
* Expired shape handle after long offline: full re-fetch, outbox kept.
* Safari private mode: in-memory PGlite with banner.
* Tombstones for rows deleted while offline: local rows removed; outbox writes fail cleanly.
* Server timestamps only; never compare client clocks.

**Dependencies**

PAP-31, PAP-35 (hard), PAP-30 (logical replication) and PAP-34 (proxy semantics), both now encoded. Unblocks PAP-143, PAP-148, PAP-163, PAP-23.

**Agent**

Built by Forge with Nova (CRDT Engineer) pairing on the outbox. Reviewed by Sentinel.

**Size**

L as an umbrella; children are M, M, M.
