# migration — Migration & Import Tools
PHASE P2 prio 2 dependsOn ['tables', 'collab']
SUMMARY: An import framework with schema mapping, dry runs and rollback; importers for CSV, Airtable, Notion, ClickUp, Linear, Stripe and QuickBooks; full export; business templates.
DESC: Goal: any business can move into a PaperOS app without losing data or lock-in. The import framework provides source connectors, a schema-mapping UI, dry runs, validation, rollback and persistent external-ID mappings for incremental re-sync. Importers cover spreadsheets, Airtable bases, Notion databases and pages, ClickUp and Linear workspaces, Stripe customers and QuickBooks/Xero charts of accounts. Full export to open formats guarantees no lock-in. Business-type seed packs (agency, retail, SaaS, clinic, restaurant) make a new app useful in minutes, and a migration agent interviews users and runs the imports. Non-goal: live two-way sync with every source.
MILESTONES: ['Import framework and CSV 2026-09-28: Format research, framework, CSV/Excel, ID mapping', 'Airtable, Notion, ClickUp importers 2026-09-30: Table and PM importers, export', 'Business migrations 2026-10-01: Stripe/QuickBooks import, templates, migration agent']


## PAP-198 [P1 Research M prio3 Backlog] Catalog export formats and API limits of Airtable, Notion, ClickUp, Monday, HubSpot and QuickBooks
key=migration/format-research milestone=Import framework and CSV agent=Researched by Scout (Import Mapper). Reviewed by Atlas for c
blockedBy=[] blocks=[]
GOAL: Before building any importer, know exactly what each source system lets us pull, in what shape and how fast: catalogue the export formats, API endpoints, auth models, pagination, rate limits, attachment access and schema quirks of Airtable, Notion, ClickUp, Monday, HubSpot and QuickBooks (plus Xero, Linear and Google Sheets since importers for them are planned), so `migration/import-framework` designs its connector interface against real constraints.
SCOPE: In:

