---
identifier: "PAP-641"
title: "Global undo manager: scoped undo and redo stacks, coalescing, Yjs UndoManager bridge, toast integration and the edit.undo|redo commands"
project: "input"
projectName: "Multi-Input Control & Accessibility"
phase: "P1"
type: "Build"
priority: 2
surfaces: ["Customer"]
milestone: "Keyboard and command system"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-150", "PAP-289"]
blocks: ["PAP-132", "PAP-144", "PAP-334", "PAP-342"]
key: "r4/input/undo-manager"
url: "https://linear.app/paperos/issue/PAP-641/global-undo-manager-scoped-undo-and-redo-stacks-coalescing-yjs"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:20.862Z"
model: "claude-opus-5"
effort: "high"
estimate: 3
dueDate: "2026-09-23"
cycle: null
---

# PAP-641: Global undo manager: scoped undo and redo stacks, coalescing, Yjs UndoManager bridge, toast integration and the edit.undo|redo commands

**Model / Effort:** Opus 5 (`claude-opus-5`) / high — Build M

**Goal**

PAP-291 registers `edit.undo|redo` as default commands and four issues (PAP-342 grid edits, PAP-334 bulk undo toast, PAP-144 conflict undo, PAP-157 ink) each invent their own undo. Build the one `UndoManager` every surface pushes into, so `mod+z` reverts the last thing the user did wherever they are, including remote-write reverts through the outbox.

**Scope**

In: `packages/input/src/undo/{UndoManager,useUndoable,scopes,yjsBridge,toast}.ts`; `registerUndoable({ label, do, undo, coalesceKey?, scope? })`; scope stack aligned with `CommandScopeProvider` (global → page → editor); Yjs `UndoManager` adapter for Tiptap and canvas docs; `UndoToast` integration ("Undone: Set Status" with Redo); telemetry; `docs/platform/input/undo.md`.

Out: server-side history and per-field undo UI (PAP-333), trash (PAP-334), conflict merge UI (PAP-144), text-field native undo inside `<input>` (browser owns it while focused).

**Spec**

* `UndoManager` keeps one stack per scope (max 200 entries, 10 min TTL); `mod+z` and `mod+shift+z` (and `mod+y` on Windows) run `edit.undo|redo` against the innermost scope with entries, falling back outward; `allowInInput: false` so native text undo wins while typing.
* `registerUndoable` returns a handle; `do()` runs immediately unless `deferred`, `undo()` must be idempotent and may be async (optimistic writes revert via `mutate` inverse patches from PAP-272); failures surface a toast and drop the entry; `coalesceKey` merges consecutive entries within 800 ms (typing into one cell).
* Yjs bridge: `bindYjsUndo(doc, scope, { trackedOrigins })` wraps `y-undo-manager` so document edits and record edits share one keyboard path; capture timeout 500 ms; user-scoped origins so a collaborator's edits are never undone.
* Every undo or redo pushes a `UndoToast` (PAP-237 toast queue) with the label and the inverse action; the PAP-334 bulk toast and PAP-144 banner register their inverse through this API instead of custom toasts.
* Remote invalidation: an entry whose target row version changed remotely (PAP-143 `record.updated` with a different actor) is marked stale; undoing it asks "Row changed since; undo anyway?" and records both versions in the audit reason `undo:<entryId>`.
* Commands `edit.undo|redo|undoHistory` (history popover listing the last 20 labels); telemetry `undo.performed { scope, label, stale }`.

**Interface contract**

Provides: `UndoManager`, `useUndoable`, `useUndoStack(scope)`, `bindYjsUndo`, `UndoEntry` type, `UndoHistoryPopover`, commands, contract port `UndoPort` for `@paperos/contract-input`. Consumes: command registry and scope stack (PAP-289), modality (PAP-150), toast (PAP-237), `mutate` inverse patches (PAP-272), Yjs docs (PAP-140, PAP-142; PAP-603 exposes the Tiptap undo origin), record change events (PAP-143). Consumed by PAP-342, PAP-334, PAP-144, PAP-132 canvas, PAP-157 ink, PAP-630, PAP-629.

**Definition of done**

* Grid cell edit, kanban move (via `onMove`) and a Tiptap comment edit all undo with `mod+z` on the sample pages; history popover works; screenshots at 375 and 1280 in three themes.
* `docs/platform/input/undo.md` with the integration recipe; changelog; Linear comment on PAP-342, PAP-334, PAP-144 naming the API.

**Test plan**

* Unit: stack limits and TTL; scope fallback order; coalescing window; async undo failure drops the entry; stale detection; Yjs bridge captures and ignores foreign origins (fake timers).
* Integration: optimistic `records.update` then undo produces the inverse patch and one audit row with the reason; redo re-applies.
* E2E: edit three cells in `/demo/grid`, press `mod+z` three times and `mod+shift+z` once, open the history popover; type in a comment and confirm native undo still works while focused; second user's edit marks an entry stale.

**Demo**

Reviewer edits a cell, moves a kanban card, presses `mod+z` twice watching both revert with toasts, then opens the history popover and redoes one. Under two minutes.

**Edge cases**

* Undo after navigating away: page-scoped stack cleared, global entries kept.
* Entry whose row was deleted remotely: skipped with a toast "Record no longer exists".
* Two windows (PAP-145): stacks are per window; a `window bus` note documents why they do not merge.
* Reduced motion: toast without slide.

**Dependencies**

PAP-289 (hard, scopes and commands), PAP-150 (hard, chord). Soft: PAP-237, PAP-272, PAP-142, PAP-143. Blocks PAP-342, PAP-334, PAP-144, PAP-132 (they adopt the manager).

**Agent**

Builder: Nova (Product Systems Engineer). Reviewer: Sentinel (Edge Case Hunter, Code Reviewer).

**Size**

M: one session.

*Round 4 critique fix (2026-09-18):* resolved 3 round-4 file keys in this description to Linear identifiers: `r4/realtime/editor-core` = PAP-603, `r4/tables/grid-fill-handle` = PAP-630, `r4/tables/grid-find-and-replace` = PAP-629.
