# Children for tables L issues and the three tables gap issues.
P = "tables"
CHILDREN = {}   # parent -> [child]
GAPS = []
def child(parent, key, title, type_, size, **s):
    CHILDREN.setdefault(parent, []).append(dict(key=key, title=title, type=type_, size=size, sections=dict(s, Size=size + ": " + s.pop("SizeNote", "one session."))))
def gap(key, title, phase, type_, priority, surfaces, milestone, blockedBy, blocks, state="Backlog", **s):
    GAPS.append(dict(key=key, title=title, phase=phase, type=type_, priority=priority, surfaces=surfaces, milestone=milestone,
                     blockedBy=blockedBy, blocks=blocks, state=state, project=P, sections=s))

# ---------------- PAP-163 compiler ----------------
child("PAP-163", "tables/compiler/core", "Compiler core: dataset resolution, per-type filter ops, sorts and signed keyset cursors", "Build", "M",
Goal="""Produce correct, parameterised SQL for the rows and count of any `ViewSpec` on entity and custom datasets, with keyset pagination that clients cannot forge.""",
Scope="""In: `packages/views/src/compiler/{index,dataset,ops/*,sort,cursor}.ts`; `compileView` returning `rows` and `count`; casts per field type; `views.ensureIndex` job. Out: groups, aggregates, shapes, procedures, hook (siblings).""",
Spec="""* `resolveDataset(ref)` returns columns for entity datasets and `record.data -> 'key'` expressions with casts (`::numeric`, `::timestamptz`, `::boolean`, `::text[]`) for custom ones.
* One op module per field type exporting `ops: Record<FilterOp, (col, value, ctx) => SQL>`; relative dates resolved server-side in the actor timezone; `{ ref: 'currentUser' }` to `ctx.actor.id`; relations to `EXISTS`; lookups and rollups to lateral joins.
* Sort compiles `ORDER BY` with `NULLS LAST` and `id` tiebreaker; cursor is base64url JSON of last values, HMAC-SHA256 signed with a server key and the spec `version`; invalid signature `CURSOR_INVALID`, version mismatch `CURSOR_STALE`.
* `toPredicate(actor, action)` (PAP-228) ANDed into every statement.
* `ensureIndex` creates expression indexes for sorted custom fields, capped at 10 per dataset.""",
Contract="""Provides: `compileView` (rows and count), `compileFilter`, `compileSort`, `encodeCursor`, `decodeCursor`, `ops` registry. Consumes: `ViewSpec` (PAP-161), `FilterTree` SQL evaluator (PAP-279), field casts (PAP-164), `toPredicate` (PAP-228).""",
DoD="""* Table-driven tests per op per type; golden SQL snapshots for ten fixture views; cursor tamper test; cross-tenant test.
* `docs/views/query-compiler.md` sections for pipeline and cursor format.""",
Test="""* Unit: every `(type, op)` pair compiles and matches the in-memory oracle on a 1k-row PGlite seed; cursor round trip, tamper and stale cases.
* Integration: `EXPLAIN` on the 100k seed shows index use for sorted custom fields after `ensureIndex`.
* E2E and visual: none.""",
Demo="""Run `pnpm tsx scripts/explain-view.ts fixtures/grid.view.json` and read the SQL, bound parameters and plan.""",
Edge="""* Null boundaries in cursors; deleted field in filter flagged `orphaned`; relation to unreadable record simply does not match.""",
Deps="""PAP-161, PAP-279, PAP-228 (hard). Blocks the two sibling children.""",
Agent="""Builder: Nova (Views Engineer). Reviewer: Sentinel (Security Auditor).""",
SizeNote="the op matrix is wide but mechanical.")

child("PAP-163", "tables/compiler/groups-shapes", "Groups, aggregates and Electric shape eligibility", "Build", "M",
Goal="""Add level-by-level grouping, aggregates and Electric shape emission to the compiler so grouped views and live grids work without client-side computation.""",
Scope="""In: `compiler/groups.ts`, `compiler/aggregates.ts`, `compiler/shape.ts`; `views.groups` and `views.distinct` SQL; shape registration. Out: procedures and hook (sibling).""",
Spec="""* `compileGroups(spec, groupPath)` returns group keys, counts and aggregates for one level (three-level grouping is three cheap queries); `unnest` when `expandMulti`; group pages of 100.
* Aggregates: `count`, `sum`, `avg`, `min`, `max`, `percentile_cont(0.5)`, `count(distinct)`, empty and filled via `count(*) filter (where ...)`; currency sums grouped by currency.
* Shape eligible only for a flat AND of `is|isAnyOf|isEmpty` on indexed columns with no groups; `ShapeDef` registered through PAP-270 with a server-set `where`; otherwise `shape` undefined.""",
Contract="""Provides: `compileGroups`, `compileAggregates`, `shapeFor(spec)`, `ShapeDef`. Consumes: core child, shape registry (PAP-270).""",
DoD="""* Unit tests for each aggregate and for `expandMulti`; shape eligibility table test; docs section on shape eligibility.""",
Test="""* Unit: aggregates versus oracle on fixtures; eligibility matrix; group pagination.
* Integration: shape registered in the PAP-270 proxy returns the same rows as `views.query` for an eligible view.""",
Demo="""Run `pnpm tsx scripts/groups-demo.ts` printing three levels of groups with counts and sums for the seed dataset.""",
Edge="""* 10k distinct group values paginated; mixed currencies never summed blindly.""",
Deps="""Core child (hard), PAP-270 (soft). Blocks the api child.""",
Agent="""Builder: Nova (Views Engineer). Reviewer: Sentinel (Code Reviewer).""",
SizeNote="one session.")

child("PAP-163", "tables/compiler/api-hook-bench", "oRPC procedures, useViewQuery hook and the 100k-row benchmark", "Build", "M",
Goal="""Expose the compiler through typed procedures and a React hook with infinite pagination, and prove the p95 budget on a 100k-row seed in CI.""",
Scope="""In: `packages/views/src/api.ts` (`views.query|count|groups|distinct`), `useViewQuery`, `vitest bench` suite, seed script. Out: view components.""",
Spec="""* Procedures are `tenantProcedure`s (PAP-268) taking `{ spec | viewId, cursor?, limit?, groupPath? }`; `limit` clamped to 200.
* `useViewQuery(spec, { pageSize }) => { pages, fetchNextPage, groups, aggregates, isStale }` on `@orpc/tanstack-query`; invalidates on record mutations, or via the shape change stream when a shape exists.
* Bench seeds 100k rows (entity and custom) and runs filtered, sorted, paginated queries; p95 under 150 ms recorded to the PR.""",
Contract="""Provides: the four procedures, `useViewQuery`, `seedViews(n)`. Consumes: both sibling children, PAP-268, PAP-271 `useShape` (soft).""",
DoD="""* Procedures documented in OpenAPI (PAP-269); bench green with the p95 table in the PR; cross-tenant harness on `views.query`.""",
Test="""* Unit: hook pagination reducer with mocked procedures.
* Integration: bench in CI; `callAs` tests for two tenants; `limit 500` clamped.
* E2E: none (grid child covers it).""",
Demo="""Run `pnpm --filter views bench compiler` and read the p95 table.""",
Edge="""* Stale cursor restarts pagination; shape invalidation falls back to refetch when the stream drops.""",
Deps="""Both sibling children (hard), PAP-268 (hard), PAP-271 (soft).""",
Agent="""Builder: Nova (Views Engineer). Reviewer: Forge (Schema Wright) on the bench.""",
SizeNote="bench setup dominates.")

