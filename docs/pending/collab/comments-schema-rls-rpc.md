---
key: "collab/comments/schema-rls-rpc"
title: "Comment schema, anchors, RLS and oRPC procedures"
project: "collab"
parent: "PAP-131"
phase: "P1"
type: "Build"
priority: 1
size: null
surfaces: ["Customer", "Staff"]
milestone: "Comments and canvas"
intendedState: "Backlog"
blockedBy: []
blocks: []
source: "round2/agent3/pending-issues.json"
linearDocument: null
identifier: "PAP-317"
status: "created"
createdAt: "2026-09-17"
---

# Comment schema, anchors, RLS and oRPC procedures

**Goal**

Ship the data and API half of comments (PAP-131): two tables, five anchor kinds with a stable key grammar, tenant RLS plus visibility policies, and the `comments.*` procedures every UI and agent uses.

**Scope**

In:

* Drizzle schema `packages/db/src/schema/comments.ts`: `comment_thread` (`id`, `tenant_id`, `workspace_id`, `anchor_type`, `anchor jsonb`, `anchor_key` generated, `status: open|resolved`, `visibility: internal|shared`, `created_by`, `resolved_by`, `resolved_at`, `linear_issue_id`, `last_activity_at`), `comment` (`id`, `thread_id`, `body_json`, `body_text`, `author_id`, `author_kind: human|agent`, `mentions uuid[]`, `reactions jsonb`, `edited_at`, `deleted_at`); indexes `(tenant_id, anchor_key, status)`.
* `anchorKey(anchor)` and Zod `CommentAnchor` union in `packages/collab/comments/anchors.ts`.
* RLS by tenant (PAP-228 helpers) and policies `comment.read|create|update|delete|resolve` in PAP-59's policy format; `internal` hidden from `customer.*`.
* oRPC `comments.threads.list|create|resolve|reopen`, `comments.create|update|delete|react`; mention resolution for users, agents and characters; events `comment.created`, `comment.mentioned`, `thread.resolved` emitted on `packages/core/events`.

Out: UI, live updates, Linear escalation (siblings).

**Spec**

* Key grammar: `entity:<type>:<id>`, `element:<route>:<specKey>`, `doc:<path>#<blockId>`, `canvas:<canvasId>:<nodeId>`, `shot:<fileId>:<frame>`.
* Body limit 10k characters; `body_text` derived with `richTextToPlain` (PAP-142) for search.
* Agents may create, never resolve customer threads; deleted comments keep the row with `deleted_at`.

**Interface contract**

Exposes tables, `CommentAnchor`, `anchorKey()`, the procedures above with `Thread` and `Comment` types in the API contract package (PAP-268), and the three event payloads `{ threadId, commentId, anchor, actorId, mentions[] }`. Consumes migrations and RLS helpers (PAP-32, PAP-228), `can()` (PAP-227), oRPC router registration and `callAs` (PAP-267, PAP-268), `richTextSchema` and `richTextToPlain` (PAP-142).

**Definition of done**

* Migration applied on staging; policies registered; procedures documented in the OpenAPI output (PAP-269).
* Event payloads validated against `packages/contracts/events.ts`.
* Linear comment with the `callAs` matrix results.

**Test plan**

* Vitest: `anchorKey` for all five kinds, invalid anchors rejected, mention parsing of `@name` and `#entity`.
* Integration (Postgres): `callAs` matrix for customer, staff, agent across read, create, resolve on `internal` and `shared` threads; RLS blocks cross-tenant reads with a forged `anchor_key`; body over 10k rejected; events emitted once per mutation.

**Demo**

Run `pnpm api:play` and call `comments.threads.create` with an entity anchor, then `comments.create` with a mention; call `threads.list` as a customer and see the internal thread missing. Under two minutes.

**Edge cases**

* Anchor for a deleted entity: thread stays; `list` marks `orphaned: true`.
* Mention of a user without access: stored; `comment.mentioned` carries `suppressed: true`.
* Duplicate reaction: idempotent.

**Dependencies**

PAP-59 and PAP-142 (hard). PAP-32, PAP-35 children (soft). Blocks the UI and live-update children.

**Agent**

Built by Forge (Schema Wright) with Nova. Reviewed by Sentinel (Security Auditor).

**Size**

M: two tables, policies and eight procedures with a full permission matrix.
