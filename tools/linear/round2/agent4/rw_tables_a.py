# Rewritten specs for tables PAP-161..PAP-167. {{key}} references resolve to child identifiers when created.
SPECS = {}
def add(k, **s): SPECS[k] = s

add("PAP-161",
Goal="""Define the one schema every PaperOS view renders from: `ViewSpec`, a strict superset of what Airtable, Notion and ClickUp views can express (data source, fields, filters, sorts, groups, aggregations, permissions, sharing). The compiler (PAP-163), every view kind (PAP-165 to PAP-170), dashboards (PAP-173) and the spec builder consume this type unchanged, so it ships complete before any view code is written.""",
Scope="""In: `packages/views/src/model/` (Zod schemas, TypeScript types, JSON Schema export, `migrateViewSpec`); Drizzle tables `dataset`, `field`, `record`, `view` in `packages/views/src/schema.ts`; `registerDataset()` registry so Drizzle entities appear as datasets; `docs/views/view-model.md` with one worked example per view kind and an Airtable/Notion/ClickUp equivalence column.

Out: query execution (PAP-163), field renderers (PAP-164), share tokens (PAP-172), the filter grammar itself (PAP-279 owns `FilterTree`; this issue imports it).""",
Spec="""* `DatasetRef = { kind: 'entity', key } | { kind: 'custom', datasetId }`. Entities register with `registerDataset({ key, table, fields: FieldDef[], defaultSort, rls: true })`; custom datasets keep `FieldDef[]` in `field` and rows in `record.data jsonb` (max 500 fields, 100 KB per row).
* `FieldDef = { id, key, name, type: FieldType, options, required, unique, hidden, computed }`; `FieldType` is re-exported from PAP-164 (17 types plus `geo` and `button` added later).
* `ViewSpec = { id, version, datasetRef, kind (10 kinds), name, fields: { fieldId, width?, visible, order, frozen? }[], filter: FilterTree, sorts (max 5), groups (max 3, `expandMulti`), aggregations, rowHeight, options (kind-specific, each a named Zod schema), search?, visibility, ownerUserId, permissions: { canEditRecords: AudienceId[], canEditView: AudienceId[] }, locked }`.
* `filter` is `FilterTree` from `packages/core/filter` (PAP-279), including `{ ref: 'currentUser' }` and relative dates; view-specific operators are contributed through that package's extension hook, not forked.
* `view` table: `id, tenant_id, workspace_id, dataset_ref jsonb, kind, name, spec jsonb, owner_user_id, visibility, position (fractional index), created_at, updated_at, deleted_at`; index `(tenant_id, dataset_ref)`; RLS via PAP-34.
* `viewSpecSchema` is strict; `migrateViewSpec(old)` applies an ordered migration list keyed by `version`.
* `packages/views/schema/view.schema.json` exported for `page.spec.yaml` inline views (PAP-119).""",
Contract="""Provides: `ViewSpec`, `FieldDef`, `DatasetRef`, `ViewKind`, `AggregateFn`, `viewSpecSchema`, `migrateViewSpec`, `registerDataset`, `getDataset(ref)`, tables `dataset|field|record|view`, JSON Schema file. Consumes: `FilterTree` and `AudienceId` (PAP-279, PAP-62), `tenant|workspace|user` FKs (PAP-33), RLS helpers (PAP-34). Events: none. API: none (CRUD arrives with PAP-172).""",
DoD="""* Zod schemas, types and JSON Schema committed; `pnpm --filter views test` green.
* Migration for the four tables with RLS policies; cross-tenant harness green.
* `docs/views/view-model.md` documents every property with the equivalence column and one fixture per kind under `packages/views/fixtures/`.
* `memberships` entity exposed as a dataset in a test.
* ADR `docs/adr/00xx-view-model.md`, CHANGELOG entry, Linear comment linking the docs page.""",
Test="""* Unit: parse and strict-mode rejection for each kind fixture; `migrateViewSpec` v1 to v2 fixture; nested filter depth 6 rejected; 501 fields rejected; duplicate slugs rejected.
* Integration (PGlite): migration applies and rolls back; RLS harness `expectTenantIsolation('view')`; registry test reads `memberships` rows through `getDataset`.
* Contract: JSON Schema validates all fixtures with `ajv`; snapshot of the schema file guards accidental breaking changes.
* Visual: none (no UI). Docs build renders the Mermaid ER diagram.""",
Demo="""Reviewer runs `pnpm --filter views test` (green in under 30 s), opens `docs/views/view-model.md` on Pages, then runs `pnpm tsx packages/views/scripts/print-spec.ts fixtures/kanban.view.json` which prints the parsed spec and its JSON Schema validation result. Under two minutes.""",
Edge="""* Filter references a deleted field: spec stays valid, condition flagged `orphaned` and skipped at compile.
* Group on multi-select: default combination semantics, `expandMulti` for one row per value.
* RLS entity dataset: `permissions` only narrows, never widens.
* Two views with the same name: allowed, slugs unique.
* Spec written by an older client: `version` lower than current triggers migration on read, never on write.""",
Deps="""PAP-33 (hard), PAP-34 (hard), PAP-279 filter grammar (hard for the `filter` type; import the draft if not merged), PAP-162 in parallel for the equivalence column. Blocks PAP-163, PAP-164, PAP-207.""",
Agent="""Builder: Quill (Page Spec Writer) with Nova (Views Engineer) pairing on the Zod model. Reviewer: Sentinel (spec-conformance) and Forge (Schema Wright) on the migration.""",
Size="""M: modelling and documentation, exhaustive because every downstream issue depends on it.""")