# ---------------- PAP-164 field types ----------------
child("PAP-164", "tables/fields/framework-primitives", "Field type framework and primitive types (text, number, currency, percent, date, checkbox, rating, url, email, phone)", "Build", "M",
Goal="""Ship `defineFieldType`, the registry and the eleven primitive types with parse, format, validation, cells, editors and casts, so the grid can render and edit real data.""",
Scope="""In: `packages/views/src/fields/{define,registry,index}.ts` and one file per primitive type; `validateRecord`; Storybook stories. Out: choice, people, attachment, relational and computed types (siblings).""",
Spec="""* `defineFieldType` signature per the parent; `fieldTypes` map and `FieldType` union exported.
* `number` with `precision`, `thousandsSeparator`; `currency` as `{ amountMinor, currency }` with per-row or fixed currency; `percent` as a number option; `date` ISO with `includeTime` and `timezone`; `rating` 0..max; `phone` via `libphonenumber-js`; `email` lowercase RFC 5322; `url` normalised.
* Editors commit on Enter or blur, cancel on Escape; DatePicker from PAP-233.""",
Contract="""Provides: `defineFieldType`, `fieldTypes`, `FieldType`, `validateRecord`, eleven types. Consumes: cell registry (PAP-71), DatePicker (PAP-233), `Money` (PAP-27).""",
DoD="""* Parse, format, validate, filter-op and cast tests per type; `fast-check` round trips; stories screenshotted at 375, 1024, 1920 in three themes; axe clean.""",
Test="""* Unit: per-type tables; locale parsing `en`, `de`, `ar`; DST calendar-date case.
* Integration: custom dataset with the eleven types round-trips through PAP-163 filters.
* Visual: matrix above.""",
Demo="""Storybook `fields/primitives` shows every cell and editor; edit a currency and a date with the keyboard.""",
Edge="""* `1.234,50` parsed by locale with preview; rating max lowered lists clamped rows in the report (sibling).""",
Deps="""PAP-161, PAP-71, PAP-233 (hard). Blocks the two sibling children.""",
Agent="""Builder: Nova with Iris on editors. Reviewer: Sentinel (Visual Inspector).""",
SizeNote="eleven small types.")

child("PAP-164", "tables/fields/choice-people-attachment", "Choice, people and attachment types (select, multiSelect, user, attachment) with FieldSettingsPanel", "Build", "M",
Goal="""Add the four types that need external data (options, users, files) plus the settings panel used by column menus and the schema editor.""",
Scope="""In: `fields/{select,multiSelect,user,attachment}.ts`, `FieldSettingsPanel`, option colour tokens. Out: relational types (sibling).""",
Spec="""* `select` stores option id; options `{ id, name, color }` with a token palette; deleted options render grey "Unknown option".
* `multiSelect` as id arrays with `hasAll|hasAny` ops and `expandMulti` grouping.
* `user` as `user.id[]` with a searchable Combobox (PAP-238) over tenant members; avatar chips.
* `attachment` as `file.id[]` from PAP-37 with thumbnail cells, upload editor and broken-file retry.
* `FieldSettingsPanel` renders each type's `OptionsEditor` with validation.""",
Contract="""Provides: four types, `FieldSettingsPanel`, `OptionColorPicker`. Consumes: framework child, Combobox (PAP-238), `uploadFile` and variants (PAP-37), members (PAP-58).""",
DoD="""* Tests per type; panel story; screenshots at 375, 1024, 1920; axe on the panel and editors.""",
Test="""* Unit: option delete keeps values; `hasAll` and `hasAny` compile; attachment `failed` state.
* Integration: upload through the editor stores a file row and renders the `sm` variant.
* Visual: matrix above.""",
Demo="""Storybook `fields/choice`: add an option with a colour, pick two users, upload an image.""",
Edge="""* Member removed from tenant renders as "Former member"; 200 options virtualised in the picker.""",
Deps="""Framework child (hard), PAP-238, PAP-37 (hard).""",
Agent="""Builder: Nova with Iris. Reviewer: Sentinel (Visual Inspector).""",
SizeNote="one session.")

child("PAP-164", "tables/fields/relational-computed", "Relational and computed types (relation, lookup, rollup, formula storage) and convertFieldType with lossiness report", "Build", "M",
Goal="""Add relation, lookup, rollup and the formula storage type with their lateral-join contracts, and the type conversion routine every schema change relies on.""",
Scope="""In: `fields/{relation,lookup,rollup,formula}.ts`, `convertFieldType`, `docs/views/field-types.md` conversion matrix. Out: formula evaluation (PAP-171), the schema editor UI (gap issue).""",
Spec="""* `relation` options `{ datasetRef, limitOne, symmetricFieldId }`; symmetric writes kept consistent in one transaction; unreadable targets render "Restricted".
* `lookup { relationFieldId, targetFieldId }` and `rollup { relationFieldId, targetFieldId, fn }` are `computed: true`, compile via lateral joins in PAP-163.
* `formula` stores AST and result type only; renders `#PENDING` until PAP-171.
* `convertFieldType(field, newType) => { lossy, sampleLosses[] }` for every pair in the matrix; conversions run in a PAP-43 job in batches of 1,000 with progress.""",
Contract="""Provides: four types, `convertFieldType`, `conversionMatrix`, `runConversion(job)`. Consumes: framework child, compiler joins (PAP-163), jobs (PAP-43). Consumed by {{gap/tables/schema-editor}}.""",
DoD="""* Tests per type and for every conversion pair; matrix documented; stories screenshotted at 375, 1024, 1920.""",
Test="""* Unit: symmetric relation consistency; lossiness for number to text, text to date, multi to single select.
* Integration: lookup and rollup values match a brute-force query on the seed.""",
Demo="""Storybook `fields/relational`: link two records, watch the lookup fill, convert a text column to a select and read the report.""",
Edge="""* Cycle of lookups rejected; conversion with 100k rows shows progress and is cancellable.""",
Deps="""Framework child (hard), PAP-163 core child (hard), PAP-43.""",
Agent="""Builder: Nova. Reviewer: Sentinel (Code Reviewer), Forge on joins.""",
SizeNote="conversion matrix is the bulk.")

