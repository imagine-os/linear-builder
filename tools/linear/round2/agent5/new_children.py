# Child issues for the L-sized parents in migration and libraries.
# Phase label, milestone, project and surfaces are inherited from the parent. State: Backlog.
CHILDREN = []

def add(parent, title, type_, size, **s):
    CHILDREN.append(dict(parent=parent, title=title, type=type_, size=size, sections=s))

def render(sections):
    order = ["Goal", "Scope", "Spec", "Interface contract", "Definition of done", "Test plan", "Demo",
             "Edge cases", "Dependencies", "Agent", "Size"]
    out = []
    for k in order:
        out.append(f"**{k}**\n\n{sections[k].strip()}")
    return "\n\n".join(out) + "\n"

# ---------------- PAP-199 Import framework ----------------
add("PAP-199", "Connector interface, mapping model and import engine (`SourceConnector`, `import_mapping`, batching, resumability, fixture connector)", "Build", "M",
Goal="""Create `packages/import` with the `SourceConnector` interface, the four import tables, the pg-boss engine that streams records in batches of 500 with transforms and two-pass relation resolution, and an in-memory fixture connector, so the other two PAP-199 children and every importer build on a running pipeline.""",
Scope="""In: `src/connector.ts` (`discover`, `stream`, `fetchAttachment`, `capabilities`, `registerConnector`); Drizzle schema `import_source`, `import_mapping`, `import_run`, `import_run_item` with RLS by `tenant_id`; `src/engine.ts` with transforms (trim, split, parseDate, parseCurrency, mapValues, template, lookup), error policy `stop|skip|collect`, cursor persistence per collection, resume from last completed batch; `src/connectors/fixture.ts`; CLI `pnpm paperos import --connector fixture --mapping m.json --dry`.

Out: dry-run transaction and rollback (child 2), inference and wizard (child 3), real connectors.""",
Spec="""* Writes go through the tables record API (PAP-164), never raw SQL, with audit reason `import:<run_id>`.
* Attachments stream to PAP-37 storage as encountered; failure creates an `error` item and a retry job.
* Relation pass runs after all collections, resolving ids via the PAP-201 helper (stubbed until it merges).
* Progress row written every batch; `import.run.progress` event published for PAP-143 (polling fallback).
* Limits enforced before start: 5M rows, 10 GB attachments, 2 concurrent runs per tenant.""",
**{"Interface contract": """Provides: `SourceConnector`, `SourceSchema`, `SourceRecord`, `MappingDefinition` (Zod), `registerConnector()`, `runImport({ mappingId, mode })`, tables above, event `import.run.progress`, CLI. Consumes: PAP-164 record API and field types, PAP-43 pg-boss, PAP-37 storage, PAP-38 audit log. Children 2 and 3 extend `import_run_item` and the engine without changing these names."""},
**{"Definition of done": """* Fixture connector run of 100k rows completes on staging under 5 minutes with progress visible (bench committed).
* Resume after a simulated crash continues from the last batch with no duplicate writes.
* `docs/migration/framework.md` explains writing a connector in under a page."""},
**{"Test plan": """* Vitest: registry, every transform, error policies, batch boundaries, cursor persistence, relation second pass including circular A-B-A, limit refusals.
* Integration (Postgres in CI): run against fixture connector, assert audit rows and RLS denial when the actor lacks table access.
* Bench script `bench/import-100k.ts` outputs JSON to `reports/`."""},
Demo="""Reviewer runs `pnpm paperos import --connector fixture --mapping fixtures/mapping.json` and watches batch progress print, then opens the target table in the grid and sees 10k rows with relations resolved. Under two minutes.""",
**{"Edge cases": """* Field type changes between discover and stream: item error, not a crash.
* Two runs on one mapping: second is queued, not rejected.
* Connector without `incremental` capability: cursor ignored, full stream each time."""},
Dependencies="""PAP-164 (hard), PAP-43 (hard), PAP-37, PAP-38. Blocks children 2 and 3 and every importer.""",
Agent="""Built by Scout (Import Mapper) with Nova on the record API. Reviewed by Sentinel (Code Reviewer, Security Auditor) and Forge (Schema Wright).""",
Size="""M""")

add("PAP-199", "Dry run, commit and rollback semantics: transaction-rolled dry run, `import_run_item` before-state, exact rollback with conflict listing", "Build", "M",
Goal="""Make every import reversible and previewable: a dry run that executes the whole pipeline inside a rolled-back transaction and produces a grouped error report, a commit that records the pre-write state of every touched record, and a rollback that restores that state exactly or refuses with a conflict list.""",
Scope="""In: `mode: dry` path wrapping batches in a transaction rolled back at the end while still persisting `import_run_item` rows and the report to a separate connection; `before jsonb` capture on `update`; rollback job walking items in reverse (`create` -> archive then hard delete if untouched, `update` -> restore `before`, mapping rows via PAP-201 `mappingBefore`); `--force` flag; report JSON `{ byField: [{ field, count, examples[20] }], totals }`; cancellation producing `cancelled` with partial rollback offer.

Out: UI (child 3), connectors.""",
Spec="""* Dry run validates against PAP-164 validators and RLS so permission errors appear before any write.
* Rollback refuses when `updated_at > run.finished_at` on any touched record unless `--force`; conflicts listed with record ids.
* Ledger-backed tables delegate rollback to a connector hook (`onRollback`) so PAP-206 can post reversing entries.
* Report stored as a file (PAP-37) referenced by `import_run.log_file_id`; retained 90 days.""",
**{"Interface contract": """Provides: `runDry(mappingId)` returning `DryRunReport` (Zod), `rollbackRun(runId, { force })`, `cancelRun(runId)`, connector hook `onRollback?(items)`, statuses `dry|commit|rollback` on `import_run`. Consumes: child 1 engine and tables, PAP-201 mapping restore. Used by child 3, the CLI and PAP-208's `runs.dry|commit|rollback` procedures."""},
**{"Definition of done": """* Dry run of the fixture mapping leaves zero rows in target tables (asserted by row count and audit log).
* Rollback of a 10k-row commit restores a byte-identical snapshot (hash comparison committed as a test).
* Report renders in the CLI as a table and is stored as JSON."""},
**{"Test plan": """* Vitest: before-state capture for create, update and skip; rollback ordering; refusal on later edits; `--force` path; cancellation mid-batch.
* Property test (fast-check): random sequences of imports and rollbacks always return the table to its prior hash.
* Integration: dry run against a table with RLS deny shows the error grouped by table."""},
Demo="""Reviewer runs `--dry` on a mapping with one deliberately wrong date column, sees 20 grouped examples, fixes the mapping, commits, edits one imported record, runs rollback and sees the single conflict listed; `--force` completes it. Under two minutes.""",
**{"Edge cases": """* Record created by import then referenced by a user-created relation: rollback archives instead of deleting and reports it.
* Crash during rollback: rollback itself is resumable by item.
* Dry run larger than 200k rows: sampled to 10k with a notice unless `--full`."""},
Dependencies="""Child 1 (hard), PAP-201 (soft: mapping restore stubbed). Blocks child 3.""",
Agent="""Built by Scout (Import Mapper). Reviewed by Sentinel (Edge Case Hunter, Code Reviewer).""",
Size="""M""")

add("PAP-199", "Type inference, mapping wizard UI and run history with per-item drill-down and rollback button", "Build", "M",
Goal="""Give staff a wizard that connects a source, proposes a mapping from inferred types with sample values, shows the dry-run report, commits with live progress and lists run history with drill-down and a guarded rollback button, at every breakpoint and keyboard-operable.""",
Scope="""In: `src/infer.ts` sampling 1,000 values per field and scoring PAP-164 types (number, currency, date, boolean, email, phone, url, select under 5 percent distinct, multi-select on delimiters, relation on key match) with confidence and warnings; routes `_app/settings/import/` (connect, collections, map fields, dedupe key, relation strategy, report, commit) and `_app/settings/import/runs` grid (PAP-165, list fallback) with item drill-down and rollback confirmation showing counts; JSON mapping export/import.

Out: connector-specific steps (each importer adds a step component via `registerWizardStep`).""",
Spec="""* Mapping table is a real `role=grid` with roving focus; inferred type shown as a select with confidence badge; sample values column truncates at 40 characters.
* Progress uses PAP-143 shapes on `import_run.stats`, polling every 2 s as fallback.
* Rollback button disabled while a run is active or when the actor lacks `import.rollback`.""",
**{"Interface contract": """Provides: `inferTypes(samples)`, `registerWizardStep(connector, step)`, routes above, components `MappingTable`, `RunReport`, `RunHistory` exported from `packages/import/ui`. Consumes: children 1 and 2, PAP-67 primitives, PAP-71 data display, PAP-165 grid. Importers PAP-200 to PAP-207 plug steps in; PAP-208 renders `RunReport` inside chat cards."""},
**{"Definition of done": """* Wizard completes end to end with the fixture connector; history shows the run and rollback works from the UI.
* axe clean on every step; mapping table fully keyboard-operable.
* Screenshots at 320, 375, 768, 1024, 1280, 1536 and 1920 in light and dark for mapping, report and history."""},
**{"Test plan": """* Vitest: inference on 15 fixture columns (dates in 6 formats, currencies, selects, relations), confidence thresholds.
* Playwright: full wizard with a deliberate error, commit, drill-down, rollback; keyboard-only run of the mapping step; visual baselines at the seven widths in both themes.
* axe on each step."""},
Demo="""Reviewer opens Settings > Import, picks the fixture connector, accepts inferred types except one they change, reads the dry-run report, commits, opens Run history and clicks Rollback. Under two minutes.""",
**{"Edge cases": """* 200 columns: mapping table virtualizes rows; sticky header.
* Inference disagrees with an existing target field type: warning with a transform suggestion.
* Narrow width 320: wizard steps stack, mapping shown as cards."""},
Dependencies="""Children 1 and 2 (hard), PAP-67, PAP-71, PAP-165 (soft: list fallback). Blocks PAP-200 to PAP-208 UI steps.""",
Agent="""Built by Scout (Import Mapper) with Iris (Component Crafter). Reviewed by Sentinel (Visual Inspector, Code Reviewer).""",
Size="""M""")

