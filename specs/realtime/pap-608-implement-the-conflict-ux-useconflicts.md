---
identifier: "PAP-608"
title: "Implement the conflict UX: `useConflicts()` on reconciler events, `ConflictBanner`, `StaleFieldIndicator`, `RemoteChangeFlash`, `PendingWriteBadge` and `FailedWriteDialog` with keep-mine, use-theirs, compare and `edit.undoRemote`"
project: "realtime"
projectName: "Multiplayer & Realtime"
phase: "P1"
type: "Build"
priority: 2
surfaces: ["Customer"]
milestone: "Record sync and conflict UX"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-144", "PAP-327"]
blocks: []
key: "r4/realtime/conflict-ux-impl"
url: "https://linear.app/paperos/issue/PAP-608/implement-the-conflict-ux-useconflicts-on-reconciler-events"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:20:40.379Z"
model: "claude-sonnet-5"
effort: "high"
estimate: 3
dueDate: "2026-09-28"
cycle: null
---

# PAP-608: Implement the conflict UX: `useConflicts()` on reconciler events, `ConflictBanner`, `StaleFieldIndicator`, `RemoteChangeFlash`, `PendingWriteBadge` and `FailedWriteDialog` with keep-mine, use-theirs, compare and `edit.undoRemote`

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / high — Build M

**Goal**

PAP-144 is a spec with static mocks and says 'follow-up issues filed in tables, realtime and spec-builder'; none exists. PAP-148 consumes `PendingWriteBadge` and `FailedWriteDialog` definitions, PAP-165 and PAP-342 expect a banner when a cell changes under an edit, PAP-333 needs field attribution. This builds the five components against the real `sync.conflict` and `sync.remoteChange` events from PAP-327 and wires the three resolutions.

**Scope**

In: `packages/collab/src/conflicts/{useConflicts,ConflictBanner,StaleFieldIndicator,RemoteChangeFlash,PendingWriteBadge,FailedWriteDialog}.tsx` implementing the PAP-144 interfaces and spec IDs (`ui.conflictBanner` and friends registered in PAP-74); `useConflicts(recordId?)` subscribing to the reconciler event target (PAP-327) and the outbox status (PAP-148, soft); resolutions: keep mine (rewrite my value as a new write with `expect` cleared), use theirs (discard local, apply remote), compare (side-by-side dialog with field-level pick); command `edit.undoRemote` (PAP-151) writing the previous value as a new write; `resolutionPolicy(fieldType)` consumed for auto-merge versus banner; copy from `packages/collab/src/copy/conflicts.ts`; integration into the grid editing child (PAP-342) and the record page (PAP-333) through a `ConflictBoundary` wrapper; docs section.

Out: Rules and copy (PAP-144), reconciler semantics (PAP-327), queue UI (PAP-148 owns `SyncQueueSheet`), Yjs merges.

**Spec**

* Untouched field with a remote change: applied silently with `RemoteChangeFlash` for 5 s and a tooltip 'Changed by Ada 3 s ago' (actor from `useRecordChanges`, PAP-326); dirty field: `ConflictBanner` inline, `role="alert"` once per record per 10 s, never blocks typing.
* Keep mine posts the local value through `mutate(..., { expect: undefined })` so the server accepts it and emits an audit row with reason `conflict.keep_mine`; agent actors get a comment mention when overwritten (PAP-144 rule; soft: PAP-131).
* Compare dialog lists every conflicting field with mine, theirs and a per-field choice; invalid combinations (status transitions) validate before submit and show a validation error, not a conflict.
* `PendingWriteBadge` states `queued|sending|failed` from the outbox; `FailedWriteDialog` offers retry and discard and links to the queue sheet when PAP-148 is present.
* Manual-resolution field types from `resolutionPolicy` (currency over threshold, status) always open the banner even when the field is not dirty.
* `ConflictBoundary` provides record context so any form or grid row inside gets the behaviour without per-field wiring.

**Interface contract**

Provides: Five components implementing PAP-144's props, `useConflicts()`, `ConflictBoundary`, command `edit.undoRemote`, stories with live event fixtures.

Consumes: Interfaces, spec IDs and copy (PAP-144), reconciler events and `mutate` extension (PAP-327), change window (PAP-326), outbox status (PAP-148, soft), `resolutionPolicy` and field types (PAP-164, soft), `ActorBadge` (PAP-60, soft), command registry (PAP-151, soft), primitives (PAP-236 to PAP-238). Consumed by PAP-342, PAP-333, PAP-148, PAP-165, PAP-120 scaffolds.

**Definition of done**

* Forced conflict through `__paperosSync.forceConflict()` shows the banner on the dirty cell; keep mine, use theirs and compare each produce the expected server state and audit rows (Playwright on the grid demo).
* Remote change on an untouched field flashes and attributes; `edit.undoRemote` restores; agent overwrite posts the mention when comments exist.
* Stories match PAP-144's approved Gate 3 references at 375 and 1280 in both themes; axe clean; docs; changelog; Linear comment with the video.

**Test plan**

* Unit: event to state mapping, once-per-10-s alert throttle, resolution payload builders, policy lookup per field type, boundary context propagation.
* E2E: two contexts editing the same cell; offline edit then reconnect producing a conflict; compare dialog with three fields.

**Demo**

Edit a cell in one browser while another user changes it; read the banner, click Compare, pick per field, submit; then trigger a remote change on an untouched field and watch the flash. Under two minutes.

**Edge cases**

* Three edits within a second: banner shows the latest actor 'and 1 other'.
* Conflict on a hidden column: row-level indicator with a link to reveal.
* Open dropdown on the conflicting field: apply deferred until it closes.
* Row deleted remotely mid-edit: 'deleted by X' banner; restore via PAP-334.

**Dependencies**

Blocked by PAP-144 and PAP-327 (hard). Soft: PAP-326, PAP-148, PAP-164, PAP-60, PAP-151, PAP-131, PAP-236 to PAP-238, PAP-334. Consumed by PAP-342, PAP-333, PAP-148, PAP-165, PAP-120.

**Agent**

Builder: Nova (Views Engineer) with Iris on components. Reviewer: Sentinel (Edge Case Hunter; Visual Inspector against the PAP-144 references).

**Size**

M: one session.