# ---------------- PAP-165 grid ----------------
child("PAP-165", "tables/grid/core", "Grid core: virtualisation, data binding, selection model and keyboard navigation", "Build", "M",
Goal="""Render 100k rows and 30 columns at 60 fps with a correct selection model and full keyboard navigation, as the foundation the editing and column children extend.""",
Scope="""In: `views/grid/{GridView,useGridSelection,useGridKeyboard,virtual}.tsx`, sticky header, frozen columns, density, empty and skeleton states. Out: editing, clipboard, bulk bar, column menu, `RecordPanel` (siblings).""",
Spec="""* TanStack Table with both axes virtualised; `useViewQuery` page 100 and prefetch; row heights 32, 40, 56, 88 px.
* Selection `{ anchor, focus }` ranges plus checkbox rows; "Select all N matching" confirms above 500.
* Keyboard: arrows, Shift+arrows, Tab, Home, End, PageUp, PageDown, Ctrl+Home, Ctrl+End, Space; commands `grid.*` via PAP-151; roving tabindex per PAP-153; `role="grid"` with `aria-rowindex`, `aria-colindex`, `aria-activedescendant`.
* Frozen columns with `position: sticky` and a scroll shadow; frozen total capped at 60 percent.""",
Contract="""Provides: `<GridView />` shell with `cellRenderer`, `headerSlot`, `toolbarSlot`, `useGridSelection`, `useGridKeyboard`, commands `grid.*`. Consumes: `useViewQuery` (PAP-163), cells (PAP-164), `EmptyState` (PAP-71), commands (PAP-151), focus (PAP-153).""",
DoD="""* Selection and keyboard reducers unit-tested; 10k-row story; screenshots at 375, 768, 1024, 1440, 1920 in three themes and four densities; performance trace meets budgets; axe clean.""",
Test="""* Unit: reducers; frozen cap maths.
* E2E: scroll to row 50,000 under 2 s; keyboard traversal; screen-reader announcements spot check.
* Visual: matrix above.""",
Demo="""Open `/demo/grid`, scroll fast, select a range with Shift+arrows, freeze a column.""",
Edge="""* 375 px first column frozen; denied `update` shows a read-only cursor.""",
Deps="""PAP-163, PAP-164, PAP-71, PAP-151 (hard). Blocks the sibling children.""",
Agent="""Builder: Nova. Reviewer: Sentinel (Visual Inspector).""",
SizeNote="performance work.")

child("PAP-165", "tables/grid/editing-clipboard-bulk", "Inline editing with optimistic commit, TSV clipboard ranges and the bulk actions bar", "Build", "M",
Goal="""Make the grid editable at Airtable speed: inline editors, optimistic writes with revert, copy and paste of ranges, and bulk actions on selections.""",
Scope="""In: `views/grid/{editing,clipboard,BulkBar}.tsx`. Out: column operations and panel (sibling), trash and undo semantics ({{gap/tables/bulk-trash}}).""",
Spec="""* Edit opens on Enter, F2, double-click or a printable key; commit through `mutate(orpc.records.update, { optimistic })` (PAP-272) with revert and toast on rejection.
* Ctrl+C copies the range as TSV; Ctrl+V parses per field type and writes in chunks of 200 with progress and cancel; overflow past the last row offers "add n rows".
* Bulk bar: count, delete, duplicate, set field value; server-side actions by filter for "all matching".""",
Contract="""Provides: `useCellEditing`, `useClipboardRange`, `<BulkBar actions />` extension point used by {{gap/tables/bulk-trash}} and PAP-189. Consumes: core child, editors and `parse` (PAP-164), `mutate` (PAP-272), `records.*` procedures.""",
DoD="""* Editing, clipboard and bulk flows in Playwright; unit tests for TSV parsing; screenshots of edit and bulk states at 375, 1024, 1920.""",
Test="""* Unit: TSV parser with quotes and newlines; chunking; revert on rejection.
* E2E: edit, reload, persisted; paste 500 rows; bulk set value on 50 rows; rejected write reverts with toast.""",
Demo="""Paste three rows from a spreadsheet into `/demo/grid`, then bulk-set a status on the selection.""",
Edge="""* Row deleted mid-edit closes the editor (PAP-144); 5,000-row paste is chunked and cancellable.""",
Deps="""Core child (hard), PAP-164, PAP-272 (soft).""",
Agent="""Builder: Nova. Reviewer: Sentinel (Edge Case Hunter).""",
SizeNote="one session.")

child("PAP-165", "tables/grid/columns-groups-panel", "Column operations, grouping headers, aggregate footer and RecordPanel", "Build", "M",
Goal="""Complete the grid with column resize, reorder, hide and freeze, sticky grouping headers with collapse, an aggregate footer and the record side panel.""",
Scope="""In: `views/grid/{ColumnMenu,columns,GroupHeader,AggregateFooter,RecordPanel}.tsx`. Out: the filter, sort and group builders (PAP-166), record detail routes and history ({{gap/tables/record-detail}}).""",
Spec="""* Resize handle 8 px, double-click auto-fit; widths persisted via `onSpecChange` debounced 500 ms; reorder via `SortableList` (PAP-155) or pointer fallback; header menu: sort, filter, group, hide, freeze, edit field (opens `FieldSettingsPanel`), insert, delete for custom datasets.
* Group headers sticky with counts and per-level aggregates from `views.groups`; collapse persisted in `spec.groups[].collapsed`; "(empty)" last.
* `AggregateFooter` per column with the type's allowed functions.
* `RecordPanel` on row expand or `?r=<id>`: all fields as editors, comments slot (PAP-131), `AuditTrail` (PAP-38).""",
Contract="""Provides: `ColumnMenu` slot API, `<RecordPanel recordId slots />`, `useColumnLayout`. Consumes: core child, `FieldSettingsPanel` (PAP-164 sibling), `views.groups` (PAP-163), `SortableList` (PAP-155), comments (PAP-131), audit (PAP-38).""",
DoD="""* Playwright for resize, reorder, freeze, hide, group collapse, panel edit; screenshots at 375, 1024, 1920; axe clean.""",
Test="""* Unit: width and order persistence reducer; group collapse state.
* E2E: the flows above plus `?r=` deep link.
* Visual: grouped grid with footer at three widths.""",
Demo="""Group `/demo/grid` by status from the header menu, collapse a group, change the footer to sum, open a row in the panel.""",
Edge="""* Auto-fit on 100k rows samples visible rows only; panel for a deleted record shows a removed state.""",
Deps="""Core child (hard), PAP-163, PAP-155 (soft), PAP-131 and PAP-38 (soft slots).""",
Agent="""Builder: Nova. Reviewer: Sentinel (Visual Inspector).""",
SizeNote="one session.")