# ---------------- PAP-202 Airtable ----------------
add("PAP-202", "Airtable connector: OAuth and PAT auth, metadata discovery, record streaming with 5 rps token bucket and expiring-attachment fetch", "Build", "M",
Goal="""Implement the `SourceConnector` for Airtable so bases, tables, fields, views and records stream into the framework reliably within Airtable's limits, with attachments fetched the moment they are seen because their URLs expire.""",
Scope="""In: `connectors/airtable/{auth,discover,stream,attachments}.ts` using the Web API with fetch; OAuth 2 (`data.records:read`, `schema.bases:read`) with PAT fallback; `GET /v0/meta/bases` and `/tables`; `stream` with `pageSize 100`, `offset`, `returnFieldsByFieldId: true`; token bucket 5 rps per base, 30 s backoff on 429; incremental via `filterByFormula: LAST_MODIFIED_TIME() > '<cursor>'`; recorded fixtures from PAP-198.

Out: field and view mapping (children 2 and 3).""",
Spec="""* `capabilities: { incremental: true, attachments: true, relations: true, rateLimit: { rps: 5, scope: 'base' } }`.
* Attachment refs carry `recordId` and `fieldId` so a stale URL can be refreshed by re-fetching the record once.
* Auth JSON stored encrypted through the data-layer secret helper; PAT never logged.""",
**{"Interface contract": """Provides: `registerConnector('airtable', ...)`, `AirtableSourceSchema` (raw field `type` and `options` preserved in `SourceField.options`), wizard step `AirtableBasePicker` registered via PAP-199 child 3. Consumes: PAP-199 child 1 interface, PAP-37 storage, PAP-198 fixtures and limits. Children 2 and 3 consume `options` verbatim."""},
**{"Definition of done": """* Discover and stream the PaperOS demo base (8 tables, 40 attachments) end to end with zero 429 failures in the log.
* Re-sync after edits fetches only changed records.
* Docs section in `docs/migration/airtable.md` on auth setup and scopes."""},
**{"Test plan": """* Vitest with msw: pagination, rate limiter timing, 429 backoff, PAT without schema scope error text, expired attachment URL refresh path.
* Integration against the demo base (credentials from the test-accounts issue), recorded run attached.
* Contract test: connector satisfies the framework's `connectorConformance()` suite."""},
Demo="""Reviewer runs `pnpm paperos import --connector airtable --base appDEMO --dry` with the demo PAT and sees eight collections discovered, record counts, and attachments staged in storage. Under two minutes.""",
**{"Edge cases": """* Base over 50k rows in one table: incremental cursor required; first run warns about duration using the PAP-198 throughput table.
* Free-tier base without attachment API access: attachments skipped with a plan note.
* Symmetric link fields: both field ids recorded so child 2 creates one relation."""},
Dependencies="""PAP-199 child 1 (hard), PAP-198 (fixtures), test-accounts issue (integration). Blocks children 2 and 3.""",
Agent="""Built by Scout (Import Mapper). Reviewed by Sentinel (Code Reviewer, Security Auditor).""",
Size="""M""")

add("PAP-202", "Airtable field mapping: every field type to PaperOS types, relations two-pass, lookups and rollups third pass, formula translation report", "Build", "M",
Goal="""Map every Airtable field type to the PaperOS field model faithfully: select colours and order kept, linked records resolved across tables, lookups and rollups created after relations exist, and formulas translated where the engine supports them with an explicit snapshot fallback.""",
Scope="""In: `mapping/airtable.ts` covering all 25 Airtable types per the PAP-198 matrix; third pass `computedFields` in the framework for lookup, rollup and formula; `mapping/airtable-formulas.ts` translating the top 40 functions to PAP-171 syntax; translation report `{ translated, snapshotted: [{ field, reason }] }`; system-field handling (`createdTime`, `lastModifiedBy` and so on).

Out: views (child 3), connector (child 1).""",
Spec="""* Unsupported formula creates `<Field> (snapshot)` text field and a report line; when PAP-171 is absent all formulas snapshot.
* Select colours map to the nearest token from PAP-66; option order preserved.
* Relation fields created for both sides when the link is symmetric; one-way links produce one field.
* Every mapped field carries `source: { system: 'airtable:<baseId>', fieldId }` for PAP-201.""",
**{"Interface contract": """Provides: `mapAirtableField(field): FieldSpec | Skip`, `translateFormula(expr): { ok, expr } | { ok: false, reason }`, framework pass `computedFields` (also used by PAP-203 rollups), `TranslationReport` type. Consumes: PAP-164 field list and validators, PAP-171 formula grammar (soft), PAP-201 relation resolution, child 1 schema."""},
**{"Definition of done": """* All 25 types have a mapping and a fixture; coverage table committed in `docs/migration/airtable.md`.
* Demo base import recreates relations, 3 lookups, 2 rollups and 3 formulas with the report listing any snapshot.
* Re-import after edits updates without duplicates."""},
**{"Test plan": """* Vitest: one fixture per field type, formula translation table (40 supported, 5 unsupported), circular lookup ordering, symmetric link detection.
* Integration: demo base import then diff record counts and relation counts against the Airtable API.
* Snapshot test of the translation report."""},
Demo="""Reviewer imports the demo base and opens the translation report showing 3 formulas translated and 1 snapshotted, then opens a record to see linked records and a rollup value matching Airtable. Under two minutes.""",
**{"Edge cases": """* Link to an excluded table: empty relation with a one-click "also import that table".
* Field named `id` or `created_at`: suffixed and reported.
* Cyclic rollups: cycle detected, fields snapshotted."""},
Dependencies="""Child 1 (hard), PAP-164 (hard), PAP-201, PAP-171 (soft). Blocks child 3.""",
Agent="""Built by Scout (Import Mapper). Reviewed by Sentinel (Edge Case Hunter, Code Reviewer) and Nova.""",
Size="""M""")

add("PAP-202", "Airtable view mapping and wizard steps: filterByFormula parsing, kanban, calendar, gallery and form views, side-by-side review", "Build", "M",
Goal="""Recreate an Airtable user's views as PaperOS saved views so the base feels the same on day one: filters, sorts, groups, hidden fields, colouring, kanban stack, calendar date and gallery cover, plus the Airtable-specific wizard steps and a side-by-side review screen.""",
Scope="""In: `mapping/airtable-views.ts` to PAP-161 view definitions; `filterByFormula` parser for common patterns (`{Field} = 'x'`, `AND/OR`, `IS_AFTER`, `FIND`, `NOT`), unparsed filters reported; wizard steps `TableSelection` with row counts and `ViewImportToggle`; review screen showing Airtable screenshot (uploaded by the user, optional) beside the PaperOS view.

Out: automations, interfaces, comments.""",
Spec="""* View kinds: grid, kanban, calendar, gallery, form (form becomes a PAP-168 form view).
* Unparseable filter keeps the view with a warning badge and the raw formula in the description.
* Hidden fields map to view field visibility; row colouring maps to `colorBy` select field.""",
**{"Interface contract": """Provides: `mapAirtableView(view, fields): ViewSpec | Partial`, `parseFilterByFormula(expr): FilterGroup | null`, wizard steps registered via PAP-199 child 3. Consumes: PAP-161 view model, child 2 field map, PAP-168 form view (soft). The filter parser is reusable by PAP-207 templates authored from Airtable bases."""},
**{"Definition of done": """* Six demo-base views recreated; two side-by-side screenshot pairs attached.
* 20 `filterByFormula` samples parsed or reported.
* Screenshots at 320, 375, 768, 1024, 1280, 1536 and 1920 in light and dark for base picker, translation report and resulting kanban."""},
**{"Test plan": """* Vitest: 20 filter samples, sort and group mapping, each view kind, hidden fields.
* Playwright: wizard from mocked OAuth to kanban view; visual baselines at seven widths, both themes; axe clean.
* Manual: compare two views with Airtable screenshots (attached)."""},
Demo="""Reviewer completes the Airtable wizard against the demo base with view import on and opens the recreated kanban grouped by Status with the same cards as Airtable. Under two minutes.""",
**{"Edge cases": """* View filter references a snapshotted formula field: filter kept on the snapshot text.
* Gallery cover field is not an attachment: warning, cover unset.
* More than 50 views: import toggles default to grid views only."""},
Dependencies="""Children 1 and 2 (hard), PAP-161 (hard), PAP-168 (soft).""",
Agent="""Built by Scout (Import Mapper) with Nova (Views Engineer). Reviewed by Sentinel (Visual Inspector, Code Reviewer).""",
Size="""M""")

