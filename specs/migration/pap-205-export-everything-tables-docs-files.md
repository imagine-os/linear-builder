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
children: ["PAP-420", "PAP-421", "PAP-422"]
blockedBy: ["PAP-33", "PAP-43", "PAP-128", "PAP-199", "PAP-201", "PAP-349"]
blocks: []
key: "migration/export"
url: "https://linear.app/paperos/issue/PAP-205/export-everything-tables-docs-files-ledger-to-open-formats"
source: "Linear snapshot 2026-09-17T15:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T13:41:56.400Z"
model: null
effort: null
---

# PAP-205: Export everything (tables, docs, files, ledger) to open formats

**Model / Effort:** set on children (umbrella is never claimed)

**Goal**

Guarantee no lock-in: any tenant owner exports everything they own (tables with schema and views, docs, files, comments, CRM, PM, ledger, audit) into one open archive, on demand or scheduled, complete enough that PaperOS re-imports it losslessly and another tool can read it. It is also the hard-delete prerequisite named in PAP-33. Umbrella for three work packages.

**Scope**

Work packages (full specs in the project document):

* **WP1 Format v1.0 and streaming job** (M): `manifest.json` with counts and SHA-256, JSON Schemas for manifest and `tables.json`, writers for every domain (`data/tables/*.jsonl|csv`, `docs/**/*.md`, `files/`, `comments.jsonl`, `crm/`, `pm/` Linear-compatible, `finance/ledger.*` and `chart-of-accounts.csv`, `audit/`, `identity/users.jsonl` without credentials), `archiver` streaming zip, `REPEATABLE READ` snapshots per table batch, redaction, scoping.
* **WP2 UI, scheduling and links** (M): `_app/settings/export`, permission `tenant.export`, signed 7-day revocable links, weekly export to the tenant's S3 or Google Drive with `age` or AES-256 passphrase encryption, audit event and owner notification.
* **WP3 Round-trip connector and verification** (M): `paperos` connector importing the archive with identities preserved (`system: paperos`), `verifyRoundTrip` comparing counts and hashes, nightly demo-tenant round trip.

Out: real-time replication, other tenants' data, per-person DSAR export (PAP-221 reuses the layout).

**Spec**

* Format changes require an ADR; `docs/migration/export-format.md` documents v1.0.
* Secrets, tokens, passkeys never exported; formula and rollup fields exported as definition plus last value.
* Exports over 10 GB warn and recommend the scheduled destination.
* Order WP1 -> WP3 -> WP2 acceptable if the UI blocks on design; report each on `PAP-205/wp<n>-<slug>`.

**Interface contract**

Provides: job `export.run`, `ExportManifest` (Zod), `registerExportDomain(name, writer)` implemented by business-core, growth and pm-linear for their tables, event `export.completed`, oRPC `export.start|list|revokeLink|schedule.*`, permission `tenant.export`, `registerConnector('paperos')`, `verifyRoundTrip()`, CLI `pnpm paperos export`. Consumes: PAP-199 engine, PAP-201, PAP-43, PAP-37, PAP-128, PAP-131, PAP-179 (soft), PAP-100, PAP-187, PAP-38, PAP-59, PAP-136 (soft), PAP-57 Google connection.

**Definition of done**

* Three work packages merged and reported.
* Integration test: export the demo tenant, import into an empty tenant through `paperos`, `roundtrip.json` shows zero mismatches; restore into the same tenant is idempotent; report attached.
* 5M-row, 20 GB export streams under 30 minutes with flat memory (bench committed).
* Scheduled encrypted export lands in MinIO and decrypts.
* Screenshots at 320, 375, 768, 1024, 1280, 1536 and 1920 in light and dark for export page and history; axe clean.
* `docs/migration/export-format.md` reviewed by Quill and Atlas; CHANGELOG; Linear comment with round-trip report.

**Test plan**

* Vitest: schema validation, JSONL and CSV round-trip per field type, redaction, scope filters, snapshot consistency, permission checks, link expiry and revocation, hash comparison.
* Bench `bench/export-20gb.ts`.
* Playwright: start, progress, download, revoke (403 afterwards), schedule; visual baselines at the seven widths, both themes.
* Nightly staging job posts the round-trip report.

**Demo**

Reviewer starts a tables-only export from Settings > Export, downloads it, unzips to see `manifest.json` and JSONL, then runs `pnpm export:verify demo empty` after importing it and reads an all-green report. Under two minutes on the fixture tenant.

**Edge cases**

* File missing from storage: `files/missing.json`, warning, export succeeds.
* Export during an import: allowed; manifest notes it.
* 2M doc versions: current only by default; `include_history` adds git history.
* Passphrase lost: unrecoverable, stated before saving.
* Shared download link: signed, owner-bound, revocable.
* Newer archive version on import: refused with upgrade hint.

**Dependencies**

PAP-199 (hard), PAP-201, PAP-43, PAP-37, PAP-128, PAP-131, PAP-59, PAP-38. Soft: PAP-179, PAP-136, PAP-57. Precondition for tenant hard-delete in PAP-33.

**Agent**

Built by Scout (Import Mapper) with Forge for snapshot semantics, Ledger for finance files and Iris for the page. Reviewed by Sentinel (Security Auditor, Edge Case Hunter) and Atlas.

**Size**

L umbrella; three M work packages. Pending sub-issue specs: [Round 2 pending issues: migration (20)](https://linear.app/paperos/document/round-2-pending-issues-migration-20-6cb063cc1be6)