* One reference sheet per source in `docs/migration/sources/{source}.md` with a fixed template: auth (OAuth scopes or PAT), base URL and SDK (`@notionhq/client` 4.x, `@linear/sdk`, `intuit-oauth`, `xero-node`, Airtable REST, ClickUp REST v2, Monday GraphQL, HubSpot v3), list and pagination shape, rate limits (Airtable 5 rps per base, Notion 3 rps average, HubSpot 100 per 10 s, QuickBooks 500 per minute per realm, and so on, each verified against current docs with the date checked), maximum page sizes, incremental sync support (`last_edited_time`, `updatedAt`, CDC or none), attachment URL expiry (Airtable URLs expire after hours, Notion after 1 h), export UI formats (CSV, JSON, Markdown+CSV zip, IIF, QBO), webhook availability, sandbox availability, and known schema quirks.
* Field type matrix `docs/migration/field-type-matrix.md`: every source field type mapped to a `tables/field-ty
SPEC(first 1200): * Time-box 1 agent-day; 45 minutes per source; unknowns recorded as "unverified" with a link to where the answer lives.
* Each reference sheet ends with a "connector implications" section: recommended auth flow, recommended sync strategy (full, incremental by timestamp, cursor), attachment strategy (stream to `data-layer/file-storage` immediately because URLs expire), and the three hardest edge cases.
* Fixtures cover: relations and lookups, multi-select, attachments, formulas, nested pages or subtasks, and archived or deleted items.
* Output consumed by `migration/import-framework` for the `SourceConnector` interface and by each importer issue; their descriptions are updated with verified limits by comment.
DOD:
* Nine reference sheets and the field type matrix merged under `docs/migration/`, rendering in the docs engine with the sources index page.
* Fixtures committed for at least Airtable, Notion, ClickUp, Linear, QuickBooks and CSV; fixture README explains anonymisation.
* Throughput table reviewed by Scout and Atlas; disagreements resolved in the PR.
* Every rate limit and expiry claim carries a source URL and a checked-on date; Vitest lint asserts the frontmatter `checkedOn` is present.
* Screenshots of each source's export UI at 1280 attached.
* CHANGELOG entry; Linear comment linking the index page and notifying `migration/import-framework`, `migration/airtable`, `migration/notion`, `migration/clickup-linear`, `migration/stripe-quickbooks`.
EDGE:
* Source requires a paid plan for API access (Airtable attachments on free tier, ClickUp some endpoints): note the plan and a UI-export fallback.
* Rate limits differ by plan or per token vs per workspace: record both and the safe default.
* Attachment URLs expire mid-import: connector implication is stream-on-discovery.
* Sources with soft-deleted items visible via API (Notion `archived`, Linear `trashed`): document whether to import as archived.
* Monday and HubSpot have no importer issue yet: sheets still written; note as follow-on.
* Trial workspace lacks features (formulas need paid): fixtures marked partial.
DEPS: None; can start now. Informs `migration/import-framework` (interface design) and every importer; overlaps with `growth/growth-research` on HubSpot mapping (share the CRM mapping section).


## PAP-199 [P1 Build L prio2 Backlog] Build the import framework: source connector, schema-mapping UI, dry run, validation, rollback
key=migration/import-framework milestone=Import framework and CSV agent=Built by Scout (Import Mapper) with Nova consulted on the re
blockedBy=['PAP-43', 'PAP-164'] blocks=['PAP-208', 'PAP-207', 'PAP-206', 'PAP-205', 'PAP-204', 'PAP-203', 'PAP-202', 'PAP-201', 'PAP-200']
GOAL: Build the one pipeline every importer uses: a `SourceConnector` interface that discovers a source's schema and streams records, a mapping model from source fields to PaperOS tables and field types, a schema-mapping UI with type-inference suggestions, a dry run that validates and reports without writing, a committed run that writes in batches with progress, and a rollback that reverses a run exactly. Importers then only implement connectors.
SCOPE: In:

* Package `packages/import/` with `src/connector.ts` interface: `discover(auth) -> SourceSchema { collections[]: { id, name, fields[]: { id, name, type, options, isRelation, targetCollectionId } } }`, `stream(collectionId, cursor?) -> AsyncIterable<SourceRecord>`, `fetchAttachment(ref) -> ReadableStream`, `capabilities { incremental, attachments, relations, rateLimit }`; connectors register with `registerConnector(name, factory)`.
* Schema `packages/import/src/schema.ts`: `import_source` (`connector`, `auth jsonb` encrypted, `display_name`, `status`), `import_mapping` (`source_id`, `version`, `definition jsonb`: collection -> target table (existing or new), field -> field (existing or create with type), transforms, relation strategy, dedupe key), `import_run` (`mapping_id`, `mode: dry|commit|rollback`, `status: queued|running|succeeded|failed|rolled_back|cancelled`, `stats jsonb` {r
SPEC(first 1200): * Dry run executes every step including transforms and validations against `tables/field-types` validators and RLS, writes `import_run_item` with `action` and `before` but inside a transaction that is rolled back; report groups errors by field and shows 20 examples each.
* Commit writes through the tables engine's record API (not raw SQL) so triggers, audit (`data-layer/audit-log`, `reason: import:<run_id>`) and search indexing apply.
* Rollback: for each item in reverse order `create` -> archive then hard delete if untouched since, `update` -> restore `before`; refuses if records were modified after the run unless `--force`, listing conflicts.
* Dedupe key (one or more fields) decides create vs update; matches also consult `migration/id-mapping`.
* Runs are resumable from the last completed batch after a crash; cursors persisted per collection.
* Limits: 5M rows per run, 10 GB attachments per run, 2 concurrent runs per tenant.
DOD:
* Vitest: connector registry, inference on 15 fixture columns (dates in 6 formats, currencies, selects), transforms, dedupe, relation second pass, dry run leaves no rows, rollback restores exact `before` state, resumability after simulated crash.
* In-memory fixture connector used for engine tests; 100k-row run completes under 5 minutes on staging with progress visible (bench committed).
* Playwright: wizard end to end with the fixture connector, dry run report with a deliberate error, commit, rollback; screenshots at 320, 375, 768, 1024, 1280, 1536 and 1920 in light and dark for mapping step, report and history.
* axe clean; mapping table keyboard-operable.
* `docs/migration/framework.md` (writing a connector in under a page, mapping JSON reference); CHANGELOG entry; Linear comment with recording and bench.
EDGE:
* Source field type changes between discover and stream: record-level validation error, not a crash; report lists the field.
* Circular relations (A references B references A): two-pass resolution handles it; self-references resolved in pass two.
* Target table has RLS denying the actor: dry run reports it up front.
* Row count exceeds limit: refuse before starting with guidance to split.
* Attachment fetch fails after record created: record kept, attachment error item, retry job for attachments only.
* User cancels mid-run: `cancelled`, partial rollback offered.
DEPS: `tables/field-types` (hard: validators and type list). `data-layer/file-storage`, `data-layer/audit-log`, `realtime/record-sync` (progress; fallback polling), `tables/grid-view` (history). Uses findings from `migration/format-research`. Unblocks every other migration issue.


## PAP-200 [P2 Build M prio2 Backlog] Import CSV, Excel and Google Sheets with type inference
key=migration/csv-excel milestone=Import framework and CSV agent=Built by Scout (Import Mapper). Reviewed by Sentinel (Edge C
blockedBy=['PAP-199'] blocks=[]
GOAL: Make spreadsheets the universal on-ramp: import CSV, TSV, Excel (`.xlsx`, `.xls`) and Google Sheets into new or existing tables with correct type inference, header detection, multi-sheet handling and large-file streaming, using the import framework so users get dry runs and rollback for free.
SCOPE: In:

* Connectors in `packages/import/src/connectors/`: `csv` (Papa Parse 5.x streaming with delimiter and encoding sniffing via `chardet`; RFC 4180 quoting, BOM handling), `excel` (ExcelJS 4.4 streaming reader for `.xlsx`; `.xls` via `xlsx` community build only for read, flagged legacy; each worksheet becomes a collection; merged cells, formulas (value not formula), dates from serials with 1900/1904 systems), `gsheets` (Google Sheets API v4 via `googleapis` with OAuth from the tenant's Google connection; each tab a collection; `valueRenderOption: UNFORMATTED_VALUE` plus formatted for dates).
* Upload path: files up to 1 GB through `data-layer/file-storage` multipart; connector reads from storage stream, never loads whole file in memory.
* Header detection: first non-empty row unless a heuristic (numeric ratio, duplicates) says otherwise; user override in the wizard; generated names `Col
SPEC(first 1200): * Sniffing samples the first 64 KB; delimiter candidates `, ; \t |`; encoding candidates UTF-8, UTF-16, Windows-1252, with a manual override.
* Excel dates: cells with date number formats become `date` or `datetime`; plain numbers remain numbers even if they look like serials.
* Google Sheets over 5M cells or protected: clear error linking to a CSV export fallback.
* Multi-sheet workbook: wizard proposes one target table per sheet; sheets that look like lookups (two columns, unique keys) are suggested as select options or relations.
* Dedupe default: none for new tables; for existing tables the primary text field or email if present, editable.
* Row limit per run inherited from framework (5M); over 200k rows the wizard recommends dry run on a 10k sample first (one click).
DOD:
* Vitest: 25 fixture files (delimiters, encodings, BOM, quoted newlines, ragged rows, Excel dates both systems, merged cells, formulas, error values, leading zeros, empty sheets, 50-column wide) all infer expected types and counts; Sheets connector tested with recorded API responses.
* Performance: 1M-row, 20-column CSV (about 150 MB) imports on staging under 4 minutes with memory under 512 MB (bench committed).
* Playwright: upload CSV, correct one inferred type, dry run, commit, open table; Excel with two sheets; Google Sheets via mocked OAuth; screenshots at 320, 375, 768, 1024, 1280, 1536 and 1920 in light and dark for upload, mapping and result.
* Template download test.
* `docs/migration/spreadsheets.md` (supported formats, inference rules, limits); CHANGELOG entry; Linear comment with recording and bench.
EDGE:
* Ragged rows (fewer or more cells than headers): missing become null, extras go to an "Overflow" text column with a warning count.
* Duplicate header names: suffixed `(2)`, `(3)`, reported.
* Numbers with mixed locales in one column (1,5 and 1.5): inferred text with a warning and a locale override option.
* 10k-row CSV where one row has a date in a different format: parsed with fallback formats; unparseable values become null and are listed.
* Excel file is password protected or corrupt: error before wizard with a retry hint.
* Google token expired mid-stream: connector refreshes once, else run pauses in `failed` resumable state.
DEPS: `migration/import-framework` (hard). `data-layer/file-storage` (uploads), Google OAuth connection from `identity/better-auth` providers, `tables/grid-view` for the result view. Referenced by empty states in `growth/crm-views` and `pm-linear/board-views`.


