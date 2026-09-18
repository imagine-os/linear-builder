---
identifier: "PAP-562"
title: "Platform backup jobs: restic for MinIO buckets, hourly orchestrator schema dumps, daily Coolify and Caddy exports, the off-site key escrow bundle and `backup_age_seconds` alerts"
project: "data-layer"
projectName: "Data Layer & Database"
phase: "P1"
type: "Infra"
priority: 1
surfaces: ["Developer"]
milestone: "Tenant-safe and observable"
state: "Backlog"
parent: "PAP-354"
children: []
blockedBy: ["PAP-30", "PAP-37", "PAP-96", "PAP-691"]
blocks: ["PAP-563"]
key: "r4/data-layer/platform-backups"
url: "https://linear.app/paperos/issue/PAP-562/platform-backup-jobs-restic-for-minio-buckets-hourly-orchestrator"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:07.862Z"
model: "claude-opus-5"
effort: "medium"
estimate: 3
dueDate: "2026-09-30"
cycle: null
---

# PAP-562: Platform backup jobs: restic for MinIO buckets, hourly orchestrator schema dumps, daily Coolify and Caddy exports, the off-site key escrow bundle and `backup_age_seconds` alerts

**Model / Effort:** Opus 5 (`claude-opus-5`) / medium — Infra M

**Goal**

First half of PAP-354: make every stateful thing outside Postgres recoverable. PAP-30 covers WAL and base backups; this child adds restic backups for tenant files, the orchestrator schema, Coolify resource definitions and Caddy config, replicates the repo to a second provider, escrows the keys that unlock it all, and exports the backup-age metrics the monthly drill and PAP-356 alert on.

**Scope**

In: `ops/backup/{restic.env,minio-sync.sh,orchestrator-dump.sh,coolify-export.ts,caddy-export.sh}`, systemd or Coolify cron definitions, restic repo `paperos-platform-backups` in Hetzner Object Storage with weekly `rclone sync` to Backblaze B2 or Cloudflare R2, escrow bundle builder `ops/backup/escrow.sh` (age-encrypted to Justin's offline key, PAP-301), `backup_age_seconds{job}` and `backup_last_success{job}` exporter, `docs/runbooks/backups.md`.

Out: The drill script, report and monthly run (sibling PAP-563); Postgres PITR (PAP-30); forge backups (PAP-274).

**Spec**

* Hourly: `mc mirror` MinIO buckets into the restic source dir then `restic backup --tag minio`; `pg_dump --schema=orchestrator` piped to `restic backup --stdin --tag orchestrator`.
* Daily: Coolify resources exported via API to `ops/coolify/*.json` and committed to `paperos-infra`; Caddyfile snapshot; both also in restic.
* Retention 24 hourly, 14 daily, 8 weekly; `restic forget --prune` weekly; `restic check --read-data-subset=5%` weekly with failure alert.
* Separate object-storage credential and bucket from `pg-backups`; credentials in sops, injected by Coolify (PAP-25); no credential on the app containers.
* Escrow bundle: sops age private keys, restic passwords, object-storage credentials, age-encrypted to Justin's offline key, uploaded to the second provider and hash-recorded in `docs/security/root-of-trust.md` (PAP-301 owns the human procedure).
* Metrics scraped by PAP-40; alerts at 2 h for hourly jobs, 26 h for daily, immediate on `restic check` failure; alert routes through PAP-356 when present, else email.

**Interface contract**

Provides: restic repo layout and tags, scripts above, escrow bundle format and hash, metrics `backup_age_seconds{job}`, `backup_last_success{job}`, runbook.

Consumes: Buckets and sops (PAP-25), MinIO (PAP-37), orchestrator schema (PAP-96), Postgres exporter pattern (PAP-30), Grafana and alerting (PAP-40), root-of-trust procedure (PAP-301). Consumed by the sibling drill, PAP-356, PAP-219 incident playbook.

**Definition of done**

* All four job classes running on staging for 48 hours with green `restic check`; `restic snapshots` shows tags and the retention policy applied.
* Induced failure (pause the hourly job) fires the 2 h alert; evidence attached.
* Escrow bundle uploaded to the second provider; decrypt tested once with Justin's offline key (recorded by PAP-301) and the hash committed.
* Runbook with restore commands per component; CHANGELOG; Linear comment with the snapshot listing.

**Test plan**

* Unit: cron expression and retention arithmetic, exporter output format, escrow bundle manifest validation, Coolify export diff stability (sorted keys).
* E2E: CI on a self-hosted runner (PAP-50): back up a scratch MinIO bucket and orchestrator schema into a scratch restic repo, restore both into fresh containers and diff checksums.

**Demo**

Reviewer runs `restic snapshots --tag minio` over the tailnet, opens the backup-age panel in Grafana, then restores yesterday's orchestrator dump into a scratch database with the runbook command. Under two minutes.

**Edge cases**

* Object-storage region outage: weekly replica in the second provider; runbook says which repo to restore from.
* MinIO bucket growing past the hourly window: `mc mirror` is incremental; alert when a job exceeds 45 minutes.
* Coolify API version drift: export pinned to the Coolify version; drift fails the daily job loudly.
* Escrow key rotation (PAP-25 `secrets:rekey`): bundle rebuilt and re-hashed the same day; old bundle deleted after the next drill.

**Dependencies**

Blocked by PAP-30, PAP-37, PAP-96 (hard). Soft: PAP-25, PAP-40, PAP-301, PAP-356, PAP-50. Blocks the sibling PAP-563.

**Agent**

Builder: Forge (Ops Runner). Reviewer: Sentinel (Security Auditor).

**Size**

M: one session.

*Round 4 critique fix (2026-09-18):* resolved 1 round-4 file key in this description to Linear identifiers: `r4/data-layer/platform-dr-drill` = PAP-563.
