---
key: "child/PAP-205/0"
title: "Export archive format v1.0 and streaming export job: manifest, JSON Schemas, table, docs, files, comments, PM, CRM, ledger and audit writers"
project: "migration"
parent: "PAP-205"
phase: "P2"
type: "Build"
priority: 2
size: "M"
surfaces: ["Customer"]
milestone: "Airtable, Notion, ClickUp importers"
intendedState: "Backlog"
blockedBy: []
blocks: []
source: "round2/agent5/pending-issues.json"
linearDocument: "https://linear.app/paperos/document/round-2-pending-issues-migration-20-6cb063cc1be6"
identifier: "PAP-420"
status: "created"
createdAt: "2026-09-17"
---

# Export archive format v1.0 and streaming export job: manifest, JSON Schemas, table, docs, files, comments, PM, CRM, ledger and audit writers

**Goal**

Define and implement the open archive every tenant can take with them: a documented v1.0 layout with JSON Schemas, and a pg-boss job that streams it into object storage with consistent snapshots and checksums, without buffering even 50 GB tenants.

**Scope**

In: `packages/import/src/export/{format,writers,job}.ts`; `archiver` 7.x streaming zip; writers for `schema/tables.json`, `schema/views.json`, `data/tables/*.jsonl|csv`, `docs/**/*.md`, `files/` plus `index.json`, `comments.jsonl`, `crm/*.jsonl`, `pm/*.jsonl` (Linear-compatible shape), `finance/ledger.jsonl|csv`, `finance/chart-of-accounts.csv`, `audit/audit_events.jsonl`, `identity/users.jsonl`, `README.md`; `manifest.json` with counts and SHA-256 per file; `REPEATABLE READ` snapshot per table batch; redaction of secrets and credentials; scoping (tenant, workspace, tables, date range, `include_files`).

Out: UI and scheduling (child 2), round-trip import (child 3).

**Spec**

* `docs/migration/export-format.md` documents v1.0; JSON Schemas for `manifest.json` and `tables.json` committed; changes require an ADR.
* Formula and rollup fields exported as definition plus last value.
* Missing files listed in `files/missing.json`; export still succeeds with a warning.

**Interface contract**

Provides: job `export.run({ tenantId, scope, format })`, `ExportManifest` (Zod), writer interface `registerExportDomain(name, writer)` that business-core, growth and pm-linear implement for their tables, event `export.completed`. Consumes: PAP-43 pg-boss, PAP-37 storage, PAP-128 docs store, PAP-131 comments, PAP-179 ledger (soft), PAP-100, PAP-187, PAP-38 audit.

**Definition of done**

* Demo tenant export validates against both schemas; every file's checksum matches the manifest.
* 5M-row, 20 GB export streams to storage under 30 minutes with flat memory (bench committed).
* Redaction test proves no token, passkey or hash leaves.

**Test plan**

* Vitest: schema validation, JSONL and CSV round-trip equality per field type, redaction, scope filters, snapshot consistency (rows inserted mid-export are excluded).
* Bench `bench/export-20gb.ts` with memory sampling.
* Domain writers each ship a fixture test through `registerExportDomain`.

**Demo**

Reviewer runs `pnpm paperos export --tenant demo --scope tables` and unzips the result to see `manifest.json`, `schema/tables.json` and a JSONL file whose row count matches the manifest. Under two minutes.

**Edge cases**

* Export requested during an import: allowed; manifest notes the concurrent run.
* 2M doc versions: current versions only by default; `include_history` adds git history JSON.
* Table dropped mid-export: domain writer reports it, archive completes.

**Dependencies**

PAP-199 child 1 (hard: shared package and mapping types), PAP-43, PAP-37, PAP-128, PAP-131, PAP-179 (soft). Blocks children 2 and 3.

**Agent**

Built by Scout (Import Mapper) with Forge for snapshot semantics and Ledger for finance files. Reviewed by Sentinel (Security Auditor, Edge Case Hunter).

**Size**

M
