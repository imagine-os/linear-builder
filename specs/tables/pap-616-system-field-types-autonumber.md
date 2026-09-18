---
identifier: "PAP-616"
title: "System field types: autonumber, createdTime, lastModifiedTime, createdBy, lastModifiedBy as read-only computed FieldTypes"
project: "tables"
projectName: "Table & Views Engine"
phase: "P1"
type: "Build"
priority: 2
surfaces: ["Developer"]
milestone: "Grid with sort, filter, group"
state: "Backlog"
parent: "PAP-164"
children: []
blockedBy: ["PAP-67", "PAP-161", "PAP-238", "PAP-302", "PAP-338"]
blocks: ["PAP-199", "PAP-332"]
key: "r4/tables/system-fields"
url: "https://linear.app/paperos/issue/PAP-616/system-field-types-autonumber-createdtime-lastmodifiedtime-createdby"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:17.104Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 2
dueDate: "2026-09-28"
cycle: null
---

# PAP-616: System field types: autonumber, createdTime, lastModifiedTime, createdBy, lastModifiedBy as read-only computed FieldTypes

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Build S

**Goal**

Add the five metadata field types Airtable, Baserow, NocoDB and Monday all ship and PAP-164's seventeen omit: `autonumber`, `createdTime`, `lastModifiedTime`, `createdBy`, `lastModifiedBy`. They are `computed: true`, need no storage in `record.data`, and are what importers (PAP-199) map "Created" and "Item ID" columns onto.

**Scope**

In: `packages/views/src/fields/{autonumber,createdTime,lastModifiedTime,createdBy,lastModifiedBy}.ts`; `record.seq bigint` column with a per-dataset sequence; compiler casts in PAP-335 `ops`; conversion matrix rows; Storybook stories.

Out: `button` (PAP-388), `geo` (PAP-170), rich text and duration (PAP-627), per-field "last modified" (Airtable's field-scoped variant; matrix row `wontdo` with ADR note).

**Spec**

* `autonumber`: `record.seq` assigned by `nextval('record_seq_<dataset_id>')` on insert inside `records.create`; options `{ prefix?, padding? }` format only; sortable, filterable with number ops, never editable; sequence created by `datasets.create` and dropped on purge.
* `createdTime|lastModifiedTime` map to `record.created_at|updated_at` with `date` ops and `includeTime: true`; `createdBy|lastModifiedBy` map to `record.created_by|updated_by` (add `updated_by` column, set by `records.update`) rendered with the `user` cell.
* `defineFieldType` gains `storage: 'data' | 'column'` with `column` name; PAP-335 `resolveDataset` reads columns for `column` storage instead of `record.data -> key`.
* Editors are `null`; cells reuse `number`, `dateTime`, `user` renderers (PAP-71); `validateRecord` rejects writes with `FIELD_READONLY`; `convertFieldType` allows only system → `text|number|date` snapshots (lossy: freezes values).
* Importers map source system columns to these types by name heuristics documented in `docs/views/field-types.md`.

**Interface contract**

Provides: five FieldTypes, `storage` option on `defineFieldType`, `record.seq` and `record.updated_by` migration, cast entries for PAP-335. Consumes: framework child (PAP-338), tables (PAP-161), compiler dataset resolution (PAP-335), `user` cell (PAP-71), `records.*` write path (PAP-613, soft: until it lands the audit trigger sets `updated_by`). Consumed by PAP-332 (field picker), PAP-199 (import mapping), PAP-333 (header metadata).

**Definition of done**

* Five types registered with stories screenshotted at 375, 1024, 1920 in three themes; migration with RLS unchanged; conversion matrix updated.
* Compiler test: filter and sort by each type through `views.query` against the oracle; `autonumber` gapless within a transaction test.
* `docs/views/field-types.md` section; CHANGELOG; Linear comment.

**Test plan**

* Unit: per-type parse/format; readonly rejection; prefix and padding formatting; snapshot conversion lossiness report.
* Integration: 1,000 concurrent inserts produce unique sequential numbers; `updated_by` reflects the acting agent principal; RLS harness on the new columns.
* E2E: add an Autonumber and a Created by column in `/demo/grid` from the column menu, sort by Created time, filter Last modified by to "me".

**Demo**

Reviewer inserts "Task ID" (autonumber, prefix `T-`) into the demo grid, creates two rows and sees `T-1001`, `T-1002`, then groups by Created by. Under two minutes.

**Edge cases**

* Import with existing ids: `autonumber` restarts from `max(seq)+1`, never reuses.
* Record restored from trash keeps its number.
* Deleted user in `createdBy`: "Former member" chip (PAP-339 rule).
* Duplicate record: new number, new created metadata.

**Dependencies**

PAP-338 (hard), PAP-161 (hard), PAP-335 (soft, `storage: column` cast). Blocks PAP-332, PAP-199.

**Agent**

Builder: Nova (Views Engineer). Reviewer: Sentinel (Code Reviewer).

**Size**

S: half a session.

*Round 4 critique fix (2026-09-18):* resolved 2 round-4 file keys in this description to Linear identifiers: `r4/tables/extra-field-types` = PAP-627, `r4/tables/records-crud-procedures` = PAP-613.
