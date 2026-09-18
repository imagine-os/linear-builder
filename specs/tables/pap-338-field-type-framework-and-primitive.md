---
identifier: "PAP-338"
title: "Field type framework and primitive types (text, number, currency, percent, date, checkbox, rating, url, email, phone)"
project: "tables"
projectName: "Table & Views Engine"
phase: "P1"
type: "Build"
priority: 1
surfaces: ["Developer"]
milestone: "Grid with sort, filter, group"
state: "Backlog"
parent: "PAP-164"
children: []
blockedBy: ["PAP-67", "PAP-71", "PAP-161", "PAP-233", "PAP-238", "PAP-655", "PAP-656", "PAP-659", "PAP-660"]
blocks: ["PAP-339", "PAP-613", "PAP-616", "PAP-620", "PAP-622", "PAP-631", "PAP-854", "PAP-879", "PAP-911"]
key: "tables/fields/framework-primitives"
url: "https://linear.app/paperos/issue/PAP-338/field-type-framework-and-primitive-types-text-number-currency-percent"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:51:41.818Z"
model: "claude-sonnet-5"
effort: "high"
estimate: 3
dueDate: "2026-09-28"
cycle: null
---

# PAP-338: Field type framework and primitive types (text, number, currency, percent, date, checkbox, rating, url, email, phone)

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / high — Build M

**Goal**

Ship `defineFieldType`, the registry and the eleven primitive types with parse, format, validation, cells, editors and casts, so the grid can render and edit real data.

**Scope**

In: `packages/views/src/fields/{define,registry,index}.ts` and one file per primitive type; `validateRecord`; Storybook stories. Out: choice, people, attachment, relational and computed types (siblings).

**Spec**

* `defineFieldType` signature per the parent; `fieldTypes` map and `FieldType` union exported.
* `number` with `precision`, `thousandsSeparator`; `currency` as `{ amountMinor, currency }` with per-row or fixed currency; `percent` as a number option; `date` ISO with `includeTime` and `timezone`; `rating` 0..max; `phone` via `libphonenumber-js`; `email` lowercase RFC 5322; `url` normalised.
* Editors commit on Enter or blur, cancel on Escape; DatePicker from PAP-233.

*Round 4 amendment (2026-09-18):*

* Round 4: per-type validation options in `optionsSchema`: `text|longText { minLength?, maxLength?, pattern?: string (RegExp source, anchored, 200 char cap) }`, `number|currency|percent { min?, max?, step? }`, `date { min?, max?, allowPast?, allowFuture? }`, `attachment { maxFiles?, accept?: string[] }`, `multiSelect|relation|user { minItems?, maxItems? }`. `validateRecord` enforces them with `VALIDATION` details and the editors surface them inline; `FieldEditor` (PAP-332) exposes them in a Validation section.

**Interface contract**

Provides: `defineFieldType`, `fieldTypes`, `FieldType`, `validateRecord`, eleven types. Consumes: cell registry (PAP-71), DatePicker (PAP-233), `Money` (PAP-27).

**Definition of done**

* Parse, format, validate, filter-op and cast tests per type; `fast-check` round trips; stories screenshotted at 375, 1024, 1920 in three themes; axe clean.

**Test plan**

* Unit: per-type tables; locale parsing `en`, `de`, `ar`; DST calendar-date case.
* Integration: custom dataset with the eleven types round-trips through PAP-163 filters.
* Visual: matrix above.

**Demo**

Storybook `fields/primitives` shows every cell and editor; edit a currency and a date with the keyboard.

**Edge cases**

* `1.234,50` parsed by locale with preview; rating max lowered lists clamped rows in the report (sibling).

**Dependencies**

PAP-161, PAP-71, PAP-233 (hard). Blocks the two sibling children.

**Agent**

Builder: Nova with Iris on editors. Reviewer: Sentinel (Visual Inspector).

**Size**

M: eleven small types.