# ---------------- PAP-168 time views ----------------
child("PAP-168", "tables/time/engine-calendar", "TimeScale engine, range compilation, overlap packing and the calendar view (month, week, day, agenda)", "Build", "M",
Goal="""Build the shared time engine and the calendar view so any dataset with a date field is browsable and reschedulable by drag.""",
Scope="""In: `views/time/{TimeScale,range,pack,CalendarView,DateRangeNav}.tsx`. Out: timeline and Gantt (siblings).""",
Spec="""* `TimeScale` maps dates to pixels per zoom; `date-fns` 4.x with `@date-fns/tz`; all-day values are calendar dates.
* Range compilation `start <= rangeEnd AND coalesce(end, start) >= rangeStart` via PAP-163; window padded one period; page 500 with "+n" chips.
* Month grid with four events per cell then "+n"; week and day with 30-minute slots and column-packed overlaps; agenda reuses PAP-169 list rows.
* Drag to move, drag-select to create, keyboard `n` to create; every event a focusable button with a descriptive label.""",
Contract="""Provides: `TimeScale`, `compileRange`, `packOverlaps`, `<CalendarView />`, `<DateRangeNav />`. Consumes: PAP-163, date cells (PAP-164), drag (PAP-155), list rows (PAP-169).""",
DoD="""* DST fixtures for two zones; Playwright drag and create; screenshots at 375, 768, 1024, 1440, 1920 in three themes; axe clean.""",
Test="""* Unit: range compile, packing, DST, month spans.
* E2E: reschedule across a DST boundary and verify the stored instant; agenda at 375 px.""",
Demo="""Drag an event to next week in `/demo/calendar`, switch to week view and back.""",
Edge="""* Multi-month spans with continuation arrows; travelling user offset change rerenders.""",
Deps="""PAP-163, PAP-164, PAP-155 (hard). Blocks siblings.""",
Agent="""Builder: Nova. Reviewer: Sentinel (Edge Case Hunter).""",
SizeNote="date maths heavy.")

child("PAP-168", "tables/time/timeline", "Timeline view: two-axis virtualised canvas, lanes, zoom levels and bar editing", "Build", "M",
Goal="""Render thousands of items across lanes on a horizontally scrolling, zoomable timeline with drag to move and resize.""",
Scope="""In: `views/time/{TimelineView,lanes,zoom}.tsx`, PNG export. Out: dependencies and critical path (Gantt sibling).""",
Spec="""* Virtualised on both axes with `@tanstack/react-virtual`; lanes from `laneField` groups; two-tier sticky headers per zoom; Ctrl+wheel zoom and pinch (PAP-156); today marker; milestones as diamonds.
* Move and resize snap to the zoom unit with a ghost preview; keyboard arrows move, Shift+arrows resize.
* Labels hidden under 40 px; export visible range with `html-to-image`.""",
Contract="""Provides: `<TimelineView />`, `useTimelineViewport`, bar renderer reused by Gantt. Consumes: engine child, PAP-155, PAP-156.""",
DoD="""* Playwright zoom, pan, move, resize on a 2,000-item seed; 60 fps assertion; screenshots at five widths in three themes.""",
Test="""* Unit: zoom tick generation; snapping.
* E2E: flows above plus keyboard resize.""",
Demo="""Zoom from month to day in `/demo/timeline`, drag a bar and resize another.""",
Edge="""* 10,000 items in one lane stay smooth; missing `endField` disables resize.""",
Deps="""Engine child (hard), PAP-155, PAP-156 (soft).""",
Agent="""Builder: Nova. Reviewer: Sentinel (Visual Inspector).""",
SizeNote="one session.")

child("PAP-168", "tables/time/gantt", "Gantt view: frozen left grid, dependency arrows, critical path, progress and working days", "Build", "M",
Goal="""Turn the timeline into a Gantt with a task grid, finish-to-start dependencies, critical path highlighting and working-day scheduling.""",
Scope="""In: `views/time/{GanttView,deps,criticalPath,workdays}.tsx`. Out: resource levelling.""",
Spec="""* Left grid (title, start, end, duration, assignee) reusing PAP-165 cells; dependencies from a self-relation field drawn as SVG paths; create by dragging a connector handle; delete via context menu.
* Dragging a bar with dependents offers "shift dependents" (Alt skips); cycles rejected with explanation; imported cycles dashed red.
* Critical path is the longest path, recomputed client-side; `progressField` fills bars; weekends shaded and skipped when `workingDays` set.""",
Contract="""Provides: `<GanttView />`, `criticalPath(items, deps)`, `shiftDependents`. Consumes: timeline child, PAP-165 cells, relation type (PAP-164).""",
DoD="""* Unit tests for critical path and working-day maths; Playwright dependency create and shift; replay at 1024 and 1920; screenshots at five widths.""",
Test="""* Unit: longest path on fixtures; cycle detection; working-day arithmetic.
* E2E: add dependency, shift, reject cycle; keyboard-only reschedule.""",
Demo="""Draw a dependency between two bars in `/demo/gantt` and move the predecessor.""",
Edge="""* Zero-duration after resize clamps and warns; under 768 px the left grid hides.""",
Deps="""Timeline child (hard), PAP-165, PAP-164.""",
Agent="""Builder: Nova. Reviewer: Sentinel (Edge Case Hunter).""",
SizeNote="one session.")

# ---------------- PAP-171 formula ----------------
child("PAP-171", "tables/formula/parser-typecheck", "Lexer, Pratt parser, AST, type checker and the defineFunction catalogue", "Build", "M",
Goal="""Parse Airtable and Notion style formulas into a typed AST with positioned diagnostics and a metadata-driven function catalogue.""",
Scope="""In: `formula/{lexer,parser,ast,types,check,functions/index}.ts`; `defineFunction`; catalogue entries (signatures only) for 80+ functions from PAP-162. Out: implementations, editor, SQL (siblings).""",
Spec="""* Grammar per the parent; `{Field}` rewritten to `@fld_<id>` at save; iterative parser with depth limit 200.
* Types `text | number | boolean | date | array<T> | null | error`; coercion rules; `checkType(ast, fields)`.
* `defineFunction({ name, aliases, params, returns, pure, volatile? })` with variadic params.""",
Contract="""Provides: `parse`, `checkType`, `AST` types, `functions` catalogue, `defineFunction`. Consumes: field types (PAP-164), inventory (PAP-162).""",
DoD="""* 200-expression golden corpus; `fast-check` fuzz for crash-freedom; diagnostics snapshots.""",
Test="""* Unit: corpus, type errors with positions, alias resolution, depth limit.""",
Demo="""Run `pnpm tsx scripts/formula-check.ts 'IF({Amount} > 1, "a", 2)'` and read the type diagnostic.""",
Edge="""* Unicode field names; unterminated strings; deleted field reference yields `#REF` marker.""",
Deps="""PAP-164, PAP-162 (hard). Blocks siblings.""",
Agent="""Builder: Nova. Reviewer: Sentinel (Edge Case Hunter).""",
SizeNote="one session.")