## PAP-201 [P2 Build S prio2 Backlog] Persist external ID mappings for re-sync and incremental imports
key=migration/id-mapping milestone=Import framework and CSV agent=Built by Scout (Import Mapper). Reviewed by Sentinel (Code R
blockedBy=['PAP-199'] blocks=[]
GOAL: Make importing twice safe: a persistent mapping between every external identifier (Airtable record id, Notion page id, ClickUp task id, Stripe customer id, spreadsheet row key) and the PaperOS record it became, so re-running an import updates instead of duplicating, relations resolve across runs and sources, and incremental imports fetch only what changed since the last cursor.
SCOPE: In:

* Schema `packages/import/src/schema.ts` additions: `external_id_map` (`tenant_id`, `system` (connector name plus optional instance, e.g. `airtable:appXYZ`), `external_collection`, `external_id`, `target_table`, `target_id`, `external_updated_at`, `content_hash`, `first_run_id`, `last_run_id`, `last_seen_at`, `deleted_at`), unique `(tenant_id, system, external_collection, external_id)`, index `(tenant_id, target_table, target_id)`; `import_cursor` (`source_id`, `collection`, `cursor jsonb`, `updated_at`).
* Framework hooks in `migration/import-framework` engine: before write, look up mapping to decide create vs update (mapping beats dedupe key); after write, upsert mapping with `content_hash` (stable JSON hash of the mapped record); relation second pass resolves target ids via the map including mappings created by earlier runs and other collections; records unchanged by hash are `sk
SPEC(first 1200): * `content_hash` computed after transforms and before write, excluding volatile fields (`updated_at`, computed rollups); algorithm SHA-256 of canonical JSON.
* Conflict rules: if mapping points to a record now archived, update it and unarchive only if mapping setting says so; if mapping target was deleted, create new and mark old mapping `deleted_at` with reason.
* Two external records mapping to one target (merge in source): second mapping recorded with `merged_into`; later updates apply from either.
* Rollback of a run removes mappings it created and restores mappings it changed (framework `import_run_item.before` extended with `mappingBefore`).
* Retention: mappings kept indefinitely; `last_seen_at` allows a cleanup report for sources disconnected over 12 months.
* Performance target: lookup under 5 ms at 10M rows (btree on the unique key); relation pass uses bulk `IN` lookups per 1,000 ids.
DOD:
* Vitest: create-then-rerun yields zero duplicates and correct skip counts; changed record updates; relation across two runs resolves; source delete policies; merge-in-source; rollback restores mappings.
* Bench: 1M mappings, 100k-row rerun with 5 percent changes completes under 2 minutes on staging.
* Playwright: run the fixture connector twice, see "updated" and "skipped" counts, badge on a record with source link; screenshots at 375, 1024 and 1920 in light and dark for badge and conflicts list.
* `pm_external_ref` and `crm_external_ref` written through the helper (integration test with PM and CRM fixtures).
* `docs/migration/id-mapping.md` (rules table, incremental setup, manual relink); CHANGELOG entry; Linear comment with bench and screenshots.
EDGE:
* External id reused by the source after deletion (Airtable never does, spreadsheets can): row-key mappings include `content_hash` sanity check; mismatch surfaces as a conflict instead of silently updating.
* Same external record imported into two different target tables intentionally: allowed via distinct `external_collection` aliases; documented.
* Cursor advanced but run partially failed: cursor only advances on `succeeded`; retries reuse the old cursor.
* Source clock skew (updated_at earlier than cursor): cursors subtract a 5-minute overlap; hash prevents redundant writes.
* Manual relink to a record of a different table: rejected.
* Tenant exports and re-imports its own PaperOS export (`migration/export`): system `paperos` mappings let round-trips keep identities.
DEPS: `migration/import-framework` (hard). Coordinates with `pm-linear/pm-data-model` and `growth/crm-model` external ref tables; used by every importer and by `migration/export` round-trip.


## PAP-202 [P2 Build L prio2 Backlog] Import Airtable bases (tables, views, relations, attachments)
key=migration/airtable milestone=Airtable, Notion, ClickUp importers agent=Built by Scout (Import Mapper) with Nova (Views Engineer) co
blockedBy=['PAP-199'] blocks=[]
GOAL: Let an Airtable user move a whole base into PaperOS: every table with its field types, select options, relations (linked records), lookups and rollups recreated on the tables engine, every view (grid, kanban, calendar, gallery, form) recreated as a saved view with filters, sorts and groups, and every attachment copied into our storage before the source URLs expire.
SCOPE: In:

* Connector `packages/import/src/connectors/airtable/` using the Airtable Web API directly (fetch, no legacy SDK): OAuth 2 flow (scopes `data.records:read`, `schema.bases:read`) or PAT fallback; `discover` via `GET /v0/meta/bases` and `/v0/meta/bases/{baseId}/tables` (fields with `type` and `options`, views with `type`); `stream` via `/v0/{baseId}/{tableId}` with `pageSize 100`, `offset` paging, `returnFieldsByFieldId: true`; rate limit 5 rps per base with token bucket and 30 s backoff on 429.
* Field mapping in `mapping/airtable.ts` per `migration/format-research` matrix: singleLineText/multilineText/richText -> text/rich text, number/percent/currency -> number/currency with precision, singleSelect/multipleSelects -> select/multi-select (colours preserved), date/dateTime -> date/datetime with timezone option, checkbox, rating, url, email, phoneNumber, attachment -> attachment (stre
SPEC(first 1200): * Relation mapping creates both sides when Airtable has a symmetric link; one-way links produce a single relation field.
* Lookups and rollups are created after relations exist (third pass in the framework: create fields, import records, resolve relations, then computed fields).
* Formula translation covers the top 40 Airtable functions; unsupported functions produce a text snapshot field named `<Field> (snapshot)` and are listed in the report.
* Base with over 50k records per table: incremental capability uses `filterByFormula: LAST_MODIFIED_TIME() > '<cursor>'` for re-sync.
* Select option colours map to the nearest design-system token; option order preserved.
* Every created table records `system: airtable:<baseId>` mappings so re-import updates.
DOD:
* Vitest: field mapping for every Airtable type from the fixtures in `migration/format-research`, view filter parsing on 20 `filterByFormula` samples, formula translation table, relation two-pass, attachment streaming with mocked expiring URLs.
* Integration against a real test base (the PaperOS demo base with 8 tables, relations, lookups, rollups, 3 formulas, 40 attachments, 6 views): full import, then a re-import after edits updates without duplicates; recording attached.
* Playwright: wizard from OAuth (mocked) to imported base view; screenshots at 320, 375, 768, 1024, 1280, 1536 and 1920 in light and dark for base picker, translation report and resulting kanban view.
* Side-by-side screenshots Airtable vs PaperOS for two views attached for visual review.
* `docs/migration/airtable.md` (what maps, what does not, formula coverage list); CHANGELOG entry; Linear comment with recording and coverage stats.
EDGE:
* Linked record pointing to a table the user excluded: relation field created but empty, with a warning and a one-click "also import that table".
* Attachment URL expired before fetch (long runs): connector re-fetches the record to obtain a fresh URL, retries once.
* Field named the same as a system field (`id`, `created_at`): renamed with suffix and reported.
* Circular lookups (A looks up B which rolls up A): computed fields created in dependency order; cycles snapshotted.
* Base exceeds tenant row limits or plan entitlements: dry run states it before any write.
* PAT without schema scope: discover fails with the exact scope to add.
DEPS: `migration/import-framework` (hard). `migration/id-mapping`, `tables/field-types`, `tables/view-model-spec`, `tables/formula-engine` (soft: snapshot fallback), `data-layer/file-storage`. Uses `migration/format-research` fixtures.


## PAP-203 [P2 Build L prio2 Backlog] Import Notion databases and pages into tables and docs
key=migration/notion milestone=Airtable, Notion, ClickUp importers agent=Built by Scout (Import Mapper) with Quill for docs placement
blockedBy=['PAP-128', 'PAP-199'] blocks=[]
GOAL: Bring a Notion workspace across without flattening it: databases become tables with their property types, relations and rollups; pages become docs in the docs engine with blocks converted to MDX (or Tiptap JSON where the target is an editable doc), preserving hierarchy, inline databases, mentions, embeds and attachments; and database pages keep their body content attached to the imported record.
SCOPE: In:

* Connector `packages/import/src/connectors/notion/` on `@notionhq/client` 4.x: OAuth public integration (tenant connects, picks pages), `discover` via `search` (databases and top-level pages) and `databases.retrieve` for property schema; `stream` via `databases.query` (page size 100, cursor) and `blocks.children.list` recursively for page bodies; 3 rps token bucket with `Retry-After` handling.
* Property mapping `mapping/notion.ts`: title, rich_text, number (formats), select, multi_select, status (as select with groups noted), date (ranges to start/end pair), people (matched to users by email, else text), files (streamed to `data-layer/file-storage`), checkbox, url, email, phone_number, formula (snapshot plus translated where `tables/formula-engine` supports), relation (two-pass), rollup (created after relations), created_time, created_by, last_edited_time, last_edited_by, unique_i
SPEC(first 1200): * Rich text annotations (bold, italic, code, strikethrough, underline, colour) map to Markdown or Tiptap marks; colours dropped with a report count.
* Internal links between imported pages rewritten to the new doc slugs in a final pass using `migration/id-mapping`.
* Images: Notion-hosted URLs expire in 1 hour, fetched immediately; external URLs kept as links unless "copy external media" is ticked.
* Databases with over 10k pages use `last_edited_time` filter for incremental re-sync.
* Docs written through the docs engine's import path (`collab/docs-engine` file writer with frontmatter `source: notion`, `sourceUrl`, `imported`), committed as a branch and PR when the repo is the docs store, or written to the tenant docs table when the runtime docs store exists.
* Max page body 5 MB; larger split into sections with a warning.
DOD:
* Vitest: every property type and every block type from fixtures converts to the expected MDX and Tiptap snapshots; link rewriting; people matching; date ranges.
* Integration against the PaperOS Notion test workspace (3 databases with relations and rollups, 25 pages nested 4 deep, 30 images, inline database, synced block): full import, then re-import after edits; recording attached.
* Playwright: picker, report, browse an imported doc with images and a table view of an imported database; screenshots at 320, 375, 768, 1024, 1280, 1536 and 1920 in light and dark for picker and imported doc.
* Side-by-side Notion vs PaperOS renders for two pages attached.
* `docs/migration/notion.md` (block coverage table, limitations); CHANGELOG entry; Linear comment with recording and coverage.
EDGE:
* Page the integration was not granted: listed as "no access" in the picker with instructions, not an error.
* Relation to a database not shared with the integration: relation field created empty with a warning.
* Deeply nested toggles (10 levels): flattened beyond level 4 with a note.
* Database with two properties named identically after normalisation (`Status` and `status`): suffix and report.
* Very large workspace (50k pages): picker paginates and estimates time from `migration/format-research` throughput table.
* Archived pages: imported with `status: archived` only if the user ticks "include archived".
DEPS: `migration/import-framework` and `collab/docs-engine` (hard). `migration/id-mapping`, `realtime/collab-text` (Tiptap target, soft: MDX only until merged), `tables/field-types`, `data-layer/file-storage`.


## PAP-204 [P2 Build M prio3 Backlog] Import ClickUp and Linear workspaces into the PM module
key=migration/clickup-linear milestone=Airtable, Notion, ClickUp importers agent=Built by Scout (Import Mapper) with Atlas consulted on Linea
blockedBy=['PAP-100', 'PAP-199'] blocks=[]
GOAL: Bring project history along: import ClickUp workspaces (spaces, folders, lists, tasks, subtasks, custom fields, statuses, comments, attachments) and Linear workspaces (teams, projects, cycles, issues, sub-issues, labels, comments, relations) into the PaperOS PM module so a team switching tools keeps identifiers, states, assignees and discussion, and so PaperOS's own Linear workspace can be mirrored into the PM tables for `pm-linear/board-views`.
SCOPE: In:

* Connector `packages/import/src/connectors/clickup/` on ClickUp REST v2 (OAuth or PAT): `discover` teams -> spaces -> folders -> lists with statuses and custom field definitions; `stream` tasks per list with `include_closed=true`, `subtasks=true`, page 100, rate limit 100 rpm per token; comments via `/task/{id}/comment`; attachments from task `attachments[]` streamed to `data-layer/file-storage`; time tracking entries optional.
* Connector `packages/import/src/connectors/linear/` on `@linear/sdk`: `discover` teams, workflow states, labels, projects, milestones, cycles; `stream` issues with `filter: { updatedAt: { gt: cursor } }`, `first: 100` pagination, plus comments, attachments, relations, history optional; respects complexity-based rate limit with backoff.
* Mapping to `pm-linear/pm-data-model` tables: ClickUp space -> `pm_team`, list -> `pm_project`, statuses -> `pm_workflow_s
SPEC(first 1200): * Identifier preservation: Linear keeps `PAP-123`; ClickUp uses custom task ids if enabled else generates, and the original ClickUp id is stored in `pm_external_ref.external_id` with `external_url`.
* Ordering: `sort_order` from ClickUp `orderindex` and Linear `sortOrder`.
* Closed items imported with `completed_at` from history where available, else `date_closed`; canceled states map to `canceled` type.
* Markdown fidelity: ClickUp comment and description markup converted with a small parser (mentions `@user`, checklists, code); Linear markdown passes through with attachment URLs rewritten.
* Incremental re-import via `updatedAt` cursors using `migration/id-mapping`; issues deleted in source archived here when the "mirror deletions" toggle is on.
* Import runs as the acting staff user; created_by on imported items is the placeholder or matched user, not the importer (audit reason `import:<run_id>`).
DOD:
* Vitest: state type inference, priority mapping, identifier strategies, people matching, ClickUp markup conversion on 20 fixtures, relation mapping, incremental rerun with no duplicates.
* Integration: import the PaperOS Linear workspace (team PAP with this plan's issues) and a ClickUp test workspace (3 lists, 150 tasks, subtasks, 5 custom fields, 40 comments, 10 attachments); recordings attached; `pm-linear/board-views` renders the result.
* Playwright: wizard with state mapping and people matching; screenshots at 320, 375, 768, 1024, 1280, 1536 and 1920 in light and dark for state mapping and imported board.
* Cross-check counts: issues, comments and attachments equal source counts in the run report.
* `docs/migration/pm-tools.md`; CHANGELOG entry; Linear comment with recordings and count table.
EDGE:
* ClickUp task in multiple lists: imported once in its home list, linked via a relation note for the others.
* Linear issue with a parent in another team: parent link kept; team differs, allowed by the PM model.
* State name collision across ClickUp lists with different meanings: mapping table is per list; user can merge.
* Comment author deleted in source: attributed to a placeholder "Former member".
* Attachment behind ClickUp auth (private URL): fetched with the token; expired token pauses the run resumable.
* Importing into a team that already has issues: identifier collisions resolved by continuing the sequence and recording the source id.
DEPS: `migration/import-framework` and `pm-linear/pm-data-model` (hard). `migration/id-mapping`, `tables/field-types` (custom fields), `data-layer/file-storage`, `pm-linear/board-views` (to view the result). Coordinate with `pm-linear/linear-sync` so both write `pm_external_ref` compatibly.


## PAP-205 [P2 Build L prio2 Backlog] Export everything (tables, docs, files, ledger) to open formats
key=migration/export milestone=Airtable, Notion, ClickUp importers agent=Built by Scout (Import Mapper) with Forge for snapshot seman
blockedBy=['PAP-43', 'PAP-199'] blocks=[]
GOAL: Guarantee no lock-in: any tenant owner can export everything they own (tables with schema and views, docs, files, comments, CRM, PM, ledger and audit history) into open formats in one archive, on demand or on a schedule, complete enough that PaperOS itself can re-import it and that a competitor's tool could read it. The archive is also the hard-delete prerequisite named in `data-layer/core-entities`.
SCOPE: In:

* Export service `packages/import/src/export/`: pg-boss job `export.run` producing a zip in `data-layer/file-storage` (`exports/<tenant>/<run_id>.zip`) with a manifest; streaming zip via `archiver` 7.x so 50 GB tenants do not buffer.
* Archive layout: `manifest.json` (schema version, tenant, generated_at, counts, checksums), `schema/tables.json` (every table with field definitions in the `tables/view-model-spec` field schema, DTCG-free), `schema/views.json`, `data/tables/{table}.jsonl` and `.csv` (JSON Lines for fidelity, CSV for convenience; relations as arrays of ids), `docs/**/*.md` with frontmatter (from `collab/docs-engine` store), `files/<id>/<filename>` plus `files/index.json` (sha256, mime, references), `comments.jsonl` (`collab/comments` with anchors), `crm/*.jsonl`, `pm/*.jsonl` (with a Linear-compatible JSON shape), `finance/ledger.jsonl` and `finance/ledger.csv` (journal
SPEC(first 1200): * Permission `tenant.export` granted to `owner` by default; each export writes an `audit_event` and notifies all owners (`collab/notifications`).
* Consistency: export runs inside a `REPEATABLE READ` snapshot per table batch so tables reference a consistent point in time recorded in the manifest; files copied by sha256 verification.
* Checksums: SHA-256 per file in manifest; archive-level hash published in the history row.
* Size limits: none, but exports over 10 GB warn about download time and recommend the scheduled S3 destination.
* Schema version `1.0` documented in `docs/migration/export-format.md` with JSON Schemas for `manifest.json` and `tables.json`; changes require an ADR.
* Redaction: encrypted secrets (OAuth tokens, API keys) never included; `identity/users.jsonl` excludes credentials and passkeys.
DOD:
* Vitest: manifest and schema JSON validate against their JSON Schemas; JSONL and CSV round-trip equality for every field type; redaction; permission checks; scope filters.
* Integration: export the demo tenant (all projects' seed data), import it into an empty tenant through the `paperos` connector, and compare row counts and hashes table by table (script committed, report attached).
* Performance: 5M-row, 20 GB demo export streams to storage under 30 minutes with steady memory (bench committed).
* Playwright: start export, watch progress, download, schedule weekly; screenshots at 320, 375, 768, 1024, 1280, 1536 and 1920 in light and dark for export page and history.
* `docs/migration/export-format.md` reviewed by Quill and Atlas; CHANGELOG entry; Linear comment with round-trip report.
EDGE:
* File missing from storage (reconciliation lag): listed in `files/missing.json`, export succeeds with warning.
* Export requested while an import is running: allowed; snapshot semantics per table; manifest notes concurrent runs.
* Tenant with 2M docs versions: only current versions exported by default; `include_history` adds git history JSON.
* Passphrase lost: PaperOS cannot decrypt; UI states this on setup and requires typing a confirmation.
* Download link shared publicly: signed, 7 days, tied to owner; revocable from history.
* Formula and rollup fields: exported as both definition and last computed value.
DEPS: `migration/import-framework` (hard: round-trip connector). `data-layer/file-storage`, `collab/docs-engine`, `collab/comments`, `business-core/ledger` (finance files, soft), `pm-linear/pm-data-model`, `growth/crm-model`, `collab/notifications`. Precondition for tenant hard-delete in `data-layer/core-entities`.


## PAP-206 [P2 Build L prio3 Backlog] Import Stripe customers and subscriptions and QuickBooks/Xero charts of accounts into the ledger
key=migration/stripe-quickbooks milestone=Business migrations agent=Built by Scout (Import Mapper) with Ledger (Bookkeeper) owni
blockedBy=['PAP-179', 'PAP-199'] blocks=[]
GOAL: Let a business arrive with its finance history intact: import Stripe customers, products, prices, subscriptions and paid invoices into the CRM, billing and ledger tables, and import a QuickBooks Online or Xero chart of accounts with opening balances (and optionally historical journal lines) into the double-entry ledger, so reports in `business-core/finance-reports` are correct from day one.
SCOPE: In:

* Connector `packages/import/src/connectors/stripe/` using `stripe` Node 18.x with the tenant's restricted key or Connect account (read-only scopes): `discover` lists object types with counts; `stream` uses auto-pagination on `customers`, `products`, `prices`, `subscriptions` (all statuses), `invoices` (`status: paid|open|void|uncollectible`), `charges`, `refunds`, `payouts` with `created` cursors for incremental; respects rate limits with the SDK's retry.
* Stripe mapping: customer -> `crm_company` or `crm_contact` (by presence of a name with a domain email) plus `business-core/finance-data-model` customer with `stripe_customer_id`; products and prices -> `business-core/stripe-billing` catalog rows (marked `imported`, not re-created in Stripe); subscriptions -> subscription rows with status and period; paid invoices -> `business-core/invoicing` invoice records (PDF link kept) and l
SPEC(first 1200): * Ledger integrity: dry run must produce a balanced trial balance (debits equal credits per currency) or the commit button is disabled with the offending entries listed.
* Every posted journal carries `source: import`, `run_id`, external ids; ledger immutability means rollback posts reversing entries, never deletes (framework rollback delegates to `ledger.reverseRun(run_id)`).
* Currency: amounts in minor units; multi-currency invoices posted in transaction currency with the tenant's base currency equivalent from the invoice's exchange rate when Stripe provides it, otherwise the finance rates table.
* Stripe fees taken from `balance_transaction.fee` per charge; missing balance transactions (old data) fall back to `application_fee` or zero with a warning.
* Duplicate policy: Stripe customer matching existing CRM contact by email links rather than creates; QuickBooks customers matching by name and email offer merge.
* Conversion date before earliest data: opening journal zero; history import covers everything.
DOD:
* Vitest: every mapping rule with fixtures from `migration/format-research`; trial balance check; reversing rollback; incremental cursors; fee and tax splitting on 15 invoice fixtures including refunds and multi-currency.
* Integration: Stripe test-mode account seeded with 50 customers, 3 products, 40 subscriptions, 120 invoices and 10 refunds; QuickBooks sandbox company and Xero demo company; import all three, run `business-core/finance-reports` P&L and balance sheet and match them to the sandbox reports within rounding; recordings and comparison table attached.
* Playwright: wizard with account mapping and trial balance step; screenshots at 320, 375, 768, 1024, 1280, 1536 and 1920 in light and dark for account mapping and trial balance.
* Ledger review sign-off by Ledger (Bookkeeper) on posting rules document.
* `docs/migration/finance-imports.md`; CHANGELOG entry; Linear comment with recordings and report comparison.
EDGE:
* Stripe invoice partially paid or with credit notes: post payment portions separately; credit notes as reversing revenue entries.
* QuickBooks account codes disabled or missing: mapping by name only, flagged for review; codes generated in a reserved range.
* Xero tracking categories or QuickBooks classes: imported as ledger dimensions if `business-core/ledger` supports them, else tags with a note.
* Historical journal referencing an account the user chose not to import: run stops in dry run with the dependency listed.
* Stripe customer deleted but invoices remain: placeholder customer "Deleted Stripe customer <id>".
* Timezone of conversion date: interpreted in tenant timezone, documented on the wizard.
DEPS: `migration/import-framework` and `business-core/ledger` (hard). `business-core/finance-data-model`, `business-core/stripe-billing`, `business-core/invoicing`, `business-core/finance-reports` (verification), `growth/crm-model`, `migration/id-mapping`.


## PAP-207 [P2 Build L prio3 Backlog] Ship business-type templates (agency, retail, SaaS, clinic, restaurant) as importable seed packs
key=migration/business-templates milestone=Business migrations agent=Built by Scout (Template Packager) with Quill for starter do
blockedBy=['PAP-199', 'PAP-161'] blocks=[]
GOAL: Make one-size-fits-all real on day one: ship five business-type templates (agency, retail, SaaS, clinic, restaurant) as importable seed packs that create the tables, fields, views, pipelines, ledger chart of accounts, page specs, sample data and starter docs a business of that type expects, applied through the import framework so they can be previewed, partially applied and rolled back like any import.
SCOPE: In:

* Pack format `packages/import/templates/<type>/pack.yaml` (Zod schema in `packages/import/src/templates/schema.ts`): metadata (name, description, icon, audiences), `tables[]` (in `tables/view-model-spec` field schema), `views[]`, `pipelines[]` (CRM stages), `chartOfAccounts[]` (ledger accounts by kind and code), `segments[]`, `sequences[]` (outreach templates, unapproved), `pages[]` (page specs per `spec-builder/schema` referencing tables and views), `navigation` (app.spec additions via `spec-builder/app-level-spec`), `docs[]` (MDX starter docs), `sampleData/*.jsonl` (optional demo rows flagged `demo: true` for one-click removal), `roles[]` (staff role presets such as Stylist, Server, Nurse), `entitlements` hints.
* The five packs with realistic content: agency (clients, projects, retainers, timesheets, invoices, proposal pipeline), retail (products, variants, inventory, suppliers,
SPEC(first 1200): * Packs versioned semver; `apply` records version; `upgrade` computes added tables and fields only (never removes) and runs as a dry run first.
* Sample data references stable ids so relations resolve; all sample rows carry `demo: true` and a "Remove sample data" action archives them via the framework rollback of the sample sub-run.
* Clinic pack marks patient fields `sensitive: true` in page specs so `identity/rbac-abac` policies default to staff-only and `data-layer/audit-log` reason is required on reads (if supported) with a documented note.
* Each pack ships at least 3 page specs, 6 views, 1 pipeline, 1 chart of accounts, 2 segments, 1 sequence and 1 starter doc; a lint enforces minimums.
* Preview screenshots generated by Playwright from a tenant with sample data and committed to the pack folder.
DOD:
* Vitest: pack schema validation for all five, lint minimums, applier conflict strategies, composition of two packs, upgrade computes correct diff.
* Integration: apply each pack to an empty tenant with sample data, run `spec-builder/conformance-tests` on generated pages, render every view, produce a ledger trial balance of zero; then remove sample data and confirm structure remains (script and report attached).
* Playwright: gallery, dry run diff, apply, browse resulting pages; screenshots at 320, 375, 768, 1024, 1280, 1536 and 1920 in light and dark for gallery and one applied dashboard per pack (5 packs, 2 themes at 1280 minimum).
* Justin reviews the five packs' content lists in one `Needs Justin` item (business realism).
* `docs/migration/templates.md`; CHANGELOG entry; Linear comment with gallery screenshots and per-pack item counts.
EDGE:
* Tenant already has a `contacts` table with different fields: merge adds missing fields, never changes existing types; report shows the merge.
* Applying the same pack twice: mapping detects it; offers upgrade or no-op.
* Pack references a view type not yet built (Gantt): view saved with `unsupported` flag rendering as list until the engine ships.
* Rollback after users entered real data into template tables: framework refuses to delete tables with non-demo rows; removes only structure with zero rows.
* Chart of accounts conflicts with an imported QuickBooks chart (`migration/stripe-quickbooks`): pack accounts mapped by code; duplicates skipped with a note.
* Sample data in a regulated pack (clinic): clearly fictional names and a banner "Sample data" on pages until removed.
DEPS: `tables/view-model-spec` and `migration/import-framework` (hard). `spec-builder/schema`, `spec-builder/app-level-spec`, `business-core/ledger`, `growth/crm-model`, `growth/outreach-sequences` (sequence templates, soft), `app-shell/create-cli` (onboarding entry), `identity/rbac-abac`.


## PAP-208 [P2 Build M prio2 Backlog] Create the migration agent character that interviews users about current tools and runs the imports
key=migration/migration-agent milestone=Business migrations agent=Built by Scout (lead) with Quill drafting the prompt and int
blockedBy=['PAP-104', 'PAP-199'] blocks=[]
GOAL: Make migration a conversation: a Scout sub-character, Migration Guide, that interviews a new tenant about the tools they use today, proposes a migration plan (which importers, which templates, in what order, with time estimates from `migration/format-research`), runs dry runs, explains the reports in plain language, asks for the decisions only a human can make, and executes committed imports through the framework, reporting progress in-app and in Linear.
SCOPE: In:

* Character `packages/agents/characters/migration-guide.yaml` (parent Scout, `kind: sub`, model `claude-fable-5-1`, effort `high`, `permissionMode: dontAsk`, tools: Read, Grep, WebFetch, MCP `paperos-import` procedures (`sources.connect` link generation, `mappings.*`, `runs.dry`, `runs.commit` only with an approval token, `runs.rollback`), deny Bash and raw SQL; budget `perSessionUsd` 8) and prompt `packages/agents/prompts/migration-guide.md` (identity, interview style, hard limits, report format).
* Skill `.claude/skills/migrate-tenant/SKILL.md`: interview script (current tools, data volumes, what matters most, cutover date, who else uses it), plan template, decision points (dedupe strategy, people matching, identifier strategy, sample data), execution loop (dry run -> summarise -> ask -> commit), completion checklist (counts match, spot checks, export baseline taken via `migration
SPEC(first 1200): * Approval token: `runs.commit` requires `approvalToken` minted by the UI button click (or a Linear comment `approve <run_id>` by an owner); tokens are single use and expire in 30 minutes.
* Plan card schema: `{ steps[]: { importer, source, collections, estimateMinutes, dependsOn }, templates[], risks[], questions[] }` validated by Zod; the agent may not skip a step the plan lists without a recorded reason.
* Report card schema mirrors `import_run.stats` plus a plain-language summary limited to 150 words and the top 5 issues with suggested fixes (field-level mapping edits the agent can apply on request).
* The agent never sees raw customer records beyond dry-run examples (20 per field) and states this when asked.
* Session limits: 90 minutes or budget; on stop it writes a resumable plan file to the tenant's docs (`agents/memory`).
* Language: follows the tenant's locale for the conversation; plan and report JSON stay English.
DOD:
* Character validates and appears in the org chart; smoke transcript shows in-role interview and a refusal to commit without a token.
* End-to-end on staging: interview a scripted tenant, produce a plan, run CSV and Airtable dry runs, get approval via button, commit, take an export baseline; recording attached.
* Eval harness: five fixtures score at or above 0.8; no fixture results in an unapproved commit (hard fail).
* Vitest: approval token lifecycle, plan and report schema validation, remit checks that trigger handoff.
* Playwright: chat surface with plan card, approve button, progress; screenshots at 320, 375, 768, 1024, 1280, 1536 and 1920 in light and dark.
* `docs/agents/migration-guide.md` and skill doc; CHANGELOG entry; Linear comment with recording and eval scores; Justin approves the character in one `Needs Justin` item.
EDGE:
* Tenant names a tool without an importer (Monday, HubSpot): agent proposes CSV export path with the exact export steps from `migration/format-research` and files a feature request comment.
* Dry run reveals 30 percent errors: agent must not commit; proposes mapping fixes and reruns dry, up to 3 iterations before escalating.
* Owner walks away mid-plan: state saved; next session resumes with a summary.
* Two owners give conflicting answers: agent records both and asks for one decision, no guessing.
* Source OAuth expires during the session: agent asks the owner to reconnect via link; never asks for passwords.
* Approval given by a non-owner: token minting is permission-gated; agent explains who can approve.
DEPS: `migration/import-framework` and `agents/roster-v1` (hard). `agents/skills-library`, `agents/eval-harness`, `agents/handoffs`, `agents/memory`, `collab/prompt-log-store`, `realtime/collab-text` and `realtime/agent-presence` (fallback: plain message list), `migration/export`, importers as available.
