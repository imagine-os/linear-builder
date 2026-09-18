---
identifier: "PAP-415"
title: "Airtable field mapping: every field type to PaperOS types, relations two-pass, lookups and rollups third pass, formula translation report"
project: "migration"
projectName: "Migration & Import Tools"
phase: "P2"
type: "Build"
priority: 2
surfaces: ["Staff"]
milestone: "Airtable, Notion, ClickUp importers"
state: "Backlog"
parent: "PAP-202"
children: []
blockedBy: ["PAP-201", "PAP-414"]
blocks: ["PAP-416"]
key: "child/PAP-202/1"
url: "https://linear.app/paperos/issue/PAP-415/airtable-field-mapping-every-field-type-to-paperos-types-relations-two"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:21:14.028Z"
model: "claude-sonnet-5"
effort: "high"
estimate: 3
dueDate: "2026-09-30"
cycle: null
---

# PAP-415: Airtable field mapping: every field type to PaperOS types, relations two-pass, lookups and rollups third pass, formula translation report

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / high — Build M

**Goal**

Map every Airtable field type to the PaperOS field model faithfully: select colours and order kept, linked records resolved across tables, lookups and rollups created after relations exist, and formulas translated where the engine supports them with an explicit snapshot fallback.

**Scope**

In: `mapping/airtable.ts` covering all 25 Airtable types per the PAP-198 matrix; third pass `computedFields` in the framework for lookup, rollup and formula; `mapping/airtable-formulas.ts` translating the top 40 functions to PAP-171 syntax; translation report `{ translated, snapshotted: [{ field, reason }] }`; system-field handling (`createdTime`, `lastModifiedBy` and so on).

Out: views (child 3), connector (child 1).

**Spec**

* Unsupported formula creates `<Field> (snapshot)` text field and a report line; when PAP-171 is absent all formulas snapshot.
* Select colours map to the nearest token from PAP-66; option order preserved.
* Relation fields created for both sides when the link is symmetric; one-way links produce one field.
* Every mapped field carries `source: { system: 'airtable:<baseId>', fieldId }` for PAP-201.

**Interface contract**

Provides: `mapAirtableField(field): FieldSpec | Skip`, `translateFormula(expr): { ok, expr } | { ok: false, reason }`, framework pass `computedFields` (also used by PAP-203 rollups), `TranslationReport` type. Consumes: PAP-164 field list and validators, PAP-171 formula grammar (soft), PAP-201 relation resolution, child 1 schema.

**Definition of done**

* All 25 types have a mapping and a fixture; coverage table committed in `docs/migration/airtable.md`.
* Demo base import recreates relations, 3 lookups, 2 rollups and 3 formulas with the report listing any snapshot.
* Re-import after edits updates without duplicates.

**Test plan**

* Vitest: one fixture per field type, formula translation table (40 supported, 5 unsupported), circular lookup ordering, symmetric link detection.
* Integration: demo base import then diff record counts and relation counts against the Airtable API.
* Snapshot test of the translation report.

**Demo**

Reviewer imports the demo base and opens the translation report showing 3 formulas translated and 1 snapshotted, then opens a record to see linked records and a rollup value matching Airtable. Under two minutes.

**Edge cases**

* Link to an excluded table: empty relation with a one-click "also import that table".
* Field named `id` or `created_at`: suffixed and reported.
* Cyclic rollups: cycle detected, fields snapshotted.

**Dependencies**

Child 1 (hard), PAP-164 (hard), PAP-201, PAP-171 (soft). Blocks child 3.

**Agent**

Built by Scout (Import Mapper). Reviewed by Sentinel (Edge Case Hunter, Code Reviewer) and Nova.

**Size**

M
