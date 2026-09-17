---
identifier: "PAP-347"
title: "Connector interface, mapping model and import engine (`SourceConnector`, `import_mapping`, batching, resumability, fixture connector)"
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
blockedBy: ["PAP-37", "PAP-43", "PAP-164", "PAP-198"]
blocks: ["PAP-348"]
key: "child/PAP-199/0"
url: "https://linear.app/paperos/issue/PAP-347/connector-interface-mapping-model-and-import-engine-sourceconnector"
source: "Linear snapshot 2026-09-17T13:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T13:05:39.257Z"
---

# PAP-347: Connector interface, mapping model and import engine (`SourceConnector`, `import_mapping`, batching, resumability, fixture connector)

**Goal**

Create `packages/import` with the `SourceConnector` interface, the four import tables, the pg-boss engine that streams records in batches of 500 with transforms and two-pass relation resolution, and an in-memory fixture connector, so the other two PAP-199 children and every importer build on a running pipeline.

**Scope**

In: `src/connector.ts` (`discover`, `stream`, `fetchAttachment`, `capabilities`, `registerConnector`); Drizzle schema `import_source`, `import_mapping`, `import_run`, `import_run_item` with RLS by `tenant_id`; `src/engine.ts` with transforms (trim, split, parseDate, parseCurrency, mapValues, template, lookup), error policy `stop|skip|collect`, cursor persistence per collection, resume from last completed batch; `src/connectors/fixture.ts`; CLI `pnpm paperos import --connector fixture --mapping m.json --dry`.

Out: dry-run transaction and rollback (child 2), inference and wizard (child 3), real connectors.

**Spec**

* Writes go through the tables record API (PAP-164), never raw SQL, with audit reason `import:<run_id>`.
* Attachments stream to PAP-37 storage as encountered; failure creates an `error` item and a retry job.
* Relation pass runs after all collections, resolving ids via the PAP-201 helper (stubbed until it merges).
* Progress row written every batch; `import.run.progress` event published for PAP-143 (polling fallback).
* Limits enforced before start: 5M rows, 10 GB attachments, 2 concurrent runs per tenant.

**Interface contract**

Provides: `SourceConnector`, `SourceSchema`, `SourceRecord`, `MappingDefinition` (Zod), `registerConnector()`, `runImport({ mappingId, mode })`, tables above, event `import.run.progress`, CLI. Consumes: PAP-164 record API and field types, PAP-43 pg-boss, PAP-37 storage, PAP-38 audit log. Children 2 and 3 extend `import_run_item` and the engine without changing these names.

**Definition of done**

* Fixture connector run of 100k rows completes on staging under 5 minutes with progress visible (bench committed).
* Resume after a simulated crash continues from the last batch with no duplicate writes.
* `docs/migration/framework.md` explains writing a connector in under a page.

**Test plan**

* Vitest: registry, every transform, error policies, batch boundaries, cursor persistence, relation second pass including circular A-B-A, limit refusals.
* Integration (Postgres in CI): run against fixture connector, assert audit rows and RLS denial when the actor lacks table access.
* Bench script `bench/import-100k.ts` outputs JSON to `reports/`.

**Demo**

Reviewer runs `pnpm paperos import --connector fixture --mapping fixtures/mapping.json` and watches batch progress print, then opens the target table in the grid and sees 10k rows with relations resolved. Under two minutes.

**Edge cases**

* Field type changes between discover and stream: item error, not a crash.
* Two runs on one mapping: second is queued, not rejected.
* Connector without `incremental` capability: cursor ignored, full stream each time.

**Dependencies**

PAP-164 (hard), PAP-43 (hard), PAP-37, PAP-38. Blocks children 2 and 3 and every importer.

**Agent**

Built by Scout (Import Mapper) with Nova on the record API. Reviewed by Sentinel (Code Reviewer, Security Auditor) and Forge (Schema Wright).

**Size**

M
