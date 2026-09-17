DOC = "https://linear.app/paperos/document/round-2-pending-issues-migration-20-6cb063cc1be6"
DESCRIPTIONS = {}

DESCRIPTIONS["PAP-198"] = """**Goal**

Before any importer is written, know exactly what each source lets us pull, in what shape and how fast. Produce one verified reference sheet per source (Airtable, Notion, ClickUp, Monday, HubSpot, QuickBooks, Xero, Linear, Google Sheets), a field-type matrix and anonymised fixtures, so PAP-199 designs `SourceConnector` against real constraints and every importer starts from recorded data.

**Scope**

In:

* `docs/migration/sources/<source>.md` on a fixed template: auth (OAuth scopes or PAT), SDK (`@notionhq/client` 4.x, `@linear/sdk`, `intuit-oauth`, `xero-node`, REST for Airtable and ClickUp, GraphQL for Monday, HubSpot v3), pagination, rate limits with source URL and `checkedOn`, page sizes, incremental support, attachment URL expiry, export UI formats, webhooks, sandbox availability, quirks, terms-of-service notes, and a closing "connector implications" section (auth flow, sync strategy, attachment strategy, three hardest edge cases).
* `docs/migration/field-type-matrix.md`: every source type mapped to a PAP-164 type with a lossy flag.
* Fixtures in `packages/import/fixtures/<source>/` (anonymised, under 1 MB, covering relations, multi-select, attachments, formulas, nesting, archived items) plus recorded API responses for offline tests.
* Throughput table: 10k rows, 100k rows, 1k attachments per source at documented limits.

Out: connectors, mapping UI, sources beyond the list.

**Spec**

* Time-box 1 agent-day, 45 minutes per source; unknowns recorded as `unverified` with a link.
* Frontmatter per sheet: `source`, `checkedOn`, `sdk`, `rateLimit`, `incremental`, `attachmentExpiry`; a Vitest lint asserts presence.
* Fixtures are the seed content for `[migration/test-accounts]` (pending issue, spec in the project document), so counts match its numbers: Airtable 8 tables and 40 attachments, Notion 3 databases and 25 pages, ClickUp 3 lists and 150 tasks, Stripe 120 invoices.

**Interface contract**

Provides: the nine sheets, `field-type-matrix.md`, fixtures folder layout `fixtures/<source>/{export,api}/`, `fixtures/README.md`, and a machine-readable `docs/migration/sources/index.json` (`{ source, rateLimit, incremental, attachmentExpiry }`) that PAP-199 reads for `capabilities.rateLimit` defaults and PAP-208 reads for time estimates. Consumes: nothing in-repo; PAP-128 renders the pages when it lands. Consumers: PAP-199, PAP-200, PAP-202, PAP-203, PAP-204, PAP-206, PAP-208, `[migration/monday-hubspot-recipes]`, and PAP-188 for the HubSpot CRM mapping section.

**Definition of done**

* Nine sheets, matrix and `index.json` merged; sources index page renders in the docs engine (or as plain Markdown if PAP-128 is late).
* Fixtures for Airtable, Notion, ClickUp, Linear, QuickBooks, Stripe and CSV committed with the anonymisation README.
* Every limit and expiry claim carries a URL and `checkedOn`; lint green.
* Screenshots of each source's export UI at 1280 attached.
* CHANGELOG entry; Linear comment linking the index and notifying PAP-199, PAP-202, PAP-203, PAP-204, PAP-206.

**Test plan**

* Vitest: frontmatter lint over all sheets; `index.json` validates against a Zod schema; every fixture folder has a README and files under 1 MB.
* Fixture smoke: each recorded API fixture parses with the SDK types it claims.
* Review: Scout and Atlas sign the throughput table in the PR; disagreements resolved there.

**Demo**

Reviewer opens `docs/migration/sources/airtable.md`, checks the rate-limit line has a URL and date, opens `field-type-matrix.md` to find `rollup`, then lists `fixtures/airtable/` and sees eight table exports. Under two minutes.

**Edge cases**

* API access needs a paid plan (Airtable attachments, some ClickUp endpoints): note plan and UI-export fallback.
* Limits differ per plan or per token versus workspace: record both and the safe default.
* Soft-deleted items visible via API (Notion `archived`, Linear `trashed`): document whether to import as archived.
* Monday and HubSpot: sheets written; importer path is CSV recipes, not a connector.
* Trial workspace lacks paid features (formulas): fixture marked partial.

**Dependencies**

None; ready now. Blocks PAP-199 (interface design) and `[migration/test-accounts]` (seed content). Informs every importer.

**Agent**

Researched by Scout (Import Mapper). Reviewed by Atlas for completeness and Quill for the docs template.

**Size**

M: nine sources at 45 minutes plus fixtures and the matrix.
"""

