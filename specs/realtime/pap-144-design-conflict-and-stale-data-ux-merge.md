---
identifier: "PAP-144"
title: "Design conflict and stale-data UX: merge banners, last-writer indicators, undo"
project: "realtime"
projectName: "Multiplayer & Realtime"
phase: "P1"
type: "Spec"
priority: 2
surfaces: ["Customer", "Staff"]
milestone: "Record sync and conflict UX"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-143", "PAP-328"]
blocks: ["PAP-148"]
key: "realtime/conflict-ux"
url: "https://linear.app/paperos/issue/PAP-144/design-conflict-and-stale-data-ux-merge-banners-last-writer-indicators"
source: "Linear snapshot 2026-09-17T13:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T13:05:30.221Z"
model: "claude-sonnet-5"
effort: "high"
---

# PAP-144: Design conflict and stale-data UX: merge banners, last-writer indicators, undo

**Goal**

Specify how PaperOS tells a user that someone else changed what they are looking at or editing, and what they can do about it. Output: a UX spec, five component definitions with spec IDs and static Storybook mocks, so record sync, offline queue and the tables engine implement one behaviour.

**Scope**

In:

* `docs/platform/realtime/conflict-ux.md`: field-level stale indicators, "updated by X just now" attribution, merge banner for form conflicts, last-writer-wins rules per field type, undo of a remote overwrite, pending and failed-write states.
* Component definitions (props, states, copy) for `StaleFieldIndicator`, `ConflictBanner`, `RemoteChangeFlash`, `PendingWriteBadge`, `FailedWriteDialog`, mapped to spec IDs `ui.conflictBanner` etc. in PAP-74's registry.
* Decision table per PAP-164 field type: auto-merge (rich text via Yjs, multi-select union), last-writer-wins with attribution (number, date, single select), manual resolution (currency over a threshold, status transitions).
* Copy deck `packages/collab/src/copy/conflicts.ts`; static stories at 375 and 1280.

Out: implementation (follow-ups filed here), Yjs merge, server merge logic.

**Spec**

* Untouched field: remote change applies silently with a 5 s flash and tooltip "Changed by Ada 3 s ago". Dirty field: inline `ConflictBanner` with "Keep mine", "Use theirs", "Compare"; never block typing.
* Undo of a remote overwrite via command `edit.undoRemote` (PAP-151) writes the previous value as a new write.
* Offline: `PendingWriteBadge`, resolves to a check for 2 s; failures open `FailedWriteDialog`.
* Agent actors use `ActorBadge` linking to the prompt log session (PAP-135).
* Banner `role="alert"` once per record per 10 s; icon plus text, never colour alone.

**Interface contract**

Exposes: TypeScript interfaces `StaleFieldIndicatorProps { field, actor, at }`, `ConflictBannerProps { conflict: SyncConflict, onKeepMine, onUseTheirs, onCompare }`, `RemoteChangeFlashProps`, `PendingWriteBadgeProps { state: queued|sending|failed }`, `FailedWriteDialogProps` in `packages/collab/src/conflicts/types.ts`; `resolutionPolicy(fieldType) -> 'merge'|'lww'|'manual'` table exported as JSON; spec IDs registered in `registry.json` (PAP-74); copy keys. Consumes: `sync.conflict` and `sync.remoteChange` event shapes from PAP-143, field type list from PAP-164, `ActorBadge` (PAP-60), `Timeline` and `Badge` (PAP-71), ADR format (PAP-130), permalink grammar from PAP-135.

**Definition of done**

* Spec merged with the decision table covering every PAP-164 field type (unknowns marked TBD with owner).
* Five definitions with props, copy and spec IDs registered; static stories at 375 and 1280, axe clean, screenshots attached.
* Follow-up issues filed in tables, realtime and spec-builder and linked; ADR for last-writer-wins vs manual recorded (PAP-130).
* Docs changelog entry; Linear comment summarising the rules in ten lines; rules ride in the next release digest (PAP-89), no separate Needs Justin item.

**Test plan**

* Unit: `resolutionPolicy()` returns a value for every field type in PAP-164's enum (test fails when a new type is added without a row); copy deck has no untranslated keys.
* Component: static stories render each state (default, hover, focus, dense, RTL); axe on each; `role="alert"` present exactly once.
* Visual: Gate 3 captures of the five stories at 375 and 1280 in both themes serve as the approved reference for PAP-148 and PAP-165 implementations.
* Review: Nova confirms the event shapes match PAP-143's `sync.conflict` type by importing it in the story fixtures.

**Demo**

Open Storybook “Conflicts”, step through the five states, open the RTL and dense variants, then open the spec's decision table and find “currency” to read why it requires manual resolution. Under two minutes.

**Edge cases**

* Three edits in a second: banner shows the latest actor "and 1 other".
* Conflict on a hidden column: row-level indicator.
* Open dropdown: defer applying until closed.
* Agent wrote later than the human: "Keep mine" wins and posts a comment mentioning the agent.
* Invalid status transition after remote change: validation error, not a conflict banner.

**Dependencies**

PAP-143 (hard, encoded). Soft: PAP-164, PAP-74, PAP-71, PAP-130. Blocks PAP-148; consumed by PAP-165, PAP-120.

**Agent**

Builder: Quill (Page Spec Writer) with Iris (Component Crafter) for mock stories. Reviewer: Nova and Sentinel (Edge Case Hunter).

**Size**

S: a spec and mock stories, no production code.