# ---------------- PAP-203 Notion ----------------
add("PAP-203", "Notion connector and database property mapping to tables (OAuth, search discovery, databases.query streaming at 3 rps, relations and rollups)", "Build", "M",
Goal="""Implement the Notion `SourceConnector` and the mapping of every database property type to PaperOS fields, so Notion databases become tables with relations and rollups intact before any page content is handled.""",
Scope="""In: `connectors/notion/` on `@notionhq/client` 4.x; OAuth public integration; `discover` via `search` plus `databases.retrieve`; `stream` via `databases.query` (page 100, cursor) with a 3 rps bucket honouring `Retry-After`; incremental by `last_edited_time`; `mapping/notion.ts` for all 20 property types (status groups noted, date ranges to start/end, people by email, files streamed, formula snapshot or translate, relation two-pass, rollup third pass, unique_id with prefix note).

Out: page bodies and blocks (child 2), picker and report (child 3).""",
Spec="""* Database page bodies are queued as `pageBody` refs for child 2; this child stores only properties.
* People unmatched by email become text with a report count.
* Auth stored encrypted; workspace id recorded as `system: notion:<workspaceId>`.""",
**{"Interface contract": """Provides: `registerConnector('notion', ...)`, `mapNotionProperty(prop): FieldSpec | Skip`, `NotionPageBodyRef { pageId, recordId }` queue consumed by child 2. Consumes: PAP-199 child 1, PAP-202 child 2 `computedFields` pass, PAP-164, PAP-201, PAP-37, PAP-198 fixtures."""},
**{"Definition of done": """* Three test-workspace databases with relations and rollups import with counts equal to Notion; re-import after edits updates only changed pages.
* Property coverage table in `docs/migration/notion.md`."""},
**{"Test plan": """* Vitest with recorded responses: every property type fixture, cursor pagination, `Retry-After` handling, date ranges, people matching.
* Integration against the test workspace (test-accounts issue); recording attached.
* Framework `connectorConformance()` suite passes."""},
Demo="""Reviewer runs `pnpm paperos import --connector notion --dry` with the test integration token and sees three databases discovered with property types listed, then commits one and opens it in the grid with a working relation column. Under two minutes.""",
**{"Edge cases": """* Relation to an unshared database: empty relation with warning.
* Two properties normalising to one name: suffixed and reported.
* Archived pages: imported only with "include archived" ticked."""},
Dependencies="""PAP-199 child 1 (hard), PAP-202 child 2 (computed pass, hard), PAP-164, PAP-201. Blocks children 2 and 3.""",
Agent="""Built by Scout (Import Mapper). Reviewed by Sentinel (Code Reviewer, Security Auditor).""",
Size="""M""")

add("PAP-203", "Notion block converter to MDX and Tiptap JSON: all block types, media upload before URL expiry, internal link rewriting", "Build", "M",
Goal="""Convert Notion page content without flattening it: every block type to MDX for the docs engine and to Tiptap JSON for editable documents, media uploaded within the one-hour URL window, and links between imported pages rewritten to their new slugs.""",
Scope="""In: `mapping/notion-blocks.ts` with `toMdx(blocks)` and `toTiptap(blocks)` covering paragraph, headings, lists (bulleted, numbered, to-do, toggle), quote, callout, code, divider, table, image/file/video/pdf, bookmark, embed, equation, column lists (flattened), synced blocks, child pages, child databases (embedded view reference), mentions, link previews; annotation marks; `rewriteLinks(pass)` using PAP-201; 5 MB body cap with sectioning.

Out: connector (child 1), tree picker (child 3).""",
Spec="""* Callouts become `<Callout>`; equations KaTeX; colours dropped and counted.
* Images fetched immediately and stored via PAP-37; external URLs kept unless "copy external media".
* Toggles deeper than level 4 flattened with a note.""",
**{"Interface contract": """Provides: `toMdx(blocks, ctx): { mdx, report }`, `toTiptap(blocks, ctx): { doc, report }`, `ConversionReport { unsupported: [{ type, count }], droppedColours, unmatchedPeople }`, final pass `rewriteLinks`. Consumes: child 1 body refs, PAP-128 MDX component set, PAP-142 Tiptap schema (soft: MDX only until merged), PAP-201 lookups. Reused by PAP-204 for ClickUp docs later."""},
**{"Definition of done": """* Every block type converts with MDX and Tiptap snapshot fixtures; 30 images from the test workspace stored.
* Two side-by-side Notion vs PaperOS renders attached.
* Block coverage table in `docs/migration/notion.md`."""},
**{"Test plan": """* Vitest: one fixture per block type for both targets, marks, nested lists, link rewriting, body splitting at 5 MB.
* Integration: 25 nested pages converted; broken-link check over the output finds zero internal 404s.
* Visual: rendered doc screenshots at 375 and 1280 in light and dark compared to Notion."""},
Demo="""Reviewer runs the converter CLI on the fixture export, opens the generated MDX in the docs engine and sees callouts, a table, an image and a link to a sibling page that resolves. Under two minutes.""",
**{"Edge cases": """* Synced block whose original is unshared: copy of visible content with a note.
* Video hosted on YouTube: kept as embed link, not downloaded.
* Code block language unknown to the highlighter: plain fenced block."""},
Dependencies="""Child 1 (hard), PAP-128 (hard), PAP-142 (soft), PAP-201, PAP-37. Blocks child 3.""",
Agent="""Built by Scout (Import Mapper) with Quill. Reviewed by Sentinel (Edge Case Hunter, Visual Inspector) and Nova for Tiptap validity.""",
Size="""M""")

add("PAP-203", "Notion hierarchy, page tree picker, docs placement and conversion report", "Build", "S",
Goal="""Let the user choose what to bring and see what happened: a page tree picker with counts, a per-page target choice (docs or table), hierarchy preserved under `docs/imported/notion/`, database page bodies attached to records, and a conversion report that names every unsupported block and unmatched person.""",
Scope="""In: wizard steps `NotionTreePicker` (checkboxes, counts, "no access" rows), `TargetChoice`, `ConversionReportView`; placement writer producing `_meta.yaml` order and frontmatter `source: notion`, `sourceUrl`, `imported`; bodies over 2,000 words become linked docs, otherwise a `Content` rich text field; docs written through the PAP-128 import path (branch and PR when the repo is the store).

Out: converter internals (child 2).""",
Spec="""* Picker paginates at 200 nodes and estimates duration from the PAP-198 throughput table.
* Report is stored with the run (PAP-199 child 2) and rendered by `RunReport` with a Notion-specific section.""",
**{"Interface contract": """Provides: wizard steps registered via PAP-199 child 3, `placeDocs(pages): DocPlan`, frontmatter fields above. Consumes: children 1 and 2, PAP-128 file writer, `RunReport`. Output docs are indexed by PAP-137 search like any other doc."""},
**{"Definition of done": """* Test workspace (25 pages, 4 levels, inline database) imports with the tree order preserved in the docs sidebar.
* Screenshots at 320, 375, 768, 1024, 1280, 1536 and 1920 in light and dark for picker and imported doc; axe clean."""},
**{"Test plan": """* Vitest: tree ordering, 2,000-word threshold, frontmatter, "no access" handling.
* Playwright: picker, target choice, report, browse an imported doc and a table view; visual baselines at seven widths, both themes.
* axe on picker and report."""},
Demo="""Reviewer opens the Notion wizard, ticks a top-level page and a database, commits, then browses the imported docs tree and the table. Under two minutes.""",
**{"Edge cases": """* 50k pages: picker shows top levels first and loads children on expand.
* Page moved in Notion between dry run and commit: placed by commit-time parent, noted.
* Docs store is the repo and the branch already exists: suffixed branch name."""},
Dependencies="""Children 1 and 2 (hard), PAP-128 (hard), PAP-199 child 3.""",
Agent="""Built by Scout (Import Mapper) with Quill. Reviewed by Sentinel (Visual Inspector).""",
Size="""S""")

# ---------------- PAP-205 Export ----------------
add("PAP-205", "Export archive format v1.0 and streaming export job: manifest, JSON Schemas, table, docs, files, comments, PM, CRM, ledger and audit writers", "Build", "M",
Goal="""Define and implement the open archive every tenant can take with them: a documented v1.0 layout with JSON Schemas, and a pg-boss job that streams it into object storage with consistent snapshots and checksums, without buffering even 50 GB tenants.""",
Scope="""In: `packages/import/src/export/{format,writers,job}.ts`; `archiver` 7.x streaming zip; writers for `schema/tables.json`, `schema/views.json`, `data/tables/*.jsonl|csv`, `docs/**/*.md`, `files/` plus `index.json`, `comments.jsonl`, `crm/*.jsonl`, `pm/*.jsonl` (Linear-compatible shape), `finance/ledger.jsonl|csv`, `finance/chart-of-accounts.csv`, `audit/audit_events.jsonl`, `identity/users.jsonl`, `README.md`; `manifest.json` with counts and SHA-256 per file; `REPEATABLE READ` snapshot per table batch; redaction of secrets and credentials; scoping (tenant, workspace, tables, date range, `include_files`).

Out: UI and scheduling (child 2), round-trip import (child 3).""",
Spec="""* `docs/migration/export-format.md` documents v1.0; JSON Schemas for `manifest.json` and `tables.json` committed; changes require an ADR.
* Formula and rollup fields exported as definition plus last value.
* Missing files listed in `files/missing.json`; export still succeeds with a warning.""",
**{"Interface contract": """Provides: job `export.run({ tenantId, scope, format })`, `ExportManifest` (Zod), writer interface `registerExportDomain(name, writer)` that business-core, growth and pm-linear implement for their tables, event `export.completed`. Consumes: PAP-43 pg-boss, PAP-37 storage, PAP-128 docs store, PAP-131 comments, PAP-179 ledger (soft), PAP-100, PAP-187, PAP-38 audit."""},
**{"Definition of done": """* Demo tenant export validates against both schemas; every file's checksum matches the manifest.
* 5M-row, 20 GB export streams to storage under 30 minutes with flat memory (bench committed).
* Redaction test proves no token, passkey or hash leaves."""},
**{"Test plan": """* Vitest: schema validation, JSONL and CSV round-trip equality per field type, redaction, scope filters, snapshot consistency (rows inserted mid-export are excluded).
* Bench `bench/export-20gb.ts` with memory sampling.
* Domain writers each ship a fixture test through `registerExportDomain`."""},
Demo="""Reviewer runs `pnpm paperos export --tenant demo --scope tables` and unzips the result to see `manifest.json`, `schema/tables.json` and a JSONL file whose row count matches the manifest. Under two minutes.""",
**{"Edge cases": """* Export requested during an import: allowed; manifest notes the concurrent run.
* 2M doc versions: current versions only by default; `include_history` adds git history JSON.
* Table dropped mid-export: domain writer reports it, archive completes."""},
Dependencies="""PAP-199 child 1 (hard: shared package and mapping types), PAP-43, PAP-37, PAP-128, PAP-131, PAP-179 (soft). Blocks children 2 and 3.""",
Agent="""Built by Scout (Import Mapper) with Forge for snapshot semantics and Ledger for finance files. Reviewed by Sentinel (Security Auditor, Edge Case Hunter).""",
Size="""M""")

