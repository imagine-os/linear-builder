---
identifier: "PAP-142"
title: "Add collaborative rich text (Tiptap + Yjs) as the shared editor for docs and comments"
project: "realtime"
projectName: "Multiplayer & Realtime"
phase: "P1"
type: "Build"
priority: 1
surfaces: ["Customer", "Staff"]
milestone: "Yjs server and presence"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-127", "PAP-140"]
blocks: ["PAP-131"]
key: "realtime/collab-text"
url: "https://linear.app/paperos/issue/PAP-142/add-collaborative-rich-text-tiptap-yjs-as-the-shared-editor-for-docs"
source: "plan/specs/bucket-5.json (round-1 canonical spec JSON)"
---

# PAP-142: Add collaborative rich text (Tiptap + Yjs) as the shared editor for docs and comments

**Goal**

Ship one collaborative rich-text editor that every PaperOS surface reuses: docs, comments, issue descriptions, notes fields in tables. It binds Tiptap to a Yjs document on the Hocuspocus server so multiple people and agents can edit simultaneously with live carets, and it degrades to a local-only editor when offline or when a field is not shared.

**Scope**

In:
- `packages/collab/src/editor/` exporting `<RichTextEditor room? value? onChange? readOnly placeholder mentions attachments />` built on `@tiptap/react` 3.x with `@tiptap/starter-kit`, `@tiptap/extension-collaboration`, `@tiptap/extension-collaboration-caret`, `@tiptap/extension-mention`, `@tiptap/extension-link`, `@tiptap/extension-placeholder`, task lists, tables, code blocks with `lowlight` highlighting, and image nodes uploading through `data-layer/file-storage`.
- Two modes: `room` given means Yjs-backed via `createDocProvider` from `realtime/yjs-server`; no room means controlled local editor with JSON value (same schema).
- Toolbar and bubble menu built from `design-system/primitives` (Button, Menu, Tooltip) with all actions registered in `input/command-registry` (`editor.bold`, `editor.link`, ...), so shortcuts and the command palette work.
- Mentions of users, agents and entities via `@` and `#`, resolved by a `MentionSource` interface; mentions render `ActorBadge` for agents.
- Markdown paste and export (`packages/collab/src/editor/markdown.ts`) using `prosemirror-markdown`.
- Storybook stories: local, collaborative (mocked provider), read-only, comment variant (compact, single toolbar row).

Out: comments anchoring and threads (`collab/comments`), docs engine pages (`collab/docs-engine`), version history UI, AI writing assistance.

**Spec**

- Yjs mapping: `Y.XmlFragment` named `default` inside the room document; the same room may host other fragments (canvas, metadata).
- Caret colours and names come from `realtime/presence` payload; agents show a distinct caret style defined later by `realtime/agent-presence` (use a dashed caret for `principalType === 'agent'` now).
- `readOnly` derives from the provider's `connection.readOnly` when collaborative; the toolbar hides and a `Badge` reads "View only".
- Content JSON schema exported as `richTextSchema` (Zod) in `packages/core` for storing non-collaborative fields in Postgres `jsonb` columns; a `renderRichText(json)` server-side renderer produces sanitised HTML (via `@tiptap/html` plus `sanitize-html`) for emails and PDFs.
- Undo/redo uses `y-undo-manager` scoped to the local user's changes (`trackedOrigins`), bound to the registry commands `edit.undo`/`edit.redo`.
- Accessibility: `role="textbox"` with `aria-multiline`, toolbar `role="toolbar"` with roving tabindex from `input/focus-management`, all buttons labelled; link dialog is a `Dialog` primitive.
- Performance: 100k-character document types with no dropped frames at 60 fps on a mid-range laptop; measured in the Playwright test with `performance.now()` between keydown and paint.
- Size budget: collaborative editor chunk under 250 KB gzipped, lazy-loaded via `React.lazy`.

**Definition of done**

- Two browsers editing the same room converge and show each other's carets; offline edits in one browser merge on reconnect (Playwright test with network offline).
- Vitest tests for markdown round-trip, mention insertion, schema validation and the server renderer sanitising script tags.
- Storybook stories for all variants at 320, 768 and 1280 px with axe passing.
- Toolbar actions appear in the command palette with correct shortcuts.
- Docs `docs/platform/realtime/editor.md` with usage for both modes.
- Changelog entry, Linear comment with Storybook link and a 20-second video of two-cursor editing from `quality/video-replays`.

**Edge cases**

- Pasting 5 MB of HTML from Word: strip styles, cap at 1 MB, and toast the truncation.
- Image upload fails: keep a placeholder node with a retry action; never lose the surrounding text.
- Mention of a user who later loses access: render as plain text with a tooltip "no longer has access".
- Room switches while the editor is mounted (navigating between comments): destroy and recreate the provider; no stale content flashes.
- IME composition (Japanese, Korean) must not be broken by collaboration transforms; test with Playwright `keyboard.insertText`.
- Read-only user tries to type: no-op, brief toast once per session.

**Dependencies**

- `realtime/yjs-server`, `collab/collab-research` (confirms Tiptap over BlockNote), `design-system/primitives`, `input/command-registry`, `data-layer/file-storage`, `realtime/presence`. Consumed by `collab/comments`, `collab/docs-engine`, `tables/field-types` (rich text field), `pm-linear/pm-data-model`.

**Agent**

Builder: Nova (CRDT Engineer sub-agent). Reviewer: Sentinel (Code Reviewer and Security Auditor for the HTML renderer); Iris reviews toolbar styling.

**Size**

M: Tiptap does the heavy lifting; the work is integration, accessibility and the two modes.