child("PAP-171", "tables/formula/evaluator-editor", "TypeScript evaluator with function implementations and the CodeMirror formula editor", "Build", "M",
Goal="""Evaluate formulas in TypeScript for previews, forms and client display, and give users an editor with autocomplete, signature help and live results.""",
Scope="""In: `formula/{evaluate,functions/*}.ts`, `FormulaEditor` (CodeMirror 6 language mode), function reference drawer. Out: SQL (sibling).""",
Spec="""* `evaluate(ast, record, ctx)` with actor timezone, cached per record version; `#ERROR` values with hover detail; `IFERROR`.
* Implementations for all catalogue functions; `LEN` and `MID` count code points.
* Editor: field and function autocomplete, signature help, inline diagnostics, live preview on a sample record, reference drawer generated from metadata.""",
Contract="""Provides: `evaluate`, `<FormulaEditor field fields sampleRecord />`, `functionDocs()`. Consumes: parser child, editor libraries from the registry (PAP-215).""",
DoD="""* Evaluator matches Airtable-documented examples; editor story screenshotted at 375, 1024, 1920; axe clean.""",
Test="""* Unit: every function against documented examples; DST date fixtures.
* E2E: type with autocomplete, see a diagnostic, fix, see the preview.""",
Demo="""Write `DATETIME_DIFF({Due}, TODAY(), 'days')` in the editor and watch the preview.""",
Edge="""* Division by zero is an error; emoji length; `TODAY()` in tenant timezone for public views.""",
Deps="""Parser child (hard).""",
Agent="""Builder: Nova with Iris on the editor. Reviewer: Sentinel.""",
SizeNote="function implementations are many but small.")

child("PAP-171", "tables/formula/sql-cache", "SQL compiler, formula_cache fallback job and the dependency graph", "Build", "M",
Goal="""Run formulas server-side where Postgres can, and materialise the rest so every formula field can be filtered, sorted and aggregated.""",
Scope="""In: `formula/{sql,cache,graph}.ts`, `compiler/ops/formula.ts` integration in PAP-163, refresh job. Out: UI.""",
Spec="""* `compile(ast) => SQL | Unsupported`; text, maths, logic and most date functions map to Postgres (`date_trunc`, `to_char` with a token translator, `regexp_*`, jsonb array functions); volatile functions excluded from indexes.
* Unsupported formulas write `record.formula_cache jsonb` via a PAP-43 job in batches of 500 when dependencies change; `records.update` enqueues affected ids.
* Dependency graph per dataset with cycle detection; `convertFieldType` and deletion consult it.""",
Contract="""Provides: `compile`, `dependencyGraph`, `refreshFormulaCache(job)`, `formula` op module for PAP-163. Consumes: parser child, evaluator child (parity tests), PAP-163, PAP-43.""",
DoD="""* TS versus SQL parity on a 1,000-record fixture for every SQL-capable function; cache refresh within one job cycle; unsupported list published.""",
Test="""* Unit: compile snapshots; graph cycles.
* Integration: filter and sort by formula through `views.query`; stale cache refresh timing.""",
Demo="""Filter the grid by a formula result and run `pnpm tsx scripts/formula-sql.ts` to print the generated SQL.""",
Edge="""* Formula referencing a rollup of a formula resolves in dependency order; 500 nested IFs compile or fall back gracefully.""",
Deps="""Parser and evaluator children (hard), PAP-163, PAP-43.""",
Agent="""Builder: Nova. Reviewer: Sentinel (Security Auditor on SQL).""",
SizeNote="one session.")

# ---------------- PAP-173 dashboards ----------------
child("PAP-173", "tables/dashboard/model-grid", "Dashboard tables, layout engine, breakpoint layouts and drag or resize with keyboard moves", "Build", "M",
Goal="""Store dashboards and lay blocks out on a responsive 12-column grid that users arrange by pointer or keyboard.""",
Scope="""In: tables `dashboard`, `dashboard_block`; procedures `dashboards.*`, `dashboardBlocks.*`; `layout/` engine; `<DashboardEditor />` shell. Out: block kinds and cross-filter (sibling).""",
Spec="""* Schema per the parent; RLS; visibility mirrors PAP-172.
* Grid 12/8/1 columns at `lg`/`md`/`sm`; row height 40 px; collisions push down; `sm` auto-derived from `y` unless customised.
* Drag and resize with 8-direction handles via PAP-155; keyboard select, arrows move one cell, Shift+arrows resize; announcements.""",
Contract="""Provides: `Dashboard`, `DashboardBlock` types, procedures, `useLayoutEngine`, `<DashboardEditor />`. Consumes: PAP-155, PAP-172, PAP-34.""",
DoD="""* Layout collision and derivation unit tests; Playwright drag, resize, keyboard move; screenshots at 375, 768, 1024, 1440, 1920.""",
Test="""* Unit: collision, derivation, bounds.
* E2E: arrange six placeholder blocks by pointer and keyboard, reload, layout persisted.""",
Demo="""Add three placeholder blocks in the editor, drag one wider, move another with the keyboard.""",
Edge="""* 40 blocks warn at 30; min sizes enforced.""",
Deps="""PAP-155, PAP-172 (hard). Blocks siblings.""",
Agent="""Builder: Nova. Reviewer: Sentinel (Visual Inspector).""",
SizeNote="one session.")

child("PAP-173", "tables/dashboard/blocks-crossfilter", "Block kinds, cross-filter bus, filter bar, params and deep links", "Build", "M",
Goal="""Render real views inside blocks and make them talk: a click in one block filters the others, with a filter bar and typed params in the URL.""",
Scope="""In: `dashboard/{Block,NumberBlock,TextBlock,FilterBarBlock,filters,params}.tsx`, `defineNumberBlock`. Out: layout (sibling), print and perf (sibling).""",
Spec="""* Blocks render views in `embedded` mode with `spec_override` merged; menu edit, duplicate, fullscreen, export, remove.
* `DashboardFilterContext` per the parent; `config.fieldMap` and `ignoreCrossFilter`; chips in the header bar.
* `FilterBarBlock` controls (select chips, date range, user picker, search) write to `global`; `NumberBlock` with delta, sparkline and goal colour; `TextBlock` Markdown with `{{param.name}}`.
* Params in `?p.<name>=` for deep links.""",
Contract="""Provides: block components, `defineNumberBlock`, `useDashboardFilters`, `FilterCondition` emission contract. Consumes: layout child, `onFilter` emitters (PAP-170, PAP-167, PAP-165), `FilterTree` (PAP-279), sparkline (PAP-170).""",
DoD="""* Cross-filter merge unit tests; Playwright chart-to-grid filter, filter bar, params; replay; screenshots at five widths.""",
Test="""* Unit: merge rules, type mismatch ignored, param parsing.
* E2E: click a bar, grid filters, chip removable; global date range refetches two charts.""",
Demo="""Click a chart bar in `/demo/dashboard` and watch the grid filter and the chip appear.""",
Edge="""* Two filter blocks on one field: last wins; deleted view shows a replace tile.""",
Deps="""Layout child (hard), PAP-170, PAP-165, PAP-167, PAP-279.""",
Agent="""Builder: Nova. Reviewer: Sentinel (Code Reviewer).""",
SizeNote="cross-filter semantics.")

