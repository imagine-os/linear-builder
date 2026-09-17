---
identifier: "PAP-161"
title: "Specify the view model: data source, fields, filters, sorts, groups, aggregations, permissions and sharing as a superset of Airtable, Notion and ClickUp"
project: "tables"
projectName: "Table & Views Engine"
phase: "P0"
type: "Spec"
priority: 1
surfaces: ["Developer", "Staff"]
milestone: "Grid with sort, filter, group"
state: "Ready for Claude"
parent: null
children: []
blockedBy: []
blocks: ["PAP-163", "PAP-164", "PAP-207", "PAP-335", "PAP-338", "PAP-361", "PAP-426"]
key: "tables/view-model-spec"
url: "https://linear.app/paperos/issue/PAP-161/specify-the-view-model-data-source-fields-filters-sorts-groups"
source: "Linear snapshot 2026-09-17T13:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T06:43:06.610Z"
model: "claude-fable-5-1"
effort: "high"
---

# PAP-161: Specify the view model: data source, fields, filters, sorts, groups, aggregations, permissions and sharing as a superset of Airtable, Notion and ClickUp

**Goal**

Define the one schema every PaperOS view renders from: `ViewSpec`, a strict superset of what Airtable, Notion and ClickUp views can express (data source, fields, filters, sorts, groups, aggregations, permissions, sharing). The compiler (PAP-163), every view kind (PAP-165 to PAP-170), dashboards (PAP-173) and the spec builder consume this type unchanged, so it ships complete before any view code is written.

**Scope**

In: `packages/views/src/model/` (Zod schemas, TypeScript types, JSON Schema export, `migrateViewSpec`); Drizzle tables `dataset`, `field`, `record`, `view` in `packages/views/src/schema.ts`; `registerDataset()` registry so Drizzle entities appear as datasets; `docs/views/view-model.md` with one worked example per view kind and an Airtable/Notion/ClickUp equivalence column.

Out: query execution (PAP-163), field renderers (PAP-164), share tokens (PAP-172), the filter grammar itself (PAP-279 owns `FilterTree`; this issue imports it).

**Spec**

* `DatasetRef = { kind: 'entity', key } | { kind: 'custom', datasetId }`. Entities register with `registerDataset({ key, table, fields: FieldDef[], defaultSort, rls: true })`; custom datasets keep `FieldDef[]` in `field` and rows in `record.data jsonb` (max 500 fields, 100 KB per row).
* `FieldDef = { id, key, name, type: FieldType, options, required, unique, hidden, computed }`; `FieldType` is re-exported from PAP-164 (17 types plus `geo` and `button` added later).
* `ViewSpec = { id, version, datasetRef, kind (10 kinds), name, fields: { fieldId, width?, visible, order, frozen? }[], filter: FilterTree, sorts (max 5), groups (max 3, `expandMulti`), aggregations, rowHeight, options (kind-specific, each a named Zod schema), search?, visibility, ownerUserId, permissions: { canEditRecords: AudienceId[], canEditView: AudienceId[] }, locked }`.
* `filter` is `FilterTree` from `packages/core/filter` (PAP-279, soft; see Dependencies for the `unknown` fallback), including `{ ref: 'currentUser' }` and relative dates; view-specific operators are contributed through that package's extension hook, not forked.
* `view` table: `id, tenant_id, workspace_id, dataset_ref jsonb, kind, name, spec jsonb, owner_user_id, visibility, position (fractional index), created_at, updated_at, deleted_at`; index `(tenant_id, dataset_ref)`; RLS via PAP-34.
* `viewSpecSchema` is strict; `migrateViewSpec(old)` applies an ordered migration list keyed by `version`.
* `packages/views/schema/view.schema.json` exported for `page.spec.yaml` inline views (PAP-119).

**Interface contract**

Provides: `ViewSpec`, `FieldDef`, `DatasetRef`, `ViewKind`, `AggregateFn`, `viewSpecSchema`, `migrateViewSpec`, `registerDataset`, `getDataset(ref)`, tables `dataset|field|record|view`, JSON Schema file. Consumes: `FilterTree` and `AudienceId` (PAP-279, PAP-62), `tenant|workspace|user` FKs (PAP-33), RLS helpers (PAP-34). Events: none. API: none (CRUD arrives with PAP-172).

