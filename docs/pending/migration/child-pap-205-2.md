---
key: "child/PAP-205/2"
title: "Round-trip `paperos` connector: import a PaperOS archive into an empty tenant and verify counts and hashes table by table"
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
identifier: "PAP-422"
status: "created"
createdAt: "2026-09-17"
---

# Round-trip `paperos` connector: import a PaperOS archive into an empty tenant and verify counts and hashes table by table

**Goal**

Prove the export is complete by re-importing it: a `paperos` `SourceConnector` that reads the v1.0 archive, recreates schema, views, records, docs, files and comments with identities preserved through `system: paperos` mappings, and a verification script that compares source and target hash by hash.

**Scope**

In: `connectors/paperos/` reading the zip stream; schema-first application (tables, fields, views) then data, docs, files, comments, PM, CRM; ledger restored through `ledger.importJournal` (reversing rules respected); `scripts/export-roundtrip.ts` producing `reports/roundtrip.json`; tenant-to-tenant move documented in `docs/migration/export-format.md`.

Out: UI (child 2), format (child 1).

**Spec**

* Identities: `external_id = original record id`, so a restore into the same tenant updates rather than duplicates.
* Files verified by sha256 before linking; mismatch listed.
* Verification compares row counts, per-table content hashes (sorted canonical JSON) and file hashes.

**Interface contract**

Provides: `registerConnector('paperos', ...)`, `verifyRoundTrip(source, target): RoundTripReport`, CLI `pnpm paperos import --connector paperos --file export.zip`. Consumes: children 1 and 2, PAP-199 engine, PAP-201 mappings, PAP-179 `importJournal` (soft). Named precondition for tenant hard-delete in PAP-33.

**Definition of done**

* Demo tenant exported, imported into an empty tenant, and `roundtrip.json` shows zero mismatches (report attached).
* Restore into the same tenant is idempotent (zero creates on second run).

**Test plan**

* Vitest: archive reader, schema-first ordering, identity mapping, hash comparison including field-type edge cases (currency minor units, dates with zones, relations).
* Integration in CI: small fixture archive round-trips in under 60 s.
* Nightly job on staging round-trips the demo tenant and posts the report.

**Demo**

Reviewer runs `pnpm paperos export --tenant demo`, then `pnpm paperos import --connector paperos --file demo.zip --tenant empty`, then `pnpm export:verify demo empty` and reads a report with all green rows. Under two minutes on the fixture tenant.

**Edge cases**

* Archive from a newer format version: refused with the version and an upgrade hint.
* Target tenant already has a table of the same name: merge fields, never change existing types.
* Ledger periods closed in the target: journals land in the current open period with a note.

**Dependencies**

Children 1 and 2 (hard), PAP-199 children 1 and 2 (hard), PAP-201, PAP-179 (soft).

**Agent**

Built by Scout (Import Mapper) with Ledger for journal restore. Reviewed by Sentinel (Edge Case Hunter) and Atlas.

**Size**

M
