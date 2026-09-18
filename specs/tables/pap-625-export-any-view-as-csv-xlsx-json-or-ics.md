---
identifier: "PAP-625"
title: "Export any view as CSV, XLSX, JSON or ICS honouring filters, sorts and visible fields, streamed as a job with a print route /print/v/:id"
project: "tables"
projectName: "Table & Views Engine"
phase: "P2"
type: "Build"
priority: 2
surfaces: ["Staff"]
milestone: "View sharing, formulas, dashboards"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-43", "PAP-337", "PAP-343", "PAP-565", "PAP-624"]
blocks: ["PAP-205", "PAP-639"]
key: "r4/tables/view-export-csv-xlsx-ics-print"
url: "https://linear.app/paperos/issue/PAP-625/export-any-view-as-csv-xlsx-json-or-ics-honouring-filters-sorts-and"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:18.944Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 3
dueDate: "2026-09-30"
cycle: null
---

# PAP-625: Export any view as CSV, XLSX, JSON or ICS honouring filters, sorts and visible fields, streamed as a job with a print route /print/v/:id

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Build M

**Goal**

Airtable, Notion, ClickUp and Baserow all let a user download the view they are looking at. PAP-205 exports the whole tenant and PAP-172 caps a public CSV, but nobody owns per-view export: the current filter, sort, group and visible fields, formatted per field type, as CSV, XLSX, JSON or (for calendar views) an ICS feed, plus a printable render.

**Scope**

In: `packages/views/src/export/{export,csv,xlsx,json,ics,print}.ts`; procedure `views.export({ viewId | spec, format, tempFilter?, locale })` returning `{ jobId }` above 2,000 rows or the file inline below; `ExportMenu` in the toolbar; route `/print/v/:id`; ICS subscribe URL `/ics/v/:token.ics` behind a share token.

Out: tenant-wide archives (PAP-205), scheduled deliveries (PAP-639), PDF templates (PAP-235), import.

**Spec**

* Rows come from PAP-337 procedures paged at 200 with the actor's predicate; only `fields[].visible` columns in `order`; values formatted with `fieldTypes[type].format(value, options, locale)`; raw ISO and minor units in JSON; relations export the target title, attachments a signed URL valid 24 h (PAP-37).
* CSV RFC 4180 with UTF-8 BOM option, `csv-stringify` 6.x; XLSX via `exceljs` 4.x streaming writer with typed number and date cells and a header row; JSON as `{ view, fields, rows }`; ICS via `ical-generator` 8.x for `calendar|timeline|gantt` kinds mapping `startField|endField|allDay`, `UID` = record id, `SEQUENCE` = version.
* Above 2,000 rows the export runs as a PAP-43 job writing to PAP-37 storage with progress, cancel and a `file.ready` event; the toolbar shows a progress toast and a download link; files expire after 7 days.
* Groups: CSV and XLSX add a leading group column per level; XLSX collapses groups with outline levels; aggregates land in a final row when `includeAggregates`.
* Public views (PAP-624) export only when `allow_export`, capped at 10k rows and rate-limited; ICS subscribe URLs are share tokens of kind `link` and refresh on every fetch.
* `/print/v/:id` renders the view without chrome via `ViewHost` `mode: 'print'` with page-break-avoid on rows, A4 and Letter `@page`, used by PAP-183 reports; commands `view.export.csv|xlsx|json|ics|print`.

**Interface contract**

Provides: `views.export`, `<ExportMenu />`, `exportView(spec, format, ctx)` stream helper, `/print/v/:id`, `/ics/v/:token.ics`, event `view.exported { viewId, format, rows }`. Consumes: `views.query|groups` (PAP-337), column layout and toolbar slot (PAP-343, PAP-618), `format` per type (PAP-338), jobs (PAP-43), files (PAP-37), share tokens (PAP-624), print CSS defaults (PAP-66). Consumed by PAP-183 reports, PAP-205 (reuses the writers), PAP-189 contact export.

**Definition of done**

* Four formats and the print route green in Vitest and Playwright; 100k-row export completes as a job under 60 s on the compose stack with progress; screenshots of the menu and print route at 375, 1024, 1920.
* `docs/views/export.md`; CHANGELOG; Linear comment with sample files attached.

**Test plan**

* Unit: CSV quoting and BOM; XLSX cell typing (number, date, boolean); JSON raw shapes; ICS all-day and timed events across DST; group column emission; visible-field projection.
* Integration: export as a viewer excludes rows the predicate hides; public view without `allow_export` gets `FORBIDDEN`; job cancel leaves no orphan file.
* E2E: filter the demo grid, export CSV inline and open it, export 100k rows as XLSX via the job toast, subscribe to the calendar ICS in a test client, print `/print/v/:id` to PDF and assert page count.

**Demo**

Reviewer filters the demo grid to one owner, exports XLSX, opens it in LibreOffice showing typed dates, then copies the ICS URL of `/demo/calendar` into a calendar app. Under two minutes.

**Edge cases**

* Formula `#ERROR` cells export as empty with a warnings sheet.
* Mixed-currency sum aggregate exports one row per currency.
* Locale `de`: CSV uses `;` delimiter when `locale.decimal === ','` and the user did not override.
* Attachment URL expiry: re-export regenerates; documented.

**Dependencies**

PAP-337 (hard), PAP-343 (hard), PAP-43 (hard, jobs). Soft: PAP-37, PAP-624, PAP-338. Blocks PAP-205 (writer reuse); PAP-183 adopts the print route softly.

**Agent**

Builder: Nova (Views Engineer). Reviewer: Sentinel (Edge Case Hunter).

**Size**

M: one session.

*Round 4 critique fix (2026-09-18):* resolved 3 round-4 file keys in this description to Linear identifiers: `r4/tables/public-view-links-and-embeds` = PAP-624, `r4/tables/scheduled-view-snapshots` = PAP-639, `r4/tables/view-toolbar-sort-group-aggregates` = PAP-618.