add("PAP-205", "Export UI, weekly scheduling to S3 or Google Drive with encryption, signed download links, history and audit", "Build", "M",
Goal="""Put export in the owner's hands: a settings page to start a scoped export, watch progress, download through a signed link, revoke it, and schedule weekly encrypted exports to the tenant's own S3 bucket or Google Drive.""",
Scope="""In: route `_app/settings/export` (start with scope, progress, history, schedule) also shown to portal owners; permission `tenant.export` defaulting to `owner`; signed URLs (7 days, revocable); destinations S3-compatible and Drive via `googleapis`; encryption `age` or zip AES-256 with a passphrase typed twice plus a "PaperOS cannot recover this" confirmation; audit event and owner notification on every export.

Out: format and job (child 1).""",
Spec="""* Schedule stored as a PAP-43 cron job per tenant; failures notify owners (PAP-136, email fallback).
* Download link tied to the requesting owner; history shows archive hash and size.
* Destination credentials stored via the data-layer secret helper.""",
**{"Interface contract": """Provides: oRPC procedures `export.start`, `export.list`, `export.revokeLink`, `export.schedule.set|get`, permission `tenant.export`, audit action `tenant.exported`, notification kind `export.completed`. Consumes: child 1 job and event, PAP-59 `can()`, PAP-38, PAP-136 (soft), PAP-57 Google connection for Drive."""},
**{"Definition of done": """* Start, progress, download, revoke and schedule all work on staging; a scheduled export lands in a MinIO bucket encrypted and decrypts with the passphrase.
* Screenshots at 320, 375, 768, 1024, 1280, 1536 and 1920 in light and dark for export page and history; axe clean."""},
**{"Test plan": """* Vitest: permission checks, link expiry and revocation, schedule serialisation, passphrase confirmation logic.
* Integration: scheduled job to local MinIO, decrypt and verify manifest hash; Drive via recorded API.
* Playwright: full flow with visual baselines at seven widths, both themes."""},
Demo="""Reviewer opens Settings > Export, starts a tables-only export, watches progress reach 100 percent, downloads it, revokes the link and confirms it now 403s. Under two minutes.""",
**{"Edge cases": """* Passphrase lost: documented as unrecoverable; UI states it before saving.
* Bucket credentials rotated: next run fails with a clear error and notification.
* Exports over 10 GB: UI recommends scheduled destination."""},
Dependencies="""Child 1 (hard), PAP-59, PAP-38, PAP-136 (soft), PAP-57.""",
Agent="""Built by Scout (Import Mapper) with Iris for the page. Reviewed by Sentinel (Security Auditor for links and redaction, Visual Inspector).""",
Size="""M""")

add("PAP-205", "Round-trip `paperos` connector: import a PaperOS archive into an empty tenant and verify counts and hashes table by table", "Build", "M",
Goal="""Prove the export is complete by re-importing it: a `paperos` `SourceConnector` that reads the v1.0 archive, recreates schema, views, records, docs, files and comments with identities preserved through `system: paperos` mappings, and a verification script that compares source and target hash by hash.""",
Scope="""In: `connectors/paperos/` reading the zip stream; schema-first application (tables, fields, views) then data, docs, files, comments, PM, CRM; ledger restored through `ledger.importJournal` (reversing rules respected); `scripts/export-roundtrip.ts` producing `reports/roundtrip.json`; tenant-to-tenant move documented in `docs/migration/export-format.md`.

Out: UI (child 2), format (child 1).""",
Spec="""* Identities: `external_id = original record id`, so a restore into the same tenant updates rather than duplicates.
* Files verified by sha256 before linking; mismatch listed.
* Verification compares row counts, per-table content hashes (sorted canonical JSON) and file hashes.""",
**{"Interface contract": """Provides: `registerConnector('paperos', ...)`, `verifyRoundTrip(source, target): RoundTripReport`, CLI `pnpm paperos import --connector paperos --file export.zip`. Consumes: children 1 and 2, PAP-199 engine, PAP-201 mappings, PAP-179 `importJournal` (soft). Named precondition for tenant hard-delete in PAP-33."""},
**{"Definition of done": """* Demo tenant exported, imported into an empty tenant, and `roundtrip.json` shows zero mismatches (report attached).
* Restore into the same tenant is idempotent (zero creates on second run)."""},
**{"Test plan": """* Vitest: archive reader, schema-first ordering, identity mapping, hash comparison including field-type edge cases (currency minor units, dates with zones, relations).
* Integration in CI: small fixture archive round-trips in under 60 s.
* Nightly job on staging round-trips the demo tenant and posts the report."""},
Demo="""Reviewer runs `pnpm paperos export --tenant demo`, then `pnpm paperos import --connector paperos --file demo.zip --tenant empty`, then `pnpm export:verify demo empty` and reads a report with all green rows. Under two minutes on the fixture tenant.""",
**{"Edge cases": """* Archive from a newer format version: refused with the version and an upgrade hint.
* Target tenant already has a table of the same name: merge fields, never change existing types.
* Ledger periods closed in the target: journals land in the current open period with a note."""},
Dependencies="""Children 1 and 2 (hard), PAP-199 children 1 and 2 (hard), PAP-201, PAP-179 (soft).""",
Agent="""Built by Scout (Import Mapper) with Ledger for journal restore. Reviewed by Sentinel (Edge Case Hunter) and Atlas.""",
Size="""M""")

# ---------------- PAP-206 Stripe / QuickBooks / Xero ----------------
add("PAP-206", "Stripe connector and mapping: customers to CRM, catalog and subscriptions to billing, invoices, fees, tax, refunds and payouts to ledger postings", "Build", "M",
Goal="""Bring a business's Stripe history in correctly: customers, products, prices, subscriptions, invoices, charges, refunds and payouts stream through the framework and post balanced journal entries with fees, tax and refunds split the way the ledger expects.""",
Scope="""In: `connectors/stripe/` on `stripe` Node 18.x with restricted read-only key or Connect account; auto-pagination with `created` cursors; `mapping/stripe.ts`: customer -> `crm_contact|crm_company` plus finance customer with `stripe_customer_id`; products and prices -> PAP-177 catalog rows marked `imported`; subscriptions -> subscription rows; paid invoices -> PAP-180 invoice records and PAP-179 journals (debit AR then cash, credit revenue per product, fee expense from `balance_transaction.fee`, tax liability); refunds reversing; payouts as transfers.

Out: QuickBooks and Xero (child 2), wizard and trial balance gate (child 3).""",
Spec="""* Amounts in minor units in transaction currency with base-currency equivalent from the invoice rate or the finance rates table.
* Missing balance transactions fall back to `application_fee` or zero with a warning.
* Existing CRM contact with the same email is linked, not duplicated.""",
**{"Interface contract": """Provides: `registerConnector('stripe', ...)`, `postingRulesStripe` (pure function invoice -> journal lines, exported for Ledger review), fixture set of 15 invoices. Consumes: PAP-199 child 1, PAP-179 `postJournal`, PAP-177 catalog, PAP-180 invoices, PAP-187 CRM, PAP-201."""},
**{"Definition of done": """* Test-mode account (50 customers, 3 products, 40 subscriptions, 120 invoices, 10 refunds) imports; P&L from PAP-183 matches Stripe's balance report within rounding (comparison table attached).
* Posting rules document signed off by Ledger (Bookkeeper)."""},
**{"Test plan": """* Vitest: posting rules on 15 invoice fixtures including partial payments, credit notes, multi-currency, refunds; every journal balances.
* Integration: recorded Stripe responses; then live test-mode run from the test-accounts issue.
* Contract test via `connectorConformance()`."""},
Demo="""Reviewer runs `pnpm paperos import --connector stripe --dry` against the seeded test account and sees invoice counts, then opens the generated journal preview where debits equal credits for each currency. Under two minutes.""",
**{"Edge cases": """* Customer deleted but invoices remain: placeholder "Deleted Stripe customer <id>".
* Subscription with trial and proration lines: proration posted as revenue adjustment.
* Payout to an unknown bank account: cash account chosen in child 3 wizard."""},
Dependencies="""PAP-199 child 1 (hard), PAP-179 (hard), PAP-177, PAP-180, PAP-187, PAP-201, test-accounts issue. Blocks child 3.""",
Agent="""Built by Scout (Import Mapper) with Ledger (Bookkeeper) owning posting rules. Reviewed by Sentinel (Security Auditor, Code Reviewer) and Ledger.""",
Size="""M""")