DESCRIPTIONS["PAP-199"] = """**Goal**

Build the one pipeline every importer uses: a `SourceConnector` interface, a mapping model, an engine that streams records in batches with transforms and relation resolution, a dry run that validates without writing, a commit with progress, and a rollback that reverses a run exactly. Importers then only implement connectors. This issue is the umbrella for three work packages.

**Scope**

Work packages (full specs in the project document, ready to become sub-issues when the Linear issue cap lifts):

* **WP1 Connector interface, mapping model and engine** (M): `SourceConnector` (`discover`, `stream`, `fetchAttachment`, `capabilities`), tables `import_source`, `import_mapping`, `import_run`, `import_run_item`, pg-boss engine in batches of 500, transforms, two-pass relations, resumability, in-memory fixture connector, CLI `pnpm paperos import`.
* **WP2 Dry run, commit and rollback** (M): transaction-rolled dry run with grouped report, `before` capture, exact rollback with conflict listing and `--force`, cancellation, connector `onRollback` hook for ledger-backed tables.
* **WP3 Type inference, wizard and run history** (M): `infer.ts`, wizard routes under `_app/settings/import/`, `registerWizardStep`, run history with drill-down and guarded rollback button.

Out: concrete connectors (PAP-200 to PAP-207), scheduled re-sync, two-way sync.

**Spec**

* Writes go through the PAP-164 record API so triggers, audit (`reason: import:<run_id>`) and search apply; never raw SQL.
* Mapping beats dedupe key; both consult PAP-201 once it lands.
* Limits: 5M rows and 10 GB attachments per run, 2 concurrent runs per tenant, refused before start.
* Progress via PAP-143 shapes with 2 s polling fallback.
* Build order WP1 -> WP2 -> WP3 on branches `PAP-199/wp<n>-<slug>`; each reported in a comment here.

**Interface contract**

Provides: `SourceConnector`, `SourceSchema`, `SourceRecord`, `MappingDefinition` (Zod), `registerConnector()`, `registerWizardStep()`, `runImport()`, `runDry()`, `rollbackRun()`, `inferTypes()`, tables above with RLS, event `import.run.progress`, components `MappingTable`, `RunReport`, `RunHistory`, CLI. Consumes: PAP-164 field types and record API, PAP-43 pg-boss, PAP-37 storage, PAP-38 audit, PAP-143 (soft), PAP-165 grid (soft), PAP-198 `index.json`. Consumers: every migration issue, PAP-208 `runs.*` procedures, PAP-207 applier.

**Definition of done**

* All three work packages merged and reported.
* Integration test `import-framework.e2e`: fixture connector wizard end to end with a deliberate error in dry run, commit of 10k rows, edit one record, rollback shows one conflict, `--force` completes; audit rows and mappings verified.
* 100k-row fixture run under 5 minutes on staging (bench committed); resume after crash proven.
* `docs/migration/framework.md`; CHANGELOG; Linear comment with recording and bench.

**Test plan**

* Vitest per WP (registry, transforms, inference on 15 columns, before-state, rollback ordering, cancellation).
* Property test: random import and rollback sequences return a table to its prior hash.
* Playwright: wizard, report, history; visual baselines at 320, 375, 768, 1024, 1280, 1536 and 1920 in light and dark; axe clean; keyboard-only mapping step.
* Bench script in `bench/`.

**Demo**

Reviewer opens Settings > Import, picks the fixture connector, accepts inferred types, reads the dry-run report, commits, then rolls back from Run history. Under two minutes.

**Edge cases**

* Field type changes mid-stream: item error, not a crash.
* Circular relations: two-pass resolution.
* RLS denies the actor: reported in dry run.
* Attachment fails after record created: error item plus retry job.
* User cancels: `cancelled` with partial rollback offered.

**Dependencies**

PAP-164 and PAP-43 (hard), PAP-198 (interface inputs), PAP-37, PAP-38, PAP-143 and PAP-165 (soft). Blocks PAP-200 to PAP-208 and the pending gap issues.

**Agent**

Built by Scout (Import Mapper) with Nova on the record API and Iris on the wizard. Reviewed by Sentinel (Code Reviewer, Security Auditor, Edge Case Hunter) and Atlas.

**Size**

L umbrella; three M work packages. Pending sub-issue specs: {DOC}
"""

DESCRIPTIONS["PAP-200"] = """**Goal**

Make spreadsheets the universal on-ramp: import CSV, TSV, Excel and Google Sheets into new or existing tables with correct type inference, header detection, multi-sheet handling and streaming for large files, on top of the framework so dry runs and rollback come free.

**Scope**

In:

* Connectors in `packages/import/src/connectors/`: `csv` (Papa Parse 5.x streaming, delimiter and encoding sniffing via `chardet`, RFC 4180, BOM), `excel` (ExcelJS 4.4 streaming for `.xlsx`; `.xls` read-only via `xlsx`, flagged legacy; one collection per worksheet; merged cells, formula values, 1900 and 1904 date systems), `gsheets` (Sheets API v4 via `googleapis` with the tenant's Google connection; one collection per tab).
* Uploads to 1 GB through PAP-37 multipart; connectors read the storage stream.
* Header detection heuristic with wizard override; `Column A` names when absent.
* Spreadsheet inference extras: percent strings, accounting negatives, locale thousands separators, Excel errors as null with warning, leading-zero codes kept as text.
* Entry points: `Import` button in empty table states, settings wizard, customer portal upload when a page spec sets `import: true`.
* CSV templates generated from any table's fields.

Out: writing back, live Sheets sync, OpenDocument, PDF tables.

**Spec**

* Sniffing on the first 64 KB; delimiters `, ; \\t |`; encodings UTF-8, UTF-16, Windows-1252; manual override.
* Excel cells with date formats become `date` or `datetime`; plain numbers stay numbers.
* Sheets over 5M cells or protected: clear error with CSV fallback link.
* Multi-sheet: one target per sheet; two-column unique sheets suggested as select options or relations.
* Over 200k rows: wizard offers a one-click 10k-sample dry run.

**Interface contract**

Provides: `registerConnector('csv'|'excel'|'gsheets')`, `sniff(buffer): { delimiter, encoding, hasHeader }`, `detectSourcePreset(headers)` hook consumed by `[migration/monday-hubspot-recipes]`, wizard steps `FileUpload`, `SheetPicker`, `HeaderOverride`, component `ImportButton` for empty states, `pnpm paperos template-csv <table>`. Consumes: PAP-199 interface and wizard registry, PAP-37 uploads, PAP-57 Google connection, PAP-165 result view. Consumers: PAP-189 and PAP-102 empty states, PAP-208, `[migration/monday-hubspot-recipes]`.

**Definition of done**

* 25 fixture files infer expected types and counts; Sheets tested with recorded responses and live against the `[migration/test-accounts]` Google app.
* 1M-row, 20-column CSV imports on staging under 4 minutes with memory under 512 MB (bench committed).
* Screenshots at 320, 375, 768, 1024, 1280, 1536 and 1920 in light and dark for upload, mapping and result; axe clean.
* `docs/migration/spreadsheets.md`; CHANGELOG; Linear comment with recording and bench.

**Test plan**

* Vitest: 25 fixtures (delimiters, encodings, BOM, quoted newlines, ragged rows, both Excel date systems, merged cells, formulas, error values, leading zeros, empty sheets, 50 columns), sniffing thresholds, template generation.
* Bench `bench/csv-1m.ts` with memory sampling.
* Playwright: CSV upload, correct one inferred type, dry run, commit, open table; two-sheet Excel; Sheets via mocked OAuth; visual baselines at the seven widths, both themes.

**Demo**

Reviewer drops `fixtures/csv/contacts-messy.csv` on an empty table, sees the delimiter and encoding detected, changes one column from text to date, runs dry, commits and opens the grid. Under two minutes.

**Edge cases**

* Ragged rows: missing become null, extras go to an `Overflow` column with a count.
* Duplicate headers: suffixed `(2)`, reported.
* Mixed locales in one column (`1,5` and `1.5`): text with warning and locale override.
* Password-protected or corrupt Excel: error before the wizard.
* Google token expires mid-stream: one refresh, then resumable `failed`.

**Dependencies**

PAP-199 (hard). PAP-37, PAP-57, PAP-165 (soft), `[migration/test-accounts]` for the live Sheets test.

**Agent**

Built by Scout (Import Mapper). Reviewed by Sentinel (Edge Case Hunter, Code Reviewer, Visual Inspector) and Quill.

**Size**

M: three connectors over one framework; parsing edge cases dominate.
"""

