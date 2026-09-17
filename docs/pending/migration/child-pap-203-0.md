---
key: "child/PAP-203/0"
title: "Notion connector and database property mapping to tables (OAuth, search discovery, databases.query streaming at 3 rps, relations and rollups)"
project: "migration"
parent: "PAP-203"
phase: "P2"
type: "Build"
priority: 2
size: "M"
surfaces: ["Staff"]
milestone: "Airtable, Notion, ClickUp importers"
intendedState: "Backlog"
blockedBy: []
blocks: []
source: "round2/agent5/pending-issues.json"
linearDocument: "https://linear.app/paperos/document/round-2-pending-issues-migration-20-6cb063cc1be6"
status: "pending"
---

# Notion connector and database property mapping to tables (OAuth, search discovery, databases.query streaming at 3 rps, relations and rollups)

**Goal**

Implement the Notion `SourceConnector` and the mapping of every database property type to PaperOS fields, so Notion databases become tables with relations and rollups intact before any page content is handled.

**Scope**

In: `connectors/notion/` on `@notionhq/client` 4.x; OAuth public integration; `discover` via `search` plus `databases.retrieve`; `stream` via `databases.query` (page 100, cursor) with a 3 rps bucket honouring `Retry-After`; incremental by `last_edited_time`; `mapping/notion.ts` for all 20 property types (status groups noted, date ranges to start/end, people by email, files streamed, formula snapshot or translate, relation two-pass, rollup third pass, unique_id with prefix note).

Out: page bodies and blocks (child 2), picker and report (child 3).

**Spec**

* Database page bodies are queued as `pageBody` refs for child 2; this child stores only properties.
* People unmatched by email become text with a report count.
* Auth stored encrypted; workspace id recorded as `system: notion:<workspaceId>`.

**Interface contract**

Provides: `registerConnector('notion', ...)`, `mapNotionProperty(prop): FieldSpec | Skip`, `NotionPageBodyRef { pageId, recordId }` queue consumed by child 2. Consumes: PAP-199 child 1, PAP-202 child 2 `computedFields` pass, PAP-164, PAP-201, PAP-37, PAP-198 fixtures.

**Definition of done**

* Three test-workspace databases with relations and rollups import with counts equal to Notion; re-import after edits updates only changed pages.
* Property coverage table in `docs/migration/notion.md`.

**Test plan**

* Vitest with recorded responses: every property type fixture, cursor pagination, `Retry-After` handling, date ranges, people matching.
* Integration against the test workspace (test-accounts issue); recording attached.
* Framework `connectorConformance()` suite passes.

**Demo**

Reviewer runs `pnpm paperos import --connector notion --dry` with the test integration token and sees three databases discovered with property types listed, then commits one and opens it in the grid with a working relation column. Under two minutes.

**Edge cases**

* Relation to an unshared database: empty relation with warning.
* Two properties normalising to one name: suffixed and reported.
* Archived pages: imported only with "include archived" ticked.

**Dependencies**

PAP-199 child 1 (hard), PAP-202 child 2 (computed pass, hard), PAP-164, PAP-201. Blocks children 2 and 3.

**Agent**

Built by Scout (Import Mapper). Reviewed by Sentinel (Code Reviewer, Security Auditor).

**Size**

M
