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
children: ["PAP-317", "PAP-318", "PAP-319"]
blockedBy: ["PAP-59", "PAP-140", "PAP-142", "PAP-229", "PAP-302"]
blocks: ["PAP-136", "PAP-137", "PAP-197", "PAP-323", "PAP-411"]
key: "collab/comments"
url: "https://linear.app/paperos/issue/PAP-131/implement-in-app-comments-anchored-to-any-entity-page-element-or-doc"
source: "Linear snapshot 2026-09-17T13:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T13:04:58.278Z"
model: null
effort: null
---

# PAP-131: Implement in-app comments anchored to any entity, page element or doc block with mentions and resolve

**Goal**

Umbrella: let people and agents discuss anything where it lives. Comments anchor to an entity, page element, doc block, canvas node or screenshot, support mentions and resolve state, update live for everyone on the same anchor, and escalate to a Linear issue in one click. Work is planned as three work packages; this issue owns the integration test and the docs.

**Scope**

Work packages (build in order; each becomes a child issue once the Linear issue limit is lifted, see the pinned comment):

1. **Comment schema, anchors, RLS and oRPC procedures** — `comment_thread` and `comment` tables, five anchor kinds and `anchor_key` grammar, visibility policies, `comments.*` procedures, event emission.
2. **Comment panel, pins and composer UI** — `CommentableRoot`, pin overlay with clustering, `CommentsPanel`, `ThreadView`, composer on `RichTextEditor` (PAP-142) in local mode with mentions.
3. **Live updates, deep links and Linear escalation** — Electric shape subscription with polling fallback, `?thread=` deep links, `threads.createIssue` through PAP-101 or the Linear SDK.

Parent owns: `docs/collab/comments.md`, the two-context Playwright integration test, Gate 3 baselines, and the `c` keyboard command registration (PAP-151).

Out: notification delivery (PAP-136), screenshot viewer (PAP-137), email replies.

**Spec**

* `anchor_key`: `entity:<type>:<id>`, `element:<route>:<specKey>`, `doc:<path>#<blockId>`, `canvas:<canvasId>:<nodeId>`, `shot:<fileId>:<frame>`; index `(tenant_id, anchor_key, status)`.
* `visibility: internal` hidden from `customer.*` audiences via PAP-59 policies `comment.read|create|update|delete|resolve`; agents may comment, never resolve customer threads.
* Body limit 10k characters; attachments through PAP-37 signed uploads.
* Live: shape on both tables scoped by tenant and anchor prefix (PAP-143) or TanStack Query polling every 5 s.

**Interface contract**

Exposes (owned by the work packages, listed here as the umbrella contract): tables `comment_thread`, `comment`; types `CommentAnchor` (discriminated union) and `anchorKey(anchor)` in `packages/collab/comments/anchors.ts`; oRPC `comments.threads.list|create|resolve|reopen|createIssue`, `comments.create|update|delete|react`; React `CommentableRoot`, `useThreads(anchor)`, `CommentsPanel`, `CommentPin`; DOM contract `data-comment-anchor` (codegen's `data-spec-key` doubles as element anchor); events `comment.created`, `comment.mentioned`, `thread.resolved` on `packages/core/events` (payload `{ threadId, commentId, anchor, actorId, mentions[] }`) consumed by PAP-136; deep link `?thread=<id>`. Consumes: `RichTextEditor` local mode (PAP-142), `can()` (PAP-59), awareness room `thread:<id>` (PAP-140, PAP-141), shape proxy (PAP-143), file uploads (PAP-37), issue creation (PAP-101).

**Definition of done**

* All three work packages merged; integration test below green in CI.
* Screenshots at 320, 375, 768, 1024, 1280, 1536 and 1920 in light and dark showing pins and panel (drawer under `lg`).
* axe clean; composer usable keyboard-only; `docs/collab/comments.md` including how a page becomes commentable; CHANGELOG entry; Linear comment with screenshots and the created test issue link.

**Test plan**

* Integration (parent): Playwright with two contexts: staff A pins an element on the sample page and posts a mention of B; B sees the pin and thread within 1 s, replies, resolves; A reopens; A creates a Linear issue (mocked PAP-101) and the thread shows the issue key; a customer context cannot see the `internal` thread. Runs at 375 and 1280.
* Unit and component tests per work package (anchor derivation, `callAs` visibility matrix, mention parsing, pin clustering, composer keyboard).
* Visual: Gate 3 baselines for pins, panel and drawer at the seven widths, both themes.
* Contract: event payload snapshot validated against `packages/contracts/events.ts`.

**Demo**

Open the sample records page, press `c`, click a field, type “@Bo looks wrong”, send. In a second browser as Bo, watch the pin appear, reply, resolve. Back as A, click “Create issue” and open the Linear link. Under two minutes.

**Edge cases**

* Anchored element removed by a deploy: thread listed under "Unanchored", pin hidden.
* Row in a virtualised grid: anchor is `entity`, not `element`.
* Mention of a user without access: stored, notification suppressed, hint shown.
* Offline: composer queues via PAP-148; append-only so no conflict.
* Fifty pins on one page: cluster with a count above 12 per viewport.

**Dependencies**

PAP-140, PAP-59, PAP-142 (hard). Soft: PAP-143, PAP-37, PAP-101, PAP-141, PAP-151. Blocks PAP-136, PAP-137, PAP-197.

**Agent**

Built by Nova (CRDT Engineer) with Iris on the panel components. Reviewed by Sentinel (Security Auditor for visibility, Visual Inspector) and Quill.

**Size**

L, planned as three M/S work packages (child issues pending the issue limit).