DESCRIPTIONS["PAP-201"] = """**Goal**

Make importing twice safe: a persistent map from every external identifier to the PaperOS record it became, so re-runs update instead of duplicate, relations resolve across runs and sources, and incremental imports fetch only what changed since the last cursor.

**Scope**

In:

* Schema: `external_id_map` (`tenant_id`, `system` such as `airtable:appXYZ`, `external_collection`, `external_id`, `target_table`, `target_id`, `external_updated_at`, `content_hash`, `first_run_id`, `last_run_id`, `last_seen_at`, `deleted_at`, `merged_into`), unique on `(tenant_id, system, external_collection, external_id)`, index on target; `import_cursor` (`source_id`, `collection`, `cursor jsonb`, `updated_at`).
* Engine hooks in PAP-199: lookup before write (mapping beats dedupe key), upsert after write with `content_hash`, unchanged records counted as `skip`, relation pass resolves through the map across runs and collections.
* Incremental mode for connectors with `capabilities.incremental`; cursor advances only on `succeeded`; source deletions handled per `onSourceDelete: ignore|archive|delete`.
* One helper `recordExternalRef()` that also writes `pm_external_ref` (PAP-100) and `crm_external_ref` (PAP-187).
* Record badge "Imported from Airtable, last synced ..." with deep link; "Mapping conflicts" list in run history.

Out: two-way sync, scheduling (a Routine calls `runIncremental`), cross-tenant mapping.

**Spec**

* `content_hash` = SHA-256 of canonical JSON after transforms, excluding volatile fields.
* Mapping to an archived record: update, unarchive only if the mapping setting says so; deleted target: create new, old mapping gets `deleted_at` with reason.
* Two external records merged in source: second mapping gets `merged_into`.
* Rollback removes mappings a run created and restores changed ones via `mappingBefore` on `import_run_item`.
* Cursors subtract a 5-minute overlap for clock skew; hash prevents redundant writes.
* Lookup under 5 ms at 10M rows; relation pass uses bulk `IN` per 1,000 ids.

**Interface contract**

Provides: tables above, `recordExternalRef()`, oRPC `import.mappings.lookup|forRecord|relink|export`, `runIncremental(sourceId)`, component `ImportedBadge`, engine hooks `beforeWrite`, `afterWrite`, `resolveRelations`. Consumes: PAP-199 engine and `import_run_item`, PAP-100 and PAP-187 ref tables. Consumers: PAP-200, PAP-202, PAP-203, PAP-204, PAP-206 (two-pass relations), PAP-205 (`system: paperos` round trip), PAP-207 (`system: template:<type>@<version>`).

**Definition of done**

* Re-run yields zero duplicates and correct skip counts; changed records update; relations across two runs resolve; delete policies and merge-in-source behave; rollback restores mappings.
* Bench: 1M mappings, 100k-row rerun with 5 percent changes under 2 minutes on staging.
* `pm_external_ref` and `crm_external_ref` written through the helper (integration test).
* Screenshots at 375, 1024 and 1920 in light and dark for badge and conflicts list.
* `docs/migration/id-mapping.md`; CHANGELOG; Linear comment with bench and screenshots.

**Test plan**

* Vitest: hash stability across key order, create-then-rerun, changed record, cross-run relation, each `onSourceDelete` policy, merge, rollback restore, relink rejection across tables.
* Bench `bench/id-mapping-1m.ts`.
* Playwright: run fixture connector twice, read "updated" and "skipped" counts, open a record badge and follow the source link; visual baselines at three widths, both themes.

**Demo**

Reviewer runs the fixture import twice, sees the second run report 0 created and N skipped, edits one source row in the fixture, runs again and sees exactly 1 updated with a badge on that record. Under two minutes.

**Edge cases**

* External id reused after deletion (spreadsheets): hash mismatch surfaces as conflict.
* Same external record into two target tables intentionally: distinct `external_collection` aliases.
* Partial failure: cursor unchanged; retry reuses it.
* Manual relink to a different table: rejected.
* PaperOS export re-imported: `system: paperos` keeps identities.

**Dependencies**

PAP-199 (hard). Coordinates with PAP-100 and PAP-187. Blocks PAP-202, PAP-203, PAP-204, PAP-205, PAP-206.

**Agent**

Built by Scout (Import Mapper). Reviewed by Sentinel (Code Reviewer, Edge Case Hunter) and Forge (Schema Wright) for indexes.

**Size**

S: two tables and engine hooks; the rules are the work.
"""