* Contract source: [Interface & Data Contracts](<https://linear.app/paperos/document/paperos-interface-and-data-contracts-d40e6a4d227c>) §1 (`spec.filter` is a `FilterTree` from `@paperos/core/filter`, PAP-279; `FilterGroup` is an alias, not a copy); §2 rows "View" (`ViewSpec` strict Zod, `dataset_ref jsonb` as `entity:key` or `custom:id`, ten view kinds, `visibility personal|shared|public`) and "Record" (`record.data jsonb` validated by `FieldDef[]`, code datasets via `registerDataset()`); `EntityRef.type` used by comments, notifications, search and audit is the dataset key from this registry; §6 row "View model".

**Definition of done**

* Zod schemas, types and JSON Schema committed; `pnpm --filter views test` green.
* Migration for the four tables with RLS policies; cross-tenant harness green.
* `docs/views/view-model.md` documents every property with the equivalence column and one fixture per kind under `packages/views/fixtures/`.
* `memberships` entity exposed as a dataset in a test.
* ADR `docs/adr/00xx-view-model.md`, CHANGELOG entry, Linear comment linking the docs page.

**Test plan**

* Unit: parse and strict-mode rejection for each kind fixture; `migrateViewSpec` v1 to v2 fixture; nested filter depth 6 rejected; 501 fields rejected; duplicate slugs rejected.
* Integration (PGlite): migration applies and rolls back; RLS harness `expectTenantIsolation('view')`; registry test reads `memberships` rows through `getDataset`.
* Contract: JSON Schema validates all fixtures with `ajv`; snapshot of the schema file guards accidental breaking changes.
* Visual: none (no UI). Docs build renders the Mermaid ER diagram.

**Demo**

Reviewer runs `pnpm --filter views test` (green in under 30 s), opens `docs/views/view-model.md` on Pages, then runs `pnpm tsx packages/views/scripts/print-spec.ts fixtures/kanban.view.json` which prints the parsed spec and its JSON Schema validation result. Under two minutes.

**Edge cases**

* Filter references a deleted field: spec stays valid, condition flagged `orphaned` and skipped at compile.
* Group on multi-select: default combination semantics, `expandMulti` for one row per value.
* RLS entity dataset: `permissions` only narrows, never widens.
* Two views with the same name: allowed, slugs unique.
* Spec written by an older client: `version` lower than current triggers migration on read, never on write.
* PAP-279 not yet In Review: `filter` is `unknown`, every fixture still parses, and the strict-mode test for the filter shape is `test.todo` naming PAP-279 so the gap is visible in the report.

**Dependencies**

Ready now; no inbound `blocks` relation is open (FIX-2, 2026-09-17). PAP-279 soft: import the draft `FilterTree` from the PAP-279 PR branch (`feat/PAP-279`, `@paperos/core/filter`); if PAP-279 is not In Review when you start, define `filter` as `unknown` (`filter: z.unknown()` in `viewSpecSchema`, exported type `FilterTree = unknown`) and leave a `// TODO(PAP-279): replace with FilterTree from @paperos/core/filter` at the definition; swapping the alias when PAP-279 merges is the only follow-up. The relation `PAP-279 blocks PAP-161` was removed for this reason; do not re-add it. PAP-33 and PAP-34 soft: they gate only work package 2 (Drizzle tables `dataset|field|record|view` and RLS policies). Build the Zod model, types, JSON Schema, `migrateViewSpec`, `registerDataset` and docs first; write the migration against the PAP-33 PR branch if it is In Review, otherwise land the tables as a second commit on this branch after PAP-33 merges and note it in the PR. PAP-162 in parallel for the equivalence column. Blocks PAP-163, PAP-164, PAP-207.

**Agent**

Builder: Quill (Page Spec Writer) with Nova (Views Engineer) pairing on the Zod model. Reviewer: Sentinel (spec-conformance) and Forge (Schema Wright) on the migration.

**Size**

M: modelling and documentation, exhaustive because every downstream issue depends on it.
