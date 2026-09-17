---
identifier: "PAP-326"
title: "Live record hooks and shape registry additions"
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
blockedBy: ["PAP-36"]
blocks: ["PAP-327"]
key: "realtime/record-sync/live-hooks-registry"
url: "https://linear.app/paperos/issue/PAP-326/live-record-hooks-and-shape-registry-additions"
source: "Linear snapshot 2026-09-17T13:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T13:05:28.589Z"
model: "claude-sonnet-5"
effort: "high"
---

# PAP-326: Live record hooks and shape registry additions

**Goal**

Turn PAP-271's raw shape hooks into the record-level API every view uses (PAP-143): `useRecord`, `useRecordChanges`, reference-counted subscriptions, per-frame batching, and shape definitions for tables and PM entities with tenant and permission predicates.

**Scope**

In:

* `packages/sync/src/live/`: `useRecord(table, id)`, `useRecordChanges(id)` (5 s window with `changedFields`, `actor`, `at`), `subscribeShape(def)` with reference counting, 30 s idle unsubscribe, LRU cap of 50 shapes with a console warning.
* Shape registry entries: `records`, `fields`, `views` (PAP-161) and PM entities (PAP-100), each with `where` built from tenant and PAP-228 predicates on the proxy side.
* Batching: incoming rows applied per animation frame; live queries suspended for off-screen virtualised rows via a `visible` flag.

Out: reconciliation (sibling 2), resubscribe and inspector (sibling 3).

**Spec**

* Change window uses server `updated_at` and `updated_by`; the actor is resolved through the `users` shape.
* `ShapeDef { table, where, columns? }`; identical defs share one subscription.

**Interface contract**

Exposes hooks above, `registerShape()`, `ShapeDef`, `sync.remoteChange` event. Consumes `useShape`, `useLiveQuery`, PGlite client (PAP-271), proxy `/api/sync/shape` (PAP-270), predicate compiler (PAP-228), table definitions (PAP-161, PAP-100).

**Definition of done**

* Grid demo cells flash with the actor avatar on remote change; shape count stays under 50 in a 60-view stress story; Linear comment with a 768 and 1440 screenshot pair.

**Test plan**

* Vitest: ref counting (two consumers, one unsubscribe keeps the shape), idle timer, LRU eviction and warning, change window expiry with fake timers, batching coalesces 100 rows into one render.
* Integration: Electric container; registering a `records` shape returns only the tenant's rows; permission predicate excludes restricted rows.
* Playwright: two contexts, remote edit flashes within 500 ms.

**Demo**

Open the grid demo in two browsers, edit a cell in one and watch the flash and avatar in the other; open React DevTools and confirm one shape per table. Under two minutes.

**Edge cases**

* Same shape requested with different column lists: separate subscriptions.
* Actor row not yet synced: flash without avatar, filled when it arrives.

**Dependencies**

PAP-271, PAP-270 (hard). PAP-161, PAP-100, PAP-228 (soft). Blocks siblings 2 and 3.

**Agent**

Built by Nova (CRDT Engineer). Reviewed by Sentinel (Code Reviewer).

**Size**

M: hooks and registry with careful lifecycle tests.
