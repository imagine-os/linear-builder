# tables — Table & Views Engine
PHASE P1 prio 1 dependsOn ['data-layer', 'design-system', 'input']
SUMMARY: A view model that is a superset of Airtable, Notion and ClickUp views, compiled to SQL, with grid, kanban, calendar, timeline, Gantt, gallery, list, form, map and chart views, rich field types and formulas.
DESC: Goal: any dataset in any app can be viewed, sorted, filtered, grouped and edited as well as in Airtable, Notion or ClickUp, and those views compose into dashboards. A view model spec defines data source, fields, filters, sorts, groups, aggregations, permissions and sharing; a query compiler turns it into SQL and Electric shapes with server-side pagination. Views include a virtualized editable grid, kanban with swimlanes, calendar/timeline/Gantt, gallery/list/form, map and chart. Field types cover text through relations, lookups, rollups and formulas with a formula engine. Saved, shared and public views plus dashboard blocks with cross-filters complete it. A parity audit against Airtable, Notion, ClickUp, Baserow and NocoDB tracks coverage. Non-goal: a spreadsheet grid with arbitrary cell formulas.
MILESTONES: ['Grid with sort, filter, group 2026-09-23: View model, parity audit, query compiler, field types, grid, filter UI', 'All view types 2026-09-27: Kanban, calendar/timeline/Gantt, gallery/list/form, map/chart', 'View sharing, formulas, dashboards 2026-09-30: Formula engine, saved and public views, dashboard blocks']


## PAP-161 [P0 Spec M prio1 Ready for Claude] Specify the view model: data source, fields, filters, sorts, groups, aggregations, permissions and sharing as a superset of Airtable, Notion and ClickUp
key=tables/view-model-spec milestone=Grid with sort, filter, group agent=Builder: Quill (Page Spec Writer) with Nova (Views Engineer)
blockedBy=[] blocks=['PAP-207', 'PAP-164', 'PAP-163']
GOAL: Define the one schema every PaperOS view renders from: a `ViewSpec` that describes data source, fields, filters, sorts, groups, aggregations, permissions and sharing as a strict superset of what Airtable, Notion and ClickUp views can express. Every later issue in this project (compiler, grid, kanban, dashboards) consumes this type unchanged, so it must be complete before any view code is written.
SCOPE: In:

* `packages/views/src/model/` in `imagine-os/paperos-template`: Zod schemas, TypeScript types, JSON Schema export, migration helpers.
* Drizzle tables `dataset`, `field`, `record` (custom datasets) and `view` in `packages/views/src/schema.ts`.
* Spec doc `docs/views/view-model.md` with one worked example per view kind.
* Code-defined dataset registry so Drizzle entities (contacts, issues, invoices) appear as datasets.