DESCRIPTIONS["PAP-202"] = """**Goal**

Let an Airtable user move a whole base into PaperOS: every table with field types, options, linked records, lookups and rollups recreated on the tables engine, every view recreated as a saved view, every attachment copied before the source URL expires. Umbrella for three work packages.

**Scope**

Work packages (full specs in the project document):

* **WP1 Connector** (M): OAuth 2 (`data.records:read`, `schema.bases:read`) or PAT, metadata discovery, `stream` with `pageSize 100` and `offset`, 5 rps token bucket, 429 backoff, incremental via `LAST_MODIFIED_TIME()`, expiring attachment refresh.
* **WP2 Field mapping** (M): all 25 Airtable types per the PAP-198 matrix, relations two-pass, lookups and rollups in a third `computedFields` pass, formula translation of the top 40 functions with `<Field> (snapshot)` fallback and report.
* **WP3 Views and wizard** (M): grid, kanban, calendar, gallery and form views to PAP-161 definitions, `filterByFormula` parser, base picker, table selection, view toggle, side-by-side review.

Out: automations, interfaces, synced tables (plain tables with a note), comments, revision history.

**Spec**

* Symmetric links create one relation with both sides; one-way links one field.
* Select colours map to the nearest PAP-66 token; option order kept.
* Tables record `system: airtable:<baseId>` mappings so re-import updates.
* Order WP1 -> WP2 -> WP3 on `PAP-202/wp<n>-<slug>` branches.

**Interface contract**

Provides: `registerConnector('airtable')`, `mapAirtableField()`, `translateFormula()`, framework pass `computedFields` (reused by PAP-203 rollups), `parseFilterByFormula()` (reused by PAP-207), wizard steps, coverage table in `docs/migration/airtable.md`. Consumes: PAP-199 interface, wizard registry and passes; PAP-201 mappings; PAP-164 types; PAP-161 views; PAP-168 forms (soft); PAP-171 formulas (soft, snapshot fallback); PAP-37 storage; PAP-198 fixtures; `[migration/test-accounts]` demo base.

**Definition of done**

* Three work packages merged and reported.
* Integration test against the PaperOS demo base (8 tables, relations, lookups, rollups, 3 formulas, 40 attachments, 6 views): full import, then re-import after edits with zero duplicates; record and relation counts equal the API's; recording attached.
* Two side-by-side Airtable versus PaperOS view screenshots attached.
* Screenshots at 320, 375, 768, 1024, 1280, 1536 and 1920 in light and dark for base picker, translation report and kanban; axe clean.
* `docs/migration/airtable.md`; CHANGELOG; Linear comment with recording and coverage stats.

**Test plan**

* Vitest: pagination and rate limiter with msw, one fixture per field type, 40 supported and 5 unsupported formulas, 20 `filterByFormula` samples, symmetric link detection, cyclic lookups, attachment refresh path.
* Framework `connectorConformance()` suite.
* Playwright: wizard from mocked OAuth to kanban; visual baselines at the seven widths, both themes.
* Live integration weekly via the fixtures health workflow.

**Demo**

Reviewer runs the Airtable wizard against the demo base with views on, reads the translation report (3 translated, 1 snapshotted), then opens the recreated kanban grouped by Status with the same cards as Airtable. Under two minutes.

**Edge cases**

* Link to an excluded table: empty relation plus one-click "also import that table".
* Attachment URL expired: re-fetch record once for a fresh URL.
* Field named `id`: suffixed and reported.
* Base exceeds tenant row limits: stated in dry run.
* PAT without schema scope: exact scope named in the error.

**Dependencies**

PAP-199 (hard), PAP-201, PAP-164, PAP-161, PAP-198, `[migration/test-accounts]` (integration). Soft: PAP-171, PAP-168, PAP-37.

**Agent**

Built by Scout (Import Mapper) with Nova (Views Engineer). Reviewed by Sentinel (Edge Case Hunter, Code Reviewer, Visual Inspector, Security Auditor) and Quill.

**Size**

L umbrella; three M work packages. Pending sub-issue specs: {DOC}
"""

DESCRIPTIONS["PAP-203"] = """**Goal**

Bring a Notion workspace across without flattening it: databases become tables with property types, relations and rollups; pages become docs (MDX for the docs engine, Tiptap JSON for editable documents) with hierarchy, media, mentions and embeds; database pages keep their body attached to the record. Umbrella for three work packages.

**Scope**

Work packages (full specs in the project document):

* **WP1 Connector and property mapping** (M): OAuth public integration, `search` and `databases.retrieve` discovery, `databases.query` streaming at 3 rps with `Retry-After`, incremental by `last_edited_time`, all 20 property types, relations two-pass, rollups via the shared `computedFields` pass.
* **WP2 Block converter** (M): `toMdx` and `toTiptap` for every block type, annotation marks, media uploaded within the one-hour URL window, internal link rewriting through PAP-201, 5 MB body sectioning.
* **WP3 Hierarchy, picker and report** (S): page tree picker with counts and "no access" rows, docs placed under `docs/imported/notion/<workspace>/<path>` with `_meta.yaml`, bodies over 2,000 words as linked docs, conversion report.

Out: comments, permissions, Notion AI properties, wiki verification.

**Spec**

* Colours dropped and counted; callouts to `<Callout>`; equations KaTeX; columns flattened with a note.
* Docs written through the PAP-128 import path (branch and PR when the repo is the store; tenant docs table when a runtime store exists).
* Order WP1 -> WP2 -> WP3 on `PAP-203/wp<n>-<slug>` branches.

**Interface contract**

Provides: `registerConnector('notion')`, `mapNotionProperty()`, `toMdx()`, `toTiptap()`, `ConversionReport`, `rewriteLinks` pass, `placeDocs()`, frontmatter `source: notion`, `sourceUrl`, `imported`, wizard steps. The block converter is reused by PAP-204 for ClickUp docs later. Consumes: PAP-199 interface and wizard, PAP-202 WP2 `computedFields`, PAP-128 MDX components and file writer, PAP-142 Tiptap schema (soft: MDX only until merged), PAP-201, PAP-164, PAP-37, PAP-198 fixtures, `[migration/test-accounts]` workspace.

**Definition of done**

* Three work packages merged and reported.
* Integration test against the PaperOS Notion test workspace (3 databases with relations and rollups, 25 pages 4 deep, 30 images, inline database, synced block): full import then re-import after edits; counts equal Notion's; zero broken internal links; recording attached.
* Two side-by-side Notion versus PaperOS renders attached.
* Screenshots at 320, 375, 768, 1024, 1280, 1536 and 1920 in light and dark for picker and imported doc; axe clean.
* `docs/migration/notion.md` with property and block coverage tables; CHANGELOG; Linear comment.

**Test plan**

* Vitest: every property type and block type with MDX and Tiptap snapshots, marks, nested lists, date ranges, people matching, link rewriting, body splitting, `Retry-After` handling, cursor pagination.
* Conformance suite; broken-link check over converted output.
* Playwright: picker, target choice, report, browse an imported doc and table view; visual baselines at the seven widths, both themes.

**Demo**

Reviewer opens the Notion wizard, ticks a top-level page and one database, commits, browses the imported docs tree with a callout, table and image, and opens the database as a grid with a working relation column. Under two minutes.

**Edge cases**

* Page not granted to the integration: "no access" row with instructions.
* Relation to an unshared database: empty with warning.
* Toggles beyond level 4: flattened with a note.
* Two properties normalising to one name: suffixed.
* 50k pages: picker loads children on expand; duration estimated from PAP-198.
* Archived pages only with "include archived".

**Dependencies**

PAP-199 and PAP-128 (hard), PAP-202 WP2 (shared pass), PAP-201, PAP-164, `[migration/test-accounts]`. Soft: PAP-142, PAP-37.

**Agent**

Built by Scout (Import Mapper) with Quill for docs placement. Reviewed by Sentinel (Edge Case Hunter, Code Reviewer, Visual Inspector) and Nova for Tiptap validity.

**Size**

L umbrella; two M and one S work package. Pending sub-issue specs: {DOC}
"""

