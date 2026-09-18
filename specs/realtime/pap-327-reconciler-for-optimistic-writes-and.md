---
identifier: "PAP-327"
title: "Reconciler for optimistic writes and conflict events"
project: "realtime"
projectName: "Multiplayer & Realtime"
phase: "P1"
type: "Build"
priority: 1
surfaces: ["Developer"]
milestone: "Record sync and conflict UX"
state: "Backlog"
parent: "PAP-143"
children: []
blockedBy: ["PAP-267", "PAP-272", "PAP-326"]
blocks: ["PAP-328", "PAP-608"]
key: "realtime/record-sync/reconciler"
url: "https://linear.app/paperos/issue/PAP-327/reconciler-for-optimistic-writes-and-conflict-events"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:30:59.972Z"
model: "claude-sonnet-5"
effort: "high"
estimate: 3
dueDate: "2026-09-28"
cycle: null
---

# PAP-327: Reconciler for optimistic writes and conflict events

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / high — Build M

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

*Round 4 amendment (2026-09-18):*
Column ownership: `packages/db` ships a `syncMeta()` column helper (from PAP-32 conventions) that adds `mutation_id uuid` and `updated_by uuid` to a table; the shape registry lint (PAP-326) refuses to register a table without it. The stamping middleware sets both from the request context; PAP-43 jobs stamp `updated_by = actorId ?? service id` so worker writes reconcile too.

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
