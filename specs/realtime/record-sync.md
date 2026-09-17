---
identifier: "PAP-143"
title: "Stream record changes via Electric shapes to all connected clients and reconcile with local writes"
project: "realtime"
projectName: "Multiplayer & Realtime"
phase: "P1"
type: "Build"
priority: 1
surfaces: ["Developer"]
milestone: "Record sync and conflict UX"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-272", "PAP-36"]
blocks: ["PAP-144", "PAP-147", "PAP-148"]
key: "realtime/record-sync"
url: "https://linear.app/paperos/issue/PAP-143/stream-record-changes-via-electric-shapes-to-all-connected-clients-and"
source: "plan/specs/bucket-5.json (round-1 canonical spec JSON)"
---

# PAP-143: Stream record changes via Electric shapes to all connected clients and reconcile with local writes

**Goal**

Make every table, list and detail page update live when any human or agent changes a record, without a page refresh and without custom WebSocket code per feature. Electric shapes stream Postgres changes into each client's PGlite; this issue wires those streams into React, reconciles them with optimistic local writes, and defines how the UI learns that data changed under it.

**Scope**

In:
- `packages/sync/src/live/`: `useLiveQuery(query)` (PGlite live query over synced tables), `useShape(table, where)` (subscribe/unsubscribe with reference counting), and `useRecord(table, id)`.
- Reconciliation between the offline outbox from `data-layer/local-first-sync` and incoming shape rows: optimistic rows carry `_pending: true`; when the server row arrives with a matching `mutation_id` (set by the API on write), the optimistic row is dropped; if the server row differs from what the client expected, emit a `conflict` event consumed by `realtime/conflict-ux`.
- Shape registry additions for `tables/*` entities (`records`, `fields`, `views`) and PM entities from `pm-linear/pm-data-model`, each with a server-side `where` derived from tenant and permission.
- Change indicators: `useRecordChanges(id)` returns `{ changedFields, actor, at }` for 5 s after a remote change so cells can flash and show the actor avatar.
- Backpressure: batch incoming rows per animation frame; suspend live queries for off-screen virtualised rows.
- Dev tooling: `window.__paperosSync` inspector listing active shapes, row counts, lag (server `lsn` vs client) and outbox length.

Out: the transport itself (Electric is deployed by `data-layer/local-first-sync`), Yjs documents, offline retry policy (`realtime/offline-queue`), conflict visuals.

**Spec**

- Libraries: `@electric-sql/client` 1.x, `@electric-sql/pglite` 0.3.x with `live` extension, `@electric-sql/react`. Shapes are subscribed through the proxy `GET /api/sync/shape` with the Better Auth session; the proxy attaches `where tenant_id = $1` and, for restricted tables, a permission-derived predicate from `identity/rbac-abac`.
- Every write goes through oRPC (`data-layer/api-layer`); the API stamps `mutation_id uuid` and `updated_by principal_id` on the row so clients can match echoes and attribute changes.
- `mutate()` from `data-layer/local-first-sync` is extended with `expect: (before) => after` so the reconciler can compare the expected post-state to the server row field by field; mismatches list `conflictingFields`.
- Lag budget: remote change visible in other clients within 500 ms p95 on staging; measured by a Playwright test that writes via API and polls the DOM.
- Permission changes: when a shape's `where` would change (role edited), the server returns `409 shape-invalid`; the client drops and resubscribes.
- Memory: unsubscribe shapes 30 s after the last consumer unmounts; cap of 50 concurrent shapes per client with LRU eviction and a console warning.

**Definition of done**

- Grid demo page: editing a cell in browser A updates browser B within 500 ms; screenshot pair attached at 768 and 1440 px.
- Vitest tests for reconciler: echo match drops optimistic row; mismatch emits conflict with correct fields; out-of-order arrival handled.
- Integration test with a real Electric container in CI (`ops/compose/test.yml`).
- Permission test: revoking access removes rows from the client within one resubscribe cycle.
- Dev inspector documented in `docs/platform/realtime/record-sync.md` with a data-flow diagram.
- Changelog entry and Linear comment with the staging demo link and lag measurement.

**Edge cases**

- Client offline for an hour returns with 300 outbox writes while 2,000 remote rows arrive: apply remote rows first, then replay outbox; conflicts surface per row.
- Row deleted remotely while the user is editing it: keep the editor open with a "deleted by X" banner and offer restore via audit log (`data-layer/audit-log`).
- Shape with 500k rows: server refuses shapes without a bounding predicate; the client must page via the views query compiler.
- Clock skew: never use client timestamps for ordering; use server `lsn`.
- Duplicate `mutation_id` echoes after a retry: idempotent drop.
- Schema migration adds a column: PGlite schema hash mismatch triggers a reset with a non-blocking toast.

**Dependencies**

- `data-layer/local-first-sync` (PGlite, outbox, proxy), `data-layer/api-layer` (mutation stamping), `identity/rbac-abac` (predicates), `tables/query-compiler` (consumer, shares the shape registry). Consumed by `realtime/conflict-ux`, `realtime/offline-queue`, `tables/grid-view`, `pm-linear/board-views`.

**Agent**

Builder: Nova (CRDT Engineer sub-agent) with Forge (Schema Wright) adding `mutation_id`/`updated_by` columns. Reviewer: Sentinel (Code Reviewer) plus Edge Case Hunter for ordering scenarios.

**Size**

L: reconciliation semantics touch the data layer, API and every list UI.
