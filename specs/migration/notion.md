---
identifier: "PAP-203"
title: "Import Notion databases and pages into tables and docs"
project: "migration"
projectName: "Migration & Import Tools"
phase: "P2"
type: "Build"
priority: 2
surfaces: ["Staff"]
milestone: "Airtable, Notion, ClickUp importers"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-128", "PAP-199", "PAP-201"]
blocks: []
key: "migration/notion"
url: "https://linear.app/paperos/issue/PAP-203/import-notion-databases-and-pages-into-tables-and-docs"
source: "plan/specs/bucket-7.json (round-1 canonical spec JSON)"
---

# PAP-203: Import Notion databases and pages into tables and docs

**Goal**

Bring a Notion workspace across without flattening it: databases become tables with their property types, relations and rollups; pages become docs in the docs engine with blocks converted to MDX (or Tiptap JSON where the target is an editable doc), preserving hierarchy, inline databases, mentions, embeds and attachments; and database pages keep their body content attached to the imported record.

**Scope**

In:
- Connector `packages/import/src/connectors/notion/` on `@notionhq/client` 4.x: OAuth public integration (tenant connects, picks pages), `discover` via `search` (databases and top-level pages) and `databases.retrieve` for property schema; `stream` via `databases.query` (page size 100, cursor) and `blocks.children.list` recursively for page bodies; 3 rps token bucket with `Retry-After` handling.
- Property mapping `mapping/notion.ts`: title, rich_text, number (formats), select, multi_select, status (as select with groups noted), date (ranges to start/end pair), people (matched to users by email, else text), files (streamed to `data-layer/file-storage`), checkbox, url, email, phone_number, formula (snapshot plus translated where `tables/formula-engine` supports), relation (two-pass), rollup (created after relations), created_time, created_by, last_edited_time, last_edited_by, unique_id -> number with prefix note, verification -> skipped with note.
- Block conversion `mapping/notion-blocks.ts` to MDX for `collab/docs-engine` docs and to Tiptap JSON for `realtime/collab-text` documents: paragraph, headings, lists (bulleted, numbered, to-do, toggle), quote, callout (-> `Callout` component), code (language preserved), divider, table, image/file/video/pdf (uploaded), bookmark and embed (link cards), equation (KaTeX), column lists (flattened with a note), synced blocks (content copied), child pages (recursive with links), child databases (imported as tables, embedded view reference inserted), mentions (page -> link, user -> name, date -> text), link_preview.
- Hierarchy: pages become docs under `docs/imported/notion/<workspace>/<path>` with `_meta.yaml` ordering by Notion order; database pages' bodies stored as a rich text field `Content` on the record, or as linked docs when over 2,000 words.
- Wizard steps: page tree picker with checkboxes and counts, target choice per top-level page (docs vs table), conversion report (unsupported blocks, unmatched people).

Out: Notion comments (API read only, imported as a note if enabled later), permissions and sharing settings, Notion AI properties, wiki verification.

**Spec**

- Rich text annotations (bold, italic, code, strikethrough, underline, colour) map to Markdown or Tiptap marks; colours dropped with a report count.
- Internal links between imported pages rewritten to the new doc slugs in a final pass using `migration/id-mapping`.
- Images: Notion-hosted URLs expire in 1 hour, fetched immediately; external URLs kept as links unless "copy external media" is ticked.
- Databases with over 10k pages use `last_edited_time` filter for incremental re-sync.
- Docs written through the docs engine's import path (`collab/docs-engine` file writer with frontmatter `source: notion`, `sourceUrl`, `imported`), committed as a branch and PR when the repo is the docs store, or written to the tenant docs table when the runtime docs store exists.
- Max page body 5 MB; larger split into sections with a warning.

**Definition of done**

- Vitest: every property type and every block type from fixtures converts to the expected MDX and Tiptap snapshots; link rewriting; people matching; date ranges.
- Integration against the PaperOS Notion test workspace (3 databases with relations and rollups, 25 pages nested 4 deep, 30 images, inline database, synced block): full import, then re-import after edits; recording attached.
- Playwright: picker, report, browse an imported doc with images and a table view of an imported database; screenshots at 320, 375, 768, 1024, 1280, 1536 and 1920 in light and dark for picker and imported doc.
- Side-by-side Notion vs PaperOS renders for two pages attached.
- `docs/migration/notion.md` (block coverage table, limitations); CHANGELOG entry; Linear comment with recording and coverage.

**Edge cases**

- Page the integration was not granted: listed as "no access" in the picker with instructions, not an error.
- Relation to a database not shared with the integration: relation field created empty with a warning.
- Deeply nested toggles (10 levels): flattened beyond level 4 with a note.
- Database with two properties named identically after normalisation (`Status` and `status`): suffix and report.
- Very large workspace (50k pages): picker paginates and estimates time from `migration/format-research` throughput table.
- Archived pages: imported with `status: archived` only if the user ticks "include archived".

**Dependencies**

`migration/import-framework` and `collab/docs-engine` (hard). `migration/id-mapping`, `realtime/collab-text` (Tiptap target, soft: MDX only until merged), `tables/field-types`, `data-layer/file-storage`.

**Agent**

Built by Scout (Import Mapper) with Quill for docs placement conventions. Reviewed by Sentinel (Edge Case Hunter, Code Reviewer, Visual Inspector) and Nova for Tiptap JSON validity.

**Size**

L: two targets (tables and docs), a full block converter and nested hierarchy.
