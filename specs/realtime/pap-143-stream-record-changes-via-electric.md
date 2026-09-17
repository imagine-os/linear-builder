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
children: ["PAP-326", "PAP-327", "PAP-328"]
blockedBy: ["PAP-36", "PAP-272"]
blocks: ["PAP-144", "PAP-147", "PAP-148", "PAP-381"]
key: "realtime/record-sync"
url: "https://linear.app/paperos/issue/PAP-143/stream-record-changes-via-electric-shapes-to-all-connected-clients-and"
source: "Linear snapshot 2026-09-17T13:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T13:03:48.140Z"
---

# PAP-143: Stream record changes via Electric shapes to all connected clients and reconcile with local writes

**Goal**

Umbrella: make every table, list and detail page update live when any human or agent changes a record, without per-feature socket code. Electric shapes (PAP-270, PAP-271) stream rows into PGlite; this issue reconciles them with optimistic writes and tells the UI when data changed under it. Planned as three work packages; the umbrella owns the lag measurement and docs.

**Scope**

Work packages (build in order; each becomes a child issue once the Linear issue limit is lifted, see the pinned comment):

1. **Live record hooks and shape registry additions** — `useRecord`, `useRecordChanges`, reference-counted subscriptions on top of PAP-271's `useShape`/`useLiveQuery`, shape entries for `records`, `fields`, `views` (PAP-161) and PM entities (PAP-100) with tenant and permission predicates, per-frame batching, LRU cap of 50 shapes.
2. **Reconciler for optimistic writes and conflict events** — `mutation_id` and `updated_by` stamping in PAP-35 middleware, `_pending` rows, echo matching, `expect` comparison, `conflict` event emission consumed by PAP-144 and PAP-148.
3. **Permission-driven resubscribe and lag measurement** — `409 shape-invalid` handling, drop and resubscribe, dev inspector `window.__paperosSync`, Playwright lag test with Electric in CI.

Parent owns `docs/platform/realtime/record-sync.md` with data-flow diagram, staging lag measurement and the grid demo page.

Out: transport (PAP-270), Yjs documents, retry policy (PAP-148), conflict visuals (PAP-144).

**Spec**

* Libraries `@electric-sql/client` 1.x, `@electric-sql/pglite` 0.3.x with `live`, `@electric-sql/react`; shapes through `/api/sync/shape` with the session (PAP-270).
* Lag budget 500 ms p95 on staging; ordering by server `lsn`, never client clocks.
* Shapes unsubscribe 30 s after the last consumer unmounts.

**Interface contract**

Exposes: `useRecord(table, id)`, `useRecordChanges(id) -> { changedFields, actor, at } | null`, `subscribeShape(def) -> unsubscribe`, `ShapeDef { table, where, columns? }` registry `registerShape()`, `mutate(proc, input, { optimistic, expect })` extension, event `sync.conflict { recordId, table, conflictingFields, mine, theirs, actor, at }` and `sync.remoteChange { recordId, changedFields, actor }` on a local `EventTarget` in `packages/sync/events.ts`, inspector shape `{ shapes[], lagMs, outboxLength }`. Consumes: `useShape`, `useLiveQuery`, PGlite client (PAP-271), shape proxy and predicates (PAP-270, PAP-228), oRPC middleware hooks for stamping `mutation_id uuid` and `updated_by` (PAP-267), outbox from PAP-272, view model tables (PAP-161), PM tables (PAP-100).

**Definition of done**

* All three work packages merged; grid demo: a cell edited in browser A updates B within 500 ms; screenshot pair at 768 and 1440.
* Integration test with a real Electric container in CI.
* Docs with diagram; changelog; Linear comment with staging demo link and lag measurement.

**Test plan**

* Integration (parent): `ops/compose/test.yml` with Postgres and Electric; Playwright writes via API and polls the DOM in a second context; asserts p95 under 500 ms over 50 writes; revokes a role via `/__test` (PAP-240) and asserts rows disappear within one resubscribe.
* Unit tests per work package (echo match drops optimistic row, mismatch emits conflict with correct fields, out-of-order arrival, duplicate echo idempotent, LRU eviction warning, 409 handling).
* Visual: grid demo captured at 768 and 1440 in both themes with the 5 s change flash.

**Demo**

Open the grid demo in two browsers, edit a cell in one and watch it flash in the other with the actor avatar; go offline in one, edit, come back and see it reconcile; open `window.__paperosSync` in devtools. Under two minutes.

**Edge cases**

* Offline an hour, 300 outbox writes vs 2,000 remote rows: remote first, then replay, conflicts per row.
* Row deleted while editing: keep editor with a "deleted by X" banner and restore via PAP-38.
* 500k-row shape: refused without a bounding predicate.
* Schema migration: PGlite hash mismatch resets with a toast.

**Dependencies**

PAP-36 (hard, encoded; children PAP-270 to PAP-272). Soft: PAP-35, PAP-59, PAP-163, PAP-240. Blocks PAP-144, PAP-148, PAP-147 and the planned push transport; consumed by PAP-165, PAP-102, PAP-131, PAP-136.

**Agent**

Builder: Nova (CRDT Engineer) with Forge (Schema Wright) on stamping columns. Reviewer: Sentinel (Code Reviewer, Edge Case Hunter for ordering).

**Size**

L, planned as three M/S work packages (child issues pending the issue limit).
