---
identifier: "PAP-627"
title: "Additional field types: richText (Tiptap JSON), duration, time, progress and json with cells, editors, casts and conversions"
project: "tables"
projectName: "Table & Views Engine"
phase: "P2"
type: "Build"
priority: 3
surfaces: ["Developer"]
milestone: "Grid with sort, filter, group"
state: "Backlog"
parent: "PAP-164"
children: []
blockedBy: ["PAP-71", "PAP-142", "PAP-233", "PAP-340", "PAP-604", "PAP-656", "PAP-660"]
blocks: ["PAP-171", "PAP-332", "PAP-341", "PAP-344", "PAP-347", "PAP-382"]
key: "r4/tables/extra-field-types"
url: "https://linear.app/paperos/issue/PAP-627/additional-field-types-richtext-tiptap-json-duration-time-progress-and"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:30:21.483Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 3
dueDate: "2026-09-28"
cycle: null
---

# PAP-627: Additional field types: richText (Tiptap JSON), duration, time, progress and json with cells, editors, casts and conversions

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Build M

**Goal**

Close the parity rows the seventeen core types leave open against Airtable (rich long text, duration), Notion (rich text everywhere), Baserow and NocoDB (duration, time, JSON) and ClickUp and Monday (manual progress): five more `defineFieldType` entries importers can map onto without lossy conversion to text.

**Scope**

In: `packages/views/src/fields/{richText,duration,time,progress,json}.ts`; cells and editors; compiler casts and ops; conversion matrix rows; `docs/views/field-types.md` update.

Out: system metadata types (PAP-616), agent-computed fields, barcode and QR (matrix `wontdo` with ADR), collaborative editing of `richText` cells in the grid (single-user editor; PAP-142 rooms only in the record page).

**Spec**

* `richText`: stores Tiptap JSON (PAP-142 schema subset: paragraphs, marks, lists, links, mentions) plus a derived `text` for search and `ILIKE`; cell renders the first 200 characters of plain text; editor is a compact Tiptap instance in a Popover (PAP-142 `RichTextEditor`), full editor in `RecordPanel`; `sql.cast` reads `data->'notes'->>'text'`.
* `duration`: integer seconds; options `{ format: 'h:mm' | 'h:mm:ss' | 'decimalHours' | 'days' }`; parse accepts `1h 30m`, `1:30`, `90m`; ops are number ops; aggregations `sum|avg|min|max`; formula type `number` with `DURATION_FORMAT`.
* `time`: wall-clock `HH:mm[:ss]` without date, stored as text, cast `::time`; editor is PAP-233 `TimeField`; ops `is|isBefore|isAfter|isBetween`; sorts correctly across midnight by option `dayStartsAt`.
* `progress`: number 0..1 with `{ display: 'bar' | 'ring' | 'percent', color? }`; cell reuses PAP-71 `progress` renderer; editor slider (PAP-236) and numeric input; may be `computed` from a rollup (`fn: 'avgChecked'`).
* `json`: arbitrary JSON up to 16 KB with a CodeMirror editor (PAP-383 dependency for the language mode), pretty cell with copy; ops `isEmpty|contains(path, value)` via `jsonb @>`; excluded from grouping.
* Conversions: `longText ↔ richText` (Markdown round trip via `marked`), `number ↔ duration|progress`, `text ↔ time` (lossy when unparsable), anything → `json` (wraps), `json` → `text` (stringifies).

**Interface contract**

Provides: five FieldTypes, `durationParse|durationFormat`, `richTextToPlain`, conversion matrix rows, casts for PAP-335. Consumes: relational child and `convertFieldType` (PAP-340), Tiptap editor (PAP-142), `TimeField` (PAP-233), `progress` cell (PAP-71), CodeMirror mode (PAP-383, soft), compiler ops (PAP-335). Consumed by PAP-199 mapping, PAP-417 Notion import (rich text), PAP-427 packs.

**Definition of done**

* Five types with stories at 375, 1024, 1920 in three themes; axe clean; per-type parse, format, validate, ops and cast tests; conversion pairs tested.
* `docs/views/field-types.md` and the parity CSV (PAP-162) updated; CHANGELOG; Linear comment.

**Test plan**

* Unit: duration parsing table (`1h 30m`, `1:30`, `90m`, `1.5h`); time midnight ordering; rich text plain derivation and Markdown round trip; json size cap; progress clamp.
* Integration: each type round-trips create, edit and filter through `views.query`; `richText` search hits through `ILIKE` on the derived text.
* E2E: add a rich text and a duration column in `/demo/grid`, type `1h 30m`, bold a word in the notes popover, filter duration greater than one hour.

**Demo**

Reviewer adds Notes (rich text) and Effort (duration), formats a note, sums Effort in the footer and sees `12:30`. Under two minutes.

**Edge cases**

* Rich text with a mention of a removed user: rendered as plain text chip.
* Duration over 24 h in `h:mm` format: `36:15`, never wraps.
* Time in a tenant with `dayStartsAt: 06:00`: `02:00` sorts after `23:00`.
* JSON above 16 KB: `VALIDATION` with size.

**Dependencies**

PAP-340 (hard, conversion routine), PAP-142 (hard for `richText`; the other four may land first). Soft: PAP-233, PAP-71, PAP-383, PAP-335. PAP-199 maps these types when they exist (soft).

**Agent**

Builder: Nova (Views Engineer); Iris on editors. Reviewer: Sentinel (Code Reviewer).

**Size**

M: one session.

*Round 4 critique fix (2026-09-18):* resolved 1 round-4 file key in this description to Linear identifiers: `r4/tables/system-fields` = PAP-616.
*Round 4 critique fix (2026-09-18):* moved to the parent's milestone (Grid with sort, filter, group) and dueDate 2026-09-28 so the umbrella PAP-164 closes with its last child.