DESCRIPTIONS["PAP-204"] = """**Goal**

Bring project history along: import ClickUp workspaces (spaces, folders, lists, tasks, subtasks, custom fields, statuses, comments, attachments) and Linear workspaces (teams, projects, cycles, issues, sub-issues, labels, comments, relations) into the PM module so a switching team keeps identifiers, states, assignees and discussion, and so PaperOS's own Linear workspace can be mirrored into PM tables for PAP-102.

**Scope**

In:

* `connectors/clickup/` on REST v2 (OAuth or PAT): discover teams, spaces, folders, lists with statuses and custom fields; stream tasks per list with `include_closed`, `subtasks`, page 100, 100 rpm; comments; attachments streamed to PAP-37.
* `connectors/linear/` on `@linear/sdk`: discover teams, states, labels, projects, milestones, cycles; stream issues with `updatedAt` cursor, `first: 100`, comments, attachments, relations; complexity-aware backoff.
* Mapping to PAP-100 tables: space -> `pm_team`, list -> `pm_project`, statuses -> `pm_workflow_state` with type inferred, task -> `pm_issue` (identifier preserved or generated, priority 1-4, dates, estimate), subtask -> `parent_id`, tags -> `pm_label`, dependencies -> `pm_issue_relation blocks`, comments -> `pm_comment` (ClickUp markup to Markdown), custom fields -> typed `custom jsonb`; Linear one-to-one.
* People matching by email; unmatched become `placeholder` users per a wizard toggle.
* Wizard steps: workspace picker, team and list selection with counts, state mapping table, people matching table, identifier strategy.

Out: ClickUp docs and whiteboards, Linear roadmaps and initiatives, time-tracking reports, two-way sync (PAP-101).

**Spec**

* Linear keeps `PAP-123`; ClickUp uses custom task ids if enabled, else generates, storing the original in `pm_external_ref` with `external_url`.
* Ordering from `orderindex` and `sortOrder`; closed items get `completed_at` from history or `date_closed`.
* Import runs as the acting staff user; `created_by` is the matched or placeholder user; audit reason `import:<run_id>`.
* Incremental via `updatedAt` cursors with PAP-201; "mirror deletions" toggle archives here.

**Interface contract**

Provides: `registerConnector('clickup'|'linear')`, `mapClickUpMarkup(text): string`, `inferStateType(status)`, wizard steps `StateMapping`, `PeopleMatching`, `IdentifierStrategy` (reusable by future PM importers), writes `pm_external_ref` through PAP-201's helper compatibly with PAP-101. Consumes: PAP-199, PAP-100 tables, PAP-201, PAP-164 for custom fields, PAP-37, PAP-102 to view results, `[migration/test-accounts]` ClickUp workspace, PAP-198 fixtures.

**Definition of done**

* Integration: import team PAP from Linear (this plan) and the ClickUp test workspace (3 lists, 150 tasks, subtasks, 5 custom fields, 40 comments, 10 attachments); PAP-102 renders both; counts of issues, comments and attachments equal the sources; recordings attached.
* Rerun produces zero duplicates.
* Screenshots at 320, 375, 768, 1024, 1280, 1536 and 1920 in light and dark for state mapping and imported board; axe clean.
* `docs/migration/pm-tools.md`; CHANGELOG; Linear comment with recordings and count table.

**Test plan**

* Vitest: state type inference, priority mapping, identifier strategies, people matching, 20 ClickUp markup fixtures, relation mapping, incremental rerun, complexity backoff with recorded Linear responses.
* Conformance suite for both connectors.
* Playwright: wizard with state mapping and people matching; visual baselines at the seven widths, both themes.

**Demo**

Reviewer runs the Linear connector against team PAP with a read-only key, maps states one-to-one, commits, and opens the PM board showing this plan's issues grouped by state with comments intact. Under two minutes.

**Edge cases**

* Task in multiple lists: imported once with a relation note.
* Parent in another team: kept; allowed by the PM model.
* Same state name with different meanings across lists: mapping is per list; user may merge.
* Deleted comment author: placeholder "Former member".
* Private attachment URL and expired token: run pauses resumable.
* Target team already has issues: sequence continues; source id recorded.

**Dependencies**

PAP-199 and PAP-100 (hard). PAP-201, PAP-164, PAP-37, PAP-102, `[migration/test-accounts]`. Coordinate with PAP-101 on `pm_external_ref`.

**Agent**

Built by Scout (Import Mapper) with Atlas on Linear fidelity. Reviewed by Sentinel (Code Reviewer, Edge Case Hunter) and Forge (Schema Wright).

**Size**

M: two connectors; the target model mirrors Linear, ClickUp mapping is the bulk.
"""