child("PAP-173", "tables/dashboard/print-perf-spec", "Lazy loading, error boundaries, print route, page-spec hook and permission tiles", "Build", "S",
Goal="""Make dashboards fast, printable and embeddable from page specs, with graceful failure per block.""",
Scope="""In: lazy block loading, per-block error boundary and skeleton, `/print/d/:id` (A4 and Letter), `layout.dashboard` in `page.spec.yaml` (PAP-120), "No access" tiles, refresh interval.""",
Spec="""* Blocks load as they scroll into view; 12-block dashboard settles under 2 s on the seed tenant; refresh min 30 s with "updated n s ago".
* Print route renders without chrome; map blocks as static images; used by PAP-183 exports.
* Viewers see "No access" tiles for views they cannot read.""",
Contract="""Provides: print route, `layout.dashboard` codegen hook, `BlockErrorBoundary`. Consumes: both sibling children, PAP-120, Playwright print (PAP-82 image).""",
DoD="""* Performance trace attached; permission test; PDF snapshot; docs `docs/views/dashboards.md`.""",
Test="""* Integration: settle time on seed; PDF page count.
* E2E: viewer without access sees the tile; block error does not break the page.""",
Demo="""Print `/demo/dashboard` to PDF and open it.""",
Edge="""* WebGL absent in print: list fallback.""",
Deps="""Sibling children (hard), PAP-120 (soft).""",
Agent="""Builder: Nova. Reviewer: Sentinel.""",
SizeNote="half a session.")

# ---------------- PAP-174 automations ----------------
child("PAP-174", "tables/automations/model-triggers", "Automation schema, trigger sources and the run runtime with idempotency, loop guard, limits and circuit breaker", "Build", "M",
Goal="""Store automations and fire them reliably from record changes, view membership, schedules, forms, webhooks and buttons, with the guards that keep a rules engine safe.""",
Scope="""In: `automations/{schema,triggers/*,runtime}.ts`, `button` field type, webhook route, `automation_run` writes. Out: actions (sibling), UI (sibling).""",
Spec="""* Tables per the parent; record triggers from PAP-38 `LISTEN/NOTIFY` debounced 500 ms; `record.entersView` diffs membership through PAP-163; cron in tenant timezone; `form.submitted` from PAP-169; HMAC webhooks with replay protection; `button.clicked`.
* Runs are PAP-43 jobs idempotent per `(automation_id, trigger_event_id)`; loop guard, chaining depth up to 3, daily limit, circuit breaker after 20 failures; imports run with automations paused.""",
Contract="""Provides: `defineTrigger`, `enqueueRun`, `automations.*` CRUD, webhook route, `button` type. Consumes: audit NOTIFY (PAP-38), jobs (PAP-43), compiler (PAP-163), `form.submitted` (PAP-169), PAP-164 registry.""",
DoD="""* Unit tests for every guard; DST schedule test; webhook replay rejected; runs visible in audit.""",
Test="""* Unit: debounce, loop guard, breaker, limits.
* Integration: grid edit produces exactly one run; 1,000-row import with automations paused produces none.""",
Demo="""Create an automation via the API, edit a record and watch `automation_run` rows appear.""",
Edge="""* Trigger table deleted disables with a reason; missing timezone defaults to UTC with a banner.""",
Deps="""PAP-38, PAP-43, PAP-163 (hard), PAP-169 (soft). Blocks siblings.""",
Agent="""Builder: Nova with Forge on NOTIFY. Reviewer: Sentinel (Edge Case Hunter).""",
SizeNote="runtime guards.")

child("PAP-174", "tables/automations/actions", "Action catalogue with scope classes, template expressions, connector.call, agent.run, delay and branch", "Build", "M",
Goal="""Give automations something to do: a typed action catalogue with safe defaults, templated values and integrations through the connector registry.""",
Scope="""In: `automations/actions/*.ts`, expression rendering shared with PAP-171, signed `webhook.send`. Out: triggers and UI (siblings).""",
Spec="""* `defineAction({ key, scope: read|write|destructive, schema, run })`; `record.update|create|delete`, `notify`, `webhook.send` (signed, retried through jobs), `connector.call` (PAP-121 registry), `agent.run` (PAP-108 handoff, approval-gated), `delay` up to 30 days, `branch`.
* Destructive actions need admin enablement and are excluded from templates; `agent.run` and `connector.call` record cost units.
* Expressions `{{record.field}}`, `{{trigger.*}}`, `{{now}}` through the PAP-171 evaluator subset.""",
Contract="""Provides: `defineAction`, `actions` registry, `renderTemplate`. Consumes: runtime child, notifications (PAP-136 core), connectors (PAP-121), handoffs (PAP-108), signed webhooks helper (PAP-222), PAP-171 evaluator (fallback to a minimal interpolation until it lands).""",
DoD="""* Every action unit-tested with fixtures; scope enforcement test; webhook signature verified by a sample receiver.""",
Test="""* Unit: each action's schema and run; destructive gating.
* Integration: notify and webhook steps from a real run; `delay` resumes after the clock advance.""",
Demo="""Run an automation with notify plus webhook against a local receiver and read both step results in the run.""",
Edge="""* Removed notify target skipped with warning; 5xx webhook retried on the jobs schedule.""",
Deps="""Runtime child (hard), PAP-121, PAP-136 core, PAP-108, PAP-222 (soft).""",
Agent="""Builder: Nova. Reviewer: Sentinel (Security Auditor).""",
SizeNote="one session.")

