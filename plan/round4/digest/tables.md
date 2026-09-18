# Round 4 digest: Table & Views Engine (`tables`)

Benchmarks: Airtable (field types, view types, interface designer, automations, sync, extensions: pivot, chart, dedupe, page designer); Notion databases (relations, rollups, templates, linked views, galleries, status groups, formulas 2.0); ClickUp views (List, Board, Box, Calendar, Gantt, Table, Timeline, Workload, Activity, Map, Mind Map, Whiteboard, Doc, Chat, Form, Embed) and custom fields; Baserow; NocoDB; Smartsheet; Monday.com; Coda.

Feature matrix: 96 rows, 54 covered, 19 partial, 23 gap. New issues: 28 (13 with a parent, 15 standalone gaps, 9 deferred to v0.2). Amendments: 8. Cross-project suggestions: 6.

## Feature matrix

| Feature | Status | Covered by | Note |
|---|---|---|---|
| View model ViewSpec superset schema | covered | PAP-161, PAP-483 | Ten kinds, filters as FilterTree, strict Zod |
| Parity checklist vs Airtable/Notion/ClickUp/Baserow/NocoDB | covered | PAP-162 | 250-400 row CSV; this matrix adds Monday, Smartsheet, Coda rows |
| Query compiler to SQL with keyset cursors | covered | PAP-335, PAP-336, PAP-337 | 100k-row bench |
| Electric shapes for live grids | covered | PAP-336, PAP-270 | Eligibility rules |
| Records CRUD API for custom datasets | gap | r4/tables/records-crud-procedures | Referenced by 164/342/333/334/169, owned by nobody |
| View renderer registry and universal ViewHost | gap | r4/tables/view-renderer-registry-and-host | Contract declares registerViewKind; no runtime owner |
| Demo routes and deterministic seed | gap | r4/tables/demo-pages-and-seed-data | Every DoD cites /demo/* |
| Field types: text, number, currency, percent, date, checkbox, rating, url, email, phone | covered | PAP-338 |  |
| Field types: select, multiSelect, user, attachment | covered | PAP-339 |  |
| Field types: relation, lookup, rollup, formula storage | covered | PAP-340 |  |
| Field types: geo, button | covered | PAP-170, PAP-388 | geo now in the map child |
| System fields: autonumber, created/modified time and by | gap | r4/tables/system-fields | Airtable, Baserow, NocoDB, Monday all ship them |
| Field types: rich text, duration, time, progress, json | gap | r4/tables/extra-field-types | Notion rich text, ClickUp progress, Baserow duration |
| Status field with todo/in-progress/done groups (Notion status) | partial | PAP-339 | Amendment: option groups on select |
| Field validation options (min, max, pattern, length) | partial | PAP-338 | Amendment |
| Field description and help text | partial | PAP-161 | Amendment: FieldDef.description |
| Field default values (static and dynamic) | gap | r4/tables/record-templates-and-field-defaults |  |
| Record templates (Notion/ClickUp) | gap | r4/tables/record-templates-and-field-defaults |  |
| Field type conversion with lossiness report | covered | PAP-340, PAP-332 |  |
| In-app schema editor (tables and fields) | covered | PAP-332 |  |
| Lookup and rollup with filtered linked records | partial | PAP-340 | Amendment: filter on lookup/rollup |
| Create linked record inline from relation picker | partial | PAP-340 | Amendment: allowCreate |
| Barcode / QR field | gap | — | wontdo for v0.1; parity row only |
| AI/agent-computed field | gap | r4/tables/agent-computed-field | Deferred |
| Field-level permissions per audience | partial | PAP-172, r4/tables/field-level-permissions | Public shares hide fields; per-audience rules deferred |
| Grid: virtualisation, selection, keyboard | covered | PAP-341 |  |
| Grid: inline edit, optimistic commit | covered | PAP-342 |  |
| Grid: TSV copy/paste ranges | covered | PAP-342, r4/input/clipboard-port | Typed clipboard payload from input |
| Grid: fill handle / drag to fill | gap | r4/tables/grid-fill-handle | Airtable and spreadsheets |
| Grid: find and replace | gap | r4/tables/grid-find-and-replace | Airtable ships it |
| Grid: column resize, reorder, hide, freeze | covered | PAP-343 |  |
| Grid: grouping headers and aggregate footer | covered | PAP-343, PAP-336 |  |
| Grid: row heights and density | covered | PAP-341, r4/design-system/density-modes |  |
| Grid: undo/redo stack for edits | partial | PAP-342, r4/input/undo-manager | Amendment: register edits in the undo manager |
| Grid: RTL and touch range selection | partial | PAP-341 | Amendment |
| Grid: context menus from commands | partial | PAP-343, r4/input/command-context-menus |  |
| Filter builder with nested AND/OR and per-type operators | covered | r4/tables/filter-builder-component, PAP-166 | Split from PAP-166 |
| Relative dates and dynamic values (current user) | covered | r4/tables/filter-builder-component, PAP-279 |  |
| Multi-sort, multi-level group, aggregates UI | covered | r4/tables/view-toolbar-sort-group-aggregates, PAP-166 |  |
| Quick filter chips and view search | covered | r4/tables/filter-builder-component, r4/tables/view-toolbar-sort-group-aggregates |  |
| Temporary URL-held filters for viewers | covered | r4/tables/view-toolbar-sort-group-aggregates |  |
| Conditional formatting / record colouring | gap | r4/tables/conditional-formatting | Airtable, Smartsheet, ClickUp, Monday |
| Kanban with swimlanes, WIP limits, drag | covered | PAP-167, PAP-331 |  |
| Calendar month/week/day/agenda | covered | PAP-344 |  |
| Timeline with lanes and zoom | covered | PAP-345 |  |
| Gantt with dependencies and critical path | covered | PAP-346 |  |
| Gallery view | covered | r4/tables/gallery-and-list-views | Split from PAP-169 |
| List view for phones | covered | r4/tables/gallery-and-list-views |  |
| Form view with conditional logic and public submit | covered | r4/tables/form-view-runtime-and-public-submit | Split from PAP-169 |
| Chart view (bar, line, area, pie, donut, number) | covered | r4/tables/chart-view-echarts | Split from PAP-170 |
| Extended charts (scatter, histogram, funnel, gauge, heatmap, combo) | gap | r4/tables/extended-chart-types | Deferred |
| Map view with clustering and bounds filter | covered | r4/tables/map-view-maplibre-and-geo-field | Split from PAP-170 |
| Geocoding of address fields | gap | r4/tables/geocoding-job | Deferred |
| Hierarchy / sub-items / tree grid (ClickUp, Notion, Smartsheet) | gap | r4/tables/tree-hierarchy-grid | Deferred |
| Workload / Box view (ClickUp, Monday) | gap | r4/tables/workload-view | Deferred |
| Pivot / summary table (Airtable ext, Coda, Smartsheet) | gap | r4/tables/pivot-summary-view | Deferred |
| Activity view | partial | PAP-333, PAP-38 | Per-record timeline; no cross-dataset activity view (v0.2) |
| Doc, Chat, Whiteboard, Mind map views (ClickUp) | partial | PAP-128, PAP-197, PAP-132 | Owned by collab and growth; mind map wontdo |
| Files view (Monday) / attachments gallery | partial | r4/tables/gallery-and-list-views, PAP-339 | Gallery over attachment cover; no dedicated files view |
| Embed view / iframe block | partial | PAP-386 | Amendment: embed block kind |
| Saved views, personal vs shared | covered | r4/tables/saved-views-switcher-and-audience-defaults | Split from PAP-172 |
| Per-audience default views | covered | r4/tables/saved-views-switcher-and-audience-defaults |  |
| View locking | covered | r4/tables/saved-views-switcher-and-audience-defaults |  |
| Public links and embeds with password and expiry | covered | r4/tables/public-view-links-and-embeds | Split from PAP-172 |
| Export view as CSV/XLSX/JSON | gap | r4/tables/view-export-csv-xlsx-ics-print | PAP-205 is tenant archive, not per-view |
| ICS feed for calendar views | gap | r4/tables/view-export-csv-xlsx-ics-print | ClickUp/Notion calendar sync |
| Print view | partial | PAP-387, r4/tables/view-export-csv-xlsx-ics-print | Dashboards had print; views get /print/v/:id |
| Scheduled snapshots to email/Slack | gap | r4/tables/scheduled-view-snapshots | Deferred |
| Import CSV/Excel/Sheets into a table | covered | PAP-200, PAP-199 | Migration project |
| Sync tables from external sources (Airtable sync) | partial | PAP-199, PAP-417, PAP-202 | Cross-project suggestion: scheduled re-sync |
| Formula engine (80+ functions, Airtable/Notion syntax) | covered | PAP-382, PAP-383, PAP-384 |  |
| Formula editor with autocomplete | covered | PAP-383 |  |
| Formula server-side compile and cache | covered | PAP-384 |  |
| Dashboards with drag layout | covered | PAP-385 |  |
| Dashboard blocks and cross-filter bus | covered | PAP-386 |  |
| Dashboard print, lazy, permission tiles | covered | PAP-387 |  |
| Number/KPI blocks with sparkline | covered | PAP-386, r4/design-system/dataviz-tokens-and-microcharts |  |
| Automations: triggers and runtime | covered | PAP-388 |  |
| Automations: actions catalogue | covered | PAP-389 |  |
| Automations: builder, run log, templates | covered | PAP-390 |  |
| Record detail page and panel | covered | PAP-333, PAP-343 |  |
| Record history with undo | covered | PAP-333 |  |
| Comments on records | covered | PAP-131, PAP-333 |  |
| Cell-level comments (Smartsheet) | gap | — | Cross-project suggestion to collab: cell anchor grammar |
| Attachments tab and previews | covered | PAP-333, r4/design-system/media-preview-and-lightbox |  |
| Bulk edit, delete, trash, restore | covered | PAP-334 |  |
| Duplicate detection and merge | gap | r4/tables/duplicate-detection-and-merge | Deferred; Airtable Dedupe ext, CRM merge |
| Duplicate record and view | covered | PAP-342, r4/tables/saved-views-switcher-and-audience-defaults |  |
| Offline edits and conflict UX | partial | PAP-272, PAP-144, PAP-167 | Data-layer and realtime own it |
| Live multiplayer presence in grid cells | partial | PAP-141, PAP-143 | Cross-project suggestion to realtime |
| Views performance budget (p95) | covered | PAP-337, PAP-242 |  |
| Accessibility: role=grid, announcements | covered | PAP-341, PAP-152 |  |
| External REST API and SDK for records | partial | PAP-269, PAP-222, r4/tables/records-crud-procedures |  |
| Agent access to views (MCP tool) | partial | PAP-291, PAP-60 | Cross-project suggestion to agents |
| Extension guide for adding kinds and types | gap | r4/tables/extension-guide-docs | Cold-session onboarding |
| Module contract, conformance, wiring | covered | PAP-483, PAP-486, PAP-489 |  |

## New issues

| Key | Title | Parent | Milestone | Size | Model / effort | Priority | Deferred |
|---|---|---|---|---|---|---|---|
| `r4/tables/records-crud-procedures` | Records CRUD procedures for custom datasets: records.list|get|create|update|archive|restore with FieldDef validation, idempotency and audit reason | — | Grid with sort, filter, group | M (3) | Opus 5 / high | 1 |  |
| `r4/tables/view-renderer-registry-and-host` | View renderer registry and ViewHost: registerViewKind, one <ViewHost spec /> that renders any kind, kind switcher and per-kind options panel | — | Grid with sort, filter, group | M (3) | Opus 5 / high | 1 |  |
| `r4/tables/demo-pages-and-seed-data` | Demo routes /demo/{grid,kanban,calendar,timeline,gantt,gallery,list,form,map,chart,dashboard} with a deterministic 100k-row seed and two demo datasets | — | Grid with sort, filter, group | M (3) | Sonnet 5 / medium | 2 |  |
| `r4/tables/system-fields` | System field types: autonumber, createdTime, lastModifiedTime, createdBy, lastModifiedBy as read-only computed FieldTypes | PAP-164 | Grid with sort, filter, group | S (2) | Sonnet 5 / medium | 2 |  |
| `r4/tables/filter-builder-component` | FilterBuilder: nested AND/OR groups, per-type operators, relative dates, dynamic values and the sentence renderer, reusable by segments and automations | PAP-166 | Grid with sort, filter, group | M (3) | Opus 5 / high | 1 |  |
| `r4/tables/view-toolbar-sort-group-aggregates` | ViewToolbar, SortEditor, GroupEditor, AggregateFooter picker, FieldVisibilityMenu, SearchBox and temporary URL view state | PAP-166 | Grid with sort, filter, group | M (3) | Sonnet 5 / high | 1 |  |
| `r4/tables/gallery-and-list-views` | Gallery and list views: cover cards with virtualised rows, dense phone list with swipe actions and grouped headers | PAP-169 | All view types | M (3) | Sonnet 5 / high | 2 |  |
| `r4/tables/form-view-runtime-and-public-submit` | Form view runtime and builder: FormSpec, conditional fields, drafts, public /f/:token submission with honeypot, Turnstile and rate limits | PAP-169 | All view types | M (3) | Opus 5 / high | 2 |  |
| `r4/tables/chart-view-echarts` | Chart view on ECharts: bar, stacked bar, line, area, pie, donut and number bound to views.groups with onFilter emission and table fallback | PAP-170 | All view types | M (3) | Sonnet 5 / high | 2 |  |
| `r4/tables/map-view-maplibre-and-geo-field` | Map view on MapLibre GL with the geo field type, clustering, bounds filter and rectangle select | PAP-170 | All view types | M (3) | Sonnet 5 / medium | 3 |  |
| `r4/tables/saved-views-switcher-and-audience-defaults` | Saved views: views.* CRUD, personal vs shared visibility, ViewSwitcher, per-audience defaults and view locking | PAP-172 | View sharing, formulas, dashboards | M (3) | Sonnet 5 / high | 1 |  |
| `r4/tables/public-view-links-and-embeds` | Public view links and embeds: view_share tokens, password and expiry, allowed_fields projection, /v/:token and /embed/v/:token with CSP and rate limits | PAP-172 | View sharing, formulas, dashboards | M (3) | Opus 5 / high | 2 |  |
| `r4/tables/view-export-csv-xlsx-ics-print` | Export any view as CSV, XLSX, JSON or ICS honouring filters, sorts and visible fields, streamed as a job with a print route /print/v/:id | — | View sharing, formulas, dashboards | M (3) | Sonnet 5 / medium | 2 |  |
| `r4/tables/conditional-formatting` | Conditional formatting: row and cell colour rules from FilterTree conditions, select-colour rows and progress bars in cells across grid, kanban, calendar and gallery | — | All view types | M (3) | Sonnet 5 / medium | 3 |  |
| `r4/tables/extra-field-types` | Additional field types: richText (Tiptap JSON), duration, time, progress and json with cells, editors, casts and conversions | PAP-164 | All view types | M (3) | Sonnet 5 / medium | 3 |  |
| `r4/tables/record-templates-and-field-defaults` | Record templates and field default values: FieldDef.defaultValue with dynamic tokens, per-dataset record templates and the New record menu | — | All view types | M (3) | Sonnet 5 / medium | 3 |  |
| `r4/tables/grid-find-and-replace` | Grid find and replace: search within the current view, match navigation, per-type replace with preview and batch write | PAP-165 | Grid with sort, filter, group | S (2) | Sonnet 5 / medium | 3 |  |
| `r4/tables/grid-fill-handle` | Grid fill handle: drag to fill down or across a range with copy, series and pattern detection for numbers and dates | PAP-165 | Grid with sort, filter, group | S (2) | Sonnet 5 / medium | 3 |  |
| `r4/tables/extension-guide-docs` | Write the views engine extension guide: adding a field type, a view kind, a filter operator, an aggregate and a dashboard block, with a checklist per contract port | — | View sharing, formulas, dashboards | S (2) | Haiku 4.5 / low | 2 |  |
| `r4/tables/duplicate-detection-and-merge` | Duplicate detection and record merge: find duplicates by fields with fuzzy matching, review pairs and merge with field-level choice | — | View sharing, formulas, dashboards | M (3) | Sonnet 5 / medium | 4 | yes |
| `r4/tables/tree-hierarchy-grid` | Hierarchy in grid and list: parent relation field drives indented sub-rows, expand and collapse, drag to re-parent and rollups along the tree | — | All view types | M (3) | Sonnet 5 / medium | 4 | yes |
| `r4/tables/workload-view` | Workload view: capacity per person per period from an assignee field and an effort field, with over-allocation highlighting | — | All view types | M (3) | Sonnet 5 / medium | 4 | yes |
| `r4/tables/pivot-summary-view` | Pivot summary view: rows and columns from two group fields, aggregate cells, totals, drill-through and CSV export | — | View sharing, formulas, dashboards | M (3) | Sonnet 5 / medium | 4 | yes |
| `r4/tables/extended-chart-types` | Extended chart types: scatter, histogram, funnel, gauge, heatmap and combo bar-line with shared series builder | PAP-170 | View sharing, formulas, dashboards | S (2) | Sonnet 5 / medium | 4 | yes |
| `r4/tables/agent-computed-field` | Agent-computed field type: a prompt template over record fields filled by a scoped agent job with cost units, caching and manual override | — | View sharing, formulas, dashboards | M (3) | Opus 5 / high | 4 | yes |
| `r4/tables/field-level-permissions` | Field-level permissions on custom datasets: per-field read and write by audience compiled into projections, editors and validators | — | View sharing, formulas, dashboards | M (3) | Opus 5 / high | 4 | yes |
| `r4/tables/scheduled-view-snapshots` | Scheduled view snapshots: email or Slack a view or dashboard export on a cron with the recipient's permissions | — | View sharing, formulas, dashboards | S (2) | Sonnet 5 / medium | 4 | yes |
| `r4/tables/geocoding-job` | Geocoding job: fill geo fields from address fields through a provider adapter (Nominatim self-hosted or Mapbox) with caching and rate limits | — | View sharing, formulas, dashboards | S (2) | Sonnet 5 / medium | 4 | yes |

## Amendments to existing specs

| Issue | Section | Summary |
|---|---|---|
| PAP-161 | Spec | * Round 4 additions (minor bump, `migrateViewSpec` step v3): `FieldDef.description?: string` (rendered as a header tooltip and form help), `FieldDef.group?: str… |
| PAP-340 | Spec | * Round 4: `lookup` and `rollup` options gain `filter?: FilterTree` evaluated over the linked records before projection or aggregation (Airtable's conditional r… |
| PAP-339 | Spec | * Round 4: `select` options may carry `group?: 'todo' / 'inProgress' / 'done'` and the field option `kind: 'status'` (Notion status semantics). Kanban reads `do… |
| PAP-338 | Spec | * Round 4: per-type validation options in `optionsSchema`: `text/longText { minLength?, maxLength?, pattern?: string (RegExp source, anchored, 200 char cap) }`,… |
| PAP-341 | Edge cases | * Round 4: RTL locales flip frozen columns to the end edge, `Home`/`End` and arrow semantics follow reading direction, and the scroll shadow mirrors (Playwright… |
| PAP-342 | Spec | * Round 4: every committed edit registers with the shared undo manager (`r4/input/undo-manager`) as one entry per cell commit (coalesced while typing into the s… |
| PAP-386 | Spec | * Round 4: two more block kinds. `embed` renders an iframe from a URL restricted to the tenant's `allowedEmbedOrigins` allowlist (settings, default empty) with … |
| PAP-166 | Scope | Round 4: this issue becomes an umbrella for two children, `r4/tables/filter-builder-component` (the standalone `FilterBuilder`, quick chips, relative dates and … |

## Cross-project suggestions

| Target | Title | Why |
|---|---|---|
| collab | Cell-level comment anchors: extend the anchor grammar with `cell:<datasetRef>:<recordId>:<fieldId>` and a grid cell comment indicator | Smartsheet and Excel comment on cells; PAP-131's grammar stops at `entity:` and the grid (PAP-343) can only show record-level threads. The tables engine will render an indicator if collab owns the anchor. |
| realtime | Cell-level presence in grids and boards: who is viewing or editing which record and field, from the PAP-141 awareness layer | Airtable and Google Sheets show collaborator cursors per cell; PAP-141 covers pages and PAP-143 record streams, but no issue projects awareness onto `GridView` cells or kanban cards. |
| migration | Scheduled re-sync of external sources into datasets (Airtable sync tables equivalent) on the PAP-199 connectors with change detection and conflict policy | Airtable Sync and Coda sync tables keep a dataset mirrored from Notion, Airtable or Stripe; PAP-199 imports once and PAP-417/PAP-423 connectors have the auth, so a scheduled incremental run belongs to migration. |
| agents | MCP tool server exposing `views.query`, `records.*` and `views.export` to agent sessions through the contract ports with `can()` and audit reasons | Characters should read and edit tables through the same permissioned API as humans; PAP-291 covers commands and PAP-60 keys, but no issue gives sessions a typed views tool. |
| quality | Add `views.query`, `views.groups` and `records.update` p95 to the PAP-242 performance budgets with the 100k-row seed from `r4/tables/demo-pages-and-seed-data` | PAP-337's bench proves the compiler once; the release-candidate k6 smoke should keep it honest as field types and formulas land. |
| spec-builder | Page spec `views:` section renders through `ViewHost` and accepts any registered kind; codegen emits `ui.dataTable` for arrays under 500 rows and a view for datasets | PAP-119 inlines view specs and PAP-120 emits `ui.dataTable`; the registry (`r4/tables/view-renderer-registry-and-host`) and the DataTable decision table (`r4/design-system/static-data-table`) give codegen one rule to follow. |

## What was missing and why it matters

1. The `records.*` write path for custom datasets was referenced by five specs and owned by none; without it the grid cannot edit, forms cannot submit and bulk actions have no server. It is now a P1 Opus 5 issue on the Grid milestone.
2. The contract (PAP-483) declares a `ViewRendererRegistry`, but no runtime issue built `registerViewKind` or a universal `ViewHost`; dashboards, PM boards and CRM would each import view components directly, defeating the plug-and-play goal. Now an explicit P1 issue that every later view kind registers into.
3. Every tables DoD points at `/demo/<kind>` and a 100k-row seed that nobody was building; a cold builder session would stall on fixtures. A deterministic seed and eleven demo routes are now one issue, layered on the app-shell starter seed (`r4/app-shell/starter-kit-demo-seed`).
4. Best-in-class parity was missing common product features rather than exotic ones: per-view export (CSV, XLSX, ICS), conditional formatting, system fields (autonumber, created and modified metadata), rich text and duration types, record templates and defaults, find and replace, fill handle. These land as P2 issues, mostly in the All view types and sharing milestones.
5. Three M issues on or near the zero-slack chain (PAP-166, PAP-169, PAP-170, PAP-172) were each two sessions of work in one ticket; splitting them into eight children (filter builder separate from toolbar, gallery/list from forms, chart from map, saved views from public links) lets them run in parallel and isolates the security-sensitive public paths for Opus review. Nine honest v0.2 features (tree grid, workload, pivot, dedupe, agent fields, field permissions, snapshots, geocoding, extended charts) are specified but deferred.
