---
identifier: "PAP-201"
title: "Persist external ID mappings for re-sync and incremental imports"
project: "migration"
projectName: "Migration & Import Tools"
phase: "P2"
type: "Build"
priority: 2
surfaces: ["Developer"]
milestone: "Import framework and CSV"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-199"]
blocks: ["PAP-202", "PAP-203", "PAP-204", "PAP-205", "PAP-206"]
key: "migration/id-mapping"
url: "https://linear.app/paperos/issue/PAP-201/persist-external-id-mappings-for-re-sync-and-incremental-imports"
source: "plan/specs/bucket-7.json (round-1 canonical spec JSON)"
---

# PAP-201: Persist external ID mappings for re-sync and incremental imports

**Goal**

Make importing twice safe: a persistent mapping between every external identifier (Airtable record id, Notion page id, ClickUp task id, Stripe customer id, spreadsheet row key) and the PaperOS record it became, so re-running an import updates instead of duplicating, relations resolve across runs and sources, and incremental imports fetch only what changed since the last cursor.

**Scope**

In:
- Schema `packages/import/src/schema.ts` additions: `external_id_map` (`tenant_id`, `system` (connector name plus optional instance, e.g. `airtable:appXYZ`), `external_collection`, `external_id`, `target_table`, `target_id`, `external_updated_at`, `content_hash`, `first_run_id`, `last_run_id`, `last_seen_at`, `deleted_at`), unique `(tenant_id, system, external_collection, external_id)`, index `(tenant_id, target_table, target_id)`; `import_cursor` (`source_id`, `collection`, `cursor jsonb`, `updated_at`).
- Framework hooks in `migration/import-framework` engine: before write, look up mapping to decide create vs update (mapping beats dedupe key); after write, upsert mapping with `content_hash` (stable JSON hash of the mapped record); relation second pass resolves target ids via the map including mappings created by earlier runs and other collections; records unchanged by hash are `skip` (counted, not written).
- Incremental mode: connectors with `capabilities.incremental` receive the stored cursor (`last_edited_time`, `updatedAt >`, offset tokens); after a successful run the cursor advances; deleted-in-source detection when the connector can list ids (`deleted_at` set on map, record archived optionally per mapping setting `onSourceDelete: ignore|archive|delete`).
- Consolidation with `pm_external_ref` (`pm-linear/pm-data-model`) and `crm_external_ref` (`growth/crm-model`): those tables remain the domain-facing view; the import engine writes both via one helper `recordExternalRef()` so PM and CRM code keep their existing joins.
- API: `import.mappings.lookup(system, externalId)`, `import.mappings.forRecord(table, id)` (used by UI badges "Imported from Airtable, last synced ..."), `import.mappings.relink(mappingId, newTargetId)` for manual fixes, `import.mappings.export(runId)` CSV.
- UI: record inspector badge with source link (deep link to Airtable or Notion when URL is known) and a "Mapping conflicts" list in run history.

Out: two-way sync back to sources, scheduling of incremental runs (framework exposes a `runIncremental` CLI; a Routine can call it), cross-tenant mapping.

**Spec**

- `content_hash` computed after transforms and before write, excluding volatile fields (`updated_at`, computed rollups); algorithm SHA-256 of canonical JSON.
- Conflict rules: if mapping points to a record now archived, update it and unarchive only if mapping setting says so; if mapping target was deleted, create new and mark old mapping `deleted_at` with reason.
- Two external records mapping to one target (merge in source): second mapping recorded with `merged_into`; later updates apply from either.
- Rollback of a run removes mappings it created and restores mappings it changed (framework `import_run_item.before` extended with `mappingBefore`).
- Retention: mappings kept indefinitely; `last_seen_at` allows a cleanup report for sources disconnected over 12 months.
- Performance target: lookup under 5 ms at 10M rows (btree on the unique key); relation pass uses bulk `IN` lookups per 1,000 ids.

**Definition of done**

- Vitest: create-then-rerun yields zero duplicates and correct skip counts; changed record updates; relation across two runs resolves; source delete policies; merge-in-source; rollback restores mappings.
- Bench: 1M mappings, 100k-row rerun with 5 percent changes completes under 2 minutes on staging.
- Playwright: run the fixture connector twice, see "updated" and "skipped" counts, badge on a record with source link; screenshots at 375, 1024 and 1920 in light and dark for badge and conflicts list.
- `pm_external_ref` and `crm_external_ref` written through the helper (integration test with PM and CRM fixtures).
- `docs/migration/id-mapping.md` (rules table, incremental setup, manual relink); CHANGELOG entry; Linear comment with bench and screenshots.

**Edge cases**

- External id reused by the source after deletion (Airtable never does, spreadsheets can): row-key mappings include `content_hash` sanity check; mismatch surfaces as a conflict instead of silently updating.
- Same external record imported into two different target tables intentionally: allowed via distinct `external_collection` aliases; documented.
- Cursor advanced but run partially failed: cursor only advances on `succeeded`; retries reuse the old cursor.
- Source clock skew (updated_at earlier than cursor): cursors subtract a 5-minute overlap; hash prevents redundant writes.
- Manual relink to a record of a different table: rejected.
- Tenant exports and re-imports its own PaperOS export (`migration/export`): system `paperos` mappings let round-trips keep identities.

**Dependencies**

`migration/import-framework` (hard). Coordinates with `pm-linear/pm-data-model` and `growth/crm-model` external ref tables; used by every importer and by `migration/export` round-trip.

**Agent**

Built by Scout (Import Mapper). Reviewed by Sentinel (Code Reviewer, Edge Case Hunter) and Forge (Schema Wright) for index design.

**Size**

S: one table, one cursor table and engine hooks; the rules are the work.
