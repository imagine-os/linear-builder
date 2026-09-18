---
identifier: "PAP-342"
title: "Inline editing with optimistic commit, TSV clipboard ranges and the bulk actions bar"
project: "tables"
projectName: "Table & Views Engine"
phase: "P1"
type: "Build"
priority: 1
surfaces: ["Staff"]
milestone: "Grid with sort, filter, group"
state: "Backlog"
parent: "PAP-165"
children: []
blockedBy: ["PAP-341", "PAP-613", "PAP-641", "PAP-643"]
blocks: ["PAP-343", "PAP-629", "PAP-630"]
key: "tables/grid/editing-clipboard-bulk"
url: "https://linear.app/paperos/issue/PAP-342/inline-editing-with-optimistic-commit-tsv-clipboard-ranges-and-the"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:28:52.029Z"
model: "claude-sonnet-5"
effort: "high"
estimate: 3
dueDate: "2026-09-28"
cycle: null
---

# PAP-342: Inline editing with optimistic commit, TSV clipboard ranges and the bulk actions bar

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / high — Build M

**Goal**

Make the grid editable at Airtable speed: inline editors, optimistic writes with revert, copy and paste of ranges, and bulk actions on selections.

**Scope**

In: `views/grid/{editing,clipboard,BulkBar}.tsx`. Out: column operations and panel (sibling), trash and undo semantics (PAP-334).

**Spec**

* Edit opens on Enter, F2, double-click or a printable key; commit through `mutate(orpc.records.update, { optimistic })` (PAP-272) with revert and toast on rejection.
* Ctrl+C copies the range as TSV; Ctrl+V parses per field type and writes in chunks of 200 with progress and cancel; overflow past the last row offers "add n rows".
* Bulk bar: count, delete, duplicate, set field value; server-side actions by filter for "all matching".

*Round 4 amendment (2026-09-18):*

* Round 4: every committed edit registers with the shared undo manager (PAP-641) as one entry per cell commit (coalesced while typing into the same cell), and paste or bulk-set as one entry, so `mod+z` reverts the last edit through the inverse patch and `mod+shift+z` re-applies; the revert-on-rejection toast reuses the manager's `UndoToast`. Editors commit on `Enter` only after IME composition ends (`isComposing === false`). Clipboard operations go through the typed `ClipboardPort` (PAP-643) with the `records` payload kind; TSV remains the plain-text fallback.

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

*Round 4 critique fix (2026-09-18):* resolved 2 round-4 file keys in this description to Linear identifiers: `r4/input/clipboard-port` = PAP-643, `r4/input/undo-manager` = PAP-641.