DESCRIPTIONS["PAP-205"] = """**Goal**

Guarantee no lock-in: any tenant owner exports everything they own (tables with schema and views, docs, files, comments, CRM, PM, ledger, audit) into one open archive, on demand or scheduled, complete enough that PaperOS re-imports it losslessly and another tool can read it. It is also the hard-delete prerequisite named in PAP-33. Umbrella for three work packages.

**Scope**

Work packages (full specs in the project document):

* **WP1 Format v1.0 and streaming job** (M): `manifest.json` with counts and SHA-256, JSON Schemas for manifest and `tables.json`, writers for every domain (`data/tables/*.jsonl|csv`, `docs/**/*.md`, `files/`, `comments.jsonl`, `crm/`, `pm/` Linear-compatible, `finance/ledger.*` and `chart-of-accounts.csv`, `audit/`, `identity/users.jsonl` without credentials), `archiver` streaming zip, `REPEATABLE READ` snapshots per table batch, redaction, scoping.
* **WP2 UI, scheduling and links** (M): `_app/settings/export`, permission `tenant.export`, signed 7-day revocable links, weekly export to the tenant's S3 or Google Drive with `age` or AES-256 passphrase encryption, audit event and owner notification.
* **WP3 Round-trip connector and verification** (M): `paperos` connector importing the archive with identities preserved (`system: paperos`), `verifyRoundTrip` comparing counts and hashes, nightly demo-tenant round trip.

Out: real-time replication, other tenants' data, per-person DSAR export (PAP-221 reuses the layout).

**Spec**

* Format changes require an ADR; `docs/migration/export-format.md` documents v1.0.
* Secrets, tokens, passkeys never exported; formula and rollup fields exported as definition plus last value.
* Exports over 10 GB warn and recommend the scheduled destination.
* Order WP1 -> WP3 -> WP2 acceptable if the UI blocks on design; report each on `PAP-205/wp<n>-<slug>`.

**Interface contract**

Provides: job `export.run`, `ExportManifest` (Zod), `registerExportDomain(name, writer)` implemented by business-core, growth and pm-linear for their tables, event `export.completed`, oRPC `export.start|list|revokeLink|schedule.*`, permission `tenant.export`, `registerConnector('paperos')`, `verifyRoundTrip()`, CLI `pnpm paperos export`. Consumes: PAP-199 engine, PAP-201, PAP-43, PAP-37, PAP-128, PAP-131, PAP-179 (soft), PAP-100, PAP-187, PAP-38, PAP-59, PAP-136 (soft), PAP-57 Google connection.

**Definition of done**

* Three work packages merged and reported.
* Integration test: export the demo tenant, import into an empty tenant through `paperos`, `roundtrip.json` shows zero mismatches; restore into the same tenant is idempotent; report attached.
* 5M-row, 20 GB export streams under 30 minutes with flat memory (bench committed).
* Scheduled encrypted export lands in MinIO and decrypts.
* Screenshots at 320, 375, 768, 1024, 1280, 1536 and 1920 in light and dark for export page and history; axe clean.
* `docs/migration/export-format.md` reviewed by Quill and Atlas; CHANGELOG; Linear comment with round-trip report.

**Test plan**

* Vitest: schema validation, JSONL and CSV round-trip per field type, redaction, scope filters, snapshot consistency, permission checks, link expiry and revocation, hash comparison.
* Bench `bench/export-20gb.ts`.
* Playwright: start, progress, download, revoke (403 afterwards), schedule; visual baselines at the seven widths, both themes.
* Nightly staging job posts the round-trip report.

**Demo**

Reviewer starts a tables-only export from Settings > Export, downloads it, unzips to see `manifest.json` and JSONL, then runs `pnpm export:verify demo empty` after importing it and reads an all-green report. Under two minutes on the fixture tenant.

**Edge cases**

* File missing from storage: `files/missing.json`, warning, export succeeds.
* Export during an import: allowed; manifest notes it.
* 2M doc versions: current only by default; `include_history` adds git history.
* Passphrase lost: unrecoverable, stated before saving.
* Shared download link: signed, owner-bound, revocable.
* Newer archive version on import: refused with upgrade hint.

**Dependencies**

PAP-199 (hard), PAP-201, PAP-43, PAP-37, PAP-128, PAP-131, PAP-59, PAP-38. Soft: PAP-179, PAP-136, PAP-57. Precondition for tenant hard-delete in PAP-33.

**Agent**

Built by Scout (Import Mapper) with Forge for snapshot semantics, Ledger for finance files and Iris for the page. Reviewed by Sentinel (Security Auditor, Edge Case Hunter) and Atlas.

**Size**

L umbrella; three M work packages. Pending sub-issue specs: {DOC}
"""

