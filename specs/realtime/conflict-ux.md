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
blockedBy: ["PAP-143"]
blocks: ["PAP-148"]
key: "realtime/conflict-ux"
url: "https://linear.app/paperos/issue/PAP-144/design-conflict-and-stale-data-ux-merge-banners-last-writer-indicators"
source: "plan/specs/bucket-5.json (round-1 canonical spec JSON)"
---

# PAP-144: Design conflict and stale-data UX: merge banners, last-writer indicators, undo

**Goal**

Specify how PaperOS tells a user that someone else changed what they are looking at or editing, and what they can do about it. The output is a written UX spec plus page-spec-ready component definitions so that `realtime/record-sync`, `realtime/offline-queue` and the tables engine implement one consistent behaviour instead of ad hoc alerts.

**Scope**

In:
- Spec document `docs/platform/realtime/conflict-ux.md` covering: field-level stale indicators, "updated by X just now" attribution, merge banner for form conflicts, last-writer-wins rules per field type, undo of a remote overwrite, offline pending states and failed-write recovery.
- Component definitions (props, states, copy) for `StaleFieldIndicator`, `ConflictBanner`, `RemoteChangeFlash`, `PendingWriteBadge`, `FailedWriteDialog`, each mapped to a spec component ID (`ui.conflictBanner` etc.) for `design-system/component-spec-mapping`.
- Decision table: for each field type from `tables/field-types` whether concurrent edits auto-merge (rich text via Yjs, multi-select union), last-writer-wins with attribution (number, date, single select), or require manual resolution (currency amounts over a threshold, status transitions).
- Copy deck in `packages/collab/src/copy/conflicts.ts` reviewed for tone (calm, specific, names the actor).
- Storybook mock stories (static) demonstrating each state at 375 and 1280 px so Justin can approve visuals before code lands elsewhere.

Out: implementation in tables and forms (follow-up issues filed by this spec), Yjs text merge (handled by CRDT), server-side merge logic.

**Spec**

- Trigger inputs come from `realtime/record-sync`: `conflict` events `{ recordId, conflictingFields, mine, theirs, actor, at }` and `useRecordChanges` for non-conflicting remote changes.
- Rules: if the user has not touched a field, a remote change applies silently with a 5 s flash and tooltip "Changed by Ada 3 s ago". If the user has a dirty local value in the same field, show `ConflictBanner` inline above the form section with two buttons: "Keep mine" (re-submit) and "Use theirs" (discard local), plus "Compare" opening a side-by-side sheet. Never block typing.
- Undo: after a remote value overwrote a non-dirty field, `Ctrl/Cmd+Z` inside that field restores the previous value as a new write (attributed to the current user), via `input/command-registry` command `edit.undoRemote`.
- Offline: `PendingWriteBadge` (clock icon) on saved-but-unsynced rows; on reconnect it resolves to a check for 2 s; failures open `FailedWriteDialog` with retry/discard/copy-to-clipboard.
- Agents: when the actor is an agent, attribution uses `ActorBadge` and links to the prompt log entry (`collab/prompt-log-ui`) so a human can see why.
- Accessibility: banner is `role="alert"` once, indicators are described via `aria-describedby`; colour is never the only signal (icon plus text).
- Each component gets a state matrix (default, hover, focus, dense, RTL) in the spec.

**Definition of done**

- Spec merged with the decision table covering every field type in `tables/field-types` (mark unknowns as "TBD with owner").
- Five component definitions with props (TypeScript interfaces), copy and spec IDs registered.
- Static Storybook stories for all five states at 375 and 1280 px, axe clean, screenshots attached.
- Follow-up Linear issues created in `tables`, `realtime` and `spec-builder` for implementation, linked from the spec.
- ADR-style rationale for last-writer-wins vs manual resolution recorded in `collab/decision-log`.
- Changelog (docs) entry and a Linear comment summarising the rules in ten lines with the Storybook link; the rules ride along in the next weekly release digest (`quality/review-report`) rather than opening a separate Needs Justin item.

**Edge cases**

- Three people edit the same field within a second: banner shows the latest actor and "and 1 other".
- Conflict on a field the user cannot see (hidden column): show a row-level indicator instead of nothing.
- Remote change arrives while a select dropdown is open: defer applying until it closes.
- Agent and human conflict where the agent wrote later: the human's "Keep mine" must still win and post a comment mentioning the agent.
- Status field transitions that are invalid after the remote change (e.g., "Done" to "In Progress" not allowed): show a validation error, not a conflict banner.
- Screen reader users: alerts must not fire more than once per record per 10 s.

**Dependencies**

- `realtime/record-sync` (event shapes), `tables/field-types` (type list), `design-system/component-spec-mapping`, `design-system/data-display`, `collab/decision-log`. Consumed by `realtime/offline-queue`, `tables/grid-view`, `spec-builder/layout-codegen`.

**Agent**

Builder: Quill (Page Spec Writer sub-agent) with Iris (Component Crafter) for the mock stories. Reviewer: Nova (owns implementation) and Sentinel (Edge Case Hunter); Justin sees the rules in the weekly release digest and only objects if he disagrees.

**Size**

S: a spec and mock stories, no production code.