add("PAP-162",
Goal="""Turn "every view feature Airtable, Notion and ClickUp have" into a checkable parity list across Airtable, Notion, ClickUp, Baserow and NocoDB, mapped row by row to `tables/*` issues, plus the formula function inventory PAP-171 implements against. The CSV becomes the coverage tracker the project reports from.""",
Scope="""In: `docs/views/parity.md`, `docs/views/parity.csv`, `docs/views/formula-functions.csv`, coverage script `pnpm --filter views parity:report`, a "Proposed issues" section for uncovered features.

Out: implementing anything; competitor screenshots (link public docs).""",
Spec="""* Sources: public docs and changelogs, plus Baserow and NocoDB repos for view and field enums; every row cites a URL and access date.
* CSV columns: `id, category, feature, airtable, notion, clickup, baserow, nocodb, paperos_issue, paperos_status (planned|in_progress|done|wontdo), notes, source`; product cells `yes|partial|no|paid`.
* Categories (minimum 25): view types; field types; filter operators per type; sorting; grouping; aggregations; density; column ops; record expansion; inline and bulk edit; keyboard; kanban; calendar/timeline/Gantt; gallery/list; forms; map; charts; formulas; lookups/rollups; sharing; permissions; dashboards; import/export; API; automations (PAP-174); record history and trash ({{gap/tables/bulk-trash}}, {{gap/tables/record-detail}}); schema editing ({{gap/tables/schema-editor}}).
* 250 to 400 rows; `paperos_issue` must be a PAP identifier or `gap`.
* `parity-report.ts` (`csv-parse` 5.x) validates rows with Zod, fails on unknown identifiers (reads `linear-ids.json` or a static list), prints coverage per product and per category.
* `formula-functions.csv`: `name, airtable_name, notion_name, category, signature, paperos_status`; 80 or more functions.""",
Contract="""Provides: `parity.csv` schema and `parity:report` exit code consumed by Gate 1 docs checks (PAP-78); `formula-functions.csv` consumed by PAP-171 `defineFunction` coverage tests; the "Proposed issues" list consumed by Atlas. Consumes: issue identifiers from Linear. No code exports.""",
DoD="""* Both CSVs and `parity.md` committed; report prints coverage per product; at least 250 rows with sources.
* Every `tables/*` issue referenced by at least one row; gaps listed with one-line acceptance criteria.
* `parity.md` linked from `docs/views/view-model.md`; report wired into Gate 1 as a docs check.
* CHANGELOG (docs) entry; Linear comment with coverage percentages and top ten gaps.""",
Test="""* Unit: Zod row schema rejects a bad status, an unknown identifier and a missing source; coverage maths on a 10-row fixture.
* Integration: `pnpm parity:report` runs in CI and fails when a referenced issue key is unknown.
* E2E and visual: none (research deliverable).""",
Demo="""Reviewer runs `pnpm --filter views parity:report`, reads the coverage table (per product, per category), opens `parity.md` and spot-checks three rows' source links. Under two minutes.""",
Edge="""* Paid-tier features recorded as `paid`, not `yes`.
* Same idea under different names: one row with aliases in notes.
* Docs change mid-audit: access date in `source`.
* Deliberately declined features (`wontdo`) link the ADR.
* Baserow/NocoDB-only features still listed; they are often cheap wins.""",
Deps="""None; starts now. Feeds PAP-161 (equivalence column), PAP-171 (function inventory) and PAP-174 (trigger and action lists). Cross-link, do not duplicate, PAP-213 and PAP-214.""",
Agent="""Builder: Scout (Library Evaluator). Reviewer: Nova (Views Engineer) for accuracy, Quill for the docs.""",
Size="""M: bounded research; time-box one session plus one revision.""")