DESCRIPTIONS["PAP-206"] = """**Goal**

Let a business arrive with its finance history intact: Stripe customers, products, prices, subscriptions and invoices into CRM, billing and ledger; a QuickBooks Online or Xero chart of accounts with opening balances into the double-entry ledger; reports in PAP-183 correct from the conversion date. Umbrella for three work packages.

**Scope**

Work packages (full specs in the project document):

* **WP1 Stripe connector and postings** (M): `stripe` Node 18.x with restricted key or Connect account, auto-pagination with `created` cursors; customer -> `crm_contact|crm_company` plus finance customer; products and prices -> PAP-177 catalog marked `imported`; subscriptions; paid invoices -> PAP-180 records and balanced journals (AR, cash, revenue per product, fee expense from `balance_transaction.fee`, tax liability); refunds reversing; payouts as transfers.
* **WP2 QuickBooks and Xero connectors** (M): `intuit-oauth` Accounting API with CDC; `xero-node` 6.x with `If-Modified-Since`; chart of accounts to ledger `kind|code|name|parent|currency|is_active`; opening journal on the conversion date; optional history.
* **WP3 Finance wizard** (M): conversion date, account mapping review with suggested matches, duplicate customer resolution, trial balance gate per currency, reversing rollback via `ledger.reverseRun(run_id)`.

Out: writing back to any source, payroll history (PAP-181 scope), inventory, multi-entity consolidation.

**Spec**

* Amounts in minor units in transaction currency with base equivalent from the invoice rate or the rates table.
* Ledger immutability: rollback posts reversing entries dated at rollback time, never deletes.
* Every journal carries `source: import`, `run_id`, external ids.
* Order WP1 and WP2 in parallel, then WP3, on `PAP-206/wp<n>-<slug>`.

**Interface contract**

Provides: `registerConnector('stripe'|'quickbooks'|'xero')`, pure `postingRulesStripe(invoice): JournalLine[]` for Ledger review, `mapChartOfAccounts()`, `openingJournal()`, `trialBalance(preview)`, `ledger.reverseRun()`, component `JournalPreview` (reusable by PAP-180), wizard steps. Consumes: PAP-199, PAP-179 `postJournal` and accounts, PAP-175, PAP-177, PAP-180, PAP-183 (verification), PAP-187, PAP-201, `[migration/test-accounts]` sandboxes. PAP-207 consumes the chart mapping for code conflicts.

**Definition of done**

* Three work packages merged and reported.
* Integration test: Stripe test account (50 customers, 3 products, 40 subscriptions, 120 invoices, 10 refunds), QuickBooks sandbox and Xero demo imported; PAP-183 P&L and balance sheet match source reports within rounding (comparison table attached); rollback returns the trial balance to its prior state.
* Posting rules document signed off by Ledger (Bookkeeper).
* Screenshots at 320, 375, 768, 1024, 1280, 1536 and 1920 in light and dark for account mapping and trial balance; axe clean.
* `docs/migration/finance-imports.md`; CHANGELOG; Linear comment with recordings and comparison.

**Test plan**

* Vitest: posting rules on 15 invoice fixtures (partial payments, credit notes, multi-currency, refunds) all balanced; every QuickBooks type and subtype and Xero class mapped; opening journal balances; cursors; trial balance offenders; reversing idempotence.
* Conformance suite for three connectors; recorded API responses in CI, live sandboxes weekly.
* Playwright: wizard with an unbalanced then a balanced fixture; visual baselines at the seven widths, both themes.

**Demo**

Reviewer connects the Stripe test account, walks the wizard, sees one duplicate customer resolved and the trial balance green, commits, then clicks Rollback and sees reversing entries in the journal. Under two minutes.

**Edge cases**

* Partially paid invoice or credit note: separate payment portions; credit notes reverse revenue.
* Missing or disabled QuickBooks codes: mapped by name, flagged, reserved range.
* Tracking categories and classes: dimensions if PAP-179 supports them, else tags.
* Journal references an unimported account: dry run stops with the dependency.
* Deleted Stripe customer: placeholder.
* Conversion date in tenant timezone.

**Dependencies**

PAP-199 and PAP-179 (hard). PAP-175, PAP-177, PAP-180, PAP-183, PAP-187, PAP-201, `[migration/test-accounts]`.

**Agent**

Built by Scout (Import Mapper) with Ledger (Bookkeeper) owning posting rules and Iris on the wizard. Reviewed by Sentinel (Security Auditor, Code Reviewer, Visual Inspector) and Ledger.

**Size**

L umbrella; three M work packages. Pending sub-issue specs: {DOC}
"""

DESCRIPTIONS["PAP-207"] = """**Goal**

Make one-size-fits-all real on day one: five business templates (agency, retail, SaaS, clinic, restaurant) as importable seed packs that create tables, views, pipelines, chart of accounts, page specs, sample data and starter docs, applied through the import framework so they preview, partially apply and roll back like any import. Umbrella for three work packages.

**Scope**

Work packages (full specs in the project document):

* **WP1 Pack format and applier** (M): `pack.yaml` Zod schema with `tables[]`, `views[]`, `pipelines[]`, `chartOfAccounts[]`, `segments[]`, `sequences[]`, `pages[]`, `navigation`, `docs[]`, `sampleData/*.jsonl` (`demo: true`), `roles[]`, `entitlements`; lint minimums; `template` `SourceConnector`; conflict strategy `skip|merge|rename`; `extends: base`; multi-pack composition; additive `upgrade`; the shared `base` pack.
* **WP2 Five packs** (M): realistic content per type, clinic fields `sensitive: true`, fictional sample data with stable ids, staff role presets, Playwright preview screenshots.
* **WP3 Gallery** (S): cards in PAP-22 onboarding and `_app/settings/templates`, dry-run diff, "apply with sample data", "Remove sample data" banner action, upgrade prompt.

Out: industry integrations (POS hardware, EHR), compliance certification (HIPAA notes only), localisation beyond English.

**Spec**

* Packs are semver; `apply` records `system: template:<type>@<version>` so re-apply offers upgrade; upgrade never removes.
* Sample data runs as a sub-run so removal is a framework rollback of that sub-run.
* Lint minimums per pack: 3 page specs, 6 views, 1 pipeline, 1 chart, 2 segments, 1 sequence, 1 doc.
* Order WP1 -> WP2 -> WP3 on `PAP-207/wp<n>-<slug>`.

**Interface contract**

Provides: `PackSchema`, `registerConnector('template')`, `lintPack()`, `planUpgrade()`, CLI `pnpm template lint|apply|upgrade`, five packs with previews, `TemplateStep` for PAP-22, route `_app/settings/templates`, components `TemplateCard`, `PackDiff`, `SampleDataBanner`. Consumes: PAP-199 engine, dry run and `RunReport`; PAP-161 field and view schema; PAP-114 page specs; PAP-117 navigation; PAP-179 accounts; PAP-187 pipelines; PAP-191 sequence format (soft); PAP-59 role presets; PAP-122 conformance; PAP-201; PAP-206 chart mapping for code conflicts. PAP-208 reads pack metadata to recommend templates.

**Definition of done**

* Three work packages merged and reported.
* Integration test: apply each pack with sample data to an empty tenant; every generated page passes PAP-122 conformance; every view renders; trial balance is zero; remove sample data leaves structure intact (script and report attached). Applying a bumped version upgrades additively; composing clinic plus retail works.
* Justin reviews the five content lists in one Needs Justin item.
* Screenshots at 320, 375, 768, 1024, 1280, 1536 and 1920 in light and dark for gallery and one dashboard per pack at 1280 in both themes; axe clean.
* `docs/migration/templates.md`; CHANGELOG; Linear comment with gallery and item counts.

**Test plan**

* Vitest: schema, every lint rule, `extends` merge, composition, conflict strategies, upgrade diff, sample sub-run rollback, sensitive annotations in clinic.
* Integration script `scripts/templates-verify.ts` in CI on the small fixture tenant.
* Playwright: gallery, diff, apply, browse, remove sample data; visual baselines at the seven widths, both themes.

**Demo**

Reviewer opens Settings > Templates, applies Restaurant with sample data, lands on the reservations calendar with tonight's fictional bookings, then clicks "Remove sample data" and sees the empty calendar with structure intact. Under two minutes.

**Edge cases**

* Existing `contacts` table with different fields: merge adds fields, never changes types.
* Same pack twice: detected, upgrade or no-op.
* Unbuilt view kind (Gantt): saved `unsupported`, renders as list.
* Rollback after real rows: non-demo tables kept.
* Chart conflicts with an imported QuickBooks chart: matched by code, duplicates skipped.
* Regulated sample data: fictional names and a banner until removed.

**Dependencies**

PAP-161 and PAP-199 (hard). PAP-114, PAP-117, PAP-179, PAP-187, PAP-59, PAP-122, PAP-201. Soft: PAP-191, PAP-22.

**Agent**

Built by Scout (Template Packager) with Quill for docs, Beacon for CRM and sequences, Iris for the gallery. Reviewed by Sentinel (Visual Inspector, Code Reviewer, Edge Case Hunter), Ledger for charts and Justin for realism.

**Size**

L umbrella; two M and one S work package. Pending sub-issue specs: {DOC}
"""

