---
identifier: "PAP-603"
title: "`RichTextEditor` core: Tiptap 3 with Yjs collaboration and carets, room and local modes, `richTextSchema`, `renderRichText`, `richTextToPlain`, undo manager and read-only binding"
project: "realtime"
projectName: "Multiplayer & Realtime"
phase: "P1"
type: "Build"
priority: 1
surfaces: ["Customer"]
milestone: "Yjs server and presence"
state: "Backlog"
parent: "PAP-142"
children: []
blockedBy: ["PAP-127", "PAP-140", "PAP-666"]
blocks: ["PAP-131", "PAP-317", "PAP-379", "PAP-604"]
key: "r4/realtime/editor-core"
url: "https://linear.app/paperos/issue/PAP-603/richtexteditor-core-tiptap-3-with-yjs-collaboration-and-carets-room"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:15.152Z"
model: "claude-opus-5"
effort: "high"
estimate: 3
dueDate: "2026-09-25"
cycle: null
---

# PAP-603: `RichTextEditor` core: Tiptap 3 with Yjs collaboration and carets, room and local modes, `richTextSchema`, `renderRichText`, `richTextToPlain`, undo manager and read-only binding

**Model / Effort:** Opus 5 (`claude-opus-5`) / high — Build M

**Goal**

First half of PAP-142 and the link on the zero-slack chain 140 → 142 → 131: the editor that comments, docs, issue descriptions and notes fields bind to. Tiptap on a Yjs fragment when a room is given, a controlled JSON value otherwise, one Zod schema for the stored JSON, a sanitised server renderer and a plain-text projection for indexing. Toolbar, mentions, markdown and uploads are the sibling, so comments can start against this core as soon as it merges.

**Scope**

In: `packages/collab/src/editor/{RichTextEditor,schema,render,plain,undo}.ts(x)` on `@tiptap/react` 3.x with starter kit, `@tiptap/extension-collaboration` and `-collaboration-caret`, placeholder, link, task list, table and `lowlight` code block extensions (no toolbar yet); props `room? value? onChange? readOnly placeholder variant: 'full'|'comment'|'inline'`; `richTextSchema` (Zod) in `packages/core` for `jsonb` columns; `renderRichText(json) -> string` with `sanitize-html`; `richTextToPlain(json)`; `y-undo-manager` scoped to `trackedOrigins` bound to `edit.undo|redo`; `readOnly` following `connection.readOnly` with a 'View only' badge; lazy-loaded collaborative chunk; Storybook local, collaborative (mock provider) and read-only stories.

Out: Toolbar, bubble menu, `editor.*` commands, mentions, markdown paste and export, image upload, Storybook for the comment variant (sibling PAP-604); anchoring and threads (PAP-131); version history (PAP-607).

**Spec**

* `Y.XmlFragment` named `default`; other fragments may share the room; provider from `createDocProvider` (PAP-140); room switch while mounted recreates the provider without a stale flash.
* Caret colours and names from PAP-141's `presenceColor` and awareness (soft: hash fallback); dashed caret for `principalType === 'agent'`.
* `richTextSchema` accepts every node and mark the extensions emit and rejects unknown nodes; `renderRichText` strips `<script>`, event handlers and `javascript:` links and rewrites internal entity links through `formatEntityKey` (PAP-302).
* `richTextToPlain` produces the text PAP-131 stores in `body_text` and PAP-138 indexes; table cells joined by tabs, list items by newlines.
* Accessibility: `role="textbox"`, `aria-multiline`, label from props; collaborative chunk under 250 KB gzipped; a 100k-character document types at 60 fps (keydown to paint under 16 ms p95 via CDP).

**Interface contract**

Provides: `RichTextEditor` (core props), `richTextSchema`, `RichTextJson`, `renderRichText`, `richTextToPlain`, `useEditorUndo()`, command ids `edit.undo|redo`, mock provider for stories.

Consumes: Library decision (PAP-127), provider and room grammar (PAP-140), presence colours (PAP-141, soft), `formatEntityKey` (PAP-302), `connection.readOnly` semantics (PAP-140), `defineCommand` for undo (PAP-151, soft). Consumed by PAP-131, PAP-317, PAP-379, PAP-164 rich text field, PAP-100, PAP-159, the sibling.

**Definition of done**

* Two browsers converge with visible carets within 1 s; offline edits merge on reconnect (Playwright, two contexts).
* `richTextSchema` accepts every story and rejects unknown nodes; `renderRichText` strips script and `javascript:` fixtures; `richTextToPlain` snapshot.
* Performance: 100k-character fixture under 16 ms p95 keydown to paint; stories at 320, 768, 1280 with axe passing; `docs/platform/realtime/editor.md` core section; changelog; Linear comment with a 20-second two-cursor video.

**Test plan**

* Unit: schema accept and reject fixtures, renderer sanitisation, plain projection, undo scoping to own origin, mode switching between room and local.
* E2E: two contexts type concurrently and converge; context A offline then reconnect merges; IME composition via `keyboard.insertText` keeps text intact; read-only user sees the badge and cannot type.

**Demo**

Open a doc in two browsers, type in both and watch carets; toggle one user to view-only and see the badge; press undo and only your own edits revert. Under two minutes.

**Edge cases**

* Read-only user types: no-op, one toast per session.
* Room switch while mounted: provider recreated, no stale flash.
* Paste of a 5 MB HTML fixture: truncated with a toast (sibling refines the markdown path).
* Provider not yet connected: local edits buffered by Yjs and merged on connect.

**Dependencies**

Blocked by PAP-127 and PAP-140 (hard). Soft: PAP-141, PAP-302, PAP-151. Blocks PAP-131, PAP-317, PAP-379 and the sibling PAP-604.

**Agent**

Builder: Nova (CRDT Engineer). Reviewer: Sentinel (Code Reviewer; Security Auditor for the renderer).

**Size**

M: one session.

*Round 4 critique fix (2026-09-18):* resolved 2 round-4 file keys in this description to Linear identifiers: `r4/realtime/doc-history` = PAP-607, `r4/realtime/editor-features` = PAP-604.
