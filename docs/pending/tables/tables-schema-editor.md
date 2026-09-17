---
key: "gap/tables/schema-editor"
title: "Build the custom dataset schema editor: create tables and fields in-app, reorder, field type conversion with a lossiness report and background backfill"
project: "tables"
parent: null
phase: "P1"
type: "Build"
priority: 1
size: null
surfaces: []
milestone: "All view types"
intendedState: "Backlog"
blockedBy: ["PAP-164", "PAP-165"]
blocks: ["PAP-199", "PAP-208"]
source: "round2/agent4/pending-issues.json"
linearDocument: "https://linear.app/paperos/document/round-2-pending-issues-tables-24-86486d9b99cc"
status: "pending"
---

# Build the custom dataset schema editor: create tables and fields in-app, reorder, field type conversion with a lossiness report and background backfill

**Goal**

Give users the Airtable "add a table, add a field, change its type" experience on top of PAP-161 custom datasets and PAP-164 types, so business templates and importers can create schema in-app and staff can evolve it safely with a lossiness report and background backfill.

**Scope**

In: `packages/views/src/schema-editor/` (`DatasetList`, `NewDatasetDialog`, `FieldList`, `FieldEditor`, `ConvertTypeDialog`); procedures `datasets.create|rename|archive`, `fields.create|update|reorder|convert|archive`; conversion job progress UI; integration with the grid column menu "edit field" and "insert field". Out: entity dataset schema (code-defined), formula editing (PAP-171), record data editing.

**Spec**

* `datasets.create({ name, icon, titleField, fields[] })` creates the `dataset` row plus `field` rows and registers the dataset; names unique per workspace; slug derived.
* `fields.create` validates `FieldDef` with the type's `optionsSchema`; `fields.reorder` uses fractional indexes; `fields.archive` soft-deletes and keeps data for 30 days with restore.
* `fields.convert({ fieldId, newType, options })` runs `convertFieldType` preview (PAP-164 relational child), shows `sampleLosses` (up to 20 rows) and requires confirmation when `lossy`; conversion runs as a PAP-43 job in batches of 1,000 with progress and cancel; views referencing the field get filters re-validated and `orphaned` conditions flagged.
* Dependency check: converting or archiving a field referenced by lookups, rollups or formulas (PAP-171 graph) warns with the dependant list and blocks when it would break a formula.
* Permissions `dataset.manage`; agents may propose schema through drafts, not apply.
* Limits: 500 fields per dataset, 200 datasets per workspace unless entitlement raises it (PAP-178).

**Interface contract**

Provides: procedures above, `<SchemaEditor datasetId />`, `<FieldEditor field onSave />` reused by the grid column menu (PAP-165) and the import mapping wizard (PAP-199), event `dataset.schema.changed { datasetId, change }`. Consumes: `dataset|field` tables (PAP-161), `defineFieldType` options editors and `convertFieldType` (PAP-164), jobs (PAP-43), dependency graph (PAP-171, soft), entitlements (PAP-178, soft). Consumed by PAP-199, PAP-208 business templates, PAP-202 importers.

**Definition of done**

* Vitest, integration and Playwright below green.
* Storybook stories; screenshots at 375, 768, 1024, 1440, 1920 in three themes; axe clean; keyboard-only field creation.
* `docs/views/schema-editor.md`; CHANGELOG; Linear comment with demo link.

**Test plan**

* Unit: name uniqueness, options validation per type, reorder indexes, dependency warnings.
* Integration: convert 10k-row number field to text with progress; cancel mid-way leaves data intact; archived field restored with data; views with orphaned filters flagged.
* E2E: create a dataset with five fields, insert a field from the grid header, convert a type and read the lossiness report, archive and restore a field.
* Visual: matrix above.

**Demo**

Reviewer clicks "New table", adds four fields of different types, opens the grid, inserts a field from the column menu, then converts a text column to single select and reads the report before confirming. Under two minutes.

**Edge cases**

* Two staff editing schema concurrently: optimistic version check returns `CONFLICT` with a refresh prompt.
* Converting with a running import: blocked until the import finishes.
* Field used as `titleField` archived: blocked, pick another first.
* 100 KB row limit exceeded by a conversion: rows listed in the report, conversion refused.
* Entity dataset opened in the editor: read-only with a link to the code definition.

**Dependencies**

PAP-164 (hard), PAP-165 (hard, column menu), PAP-161, PAP-43, PAP-171 and PAP-178 (soft). Blocks PAP-199, PAP-208.

**Agent**

Builder: Nova (Views Engineer) with Iris on dialogs. Reviewer: Sentinel (Code Reviewer, Edge Case Hunter).

**Size**

M: procedures are thin over PAP-164; the conversion UX and dependency checks carry the work.
