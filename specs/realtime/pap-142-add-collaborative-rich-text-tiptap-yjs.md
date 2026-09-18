---
identifier: "PAP-142"
title: "Add collaborative rich text (Tiptap + Yjs) as the shared editor for docs and comments"
project: "realtime"
projectName: "Multiplayer & Realtime"
phase: "P1"
type: "Build"
priority: 1
surfaces: ["Staff"]
milestone: "Yjs server and presence"
state: "Backlog"
parent: null
children: ["PAP-604", "PAP-603"]
blockedBy: ["PAP-127", "PAP-140", "PAP-666"]
blocks: ["PAP-131", "PAP-317", "PAP-379", "PAP-627", "PAP-654", "PAP-737", "PAP-837", "PAP-856"]
key: "realtime/collab-text"
url: "https://linear.app/paperos/issue/PAP-142/add-collaborative-rich-text-tiptap-yjs-as-the-shared-editor-for-docs"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:28:41.887Z"
model: null
effort: null
estimate: null
dueDate: "2026-09-25"
cycle: null
---

# PAP-142: Add collaborative rich text (Tiptap + Yjs) as the shared editor for docs and comments

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / high — Build M

**Goal**

Ship one collaborative rich-text editor every surface reuses: docs, comments, issue descriptions, notes fields. Tiptap binds to a Yjs document on Hocuspocus so people and agents edit together with live carets, and it degrades to a local editor when a field is not shared.

**Scope**

In:

* `packages/collab/src/editor/` exporting `<RichTextEditor room? value? onChange? readOnly placeholder mentions attachments variant />` on `@tiptap/react` 3.x with starter kit, collaboration and caret extensions, mention, link, placeholder, task lists, tables, `lowlight` code blocks and image nodes uploading via PAP-37.
* Modes: `room` → Yjs via `createDocProvider` (PAP-140); no room → controlled JSON value, same schema.
* Toolbar and bubble menu from PAP-67 primitives; every action registered in PAP-151 (`editor.bold`, `editor.link`, ...).
* Mentions of users, agents and entities via `@` and `#` through a `MentionSource` interface; agents render `ActorBadge` (PAP-60).
* Markdown paste and export via `prosemirror-markdown`; Storybook: local, collaborative (mock provider), read-only, `comment` variant.

Out: anchoring and threads (PAP-131), docs pages (PAP-128), version history UI, AI assistance.

**Spec**

* `Y.XmlFragment` named `default`; other fragments may share the room.
* Caret colours and names from PAP-141; dashed caret for `principalType === 'agent'`.
* `readOnly` follows `connection.readOnly`; toolbar hides and a badge reads "View only".
* `richTextSchema` (Zod) in `packages/core` for `jsonb` columns; `renderRichText(json)` server renderer with `sanitize-html`.
* Undo via `y-undo-manager` scoped to `trackedOrigins`, bound to `edit.undo|redo`.
* `role="textbox"`, toolbar roving tabindex from PAP-152; collaborative chunk under 250 KB gzipped, lazy-loaded; 100k-character doc types at 60 fps.

**Interface contract**

Exposes: `RichTextEditor` props above (`variant: 'full'|'comment'|'inline'`), `richTextSchema` and `RichTextJson` type, `renderRichText(json) -> string`, `richTextToPlain(json)` (used by PAP-131 `body_text` and PAP-138 indexing), `MentionSource { search(q, kinds) -> Mention[] }` and `Mention { kind: user|agent|entity, id, label, avatarUrl? }`, `markdownToRichText()` and `richTextToMarkdown()`, registry command ids `editor.*`. Consumes: provider and room grammar (PAP-140), presence colours (PAP-141), primitives `Button`, `Menu`, `Tooltip`, `Dialog` (PAP-236 to PAP-238), `defineCommand` (PAP-151), roving tabindex (PAP-152), signed uploads (PAP-37), `ActorBadge` (PAP-60), library choice (PAP-127).

**Definition of done**

* Two browsers converge with visible carets; offline edits merge on reconnect.
* Toolbar actions appear in the palette with shortcuts.
* Storybook stories at 320, 768 and 1280 with axe passing; `docs/platform/realtime/editor.md`; changelog; Linear comment with Storybook link and a 20-second two-cursor video (PAP-83).

**Test plan**

* Vitest: markdown round-trip fixtures, mention insertion and serialisation, `richTextSchema` accepts stories and rejects unknown nodes, `renderRichText` strips `<script>` and `javascript:` links, `richTextToPlain` snapshot.
* Integration: mock provider emits remote updates and the editor renders them; `readOnly` toggles with `connection.readOnly`.
* Playwright, two contexts: type in both, assert convergence within 1 s and caret labels; set context A offline, type, reconnect, assert merge; IME composition via `keyboard.insertText` keeps text intact; paste a 5 MB HTML fixture truncates with a toast.
* Performance: 100k-character fixture, measure keydown-to-paint under 16 ms p95 via CDP.
* Visual: Gate 3 captures of the four stories in three themes.

**Demo**

Open a doc in two browsers, type in both and watch carets; press `mod+k`, run “Bold”; toggle one user to view-only and see the badge; paste a markdown list and see it convert. Under two minutes.

**Edge cases**

* Image upload fails: placeholder node with retry.
* Mentioned user loses access: plain text with a tooltip.
* Room switch while mounted: provider recreated, no stale flash.
* Read-only user types: no-op, one toast per session.

**Dependencies**

PAP-127, PAP-140 (hard, encoded). Soft: PAP-141, PAP-67, PAP-151, PAP-152, PAP-37, PAP-60. Blocks PAP-131 and the planned runtime docs store; consumed by PAP-164, PAP-100, PAP-159.

*Round 4 amendment (2026-09-18):*
Work is split into PAP-603 (binding, schema, renderer, plain text, undo, read-only; blocks PAP-131) and PAP-604 (toolbar, commands, mentions, markdown, images). PAP-131 and PAP-317 depend on the core only, which shortens the zero-slack chain 140 → 142 → 131 by roughly one session.

**Agent**

Builder: Nova (CRDT Engineer). Reviewer: Sentinel (Code Reviewer, Security Auditor for the renderer); Iris reviews toolbar styling.

**Size**

M: Tiptap does the heavy lifting; integration, accessibility and two modes remain.

*Round 4 critique fix (2026-09-18):* resolved 2 round-4 file keys in this description to Linear identifiers: `r4/realtime/editor-core` = PAP-603, `r4/realtime/editor-features` = PAP-604.
