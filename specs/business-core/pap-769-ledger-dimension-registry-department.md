---
identifier: "PAP-769"
title: "Ledger dimension registry: department, location, project and class dimensions per tenant, validated on posting and exposed as report filters"
project: "business-core"
projectName: "Business Core: Payments, Finance & Payroll"
phase: "P2"
type: "Build"
priority: 3
surfaces: ["Staff"]
milestone: "Ledger and reports"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-392"]
blocks: ["PAP-183", "PAP-424", "PAP-780"]
key: "r4/business-core/ledger-dimensions-registry"
url: "https://linear.app/paperos/issue/PAP-769/ledger-dimension-registry-department-location-project-and-class"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:20:14.663Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 2
dueDate: "2026-09-29"
cycle: null
---

# PAP-769: Ledger dimension registry: department, location, project and class dimensions per tenant, validated on posting and exposed as report filters

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Build S

**Goal**

`dimensions jsonb` appears on transactions, journal lines, documents and payroll postings, PAP-183 takes a `dimensions` parameter and PAP-424 asks whether the ledger 'supports dimensions', but nothing defines which dimensions exist or validates values. A small registry closes that.

**Scope**

In: table `fin_dimension (tenant_id, key, label, kind: select|relation, options jsonb?, dataset_key?, required_on: kind[]?, is_active)`, seeded `department`, `location`, `project`, `class`; validation inside `ledger_post` (unknown key or option rejects with `VALIDATION`); `dimensions` filter and group-by in PAP-183 `defineReport` params; settings page `/finance/settings/dimensions`; posting rules may set defaults from the source (payroll department, document line dimension).

Out: row-level permissions by dimension, hierarchies beyond one parent level.

**Spec**

* Dimension values on lines are `{ key: value }` with `value` an option key or a record id of `dataset_key`; a `relation` dimension resolves labels through PAP-161 at read time.
* Deactivating a dimension keeps history; new postings may not use it; reports still group by it for past periods.
* GIN index on `fin_journal_line.dimensions` and a materialised per-period balance by `(account_id, dimension key, value)` refreshed with `fin_account_balance`.

**Interface contract**

Provides: `fin_dimension`, `validateDimensions`, `dimensions.*` procedures, report param support, settings page. Consumes: journal tables and `ledger_post` (PAP-392), reports (PAP-183), datasets (PAP-161).

**Definition of done**

* Posting with an unknown dimension rejected; P&L grouped by department matches a brute-force sum on the demo seed; settings page screenshots at 375, 1024, 1920.
* `docs/finance/dimensions.md`; CHANGELOG; comment on PAP-424 confirming dimensions exist for tracking categories.

**Test plan**

* Unit: validation matrix (unknown key, inactive option, relation id missing), balance maintenance per dimension.
* E2E: add a `location` option, post a manual entry with it, filter the P&L by that location.

**Demo**

Reviewer adds `location: Austin`, posts an entry and filters the P&L to it. Under two minutes.

**Edge cases**

* Line without a required dimension: rejected naming the dimension and the rule that requires it.
* Option renamed: label changes, key stable, history intact.

**Dependencies**

Hard: PAP-392. Soft: PAP-183, PAP-161. Blocks PAP-183 and PAP-424 (soft).

**Agent**

Builder: Ledger (Bookkeeper). Reviewer: Sentinel (Code Reviewer).

**Size**

S: half a session.
