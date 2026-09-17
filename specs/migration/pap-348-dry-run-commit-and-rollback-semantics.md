---
identifier: "PAP-348"
title: "Dry run, commit and rollback semantics: transaction-rolled dry run, `import_run_item` before-state, exact rollback with conflict listing"
project: "migration"
projectName: "Migration & Import Tools"
phase: "P1"
type: "Build"
priority: 2
surfaces: ["Developer", "Staff"]
milestone: "Import framework and CSV"
state: "Backlog"
parent: "PAP-199"
children: []
blockedBy: ["PAP-347"]
blocks: ["PAP-349"]
key: "child/PAP-199/1"
url: "https://linear.app/paperos/issue/PAP-348/dry-run-commit-and-rollback-semantics-transaction-rolled-dry-run"
source: "Linear snapshot 2026-09-17T13:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T13:05:39.257Z"
model: "claude-sonnet-5"
effort: "high"
---

# PAP-348: Dry run, commit and rollback semantics: transaction-rolled dry run, `import_run_item` before-state, exact rollback with conflict listing

**Goal**

Make every import reversible and previewable: a dry run that executes the whole pipeline inside a rolled-back transaction and produces a grouped error report, a commit that records the pre-write state of every touched record, and a rollback that restores that state exactly or refuses with a conflict list.

**Scope**

In: `mode: dry` path wrapping batches in a transaction rolled back at the end while still persisting `import_run_item` rows and the report to a separate connection; `before jsonb` capture on `update`; rollback job walking items in reverse (`create` -> archive then hard delete if untouched, `update` -> restore `before`, mapping rows via PAP-201 `mappingBefore`); `--force` flag; report JSON `{ byField: [{ field, count, examples[20] }], totals }`; cancellation producing `cancelled` with partial rollback offer.

Out: UI (child 3), connectors.

**Spec**

* Dry run validates against PAP-164 validators and RLS so permission errors appear before any write.
* Rollback refuses when `updated_at > run.finished_at` on any touched record unless `--force`; conflicts listed with record ids.
* Ledger-backed tables delegate rollback to a connector hook (`onRollback`) so PAP-206 can post reversing entries.
* Report stored as a file (PAP-37) referenced by `import_run.log_file_id`; retained 90 days.

**Interface contract**

Provides: `runDry(mappingId)` returning `DryRunReport` (Zod), `rollbackRun(runId, { force })`, `cancelRun(runId)`, connector hook `onRollback?(items)`, statuses `dry|commit|rollback` on `import_run`. Consumes: child 1 engine and tables, PAP-201 mapping restore. Used by child 3, the CLI and PAP-208's `runs.dry|commit|rollback` procedures.

**Definition of done**

* Dry run of the fixture mapping leaves zero rows in target tables (asserted by row count and audit log).
* Rollback of a 10k-row commit restores a byte-identical snapshot (hash comparison committed as a test).
* Report renders in the CLI as a table and is stored as JSON.

**Test plan**

* Vitest: before-state capture for create, update and skip; rollback ordering; refusal on later edits; `--force` path; cancellation mid-batch.
* Property test (fast-check): random sequences of imports and rollbacks always return the table to its prior hash.
* Integration: dry run against a table with RLS deny shows the error grouped by table.

**Demo**

Reviewer runs `--dry` on a mapping with one deliberately wrong date column, sees 20 grouped examples, fixes the mapping, commits, edits one imported record, runs rollback and sees the single conflict listed; `--force` completes it. Under two minutes.

**Edge cases**

* Record created by import then referenced by a user-created relation: rollback archives instead of deleting and reports it.
* Crash during rollback: rollback itself is resumable by item.
* Dry run larger than 200k rows: sampled to 10k with a notice unless `--full`.

**Dependencies**

Child 1 (hard), PAP-201 (soft: mapping restore stubbed). Blocks child 3.

**Agent**

Built by Scout (Import Mapper). Reviewed by Sentinel (Edge Case Hunter, Code Reviewer).

**Size**

M
