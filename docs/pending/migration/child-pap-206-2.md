---
key: "child/PAP-206/2"
title: "Finance import wizard: conversion date, account mapping review, duplicate customer resolution, trial balance gate and reversing rollback"
project: "migration"
parent: "PAP-206"
phase: "P2"
type: "Build"
priority: 3
size: "M"
surfaces: ["Staff"]
milestone: "Business migrations"
intendedState: "Backlog"
blockedBy: []
blocks: []
source: "round2/agent5/pending-issues.json"
linearDocument: "https://linear.app/paperos/document/round-2-pending-issues-migration-20-6cb063cc1be6"
status: "pending"
---

# Finance import wizard: conversion date, account mapping review, duplicate customer resolution, trial balance gate and reversing rollback

**Goal**

Make finance imports safe for a non-accountant: a wizard that reviews account matches, resolves duplicate customers, refuses to commit unless the trial balance is balanced per currency, and rolls back by posting reversing entries because the ledger is immutable.

**Scope**

In: wizard steps `SourcePick`, `ConversionDate`, `AccountMapping` (suggested matches by code and name), `DuplicateCustomers` (link or merge against CRM), `TrialBalance` (per currency, offending entries listed, commit disabled when unbalanced); connector hook `onRollback` implemented as `ledger.reverseRun(run_id)`; every journal tagged `source: import`, `run_id`, external ids.

Out: connectors (children 1 and 2).

**Spec**

* Trial balance computed from the dry-run journal preview, not from posted data.
* Reversing entries dated at rollback time with a memo referencing the run.
* Wizard steps registered through PAP-199 child 3.

**Interface contract**

Provides: steps above, `trialBalance(preview): { balanced, byCurrency, offenders }`, `ledger.reverseRun(runId)` (implemented against PAP-179 API), UI component `JournalPreview`. Consumes: children 1 and 2, PAP-199 children 2 and 3, PAP-179, PAP-187 duplicate lookup. `JournalPreview` is reusable by PAP-180 for manual journals.

**Definition of done**

* Wizard completes against all three sources on staging; unbalanced fixture disables commit with offenders shown.
* Rollback of a committed run posts reversing entries and the trial balance returns to its prior state.
* Screenshots at 320, 375, 768, 1024, 1280, 1536 and 1920 in light and dark for account mapping and trial balance; axe clean.

**Test plan**

* Vitest: trial balance logic, match suggestions, merge rules, reversing rollback idempotence.
* Playwright: wizard with an unbalanced fixture then a balanced one; visual baselines at seven widths, both themes.
* Integration: rollback on staging verified by PAP-183 reports.

**Demo**

Reviewer walks the wizard with the Stripe test account, sees one duplicate customer resolved, the trial balance green, commits, then clicks Rollback and sees reversing entries in the journal. Under two minutes.

**Edge cases**

* Multi-currency imbalance in one currency only: that currency's offenders listed; others green.
* User changes conversion date after mapping: opening journal recomputed, mapping kept.
* Rollback after period close: reversing entries land in the open period with a note.

**Dependencies**

Children 1 and 2 (hard), PAP-199 children 2 and 3 (hard), PAP-179, PAP-183 (verification), PAP-187.

**Agent**

Built by Scout (Import Mapper) with Ledger (Bookkeeper) and Iris. Reviewed by Sentinel (Visual Inspector, Code Reviewer) and Ledger.

**Size**

M
