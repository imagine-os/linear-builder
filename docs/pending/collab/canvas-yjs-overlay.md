---
key: "collab/canvas/yjs-overlay"
title: "Collaborative overlay: notes, regions, overrides in Yjs"
project: "collab"
parent: "PAP-132"
phase: "P1"
type: "Build"
priority: 1
size: null
surfaces: ["Staff", "Developer"]
milestone: "Comments and canvas"
intendedState: "Backlog"
blockedBy: []
blocks: []
source: "round2/agent3/pending-issues.json"
linearDocument: null
status: "pending"
---

# Collaborative overlay: notes, regions, overrides in Yjs

**Goal**

Make the canvas (PAP-132) collaborative: position overrides, sticky notes, regions, hidden sets and viewport bookmarks live in a Yjs document on Hocuspocus, with presence cursors, undo and a per-selection reset to the generated layout.

**Scope**

In:

* Yjs doc `canvas:<appId>` (PAP-140 room) with `Y.Map`s `positions`, `notes`, `regions`, `hidden`, `viewportBookmarks`; `useCanvasOverlay(room)` merging overrides onto the generated graph.
* Presence cursors and selections via PAP-141 on `[data-presence-surface="canvas"]`.
* Undo and redo with `y-undomanager` scoped to the local user; commands `edit.undo|redo` (PAP-151).
* "Reset layout" clears overrides for selected nodes only; orphan cleanup action for overrides whose node id no longer exists.

Out: node rendering (sibling 1), filters and export (sibling 3).

**Spec**

* Merge rule: generated position unless an override exists.
* Room authorised for tenant staff by PAP-140's auth hook; read-only from JSON with a banner when Hocuspocus is down.
* Notes are markdown rendered with `renderMdx` (PAP-128).

**Interface contract**

Exposes `CanvasOverlayDoc` schema, `useCanvasOverlay(room) -> { positions, notes, regions, hidden, bookmarks, setPosition, addNote, reset }`, `OverlayLayer` component reused by PAP-137. Consumes `createDocProvider` (PAP-140), presence payload (PAP-141), node registry (sibling 1), `defineCommand` (PAP-151).

**Definition of done**

* Two contexts move a node and see it within 1 s; note added in one appears in the other; undo works per user.
* Linear comment with a two-context screenshot at 1280.

**Test plan**

* Vitest: override merge (with and without override), reset for selection only, orphan detection, undo scope excludes remote changes.
* Integration: two `Y.Doc`s connected through a local Hocuspocus converge on `positions` after concurrent drags.
* Playwright, two contexts: drag in A, assert B position within 1 s; add a note; undo in A does not undo B's change.

**Demo**

Open the canvas in two browsers, drag a node and add a sticky note in one, watch both appear in the other, press `mod+z` to undo only your move, click Reset layout on a selection. Under two minutes.

**Edge cases**

* Two users drag one node: last writer wins with a cursor highlight.
* Hocuspocus down: read-only with a banner.
* Renamed page id: orphan override listed for cleanup.

**Dependencies**

Sibling 1, PAP-140 (hard). PAP-141, PAP-151, PAP-128 (soft). Blocks sibling 3.

**Agent**

Built by Nova (CRDT Engineer). Reviewed by Sentinel (Code Reviewer).

**Size**

M: Yjs schema, merge and undo semantics.
