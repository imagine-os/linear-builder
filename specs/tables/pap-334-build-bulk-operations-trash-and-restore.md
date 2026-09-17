---
identifier: "PAP-334"
title: "Build bulk operations, trash and restore: multi-row edit and delete with server batching, soft-delete trash with 30-day restore, undo toast"
project: "tables"
projectName: "Table & Views Engine"
phase: "P1"
type: "Build"
priority: 2
surfaces: ["Customer", "Staff"]
milestone: "All view types"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-32", "PAP-165"]
blocks: ["PAP-199", "PAP-208"]
key: "gap/tables/bulk-trash"
url: "https://linear.app/paperos/issue/PAP-334/build-bulk-operations-trash-and-restore-multi-row-edit-and-delete-with"
source: "Linear snapshot 2026-09-17T13:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T13:05:03.569Z"
---

# PAP-334: Build bulk operations, trash and restore: multi-row edit and delete with server batching, soft-delete trash with 30-day restore, undo toast

**Goal**

Make `softDelete()` from PAP-32 a user-facing feature: bulk edit and delete across any view with server-side batching, a trash per dataset with 30-day restore, and an undo toast for every destructive action, so `crud.spec` expectations (PAP-86) hold everywhere.

**Scope**

In: procedures `records.bulkUpdate|bulkDelete|restore|purge`, `trash.list`; `packages/views/src/bulk/` (`BulkBar` actions, `ConfirmBulkDialog`, `UndoToast`, `TrashView`); route `/trash/$dataset`; nightly purge job. Out: field-level history (record-detail gap), import rollback (PAP-199).

**Spec**

* `records.bulkUpdate({ datasetRef, selection: { ids[] } | { filter: FilterTree }, patch })` and `bulkDelete` run in batches of 500 inside a PAP-43 job when the selection exceeds 200, returning `{ jobId }` and progress; below 200 they run inline. Selection by filter re-evaluates server-side with the actor's predicate.
* Soft delete sets `deleted_at` and `deleted_by`; views exclude deleted rows by default; `TrashView` lists them with restore and purge; `purge` after 30 days by a nightly job, sooner by `dataset.manage` holders.
* Undo toast for 10 seconds after any bulk action calls the inverse (`restore` or a reverse patch captured from the audit rows); undo of a bulk update replays previous values per row.
* Confirm dialog above 50 rows shows count, a sample of five titles and the reversibility note.
* Relations pointing at trashed records render a "In trash" chip; restoring re-links; purging nulls them (audited).
* Permissions: `<entity>.update|delete` per row; the batch skips denied rows and reports the count.

**Interface contract**

Provides: procedures above, `BulkBar` action set registered into PAP-165 (`delete`, `duplicate`, `setField`, `restore`), `<UndoToast />`, `<TrashView datasetRef />`, event `records.bulk.finished { jobId, kind, count }`. Consumes: `softDelete` and `withTenant` (PAP-32), audit rows (PAP-38), jobs (PAP-43), grid selection (PAP-165 editing child), `FilterTree` predicate (PAP-279, PAP-228), toast (PAP-237). Consumed by PAP-199 (import rollback reuses `bulkDelete`), PAP-208 templates, PAP-189 bulk actions.

**Definition of done**

* Vitest, integration and Playwright below green.
* Screenshots at 375, 1024, 1920 in three themes for bulk bar, confirm dialog, toast and trash; axe clean.
* `docs/views/bulk-trash.md`; CHANGELOG; Linear comment with demo link.

**Test plan**

* Unit: batching maths, undo inverse patch construction, denied-row accounting.
* Integration: bulk delete 5,000 rows by filter runs as a job with progress; restore returns them with relations intact; purge after 30 days via a fixed clock; cross-tenant harness on trash.
* E2E: select 60 rows, bulk set a field, undo from the toast; delete 10 rows, open trash, restore two, purge one.
* Visual: matrix above.

**Demo**

Reviewer selects all matching rows in a filtered grid, bulk-sets Status, clicks Undo in the toast, then deletes five rows and restores two of them from Trash. Under two minutes.

**Edge cases**

* Undo after the toast expired: use Trash or History (record-detail gap).
* Bulk update hitting a validation error on some rows: partial success with a per-row error list.
* Restoring a record whose dataset field was archived: value kept, field hidden.
* Purge of a record referenced by a posted ledger line (PAP-179): blocked with explanation.
* Offline bulk action: refused with "connect to run bulk actions" (no outbox for batches).

**Dependencies**

PAP-165 (hard, editing child), PAP-32 (hard), PAP-38, PAP-43, PAP-279, PAP-228. Blocks PAP-199 rollback reuse, PAP-208.

**Agent**

Builder: Nova (Views Engineer). Reviewer: Sentinel (Security Auditor for filter-based batches, Edge Case Hunter).

**Size**

M: the batching and undo semantics are the work; UI is small.
