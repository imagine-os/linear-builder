---
identifier: "PAP-199"
title: "Build the import framework: source connector, schema-mapping UI, dry run, validation, rollback"
project: "migration"
projectName: "Migration & Import Tools"
phase: "P1"
type: "Build"
priority: 2
surfaces: ["Developer", "Staff"]
milestone: "Import framework and CSV"
state: "Backlog"
parent: null
children: ["PAP-347", "PAP-348", "PAP-349"]
blockedBy: ["PAP-37", "PAP-43", "PAP-164", "PAP-198", "PAP-332", "PAP-334", "PAP-340"]
blocks: ["PAP-200", "PAP-201", "PAP-202", "PAP-203", "PAP-204", "PAP-205", "PAP-206", "PAP-207", "PAP-208", "PAP-414", "PAP-417", "PAP-420", "PAP-423", "PAP-426"]
key: "migration/import-framework"
url: "https://linear.app/paperos/issue/PAP-199/build-the-import-framework-source-connector-schema-mapping-ui-dry-run"
source: "Linear snapshot 2026-09-17T13:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T13:05:35.594Z"
---

# PAP-199: Build the import framework: source connector, schema-mapping UI, dry run, validation, rollback

**Goal**

Build the one pipeline every importer uses: a `SourceConnector` interface, a mapping model, an engine that streams records in batches with transforms and relation resolution, a dry run that validates without writing, a commit with progress, and a rollback that reverses a run exactly. Importers then only implement connectors. This issue is the umbrella for three work packages.

**Scope**

Work packages (full specs in the project document, ready to become sub-issues when the Linear issue cap lifts):

* **WP1 Connector interface, mapping model and engine** (M): `SourceConnector` (`discover`, `stream`, `fetchAttachment`, `capabilities`), tables `import_source`, `import_mapping`, `import_run`, `import_run_item`, pg-boss engine in batches of 500, transforms, two-pass relations, resumability, in-memory fixture connector, CLI `pnpm paperos import`.
* **WP2 Dry run, commit and rollback** (M): transaction-rolled dry run with grouped report, `before` capture, exact rollback with conflict listing and `--force`, cancellation, connector `onRollback` hook for ledger-backed tables.
* **WP3 Type inference, wizard and run history** (M): `infer.ts`, wizard routes under `_app/settings/import/`, `registerWizardStep`, run history with drill-down and guarded rollback button.

Out: concrete connectors (PAP-200 to PAP-207), scheduled re-sync, two-way sync.

**Spec**

* Writes go through the PAP-164 record API so triggers, audit (`reason: import:<run_id>`) and search apply; never raw SQL.
* Mapping beats dedupe key; both consult PAP-201 once it lands.
* Limits: 5M rows and 10 GB attachments per run, 2 concurrent runs per tenant, refused before start.
* Progress via PAP-143 shapes with 2 s polling fallback.
* Build order WP1 -> WP2 -> WP3 on branches `PAP-199/wp<n>-<slug>`; each reported in a comment here.

**Interface contract**

Provides: `SourceConnector`, `SourceSchema`, `SourceRecord`, `MappingDefinition` (Zod), `registerConnector()`, `registerWizardStep()`, `runImport()`, `runDry()`, `rollbackRun()`, `inferTypes()`, tables above with RLS, event `import.run.progress`, components `MappingTable`, `RunReport`, `RunHistory`, CLI. Consumes: PAP-164 field types and record API, PAP-43 pg-boss, PAP-37 storage, PAP-38 audit, PAP-143 (soft), PAP-165 grid (soft), PAP-198 `index.json`. Consumers: every migration issue, PAP-208 `runs.*` procedures, PAP-207 applier.

**Definition of done**

* All three work packages merged and reported.
* Integration test `import-framework.e2e`: fixture connector wizard end to end with a deliberate error in dry run, commit of 10k rows, edit one record, rollback shows one conflict, `--force` completes; audit rows and mappings verified.
* 100k-row fixture run under 5 minutes on staging (bench committed); resume after crash proven.
* `docs/migration/framework.md`; CHANGELOG; Linear comment with recording and bench.

**Test plan**

* Vitest per WP (registry, transforms, inference on 15 columns, before-state, rollback ordering, cancellation).
* Property test: random import and rollback sequences return a table to its prior hash.
* Playwright: wizard, report, history; visual baselines at 320, 375, 768, 1024, 1280, 1536 and 1920 in light and dark; axe clean; keyboard-only mapping step.
* Bench script in `bench/`.

**Demo**

Reviewer opens Settings > Import, picks the fixture connector, accepts inferred types, reads the dry-run report, commits, then rolls back from Run history. Under two minutes.

**Edge cases**

* Field type changes mid-stream: item error, not a crash.
* Circular relations: two-pass resolution.
* RLS denies the actor: reported in dry run.
* Attachment fails after record created: error item plus retry job.
* User cancels: `cancelled` with partial rollback offered.

**Dependencies**

PAP-164 and PAP-43 (hard), PAP-198 (interface inputs), PAP-37, PAP-38, PAP-143 and PAP-165 (soft). Blocks PAP-200 to PAP-208 and the pending gap issues.

**Agent**

Built by Scout (Import Mapper) with Nova on the record API and Iris on the wizard. Reviewed by Sentinel (Code Reviewer, Security Auditor, Edge Case Hunter) and Atlas.

**Size**

L umbrella; three M work packages. Pending sub-issue specs: [Round 2 pending issues: migration (20)](https://linear.app/paperos/document/round-2-pending-issues-migration-20-6cb063cc1be6)