add("PAP-163",
Goal="""Turn any `ViewSpec` into an RLS-respecting Postgres query and, where eligible, an Electric shape, so every view kind renders server-paginated rows, groups and aggregates without writing SQL. Umbrella for three children; this issue is Done when all three are Done and the integration bench below passes.""",
Scope="""Children (M each, same milestone, Backlog):

* {{tables/compiler/core}} Compiler core: dataset resolution, per-type filter ops, sorts and signed keyset cursors.
* {{tables/compiler/groups-shapes}} Groups, aggregates and Electric shape eligibility.
* {{tables/compiler/api-hook-bench}} oRPC procedures, `useViewQuery` hook and the 100k-row benchmark.

Out: filter UI (PAP-166), formula evaluation (PAP-171; formula fields opaque until then), full-text ranking (PAP-39).""",
Spec="""Decisions binding all children:

* `compileView(spec, ctx: { actor, tenantId, dataset, cursor?, limit, groupPath? }) => { rows: SQL, count: SQL, groups?: SQL, aggregates?: SQL, shape?: ShapeDef }` using Drizzle `sql` fragments; all literals bound, never concatenated.
* Custom datasets compile `record.data -> 'key'` with casts from the field type; expression indexes created on demand by `views.ensureIndex` (cap 10 per dataset); GIN on `data`.
* Filters compile through the shared evaluator of PAP-279 with per-type op modules in `compiler/ops/<type>.ts`; relations to `EXISTS`; lookups and rollups to lateral joins.
* Keyset cursors: base64url JSON of last sort values plus `id`, HMAC-signed; `limit` max 200, default 50.
* `toPredicate(actor, '<entity>.list')` from PAP-228 ANDed into every query; RLS is the backstop.
* Shapes only for flat AND of `is|isAnyOf|isEmpty` on indexed columns with no groups (PAP-270 registry).""",
Contract="""Provides: `compileView`, `compileFilter`, `compileSort`, `compileGroups`, `compileAggregates`, `ShapeDef`, procedures `views.query|count|groups|distinct`, hook `useViewQuery(spec, { pageSize }) => { pages, fetchNextPage, groups, aggregates, isStale }`, error codes `CURSOR_INVALID`, `CURSOR_STALE`. Consumes: `ViewSpec` (PAP-161), `FilterTree` evaluators (PAP-279), `toPredicate` (PAP-228), `tenantProcedure` and error mapping (PAP-267, PAP-268), shape registry (PAP-270), field casts (PAP-164). Consumed by every view kind, PAP-183 reports, PAP-194 rollups, PAP-195 segments.""",
DoD="""* All three children Done.
* Integration bench: 100k-row seed, filtered plus sorted plus paginated query p95 under 150 ms in CI (`vitest bench`), `EXPLAIN` shows index use, no sequential scan on `record`.
* Golden SQL snapshots for the ten fixture views; cross-tenant harness extended with view queries.
* `docs/views/query-compiler.md` (pipeline, cursor format, shape eligibility); CHANGELOG; Linear comment with the benchmark table.""",
Test="""Umbrella integration test `packages/views/test/compiler.e2e.test.ts`: seed 100k rows across an entity and a custom dataset; run each fixture view through `views.query`, `views.groups` (3 levels) and `views.count`; assert row counts against an in-memory oracle from PAP-279's evaluator; tamper a cursor and expect `CURSOR_INVALID`; run as two tenants and assert zero leakage; record p95 timings. Visual: none.""",
Demo="""Reviewer runs `pnpm --filter views bench compiler` and sees the p95 table, then `pnpm tsx scripts/explain-view.ts fixtures/grid.view.json` printing generated SQL and the `EXPLAIN` plan with the index scan highlighted. Under two minutes.""",
Edge="""* All-null sort field: `nullsLast` honoured, cursor handles null boundaries.
* Group key with 10k distinct values: `views.groups` paginates at 100.
* Field type changed after a cursor was issued: `CURSOR_STALE`, client restarts.
* Currency `sum` across currencies returns a per-currency map.
* Actor and tenant timezones differ for `today`: actor wins, documented.""",
Deps="""PAP-161 (hard), PAP-35 children (hard), PAP-59 via PAP-228 (hard), PAP-279 (hard), PAP-36 children (soft: shapes optional), PAP-164 (casts, either order). Blocks PAP-165, PAP-167, PAP-168, PAP-169, PAP-170, PAP-194, PAP-195.""",
Agent="""Builder: Nova (Views Engineer). Reviewer: Sentinel (Security Auditor for injection and cursor forgery), Forge (Schema Wright) for indexes.""",
Size="""L, split into three M children; the umbrella carries only the integration bench.""")

