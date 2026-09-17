---
identifier: "PAP-161"
title: "Specify the view model: data source, fields, filters, sorts, groups, aggregations, permissions and sharing as a superset of Airtable, Notion and ClickUp"
project: "tables"
projectName: "Table & Views Engine"
phase: "P0"
type: "Spec"
priority: 1
surfaces: ["Staff", "Developer"]
milestone: "Grid with sort, filter, group"
state: "Ready for Claude"
parent: null
children: []
blockedBy: []
blocks: ["PAP-163", "PAP-164", "PAP-207"]
key: "tables/view-model-spec"
url: "https://linear.app/paperos/issue/PAP-161/specify-the-view-model-data-source-fields-filters-sorts-groups"
source: "plan/specs/bucket-6.json (round-1 canonical spec JSON)"
---

# PAP-161: Specify the view model: data source, fields, filters, sorts, groups, aggregations, permissions and sharing as a superset of Airtable, Notion and ClickUp

**Goal**

Define the one schema every PaperOS view renders from: a `ViewSpec` that describes data source, fields, filters, sorts, groups, aggregations, permissions and sharing as a strict superset of what Airtable, Notion and ClickUp views can express. Every later issue in this project (compiler, grid, kanban, dashboards) consumes this type unchanged, so it must be complete before any view code is written.

**Scope**

In:
- `packages/views/src/model/` in `imagine-os/paperos-template`: Zod schemas, TypeScript types, JSON Schema export, migration helpers.
- Drizzle tables `dataset`, `field`, `record` (custom datasets) and `view` in `packages/views/src/schema.ts`.
- Spec doc `docs/views/view-model.md` with one worked example per view kind.
- Code-defined dataset registry so Drizzle entities (contacts, issues, invoices) appear as datasets.

Out: query execution (`tables/query-compiler`), field renderers (`tables/field-types`), sharing tokens (`tables/view-sharing`).

**Spec**

- `DatasetRef = { kind: 'entity', key: string } | { kind: 'custom', datasetId: string }`. Code datasets register via `registerDataset({ key, table, fields: FieldDef[], defaultSort, rls: true })` in `packages/views/src/registry.ts`; custom datasets store `FieldDef[]` in the `field` table and rows as `record.data jsonb`.
- `FieldDef = { id, key, name, type: FieldType, options: Record<string, unknown>, required, unique, hidden, computed }`; `FieldType` is the union listed in `tables/field-types`.
- `ViewSpec = { id, datasetRef, kind: 'grid'|'kanban'|'calendar'|'timeline'|'gantt'|'gallery'|'list'|'form'|'map'|'chart', name, fields: { fieldId, width?, visible, order, frozen? }[], filter: FilterGroup, sorts: { fieldId, dir, nullsLast }[], groups: { fieldId, dir, collapsed?: string[] }[] (max 3), aggregations: { fieldId, fn: 'count'|'sum'|'avg'|'min'|'max'|'median'|'unique'|'empty'|'filled'|'percentEmpty' }[], rowHeight: 'short'|'medium'|'tall'|'extraTall', options: kind-specific (e.g. kanban `{ groupField, swimlaneField?, wipLimits }`, calendar `{ startField, endField? }`), search?: string, visibility: 'personal'|'shared'|'public', ownerUserId, permissions: { canEditRecords: AudienceId[], canEditView: AudienceId[] }, locked: boolean }`.
- `FilterGroup = { op: 'and'|'or', children: (FilterCondition | FilterGroup)[] }`, `FilterCondition = { fieldId, op: FilterOp, value?, relative?: { unit, amount, anchor } }`; `FilterOp` per field type (`is, isNot, contains, doesNotContain, isEmpty, isNotEmpty, gt, gte, lt, lte, isWithin, isBefore, isAfter, isAnyOf, isNoneOf, hasAll, hasAny`). Dynamic values `{ ref: 'currentUser' }` and `{ ref: 'today' }` supported.
- `view` table: `id, tenant_id, workspace_id, dataset_ref jsonb, kind, name, spec jsonb, owner_user_id, visibility, position (fractional index), created_at, updated_at, deleted_at`; index `(tenant_id, dataset_ref)`.
- `viewSpecSchema.parse` is strict (no unknown keys); `migrateViewSpec(old)` bumps `version` with a migration list.
- Export `packages/views/schema/view.schema.json` for the spec builder so `page.spec.yaml` can embed a view inline (`spec-builder/data-section`).

**Definition of done**

- Zod schemas, types and JSON Schema committed; `pnpm --filter views test` covers parse, strict-mode rejection, migration and one fixture per kind.
- Drizzle migration for `dataset`, `field`, `record`, `view` with RLS policies via `data-layer/rls-tenancy` and cross-tenant harness green.
- `docs/views/view-model.md` documents every property with an Airtable/Notion/ClickUp equivalence column.
- Fixture `packages/views/fixtures/*.view.json` for the 10 kinds validates in CI.
- Registry proves a Drizzle entity (`memberships`) exposes as a dataset in a test.
- ADR `docs/adr/00xx-view-model.md`; CHANGELOG entry; Linear comment linking the doc on GitHub Pages.

**Edge cases**

- Filter references a deleted field: spec stays valid, condition flagged `orphaned` and skipped at compile.
- Group on a multi-select: define "one row per value" vs "combination" semantics (default: combination, option `expandMulti`).
- Custom dataset with 500 fields: `record.data` stays jsonb but enforce max 500 fields and 100 KB per row.
- Views on entities with RLS: spec never grants more than RLS allows; `permissions` only narrows.
- Nested filter depth beyond 5 rejected with a clear error.
- Two views with the same name in a dataset: allowed, but slugs are unique.

**Dependencies**

- `data-layer/core-entities` for tenant/workspace/user FKs; `data-layer/drizzle-schema` for migration workflow; `tables/feature-parity-audit` runs in parallel and feeds the equivalence column.

**Agent**

Builder: Quill (Page Spec Writer) with Nova (Views Engineer) pairing on the Zod model. Reviewer: Sentinel (Code Reviewer, spec-conformance) plus Forge (Schema Wright) on the migration.

**Size**

M: mostly modelling and documentation, but it must be exhaustive because every downstream issue depends on it.