child("PAP-174", "tables/automations/builder-log-templates", "Automation builder page, test run, run log with replay, five starter templates and import hooks", "Build", "M",
Goal="""Let staff build, test and debug automations without code, and give templates and importers a way to ship automations.""",
Scope="""In: `specs/pages/tables/automations.page.spec.yaml`, builder page (trigger picker, `FilterBuilder` conditions, action list with drag reorder, test run), run log grid with replay, templates JSON for PAP-208, mapping hooks for PAP-202 and PAP-204.""",
Spec="""* Builder keyboard-operable per PAP-158; test run executes against a sample record without side effects (dry-run flag on actions).
* Run log as a grid view with step expansion and replay; retention 90 days.
* Templates: appointment reminder, deal stage notification, overdue invoice nudge, new lead assignment, weekly digest.""",
Contract="""Provides: builder route, `automationTemplates`, `mapImportedAutomation(source)` hook, run log dataset. Consumes: both siblings, `FilterBuilder` (PAP-166), drag (PAP-155), grid (PAP-165), page spec tooling (PAP-120).""",
DoD="""* Playwright build, test run, real run, replay; screenshots at 375 and 1280 in three themes; parity matrix in docs; templates validate.""",
Test="""* Unit: template JSON validates; import mapping fixtures.
* E2E: full flow from the parent's umbrella test; keyboard-only build.""",
Demo="""Build "when Status becomes Done, notify owner", test it, edit a record, open the run.""",
Edge="""* Template installed twice is idempotent; replay of a run with a deleted record fails clearly.""",
Deps="""Both siblings (hard), PAP-166, PAP-165, PAP-155, PAP-120.""",
Agent="""Builder: Nova with Iris on the builder. Reviewer: Sentinel (Visual Inspector).""",
SizeNote="one session.")

# ---------------- gap issues ----------------
gap("gap/tables/schema-editor",
"Build the custom dataset schema editor: create tables and fields in-app, reorder, field type conversion with a lossiness report and background backfill",
"P1", "Build", 1, ["Staff", "Customer"], "All view types", ["PAP-164", "PAP-165"], ["PAP-199", "PAP-208"],
Goal="""Give users the Airtable "add a table, add a field, change its type" experience on top of PAP-161 custom datasets and PAP-164 types, so business templates and importers can create schema in-app and staff can evolve it safely with a lossiness report and background backfill.""",
Scope="""In: `packages/views/src/schema-editor/` (`DatasetList`, `NewDatasetDialog`, `FieldList`, `FieldEditor`, `ConvertTypeDialog`); procedures `datasets.create|rename|archive`, `fields.create|update|reorder|convert|archive`; conversion job progress UI; integration with the grid column menu "edit field" and "insert field". Out: entity dataset schema (code-defined), formula editing (PAP-171), record data editing.""",
Spec="""* `datasets.create({ name, icon, titleField, fields[] })` creates the `dataset` row plus `field` rows and registers the dataset; names unique per workspace; slug derived.
* `fields.create` validates `FieldDef` with the type's `optionsSchema`; `fields.reorder` uses fractional indexes; `fields.archive` soft-deletes and keeps data for 30 days with restore.
* `fields.convert({ fieldId, newType, options })` runs `convertFieldType` preview (PAP-164 relational child), shows `sampleLosses` (up to 20 rows) and requires confirmation when `lossy`; conversion runs as a PAP-43 job in batches of 1,000 with progress and cancel; views referencing the field get filters re-validated and `orphaned` conditions flagged.
* Dependency check: converting or archiving a field referenced by lookups, rollups or formulas (PAP-171 graph) warns with the dependant list and blocks when it would break a formula.
* Permissions `dataset.manage`; agents may propose schema through drafts, not apply.
* Limits: 500 fields per dataset, 200 datasets per workspace unless entitlement raises it (PAP-178).""",
Contract="""Provides: procedures above, `<SchemaEditor datasetId />`, `<FieldEditor field onSave />` reused by the grid column menu (PAP-165) and the import mapping wizard (PAP-199), event `dataset.schema.changed { datasetId, change }`. Consumes: `dataset|field` tables (PAP-161), `defineFieldType` options editors and `convertFieldType` (PAP-164), jobs (PAP-43), dependency graph (PAP-171, soft), entitlements (PAP-178, soft). Consumed by PAP-199, PAP-208 business templates, PAP-202 importers.""",
DoD="""* Vitest, integration and Playwright below green.
* Storybook stories; screenshots at 375, 768, 1024, 1440, 1920 in three themes; axe clean; keyboard-only field creation.
* `docs/views/schema-editor.md`; CHANGELOG; Linear comment with demo link.""",
Test="""* Unit: name uniqueness, options validation per type, reorder indexes, dependency warnings.
* Integration: convert 10k-row number field to text with progress; cancel mid-way leaves data intact; archived field restored with data; views with orphaned filters flagged.
* E2E: create a dataset with five fields, insert a field from the grid header, convert a type and read the lossiness report, archive and restore a field.
* Visual: matrix above.""",
Demo="""Reviewer clicks "New table", adds four fields of different types, opens the grid, inserts a field from the column menu, then converts a text column to single select and reads the report before confirming. Under two minutes.""",
Edge="""* Two staff editing schema concurrently: optimistic version check returns `CONFLICT` with a refresh prompt.
* Converting with a running import: blocked until the import finishes.
* Field used as `titleField` archived: blocked, pick another first.
* 100 KB row limit exceeded by a conversion: rows listed in the report, conversion refused.
* Entity dataset opened in the editor: read-only with a link to the code definition.""",
Deps="""PAP-164 (hard), PAP-165 (hard, column menu), PAP-161, PAP-43, PAP-171 and PAP-178 (soft). Blocks PAP-199, PAP-208.""",
Agent="""Builder: Nova (Views Engineer) with Iris on dialogs. Reviewer: Sentinel (Code Reviewer, Edge Case Hunter).""",
Size="""M: procedures are thin over PAP-164; the conversion UX and dependency checks carry the work.""")