add("PAP-206", "QuickBooks Online and Xero connectors: chart of accounts, opening balances on a conversion date, optional journal and invoice history", "Build", "M",
Goal="""Import a chart of accounts and opening balances from QuickBooks Online or Xero into the double-entry ledger so reports are correct from the conversion date, with optional history after it.""",
Scope="""In: `connectors/quickbooks/` (OAuth 2 via `intuit-oauth`, `Account`, `JournalEntry`, `Customer`, `Vendor`, `Invoice`, `Bill`, `Payment`, CDC incremental) and `connectors/xero/` (`xero-node` 6.x, `Accounts`, `Contacts`, `Invoices`, `ManualJournals`, `BankTransactions`, `If-Modified-Since`); `mapping/coa.ts` account type and subtype (or Xero class and type) -> ledger `kind`, `code`, `name`, `parent`, `currency`, `is_active`; opening journal on the conversion date; history import of journals and invoices after it.

Out: Stripe (child 1), wizard (child 3).""",
Spec="""* Missing or disabled codes: mapped by name, flagged, codes generated in a reserved range.
* Tracking categories and classes become ledger dimensions when PAP-179 supports them, else tags with a note.
* Conversion date interpreted in tenant timezone.""",
**{"Interface contract": """Provides: `registerConnector('quickbooks', ...)`, `registerConnector('xero', ...)`, `mapChartOfAccounts(accounts): LedgerAccountSpec[]`, `openingJournal(balances, date)`. Consumes: PAP-199 child 1, PAP-179 accounts and journals, PAP-175 customers and vendors, PAP-201. Chart output also consumed by PAP-207 packs for code conflict handling."""},
**{"Definition of done": """* QuickBooks sandbox company and Xero demo company both import; balance sheet from PAP-183 on the conversion date matches the source report within rounding (tables attached).
* `docs/migration/finance-imports.md` section on conversion dates and history."""},
**{"Test plan": """* Vitest: account mapping for every QuickBooks type and subtype and every Xero class; opening journal balances; CDC and `If-Modified-Since` cursors.
* Integration: recorded API responses in CI; live sandbox and demo runs from the test-accounts issue.
* Conformance suite passes for both connectors."""},
Demo="""Reviewer connects the QuickBooks sandbox, picks a conversion date, and sees the chart of accounts mapped with kinds and an opening journal whose debits equal credits. Under two minutes.""",
**{"Edge cases": """* Historical journal referencing an unimported account: dry run stops with the dependency listed.
* Account exists in the tenant with the same code: offered as a match.
* Xero demo company resets monthly: fixtures pinned in the repo."""},
Dependencies="""PAP-199 child 1 (hard), PAP-179 (hard), PAP-175, PAP-201, test-accounts issue. Blocks child 3.""",
Agent="""Built by Scout (Import Mapper) with Ledger (Bookkeeper). Reviewed by Sentinel (Security Auditor) and Ledger.""",
Size="""M""")

add("PAP-206", "Finance import wizard: conversion date, account mapping review, duplicate customer resolution, trial balance gate and reversing rollback", "Build", "M",
Goal="""Make finance imports safe for a non-accountant: a wizard that reviews account matches, resolves duplicate customers, refuses to commit unless the trial balance is balanced per currency, and rolls back by posting reversing entries because the ledger is immutable.""",
Scope="""In: wizard steps `SourcePick`, `ConversionDate`, `AccountMapping` (suggested matches by code and name), `DuplicateCustomers` (link or merge against CRM), `TrialBalance` (per currency, offending entries listed, commit disabled when unbalanced); connector hook `onRollback` implemented as `ledger.reverseRun(run_id)`; every journal tagged `source: import`, `run_id`, external ids.

Out: connectors (children 1 and 2).""",
Spec="""* Trial balance computed from the dry-run journal preview, not from posted data.
* Reversing entries dated at rollback time with a memo referencing the run.
* Wizard steps registered through PAP-199 child 3.""",
**{"Interface contract": """Provides: steps above, `trialBalance(preview): { balanced, byCurrency, offenders }`, `ledger.reverseRun(runId)` (implemented against PAP-179 API), UI component `JournalPreview`. Consumes: children 1 and 2, PAP-199 children 2 and 3, PAP-179, PAP-187 duplicate lookup. `JournalPreview` is reusable by PAP-180 for manual journals."""},
**{"Definition of done": """* Wizard completes against all three sources on staging; unbalanced fixture disables commit with offenders shown.
* Rollback of a committed run posts reversing entries and the trial balance returns to its prior state.
* Screenshots at 320, 375, 768, 1024, 1280, 1536 and 1920 in light and dark for account mapping and trial balance; axe clean."""},
**{"Test plan": """* Vitest: trial balance logic, match suggestions, merge rules, reversing rollback idempotence.
* Playwright: wizard with an unbalanced fixture then a balanced one; visual baselines at seven widths, both themes.
* Integration: rollback on staging verified by PAP-183 reports."""},
Demo="""Reviewer walks the wizard with the Stripe test account, sees one duplicate customer resolved, the trial balance green, commits, then clicks Rollback and sees reversing entries in the journal. Under two minutes.""",
**{"Edge cases": """* Multi-currency imbalance in one currency only: that currency's offenders listed; others green.
* User changes conversion date after mapping: opening journal recomputed, mapping kept.
* Rollback after period close: reversing entries land in the open period with a note."""},
Dependencies="""Children 1 and 2 (hard), PAP-199 children 2 and 3 (hard), PAP-179, PAP-183 (verification), PAP-187.""",
Agent="""Built by Scout (Import Mapper) with Ledger (Bookkeeper) and Iris. Reviewed by Sentinel (Visual Inspector, Code Reviewer) and Ledger.""",
Size="""M""")

# ---------------- PAP-207 Business templates ----------------
add("PAP-207", "Template pack format, Zod schema, lint, and the `template` applier connector with conflict strategies, composition and upgrade", "Build", "M",
Goal="""Define how a business template is written and applied: a versioned `pack.yaml` schema, a lint that enforces minimum content, and a `SourceConnector` applier so packs get dry run, rollback and id mapping for free, including `extends`, multi-pack composition and additive upgrades.""",
Scope="""In: `packages/import/src/templates/{schema,lint,apply,upgrade}.ts`; pack sections `tables[]`, `views[]`, `pipelines[]`, `chartOfAccounts[]`, `segments[]`, `sequences[]`, `pages[]`, `navigation`, `docs[]`, `sampleData/*.jsonl` (`demo: true`), `roles[]`, `entitlements`; conflict strategy `skip|merge|rename` per table and account; `extends: base`; `upgrade` computing added tables and fields only; a `base` pack (contacts, companies, tasks, documents) used by the five packs.

Out: pack content (child 2), gallery (child 3).""",
Spec="""* Lint minimums: 3 page specs, 6 views, 1 pipeline, 1 chart, 2 segments, 1 sequence, 1 doc.
* Mapping system `template:<type>@<version>` so re-apply detects and offers upgrade.
* Sample data applied as a sub-run so "Remove sample data" is a rollback of that sub-run.""",
**{"Interface contract": """Provides: `PackSchema` (Zod), `registerConnector('template', ...)`, `lintPack(path)`, `planUpgrade(tenant, pack): Diff`, CLI `pnpm template lint|apply|upgrade`. Consumes: PAP-199 children 1 and 2, PAP-161 field and view schema, PAP-114 page spec schema, PAP-117 navigation, PAP-179 accounts, PAP-187 pipelines, PAP-201. Children 2 and 3 and future packs depend only on these names."""},
**{"Definition of done": """* `base` pack applies to an empty tenant, re-apply is a no-op, a bumped version upgrades additively.
* Conflict strategies proven on a tenant with an existing `contacts` table.
* `docs/migration/templates.md` authoring section."""},
**{"Test plan": """* Vitest: schema validation, every lint rule, `extends` merge, composition of two packs, conflict strategies, upgrade diff, sample sub-run rollback.
* Integration: apply `base` with sample data, remove sample data, assert structure remains.
* Snapshot of the upgrade diff output."""},
Demo="""Reviewer runs `pnpm template apply base --tenant empty --dry`, reads the diff, applies, then bumps the pack version and runs `upgrade` to see only additions listed. Under two minutes.""",
**{"Edge cases": """* Pack references a view kind not built yet (Gantt): saved with `unsupported`, renders as list.
* Rollback after real rows exist: tables with non-demo rows kept; only empty structure removed.
* Two packs define the same account code: second skipped with a note."""},
Dependencies="""PAP-199 children 1 and 2 (hard), PAP-161 (hard), PAP-114, PAP-117, PAP-179, PAP-187, PAP-201. Blocks children 2 and 3.""",
Agent="""Built by Scout (Template Packager). Reviewed by Sentinel (Code Reviewer, Edge Case Hunter) and Nova.""",
Size="""M""")