add("PAP-164",
Goal="""Implement the field type system: for each of the 17 types one definition owning validation, parsing, formatting, cell renderer, editor, filter operators, sort and group behaviour, aggregations and storage casts. Views, forms, imports and the spec builder look behaviour up here. Umbrella for three children.""",
Scope="""Children (M each, same milestone, Backlog):

* {{tables/fields/framework-primitives}} `defineFieldType`, registry and primitive types: text, longText, number, currency, percent, date, checkbox, rating, url, email, phone.
* {{tables/fields/choice-people-attachment}} select, multiSelect, user, attachment with cell-registry integration and `FieldSettingsPanel`.
* {{tables/fields/relational-computed}} relation, lookup, rollup, formula storage type and `convertFieldType` with lossiness report.

Out: formula evaluation (PAP-171), import inference (PAP-200), `geo` (PAP-170), `button` (PAP-174), the in-app schema editor ({{gap/tables/schema-editor}}).""",
Spec="""Decisions binding all children:

* `defineFieldType<TOptions, TValue>({ type, label, icon, optionsSchema, valueSchema, defaultOptions, parse(input, options, locale), format(value, options, locale), sql: { cast, jsonExtract }, filterOps, sortable, groupable, aggregations, Cell, Editor, OptionsEditor, exampleValues })`.
* Storage in `record.data[key]`: `date` ISO 8601 with `includeTime` and `timezone: 'utc'|'local'`; `currency` `{ amountMinor, currency }` matching `Money` (PAP-27); `relation`, `attachment`, `user` are id arrays; `select` stores option id with `{ id, name, color }` options; `rating` integer 0..max (10).
* `validateRecord(dataset, data)` runs server-side in `records.create|update` and client-side in editors; errors `VALIDATION` with `{ fieldKey, message }[]`.
* Editor props `{ value, onChange, onCommit, onCancel, autoFocus, field }`; Enter or blur commits, Escape cancels; relation and user editors use Combobox (PAP-238), date editor uses DatePicker (PAP-233).
* `libphonenumber-js` 1.x for phone, `new URL()` for url, Zod RFC 5322 for email.""",
Contract="""Provides: `fieldTypes` map, `FieldType` union (imported by PAP-161), `defineFieldType`, `validateRecord`, `convertFieldType(field, newType) => { lossy, sampleLosses }`, `FieldSettingsPanel`, cell and editor components registered in the PAP-71 cell registry. Consumes: `Money` and `Truncate` (PAP-71, PAP-27), Combobox and DatePicker (PAP-238, PAP-233), `files.*` (PAP-37), `user` (PAP-33). Consumed by PAP-165 to PAP-170, PAP-199 mapping UI, PAP-119 data section.""",
DoD="""* All three children Done.
* Integration: a custom dataset with every type round-trips create, edit and filter through `views.query` for each `filterOp` the type declares.
* Storybook stories for every Cell and Editor at three densities; screenshots at 375, 1024, 1920 in light, dark, high-contrast; axe clean.
* `docs/views/field-types.md` with the conversion matrix; CHANGELOG; Linear comment with Storybook link.""",
Test="""Umbrella test `fields.e2e.test.ts`: seed one record per example value for all 17 types; for each type and each declared `filterOp` run the compiler and assert the in-memory `parse`/`format` oracle agrees; `fast-check` property test that `parse(format(v)) == v` for every type and locale `en`, `de`, `ar`; Playwright keyboard-only commit and cancel on each editor; visual matrix as above.""",
Demo="""Reviewer opens Storybook `fields/all-types` showing every Cell beside its Editor, edits a currency cell and a relation cell with the keyboard, then opens `fields/convert` where changing number to text shows the lossiness report. Under two minutes.""",
Edge="""* Per-row versus fixed currency: both supported, aggregations per currency.
* Date without time across DST: calendar date, not instant.
* Relation to an unreadable record: "Restricted" chip.
* Deleted select option: value kept, grey "Unknown option", filters still match by id.
* Pasting `1.234,50` into a number: tenant-locale parse with preview.""",
Deps="""PAP-161 (hard), PAP-71 (hard, cell registry), PAP-67 children (hard), PAP-233 (hard for date editor), PAP-37 (attachment child only), PAP-33. Blocks PAP-165, PAP-171, PAP-199.""",
Agent="""Builder: Nova (Views Engineer) with Iris (Component Crafter) on editors. Reviewer: Sentinel (Code Reviewer, Visual Inspector).""",
Size="""L, split into three M children.""")

