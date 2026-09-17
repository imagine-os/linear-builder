---
identifier: "PAP-30"
title: "Provision Postgres 17 on the self-hosted VPS with automated backups and point-in-time recovery"
project: "data-layer"
projectName: "Data Layer & Database"
phase: "P0"
type: "Infra"
priority: 1
surfaces: ["Developer"]
milestone: "Postgres + Drizzle baseline"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-25"]
blocks: ["PAP-26", "PAP-36", "PAP-40", "PAP-270", "PAP-354"]
key: "data-layer/postgres-provision"
url: "https://linear.app/paperos/issue/PAP-30/provision-postgres-17-on-the-self-hosted-vps-with-automated-backups"
source: "Linear snapshot 2026-09-17T15:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T13:40:56.716Z"
model: "claude-opus-5"
effort: "medium"
---

# PAP-30: Provision Postgres 17 on the self-hosted VPS with automated backups and point-in-time recovery

**Model / Effort:** Opus 5 (`claude-opus-5`) / medium — Infra M

**Goal**

Stand up production and staging Postgres 17 on the PAP-25 host under Coolify with continuous WAL archiving, nightly base backups, point-in-time recovery proven by a drill, PgBouncer in front, logical replication on for Electric (PAP-36), and every extension later issues need pre-installed.

**Scope**

In:

* Coolify services exported as `ops/compose/postgres.yml` for `pg-prod` and `pg-staging` on `pgvector/pgvector:pg17`.
* `pgBackRest` sidecar shipping WAL to bucket `paperos-backups/pg` (PAP-25): nightly full, hourly incremental, 14-day retention; daily `verify`; weekly automated restore drill.
* Roles `paperos_owner`, `paperos_app` (`NOBYPASSRLS`), `paperos_readonly`, `electric` (replication), `paperos_backup`.
* Tuning for 8 GB: `shared_buffers 2GB`, `work_mem 16MB`, `max_connections 200`, `wal_level logical`, `max_replication_slots 10`, `max_wal_size 2GB`.
* PgBouncer (transaction mode) for the API; direct connections for Electric and Hocuspocus.
* `postgres_exporter` for PAP-40.

Out: schema (PAP-32), the local compose stack (PAP-42), MinIO (PAP-37).

**Spec**

* `ops/db/init/*.sql` on first boot: roles, databases `paperos_prod` and `paperos_staging`, extensions `vector`, `pg_trgm`, `pgcrypto`, `pg_stat_statements`, `citext`, `ALTER SYSTEM` settings.
* Secrets in Coolify env from sops; names match `serverEnvSchema` (PAP-17): `DATABASE_URL` (app via PgBouncer), `DATABASE_URL_MIGRATOR` (owner, direct), `DATABASE_URL_ELECTRIC`.
* `ops/db/README.md`: connection strings per role, psql access over the tailnet, PITR procedure with exact commands, RPO 1 h, RTO 30 min.
* Weekly drill result posted to Linear via PAP-97 when available, else logged.
* Password rotation runbook updating Coolify env and reloading PgBouncer without downtime.

**Interface contract**

Provides:

* Env vars `DATABASE_URL`, `DATABASE_URL_MIGRATOR`, `DATABASE_URL_READONLY`, `DATABASE_URL_ELECTRIC` per environment, stored in `ops/secrets/<env>-db.enc.yaml`.
* Role semantics: `paperos_app` is subject to RLS (PAP-34 relies on `NOBYPASSRLS`); `paperos_owner` runs migrations (PAP-32, PAP-26); `electric` has `REPLICATION` and a publication `electric_pub` (PAP-36).
* Extensions guaranteed present: `vector` (PAP-39), `pg_trgm` (PAP-39), `pgcrypto` (field-encryption issue, PAP-38 hashes), `pg_stat_statements` (PAP-40), `citext` (PAP-33).
* Metrics endpoint `postgres_exporter:9187` on the internal network (PAP-40).
* Backup repo path `paperos-backups/pg/<env>` (object-storage DR issue restores from it).

Consumes: host, Coolify, buckets and sops (PAP-25).

**Definition of done**

* Both instances reachable through PgBouncer with TLS from a test container; `SELECT version()` shows 17.x and all extensions.
* WAL archives in the bucket; `pgbackrest info` shows a full backup.
* Restore drill: recover staging to 10 minutes earlier and find a row inserted then deleted (transcript).
* Screenshots of the Coolify service page, `pgbackrest info` and exporter metrics at 1280 and 1920.
* `ops/db/README.md`, ADR `0003-postgres-hosting.md`, CHANGELOG, Linear comment with the drill transcript.

**Test plan**

* Unit: `bats` test that `init/*.sql` runs idempotently twice on a local `pgvector:pg17` container.
* Integration: connect as each role and assert `rolbypassrls`, `rolreplication`, `SHOW wal_level`, publication existence.
* Backup: `pgbackrest verify` in CI against a scratch stanza; scheduled drill script asserts the deleted row is present.
* Failure: stop MinIO, write 100 rows, restart, assert WAL catch-up and `archive_command` alerts (log).
* Ops: disk-usage alert fires in a test by lowering the threshold.

**Demo**

Reviewer runs `psql "$DATABASE_URL_READONLY" -c "select version(); \dx"` over the tailnet, then `pgbackrest --stanza=staging info` and opens the exporter metrics in Grafana or `curl`. Under 90 seconds.

**Edge cases**

* MinIO unavailable during archive: writes continue, WAL accumulates, alert at 70 percent disk.
* PgBouncer transaction mode breaks `LISTEN/NOTIFY` and session `SET`: documented; `SET LOCAL` only (PAP-32 lint).
* Coolify redeploy must keep the named volume (tested).
* Cluster in UTC; app converts.
* Replication slot left by a dead Electric instance fills the disk: `max_slot_wal_keep_size 4GB` and a monitor.

**Dependencies**

PAP-25 (hard). Unblocks PAP-26, PAP-36 (logical replication), PAP-40 (exporter), PAP-140. Schema work starts on PAP-42, not here.

**Agent**

Built by Forge (Ops Runner). Reviewed by Sentinel (Security Auditor).

**Size**

M: compose, init scripts, backup sidecar and one drill.