Out: query execution (`tables/query-compiler`), field renderers (`tables/field-types`), sharing tokens (`tables/view-sharing`).
SPEC(first 1200): * `DatasetRef = { kind: 'entity', key: string } | { kind: 'custom', datasetId: string }`. Code datasets register via `registerDataset({ key, table, fields: FieldDef[], defaultSort, rls: true })` in `packages/views/src/registry.ts`; custom datasets store `FieldDef[]` in the `field` table and rows as `record.data jsonb`.
* `FieldDef = { id, key, name, type: FieldType, options: Record<string, unknown>, required, unique, hidden, computed }`; `FieldType` is the union listed in `tables/field-types`.
* `ViewSpec = { id, datasetRef, kind: 'grid'|'kanban'|'calendar'|'timeline'|'gantt'|'gallery'|'list'|'form'|'map'|'chart', name, fields: { fieldId, width?, visible, order, frozen? }[], filter: FilterGroup, sorts: { fieldId, dir, nullsLast }[], groups: { fieldId, dir, collapsed?: string[] }[] (max 3), aggregations: { fieldId, fn: 'count'|'sum'|'avg'|'min'|'max'|'median'|'unique'|'empty'|'filled'|'percentEmpty' }[], rowHeight: 'short'|'medium'|'tall'|'extraTall', options: kind-specific (e.g. kanban `{ groupField, swimlaneField?, wipLimits }`, calendar `{ startField, endField? }`), search?: string, visibility: 'personal'|'shared'|'public', ownerUserId, permissions: { canEditRecords: AudienceId[]
DOD:
* Zod schemas, types and JSON Schema committed; `pnpm --filter views test` covers parse, strict-mode rejection, migration and one fixture per kind.
* Drizzle migration for `dataset`, `field`, `record`, `view` with RLS policies via `data-layer/rls-tenancy` and cross-tenant harness green.
* `docs/views/view-model.md` documents every property with an Airtable/Notion/ClickUp equivalence column.
* Fixture `packages/views/fixtures/*.view.json` for the 10 kinds validates in CI.
* Registry proves a Drizzle entity (`memberships`) exposes as a dataset in a test.
* ADR `docs/adr/00xx-view-model.md`; CHANGELOG entry; Linear comment linking the doc on GitHub Pages.
EDGE:
* Filter references a deleted field: spec stays valid, condition flagged `orphaned` and skipped at compile.
* Group on a multi-select: define "one row per value" vs "combination" semantics (default: combination, option `expandMulti`).
* Custom dataset with 500 fields: `record.data` stays jsonb but enforce max 500 fields and 100 KB per row.
* Views on entities with RLS: spec never grants more than RLS allows; `permissions` only narrows.
* Nested filter depth beyond 5 rejected with a clear error.
* Two views with the same name in a dataset: allowed, but slugs are unique.
DEPS: * `data-layer/core-entities` for tenant/workspace/user FKs; `data-layer/drizzle-schema` for migration workflow; `tables/feature-parity-audit` runs in parallel and feeds the equivalence column.


## PAP-162 [P0 Research M prio2 Ready for Claude] Audit Airtable, Notion, ClickUp, Baserow and NocoDB view features into a parity checklist
key=tables/feature-parity-audit milestone=Grid with sort, filter, group agent=Builder: Scout (Library Evaluator). Reviewer: Nova (Views En
blockedBy=[] blocks=[]
GOAL: Turn "every feature Airtable, Notion and ClickUp have for views" into a concrete, checkable parity list. The audit enumerates view types, field types, filter operators, grouping, aggregation, sharing and interaction features across Airtable, Notion, ClickUp, Baserow and NocoDB, marks which PaperOS issue covers each, and becomes the coverage tracker the project reports against.
SCOPE: In:

* `docs/views/parity.md` (human-readable) and `docs/views/parity.csv` (machine-readable) in `imagine-os/paperos-template`.
* Coverage script `pnpm --filter views parity:report` that prints percentage covered per product and per category.
* Gap issues: any feature not covered by an existing `tables/*` issue is proposed as a new Linear issue draft in the comment.

Out: implementing any feature; UI screenshots of competitors (link to public docs instead).
SPEC(first 1200): * Sources: public documentation and changelogs of Airtable, Notion, ClickUp, Baserow and NocoDB; the OSS repos of Baserow and NocoDB for their view/field enums. Use `WebFetch`; cite URLs in a `source` column.
* CSV columns: `id, category, feature, airtable, notion, clickup, baserow, nocodb, paperos_issue, paperos_status (planned|in_progress|done|wontdo), notes, source`. Product columns hold `yes|partial|no|paid`.
* Categories (minimum): view types; field types; filter operators per field type; sort options; grouping (levels, collapsed, aggregates per group); aggregations; row height/density; column ops (freeze, hide, resize, reorder, wrap); record expansion; inline editing; bulk edit; keyboard navigation; kanban (swimlanes, WIP, card cover, collapse); calendar/timeline/Gantt (dependencies, milestones, zoom); gallery/list; forms (conditional logic, prefill, branding); map; charts; formulas (function count); lookups/rollups; sharing (personal/shared/public, embed, password, expiry); permissions (field-level, view lock); dashboards (blocks, cross-filter); import/export; API access; automations (mark out of scope with pointer to `growth/*` or a future project).
* Expect 250-400 rows. E
DOD:
* `parity.md` and `parity.csv` committed; CSV validates; report prints per-product coverage.
* At least 250 rows with source URLs; formula inventory has 80+ functions.
* Every `tables/*` issue is referenced by at least one row; gaps listed in a "Proposed issues" section with one-line acceptance criteria.
* `docs/views/parity.md` linked from `docs/views/view-model.md`.
* CHANGELOG entry (docs section); Linear comment summarising coverage percentages and the top 10 gaps for Atlas to decide on.
* Report script runs in CI gate 1 (`quality/ci-gate1`) as a docs check.
EDGE:
* Features gated behind paid tiers (Airtable Interfaces, Notion charts) recorded as `paid`, not `yes`.
* Features that are the same idea under different names (Notion "sub-items" vs ClickUp "subtasks") get one row with aliases in notes.
* Product docs that change during the audit: record the access date in `source`.
* Features PaperOS deliberately declines (spreadsheet cell formulas) marked `wontdo` with the ADR link.
* Baserow/NocoDB features absent from the big three are still listed; they often reveal cheap wins.
DEPS: * `tables/view-model-spec` consumes the equivalence table; `libraries/data-landscape` and `libraries/oss-products` overlap on NocoDB/Baserow and should be cross-linked, not duplicated.


## PAP-163 [P1 Build L prio1 Backlog] Build the view query compiler from view model to SQL and Electric shapes with server-side pagination
key=tables/query-compiler milestone=Grid with sort, filter, group agent=Builder: Nova (Views Engineer). Reviewer: Sentinel (Code Rev
blockedBy=['PAP-35', 'PAP-161'] blocks=['PAP-170', 'PAP-169', 'PAP-168', 'PAP-167', 'PAP-165']
GOAL: Turn any `ViewSpec` into an efficient, RLS-respecting Postgres query and, where possible, an Electric shape, so views render server-paginated pages of rows, groups and aggregates without every view component writing SQL. This is the engine every view kind calls.
SCOPE: In:

* `packages/views/src/compiler/` with `compileView`, `compileFilter`, `compileSort`, `compileGroups`, `compileAggregates`.
* oRPC procedures `views.query`, `views.count`, `views.groups`, `views.distinct` in `packages/views/src/api.ts`.
* Electric shape registration for simple views (`data-layer/local-first-sync`).
* Client hook `useViewQuery(spec, { pageSize })` with infinite pagination.

Out: filter UI (`tables/filter-sort-group-ui`), formula evaluation (`tables/formula-engine`; compiler treats formula fields as opaque until then), full-text search ranking (`data-layer/search`).
SPEC(first 1200): * Input `compileView(spec: ViewSpec, ctx: { actor, tenantId, dataset: ResolvedDataset, cursor?, limit, groupPath?: GroupKey[] })` returns `{ rows: SQL, count: SQL, groups?: SQL, aggregates?: SQL, shape?: ShapeDef }` using Drizzle `sql` fragments. Never string-concatenate user values; all literals are bound parameters.
* Dataset resolution: entity datasets compile to real columns; custom datasets compile `record.data -> 'fieldKey'` with casts chosen from the field type (`::numeric`, `::timestamptz`, `::boolean`, `::text[]`). Custom datasets get a GIN index on `data` and expression indexes created on demand for fields used in sorts (`views.ensureIndex` job, capped at 10 per dataset).
* Filters: each `FilterOp` has a compile function per field type in `compiler/ops/<type>.ts`; relative dates resolve on the server in the actor's timezone; `{ ref: 'currentUser' }` resolves to `ctx.actor.id`. Relations compile to `EXISTS` subqueries; lookups/rollups compile to lateral joins.
* Sorting: keyset pagination using the sort fields plus `id` as tiebreaker; cursor is base64url JSON of the last row's sort values, signed with HMAC so clients cannot forge it. `limit` capped at 200; default 50.
* Gr
DOD:
* Unit tests per op per type (table-driven) and golden SQL snapshots for the 10 fixture views.
* Integration test against Postgres with a 100k-row seed: p95 under 150 ms for filtered, sorted, paginated queries; measured in CI with `vitest bench` and recorded in the PR.
* Cursor tamper test returns `VALIDATION`.
* Cross-tenant test from `data-layer/rls-tenancy` extended with view queries.
* `docs/views/query-compiler.md` explains compile pipeline, cursor format, shape eligibility.
* CHANGELOG entry; Linear comment with benchmark table and link to the docs page.
EDGE:
* Sort on a field with all nulls: `nullsLast` respected, keyset cursor handles null boundaries.
* Filtering a relation field by a record the actor cannot see: `EXISTS` inherits RLS so the row simply does not match.
* Group key with 10k distinct values: `views.groups` paginates groups (`limit` 100) and the UI shows "load more groups".
* Field type changed after a cursor was issued: cursor version mismatch returns `CONFLICT`, client restarts from page one.
* Aggregate `sum` on currency fields with mixed currencies: return per-currency map, never a blind sum.
* Timezone differing between actor and tenant for "today": actor timezone wins; documented.
DEPS: * `tables/view-model-spec` (types); `data-layer/api-layer` (oRPC conventions, error codes); `data-layer/local-first-sync` (shape registry); `identity/rbac-abac` (`toPredicate`); `data-layer/rls-tenancy`.


## PAP-164 [P1 Build L prio1 Backlog] Implement field types: text, number, currency, date, select, multi-select, relation, lookup, rollup, formula, attachment, user, checkbox, rating, URL, email, phone
key=tables/field-types milestone=Grid with sort, filter, group agent=Builder: Nova (Views Engineer) with Iris (Component Crafter)
blockedBy=['PAP-161'] blocks=['PAP-199', 'PAP-171', 'PAP-165']
GOAL: Implement the field type system: for each of the 17 field types, a definition that owns validation, parsing, formatting, default cell renderer and editor, allowed filter operators, sort and group behaviour, aggregations and storage casting. Views, forms, imports and the spec builder all look up field behaviour here instead of special-casing types.
SCOPE: In:

* `packages/views/src/fields/` with `defineFieldType`, a registry, and one file per type: text, longText (alias of text with `multiline`), number, currency, percent (number option), date, select, multiSelect, relation, lookup, rollup, formula (storage and type only; evaluation in `tables/formula-engine`), attachment, user, checkbox, rating, url, email, phone.
* Cell renderers registered into the `design-system/data-display` cell registry and cell editors for inline editing.
* Field options editors (`FieldSettingsPanel`) used by grid column menus and the custom-dataset schema editor.

Out: formula parsing/evaluation; import type inference (`migration/csv-excel`); geo field (added in `tables/map-chart-views`).
SPEC(first 1200): * `defineFieldType<TOptions, TValue>({ type, label, icon, optionsSchema: ZodSchema, valueSchema: ZodSchema, defaultOptions, parse(input, options, locale): TValue | ParseError, format(value, options, locale): string, sql: { cast, jsonExtract }, filterOps: FilterOp[], sortable, groupable, aggregations: AggregateFn[], Cell, Editor, OptionsEditor, exampleValues })`.
* Storage: values in `record.data[fieldKey]` as JSON; `date` is ISO 8601 string with `options.includeTime` and `options.timezone: 'utc'|'local'`; `currency` is `{ amountMinor: number, currency: 'USD' }` (never floats, matching `Money` in data-display); `relation` is `string[]` of record ids with `options.datasetRef, options.limitOne, options.symmetricFieldId`; `attachment` is `string[]` of `file.id` from `data-layer/file-storage`; `user` is `string[]` of `user.id`; `select` stores option id, options carry `{ id, name, color (token name) }`; `rating` is integer 0..options.max (max 10).
* `lookup` options `{ relationFieldId, targetFieldId }`; `rollup` options `{ relationFieldId, targetFieldId, fn }`; both are `computed: true`, read-only, compile via lateral joins in `tables/query-compiler`.
* Validation runs server-side in `r
DOD:
* Each type has tests for parse, format, validate, filter op list and cast; property tests with `fast-check` for round-tripping parse/format.
* Storybook stories for every Cell and Editor at three densities, tagged `visual`, screenshotted at 375, 1024 and 1920 in light, dark and high-contrast.
* axe passes on all editors; keyboard-only commit/cancel verified by interaction tests.
* Type conversion matrix documented with lossiness in `docs/views/field-types.md`.
* Cell registry integration test with `design-system/data-display`.
* CHANGELOG entry; Linear comment with Storybook link.
EDGE:
* Currency field with per-row currency vs fixed currency option; both supported, aggregations per currency.
* Date without time compared across DST boundaries: treat as calendar date, not instant.
* Relation to a record in a dataset the user cannot read: render "Restricted" chip, not the id.
* Select option deleted while rows still reference it: keep value, render as grey "Unknown option", filter still works on id.
* Attachment whose file row is `failed`: show broken-file icon with retry.
* Rating max lowered below existing values: conversion report lists clamped rows.
* Pasting "1,234.50" or "1.234,50" into a number: parse using tenant locale, show preview.
DEPS: * `tables/view-model-spec` (FieldDef); `design-system/data-display` (cell registry and `Money`, `Truncate`); `design-system/primitives` (Combobox, DatePicker); `data-layer/file-storage` (attachments); `data-layer/core-entities` (`user`).


## PAP-165 [P1 Build L prio1 Backlog] Build the virtualized grid view (TanStack Table) with inline edit, column resize/reorder, freeze and cell types
key=tables/grid-view milestone=Grid with sort, filter, group agent=Builder: Nova (Views Engineer). Reviewer: Sentinel (Code Rev
blockedBy=['PAP-71', 'PAP-164', 'PAP-163'] blocks=['PAP-183', 'PAP-173', 'PAP-172', 'PAP-166', 'PAP-135']
GOAL: Build the workhorse grid view: a virtualised, keyboard-first, inline-editable table on TanStack Table with column resize, reorder, freeze, hide, row density, grouping headers and aggregate footers, rendering any dataset through the query compiler and field types. It must feel as fast as Airtable at 100k rows.
SCOPE: In:

* `packages/views/src/views/grid/` exporting `<GridView spec onSpecChange datasetRef />` and the record side panel `<RecordPanel />`.
* Column header menu (sort, filter, group, hide, freeze, edit field, insert left/right, delete for custom datasets).
* Row selection, bulk actions bar (delete, duplicate, set field value), copy/paste of cell ranges as TSV.
* Add row, expand row, row reorder for custom datasets with a manual sort field.

Out: filter/sort/group builder panels (`tables/filter-sort-group-ui`, this issue exposes the hooks), sharing controls, formula editing.
SPEC(first 1200): * Libraries: `@tanstack/react-table` 8.x, `@tanstack/react-virtual` 3.x (rows and columns virtualised), `input/drag-drop` `SortableList` for column reorder and row reorder, `fractional-indexing` for `sort_key`.
* Data: `useViewQuery` from `tables/query-compiler`; page size 100; prefetch next page when the last rendered row is within 30 rows of the end; groups rendered as sticky headers with collapse state persisted in `spec.groups[].collapsed`.
* Layout: header sticky; frozen columns via `position: sticky` with a shadow when scrolled; row heights 32/40/56/88 px for the four `rowHeight` values; column widths from `spec.fields[].width` (min 60, max 1200), persisted through `onSpecChange` debounced 500 ms; resize handle 8 px hit area, double-click auto-fits from the visible rows.
* Cells: rendered via field type `Cell`; edit mode opens `Editor` on Enter, F2, double-click or typing a printable character; commit writes through `mutate(orpc.records.update, ..., { optimistic })` from `data-layer/local-first-sync`, reverting and toasting on rejection.
* Keyboard: arrow keys move the active cell; Shift+arrows extend range; Tab/Shift+Tab move across columns; Home/End, PageUp/PageDown, Ctrl+H
DOD:
* Vitest for selection model, keyboard reducer, clipboard parsing; Playwright interaction tests for edit, resize, reorder, freeze and paste.
* Storybook story `views/grid` with 10k rows tagged `visual`; screenshots at 375, 768, 1024, 1440, 1920 across three themes and four densities.
* axe clean; screen reader announces row/column and edit state (NVDA and VoiceOver spot check per `input/screen-reader` checklist).
* Performance trace attached to the PR meeting the budgets.
* `docs/views/grid.md` covering keyboard map and extension points.
* CHANGELOG entry; Linear comment with Pages demo link and video replay from `quality/video-replays`.
EDGE:
* 375 px width: horizontal scroll with first column frozen, header menu becomes a bottom sheet.
* Row deleted by another user while being edited: editor closes, toast "record removed", focus moves to the next row (`realtime/conflict-ux`).
* Paste of 5,000 rows: chunk into batches of 200 mutations with progress and cancel.
* Column widths exceed viewport with frozen columns wider than viewport: cap frozen total at 60 percent.
* Group header for a null value labelled "(empty)" and sorts last.
* Read-only dataset or denied `update`: cells render but editors do not open, cursor indicates read-only.
DEPS: * `tables/query-compiler`, `tables/field-types`, `design-system/data-display`, `input/drag-drop`, `input/command-registry`, `input/focus-management`, `data-layer/local-first-sync`.


## PAP-166 [P1 Build M prio1 Backlog] Build the filter builder (AND/OR groups), multi-sort and multi-level grouping UI with aggregates
key=tables/filter-sort-group-ui milestone=Grid with sort, filter, group agent=Builder: Nova (Views Engineer). Reviewer: Sentinel (Visual I
blockedBy=['PAP-165'] blocks=['PAP-195', 'PAP-174']
GOAL: Give every view Airtable-class controls: a filter builder with nested AND/OR groups and per-type operators, a multi-sort editor, up to three levels of grouping with per-group aggregates, and a view toolbar that hosts them. The panels edit the `ViewSpec` and everything else re-renders through the compiler.
SCOPE: In:

* `packages/views/src/controls/`: `<ViewToolbar />`, `<FilterBuilder />`, `<SortEditor />`, `<GroupEditor />`, `<AggregateFooter />`, `<FieldVisibilityMenu />`, `<SearchBox />`.
* Relative date pickers, dynamic values (`currentUser`, `today`), quick filters (chips) for select and user fields.
* Aggregate selection per column footer and per group header.

Out: saved-view management (`tables/view-sharing`), formula fields in filters beyond their result type.
SPEC(first 1200): * Toolbar layout: left `[Views ▾] [Search]`, right `[Fields] [Filter n] [Sort n] [Group n] [Row height] [Share]`; each control shows a count badge when active; below 768 px it collapses to a single "Options" button opening a bottom sheet with tabs.
* `FilterBuilder` renders `spec.filter` as rows: `[field ▾] [op ▾] [value editor]`; a group renders indented with its own `and/or` toggle; "Add condition", "Add group" (max depth 5); drag handles reorder via `input/drag-drop`. Operators come from `fieldTypes[type].filterOps`; value editor comes from the field type `Editor` or a dedicated filter editor (`isWithin` shows unit and amount; relative anchors: `today, yesterday, tomorrow, oneWeekAgo, oneWeekFromNow, oneMonthAgo, oneMonthFromNow, startOfWeek, startOfMonth, exactDate`).
* Edits are applied optimistically to the spec after 300 ms debounce; the compiler query runs and the toolbar shows "n of N records" from `views.count`.
* `SortEditor`: ordered list `[field ▾] [A→Z | Z→A] [nulls last]`, drag to reorder, max 5 sorts; manual order option for custom datasets toggles the `sort_key` column.
* `GroupEditor`: up to 3 levels, each `[field ▾] [order]` and `expandMulti` toggle for multi-sel
DOD:
* Vitest for spec reducers (add/remove/move condition, depth limit, URL round-trip).
* Playwright interaction tests: build a 3-level nested filter, reorder sorts, group by two fields, change aggregate, verify grid counts.
* Storybook stories for each control tagged `visual`; screenshots at 375, 768, 1024, 1440, 1920, three themes.
* axe clean; focus returns to the toolbar button when a panel closes.
* `docs/views/controls.md` with operator table per field type.
* CHANGELOG entry; Linear comment with demo link and video replay.
EDGE:
* Field removed while the panel is open: row shows "field deleted" and a remove button.
* Contradictory filters (`is empty` and `is not empty`) allowed, count shows 0, no error.
* Grouping by the same field twice is blocked in the picker.
* 40 quick-filter chips: overflow into a "+n" popover.
* URL temporary filters exceeding 2 KB: fall back to session storage with a warning.
* Screen reader: operator changes announce the new sentence form ("Status is any of Open, Blocked").
DEPS: * `tables/grid-view` (hosts the toolbar), `tables/query-compiler` (count and aggregates), `tables/field-types` (operators, editors), `input/drag-drop`, `design-system/primitives` (Popover, Sheet, Combobox).


## PAP-167 [P1 Build M prio1 Backlog] Build the kanban board view with swimlanes, WIP limits and drag-and-drop
key=tables/kanban-view milestone=All view types agent=Builder: Nova (Views Engineer). Reviewer: Sentinel (Visual I
blockedBy=['PAP-155', 'PAP-163'] blocks=['PAP-189', 'PAP-102']
GOAL: Build the kanban board view so any dataset with a select, status or user field can be worked as a board: columns per group value, optional swimlanes by a second field, WIP limits, accessible drag-and-drop between and within columns, card templates and inline card creation. PM boards (`pm-linear/board-views`) and CRM pipelines (`growth/crm-views`) are the first consumers.
SCOPE: In:

* `packages/views/src/views/kanban/`: `<KanbanView spec onSpecChange datasetRef />`, `<KanbanColumn />`, `<KanbanCard />`, `<CardTemplateEditor />`.
* Kanban options in `ViewSpec.options`: `{ groupField, swimlaneField?, wipLimits: Record<optionId, number>, cardFields: fieldId[], coverField?, colorField?, hideEmptyColumns, collapsedColumns: optionId[], columnOrder?: optionId[] }`.
* Column-level aggregates (count and one numeric sum) in the header.

Out: Gantt/time (`tables/calendar-timeline-gantt`), automation on move (future), swimlane by relation (v2).
SPEC(first 1200): * Group field must be `select`, `user` or a relation with `limitOne`; the picker only offers those. Columns come from `views.groups` level 1 with counts; card pages per column via `views.query` with `groupPath`, page size 50 and "Load more" at the column end; the column virtualises cards with `@tanstack/react-virtual`.
* Swimlanes: when `swimlaneField` set, rows per lane value with collapsible lane headers; each cell is a column-lane intersection with its own pagination.
* Drag-and-drop uses `input/drag-drop` (`SortableList` across containers with `canDrop`); dropping into a column writes `{ [groupField]: optionId }` plus `sort_key` via `between()` for custom datasets; for entity datasets with no manual order, position within column is by the view's sort and drop only changes the group value (UI shows a "sorted by X" hint). Moves are optimistic and revert with a toast on rejection.
* WIP limit: header shows `n / limit`, turns warning colour at limit and danger above; `canDrop` returns `{ reason: 'WIP limit reached' }` when a limit would be exceeded unless the user holds Alt (override, audited in the update reason).
* Card: title field (first text field or dataset `titleField`), up 
DOD:
* Vitest for move reducer, WIP evaluation and template config.
* Playwright: drag card between columns, keyboard move, WIP block, inline add, swimlane collapse; runs against seed of 2,000 records across 8 columns.
* Storybook story tagged `visual`; screenshots at 375, 768, 1024, 1440, 1920 in three themes; video replay of a drag flow at each width.
* 60 fps drag verified with the Profiler assertion pattern from `input/drag-drop`.
* `docs/views/kanban.md`; CHANGELOG entry; Linear comment with demo link.
EDGE:
* Group field with 200 options: columns virtualised horizontally, hidden by default beyond the first 30 with "Show all".
* Two users move the same card simultaneously: last write wins by server timestamp, the loser's card animates to its actual column (`realtime/record-sync`).
* Card moved into a column the user cannot write (permission condition on status): `canDrop` denied with reason from `decision.explain()`.
* Column option deleted while board open: cards move to "(no value)" after refetch, toast explains.
* Very long titles wrap to 3 lines then truncate with tooltip.
* Offline: moves queue in the offline outbox and cards show a pending badge.
DEPS: * `tables/query-compiler`, `tables/field-types`, `input/drag-drop`, `design-system/data-display` (AvatarStack, Badge), `realtime/record-sync` for live updates (optional at first).


## PAP-168 [P1 Build L prio2 Backlog] Build calendar, timeline and Gantt views with dependencies
key=tables/calendar-timeline-gantt milestone=All view types agent=Builder: Nova (Views Engineer). Reviewer: Sentinel (Edge Cas
blockedBy=['PAP-163'] blocks=[]
GOAL: Add the three time-based views: a calendar (month, week, day, agenda), a horizontal timeline with zoom, and a Gantt with dependency arrows and critical path highlighting. Any dataset with a date field can be scheduled by dragging; Gantt additionally reads a self-relation field for dependencies.
SCOPE: In:

* `packages/views/src/views/time/`: shared `TimeScale` engine, `<CalendarView />`, `<TimelineView />`, `<GanttView />`, `<DateRangeNav />`.
* Options: `{ startField, endField?, allDay?: boolean, dependencyField?, milestoneField?, progressField?, laneField? (timeline/Gantt grouping), colorField?, workingDays: number[], zoom: 'hour'|'day'|'week'|'month'|'quarter' }`.
* Drag to move, resize to change duration, create by drag-selecting a range.

Out: recurring events, external calendar sync (Google/Outlook, future project), resource levelling.
SPEC(first 1200): * Dates: `date-fns` 4.x and `@date-fns/tz`; all math in the actor's timezone; all-day dates treated as calendar dates. Fetch window is the visible range padded by one period, compiled as `startField <= rangeEnd AND coalesce(endField, startField) >= rangeStart` via `tables/query-compiler`; page size 500 with an "n more" overflow chip per day cell.
* Calendar: CSS grid 7 columns; month cells show up to 4 events then "+n"; week/day show a time axis with 30-minute slots and overlapping events laid out with a column-packing algorithm; agenda is a grouped list by day reusing `tables/gallery-list-form` list rows. Navigation: prev/next/today, keyboard arrows move day focus, Enter opens the record panel, `n` creates.
* Timeline: horizontal virtualised canvas (`@tanstack/react-virtual` on both axes), lanes from `laneField` groups, zoom levels with sticky date headers (two-tier: month over day, quarter over week); wheel plus Ctrl zooms, drag pans; today marker line; items as bars with title, milestone as diamond.
* Gantt: timeline plus a left frozen grid (title, start, end, duration, assignee) reusing grid cells; dependencies drawn as SVG paths (finish-to-start) from `dependencyField` (relati
DOD:
* Vitest for range compilation, overlap packing, critical path, working-day math and DST cases (fixtures for America/Los_Angeles and Europe/Berlin).
* Playwright: drag to reschedule, resize, create by drag, add dependency, zoom; 2,000-item seed.
* Storybook stories per view tagged `visual`; screenshots at 375, 768, 1024, 1440, 1920, three themes; video replay of the Gantt drag at 1024 and 1920.
* axe clean; keyboard-only rescheduling works.
* `docs/views/time-views.md` with options table; CHANGELOG entry; Linear comment with demo link.
EDGE:
* End before start after a resize: clamp to zero duration and warn.
* Events spanning months in month view render as multi-row spans with continuation arrows.
* Dependency cycles (A→B→A): reject on create with explanation; existing cycles from imports render dashed red.
* 10,000 items in one timeline lane: virtualisation keeps 60 fps; label collision hides labels under 40 px bar width.
* Missing `endField`: bars are one unit wide, resize disabled.
* Timezone change mid-session (travelling user): rerender on `visibilitychange` if the offset changed.
DEPS: * `tables/query-compiler`, `tables/field-types` (date, relation, number), `tables/grid-view` (left grid cells), `input/drag-drop`, `input/touch-gestures` for pinch zoom.


## PAP-169 [P1 Build M prio2 Backlog] Build gallery, list and form views
key=tables/gallery-list-form milestone=All view types agent=Builder: Nova (Views Engineer); Iris (Component Crafter) on 
blockedBy=['PAP-163'] blocks=[]
GOAL: Ship the three presentation-oriented views: gallery (card grid with cover images), list (dense vertical feed usable on phones and in sidebars) and form (a data-entry view that creates records, optionally public). Together they cover customer-facing directories, feeds and intake forms without custom pages.
SCOPE: In:

* `packages/views/src/views/gallery/`, `views/list/`, `views/form/` with options in `ViewSpec.options`.
* Form runtime and public form route `/f/:token` (token issuance from `tables/view-sharing`; until it lands, forms are internal only).
* Form builder panel (field order, labels, help text, required, conditional visibility, prefill via URL params, submit message, redirect).

Out: payments in forms (`business-core/invoicing` payment links can be embedded later), file upload limits beyond file-storage defaults, multi-page forms (v2).
SPEC(first 1200): * Gallery options `{ coverField?, coverFit: 'cover'|'contain', cardSize: 'sm'|'md'|'lg', cardFields: fieldId[], titleField?, showEmptyFields }`; responsive CSS grid `repeat(auto-fill, minmax(size, 1fr))` with 200/280/360 px card widths; virtualised rows; card click opens the record panel; cover from `attachment` (first image, `variants.md` from file-storage) or a URL field; skeleton cards on load.
* List options `{ titleField, subtitleField?, metaFields: fieldId[], avatarField?, dense }`; rows 56/72 px; grouped headers from `spec.groups`; swipe actions on touch (`input/touch-gestures`) configurable to two actions (e.g. set status, delete); suits sidebars at 320 px.
* Form model: `FormSpec = { fields: { fieldId, label?, help?, required, placeholder?, hiddenWhen?: FilterGroup (over form values), prefillParam? }[], title, description (Markdown), submitLabel, successMessage, redirectUrl?, allowMultiple, honeypot: true, captcha?: 'turnstile' }` stored in `spec.options`.
* Rendering: one field per row using field type `Editor` in form mode; validation on blur and submit via `validateRecord`; error summary at top with links; progress saved to `localStorage` per form id (draft), cleared on
DOD:
* Vitest for form validation, conditional logic, prefill parsing, honeypot and rate limiting.
* Playwright: gallery scroll and open record, list swipe action (touch emulation), form fill with errors then success, public form submission with a token.
* Storybook stories tagged `visual` for the three views and the builder; screenshots at 375, 768, 1024, 1440, 1920 in three themes; public form screenshotted with two tenant brands.
* axe clean; form labels and error associations verified.
* `docs/views/gallery-list-form.md`; CHANGELOG entry; Linear comment with a live public form link on the demo tenant.
EDGE:
* Cover image missing or `failed`: placeholder illustration from `design-system/icons-illustrations`.
* Form with a relation field: public forms render it as a select of records the `form-submitter` principal may read (usually none) or hide it; builder warns.
* Submitting after the form was unpublished: 410 with a friendly page.
* 50 MB attachment on a public form: rejected by file-storage limits with a clear message.
* Duplicate submissions on double-click: idempotency key per draft.
* Right-to-left locale: layout mirrors, list swipe directions flip.
DEPS: * `tables/query-compiler`, `tables/field-types`, `data-layer/file-storage`, `design-system/theming`, `input/touch-gestures`, `input/drag-drop`; `tables/view-sharing` for public tokens.


## PAP-170 [P2 Build M prio2 Backlog] Build map view and chart view (bar, line, pie, number) bound to view aggregations
key=tables/map-chart-views milestone=All view types agent=Builder: Nova (Views Engineer) with Iris (dataviz plugin) on
blockedBy=['PAP-163'] blocks=['PAP-173']
GOAL: Add the two analytic views: a map view plotting records with coordinates on vector tiles, and a chart view (bar, line, area, pie, number/KPI) bound to the compiler's group and aggregate output. Both are the building blocks `tables/dashboard-blocks` arranges, so their props must be data-driven and cross-filter aware from day one.
SCOPE: In:

* `packages/views/src/views/map/` and `views/chart/`, plus a new `geo` field type `{ lat, lng, label? }` registered in `tables/field-types`.
* Chart options `{ chartType: 'bar'|'stackedBar'|'line'|'area'|'pie'|'donut'|'number', xField (group), seriesField?, yAggregate: { fieldId?, fn }, sortBy, limit, colorScheme, showLegend, showDataLabels, goal? }`.
* Map options `{ geoField, labelField?, colorField?, cluster: boolean, fitToData, basemap: 'light'|'dark'|'auto' }`.
* Click-to-filter events emitted as `onFilter(FilterCondition)` for dashboards.

Out: geocoding addresses (a follow-up using an integration connector), choropleths, custom tile hosting, drill-through beyond one level.
SPEC(first 1200): * Chart library: Apache ECharts 5.x imported per-chart (`echarts/core` with only needed renderers) to keep bundle under 250 KB gzip for the chart view; render into a `ResizeObserver`-driven container; theme built from design tokens at runtime (categorical palette from the `dataviz` skill's validated palette mapped onto `--pos-color-*` variables; sequential ramps for stacked series), regenerated on theme change.
* Data: `views.groups` provides x categories and aggregates; two-level grouping (`xField`, `seriesField`) yields series; `limit` caps categories (default 20, remainder bucketed into "Other"); number chart uses `views.query` aggregates with an optional comparison to the previous period when `xField` is a date bucket (`day|week|month|quarter|year` set in `options.bucket`).
* Formatting uses the field type `format` (currency in minor units, percent) for axes and tooltips; tooltips show category, series, value and count; data labels optional.
* Interaction: click a bar/slice emits `onFilter({ fieldId: xField, op: 'is', value })`; active filter highlights the element and dims others; legend toggles series; keyboard: Tab to chart, arrows move focus across categories with an access
DOD:
* Vitest for series shaping, "Other" bucketing, period comparison and bounds filter compilation.
* Playwright: click-to-filter round trip, legend toggle, map cluster zoom, rectangle select; WebGL enabled in the Playwright image.
* Storybook stories for each chart type and the map tagged `visual`; screenshots at 375, 768, 1024, 1440, 1920 in light, dark and high-contrast (palette contrast validated with the dataviz checker).
* Bundle size check in CI: chart chunk under 250 KB gzip, map chunk lazy-loaded.
* `docs/views/map-chart.md`; CHANGELOG entry; Linear comment with demo link.
EDGE:
* 10,000 points on the map: clustering on; above 50,000 the view asks the user to filter first.
* Negative values in a pie chart: refuse with a message and suggest bar.
* Mixed-currency sums: one series per currency, never summed.
* Date bucket with gaps: fill zero buckets so lines do not connect across missing months.
* Browsers without WebGL (some kiosks): map shows a static list with coordinates and an explanation.
* Colour-blind users: patterns/dashes for series in high-contrast theme, legend always includes text.
DEPS: * `tables/query-compiler` (groups, aggregates, bounds filter), `tables/field-types` (geo type), `design-system/tokens` (palette), `design-system/theming` (runtime theme switch), `libraries/data-landscape` (ECharts choice confirmed via ADR).


## PAP-171 [P2 Build L prio2 Backlog] Build a formula engine compatible with common Airtable and Notion functions
key=tables/formula-engine milestone=View sharing, formulas, dashboards agent=Builder: Nova (Views Engineer). Reviewer: Sentinel (Code Rev
blockedBy=['PAP-164'] blocks=[]
GOAL: Build a formula engine so `formula` fields compute values users already know how to write, compatible with the most-used Airtable and Notion functions, with static type checking, an evaluator in TypeScript for editors and previews, and SQL compilation for the subset that can run inside the query compiler so formulas can be filtered, sorted and aggregated server-side.
SCOPE: In:

* `packages/views/src/formula/`: lexer, Pratt parser to AST, type checker, TS evaluator, SQL compiler, function library, error model, editor component with autocomplete and inline diagnostics.
* Function coverage from `docs/views/formula-functions.csv` (`tables/feature-parity-audit`): at least 80 functions across text, number, logical, date, array and record categories, with Notion-style aliases (`prop("Name")`, `dateBetween`, `formatDate`, `empty`).
* Dependency graph for computed fields (formula referencing lookup/rollup/formula) with cycle detection.

Out: cell-level spreadsheet formulas, user-defined functions, formulas referencing other datasets except through relation fields.
SPEC(first 1200): * Grammar: Airtable-style `IF({Status} = "Done", 1, 0)` with `{Field Name}` references, `&` concatenation, `+ - * / %`, comparisons, `AND/OR/NOT` as functions and `&&/||/!` as operators (Notion style), string escapes, comments `//`. Field references resolve by field id at save time (`{Field}` rewritten to `@fld_123` in stored AST) so renames are safe.
* Types: `text | number | boolean | date | array<T> | null | error`; `checkType(ast, fields) => { resultType, diagnostics }`; implicit coercions only number→text in `&` and text→number in arithmetic when parseable; otherwise diagnostics with positions.
* Functions declared via `defineFunction({ name, aliases, params: [{ name, type, variadic? }], returns, ts: impl, sql?: (args) => SQL, pure: true })`; date functions take the actor timezone from context; `NOW()`/`TODAY()` are marked volatile and excluded from SQL indexes.
* Evaluation: `evaluate(ast, record, ctx)` used for editor previews, form conditional logic and client display; results cached per record version.
* SQL: `compile(ast) => SQL | Unsupported`; supported functions cover text, math, logic and most date functions using Postgres equivalents (`date_trunc`, `age`, `to_char` wi
DOD:
* Vitest: parser golden tests (200+ expressions), type checker cases, evaluator vs Airtable-documented examples, SQL compiler parity tests asserting TS and SQL results match on a 1,000-record fixture for every SQL-capable function.
* Fuzz test with `fast-check` for parser crash-freedom.
* Storybook story for the editor tagged `visual`; screenshots at 375, 1024, 1920 in three themes.
* Function reference published to `docs/views/formulas.md` from metadata; coverage row updated in the parity CSV.
* CHANGELOG entry; Linear comment with function coverage count and unsupported-in-SQL list.
EDGE:
* Formula referencing a deleted field: field stays, shows `#REF` with a fix-it action.
* Unicode and emoji in `LEN` and `MID`: count code points, matching Airtable.
* Date arithmetic across DST: use timezone-aware functions; test fixtures cover it.
* Deep nesting (500 nested IFs): parser is iterative or depth-limited to 200 with a clear error.
* Formula producing an array (lookup values): aggregations offered are count/unique/join.
* Timezone of `TODAY()` in a shared public view: tenant timezone, not viewer.
DEPS: * `tables/field-types` (formula type, lookup/rollup), `tables/query-compiler` (integration point for `compile`), `tables/feature-parity-audit` (function inventory).


## PAP-172 [P2 Build M prio2 Backlog] Add saved views, personal vs shared views, public embeds and per-audience defaults
key=tables/view-sharing milestone=View sharing, formulas, dashboards agent=Builder: Nova (Views Engineer). Reviewer: Sentinel (Security
blockedBy=['PAP-59', 'PAP-165'] blocks=[]
GOAL: Make views first-class permissioned objects: personal versus shared views, per-audience default views for each dataset, public read-only links and embeds with expiry and password, view locking, and a views switcher that lists what the actor may see. This is what turns the engine into something customers, staff and partners each experience differently.
SCOPE: In:

* `view_share` table and oRPC procedures `views.list|create|update|duplicate|delete|reorder|share|revoke|setDefault`.
* `<ViewSwitcher />`, `<ShareViewDialog />`, `<ViewSettingsSheet />` in `packages/views/src/sharing/`.
* Public routes `/v/:token` (read-only view) and `/embed/v/:token` (iframe-friendly) in `apps/web`.
* Permission actions `view.read|update|delete|share|lock` wired into `identity/rbac-abac`.

Out: per-field permissions on entity datasets (that lives in the permission engine and specs), comments on public views.
SPEC(first 1200): * `view.visibility`: `personal` (only owner; stored per user), `shared` (workspace members per role policies), `public` (via token). Default new views are `personal`; "Share with workspace" flips to `shared` and requires `view.share`.
* Per-audience defaults: `view_default` table `(tenant_id, dataset_ref, audience_id, view_id)`; `views.resolveDefault(datasetRef, actor)` picks the most specific audience match from `identity/audience-model` segments, else the first shared view, else creates a personal grid. Pages declare `views.default` in `page.spec.yaml` for compile-time defaults.
* `view_share`: `id, view_id, token (32-byte base64url, unique, indexed), kind: 'link'|'embed', password_hash?, expires_at?, allow_export, allowed_fields jsonb (hidden fields stripped server-side), created_by, revoked_at, view_count, last_viewed_at`. Tokens are shown once at creation; rotating creates a new row.
* Public request path: `/v/:token` runs as the `service` principal `public-viewer` with `tenantId` from the share; `views.publicQuery({ token, cursor })` reuses the compiler with `allowed_fields` projection and forces `permissions.canEditRecords = []`; rate limit 120/min per IP and 10k/day per tok
DOD:
* Vitest for default resolution precedence and share validation; integration tests for token, expiry, password, revoked and field stripping cases.
* Permission matrix tests generated via `identity/permission-tests` for the view actions.
* Playwright: create share, open `/v/:token` in a fresh context, verify hidden field absent, revoke and see 410.
* Storybook stories for switcher and share dialog tagged `visual`; screenshots at 375, 768, 1024, 1440, 1920 in three themes; embed page screenshotted at 320 and 1024.
* `docs/views/sharing.md` including a security note; CHANGELOG entry; Linear comment with a live public view link.
EDGE:
* Personal view owner leaves the tenant: personal views are deleted with membership; shared views transfer to the workspace owner.
* Public view on an entity dataset with RLS: `public-viewer` principal has no rows unless an explicit `allow` policy exists; the share dialog warns "This view will show 0 records" using a preview count.
* Token pasted into a browser after expiry: 410 page with tenant branding, no data.
* Two audiences match a user (staff who is also a customer): the more specific segment wins; ties resolve by `position`.
* Embed inside a site not on the allowlist: blank with a CSP violation, documented for tenants.
* Export enabled on a public view: CSV limited to 10k rows and rate-limited.
DEPS: * `tables/grid-view` (first view kind to share), `identity/rbac-abac`, `identity/audience-model`, `data-layer/audit-log`, `design-system/theming` for embed branding, `business-core/entitlements` (public views count as a plan limit).


## PAP-173 [P2 Build L prio2 Backlog] Compose views into dashboard pages with drag-arranged blocks and cross-filters
key=tables/dashboard-blocks milestone=View sharing, formulas, dashboards agent=Builder: Nova (Views Engineer). Reviewer: Sentinel (Visual I
blockedBy=['PAP-155', 'PAP-165', 'PAP-170'] blocks=['PAP-186']
GOAL: Compose views into dashboard pages: a responsive 12-column grid of drag-arranged blocks (any view kind, KPI numbers, text, filter controls) with cross-filtering, so a click on a chart bar filters the grid beside it. This is the "incredible ways to view data on one page" outcome and the surface `business-core/cash-dashboard` and `pm-linear/board-views` build on.
SCOPE: In:

* Tables `dashboard` and `dashboard_block`; oRPC `dashboards.*` and `dashboardBlocks.*`.
* `packages/views/src/dashboard/`: `<Dashboard />`, `<DashboardEditor />`, `<Block />` wrapper, `<FilterBarBlock />`, `<TextBlock />`, `<NumberBlock />`, block picker.
* Cross-filter bus, global date range, dashboard-level parameters, fullscreen block, refresh interval.
* Page spec support: `layout.dashboard: <dashboardId>` in `page.spec.yaml`.

Out: scheduled email snapshots (`collab/notifications` follow-up), per-block permissions beyond inheriting view permissions, dashboard templates marketplace.
SPEC(first 1200): * `dashboard`: `id, tenant_id, workspace_id, name, description, layout jsonb (per breakpoint), params jsonb, visibility, owner_user_id, refresh_seconds?, position`. `dashboard_block`: `id, dashboard_id, kind: 'view'|'number'|'text'|'filter'|'divider', view_id?, spec_override jsonb, title, config jsonb, x, y, w, h, min_w, min_h`.
* Grid: 12 columns, row height 40 px, gap from tokens; breakpoints `lg >= 1280` (12 cols), `md >= 768` (8 cols), `sm < 768` (1 col, blocks stack by `y`); each breakpoint layout stored separately, `sm` auto-derived unless customised. Drag and resize via `input/drag-drop` with 8-direction handles; collision pushes blocks down; keyboard: select block, arrows move by one cell, Shift+arrows resize; announcements.
* Blocks render the referenced view in "embedded" mode (no toolbar, compact header with title, view kind icon, menu: edit, duplicate, fullscreen, export, remove) using `spec_override` merged over the view spec (so one saved view can appear twice with different filters).
* Cross-filter bus: `DashboardFilterContext` holds `{ global: FilterGroup, byBlock: Record<blockId, FilterCondition[]> }`; views emit `onFilter` (charts, map, kanban column header, grid 
DOD:
* Vitest for layout collision, breakpoint derivation, cross-filter merge, URL param parsing.
* Playwright: add blocks, drag, resize, cross-filter from chart to grid, fullscreen, keyboard move; screenshots of a 6-block demo dashboard at 375, 768, 1024, 1440, 1920 in three themes; video replay of cross-filtering.
* Performance trace attached showing the 2 s budget.
* Permission tests: viewer sees blocks only for views they may read (others render "No access" tile).
* `docs/views/dashboards.md`; CHANGELOG entry; Linear comment with the demo dashboard link.
EDGE:
* Referenced view deleted: block shows a "View removed" tile with replace action, dashboard still loads.
* Cross-filter on a field with different types across datasets (text vs select): mapping validated; mismatch ignored with a tooltip.
* 40 blocks: lazy loading and a warning at 30 that dashboards this large hurt performance.
* Two filter blocks controlling the same field: last change wins, both display the current value.
* Print at A4 with a map block: rendered as a static image; WebGL unavailable in print falls back to list.
* Block owner loses access to the view: block renders "No access" for them, others unaffected.
DEPS: * `tables/map-chart-views` (chart and map blocks), `tables/grid-view`, `input/drag-drop`, `tables/view-sharing` (dashboard visibility mirrors view visibility), `spec-builder/layout-codegen` for the page spec hook.


## PAP-174 [P2 Build L prio2 Backlog] Build table automations: triggers (record change, schedule, form, inbound webhook), filter-tree conditions and actions (update record, notify, outbound webhook, connector call, create Linear issue) with a run log
key=tables/automations milestone=View sharing, formulas, dashboards agent=Built by Nova (Views Engineer) with Forge for the LISTEN/NOT
blockedBy=['PAP-121', 'PAP-43', 'PAP-166'] blocks=[]
GOAL: Justin asked for a table system with every feature Airtable, Notion and ClickUp have. All three ship automations, and `tables/feature-parity-audit` will list them, but no issue builds them: when a record enters a view, on a schedule, when a form is submitted or a webhook arrives, run conditions and actions without code. Automations also give every business template a way to encode its own workflow (send the reminder, move the deal, post to Slack), which is what "adapts to every type of business" needs in practice.
SCOPE: In:

* Schema `packages/views/src/automations/schema.ts`: `automation` (`tenant_id`, `name`, `enabled`, `trigger jsonb`, `conditions jsonb` (the filter tree from `tables/view-model-spec`), `actions jsonb[]`, `owner_id`, `run_limit_per_day`), `automation_run` (`status`, `trigger_payload`, `steps jsonb`, `error`, `duration_ms`, `cost_units`).
* Triggers: `record.created|updated|deleted` on a table, `record.entersView(viewId)` (evaluated by diffing view membership through `tables/query-compiler`), `schedule` (cron in tenant timezone), `form.submitted` (`tables/gallery-list-form`), `webhook.received` (per-automation URL with HMAC secret), `button.clicked` (a button field type added to `tables/field-types`).
* Conditions: reuse the filter builder UI and compiler; template variables `{{record.field}}`, `{{trigger.*}}`, `{{now}}` with a small expression language shared with `tables/formula-engi
SPEC(first 1200): * Triggers on record changes come from Postgres `LISTEN/NOTIFY` emitted by the audit triggers in `data-layer/audit-log`, debounced 500 ms per record so bulk edits fire once per record.
* Loop protection: a run that updates a record which would re-trigger the same automation is allowed once, then stopped with a `loop_guard` status; automations can opt into chaining depth up to 3.
* Every action declares a scope class (`read`, `write`, `destructive`) per `libraries/mcp-servers`; destructive actions require explicit enablement by a tenant admin and are excluded from templates.
* Run log retention 90 days; runs and steps visible in `data-layer/audit-log` with `actor_kind = 'automation'`.
* Costed: `agent.run` and `connector.call` record units for `pm-linear/credit-metering` style per-tenant budgets.
* Templates: five starter automations shipped with `migration/business-templates` (appointment reminder, deal stage notification, overdue invoice nudge, new lead assignment, weekly digest).
DOD:
* Parity matrix in `docs/tables/automations.md` against Airtable, Notion and ClickUp trigger and action lists from `tables/feature-parity-audit`, with gaps marked.
* Playwright flow: create an automation "when status becomes Done, notify owner and post webhook", test-run, real run from a grid edit, run log shows both steps (screenshots at 1280 and 375).
* Schedule trigger fires in tenant timezone across a DST boundary (unit test with fixed clocks).
* Loop guard test; circuit breaker test; daily limit test.
* Webhook receiver rejects unsigned and replayed payloads (test).
* Accessibility: builder operable by keyboard alone (`input/screen-reader` sub-check).
* `CHANGELOG.md`, page specs merged, Linear comment with demo video.
EDGE:
* Trigger table deleted: automations referencing it disabled with a visible reason.
* Notification target user removed from tenant: `notify` step skipped with a warning, run continues.
* Outbound webhook target returns 5xx for an hour: retry schedule from the jobs package, then failed step with resend button.
* Thousands of records imported at once (`migration/import-framework`) matching a `record.created` trigger: imports run with `automations: paused` by default and a post-import choice to run for imported rows.
* Time zone missing on tenant: schedules default to UTC with a banner until set.
* Offline client edits synced later (`realtime/offline-queue`): triggers fire on server apply time, not on client edit time; the run log shows both timestamps.
DEPS: `tables/filter-sort-group-ui` (condition editor and filter tree), `data-layer/jobs-queue` (runtime), `spec-builder/integrations-section` (connector registry). Soft: `collab/notifications`, `data-layer/audit-log`, `tables/formula-engine`, `tables/gallery-list-form`, `input/drag-drop`, `agents/handoffs`. Consumed by `migration/business-templates`, `growth/segments`, `business-core/invoicing` (overdue nudges).
