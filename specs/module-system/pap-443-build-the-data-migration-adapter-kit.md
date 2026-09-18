---
identifier: "PAP-443"
title: "Build the data migration adapter kit: expand-contract table migrations with dual-write and backfill, event upcasters, API response adapters and Yjs document converters"
project: "module-system"
projectName: "Module System & Swap Tooling"
phase: "P1"
type: "Build"
priority: 2
surfaces: ["Developer"]
milestone: "Shell swap drill passes"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-32", "PAP-43", "PAP-436", "PAP-564", "PAP-565"]
blocks: ["PAP-540"]
key: "module-system/migration-adapter-kit"
url: "https://linear.app/paperos/issue/PAP-443/build-the-data-migration-adapter-kit-expand-contract-table-migrations"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:49:48.361Z"
model: "claude-sonnet-5"
effort: "high"
estimate: 3
dueDate: "2026-10-01"
cycle: null
---

# PAP-443: Build the data migration adapter kit: expand-contract table migrations with dual-write and backfill, event upcasters, API response adapters and Yjs document converters

**Model / Effort:** Sonnet 5 / high

**Goal**

Make data-shape changes swappable and reversible. A rewrite that changes a table, an event payload, an API response or a Yjs document schema must never strand the old implementation during the deprecation window; this kit gives one `defineMigrationAdapter()` for the four shapes, generates the expand-contract checklist the swap CLI enforces, and runs backfills as idempotent pg-boss jobs (`docs/module-system.md` section 4, last row).

**Scope**

In:

* `defineMigrationAdapter({ contract, kind: table|event|api|ydoc, from, to, upcast, downcast?, backfill? })` in `packages/kernel/migrate`, registered from the module package and listed in `ops/migrations/<module>.json`.
* Tables: expand-contract helpers on Drizzle (PAP-32): `expand` migration adds nullable columns or new tables; `dualWrite(repo, from, to)` wrapper for repository ports; `backfill` job (PAP-43) in batches of 1,000 with progress rows and resume; `verify` compares counts and samples; `contract` migration is generated only after the swap CLI's `remove` step.
* Events: thin wrapper over `defineUpcaster` (event registry issue) so all four shapes are listed in one place.
* API: `defineResponseAdapter` (gateway issue) registration with the window.
* Yjs: `ydocVersion` in the document meta map; converter run on open by the collab doc port when the stored version is older; never rewrites stored updates, writes a new snapshot.
* `paperos module migrate <id> --plan` printing the checklist and state.

Out: the migrations themselves for any module, the sync outbox (PAP-272), tenant purge (PAP-355).

**Spec**

* No destructive DDL (drop column, drop table, narrow type) is allowed while a window is open; the migration linter blocks it and the swap CLI reads the same metadata.
* Dual-write is transactional per row (same PG transaction) and records the write in `migration_dual_write_log` for verification.
* Backfills are idempotent (`(migration_id, row_id)` unique), tenant-aware (RLS bypass with `app.reason`, PAP-38) and paced (configurable rows per second).
* Yjs converters are pure functions from one update set to a new document; the old snapshot is retained until `remove`.
* Every adapter has a fixture pair (old shape, new shape) and a test that `upcast(old) == new`.

**Interface contract**

Provides: `defineMigrationAdapter`, expand-contract helpers, `dualWrite`, backfill job, `verify`, Yjs converter hook, `paperos module migrate`, migration linter rule. Consumes: PAP-32 Drizzle migration workflow and per-module migration sets (PAP-265), PAP-43 jobs, PAP-38 audit and reason, event schema registry, gateway response adapters, `CollabDocPort` (realtime contract) for the Yjs hook. Consumed by: the swap CLI (destructive migration detection, step 7 gate), any module rewrite that changes shapes, PAP-430 template upgrades, PAP-355 retention (shares the batch runner).

**Test plan**

* Unit: adapter registration, checklist generation, linter on destructive DDL fixtures.
* Integration (compose): expand a `comment` table with a new column, dual-write through the repository port, backfill 50k rows in batches with a forced restart mid-way, verify equal; contract step refused while the window is open.
* Events and API: fixture pairs upcast correctly (delegated to the registry and gateway tests, referenced here).
* Yjs: a v1 fixture document opens through the converter as v2; the v1 snapshot still loads with the old implementation.

**Definition of done**

* Kit merged with one worked example per shape in `examples/`; backfill resume recording; linter in Gate 1.
* `docs/platform/migrations.md` (expand-contract guide); Linear comment.

**Edge cases**

* Backfill slower than new writes (hot table): dual-write covers new rows; backfill only touches rows older than its start marker.
* Column rename: modelled as add plus dual-write plus backfill plus drop-after-window, never `RENAME COLUMN`.
* Yjs document larger than the 20 MB cap after conversion: converter fails the open with a clear error and the old snapshot stays; a Needs Justin card is created.
* Tenant disabled the module mid-backfill: rows for that tenant are skipped and listed in the verify report.

**Dependencies**

Blocked by PAP-32, PAP-43, module-system/event-schema-registry.

**Agent**

Built by Forge. Reviewed by Sentinel and Nova.

**Size**

M

**Demo**

Reviewer runs `paperos module migrate collab --plan` and sees the expand-contract checklist for a new comment column; runs the backfill on the seeded stack, kills the worker at 40 percent, restarts, and `verify` reports equal counts; tries to add a `DROP COLUMN` migration and the linter blocks it naming the open window. Three minutes.

*Round 4 critique fix (2026-09-18):* PAP-540 was split out as a follow-on issue (FIX-R4-1); this issue is a leaf again with its Model / Effort labels and estimate restored, and it blocks PAP-540.
