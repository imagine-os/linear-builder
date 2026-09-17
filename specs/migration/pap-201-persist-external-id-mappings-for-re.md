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
blockedBy: ["PAP-199", "PAP-349"]
blocks: ["PAP-202", "PAP-203", "PAP-204", "PAP-205", "PAP-206", "PAP-415", "PAP-417", "PAP-422", "PAP-423"]
key: "migration/id-mapping"
url: "https://linear.app/paperos/issue/PAP-201/persist-external-id-mappings-for-re-sync-and-incremental-imports"
source: "Linear snapshot 2026-09-17T15:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T13:41:54.721Z"
model: "claude-sonnet-5"
effort: "medium"
---

# PAP-201: Persist external ID mappings for re-sync and incremental imports

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Build S

**Goal**

Make importing twice safe: a persistent map from every external identifier to the PaperOS record it became, so re-runs update instead of duplicate, relations resolve across runs and sources, and incremental imports fetch only what changed since the last cursor.

**Scope**

In:

* Schema: `external_id_map` (`tenant_id`, `system` such as `airtable:appXYZ`, `external_collection`, `external_id`, `target_table`, `target_id`, `external_updated_at`, `content_hash`, `first_run_id`, `last_run_id`, `last_seen_at`, `deleted_at`, `merged_into`), unique on `(tenant_id, system, external_collection, external_id)`, index on target; `import_cursor` (`source_id`, `collection`, `cursor jsonb`, `updated_at`).
* Engine hooks in PAP-199: lookup before write (mapping beats dedupe key), upsert after write with `content_hash`, unchanged records counted as `skip`, relation pass resolves through the map across runs and collections.
* Incremental mode for connectors with `capabilities.incremental`; cursor advances only on `succeeded`; source deletions handled per `onSourceDelete: ignore|archive|delete`.
* One helper `recordExternalRef()` that also writes `pm_external_ref` (PAP-100) and `crm_external_ref` (PAP-187).
* Record badge "Imported from Airtable, last synced ..." with deep link; "Mapping conflicts" list in run history.

Out: two-way sync, scheduling (a Routine calls `runIncremental`), cross-tenant mapping.

**Spec**

* `content_hash` = SHA-256 of canonical JSON after transforms, excluding volatile fields.
* Mapping to an archived record: update, unarchive only if the mapping setting says so; deleted target: create new, old mapping gets `deleted_at` with reason.
* Two external records merged in source: second mapping gets `merged_into`.
* Rollback removes mappings a run created and restores changed ones via `mappingBefore` on `import_run_item`.
* Cursors subtract a 5-minute overlap for clock skew; hash prevents redundant writes.
* Lookup under 5 ms at 10M rows; relation pass uses bulk `IN` per 1,000 ids.

**Interface contract**

Provides: tables above, `recordExternalRef()`, oRPC `import.mappings.lookup|forRecord|relink|export`, `runIncremental(sourceId)`, component `ImportedBadge`, engine hooks `beforeWrite`, `afterWrite`, `resolveRelations`. Consumes: PAP-199 engine and `import_run_item`, PAP-100 and PAP-187 ref tables. Consumers: PAP-200, PAP-202, PAP-203, PAP-204, PAP-206 (two-pass relations), PAP-205 (`system: paperos` round trip), PAP-207 (`system: template:<type>@<version>`).

**Definition of done**

* Re-run yields zero duplicates and correct skip counts; changed records update; relations across two runs resolve; delete policies and merge-in-source behave; rollback restores mappings.
* Bench: 1M mappings, 100k-row rerun with 5 percent changes under 2 minutes on staging.
* `pm_external_ref` and `crm_external_ref` written through the helper (integration test).
* Screenshots at 375, 1024 and 1920 in light and dark for badge and conflicts list.
* `docs/migration/id-mapping.md`; CHANGELOG; Linear comment with bench and screenshots.

**Test plan**

* Vitest: hash stability across key order, create-then-rerun, changed record, cross-run relation, each `onSourceDelete` policy, merge, rollback restore, relink rejection across tables.
* Bench `bench/id-mapping-1m.ts`.
* Playwright: run fixture connector twice, read "updated" and "skipped" counts, open a record badge and follow the source link; visual baselines at three widths, both themes.

**Demo**

Reviewer runs the fixture import twice, sees the second run report 0 created and N skipped, edits one source row in the fixture, runs again and sees exactly 1 updated with a badge on that record. Under two minutes.

**Edge cases**

* External id reused after deletion (spreadsheets): hash mismatch surfaces as conflict.
* Same external record into two target tables intentionally: distinct `external_collection` aliases.
* Partial failure: cursor unchanged; retry reuses it.
* Manual relink to a different table: rejected.
* PaperOS export re-imported: `system: paperos` keeps identities.

**Dependencies**

PAP-199 (hard). Coordinates with PAP-100 and PAP-187. Blocks PAP-202, PAP-203, PAP-204, PAP-205, PAP-206.

**Agent**

Built by Scout (Import Mapper). Reviewed by Sentinel (Code Reviewer, Edge Case Hunter) and Forge (Schema Wright) for indexes.

**Size**

S: two tables and engine hooks; the rules are the work.
