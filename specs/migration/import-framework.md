---
identifier: "PAP-199"
title: "Build the import framework: source connector, schema-mapping UI, dry run, validation, rollback"
project: "migration"
projectName: "Migration & Import Tools"
phase: "P1"
type: "Build"
priority: 2
surfaces: ["Staff", "Developer"]
milestone: "Import framework and CSV"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-164", "PAP-198", "PAP-37", "PAP-43"]
blocks: ["PAP-200", "PAP-201", "PAP-202", "PAP-203", "PAP-204", "PAP-205", "PAP-206", "PAP-207", "PAP-208"]
key: "migration/import-framework"
url: "https://linear.app/paperos/issue/PAP-199/build-the-import-framework-source-connector-schema-mapping-ui-dry-run"
source: "plan/specs/bucket-7.json (round-1 canonical spec JSON)"
---

# PAP-199: Build the import framework: source connector, schema-mapping UI, dry run, validation, rollback

**Goal**

Build the one pipeline every importer uses: a `SourceConnector` interface that discovers a source's schema and streams records, a mapping model from source fields to PaperOS tables and field types, a schema-mapping UI with type-inference suggestions, a dry run that validates and reports without writing, a committed run that writes in batches with progress, and a rollback that reverses a run exactly. Importers then only implement connectors.

**Scope**

In:
- Package `packages/import/` with `src/connector.ts` interface: `discover(auth) -> SourceSchema { collections[]: { id, name, fields[]: { id, name, type, options, isRelation, targetCollectionId } } }`, `stream(collectionId, cursor?) -> AsyncIterable<SourceRecord>`, `fetchAttachment(ref) -> ReadableStream`, `capabilities { incremental, attachments, relations, rateLimit }`; connectors register with `registerConnector(name, factory)`.
- Schema `packages/import/src/schema.ts`: `import_source` (`connector`, `auth jsonb` encrypted, `display_name`, `status`), `import_mapping` (`source_id`, `version`, `definition jsonb`: collection -> target table (existing or new), field -> field (existing or create with type), transforms, relation strategy, dedupe key), `import_run` (`mapping_id`, `mode: dry|commit|rollback`, `status: queued|running|succeeded|failed|rolled_back|cancelled`, `stats jsonb` {read, created, updated, skipped, errors, attachments}, `started_at`, `finished_at`, `log_file_id`), `import_run_item` (`run_id`, `source_collection`, `source_id`, `target_table`, `target_id`, `action: create|update|skip|error`, `before jsonb`, `error`).
- Engine `src/engine.ts`: pg-boss job per run; batches of 500; transforms library (trim, split, parse date with format detection, currency parse, map values, template, lookup); relation resolution in a second pass using `migration/id-mapping`; attachments streamed to `data-layer/file-storage` as encountered; error policy `stop|skip|collect`; progress rows emitted every batch for live UI via `realtime/record-sync`.
- Type inference `src/infer.ts`: samples up to 1,000 values per field, scores candidate `tables/field-types` types (number, currency, date, boolean, email, phone, url, select when distinct under 5 percent, multi-select on delimiters, relation when values match another collection's keys), confidence and warnings.
- Mapping UI `apps/web/src/routes/_app/settings/import/`: wizard (connect source, pick collections, map fields with inferred suggestions and sample values, dedupe key, relation strategy, review dry run report, commit); run history grid view with per-item drill-down; rollback button with confirmation showing counts.
- CLI `pnpm paperos import --connector csv --file x.csv --mapping m.json --dry` for agents and tests; JSON mapping files validated by Zod.

Out: the concrete connectors (CSV in `migration/csv-excel`, others in their issues), scheduled re-sync (framework exposes `cursor`, scheduling is later), two-way sync.

**Spec**

- Dry run executes every step including transforms and validations against `tables/field-types` validators and RLS, writes `import_run_item` with `action` and `before` but inside a transaction that is rolled back; report groups errors by field and shows 20 examples each.
- Commit writes through the tables engine's record API (not raw SQL) so triggers, audit (`data-layer/audit-log`, `reason: import:<run_id>`) and search indexing apply.
- Rollback: for each item in reverse order `create` -> archive then hard delete if untouched since, `update` -> restore `before`; refuses if records were modified after the run unless `--force`, listing conflicts.
- Dedupe key (one or more fields) decides create vs update; matches also consult `migration/id-mapping`.
- Runs are resumable from the last completed batch after a crash; cursors persisted per collection.
- Limits: 5M rows per run, 10 GB attachments per run, 2 concurrent runs per tenant.

**Definition of done**

- Vitest: connector registry, inference on 15 fixture columns (dates in 6 formats, currencies, selects), transforms, dedupe, relation second pass, dry run leaves no rows, rollback restores exact `before` state, resumability after simulated crash.
- In-memory fixture connector used for engine tests; 100k-row run completes under 5 minutes on staging with progress visible (bench committed).
- Playwright: wizard end to end with the fixture connector, dry run report with a deliberate error, commit, rollback; screenshots at 320, 375, 768, 1024, 1280, 1536 and 1920 in light and dark for mapping step, report and history.
- axe clean; mapping table keyboard-operable.
- `docs/migration/framework.md` (writing a connector in under a page, mapping JSON reference); CHANGELOG entry; Linear comment with recording and bench.

**Edge cases**

- Source field type changes between discover and stream: record-level validation error, not a crash; report lists the field.
- Circular relations (A references B references A): two-pass resolution handles it; self-references resolved in pass two.
- Target table has RLS denying the actor: dry run reports it up front.
- Row count exceeds limit: refuse before starting with guidance to split.
- Attachment fetch fails after record created: record kept, attachment error item, retry job for attachments only.
- User cancels mid-run: `cancelled`, partial rollback offered.

**Dependencies**

`tables/field-types` (hard: validators and type list). `data-layer/file-storage`, `data-layer/audit-log`, `realtime/record-sync` (progress; fallback polling), `tables/grid-view` (history). Uses findings from `migration/format-research`. Unblocks every other migration issue.

**Agent**

Built by Scout (Import Mapper) with Nova consulted on the record API. Reviewed by Sentinel (Code Reviewer, Security Auditor for auth storage and RLS, Edge Case Hunter) and Atlas.

**Size**

L: interface, engine, inference, wizard and rollback are each substantial and must be right for seven importers.
