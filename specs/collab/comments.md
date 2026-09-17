---
identifier: "PAP-131"
title: "Implement in-app comments anchored to any entity, page element or doc block with mentions and resolve"
project: "collab"
projectName: "In-App Collaboration & Knowledge"
phase: "P1"
type: "Build"
priority: 1
surfaces: ["Customer", "Staff"]
milestone: "Comments and canvas"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-140", "PAP-142", "PAP-229", "PAP-59"]
blocks: ["PAP-136", "PAP-137", "PAP-197"]
key: "collab/comments"
url: "https://linear.app/paperos/issue/PAP-131/implement-in-app-comments-anchored-to-any-entity-page-element-or-doc"
source: "plan/specs/bucket-4.json (round-1 canonical spec JSON)"
---

# PAP-131: Implement in-app comments anchored to any entity, page element or doc block with mentions and resolve

**Goal**

Let people and agents discuss anything where it lives: comments anchored to an entity, a page element, a doc block, a canvas node or a screenshot, with mentions, resolve state and one-click escalation to a Linear issue. Threads update live for everyone viewing the same anchor.

**Scope**

In:
- Drizzle schema `packages/db/src/schema/comments.ts`: `comment_thread` (`id`, `tenant_id`, `workspace_id`, `anchor_type: entity|element|doc_block|canvas_node|screenshot`, `anchor jsonb` (`{ entityType, entityId }` | `{ route, specKey, selector?, rect? }` | `{ docPath, blockId }` | `{ canvasId, nodeId }` | `{ fileId, frame?, rect }`), `anchor_key text` generated for indexing, `status: open|resolved`, `visibility: internal|shared`, `created_by`, `resolved_by`, `resolved_at`, `linear_issue_id`, `last_activity_at`); `comment` (`id`, `thread_id`, `body_json jsonb` Tiptap document, `body_text`, `author_id`, `author_kind: human|agent`, `mentions uuid[]`, `reactions jsonb`, `edited_at`, `deleted_at`). RLS by tenant; `visibility: internal` hidden from `customer.*` audiences via `identity/rbac-abac` policies `comment.read|create|update|delete|resolve`.
- oRPC `comments.threads.list({ anchorKey | entity | route, status })`, `threads.create`, `threads.resolve|reopen`, `threads.createIssue`, `comments.create|update|delete|react`; mentions resolve `@name` for users, agent principals and characters.
- Realtime: Electric shape on both tables scoped by tenant and anchor prefix (`realtime/record-sync`); typing indicator via `realtime/presence` awareness on `thread:<id>`.
- UI in `packages/collab/comments/`: `<CommentableRoot>` provider, `data-comment-anchor` attributes (codegen emits `data-spec-key`, so element anchors use it), pin overlay positioned from `getBoundingClientRect` and re-anchored on resize and scroll, `CommentsPanel` for the inspector slot listing threads for the current page or entity, `ThreadView`, composer built on Tiptap 2 with `Mention` and `Placeholder` extensions (no Yjs for drafts), `ResolveButton`, `CreateIssueButton`.
- Escalation: `threads.createIssue` calls `pm-linear/linear-sync` (or the Linear SDK directly until it lands) to create an issue titled from the first comment, description with the deep link `<appUrl>/<route>?thread=<id>`, label `Bug` or `Improvement` chosen by the user, and stores `linear_issue_id`; status is shown on the thread.
- Events emitted on the internal bus for `collab/notifications`: `comment.created`, `comment.mentioned`, `thread.resolved`.

Out: notification delivery, screenshot viewer (`collab/screenshot-annotations`), doc editing, email replies.

**Spec**

- `anchor_key` format: `entity:<type>:<id>`, `element:<route>:<specKey>`, `doc:<path>#<blockId>`, `canvas:<canvasId>:<nodeId>`, `shot:<fileId>:<frame>`; indexed with `(tenant_id, anchor_key, status)`.
- Deep link `?thread=<id>` opens the panel and scrolls to the anchor; missing anchor shows the thread with an "element moved" note.
- Agents may comment (author_kind `agent`) with visible attribution from `identity/agent-principals`; agents may not resolve customer threads.
- Body limit 10k characters; attachments via `data-layer/file-storage` signed uploads, images inline.
- Keyboard: `c` to comment on focused element when `input/command-registry` is present; composer `Cmd+Enter` to send.

**Definition of done**

- Vitest: anchor key derivation, RLS and visibility tests through `callAs(actor)` for customer, staff and agent, mention parsing.
- Playwright: two contexts, one posts a comment on an element, the other sees it within 1 s; resolve and reopen; create Linear issue (mocked); screenshots at 320, 375, 768, 1024, 1280, 1536 and 1920 in light and dark showing pins and panel (drawer under `lg`).
- axe clean; composer usable with keyboard only.
- `docs/collab/comments.md` including how a page becomes commentable; CHANGELOG entry; Linear comment with screenshots and the created test issue link.

**Edge cases**

- Anchored element removed by a later deploy: thread remains listed under "Unanchored" for the page; pin hidden.
- Comment on a row inside a virtualised grid: anchor is `entity` (row id), not `element`, so scrolling does not lose it.
- Mention of a user without access to the anchor: mention stored but notification suppressed with a hint to the author.
- Offline: composer queues via `realtime/offline-queue`, shows pending state; conflict impossible (append-only).
- Deleted comment with replies: body replaced by "deleted", thread kept.
- Fifty pins on one page: pins cluster with a count badge above 12 per viewport.

**Dependencies**

`realtime/yjs-server` (presence transport) and `identity/rbac-abac` (hard). `realtime/record-sync` for live updates (fallback: TanStack Query polling every 5 s), `data-layer/file-storage`, `pm-linear/linear-sync`. Unblocks `collab/notifications`, `collab/screenshot-annotations`, `growth/support-inbox`, canvas node comments.

**Agent**

Built by Nova (CRDT Engineer) with Iris on the panel components. Reviewed by Sentinel (Security Auditor for visibility, Visual Inspector) and Quill.

**Size**

L: five anchor types, realtime, permissions and a Linear escalation path.
