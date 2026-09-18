---
identifier: "PAP-272"
title: "Offline write outbox, replay with backoff, leader election and SyncIndicator"
project: "data-layer"
projectName: "Data Layer & Database"
phase: "P1"
type: "Build"
priority: 1
surfaces: ["Staff"]
milestone: "Local-first sync working"
state: "Backlog"
parent: "PAP-36"
children: []
blockedBy: ["PAP-268", "PAP-271"]
blocks: ["PAP-143", "PAP-327", "PAP-609"]
key: "child/PAP-36/17"
url: "https://linear.app/paperos/issue/PAP-272/offline-write-outbox-replay-with-backoff-leader-election-and"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:21:27.893Z"
model: "claude-sonnet-5"
effort: "high"
estimate: 3
dueDate: "2026-09-25"
cycle: null
---

# PAP-272: Offline write outbox, replay with backoff, leader election and SyncIndicator

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / high — Build M

**Goal**

Add the write path: `mutate()` applies an optimistic update to PGlite and either calls oRPC directly or enqueues in `_outbox`; replay runs with exponential backoff under a `navigator.locks` leader; `<SyncIndicator/>` shows online, offline, syncing and error states; the demo route proves an offline edit survives reload and replays.

**Scope**

In: `_outbox` table, `mutate()`, replay loop, failure UI (retry or discard), leader election, `useSyncStatus`, `SyncIndicator` in `@paperos/ui`, demo route edit flow.

Out: ordering guarantees across entities and conflict UX (PAP-148, PAP-143 extend).

**Spec**

* Backoff 1 s to 60 s, 20 attempts, then `failed`.
* `FORBIDDEN` on replay: mark failed, show reason, roll back the optimistic row.
* Tombstones from shapes remove local rows; outbox writes against them fail cleanly.

**Interface contract**

Provides: `mutate`, `useSyncStatus`, `SyncIndicator`, `_outbox` schema. Consumes: hooks and PGlite (child 2), oRPC client (PAP-35 child 2). Consumed by PAP-148, PAP-143.

**Definition of done**

* Playwright: rename offline, reload, go online, replay succeeds (recording).
* Two tabs: only the leader replays.
* Vitest for state machine and backoff; `SyncIndicator` screenshots at 375, 768, 1280, 1920.

**Test plan**

* Unit: outbox transitions; backoff schedule; rollback on `FORBIDDEN`.
* E2E: offline edit and replay; leader election with two pages.
* Visual: four indicator states.

**Demo**

Reviewer goes offline in DevTools, renames a workspace (indicator shows 1 pending), reloads, goes online and watches the indicator clear as the server row updates. Under 90 seconds.

**Edge cases**

* Expired handle after long offline: full re-fetch, outbox kept.
* Clock skew: server timestamps only.

**Dependencies**

Child 2, PAP-35 child 2 (hard). Feeds PAP-143, PAP-148.

**Agent**

Built by Forge with Nova (CRDT Engineer). Reviewed by Sentinel.

**Size**

M
