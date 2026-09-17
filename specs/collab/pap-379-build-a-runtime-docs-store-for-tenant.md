---
identifier: "PAP-379"
title: "Build a runtime docs store for tenant-authored documents: Yjs-backed pages in Postgres with the same routes, search registration and comment anchors as repo MDX"
project: "collab"
projectName: "In-App Collaboration & Knowledge"
phase: "P2"
type: "Build"
priority: 3
surfaces: ["Customer", "Staff"]
milestone: "Knowledge surfaced everywhere"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-128", "PAP-142"]
blocks: []
key: "collab/runtime-docs-store"
url: "https://linear.app/paperos/issue/PAP-379/build-a-runtime-docs-store-for-tenant-authored-documents-yjs-backed"
source: "Linear snapshot 2026-09-17T13:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T13:05:14.622Z"
---

# PAP-379: Build a runtime docs store for tenant-authored documents: Yjs-backed pages in Postgres with the same routes, search registration and comment anchors as repo MDX

**Goal**

Give tenants Notion-style documents without a git commit: pages authored in the collaborative editor, stored per tenant in Postgres as Yjs state plus a rendered snapshot, served through the same docs routes, search kind and comment anchors as repo MDX. PAP-203 (Notion import) writes here.

**Scope**

In:

* Schema `doc_page(id, tenant_id, workspace_id, parent_id, slug, title, icon, audience[], status: draft|published|archived, yjs_room, snapshot_json, snapshot_text, created_by, updated_by, updated_at)` and `doc_page_version(page_id, version, snapshot_json, author_id, created_at)`; RLS by tenant; policies `doc.view|edit|publish`.
* Editing: `RichTextEditor` (PAP-142) in room `doc:<tenant>:doc_page:<id>` on PAP-140; snapshot written on room unload and every 60 s; version saved on publish.
* Routes `/_app/docs/t/$slug` (staff) and `/_public/docs/t/$slug` (published customer pages) inside PAP-128's docs shell with the same sidebar tree (tenant section) and TOC.
* Search: registered as kind `doc` with `source: tenant` (PAP-138); comment anchors `doc:<pageId>#<blockId>` (PAP-131) using Tiptap block ids.
* Import API `docs.import({ pages: [{ slug, title, richText }] })` used by PAP-203.

Out: templates gallery, page-level permissions beyond audience, publishing to external sites.

**Spec**

* Slugs unique per workspace; moves keep a redirect row.
* `snapshot_text` from `richTextToPlain` for search; render uses `renderRichText` for public pages (no editor bundle).
* Version history drawer reuses PAP-128's History UI with versions instead of commits.

**Interface contract**

Exposes: tables above, oRPC `docs.pages.list|get|create|update|publish|move|import`, `docs.versions.list|restore`, `TenantDocPage` component, sidebar tree contribution `useTenantDocsTree()`. Consumes: `RichTextEditor`, `renderRichText`, `richTextToPlain` (PAP-142), rooms (PAP-140), docs shell, sidebar and History UI (PAP-128), `registerSearchable` (PAP-39, PAP-138), `CommentAnchor` (PAP-131), `can()` (PAP-59).

**Definition of done**

* Staff creates, edits collaboratively, publishes; customer sees the published page publicly; search finds it; a comment anchors to a block.
* Screenshots at 320, 375, 768, 1024, 1280, 1536 and 1920 in light and dark; axe clean; `docs/collab/runtime-docs.md`; CHANGELOG entry; Linear comment.

**Test plan**

* Vitest: slug uniqueness and redirect on move, snapshot debounce, version creation on publish, import mapping.
* Integration (Postgres): RLS and `doc.view` matrix via `callAs`; public route returns only `published` pages with `customer` audience.
* Playwright, two contexts: co-edit a page, publish, open the public URL anonymously, search for a phrase, comment on a paragraph; restore a version.
* Visual: Gate 3 baselines for editor and public page at the seven widths.

**Demo**

Create “Onboarding checklist”, type with a colleague in another browser, publish, open the public link in a private window, search “checklist” from the palette, comment on the second paragraph. Under two minutes.

**Edge cases**

* Publish while others edit: snapshot from the current Yjs state; editing continues.
* Slug collision on import: suffix `-2` and report.
* 5 MB page: images via PAP-37, text capped at 1 MB with a notice.
* Hocuspocus down: read-only from the last snapshot.

**Dependencies**

PAP-128, PAP-142 (hard). Soft: PAP-140, PAP-138, PAP-131, PAP-59, PAP-37. Consumed by PAP-203 and the in-app help issue.

**Agent**

Built by Nova (CRDT Engineer) with Quill on content conventions. Reviewed by Sentinel (Security Auditor for public routes, Visual Inspector).

**Size**

M: schema plus glue between editor, docs shell, search and comments.