add("PAP-165",
Goal="""Build the workhorse grid view: virtualised, keyboard-first, inline-editable, with column resize, reorder, freeze, hide, density, grouping headers and aggregate footers, rendering any dataset through the compiler and field types, as fast as Airtable at 100k rows. Umbrella for three children.""",
Scope="""Children (M each, same milestone, Backlog):

* {{tables/grid/core}} Grid core: row and column virtualisation, `useViewQuery` binding, selection model, keyboard reducer, `role="grid"` semantics.
* {{tables/grid/editing-clipboard-bulk}} Inline editing with optimistic commit, TSV clipboard in chunks, bulk actions bar.
* {{tables/grid/columns-groups-panel}} Column operations, grouping headers, aggregate footer, `RecordPanel`.

Out: filter, sort and group builders (PAP-166), sharing (PAP-172), formula editing (PAP-171), trash and restore ({{gap/tables/bulk-trash}}), record detail routes ({{gap/tables/record-detail}}).""",
Spec="""Decisions binding all children:

* `@tanstack/react-table` 8.x, `@tanstack/react-virtual` 3.x; column and row reorder through `SortableList` (PAP-155) when merged, native pointer fallback otherwise; `fractional-indexing` for `sort_key`.
* Data via `useViewQuery`, page 100, prefetch within 30 rows of the end; collapsed groups persisted in `spec.groups[].collapsed`.
* Row heights 32, 40, 56, 88 px; widths 60 to 1200 px persisted through `onSpecChange` debounced 500 ms; frozen total capped at 60 percent of viewport.
* Edit opens on Enter, F2, double-click or a printable key; commit through `mutate(orpc.records.update, { optimistic })` (PAP-272), revert and toast on rejection.
* Commands `grid.*` registered in PAP-151; roving tabindex per PAP-153; `aria-rowindex`, `aria-colindex`, `aria-activedescendant`.
* Budgets: first paint under 300 ms for 100 rows; 60 fps scrolling with 30 columns at 1920 px.""",
Contract="""Provides: `<GridView spec onSpecChange datasetRef embedded? onFilter? />`, `<RecordPanel recordId />`, hooks `useGridSelection`, `useGridKeyboard`, `useClipboardRange`, commands `grid.*`, `GridColumnMenu` slot for PAP-166 and the schema editor. Consumes: `useViewQuery` (PAP-163), `fieldTypes` (PAP-164), `EmptyState` and cells (PAP-71), `SortableList` (PAP-155), `defineCommand` (PAP-151), `mutate` (PAP-272), comments slot (PAP-131), `AuditTrail` (PAP-38). Consumed by PAP-166, PAP-172, PAP-173, PAP-179 journal, PAP-183 reports, PAP-189 contacts, PAP-135.""",
DoD="""* All three children Done.
* Storybook `views/grid` with 10k rows; screenshots at 375, 768, 1024, 1440, 1920 in three themes and four densities; axe clean; NVDA and VoiceOver spot check.
* Performance trace attached meeting both budgets.
* `docs/views/grid.md` with keyboard map and extension points; CHANGELOG; Linear comment with demo link and video replay.""",
Test="""Umbrella Playwright `grid.e2e.spec.ts` against the 100k seed: scroll to row 50,000 in under 2 s; edit a cell, reload, value persists; paste a 500-row TSV range and see chunked progress; resize, reorder, freeze a column and verify `spec.fields` after reload; group by status and collapse a group; open `RecordPanel` and edit from it; keyboard-only run of the same flow. Profiler assertion for 60 fps.""",
Demo="""Reviewer opens the Pages demo `/demo/grid`, types into a cell and presses Enter, drags a column header, freezes it, pastes three rows from a spreadsheet and expands a row into the side panel. Under two minutes.""",
Edge="""* 375 px: first column frozen, header menu becomes a bottom sheet.
* Row deleted by another user mid-edit: editor closes, toast, focus to next row (PAP-144).
* 5,000-row paste: batches of 200 with cancel.
* Null group header "(empty)" sorts last.
* Denied `update`: cells render, editors never open.""",
Deps="""PAP-163 (hard), PAP-164 (hard), PAP-71 (hard), PAP-151 (hard), PAP-155 (soft, fallback reorder), PAP-36 children (soft, optimistic path). Blocks PAP-166, PAP-172, PAP-173, PAP-183, PAP-135, PAP-189.""",
Agent="""Builder: Nova (Views Engineer). Reviewer: Sentinel (Code Reviewer, Visual Inspector, Edge Case Hunter).""",
Size="""L, split into three M children.""")

