---
identifier: "PAP-38"
title: "Build append-only audit log with actor (human or agent), diff and reason fields"
project: "data-layer"
projectName: "Data Layer & Database"
phase: "P1"
type: "Build"
priority: 2
surfaces: ["Agent", "Staff"]
milestone: "Local-first sync working"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-33"]
blocks: ["PAP-61", "PAP-174", "PAP-333", "PAP-355", "PAP-356", "PAP-388"]
key: "data-layer/audit-log"
url: "https://linear.app/paperos/issue/PAP-38/build-append-only-audit-log-with-actor-human-or-agent-diff-and-reason"
source: "Linear snapshot 2026-09-17T13:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T04:05:40.025Z"
---

# PAP-38: Build append-only audit log with actor (human or agent), diff and reason fields

**Goal**

Record every mutation as an immutable `audit_event` with who (human, agent, service or system), what changed (before, after, diff), why (a reason agents must supply) and which request caused it, so Justin can answer "who changed this and why" for any row and reviewers can trace agent behaviour to data.

**Scope**

In:

* Append-only guarantees: table owned by `paperos_owner`; app role has INSERT and SELECT; triggers reject UPDATE and DELETE; monthly partitions, 24-month retention, Parquet archival to MinIO.
* Generic trigger `paperos.audit_trigger()` attached by the PAP-34 generator, reading `app.actor_id`, `app.actor_kind`, `app.request_id`, `app.reason`.
* Diff `{ field: { from, to } }` excluding `updated_at`; redaction via `paperos.audit_redactions` fed by PAP-41's `pii.json`.
* Per-tenant hash chain; `pnpm audit:verify`.
* oRPC `audit.list`, `audit.forEntity`; `<AuditTrail/>` in `@paperos/ui`.

Out: retention enforcement for other tables (retention issue), log shipping (PAP-40).

**Spec**

* Actions `insert|update|delete|restore|bypass_read`.
* Opt-out list for high-churn tables in `packages/db/src/audit/exclusions.ts`.
* Partitions three months ahead via `pg_partman` or a monthly cron; default partition as safety net with alert.
* Archival monthly: partitions older than 24 months to `audit/<yyyy>/<mm>.parquet` via DuckDB in a PAP-43 job, then detach and drop after checksum.
* `hash = sha256(prev_hash || canonical json)` per tenant.
* Overhead under 15 percent on a 10k-row bulk update; `app.audit_mode = 'summary'` writes one event per batch for imports.
* Agent writes without `app.reason` are rejected; human writes may omit it.

**Interface contract**

Provides:

* Session variables read: `app.actor_id`, `app.actor_kind`, `app.request_id`, `app.reason`, `app.audit_mode` (set by PAP-32 `createDb`, supplied by PAP-35 middleware and PAP-43 workers).
* Table `paperos.audit_redactions (table_name, column_name)` populated from `pii.json` (PAP-41).
* oRPC `audit.list({ actor?, action?, entityType?, entityId?, from?, to?, cursor? })` and `audit.forEntity(entityType, entityId)`; `AuditEventDto`.
* Component `AuditTrail` with props `{ entityType, entityId }`.
* SQL helper `paperos.audit_summary_begin()` for bulk imports (PAP-199).
* Jobs `audit.partitions`, `audit.archive` (PAP-43).

Consumes: `audit_event` table (PAP-33), generator hook (PAP-34), context vars (PAP-35), jobs (PAP-43), bucket (PAP-37).

**Definition of done**

* Every API write on a seeded tenant produces an event with correct actor, diff and request id (integration test).
* UPDATE and DELETE as `paperos_app` fail; hash-chain verification passes and detects a tampered row.
* Agent mutation without reason rejected; human allowed.
* `<AuditTrail/>` on the settings example page at 375, 768, 1024, 1280, 1920, light and dark.
* Bench committed; partition test; `docs/data/audit.md`; CHANGELOG; Linear comment.

**Test plan**

* SQL: trigger tests for insert, update, delete, restore; redaction of a listed column; `truncated` flag on a 100 KB jsonb.
* Unit: canonical JSON and hash chain; `audit:verify` on a fixture with one tampered row.
* Integration: `callAs(agent)` update without reason raises `VALIDATION`; cascading delete shares one `request_id`.
* Bench: 10k-row bulk update with and without trigger, committed with numbers.
* Visual: `AuditTrail` grouped by request at five widths.

**Demo**

Reviewer edits a workspace name on the settings page, opens the Audit tab and sees the event with actor, before and after, reason and request id, then runs `pnpm audit:verify --tenant <slug>` for a green chain. Under 90 seconds.

**Edge cases**

* Large jsonb: before and after capped at 64 KB each with hash and `truncated`.
* Cron actor: `actor_kind = 'system'`, reason equals job name.
* Redaction list changes: history not rewritten.
* Missing current partition after restore: default partition plus alert.
* Timezone: stored UTC, rendered in the viewer's zone.

**Dependencies**

PAP-33 (hard). Soft: PAP-34, PAP-35, PAP-43, PAP-37, PAP-41. Consumed by PAP-61, PAP-64, PAP-129, PAP-179, PAP-114.

**Agent**

Built by Forge (Schema Wright) with Iris on `<AuditTrail/>`. Reviewed by Sentinel (Security Auditor).

**Size**

M: trigger, chain, two procedures, one component.
