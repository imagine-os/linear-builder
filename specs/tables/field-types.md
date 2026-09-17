---
identifier: "PAP-164"
title: "Implement field types: text, number, currency, date, select, multi-select, relation, lookup, rollup, formula, attachment, user, checkbox, rating, URL, email, phone"
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
blockedBy: ["PAP-161", "PAP-233", "PAP-238", "PAP-67", "PAP-71"]
blocks: ["PAP-165", "PAP-171", "PAP-199"]
key: "tables/field-types"
url: "https://linear.app/paperos/issue/PAP-164/implement-field-types-text-number-currency-date-select-multi-select"
source: "plan/specs/bucket-6.json (round-1 canonical spec JSON)"
---

# PAP-164: Implement field types: text, number, currency, date, select, multi-select, relation, lookup, rollup, formula, attachment, user, checkbox, rating, URL, email, phone

**Goal**

Implement the field type system: for each of the 17 field types, a definition that owns validation, parsing, formatting, default cell renderer and editor, allowed filter operators, sort and group behaviour, aggregations and storage casting. Views, forms, imports and the spec builder all look up field behaviour here instead of special-casing types.

**Scope**

In:
- `packages/views/src/fields/` with `defineFieldType`, a registry, and one file per type: text, longText (alias of text with `multiline`), number, currency, percent (number option), date, select, multiSelect, relation, lookup, rollup, formula (storage and type only; evaluation in `tables/formula-engine`), attachment, user, checkbox, rating, url, email, phone.
- Cell renderers registered into the `design-system/data-display` cell registry and cell editors for inline editing.
- Field options editors (`FieldSettingsPanel`) used by grid column menus and the custom-dataset schema editor.

Out: formula parsing/evaluation; import type inference (`migration/csv-excel`); geo field (added in `tables/map-chart-views`).

**Spec**

- `defineFieldType<TOptions, TValue>({ type, label, icon, optionsSchema: ZodSchema, valueSchema: ZodSchema, defaultOptions, parse(input, options, locale): TValue | ParseError, format(value, options, locale): string, sql: { cast, jsonExtract }, filterOps: FilterOp[], sortable, groupable, aggregations: AggregateFn[], Cell, Editor, OptionsEditor, exampleValues })`.
- Storage: values in `record.data[fieldKey]` as JSON; `date` is ISO 8601 string with `options.includeTime` and `options.timezone: 'utc'|'local'`; `currency` is `{ amountMinor: number, currency: 'USD' }` (never floats, matching `Money` in data-display); `relation` is `string[]` of record ids with `options.datasetRef, options.limitOne, options.symmetricFieldId`; `attachment` is `string[]` of `file.id` from `data-layer/file-storage`; `user` is `string[]` of `user.id`; `select` stores option id, options carry `{ id, name, color (token name) }`; `rating` is integer 0..options.max (max 10).
- `lookup` options `{ relationFieldId, targetFieldId }`; `rollup` options `{ relationFieldId, targetFieldId, fn }`; both are `computed: true`, read-only, compile via lateral joins in `tables/query-compiler`.
- Validation runs server-side in `records.create/update` via the shared `validateRecord(dataset, data)` and client-side in editors; errors return `VALIDATION` with `{ fieldKey, message }[]`.
- Editors: `Editor` props `{ value, onChange, onCommit, onCancel, autoFocus, field }`; commit on Enter or blur, cancel on Escape; relation and user editors use a searchable Combobox from `design-system/primitives`; attachment editor uses the upload flow from file-storage; date editor uses the DatePicker with keyboard entry.
- Phone via `libphonenumber-js` 1.x (formatting only, default country from tenant settings); URL normalised with `new URL()`; email lowercase and RFC 5322 check via Zod.
- Type conversion: `convertFieldType(field, newType)` with a lossiness report (`{ lossy: boolean, sampleLosses }`) shown before confirming.
- `packages/views/src/fields/index.ts` exports `fieldTypes` map and `FieldType` union used by `tables/view-model-spec`.

**Definition of done**

- Each type has tests for parse, format, validate, filter op list and cast; property tests with `fast-check` for round-tripping parse/format.
- Storybook stories for every Cell and Editor at three densities, tagged `visual`, screenshotted at 375, 1024 and 1920 in light, dark and high-contrast.
- axe passes on all editors; keyboard-only commit/cancel verified by interaction tests.
- Type conversion matrix documented with lossiness in `docs/views/field-types.md`.
- Cell registry integration test with `design-system/data-display`.
- CHANGELOG entry; Linear comment with Storybook link.

**Edge cases**

- Currency field with per-row currency vs fixed currency option; both supported, aggregations per currency.
- Date without time compared across DST boundaries: treat as calendar date, not instant.
- Relation to a record in a dataset the user cannot read: render "Restricted" chip, not the id.
- Select option deleted while rows still reference it: keep value, render as grey "Unknown option", filter still works on id.
- Attachment whose file row is `failed`: show broken-file icon with retry.
- Rating max lowered below existing values: conversion report lists clamped rows.
- Pasting "1,234.50" or "1.234,50" into a number: parse using tenant locale, show preview.

**Dependencies**

- `tables/view-model-spec` (FieldDef); `design-system/data-display` (cell registry and `Money`, `Truncate`); `design-system/primitives` (Combobox, DatePicker); `data-layer/file-storage` (attachments); `data-layer/core-entities` (`user`).

**Agent**

Builder: Nova (Views Engineer) with Iris (Component Crafter) on editors. Reviewer: Sentinel (Code Reviewer, Visual Inspector).

**Size**

L: 17 types times parse/format/cell/editor/tests; split into two PRs (scalar types, then relational/computed).