add("PAP-166",
Goal="""Give every view Airtable-class controls: a filter builder with nested AND/OR groups and per-type operators, multi-sort, three-level grouping with per-group aggregates, quick-filter chips and a toolbar that hosts them. The panels edit `ViewSpec`; everything re-renders through the compiler.""",
Scope="""In: `packages/views/src/controls/`: `ViewToolbar`, `FilterBuilder`, `SortEditor`, `GroupEditor`, `AggregateFooter`, `FieldVisibilityMenu`, `SearchBox`; relative date and dynamic value editors; temporary URL-held filters for users without `view.update`.

Out: saved-view management (PAP-172), grammar definition (PAP-279), formula fields beyond their result type.""",
Spec="""* Toolbar: left `[Views] [Search]`, right `[Fields] [Filter n] [Sort n] [Group n] [Row height] [Share]`; under 768 px collapses to one "Options" bottom sheet with tabs.
* `FilterBuilder` renders `FilterTree` rows `[field] [op] [value]`; groups indent with their own and/or toggle; depth max 5; operators from `fieldTypes[type].filterOps`; relative anchors `today, yesterday, tomorrow, oneWeekAgo, oneWeekFromNow, oneMonthAgo, oneMonthFromNow, startOfWeek, startOfMonth, exactDate`; drag reorder via PAP-155.
* Edits apply after 300 ms debounce; toolbar shows "n of N records" from `views.count`.
* `SortEditor` max 5 sorts with nulls-last toggle and manual order for custom datasets; `GroupEditor` max 3 levels with `expandMulti` and per-level aggregate.
* Quick filters: fields with `options.quickFilter` render as chips building `isAnyOf`; overflow into "+n".
* Search: `spec.search` over visible text fields, `ILIKE` until PAP-39 lands, then `tsvector`.
* Temporary filters in `?f=&s=&g=` compressed with `lz-string`; "Save to view" gated by permission.
* Commands `view.filter.add`, `view.sort.add`, `view.group.add`, `view.search.focus`.""",
Contract="""Provides: the seven components above, `useTempViewState()` for URL-held filters, `FilterBuilder` reused standalone by PAP-195 segments and PAP-174 conditions (`<FilterBuilder tree onChange fields extraOperators? />`). Consumes: `FilterTree` types and `describe()` sentence renderer (PAP-279), `filterOps` and editors (PAP-164), `views.count` (PAP-163), Popover, Sheet, Combobox (PAP-237, PAP-238), `SortableList` (PAP-155), commands (PAP-151). Host: `GridView` toolbar slot (PAP-165).""",
DoD="""* Vitest for reducers and URL round trip; Playwright flows below green.
* Storybook stories per control; screenshots at 375, 768, 1024, 1440, 1920 in three themes; axe clean; focus returns to the toolbar button on close.
* `docs/views/controls.md` with the operator table per type; CHANGELOG; Linear comment with demo and replay.""",
Test="""* Unit: add, remove, move, nest conditions; depth 6 rejected; duplicate group field blocked; `lz-string` round trip; sentence renderer snapshots.
* Integration: builder output compiles through PAP-163 for every operator of every type against a 1k-row seed and matches the in-memory oracle.
* E2E: build a three-level nested filter, reorder two sorts, group by two fields, change an aggregate, verify grid counts; repeat keyboard-only; 375 px bottom-sheet variant.
* Visual: the five widths, three themes, panels open and closed.""",
Demo="""Reviewer opens the grid demo, adds "Status is any of Open, Blocked" and a nested "or" group, sorts by two fields, groups by owner, switches the footer aggregate to sum, and watches the count badge update. Under two minutes.""",
Edge="""* Field deleted while the panel is open: row shows "field deleted" with remove.
* Contradictory filters allowed, count 0.
* 40 chips overflow into a popover.
* URL over 2 KB falls back to session storage with a warning.
* Screen reader announces the sentence form on operator change.""",
Deps="""PAP-165 (hard), PAP-163, PAP-164, PAP-279 (hard), PAP-155 (soft), PAP-67 children. Blocks PAP-174, PAP-195.""",
Agent="""Builder: Nova (Views Engineer). Reviewer: Sentinel (Visual Inspector, Edge Case Hunter); Iris on control styling.""",
Size="""M: UI over existing primitives; one to two sessions.""")

