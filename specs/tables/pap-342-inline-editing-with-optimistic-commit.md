---
identifier: "PAP-342"
title: "Inline editing with optimistic commit, TSV clipboard ranges and the bulk actions bar"
project: "tables"
projectName: "Table & Views Engine"
phase: "P1"
type: "Build"
priority: 1
surfaces: ["Customer", "Staff"]
milestone: "Grid with sort, filter, group"
state: "Backlog"
parent: "PAP-165"
children: []
blockedBy: ["PAP-341"]
blocks: ["PAP-343"]
key: "tables/grid/editing-clipboard-bulk"
url: "https://linear.app/paperos/issue/PAP-342/inline-editing-with-optimistic-commit-tsv-clipboard-ranges-and-the"
source: "Linear snapshot 2026-09-17T13:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T13:05:35.594Z"
model: "claude-sonnet-5"
effort: "high"
---

# PAP-342: Inline editing with optimistic commit, TSV clipboard ranges and the bulk actions bar

**Goal**

Make the grid editable at Airtable speed: inline editors, optimistic writes with revert, copy and paste of ranges, and bulk actions on selections.

**Scope**

In: `views/grid/{editing,clipboard,BulkBar}.tsx`. Out: column operations and panel (sibling), trash and undo semantics (PAP-334).

**Spec**

* Edit opens on Enter, F2, double-click or a printable key; commit through `mutate(orpc.records.update, { optimistic })` (PAP-272) with revert and toast on rejection.
* Ctrl+C copies the range as TSV; Ctrl+V parses per field type and writes in chunks of 200 with progress and cancel; overflow past the last row offers "add n rows".
* Bulk bar: count, delete, duplicate, set field value; server-side actions by filter for "all matching".

**Interface contract**

Provides: `useCellEditing`, `useClipboardRange`, `<BulkBar actions />` extension point used by PAP-334 and PAP-189. Consumes: core child, editors and `parse` (PAP-164), `mutate` (PAP-272), `records.*` procedures.

**Definition of done**

* Editing, clipboard and bulk flows in Playwright; unit tests for TSV parsing; screenshots of edit and bulk states at 375, 1024, 1920.

**Test plan**

* Unit: TSV parser with quotes and newlines; chunking; revert on rejection.
* E2E: edit, reload, persisted; paste 500 rows; bulk set value on 50 rows; rejected write reverts with toast.

**Demo**

Paste three rows from a spreadsheet into `/demo/grid`, then bulk-set a status on the selection.

**Edge cases**

* Row deleted mid-edit closes the editor (PAP-144); 5,000-row paste is chunked and cancellable.

**Dependencies**

Core child (hard), PAP-164, PAP-272 (soft).

**Agent**

Builder: Nova. Reviewer: Sentinel (Edge Case Hunter).

**Size**

M: one session.