gap("gap/tables/record-detail",
"Build record-level features shared by every module: record detail page and panel routing, activity timeline, attachments tab, per-record comments and field history with undo",
"P1", "Build", 2, ["Staff", "Customer"], "All view types", ["PAP-165", "PAP-38"], ["PAP-189", "PAP-102"],
Goal="""Give every dataset one record surface, `/records/$table/$id`, that CRM, PM, finance and custom tables reuse: header, fields form, activity timeline, attachments, comments and field history with undo, so no module builds its own detail page.""",
Scope="""In: routes `/records/$dataset/$id` and the `?r=` panel mode; `packages/views/src/record/` (`RecordPage`, `RecordHeader`, `RecordFields`, `ActivityTimeline`, `AttachmentsTab`, `FieldHistory`); procedures `records.history|undo|related`; page spec `specs/pages/tables/record.page.spec.yaml` with per-dataset overrides. Out: module-specific layouts beyond slots (PAP-189 adds CRM slots), comment engine (PAP-131), audit storage (PAP-38).""",
Spec="""* Layout via PAP-70 `SplitPane` and `Inspector`: header (title field, status chip, owner, actions), left fields form using PAP-164 editors grouped by `FieldGroup`, right tabs Activity, Comments, Attachments, History; under `md` tabs stack and the panel becomes a drawer.
* Activity merges `audit_event` rows (PAP-38), comments (PAP-131) and module events (`crm_activity`, `document.*`) through a `registerActivitySource(dataset, fn)` hook into one PAP-71 `Timeline`.
* History: per-field diff list from audit rows; `records.undo({ recordId, auditEventId })` writes the previous value as a new update with reason `undo:<eventId>`; only the latest change per field is undoable by default.
* Attachments tab lists every attachment field's files with upload and preview (PAP-37).
* Related records: `records.related` lists inverse relations grouped by dataset as embedded views (PAP-165 embedded mode).
* Deep links `?r=<id>` open the panel on any view; `/records/...` is the full page; both share state.
* Permissions from the dataset (`<entity>.read|update`); history visible to `update` holders.""",
Contract="""Provides: `RecordPage`, `RecordPanel` (supersedes the PAP-165 stub), `registerActivitySource`, `registerRecordSlot(dataset, slot, component)`, procedures `records.history|undo|related`, route pattern `/records/$dataset/$id`. Consumes: editors (PAP-164), grid embedded mode (PAP-165), audit (PAP-38), comments (PAP-131), files (PAP-37), layouts (PAP-70), `Timeline` (PAP-71), conflict UX (PAP-144). Consumed by PAP-189 company and deal pages, PAP-102 issue detail, PAP-180 document detail, {{gap/tables/bulk-trash}} (restore from history).""",
DoD="""* Vitest, integration and Playwright below green.
* Screenshots at 375, 768, 1024, 1440, 1920 in three themes for page and panel; axe clean.
* `docs/views/record-detail.md` (adding a slot or activity source); CHANGELOG; Linear comment with demo link.""",
Test="""* Unit: history diff builder, undo eligibility, activity merge ordering, slot registry.
* Integration: undo writes the prior value and an audit row with the reason; related records respect RLS; activity source from a module appears in order.
* E2E: open a record from the grid, edit two fields, undo one from History, upload an attachment, add a comment, open the same record via `/records/...` and `?r=`.
* Visual: matrix above.""",
Demo="""Reviewer expands a row in `/demo/grid`, edits a field in the panel, opens History and clicks Undo, then switches to the full page and adds a comment that appears in the timeline. Under two minutes.""",
Edge="""* Record deleted while open: removed state with restore if trashed.
* Field changed by two users: undo targets the actor's own change and warns about the newer one.
* 10k audit rows: history paginated by field.
* Dataset without a title field uses the id and suggests setting one.
* Customer audience opening a staff record: 403 page via `can()`.""",
Deps="""PAP-165 (hard), PAP-38 (hard), PAP-164, PAP-70, PAP-71, PAP-131 and PAP-37 (soft slots), PAP-144. Blocks PAP-189, PAP-102 detail pages.""",
Agent="""Builder: Nova (Views Engineer) with Iris on layout. Reviewer: Sentinel (Visual Inspector, Code Reviewer).""",
Size="""M: composition of existing pieces plus history and undo semantics.""")

gap("gap/tables/bulk-trash",
"Build bulk operations, trash and restore: multi-row edit and delete with server batching, soft-delete trash with 30-day restore, undo toast",
"P1", "Build", 2, ["Staff", "Customer"], "All view types", ["PAP-165", "PAP-32"], ["PAP-199", "PAP-208"],
Goal="""Make `softDelete()` from PAP-32 a user-facing feature: bulk edit and delete across any view with server-side batching, a trash per dataset with 30-day restore, and an undo toast for every destructive action, so `crud.spec` expectations (PAP-86) hold everywhere.""",
Scope="""In: procedures `records.bulkUpdate|bulkDelete|restore|purge`, `trash.list`; `packages/views/src/bulk/` (`BulkBar` actions, `ConfirmBulkDialog`, `UndoToast`, `TrashView`); route `/trash/$dataset`; nightly purge job. Out: field-level history (record-detail gap), import rollback (PAP-199).""",
Spec="""* `records.bulkUpdate({ datasetRef, selection: { ids[] } | { filter: FilterTree }, patch })` and `bulkDelete` run in batches of 500 inside a PAP-43 job when the selection exceeds 200, returning `{ jobId }` and progress; below 200 they run inline. Selection by filter re-evaluates server-side with the actor's predicate.
* Soft delete sets `deleted_at` and `deleted_by`; views exclude deleted rows by default; `TrashView` lists them with restore and purge; `purge` after 30 days by a nightly job, sooner by `dataset.manage` holders.
* Undo toast for 10 seconds after any bulk action calls the inverse (`restore` or a reverse patch captured from the audit rows); undo of a bulk update replays previous values per row.
* Confirm dialog above 50 rows shows count, a sample of five titles and the reversibility note.
* Relations pointing at trashed records render a "In trash" chip; restoring re-links; purging nulls them (audited).
* Permissions: `<entity>.update|delete` per row; the batch skips denied rows and reports the count.""",
Contract="""Provides: procedures above, `BulkBar` action set registered into PAP-165 (`delete`, `duplicate`, `setField`, `restore`), `<UndoToast />`, `<TrashView datasetRef />`, event `records.bulk.finished { jobId, kind, count }`. Consumes: `softDelete` and `withTenant` (PAP-32), audit rows (PAP-38), jobs (PAP-43), grid selection (PAP-165 editing child), `FilterTree` predicate (PAP-279, PAP-228), toast (PAP-237). Consumed by PAP-199 (import rollback reuses `bulkDelete`), PAP-208 templates, PAP-189 bulk actions.""",
DoD="""* Vitest, integration and Playwright below green.
* Screenshots at 375, 1024, 1920 in three themes for bulk bar, confirm dialog, toast and trash; axe clean.
* `docs/views/bulk-trash.md`; CHANGELOG; Linear comment with demo link.""",
Test="""* Unit: batching maths, undo inverse patch construction, denied-row accounting.
* Integration: bulk delete 5,000 rows by filter runs as a job with progress; restore returns them with relations intact; purge after 30 days via a fixed clock; cross-tenant harness on trash.
* E2E: select 60 rows, bulk set a field, undo from the toast; delete 10 rows, open trash, restore two, purge one.
* Visual: matrix above.""",
Demo="""Reviewer selects all matching rows in a filtered grid, bulk-sets Status, clicks Undo in the toast, then deletes five rows and restores two of them from Trash. Under two minutes.""",
Edge="""* Undo after the toast expired: use Trash or History (record-detail gap).
* Bulk update hitting a validation error on some rows: partial success with a per-row error list.
* Restoring a record whose dataset field was archived: value kept, field hidden.
* Purge of a record referenced by a posted ledger line (PAP-179): blocked with explanation.
* Offline bulk action: refused with "connect to run bulk actions" (no outbox for batches).""",
Deps="""PAP-165 (hard, editing child), PAP-32 (hard), PAP-38, PAP-43, PAP-279, PAP-228. Blocks PAP-199 rollback reuse, PAP-208.""",
Agent="""Builder: Nova (Views Engineer). Reviewer: Sentinel (Security Auditor for filter-based batches, Edge Case Hunter).""",
Size="""M: the batching and undo semantics are the work; UI is small.""")
