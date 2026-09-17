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
blockedBy: ["PAP-199"]
blocks: []
key: "migration/csv-excel"
url: "https://linear.app/paperos/issue/PAP-200/import-csv-excel-and-google-sheets-with-type-inference"
source: "plan/specs/bucket-7.json (round-1 canonical spec JSON)"
---

# PAP-200: Import CSV, Excel and Google Sheets with type inference

**Goal**

Make spreadsheets the universal on-ramp: import CSV, TSV, Excel (`.xlsx`, `.xls`) and Google Sheets into new or existing tables with correct type inference, header detection, multi-sheet handling and large-file streaming, using the import framework so users get dry runs and rollback for free.

**Scope**

In:
- Connectors in `packages/import/src/connectors/`: `csv` (Papa Parse 5.x streaming with delimiter and encoding sniffing via `chardet`; RFC 4180 quoting, BOM handling), `excel` (ExcelJS 4.4 streaming reader for `.xlsx`; `.xls` via `xlsx` community build only for read, flagged legacy; each worksheet becomes a collection; merged cells, formulas (value not formula), dates from serials with 1900/1904 systems), `gsheets` (Google Sheets API v4 via `googleapis` with OAuth from the tenant's Google connection; each tab a collection; `valueRenderOption: UNFORMATTED_VALUE` plus formatted for dates).
- Upload path: files up to 1 GB through `data-layer/file-storage` multipart; connector reads from storage stream, never loads whole file in memory.
- Header detection: first non-empty row unless a heuristic (numeric ratio, duplicates) says otherwise; user override in the wizard; generated names `Column A` when absent.
- Type inference from the framework plus spreadsheet specifics: percent strings, accounting negatives `(1,234.00)`, thousands separators by locale, Excel error values (`#N/A`) as null with warning, leading-zero codes preserved as text (postcodes, SKUs).
- Public entry points: `Import` button in empty table states (`growth/crm-views`, PM boards), settings wizard, and a customer-facing portal upload when a page spec enables `import: true` (customer surface).
- Templates: downloadable CSV templates generated from any existing table's fields with sample rows.

Out: writing back to sheets, live Google Sheets sync (follow-on), OpenDocument formats (documented gap), PDF tables.

**Spec**

- Sniffing samples the first 64 KB; delimiter candidates `, ; \t |`; encoding candidates UTF-8, UTF-16, Windows-1252, with a manual override.
- Excel dates: cells with date number formats become `date` or `datetime`; plain numbers remain numbers even if they look like serials.
- Google Sheets over 5M cells or protected: clear error linking to a CSV export fallback.
- Multi-sheet workbook: wizard proposes one target table per sheet; sheets that look like lookups (two columns, unique keys) are suggested as select options or relations.
- Dedupe default: none for new tables; for existing tables the primary text field or email if present, editable.
- Row limit per run inherited from framework (5M); over 200k rows the wizard recommends dry run on a 10k sample first (one click).

**Definition of done**

- Vitest: 25 fixture files (delimiters, encodings, BOM, quoted newlines, ragged rows, Excel dates both systems, merged cells, formulas, error values, leading zeros, empty sheets, 50-column wide) all infer expected types and counts; Sheets connector tested with recorded API responses.
- Performance: 1M-row, 20-column CSV (about 150 MB) imports on staging under 4 minutes with memory under 512 MB (bench committed).
- Playwright: upload CSV, correct one inferred type, dry run, commit, open table; Excel with two sheets; Google Sheets via mocked OAuth; screenshots at 320, 375, 768, 1024, 1280, 1536 and 1920 in light and dark for upload, mapping and result.
- Template download test.
- `docs/migration/spreadsheets.md` (supported formats, inference rules, limits); CHANGELOG entry; Linear comment with recording and bench.

**Edge cases**

- Ragged rows (fewer or more cells than headers): missing become null, extras go to an "Overflow" text column with a warning count.
- Duplicate header names: suffixed `(2)`, `(3)`, reported.
- Numbers with mixed locales in one column (1,5 and 1.5): inferred text with a warning and a locale override option.
- 10k-row CSV where one row has a date in a different format: parsed with fallback formats; unparseable values become null and are listed.
- Excel file is password protected or corrupt: error before wizard with a retry hint.
- Google token expired mid-stream: connector refreshes once, else run pauses in `failed` resumable state.

**Dependencies**

`migration/import-framework` (hard). `data-layer/file-storage` (uploads), Google OAuth connection from `identity/better-auth` providers, `tables/grid-view` for the result view. Referenced by empty states in `growth/crm-views` and `pm-linear/board-views`.

**Agent**

Built by Scout (Import Mapper). Reviewed by Sentinel (Edge Case Hunter for parsing fixtures, Code Reviewer, Visual Inspector) and Quill.

**Size**

M: three connectors over one framework; parsing edge cases dominate.
