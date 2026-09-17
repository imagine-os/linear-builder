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
children: ["PAP-338", "PAP-339", "PAP-340"]
blockedBy: ["PAP-67", "PAP-71", "PAP-161", "PAP-233", "PAP-238", "PAP-302"]
blocks: ["PAP-165", "PAP-171", "PAP-199", "PAP-332", "PAP-341", "PAP-347", "PAP-382"]
key: "tables/field-types"
url: "https://linear.app/paperos/issue/PAP-164/implement-field-types-text-number-currency-date-select-multi-select"
source: "Linear snapshot 2026-09-17T15:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T13:41:43.225Z"
model: null
effort: null
---

# PAP-164: Implement field types: text, number, currency, date, select, multi-select, relation, lookup, rollup, formula, attachment, user, checkbox, rating, URL, email, phone

**Model / Effort:** set on children (umbrella is never claimed)

**Goal**

Implement the field type system: for each of the 17 types one definition owning validation, parsing, formatting, cell renderer, editor, filter operators, sort and group behaviour, aggregations and storage casts. Views, forms, imports and the spec builder look behaviour up here. Umbrella for three children.

**Scope**

Children (M each, same milestone, Backlog):

* PAP-338 `defineFieldType`, registry and primitive types: text, longText, number, currency, percent, date, checkbox, rating, url, email, phone.
* PAP-339 select, multiSelect, user, attachment with cell-registry integration and `FieldSettingsPanel`.
* PAP-340 relation, lookup, rollup, formula storage type and `convertFieldType` with lossiness report.

Out: formula evaluation (PAP-171), import inference (PAP-200), `geo` (PAP-170), `button` (PAP-174), the in-app schema editor (PAP-332).

**Spec**

Decisions binding all children:

* `defineFieldType<TOptions, TValue>({ type, label, icon, optionsSchema, valueSchema, defaultOptions, parse(input, options, locale), format(value, options, locale), sql: { cast, jsonExtract }, filterOps, sortable, groupable, aggregations, Cell, Editor, OptionsEditor, exampleValues })`.
* Storage in `record.data[key]`: `date` ISO 8601 with `includeTime` and `timezone: 'utc'|'local'`; `currency` `{ amountMinor, currency }` matching `Money` (PAP-27); `relation`, `attachment`, `user` are id arrays; `select` stores option id with `{ id, name, color }` options; `rating` integer 0..max (10).
* `validateRecord(dataset, data)` runs server-side in `records.create|update` and client-side in editors; errors `VALIDATION` with `{ fieldKey, message }[]`.
* Editor props `{ value, onChange, onCommit, onCancel, autoFocus, field }`; Enter or blur commits, Escape cancels; relation and user editors use Combobox (PAP-238), date editor uses DatePicker (PAP-233).
* `libphonenumber-js` 1.x for phone, `new URL()` for url, Zod RFC 5322 for email.

**Interface contract**

Provides: `fieldTypes` map, `FieldType` union (imported by PAP-161), `defineFieldType`, `validateRecord`, `convertFieldType(field, newType) => { lossy, sampleLosses }`, `FieldSettingsPanel`, cell and editor components registered in the PAP-71 cell registry. Consumes: `Money` and `Truncate` (PAP-71, PAP-27), Combobox and DatePicker (PAP-238, PAP-233), `files.*` (PAP-37), `user` (PAP-33). Consumed by PAP-165 to PAP-170, PAP-199 mapping UI, PAP-119 data section.

* Contract source: [Interface & Data Contracts](<https://linear.app/paperos/document/paperos-interface-and-data-contracts-d40e6a4d227c>) §1 (`Money = { amountMinor: bigint, currency }` in TypeScript, `amount_minor bigint + currency char(3)` in Postgres, decimal string on the wire; the `currency` field type must store and cast exactly that and never a float; ids are UUIDv7 strings; timestamps ISO-8601 UTC); §2 row "Record" (`record.data jsonb` validated by `FieldDef[]`); §6 row "Shared value types" (provider: pending contracts issue A; interim import from PAP-175).

**Definition of done**

* All three children Done.
* Integration: a custom dataset with every type round-trips create, edit and filter through `views.query` for each `filterOp` the type declares.
* Storybook stories for every Cell and Editor at three densities; screenshots at 375, 1024, 1920 in light, dark, high-contrast; axe clean.
* `docs/views/field-types.md` with the conversion matrix; CHANGELOG; Linear comment with Storybook link.

**Test plan**

Umbrella test `fields.e2e.test.ts`: seed one record per example value for all 17 types; for each type and each declared `filterOp` run the compiler and assert the in-memory `parse`/`format` oracle agrees; `fast-check` property test that `parse(format(v)) == v` for every type and locale `en`, `de`, `ar`; Playwright keyboard-only commit and cancel on each editor; visual matrix as above.

**Demo**

Reviewer opens Storybook `fields/all-types` showing every Cell beside its Editor, edits a currency cell and a relation cell with the keyboard, then opens `fields/convert` where changing number to text shows the lossiness report. Under two minutes.

**Edge cases**

* Per-row versus fixed currency: both supported, aggregations per currency.
* Date without time across DST: calendar date, not instant.
* Relation to an unreadable record: "Restricted" chip.
* Deleted select option: value kept, grey "Unknown option", filters still match by id.
* Pasting `1.234,50` into a number: tenant-locale parse with preview.

**Dependencies**

PAP-161 (hard), PAP-71 (hard, cell registry), PAP-67 children (hard), PAP-233 (hard for date editor), PAP-37 (attachment child only), PAP-33. Blocks PAP-165, PAP-171, PAP-199.

**Agent**

Builder: Nova (Views Engineer) with Iris (Component Crafter) on editors. Reviewer: Sentinel (Code Reviewer, Visual Inspector).

**Size**

L, split into three M children.

**Pending issues**

Bracketed references above are fully specified work packages that Linear refused to create on 2026-09-17 (`USAGE_LIMIT_EXCEEDED`, free-plan issue cap). Their specs live in the project document(s) [tables](<https://linear.app/paperos/document/round-2-pending-issues-tables-24-86486d9b99cc>) and they are created as issues by `round2/agent4/create_issues.py` once the workspace plan is upgraded.
