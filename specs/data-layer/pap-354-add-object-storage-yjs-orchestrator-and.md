---
identifier: "PAP-354"
title: "Add object-storage, Yjs, orchestrator and sops-key backups and a monthly platform-wide disaster-recovery drill restoring everything on a fresh host against RPO 1 h and RTO 4 h"
project: "data-layer"
projectName: "Data Layer & Database"
phase: "P1"
type: "Infra"
priority: 1
surfaces: ["Developer"]
milestone: "Tenant-safe and observable"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-30", "PAP-37", "PAP-96", "PAP-140"]
blocks: ["PAP-88"]
key: "security/platform-dr"
url: "https://linear.app/paperos/issue/PAP-354/add-object-storage-yjs-orchestrator-and-sops-key-backups-and-a-monthly"
source: "Linear snapshot 2026-09-17T15:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T13:42:36.792Z"
model: "claude-opus-5"
effort: "medium"
---

# PAP-354: Add object-storage, Yjs, orchestrator and sops-key backups and a monthly platform-wide disaster-recovery drill restoring everything on a fresh host against RPO 1 h and RTO 4 h

**Model / Effort:** Opus 5 (`claude-opus-5`) / medium — Infra M

**Goal**

PAP-30 proves Postgres PITR and PAP-53/PAP-274 prove the forge, but tenant files in MinIO, Yjs document state, the orchestrator database, Coolify definitions and the sops age keys have no backup and nobody has restored the whole platform at once. This issue sets the platform recovery objectives (RPO 1 h for data, RTO 4 h to a working staging-equivalent stack) and proves them monthly with a scripted drill on a throwaway host.

Merges `gap/data-layer/platform-dr` (same drill; merged 2026-09-17, FIX-6). From it: the smoke suite reuses PAP-86 flows, the restore uses only images from our own registry (PAP-50; GitHub blocked as in PAP-53), and the drill proves field decryption works with keys restored from escrow (PAP-353).

**Scope**

* In: restic backup jobs for MinIO buckets, `yjs_documents` and `yjs_updates` (already in Postgres, verified as part of PITR), orchestrator schema, Coolify resource exports, Caddy config; encrypted off-site copy of the sops age private keys and restic passwords in a second provider; `ops/dr/platform-drill.sh`; `docs/runbooks/platform-dr.md` with RPO/RTO table; monthly cron and Linear report; backup monitoring hooks for PAP-356.
* Out: forge DR (PAP-53), Postgres PITR mechanics (PAP-30), Linear (SaaS, exported nightly by PAP-101 backfill as a bonus), application code (in git on two forges).

**Spec**

* Backups: restic repo `paperos-platform-backups` in Hetzner Object Storage (separate bucket and credential from `pg-backups`) with hourly `minio` bucket sync (`mc mirror` into the restic source then `restic backup`), hourly orchestrator `pg_dump` (schema `orchestrator`), daily Coolify export (`ops/coolify/*.json` via API) and Caddy config; retention 24 hourly, 14 daily, 8 weekly; `restic check --read-data-subset=5%` weekly.
* Key escrow: sops age private keys, restic passwords and object-storage credentials are age-encrypted to Justin's offline key and stored in a second provider (Backblaze B2 or Cloudflare R2 free tier) plus a printed QR in Justin's possession (PAP-301 owns the human procedure); the drill starts from that escrow, not from the live host.
* Targets: RPO 1 h (Postgres WAL and hourly object sync), RTO 4 h for the full stack, 30 min for Postgres alone (PAP-30); measured, not asserted.
* Drill `ops/dr/platform-drill.sh`: (1) `hcloud server create` cpx31 from cloud-init; (2) install Coolify and Caddy via `ops/bootstrap.sh` (PAP-25) pointed at `dr.<domain>`; (3) restore sops keys from escrow; (4) restore Postgres to the newest recoverable point (PAP-30 procedure) and orchestrator schema; (5) restore MinIO buckets; (6) deploy `apps/api`, `apps/web`, Hocuspocus, Electric from Coolify exports with immutable image digests (PAP-26); (7) run the smoke suite: sign in as a seeded user, open a table, open a Yjs doc and see the last edit, download a file, orchestrator `/status`; (8) compute RPO as `now - max(latest restored row timestamps)` and RTO as wall clock; (9) write `docs/runbooks/dr-reports/platform-<date>.md` with phase timings, targets met or missed, gaps as Linear issues; (10) destroy unless `--keep`; abort after 6 h.
* Monitoring: `backup_age_seconds` per job exported for PAP-40; alert at 2 h for hourly jobs, 26 h for daily; `restic check` failures alert immediately.
* Schedule: first Sunday monthly via Forgejo Actions cron, report posted to Linear; first run before the 2026-09-30 release candidate.

**Interface contract**

* Provides: restic repo layout, `ops/dr/platform-drill.sh`, report template, metrics `backup_age_seconds{job}`, `backup_last_success{job}`, events `dr.drill.completed`, runbook.
* Consumers: PAP-88/PAP-252 release policy (a release candidate requires a green drill within 30 days), PAP-356 (backup alerts), PAP-219 incident playbook (restore procedure), PAP-53 (shares the host bootstrap).
* Requires: PAP-30 PITR, PAP-37 MinIO, PAP-140 persistence tables, PAP-96 orchestrator schema, PAP-25 bootstrap, PAP-26 image digests.

**Definition of done**

* One full drill completed with RPO under 1 h and RTO under 4 h, report committed, screenshots of the restored app at 1280 and the Yjs doc with its last edit.
* Escrow verified: the drill decrypts keys from the second provider using Justin's offline key procedure (Justin performs the decrypt step once; recorded).
* Backup age metrics visible in Grafana; induced failure (pause the hourly job) fires the alert within 2 h.
* `restic check` weekly job green for two weeks.
* Runbook; changelog; Linear comment with the report link.

**Test plan**

* Unit: RPO/RTO calculators, report renderer.
* Integration: restore MinIO and orchestrator schema into scratch containers in CI on a self-hosted runner (PAP-50).
* e2e: the monthly drill itself.
* No UI beyond screenshots.

**Demo**

Open the latest `platform-<date>.md`: the phase table, RPO 41 min, RTO 3 h 12 min, the restored app screenshot; then show `backup_age_seconds` in Grafana. One minute.

**Edge cases**

* Object storage region outage: escrow in a second provider; restic repo replicated weekly to that provider (`rclone sync`).
* Yjs documents with updates not yet compacted: restore includes `yjs_updates`; compaction runs on first load.
* Orchestrator state restored with claims in flight: PAP-96 re-queues `interrupted` sessions; the drill verifies no duplicate PRs.
* Coolify version drift between live and drill: exports pinned to a Coolify version; drill installs that version.
* Drill cost: one cpx31 for at most 6 h monthly, roughly EUR 0.10; abort guard enforced.

**Dependencies**

Blocked by PAP-30, PAP-37, PAP-140, PAP-96. Blocks PAP-88. Soft: PAP-25, PAP-26, PAP-50, PAP-53, PAP-301.

**Agent**

Built by Forge (Ops Runner sub-agent); reviewed by Sentinel (Security Auditor); Justin performs the escrow decrypt once.

**Size**

M