add("PAP-207", "Author the five business packs (agency, retail, SaaS, clinic, restaurant) with page specs, views, pipelines, charts of accounts, sample data and starter docs", "Build", "M",
Goal="""Write the content that makes a new app useful in minutes: five realistic packs, each with tables, views, pipeline, chart of accounts, segments, one sequence, page specs, navigation, a starter doc and clearly fictional sample data, passing the lint and conformance tests.""",
Scope="""In: `packages/import/templates/{agency,retail,saas,clinic,restaurant}/`; agency (clients, projects, retainers, timesheets, invoices, proposal pipeline); retail (products, variants, inventory, suppliers, purchase orders, sales, loyalty segment); SaaS (accounts, plans, subscriptions, usage events, churn segment, onboarding sequence); clinic (patients with `sensitive: true` fields, appointments calendar, practitioners, treatments, consent forms, recall sequence); restaurant (menu items, tables and reservations calendar, shifts, suppliers, daily sales); staff role presets; preview screenshots generated by Playwright.

Out: format and applier (child 1), gallery (child 3).""",
Spec="""* Clinic pack marks patient fields `sensitive: true` so PAP-59 policies default to staff-only and a "Sample data" banner shows until removal.
* Sample rows use stable ids so relations resolve; names obviously fictional.
* Each pack's chart of accounts balances to zero on apply.""",
**{"Interface contract": """Provides: five packs plus preview PNGs at 1280 in both themes per pack, role presets consumed by PAP-59 seeding, sequence templates consumed by PAP-191 (unapproved state). Consumes: child 1 schema and lint, PAP-122 conformance tests for generated pages. PAP-208 reads pack metadata to recommend templates."""},
**{"Definition of done": """* All five packs pass lint; applied to empty tenants every page passes PAP-122 conformance, every view renders, trial balance is zero (script and report attached).
* Justin reviews the five content lists in one Needs Justin item.
* Item counts per pack in `docs/migration/templates.md`."""},
**{"Test plan": """* Vitest: lint on all five; sample data relation integrity; sensitive-field annotations present in clinic.
* Integration: apply each pack, run conformance, render every view headlessly, remove sample data.
* Visual: one dashboard per pack at 1280 in light and dark, plus 375 for two packs."""},
Demo="""Reviewer applies the restaurant pack with sample data to an empty tenant and opens the reservations calendar showing tonight's fictional bookings, then removes sample data and sees the empty calendar with structure intact. Under two minutes.""",
**{"Edge cases": """* Tenant already has `contacts` with different fields: merge adds fields only.
* Pack applied on top of an imported QuickBooks chart: accounts matched by code, duplicates skipped.
* Locale other than English: pack copy stays English, dates and currency follow tenant settings."""},
Dependencies="""Child 1 (hard), PAP-122 (verification), PAP-59, PAP-191 (soft). Blocks child 3 previews.""",
Agent="""Built by Scout (Template Packager) with Quill for docs and Beacon for CRM and sequences. Reviewed by Ledger (charts), Sentinel (Visual Inspector) and Justin (realism).""",
Size="""M""")

add("PAP-207", "Template gallery in onboarding and settings: cards with previews, dry-run diff, apply with or without sample data, remove sample data", "Build", "S",
Goal="""Surface templates where a new business meets PaperOS: a gallery in the `paperos create` onboarding flow and in settings, with preview cards, included-items list, a diff preview from dry run, an "apply with sample data" toggle and a one-click sample-data removal.""",
Scope="""In: route `_app/settings/templates` and an onboarding step in PAP-22's flow; components `TemplateCard`, `PackDiff`, `SampleDataBanner`; upgrade prompt when a newer pack version exists.

Out: pack content and applier.""",
Spec="""* Diff preview reuses `RunReport` from PAP-199 child 3 with a templates section (tables added, fields merged, accounts skipped).
* Banner shows on every page containing demo rows until removal.""",
**{"Interface contract": """Provides: components above, route, onboarding step export `TemplateStep` for PAP-22. Consumes: child 1 applier and `planUpgrade`, child 2 previews and metadata, PAP-199 child 3 `RunReport`. PAP-208 links to this route when recommending templates."""},
**{"Definition of done": """* Gallery renders five cards with previews; apply and remove sample data work on staging.
* Screenshots at 320, 375, 768, 1024, 1280, 1536 and 1920 in light and dark for gallery and one applied dashboard; axe clean."""},
**{"Test plan": """* Vitest: card metadata rendering, upgrade prompt logic.
* Playwright: gallery, diff, apply with sample data, browse a page, remove sample data; visual baselines at seven widths, both themes.
* axe on gallery and diff."""},
Demo="""Reviewer opens Settings > Templates, picks Agency, reads the diff, applies with sample data and lands on the agency dashboard; clicks "Remove sample data" in the banner. Under two minutes.""",
**{"Edge cases": """* Same pack already applied: card shows "Applied" and an Upgrade button when relevant.
* Apply fails at dry run (RLS): error shown inline with the offending table.
* 320 width: cards stack, previews hidden behind a tap."""},
Dependencies="""Children 1 and 2 (hard), PAP-22 (soft: settings route works alone), PAP-199 child 3.""",
Agent="""Built by Scout (Template Packager) with Iris. Reviewed by Sentinel (Visual Inspector).""",
Size="""S""")

# ---------------- PAP-213 Data landscape ----------------
add("PAP-213", "Table library spike and ADR: TanStack Table plus Virtual, AG Grid Community, Glide Data Grid and react-data-grid at 100k rows", "Research", "M",
Goal="""Choose the grid library the views engine renders with by building the same 100k-row grid in four candidates and scoring them with the shared rubric plus table-specific extras, then record the ADR so `tables/grid-view` builds without re-litigating. Time-box 4 hours; if unmerged by 2026-09-21, PAP-165 proceeds with TanStack Table v8 and this ADR confirms or reverses it.""",
Scope="""In: `spikes/data-libs/tables/` Vite routes per candidate with inline edit, column resize, frozen columns, grouping and 100k rows over TanStack Virtual where headless; Playwright scroll traces; axe; bundle sizes; scorecards with extras (headless vs rendered, virtualization at 100k, editing hooks, pinning, grouping primitives, server-side pagination hooks for PAP-163, `role=grid` semantics per PAP-152, dnd-kit compatibility, touch); ADR `docs/adr/NNNN-PAP-213-table-library.md`; registry drafts. Handsontable rejected on license.

Out: charts, maps, canvas and editor (siblings).""",
Spec="""* Reference profile: Playwright on the CI runner with CPU throttling 4x; FPS from the trace's frame timings.
* AG Grid Community gaps versus Enterprise (row grouping) recorded explicitly.
* Glide's canvas rendering scored down on a11y and testability with the vision-agent dependency noted.""",
**{"Interface contract": """Provides: ADR with winner, fallback and migration hours, `results/tables.json`, registry entries, a comment on PAP-165 and PAP-163 with exact package and version. Consumes: PAP-209 rubric and `pnpm lib score`, PAP-66 tokens (soft), PAP-162 parity audit findings (cross-link, no repetition)."""},
**{"Definition of done": """* Four routes merged under `spikes/` with results JSON and generated comparison table.
* Winner shows 100k rows at 55+ FPS scroll in a committed trace; screenshots at 375, 1024, 1920 in light and dark.
* ADR accepted with Nova and Atlas approval comments; PAP-165 description updated."""},
**{"Test plan": """* Playwright per route: scroll trace, inline edit, resize, pin, group; axe scan; screenshot at three widths and two themes.
* `pnpm lib score` validates every scorecard (evidence URLs required).
* Bundle: `vite build --mode analyze` per route committed."""},
Demo="""Reviewer opens the ADR, reads the comparison table, then runs `pnpm spike tables --lib tanstack` and scrolls a 100k-row grid while editing a cell. Under two minutes.""",
**{"Edge cases": """* Candidate cannot virtualize columns: note for the 200-column importer case.
* TanStack Table v9 alpha: evaluate v8 stable, note the timeline.
* Tie within 5 points: migration-cost rule, no re-scoring."""},
Dependencies="""PAP-209 (hard; use draft if unmerged), PAP-162 (cross-link). Informs PAP-165, PAP-163; PAP-165 defaults to TanStack if this is late.""",
Agent="""Researched by Scout (Library Evaluator) paired with Nova (Views Engineer). Reviewed by Nova and Atlas.""",
Size="""M""")

add("PAP-213", "Chart and map library spikes and ADRs: ECharts, visx, Recharts, Observable Plot, Nivo, Chart.js; MapLibre GL and Leaflet with self-hosted tiles", "Research", "M",
Goal="""Decide the chart library dashboards use and the map library the map view uses, measured on theming from tokens, tree-shaken size, screenshot stability, accessibility fallbacks and large-data performance, and record two ADRs so `tables/map-chart-views` builds directly.""",
Scope="""In: `spikes/data-libs/charts/` (10k-point line, stacked bar, pie, number tile with theme switch per candidate) and `spikes/data-libs/maps/` (5k clustered markers; MapLibre with Protomaps PMTiles versus OpenFreeMap tiles, Leaflet); scorecards with chart extras (tree-shaken size for four chart kinds, CSS-variable theming, SVG vs canvas for PAP-82 stability, accessible descriptions and data-table fallback, dark mode) and map extras (vector tiles, clustering, offline tiles in Tauri, tile licenses, bundle); ADRs for charts and maps; registry drafts. Time-box 4.5 hours.

Out: tables, canvas, editor (siblings); dashboard build (PAP-170, PAP-172).""",
Spec="""* ECharts measured via `echarts/core` tree-shaken path only.
* Charts follow the dataviz guidance Iris owns (palette from tokens, accessible legends).
* Map tiles must not require a paid key; ops cost of PMTiles hosting recorded.""",
**{"Interface contract": """Provides: two ADRs with fallback and migration hours, `results/charts.json`, `results/maps.json`, registry entries, comments on PAP-170 with exact packages. Consumes: PAP-209 rubric, PAP-66 tokens, PAP-82 screenshot stability requirements."""},
**{"Definition of done": """* Chart winner renders 10k points under 200 ms in a committed trace; theme switch screenshots at 375, 1024, 1920 in light and dark.
* Map spike clusters 5k markers with self-hosted tiles offline in the Tauri shell or a minimal scaffold.
* ADRs accepted with Nova and Atlas approvals; PAP-170 description updated."""},
**{"Test plan": """* Playwright: render timing per candidate, screenshot diff stability across three runs (SVG vs canvas), axe with data-table fallback present.
* Bundle analysis per candidate committed.
* `pnpm lib score` validation of scorecards."""},
Demo="""Reviewer runs `pnpm spike charts --lib echarts`, toggles dark mode and watches the chart re-theme from tokens, then opens the map route and pans a clustered 5k-marker map with local tiles. Under two minutes.""",
**{"Edge cases": """* Canvas charts produce nondeterministic screenshots: record and weigh against Gate 3.
* Library needs a global CSS import: scored under composability.
* Tile style license (ODbL attribution): recorded in the registry entry."""},
Dependencies="""PAP-209 (hard; draft acceptable), PAP-66 (soft). Informs PAP-170, PAP-172.""",
Agent="""Researched by Scout (Library Evaluator) with Iris for chart theming. Reviewed by Nova and Atlas.""",
Size="""M""")

