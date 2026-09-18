---
identifier: "PAP-613"
title: "Records CRUD procedures for custom datasets: records.list|get|create|update|archive|restore with FieldDef validation, idempotency and audit reason"
project: "tables"
projectName: "Table & Views Engine"
phase: "P1"
type: "Build"
priority: 1
surfaces: ["Developer"]
milestone: "Grid with sort, filter, group"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-161", "PAP-268", "PAP-304", "PAP-338", "PAP-558"]
blocks: ["PAP-169", "PAP-332", "PAP-333", "PAP-334", "PAP-342", "PAP-620", "PAP-628", "PAP-629", "PAP-638"]
key: "r4/tables/records-crud-procedures"
url: "https://linear.app/paperos/issue/PAP-613/records-crud-procedures-for-custom-datasets"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:20:41.146Z"
model: "claude-opus-5"
effort: "high"
estimate: 3
dueDate: "2026-09-28"
cycle: null
---

# PAP-613: Records CRUD procedures for custom datasets: records.list|get|create|update|archive|restore with FieldDef validation, idempotency and audit reason

**Model / Effort:** Opus 5 (`claude-opus-5`) / high — Build M

**Goal**

Own the `records.*` router that PAP-342, PAP-333, PAP-334 and PAP-169 call but no issue builds: typed oRPC procedures over `record.data jsonb` for custom datasets, validated by the dataset's `FieldDef[]`, RLS-scoped, idempotent, audited and mirrored into Electric shapes.

**Scope**

In: `packages/views/src/records/{router,validate,serialize}.ts`; procedures `records.list|get|create|update|archive|restore|duplicate`; Zod input schemas derived at request time from `FieldDef[]` (`fieldDefsToZod(dataset)`); `record` table indexes; OpenAPI tags; `callAs` fixtures; `docs/views/records-api.md`.

Out: bulk endpoints and trash UI (PAP-334), history and undo (PAP-333), entity-dataset routers (their modules), `views.query` (PAP-337).

**Spec**

* Procedures are `tenantProcedure`s (PAP-268): `records.list({ datasetRef, filter?: FilterTree, sort?, cursor?, limit<=100 })` delegates to `compileView` with an ad-hoc `ViewSpec`; `records.get({ datasetRef, id })`; `records.create({ datasetRef, data, position? })`; `records.update({ datasetRef, id, patch, expectedVersion? })`; `records.archive|restore({ datasetRef, id })`; `records.duplicate({ datasetRef, id, includeAttachments })`.
* `validateRecord(dataset, data)` (PAP-338) runs before every write; errors are `VALIDATION` with `details: [{ path: fieldKey, issue }]`; unknown keys are stripped, `computed` fields rejected with `FIELD_READONLY`, `required` enforced on create and on patches that null a field.
* Writes set `record.version = version + 1`; `expectedVersion` mismatch returns 409 `{ code: 'CONFLICT', server: row }` so PAP-272 and PAP-144 can merge; `Idempotency-Key` honoured through PAP-304 for `create` and `duplicate`.
* Every write passes `toPredicate(actor, '<dataset>.update')` (PAP-228) and RLS; agents must send `X-PaperOS-Reason`; audit rows (PAP-38) carry `before/after/diff` per field key.
* Row cap 100 KB and 500 fields enforced server-side (PAP-161); `position` uses fractional indexing; `archive` sets `deleted_at` (PAP-32 `softDelete`) and emits `record.deleted`; `create|update` emit `record.created|updated` with changed keys only (PAP-303 envelope).
* Shape invalidation: after a write the router calls `shapes.touch(datasetRef)` so PAP-336 shapes and `useViewQuery` refetch; REST mirror via PAP-269.

**Interface contract**

Provides: `records.*` procedures, `fieldDefsToZod(dataset)`, `RecordDTO` (`{ id, version, data, createdAt, updatedAt, createdBy }`), error codes `FIELD_READONLY`, `RECORD_TOO_LARGE`, OpenAPI section, `seedRecords(datasetRef, n)` test helper. Consumes: `dataset|field|record` tables and `registerDataset` (PAP-161), `validateRecord` and casts (PAP-338), `compileView` (PAP-335), `tenantProcedure` and `callAs` (PAP-268), idempotency (PAP-304), audit (PAP-38), `toPredicate` (PAP-228), event envelope (PAP-303). Consumed by PAP-342 editing, PAP-334 bulk, PAP-333 history, PAP-169 `forms.submit`, PAP-332 schema editor, PAP-199 importers.

**Definition of done**

* All seven procedures merged with OpenAPI docs; `docs/views/records-api.md` with one curl example per procedure.
* Cross-tenant harness (PAP-34) extended with `records.get|update` as two tenants: zero leakage.
* Bench: 1,000 sequential `records.update` calls p95 under 40 ms on the compose stack; result table in the PR.
* CHANGELOG entry; Linear comment on PAP-342, PAP-334, PAP-333, PAP-169 naming the procedure signatures they now import.

**Test plan**

* Unit: `fieldDefsToZod` for every FieldType in the registry (valid and invalid sample per type); required-on-null patch; computed-field rejection; 100 KB cap; version increment and `CONFLICT` body; idempotent create returns the same id.
* Integration: `callAs(owner)` creates, updates with a stale `expectedVersion` (409), archives and restores; `callAs(viewer)` gets `FORBIDDEN` on update and `NOT_FOUND` on a foreign tenant; audit row diff matches the patch; `record.updated` event payload lists only changed keys.
* E2E: none directly (PAP-342 grid editing exercises the router end to end).

**Demo**

Reviewer runs `pnpm tsx scripts/records-demo.ts` creating a five-field dataset, inserts three records, patches one with a stale version and prints the 409 body, then archives and restores a record while tailing `audit_event`. Under two minutes.

**Edge cases**

* Patch renames a select option id that no longer exists: stored as-is, flagged `unknownOption` in the response warnings, never rejected (PAP-339 semantics).

**Dependencies**

PAP-338 (hard, `validateRecord`), PAP-161 (hard, tables), PAP-268 (hard, `tenantProcedure`), PAP-304 (hard, idempotency; interim in-memory store from PAP-35 acceptable if PAP-304 is In Review). Soft: PAP-38, PAP-228, PAP-303, PAP-336. Blocks PAP-342, PAP-334, PAP-333, PAP-169, PAP-332.

**Agent**

Builder: Nova (Views Engineer) with Forge (Schema Wright) on indexes. Reviewer: Sentinel (Security Auditor, Code Reviewer).

**Size**

M: one session.
