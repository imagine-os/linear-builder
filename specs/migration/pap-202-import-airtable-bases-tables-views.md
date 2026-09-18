---
identifier: "PAP-202"
title: "Import Airtable bases (tables, views, relations, attachments)"
project: "migration"
projectName: "Migration & Import Tools"
phase: "P2"
type: "Build"
priority: 2
surfaces: ["Staff"]
milestone: "Airtable, Notion, ClickUp importers"
state: "Backlog"
parent: null
children: ["PAP-414", "PAP-416", "PAP-415"]
blockedBy: ["PAP-199", "PAP-201", "PAP-349"]
blocks: []
key: "migration/airtable"
url: "https://linear.app/paperos/issue/PAP-202/import-airtable-bases-tables-views-relations-attachments"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T12:57:16.008Z"
model: null
effort: null
estimate: null
dueDate: "2026-09-30"
cycle: null
---

# PAP-202: Import Airtable bases (tables, views, relations, attachments)

**Model / Effort:** set on children (umbrella is never claimed)

**Goal**

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

Provides: `registerConnector('airtable')`, `mapAirtableField()`, `translateFormula()`, framework pass `computedFields` (reused by PAP-203 rollups), `parseFilterByFormula()` (reused by PAP-207), wizard steps, coverage table in `docs/migration/airtable.md`. Consumes: PAP-199 interface, wizard registry and passes; PAP-201 mappings; PAP-164 types; PAP-161 views; PAP-168 forms (soft); PAP-171 formulas (soft, snapshot fallback); PAP-37 storage; PAP-198 fixtures; PAP-198 work package 2 (test accounts) demo base.

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

PAP-199 (hard), PAP-201, PAP-164, PAP-161, PAP-198 (fixtures). Soft: PAP-171, PAP-168, PAP-37; PAP-198 work package 2 (importer test accounts; integration tests read only its env names and skip with `skipped: no-credentials` when unset) for the live Airtable run.

**Agent**

Built by Scout (Import Mapper) with Nova (Views Engineer). Reviewed by Sentinel (Edge Case Hunter, Code Reviewer, Visual Inspector, Security Auditor) and Quill.

**Size**

L umbrella; three M work packages. Pending sub-issue specs: [Round 2 pending issues: migration (20)](https://linear.app/paperos/document/round-2-pending-issues-migration-20-6cb063cc1be6)