add("PAP-213", "Canvas and editor shortlist: tldraw, React Flow, Excalidraw, Konva; Tiptap, BlockNote, Lexical, Plate, handed to collab research", "Research", "S",
Goal="""Produce a two-candidate shortlist per category for canvas and rich text, with facts and rubric pre-scores, and hand it to `collab/collab-research` (PAP-127) which owns the final decision, so no analysis is done twice. Time-box 2 hours.""",
Scope="""In: facts via `scripts/lib-facts.ts` for eight libraries; pre-score on the rubric's facts-only criteria; license notes (tldraw `SEE LICENSE IN` watermark clause via PAP-211 tiers); one-paragraph rationale per exclusion; shortlist posted as a comment on PAP-127 and saved as `spikes/data-libs/shortlist.md`.

Out: spikes, ADRs, any decision.""",
Spec="""* Shortlist format: `{ category, candidates: [{ id, version, license, preScore, why }], excluded: [{ id, why }] }` validated by the scorecard schema.
* tldraw's watermark and license and BlockNote's dependence on Tiptap called out explicitly.""",
**{"Interface contract": """Provides: `shortlist.md`, JSON in `results/shortlist.json`, comment on PAP-127. Consumes: PAP-209 facts collector and rubric, PAP-211 tiers. PAP-127 consumes the shortlist and must not re-collect facts."""},
**{"Definition of done": """* Shortlist committed and commented on PAP-127 within the time box.
* Every candidate has facts with checked-on dates and a license tier."""},
**{"Test plan": """* `pnpm lib score --facts-only` validates the JSON.
* Vitest lint asserts eight candidates and two per category in the shortlist.
* Reviewer check: Atlas confirms no overlap with PAP-127's scope."""},
Demo="""Reviewer opens the comment on PAP-127 and reads two canvas and two editor candidates with license tier and pre-score, then opens `results/shortlist.json`. Under one minute.""",
**{"Edge cases": """* Facts collector rate-limited: cached facts with a warning.
* Library changed license recently (tldraw 2023): recorded in `why`.
* PAP-127 already merged: shortlist becomes a confirmation comment, no new work."""},
Dependencies="""PAP-209 (hard; draft acceptable), PAP-211 (soft). Informs PAP-127, PAP-132, PAP-142.""",
Agent="""Researched by Scout (Library Evaluator). Reviewed by Atlas.""",
Size="""S""")

# ---------------- PAP-214 Backend landscape ----------------
add("PAP-214", "Decide jobs, transactional email and PDF generation with Docker measurements: Inngest, Trigger.dev, BullMQ, pg-boss, Graphile Worker; Resend, Postmark, SES, Postal; Playwright PDF, react-pdf, Typst", "Research", "M",
Goal="""Settle the three server building blocks other projects are waiting on most: the job queue PAP-43 builds, the email transport PAP-57, PAP-136 and PAP-191 send through, and the PDF renderer PAP-180 uses, each measured in Docker on the shared VPS profile and recorded as ADRs. Time-box 4.5 hours.""",
Scope="""In: `ops/compose/candidates/{jobs,email,pdf}/` compose files; `docker stats` after 5-minute warm-up under 50 req/s where applicable; scorecards with extras (self-host maturity, Postgres-native, RAM, TypeScript SDK, `docker compose up` story, tenant isolation, exit cost); email ADR covering DKIM, SPF, DMARC and a sandbox mode with allowlist for agent sessions; PDF ADR tested with an invoice containing CJK and RTL text; three ADRs; registry drafts.

Out: search, observability, flags, storage (sibling 2); validation and runtime (sibling 3); implementing anything.""",
Spec="""* Redis acceptable only if two or more chosen services need it; Kubernetes-only candidates rejected.
* pg-boss is the incumbent (PAP-43 already names it); the ADR must confirm or reverse with numbers.
* Each ADR names consuming issue, exact package or image tag, env vars for PAP-17, fallback and migration hours.""",
**{"Interface contract": """Provides: ADRs `jobs`, `email`, `pdf` with the fields above, `results/backend-1.json`, compose files for winners under `ops/compose/`, a `@paperos/email` transport interface sketch (`send`, `sandbox`, `allowlist`) handed to data-layer, comments on PAP-43, PAP-57, PAP-136, PAP-180, PAP-191. Consumes: PAP-209 rubric, PAP-211 tiers, PAP-25 VPS profile numbers."""},
**{"Definition of done": """* Three ADRs accepted with Forge and Atlas approval; measured RAM table committed.
* Winner compose files start cleanly in CI on a Forgejo or GitHub runner.
* Consuming issues commented with the decision."""},
**{"Test plan": """* CI job `compose-smoke` runs `docker compose up --wait` for each winner and a health probe.
* `pnpm lib score` validates scorecards; evidence URLs required.
* PDF fixture rendered and visually checked at A4 with CJK and RTL text."""},
Demo="""Reviewer reads the jobs ADR, runs `docker compose -f ops/compose/jobs.yml up`, enqueues a sample job from the README and sees it complete; opens the rendered CJK invoice PDF. Under two minutes.""",
**{"Edge cases": """* Candidate self-hosting is license-gated (Inngest, Trigger.dev tiers): score the self-host path only and verify the tier.
* Email provider blocks unverified domains: sandbox mode documented; DNS setup becomes a Justin task.
* PDF fonts missing in the container: font bundle listed in the ADR."""},
Dependencies="""PAP-209 (hard; draft acceptable), PAP-211 (soft), PAP-25 (soft). Blocks PAP-43 (via parent relation). Informs PAP-57, PAP-136, PAP-180, PAP-191.""",
Agent="""Researched by Scout (Library Evaluator) with Forge (Ops Runner) for measurements. Reviewed by Forge and Atlas.""",
Size="""M""")

add("PAP-214", "Decide search, observability, feature flags and object storage with a resource budget table under 6 GB", "Research", "M",
Goal="""Choose the remaining self-hosted services so the platform fits one VPS: search engine (or none beyond Postgres), observability stack, feature flags (or page-spec access rules) and object storage, each measured for RAM and CPU and recorded as ADRs with a total under the 6 GB service budget. Time-box 4.5 hours.""",
Scope="""In: candidates search (Postgres `tsvector` plus pgvector baseline, ParadeDB `pg_search`, Meilisearch, Typesense), observability (OpenTelemetry collector with Grafana LGTM, SigNoz, HyperDX), flags (Unleash, Flagsmith, own table plus PAP-59 policies), storage (MinIO, Garage, SeaweedFS); compose files and measurements as in sibling 1; resource budget table `docs/adr/backend-resource-budget.md` summing all chosen services including sibling 1's winners; four ADRs; registry drafts.

Out: jobs, email, PDF (sibling 1); implementing (PAP-39, PAP-40, PAP-37).""",
Spec="""* Search ADR starts from PAP-39's `tsvector` plus pgvector plan and must justify any extra service.
* "No new service" is a valid flag decision when page-spec access rules cover the need.
* SigNoz's ClickHouse counted against the budget.""",
**{"Interface contract": """Provides: ADRs `search`, `observability`, `flags`, `storage`, `results/backend-2.json`, the resource budget table, compose winners, comments on PAP-39, PAP-40, PAP-37, PAP-17 (env vars). Consumes: PAP-209, PAP-211, sibling 1 measurements, PAP-25 profile."""},
**{"Definition of done": """* Four ADRs accepted; budget table shows measured totals under 6 GB with headroom stated.
* Winner compose files start in CI; losers removed or moved to `spikes/`.
* PAP-37, PAP-39, PAP-40 commented."""},
**{"Test plan": """* `compose-smoke` job for each winner.
* Budget table generated by a script from `docker stats` JSON so numbers are reproducible.
* Scorecard validation via `pnpm lib score`."""},
Demo="""Reviewer opens the resource budget table, sees every chosen service with measured RAM and the total, then runs `docker compose -f ops/compose/observability.yml up` and opens Grafana with the sample dashboard. Under two minutes.""",
**{"Edge cases": """* Candidate needs more RAM than the whole budget (SigNoz on small profile): reject with the number.
* MinIO license (AGPL) is `service` tier: recorded with PAP-211 context.
* Search decision is "Postgres only": ADR still written."""},
Dependencies="""PAP-209 (hard; draft acceptable), sibling 1 (budget totals), PAP-211. Informs PAP-37, PAP-39, PAP-40.""",
Agent="""Researched by Scout (Library Evaluator) with Forge (Ops Runner). Reviewed by Forge and Atlas.""",
Size="""M""")

