---
key: "realtime/record-sync/reconciler"
title: "Reconciler for optimistic writes and conflict events"
project: "realtime"
parent: "PAP-143"
phase: "P1"
type: "Build"
priority: 1
size: null
surfaces: ["Developer"]
milestone: "Record sync and conflict UX"
intendedState: "Backlog"
blockedBy: []
blocks: []
source: "round2/agent3/pending-issues.json"
linearDocument: null
status: "pending"
---

# Reconciler for optimistic writes and conflict events

**Goal**

Make optimistic writes and incoming shape rows agree (PAP-143): stamp every write with a `mutation_id`, drop optimistic rows when their echo arrives, compare expected and actual state field by field, and emit the `sync.conflict` event PAP-144 and PAP-148 consume.

**Scope**

In:

* API middleware in PAP-267 stamping `mutation_id uuid` and `updated_by principal_id` on written rows (Forge adds the columns to synced tables).
* Client: optimistic rows carry `_pending: true`; `mutate(proc, input, { optimistic, expect: (before) => after })` from PAP-272 extended; echo matching by `mutation_id`; mismatch emits `sync.conflict { recordId, table, conflictingFields, mine, theirs, actor, at }`.
* Ordering by server `lsn`; duplicate echoes dropped idempotently; out-of-order arrival handled by version comparison.

Out: hooks (sibling 1), UI (PAP-144), retry (PAP-148).

**Spec**

* Comparison is per field with type-aware equality (dates, decimals as strings, arrays order-insensitive for multi-select).
* Remote rows apply before outbox replay after a reconnect.

**Interface contract**

Exposes `mutate()` extension, `Reconciler` class, `sync.conflict` event type in `packages/sync/events.ts`. Consumes outbox (PAP-272), oRPC middleware chain (PAP-267), synced table columns (PAP-32), hooks (sibling 1).

**Definition of done**

* Optimistic edit resolves without flicker; a forced mismatch emits a conflict with the right fields; Linear comment with the test output.

**Test plan**

* Vitest: echo match drops the optimistic row, mismatch lists exactly the conflicting fields, out-of-order `lsn` handled, duplicate echo idempotent, type-aware equality fixtures, reconnect applies remote before replay.
* Integration: API middleware stamps columns on a real write; `updated_by` matches the `callAs` principal.

**Demo**

Edit a cell, watch the pending style clear when the echo arrives; in devtools run `__paperosSync.forceConflict('records', id)` and see the conflict event logged with `conflictingFields`. Under two minutes.

**Edge cases**

* Server rejects the write: optimistic row reverted, event `sync.rejected`.
* Row deleted remotely before the echo: conflict with `theirs: null`.

**Dependencies**

Sibling 1, PAP-272, PAP-267 (hard). Blocks sibling 3; consumed by PAP-144, PAP-148.

**Agent**

Built by Nova (CRDT Engineer) with Forge (Schema Wright) for columns. Reviewed by Sentinel (Edge Case Hunter).

**Size**

M: subtle ordering semantics with a thorough unit suite.