add("PAP-167",
Goal="""Build the kanban view so any dataset with a select, status or single-relation field works as a board: columns per group value, optional swimlanes, WIP limits, accessible drag-and-drop, card templates and inline creation. PM boards (PAP-102) and CRM pipelines (PAP-189) are the first consumers.""",
Scope="""In: `packages/views/src/views/kanban/`: `KanbanView`, `KanbanColumn`, `KanbanCard`, `CardTemplateEditor`; options `{ groupField, swimlaneField?, wipLimits, cardFields, coverField?, colorField?, hideEmptyColumns, collapsedColumns, columnOrder? }`; column aggregates (count plus one sum).

Out: time views (PAP-168), automation on move (PAP-174), swimlane by multi-relation.""",
Spec="""* Group field must be `select`, `user` or relation with `limitOne`. Columns from `views.groups` level 1; cards per column via `views.query` with `groupPath`, page 50, "Load more"; each column virtualised.
* Swimlanes: lane per `swimlaneField` value, each cell paginated independently.
* Drop writes `{ [groupField]: optionId }` plus `sort_key` via `between()` for custom datasets; entity datasets without manual order change only the group value and show a "sorted by X" hint; optimistic with revert toast.
* WIP: header `n / limit`, warning at limit, danger above; `canDrop` returns `{ reason }` unless Alt override (audited).
* Card: title, up to six `cardFields` at compact density, cover, colour bar, avatar stack, comment badge slot (PAP-131).
* Inline "+ New" creates with the column value; Enter keeps adding.
* Keyboard: Space pick up, arrows move, Space drop, Escape cancel; `LiveAnnouncer`; commands `kanban.*`.
* Under 768 px: horizontally snapping single-column panes with a pager; under 1024 px max three card fields.""",
Contract="""Provides: `<KanbanView spec onSpecChange datasetRef onMove? onFilter? />`, `KanbanCard` template API, `onMove(recordId, from, to, index)` hook used by PAP-189 for won/lost dialogs and PAP-102 for Linear sync, `canDrop` extension. Consumes: `views.groups|query` (PAP-163), cells (PAP-164), `KanbanDnd` (PAP-155), `AvatarStack`, `Badge` (PAP-71), `LiveAnnouncer` (PAP-153), record sync (PAP-143, optional).""",
DoD="""* Vitest for move reducer, WIP evaluation, template config; Playwright flows below on a 2,000-record, eight-column seed.
* Storybook story; screenshots at 375, 768, 1024, 1440, 1920 in three themes; video replay of a drag at each width; 60 fps drag assertion.
* `docs/views/kanban.md`; CHANGELOG; Linear comment with demo link.""",
Test="""* Unit: move reducer including same-column reorder; WIP maths; Alt override flag; template config validation.
* Integration: `onMove` writes group value and `sort_key`; two clients moving the same card converge (PAP-143 harness).
* E2E: pointer drag between columns, keyboard move, WIP block with reason, inline add, swimlane collapse, 375 px pager; axe run per state.
* Visual: matrix above plus collapsed columns and empty "(no value)" column.""",
Demo="""Reviewer opens `/demo/kanban`, drags a card into a column at its WIP limit and reads the refusal, holds Alt to override, adds a card inline, then uses keyboard only to move another card. Under two minutes.""",
Edge="""* 200 options: columns virtualised, first 30 shown with "Show all".
* Concurrent moves: last write wins, loser animates to the real column.
* Drop into a column the user cannot write: refused with `explain()` reason.
* Option deleted while open: cards move to "(no value)" after refetch, toast.
* Offline: moves queue in the outbox with a pending badge.""",
Deps="""PAP-163 (hard), PAP-155 (hard for cross-container drag), PAP-164, PAP-71, PAP-143 (soft). Blocks PAP-102, PAP-189.""",
Agent="""Builder: Nova (Views Engineer). Reviewer: Sentinel (Visual Inspector, Edge Case Hunter); Iris on card design.""",
Size="""M: drag infrastructure exists; the work is board semantics, per-column pagination and polish.""")
