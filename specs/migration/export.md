---
identifier: "PAP-205"
title: "Export everything (tables, docs, files, ledger) to open formats"
project: "migration"
projectName: "Migration & Import Tools"
phase: "P2"
type: "Build"
priority: 2
surfaces: ["Customer"]
milestone: "Airtable, Notion, ClickUp importers"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-128", "PAP-199", "PAP-201", "PAP-33", "PAP-43"]
blocks: []
key: "migration/export"
url: "https://linear.app/paperos/issue/PAP-205/export-everything-tables-docs-files-ledger-to-open-formats"
source: "plan/specs/bucket-7.json (round-1 canonical spec JSON)"
---

# PAP-205: Export everything (tables, docs, files, ledger) to open formats

**Goal**

Guarantee no lock-in: any tenant owner can export everything they own (tables with schema and views, docs, files, comments, CRM, PM, ledger and audit history) into open formats in one archive, on demand or on a schedule, complete enough that PaperOS itself can re-import it and that a competitor's tool could read it. The archive is also the hard-delete prerequisite named in `data-layer/core-entities`.

**Scope**

In:
- Export service `packages/import/src/export/`: pg-boss job `export.run` producing a zip in `data-layer/file-storage` (`exports/<tenant>/<run_id>.zip`) with a manifest; streaming zip via `archiver` 7.x so 50 GB tenants do not buffer.
- Archive layout: `manifest.json` (schema version, tenant, generated_at, counts, checksums), `schema/tables.json` (every table with field definitions in the `tables/view-model-spec` field schema, DTCG-free), `schema/views.json`, `data/tables/{table}.jsonl` and `.csv` (JSON Lines for fidelity, CSV for convenience; relations as arrays of ids), `docs/**/*.md` with frontmatter (from `collab/docs-engine` store), `files/<id>/<filename>` plus `files/index.json` (sha256, mime, references), `comments.jsonl` (`collab/comments` with anchors), `crm/*.jsonl`, `pm/*.jsonl` (with a Linear-compatible JSON shape), `finance/ledger.jsonl` and `finance/ledger.csv` (journal lines) plus `finance/chart-of-accounts.csv` importable by QuickBooks or Xero, `audit/audit_events.jsonl`, `identity/users.jsonl` (members, roles; no credentials), `README.md` describing the layout.
- Scoping options: whole tenant (owner only), one workspace, selected tables, date range for audit and ledger; `include_files` toggle; format `jsonl+csv|jsonl|csv`.
- Scheduling: tenant setting for weekly export to their own S3 bucket or Google Drive (Drive via `googleapis` upload) with encryption (age or zip AES-256 with a passphrase they set).
- Round-trip: a `paperos` connector for `migration/import-framework` that imports this archive (used by the `system: paperos` mappings in `migration/id-mapping`), so restore and tenant-to-tenant moves work.
- UI at `_app/settings/export`: start export with scope, progress, history with download links (signed URLs, 7 day expiry), schedule settings; customer portal owners see the same page for their tenant.

Out: real-time replication, exporting other tenants' data (never), GDPR per-person data subject export (follow-on using the same layout filtered by contact).

**Spec**

- Permission `tenant.export` granted to `owner` by default; each export writes an `audit_event` and notifies all owners (`collab/notifications`).
- Consistency: export runs inside a `REPEATABLE READ` snapshot per table batch so tables reference a consistent point in time recorded in the manifest; files copied by sha256 verification.
- Checksums: SHA-256 per file in manifest; archive-level hash published in the history row.
- Size limits: none, but exports over 10 GB warn about download time and recommend the scheduled S3 destination.
- Schema version `1.0` documented in `docs/migration/export-format.md` with JSON Schemas for `manifest.json` and `tables.json`; changes require an ADR.
- Redaction: encrypted secrets (OAuth tokens, API keys) never included; `identity/users.jsonl` excludes credentials and passkeys.

**Definition of done**

- Vitest: manifest and schema JSON validate against their JSON Schemas; JSONL and CSV round-trip equality for every field type; redaction; permission checks; scope filters.
- Integration: export the demo tenant (all projects' seed data), import it into an empty tenant through the `paperos` connector, and compare row counts and hashes table by table (script committed, report attached).
- Performance: 5M-row, 20 GB demo export streams to storage under 30 minutes with steady memory (bench committed).
- Playwright: start export, watch progress, download, schedule weekly; screenshots at 320, 375, 768, 1024, 1280, 1536 and 1920 in light and dark for export page and history.
- `docs/migration/export-format.md` reviewed by Quill and Atlas; CHANGELOG entry; Linear comment with round-trip report.

**Edge cases**

- File missing from storage (reconciliation lag): listed in `files/missing.json`, export succeeds with warning.
- Export requested while an import is running: allowed; snapshot semantics per table; manifest notes concurrent runs.
- Tenant with 2M docs versions: only current versions exported by default; `include_history` adds git history JSON.
- Passphrase lost: PaperOS cannot decrypt; UI states this on setup and requires typing a confirmation.
- Download link shared publicly: signed, 7 days, tied to owner; revocable from history.
- Formula and rollup fields: exported as both definition and last computed value.

**Dependencies**

`migration/import-framework` (hard: round-trip connector). `data-layer/file-storage`, `collab/docs-engine`, `collab/comments`, `business-core/ledger` (finance files, soft), `pm-linear/pm-data-model`, `growth/crm-model`, `collab/notifications`. Precondition for tenant hard-delete in `data-layer/core-entities`.

**Agent**

Built by Scout (Import Mapper) with Forge for snapshot semantics and Ledger for finance formats. Reviewed by Sentinel (Security Auditor for redaction and links, Edge Case Hunter) and Atlas.

**Size**

L: touches every data domain and must be provably complete via round-trip.