DESCRIPTIONS["PAP-208"] = """**Goal**

Make migration a conversation: a Scout sub-character, Migration Guide, interviews a new tenant about current tools, proposes a plan (importers, templates, order, time estimates from PAP-198), runs dry runs, explains reports plainly, asks only the decisions a human must make, and commits imports through the framework with an approval token, reporting progress in-app and in Linear.

**Scope**

In:

* Character `packages/agents/characters/migration-guide.yaml` (parent Scout, `kind: sub`, model `claude-fable-5-1`, effort `high`, `permissionMode: dontAsk`; tools Read, Grep, WebFetch and MCP `paperos-import` procedures `sources.connect`, `mappings.*`, `runs.dry`, `runs.commit` with approval token, `runs.rollback`; Bash and raw SQL denied; `perSessionUsd` 8) and prompt `packages/agents/prompts/migration-guide.md`.
* Skill `.claude/skills/migrate-tenant/SKILL.md`: interview script, plan template, decision points, execution loop (dry -> summarise -> ask -> commit), completion checklist with an export baseline via PAP-205.
* Chat surface `_app/settings/migrate` on PAP-142 messages with the agent as participant (PAP-146), plan and report cards as JSON blocks, approve button minting the token; exchanges logged to PAP-129.
* Capabilities and limits read at run time from PAP-198 `index.json` and the connector registry, so new importers need no prompt change.
* Handoff to Needs Justin or the owner when a decision exceeds remit (over 5M rows, regulated data, conversion dates).
* Five eval fixtures for PAP-110 with golden plans and a rubric.

Out: building importers, live sync, migrating credentials, sources the tenant has not connected.

**Spec**

* `runs.commit` requires `approvalToken` minted by the UI button or an owner's Linear comment `approve <run_id>`; single use, 30-minute expiry, permission-gated.
* Plan card `{ steps[]: { importer, source, collections, estimateMinutes, dependsOn }, templates[], risks[], questions[] }`; report card mirrors `import_run.stats` plus a 150-word summary and top five issues with suggested fixes.
* The agent sees at most 20 dry-run examples per field.
* Session cap 90 minutes or budget; resumable plan saved via PAP-109.
* Conversation follows tenant locale; JSON stays English.

**Interface contract**

Provides: character and prompt, skill, MCP server `paperos-import` exposing the procedures above with Zod schemas, `PlanCard` and `ReportCard` schemas, approval token API `import.approvals.mint|consume`, route `_app/settings/migrate`, eval fixtures. Consumes: PAP-199 `runDry|runImport|rollbackRun` and `RunReport`, PAP-104 roster, PAP-105 skill format, PAP-108 handoff protocol, PAP-109 memory, PAP-110 harness, PAP-129 log, PAP-142 and PAP-146 (fallback: plain message list), PAP-205 export, PAP-198 `index.json`, PAP-207 pack metadata, `[migration/monday-hubspot-recipes]` recipes.

**Definition of done**

* Character validates and appears in the org chart; smoke transcript shows an in-role interview and a refusal to commit without a token.
* Staging end to end: scripted tenant interviewed, plan produced, CSV and Airtable dry runs, approval by button, commit, export baseline taken; recording attached.
* Five eval fixtures score at or above 0.8; any unapproved commit is a hard fail.
* Screenshots at 320, 375, 768, 1024, 1280, 1536 and 1920 in light and dark of the chat with plan card and approve button; axe clean.
* `docs/agents/migration-guide.md`; CHANGELOG; Linear comment with recording and scores; Justin approves the character in one Needs Justin item.

**Test plan**

* Vitest: token lifecycle (single use, expiry, permission), plan and report schemas, remit checks triggering handoff, procedure allowlist (no Bash, no SQL).
* Eval harness: five interviews (agency on Airtable and QuickBooks, SaaS on Notion and Stripe, restaurant on spreadsheets, clinic on ClickUp, mixed) scored nightly.
* Playwright: chat, plan card, approve, progress; visual baselines at the seven widths, both themes.

**Demo**

Reviewer opens Settings > Migrate, names Airtable and QuickBooks in three answers, receives a plan card with estimates, requests a dry run, reads the plain-language report and clicks Approve to watch the commit. Under two minutes with fixture sources.

**Edge cases**

* Tool without an importer (Monday, HubSpot): CSV recipe path proposed.
* Dry run with 30 percent errors: no commit; three mapping iterations then escalation.
* Owner leaves mid-plan: state saved and resumed with a summary.
* Conflicting owners: both recorded, one decision requested.
* OAuth expires: reconnect link; never passwords.
* Non-owner approval: minting denied; agent names who can approve.

**Dependencies**

PAP-199 and PAP-104 (hard). PAP-105, PAP-108, PAP-109, PAP-110, PAP-129, PAP-142, PAP-146, PAP-205, importers as available.

**Agent**

Built by Scout (lead) with Quill drafting the prompt. Reviewed by Sentinel (Security Auditor, Code Reviewer); Justin approves the character.

**Size**

M: character, skill, one chat surface and evals over an existing framework.
"""

for _k in list(DESCRIPTIONS):
    DESCRIPTIONS[_k] = DESCRIPTIONS[_k].replace("{DOC}", DOC)
