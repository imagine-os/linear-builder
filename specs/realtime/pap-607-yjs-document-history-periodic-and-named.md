---
identifier: "PAP-607"
title: "Yjs document history: periodic and named snapshots, a version list with authors derived from the updates log, restore as a new update, rich-text diff rendering and retention"
project: "realtime"
projectName: "Multiplayer & Realtime"
phase: "P1"
type: "Build"
priority: 2
surfaces: ["Customer"]
milestone: "Record sync and conflict UX"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-140"]
blocks: []
key: "r4/realtime/doc-history"
url: "https://linear.app/paperos/issue/PAP-607/yjs-document-history-periodic-and-named-snapshots-a-version-list-with"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:15.599Z"
model: "claude-opus-5"
effort: "medium"
estimate: 3
dueDate: "2026-09-28"
cycle: null
---

# PAP-607: Yjs document history: periodic and named snapshots, a version list with authors derived from the updates log, restore as a new update, rich-text diff rendering and retention

**Model / Effort:** Opus 5 (`claude-opus-5`) / medium — Build M

**Goal**

Every collaborative product ships version history (Google Docs, Notion, Figma, Liveblocks) and nothing here owns it: PAP-140 keeps an append-only `yjs_updates` log and compacts it, PAP-379 promises `docs.versions.list|restore` for tenant docs, PAP-321 and PAP-132 want 'reset to generated layout'. This gives the realtime module one history primitive that every Yjs consumer reuses instead of reading raw updates.

**Scope**

In: Table `yjs_snapshot (room, id uuidv7, kind: auto|named, name?, created_by, created_at, snapshot bytea, state_vector bytea, size_bytes)`; server: auto snapshot every 500 updates or 30 minutes of edits by a new author set (piggybacks on PAP-140 compaction), `POST /rooms/:room/snapshots` for named versions; `docs/versions` procedures `history.list(room)`, `history.get(id)`, `history.restore(id)` (applies the diff as a new update by the restoring principal, never rewrites history), `history.diff(a, b)` for text fragments; authors per version from `yjs_updates.principal_id` between snapshots (column added to the updates log); client `useDocHistory(room)` and `<VersionList/>`, rich-text diff renderer (`renderRichTextDiff`) built on the editor core; retention: auto snapshots 30 days, named forever, documents in purged tenants deleted with them; `docs/platform/realtime/history.md`.

Out: Docs shell UI placement (PAP-128 History pane, PAP-379 consumes), canvas visual diff (PAP-321 uses the API only), record field history (PAP-333, audit based).

**Spec**

* Snapshots use `Y.snapshot` with `gc: false` on documents that enable history (room option `history: true`, default for `doc:` and `canvas:` rooms, off for `page:` ephemeral rooms); size cap shares PAP-140's 20 MB rule.
* `restore` computes the target state, applies `Y.encodeStateAsUpdate` from the snapshot onto the live doc as a normal transaction with origin `{ restoreOf: id, principalId }`, so undo, presence and audit all see a regular edit; an audit event `doc.restored` is written (PAP-38).
* Authors: `yjs_updates` gains `principal_id` and `origin jsonb`; the version list groups consecutive updates by author set and time gap (10 minutes); agents appear with `ActorBadge` (PAP-60).
* Diff: text-level diff of `richTextToPlain` blocks with inline word diff, rendered read-only in the editor core with insert and delete marks; canvas and other fragments return a structural summary (`nodesAdded|Removed|Changed`).
* Permissions: `history.list|get` require `document.read`, `restore` requires `document.write`; guests never restore; `permission.changed` re-evaluates (PAP-591, soft).

**Interface contract**

Provides: Table `yjs_snapshot`, procedures `history.*`, room option `history`, `useDocHistory`, `<VersionList/>`, `renderRichTextDiff`, event `doc.restored`, `principal_id` on `yjs_updates`.

Consumes: Server persistence, compaction and admin routes (PAP-140), editor core for diff rendering (PAP-603, soft), `can()` (PAP-227), audit (PAP-38), `ActorBadge` (PAP-60, soft), retention (PAP-560, soft), tenant purge (PAP-561, soft). Consumed by PAP-379, PAP-128, PAP-321, PAP-132, PAP-134, PAP-142.

**Definition of done**

* Edit a doc in two browsers, create a named version, keep editing, restore the version: both browsers show the restored text, undo reverts the restore, the version list shows both authors and the restore entry (Playwright).
* Auto snapshot after 500 updates proven in the integration suite; diff between two versions renders inserts and deletes; restore refused for `document.read` only.
* Retention job removes auto snapshots older than 30 days; docs; changelog; Linear comment with the video.

**Test plan**

* Unit: author grouping algorithm, snapshot cadence triggers, diff renderer on fixtures, permission matrix for the three procedures.
* E2E: the restore scenario above; a 19 MB document snapshot within the cap; purge deletes snapshots with the tenant.

**Demo**

Open a doc, type, save 'Draft 1', type more, open History, compare Draft 1 with now, restore it and press undo. Under two minutes.

**Edge cases**

* Document created before `history: true` was enabled: history starts at the first snapshot; the list says so.
* Restore while another user is typing: their edits merge on top; the banner (PAP-608) attributes the change.
* Snapshot storage growth: size metric per room exported for PAP-40; alert above 200 MB per tenant.

**Dependencies**

Blocked by PAP-140 (hard). Soft: PAP-603, PAP-227, PAP-38, PAP-60, PAP-560, PAP-561, PAP-591. Consumed by PAP-379, PAP-128, PAP-321, PAP-132, PAP-134.

**Agent**

Builder: Nova (CRDT Engineer). Reviewer: Sentinel (Code Reviewer; Edge Case Hunter).

**Size**

M: one session.

*Round 4 critique fix (2026-09-18):* resolved 5 round-4 file keys in this description to Linear identifiers: `r4/data-layer/retention-jobs` = PAP-560, `r4/data-layer/tenant-purge` = PAP-561, `r4/identity/permission-propagation` = PAP-591, `r4/realtime/conflict-ux-impl` = PAP-608, `r4/realtime/editor-core` = PAP-603.
