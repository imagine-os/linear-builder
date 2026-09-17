---
identifier: "PAP-200"
title: "Import CSV, Excel and Google Sheets with type inference"
project: "migration"
projectName: "Migration & Import Tools"
phase: "P2"
type: "Build"
priority: 2
surfaces: ["Customer", "Staff"]
milestone: "Import framework and CSV"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-199", "PAP-349"]
blocks: ["PAP-413"]
key: "migration/csv-excel"
url: "https://linear.app/paperos/issue/PAP-200/import-csv-excel-and-google-sheets-with-type-inference"
source: "Linear snapshot 2026-09-17T15:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T13:41:54.580Z"
model: "claude-sonnet-5"
effort: "high"
---

# PAP-200: Import CSV, Excel and Google Sheets with type inference

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / high — Build M

**Goal**

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

* Sniffing on the first 64 KB; delimiters `, ; \t |`; encodings UTF-8, UTF-16, Windows-1252; manual override.
* Excel cells with date formats become `date` or `datetime`; plain numbers stay numbers.
* Sheets over 5M cells or protected: clear error with CSV fallback link.
* Multi-sheet: one target per sheet; two-column unique sheets suggested as select options or relations.
* Over 200k rows: wizard offers a one-click 10k-sample dry run.

**Interface contract**

Provides: `registerConnector('csv'|'excel'|'gsheets')`, `sniff(buffer): { delimiter, encoding, hasHeader }`, `detectSourcePreset(headers)` hook consumed by `PAP-413`, wizard steps `FileUpload`, `SheetPicker`, `HeaderOverride`, component `ImportButton` for empty states, `pnpm paperos template-csv <table>`. Consumes: PAP-199 interface and wizard registry, PAP-37 uploads, PAP-57 Google connection, PAP-165 result view. Consumers: PAP-189 and PAP-102 empty states, PAP-208, `PAP-413`.

**Definition of done**

* 25 fixture files infer expected types and counts; Sheets tested with recorded responses and live against the Google OAuth app from PAP-198 work package 2 when `GOOGLE_TEST_CLIENT_ID` is set, otherwise `skipped: no-credentials`.
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

PAP-199 (hard). PAP-37, PAP-57, PAP-165 (soft); PAP-198 work package 2 (importer test accounts; integration tests read only its env names and skip with `skipped: no-credentials` when unset) for the live Sheets test only.

**Agent**

Built by Scout (Import Mapper). Reviewed by Sentinel (Edge Case Hunter, Code Reviewer, Visual Inspector) and Quill.

**Size**

M: three connectors over one framework; parsing edge cases dominate.