add("PAP-214", "Confirm validation and runtime, cross-link confirmed choices, consolidate ADRs, compose files and registry entries", "Research", "S",
Goal="""Close the backend survey: decide Zod 4 versus Valibot and ArkType and Node 22 versus Bun for the API, confirm the already-owned choices by cross-link (Better Auth, Drizzle, ElectricSQL, Hocuspocus, oRPC), and consolidate everything into the ADR index, `ops/compose/`, and registry entries. Time-box 2 hours.""",
Scope="""In: validation and runtime scorecards (Bun tested against Tauri sidecars and native modules); cross-link sections pointing at PAP-56, PAP-32, PAP-31, PAP-139, PAP-35 with no re-scoring; ADR index update; registry drafts for every winner from all three children; CHANGELOG entry; summary comment on PAP-214 with the full decision table.

Out: any new candidates.""",
Spec="""* Runtime defaults to Node 22 on any Bun incompatibility with a chosen library.
* Consolidated table columns: decision, package or image, version, RAM, consuming issue, fallback, migration hours, ADR.""",
**{"Interface contract": """Provides: ADRs `validation`, `runtime`, the consolidated decision table in `docs/libraries/backend-decisions.md`, registry drafts, ADR index entries. Consumes: siblings 1 and 2 outputs, PAP-209, PAP-216 CLI when live (else a Linear comment for Scout)."""},
**{"Definition of done": """* Two ADRs accepted; decision table complete for all eleven decisions; registry drafts exist for each winner.
* License check passes on all chosen packages and images.
* CHANGELOG entry and summary comment posted."""},
**{"Test plan": """* Vitest smoke: Zod 4 and the runner-up validate the same 20 schemas; timing recorded.
* Bun compatibility script against the current lockfile committed with output.
* `pnpm lib registry check` passes if the registry is live."""},
Demo="""Reviewer opens `backend-decisions.md` and sees eleven rows each linking to an accepted ADR, then runs `pnpm lib score docs/libraries/scorecards/runtime.yaml` and reads the table. Under one minute.""",
**{"Edge cases": """* A confirmed choice's research issue is still open: cross-link marked "pending" and not blocked.
* Registry not live: drafts kept in `docs/registry/drafts/` for PAP-216 to import.
* Sibling ADR still `proposed`: table marks it and the summary lists what is outstanding."""},
Dependencies="""Siblings 1 and 2 (hard), PAP-209, PAP-216 (soft).""",
Agent="""Researched by Scout (Library Evaluator). Reviewed by Atlas.""",
Size="""S""")

# ---------------- PAP-215 OSS products ----------------
add("PAP-215", "Spike tables and PM products: NocoDB, Baserow and Plane with compose, seeded flows, metrics and scorecards", "Research", "M",
Goal="""Run NocoDB, Baserow and Plane from pinned compose files, exercise the flows the tables and PM projects care about, capture metrics and screenshots, and produce scorecards with a provisional mode (`embed|fork|borrow|reject`) for the sibling ADR. Time-box 6 hours.""",
Scope="""In: `spikes/oss-products/{nocodb,baserow,plane}/` with `docker-compose.yml`, `.env.example`, `README.md`, `metrics.json` (RAM idle and after flow, startup time, export completeness), screenshots at 375 and 1280; flows: NocoDB and Baserow (create table, relation, filter, kanban, API and webhook), Plane (issue, cycle, board, API); scorecards with product extras (license and tenancy tier, API completeness, SSO and embedding, data ownership, ops footprint, UX distance from PAP-161, upstream velocity).

Out: the ADR (sibling 3), other products.""",
Spec="""* Product not started within 20 minutes on the reference profile: ops scored down, move on.
* Expected licenses to verify: NocoDB AGPL-3.0, Baserow MIT core with premium modules, Plane AGPL-3.0; AGPL forces `embed` or `borrow`.
* Share findings with PAP-162 by cross-link, never repeat its feature audit.""",
**{"Interface contract": """Provides: three spike folders, three scorecards, `metrics.json` per product, provisional modes for sibling 3. Consumes: PAP-209 rubric extras, PAP-211 `service` tier, PAP-162 findings, PAP-25 VPS profile."""},
**{"Definition of done": """* Three compose spikes start in CI (`compose-smoke`) and locally; screenshots and metrics committed.
* Scorecards validate; each has a provisional mode with a one-paragraph rationale.
* Comment on PAP-162 and PAP-100 with the relevant findings."""},
**{"Test plan": """* `compose-smoke` per product with a health probe.
* Playwright scripts for each required flow saving screenshots at 375 and 1280.
* `pnpm lib score` validation."""},
Demo="""Reviewer runs `docker compose -f spikes/oss-products/nocodb/docker-compose.yml up`, opens the seeded kanban, then reads `metrics.json` and the scorecard. Under two minutes after images pull.""",
**{"Edge cases": """* Multi-tenancy per instance only: ops cost multiplied; usually reject for embed.
* Export is UI-only: data-ownership gate fails.
* Image needs more than 2 GB RAM: recorded against the PAP-214 budget."""},
Dependencies="""PAP-209 (hard), PAP-211 (soft), PAP-162 (cross-link). Blocks sibling 3.""",
Agent="""Researched by Scout (Library Evaluator) with Forge (Ops Runner). Reviewed by Nova and Atlas.""",
Size="""M""")

add("PAP-215", "Spike growth products: Twenty CRM, Chatwoot, Listmonk and Postiz with compose, seeded flows, metrics and scorecards", "Research", "M",
Goal="""Run Twenty, Chatwoot, Listmonk and Postiz, exercise the CRM, support inbox, campaign and social scheduling flows the growth project needs, and produce scorecards with provisional modes for the sibling ADR so `growth/*` stops guessing. Time-box 8 hours.""",
Scope="""In: `spikes/oss-products/{twenty,chatwoot,listmonk,postiz}/` with compose, env example, README, `metrics.json`, screenshots at 375 and 1280; flows: Twenty (company, contact, deal, stage move, API read), Chatwoot (inbox, assign, reply, contact link), Listmonk (list, campaign, template, bounce handling), Postiz (mock provider, schedule, approval); scorecards with product extras.

Out: the ADR (sibling 3).""",
Spec="""* Expected licenses to verify: Twenty AGPL-3.0, Chatwoot MIT, Listmonk AGPL-3.0, Postiz AGPL-3.0.
* Cross-link PAP-188 (growth research) findings; do not repeat them.
* SSO gated behind paid tiers recorded as an exact gate.""",
**{"Interface contract": """Provides: four spike folders, four scorecards, metrics, provisional modes for sibling 3, comments on PAP-188, PAP-187, PAP-197, PAP-190. Consumes: PAP-209, PAP-211, PAP-188 findings, PAP-25 profile."""},
**{"Definition of done": """* Four compose spikes start in CI and locally; screenshots and metrics committed.
* Scorecards validate with provisional modes and rationale.
* Comments posted on the four growth issues."""},
**{"Test plan": """* `compose-smoke` per product.
* Playwright flow scripts with screenshots at 375 and 1280.
* Scorecard validation."""},
Demo="""Reviewer starts the Twenty compose, opens the seeded pipeline and moves a deal, then reads the scorecard's embed section on SSO limits. Under two minutes after pull.""",
**{"Edge cases": """* Product ships its own auth and cannot trust Better Auth: embed needs a proxy or downgrades to borrow.
* Twenty image over 2 GB RAM: recorded against budget.
* Postiz needs real provider apps: mock provider only; note for PAP-190."""},
Dependencies="""PAP-209 (hard), PAP-211 (soft), PAP-188 (cross-link). Blocks sibling 3.""",
Agent="""Researched by Scout (Library Evaluator) with Forge (Ops Runner). Reviewed by Beacon and Atlas.""",
Size="""M""")

add("PAP-215", "Spike Cal.com and Formbricks, then write the OSS products mode ADR, borrow reference docs and embed integration contracts", "Research", "M",
Goal="""Finish the product evaluation and make it actionable: spike the two remaining products, then write the single ADR with the mode matrix for all nine, a borrow reference doc (data model diagram and UX patterns) for every `borrow` verdict and an embed contract (SSO, API surface, tenant mapping, theming, export path, owner) for every `embed` verdict. Time-box 4 hours plus writing.""",
Scope="""In: `spikes/oss-products/{calcom,formbricks}/` as in the siblings; ADR `docs/adr/NNNN-PAP-215-oss-products.md` with per-product sections and summary matrix; `docs/registry/reference/<id>.md` with Mermaid data model per borrow; embed contracts per embed; registry entries `adopted` (embed), `reference` (borrow), `rejected`; comments on PAP-188, PAP-162, PAP-197, PAP-100.

Out: integrating anything.""",
Spec="""* Expected licenses: Cal.com AGPL-3.0 plus commercial `ee`, Formbricks AGPL-3.0 plus `ee`.
* `fork` requires Justin and is expected to be zero products.
* Matrix columns: product, license, tier, mode, RAM, owner character, consuming issue.""",
**{"Interface contract": """Provides: ADR with matrix, reference docs, embed contracts, registry entries, comments. Consumes: siblings 1 and 2 scorecards and metrics, PAP-209, PAP-211, PAP-216 CLI when live."""},
**{"Definition of done": """* Nine spikes, nine scorecards, one accepted ADR with Atlas, Nova and Beacon approvals.
* Reference docs for every borrow, contracts for every embed, registry entries for all nine.
* CHANGELOG entry; Linear comment with the matrix and screenshot gallery."""},
**{"Test plan": """* `compose-smoke` for the two new products.
* Vitest lint: every product in the matrix has a mode, a scorecard path and a registry entry.
* Mermaid diagrams render in the docs engine (screenshot)."""},
Demo="""Reviewer opens the ADR, reads the nine-row matrix, clicks through to one borrow reference doc with its data model diagram and one embed contract. Under two minutes.""",
**{"Edge cases": """* Single-company upstream with recent license changes: fork risk raised, borrow preferred.
* Product requires a paid tier for API: embed scored down with exact gate.
* Registry not live: entries drafted in `docs/registry/drafts/`."""},
Dependencies="""Siblings 1 and 2 (hard), PAP-209, PAP-211, PAP-216 (soft).""",
Agent="""Researched by Scout (Library Evaluator) with Forge. Reviewed by Atlas, Nova and Beacon.""",
Size="""M""")
