---
identifier: "PAP-573"
title: "Enable pgAudit for DDL, role and bypass sessions and add database health checks: bloat, vacuum, index usage, replication slot lag and connection saturation dashboards with alerts"
project: "data-layer"
projectName: "Data Layer & Database"
phase: "P2"
type: "Infra"
priority: 3
surfaces: ["Developer"]
milestone: "Tenant-safe and observable"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-30", "PAP-40"]
blocks: []
key: "r4/data-layer/pgaudit-db-health"
url: "https://linear.app/paperos/issue/PAP-573/enable-pgaudit-for-ddl-role-and-bypass-sessions-and-add-database"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:20:46.839Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 2
dueDate: "2026-09-30"
cycle: null
---

# PAP-573: Enable pgAudit for DDL, role and bypass sessions and add database health checks: bloat, vacuum, index usage, replication slot lag and connection saturation dashboards with alerts

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Infra S

**Goal**

PAP-38 audits application rows and PAP-40 watches latency, but nobody records who ran `ALTER ROLE` or `DROP POLICY` on the cluster, and the failure modes that actually take Postgres down (bloat, a stuck replication slot from a dead Electric instance, connection exhaustion behind PgBouncer) have no dashboard. This adds the database's own audit and health checks so the threat model's B4 boundary has detection.

**Scope**

In: `pgaudit` extension enabled in `ops/db/init` for the `paperos_owner` and `paperos_readonly` roles (`pgaudit.log = 'ddl, role'`) and for any session with `app.bypass = 'on'` (`pgaudit.log = 'all'` via `SET LOCAL`), log shipping to Loki with a parser, Grafana dashboard `postgres-health` (bloat estimate, dead tuples and last vacuum per table, unused indexes, slot lag and `max_slot_wal_keep_size` headroom, connection saturation per role, long transactions, lock waits), alert rules, weekly `db:health` report posted to Linear, `docs/ops/postgres-health.md`.

Out: Application audit (PAP-38), security event routing (PAP-356 consumes the pgAudit stream), tuning changes (PAP-30 runbook).

**Spec**

* pgAudit configured in `postgresql.conf` via `ALTER SYSTEM`; DDL and role statements logged for every role; bypass sessions log all statements because `app.bypass` is the highest-risk path (PAP-34).
* Loki pipeline labels `pgaudit` lines with `role`, `class`, `command`, `object`; PAP-356 rule `db.ddl_outside_migration` fires when DDL runs outside the migrator connection.
* Dashboard panels from `pg_stat_user_tables`, `pg_stat_user_indexes`, `pg_replication_slots`, `pg_stat_activity`, `pg_locks` and a bloat estimate query; refresh 1 minute.
* Alerts: slot lag over 30 s or retained WAL over 3 GB, connections over 80 percent of `max_connections` per role, a transaction older than 5 minutes, dead tuples over 20 percent on a table larger than 1 GB, an unused index larger than 100 MB (weekly, informational).
* `pnpm db:health` prints the same numbers as a table and posts the weekly report through PAP-97 when available.

**Interface contract**

Provides: pgAudit configuration, Loki labels, dashboard `postgres-health`, alert rules, script `db:health`, docs.

Consumes: Postgres init and exporter (PAP-30), Loki, Grafana and alerting (PAP-40), bypass semantics (PAP-34), security telemetry rules (PAP-356, soft), Linear comment helper (PAP-97, soft).

**Definition of done**

* `ALTER ROLE` as owner appears in Loki with labels; a bypass session's statements are logged; DDL outside the migrator fires the rule (evidence).
* Dashboard provisioned from JSON with no manual clicks; screenshots at 1280 and 1920; each alert fired once by a synthetic condition (slot lag via a paused Electric container).
* Weekly report posted once; docs; CHANGELOG; Linear comment.

**Test plan**

* Unit: Loki parser fixtures for pgAudit lines, bloat query on a fixture, alert threshold rendering.
* E2E: CI compose: enable pgAudit, run a DDL as owner, assert the log line; pause the Electric container and assert slot lag grows in the exporter.

**Demo**

Reviewer runs `pnpm db:health` over the tailnet, opens the dashboard, then stops the Electric container for a minute and watches the slot lag panel and alert. Under two minutes.

**Edge cases**

* pgAudit log volume on bulk migrations: DDL only, so bounded; `all` only inside bypass sessions which are rare and audited anyway.
* PgBouncer hides client addresses: `application_name` carries the service name (PAP-267 sets it).
* Log line over Loki's limit: truncated with a marker; full statement hash kept.

**Dependencies**

Blocked by PAP-30 and PAP-40 (hard). Soft: PAP-34, PAP-356, PAP-97.

**Agent**

Builder: Forge (Ops Runner). Reviewer: Sentinel (Security Auditor).

**Size**

S: half a session.
