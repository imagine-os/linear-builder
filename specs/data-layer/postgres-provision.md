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
blocks: ["PAP-26", "PAP-270", "PAP-36", "PAP-40"]
key: "data-layer/postgres-provision"
url: "https://linear.app/paperos/issue/PAP-30/provision-postgres-17-on-the-self-hosted-vps-with-automated-backups"
source: "plan/specs/bucket-0.json (round-1 canonical spec JSON)"
---

# PAP-30: Provision Postgres 17 on the self-hosted VPS with automated backups and point-in-time recovery

**Goal**

Stand up the production and staging Postgres 17 instances on the Hetzner VPS under Coolify, with continuous WAL archiving to object storage, nightly base backups, point-in-time recovery proven by a drill, and the extensions every later issue needs (pgvector, pg_trgm, pgcrypto, pg_stat_statements) pre-installed.

**Scope**

In:
- Coolify service definitions (exported as `ops/compose/postgres.yml` for reproducibility) for `pg-prod` and `pg-staging` using the `pgvector/pgvector:pg17` image (or `postgres:17` plus extension build; record choice).
- `pgBackRest` (preferred) or `WAL-G` sidecar shipping WAL to a MinIO bucket `pg-backups` (MinIO deployed here minimally; full file service is `data-layer/file-storage`); nightly full, hourly incremental, 14-day retention.
- Roles: `paperos_owner` (migrations only, `DATABASE_URL_MIGRATOR`), `paperos_app` (runtime, `NOBYPASSRLS`), `paperos_readonly` (reporting/agents), `electric` (logical replication), `paperos_backup`.
- Config tuned for 8 GB box: `shared_buffers 2GB`, `work_mem 16MB`, `max_connections 200` behind PgBouncer (transaction mode, `pgbouncer` container) except Electric which needs a direct connection.
- `wal_level = logical`, `max_replication_slots 10`, `max_wal_senders 10` (for `data-layer/local-first-sync`).
- TLS (Coolify/Caddy-issued certs or self-signed with client verification), firewall allowing only the Docker network and the tailnet/VPN.
- Monitoring hooks: `postgres_exporter` container for `data-layer/observability`.
- Restore drill script `ops/db/restore-drill.sh` that restores to a timestamp into a scratch container and verifies row counts.

Out: schema (`data-layer/drizzle-schema`), RLS policies, read replicas, managed cloud Postgres.

**Spec**

- Secrets via Coolify env; documented names match `serverEnvSchema` in `app-shell/env-config`.
- `ops/db/init/*.sql` run on first boot: create roles, databases `paperos_prod`/`paperos_staging`, extensions, `ALTER SYSTEM` settings.
- Backup verification: daily `pgbackrest verify` plus a weekly automated restore drill (cron in Coolify) posting result to Linear via `pm-linear/webhooks` when available, else to a log.
- `ops/db/README.md`: connection strings per role, how to get a psql shell, PITR procedure with exact commands, RPO 1 h, RTO 30 min targets.
- `pnpm db:up` brings a local Postgres 17 with the same init scripts via Docker Compose for developers and CI (`ops/compose/dev.yml`).

**Definition of done**

- Both instances reachable through PgBouncer with TLS from the API container; `SELECT version()` shows 17.x and all extensions installed.
- WAL archives appear in MinIO; `pgbackrest info` shows a full backup.
- Restore drill run: recover staging to a point 10 minutes earlier and confirm a deliberately inserted then deleted row is present; transcript attached.
- Local `pnpm db:up` works on Linux and macOS; CI uses the same compose file.
- Screenshots of Coolify service page, `pgbackrest info`, and exporter metrics (1280 and 1920).
- `ops/db/README.md` complete; ADR `docs/adr/0003-postgres-hosting.md`; CHANGELOG; Linear comment with drill transcript link.

**Edge cases**

- MinIO unavailable during archive: `archive_command` failure must not stop writes; WAL accumulates; alert when disk over 70 percent.
- Disk full on VPS: `pg_wal` on same volume; set `max_wal_size 2GB` and monitor.
- PgBouncer transaction mode breaks `LISTEN/NOTIFY` and prepared statements: document; Electric and Hocuspocus connect directly.
- Coolify redeploy recreating the container must not lose data: named volume, tested.
- Time zone: cluster in UTC; app converts.
- Password rotation: procedure that updates Coolify env and reloads PgBouncer without downtime.

**Dependencies**

`app-shell/vps-coolify-bootstrap` (hard: host, Coolify, tailnet, object storage for WAL archives, sops). Unblocks `app-shell/app-deploy-pipeline` (staging and production databases), `data-layer/local-first-sync` (logical replication), `realtime/yjs-server`, `identity/better-auth` on staging. Schema work itself starts on `data-layer/local-dev-stack`, not here.

**Agent**

Built by Forge (Ops Runner sub-agent). Reviewed by Sentinel (Security Auditor for roles, TLS and firewall; Code Reviewer for scripts).

**Size**

M: standard components, but backups must be proven by an actual restore, not configured and assumed.
