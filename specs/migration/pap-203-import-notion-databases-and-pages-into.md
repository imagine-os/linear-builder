---
identifier: "PAP-203"
title: "Import Notion databases and pages into tables and docs"
project: "migration"
projectName: "Migration & Import Tools"
phase: "P2"
type: "Build"
priority: 4
surfaces: ["Staff"]
milestone: "Airtable, Notion, ClickUp importers"
state: "Backlog"
parent: null
children: ["PAP-417", "PAP-418", "PAP-419"]
blockedBy: ["PAP-128", "PAP-199", "PAP-201", "PAP-349"]
blocks: []
key: "migration/notion"
url: "https://linear.app/paperos/issue/PAP-203/import-notion-databases-and-pages-into-tables-and-docs"
source: "Linear snapshot 2026-09-17T15:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T13:41:56.242Z"
model: null
effort: null
---

# PAP-203: Import Notion databases and pages into tables and docs

**Model / Effort:** set on children (umbrella is never claimed)

**Goal**

Deferred to v0.2 by the Execution Schedule (NJ-14 stop-loss 09-27 can reinstate). Not claimable before 10-01.

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

Provides: `registerConnector('notion')`, `mapNotionProperty()`, `toMdx()`, `toTiptap()`, `ConversionReport`, `rewriteLinks` pass, `placeDocs()`, frontmatter `source: notion`, `sourceUrl`, `imported`, wizard steps. The block converter is reused by PAP-204 for ClickUp docs later. Consumes: PAP-199 interface and wizard, PAP-202 WP2 `computedFields`, PAP-128 MDX components and file writer, PAP-142 Tiptap schema (soft: MDX only until merged), PAP-201, PAP-164, PAP-37, PAP-198 fixtures, PAP-198 work package 2 (test accounts) workspace.

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

PAP-199 and PAP-128 (hard), PAP-202 WP2 (shared pass), PAP-201, PAP-164. Soft: PAP-142, PAP-37; PAP-198 work package 2 (importer test accounts; integration tests read only its env names and skip with `skipped: no-credentials` when unset) for the live Notion run.

**Agent**

Built by Scout (Import Mapper) with Quill for docs placement. Reviewed by Sentinel (Edge Case Hunter, Code Reviewer, Visual Inspector) and Nova for Tiptap validity.

**Size**

L umbrella; two M and one S work package. Pending sub-issue specs: [Round 2 pending issues: migration (20)](https://linear.app/paperos/document/round-2-pending-issues-migration-20-6cb063cc1be6)
