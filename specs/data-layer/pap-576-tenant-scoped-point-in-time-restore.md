---
identifier: "PAP-576"
title: "Tenant-scoped point-in-time restore: PITR into a scratch database, tenant extract, diff preview and selective re-import through the import engine"
project: "data-layer"
projectName: "Data Layer & Database"
phase: "P2"
type: "Infra"
priority: 4
surfaces: ["Staff"]
milestone: "Tenant-safe and observable"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-30", "PAP-347"]
blocks: []
key: "r4/data-layer/tenant-pitr-restore"
url: "https://linear.app/paperos/issue/PAP-576/tenant-scoped-point-in-time-restore-pitr-into-a-scratch-database"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:09.875Z"
model: "claude-opus-5"
effort: "medium"
estimate: 3
dueDate: null
cycle: null
---

# PAP-576: Tenant-scoped point-in-time restore: PITR into a scratch database, tenant extract, diff preview and selective re-import through the import engine

**Model / Effort:** Opus 5 (`claude-opus-5`) / medium — Infra M

**Goal**

Deferred to v0.2 (past 2026-10-01): PAP-334's 30-day trash covers most mistakes, but a bulk import gone wrong, an automation loop or an agent with a bad filter can damage one tenant's data in ways row-level trash cannot undo, and cluster-wide PITR (PAP-30) would roll back every other tenant. This restores one tenant to a moment in time: recover the cluster to a scratch database, extract the tenant, show the diff, and re-import selected tables or rows with the import engine's dry-run and rollback semantics.

**Scope**

In: `ops/db/tenant-restore.sh` (pgBackRest restore to `scratch_<ts>` with `--target-time`), `packages/db/src/restore/{extract,diff}.ts` producing a PaperOS archive (PAP-420 format) from the scratch database for one tenant, diff preview per table (rows added, changed, removed since the target time), selective re-import through the `paperos` connector (PAP-422) with PAP-348 dry run and rollback, staff console page `/console/data/restore` behind `data.restore` permission and a Needs Justin card for tenants over 1 GB, `docs/runbooks/tenant-restore.md`.

Out: Cluster PITR itself (PAP-30), file object versions (MinIO versioning is on; the extract references versions), Yjs document history (PAP-607), trash and undo (PAP-334).

**Spec**

* Flow: staff picks tenant and target time; the job restores the newest base backup plus WAL to the target into a scratch database on the same host (time-boxed, disk check first), extracts the tenant with `purgeOrder()` from PAP-561 reversed, writes the archive to MinIO, and drops the scratch database.
* Diff: keyed by primary key per table; shows counts and a sample; changed rows compare `updated_at` and a row hash; the preview is stored as an `import_run` in `dry_run` state.
* Apply: selected tables or rows go through the import engine with `mode: 'restore'` (upsert by id, no new ids), audited with reason and `impersonation`-style banner for the operator; rollback available for 24 h via PAP-348.
* Guards: tenant must not be `purging`; concurrent restores per tenant refused; scratch database limited to one at a time; wall clock over 2 h aborts.
* Everything runs under `paperos_owner` inside audited `app.bypass` transactions (PAP-34, PAP-38).

**Interface contract**

Provides: Script `tenant-restore.sh`, job `tenant.restore`, procedures `restore.preview|apply|list`, page `/console/data/restore`, runbook.

Consumes: PITR and backups (PAP-30), import engine and rollback (PAP-347, PAP-348), archive format and round-trip connector (PAP-420, PAP-422), purge order (PAP-561), audit and bypass (PAP-34, PAP-38), console (PAP-63), decision cards (PAP-94).

**Definition of done**

* Seeded tenant damaged by a scripted bulk update is restored to five minutes earlier through the console; diff preview matches the script's changes; other tenants untouched (checksums).
* Guards tested: purging tenant, concurrent request, oversize tenant card; scratch database dropped after every run including failures.
* Runbook; CHANGELOG; Linear comment with the recording.

**Test plan**

* Unit: target-time parsing, diff algorithm on fixture tables (added, changed, removed, unchanged), guard matrix, archive writer for one tenant.
* E2E: CI on a self-hosted runner: restore a scratch stanza to a target time, extract, diff and apply one table; assert row-level equality.

**Demo**

Reviewer runs the damage script on the demo tenant, opens Restore, picks 'ten minutes ago', reads the diff (200 rows changed in `records`), applies that table and reloads the grid. Two minutes.

**Edge cases**

* Schema migrated between target time and now: extract runs on the old schema; the import maps columns through the connector's mapping model and reports unmappable ones.
* Rows created after the target time: kept by default; a 'remove rows created after' option exists with a second confirmation.
* WAL gap in the backup: restore fails early with the nearest recoverable time.

**Dependencies**

Blocked by PAP-30 and PAP-347 (hard). Soft: PAP-348, PAP-420, PAP-422, PAP-63, PAP-94, PAP-561. Deferred to v0.2; not claimable before 10-01.

**Agent**

Builder: Forge (Ops Runner) with Scout (Import Mapper). Reviewer: Sentinel (Security Auditor; Edge Case Hunter for the diff).

**Size**

M: one session.

*Round 4 critique fix (2026-09-18):* resolved 2 round-4 file keys in this description to Linear identifiers: `r4/data-layer/tenant-purge` = PAP-561, `r4/realtime/doc-history` = PAP-607.
