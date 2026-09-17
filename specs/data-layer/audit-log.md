---
identifier: "PAP-38"
title: "Build append-only audit log with actor (human or agent), diff and reason fields"
project: "data-layer"
projectName: "Data Layer & Database"
phase: "P1"
type: "Build"
priority: 2
surfaces: ["Staff", "Agent"]
milestone: "Local-first sync working"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-33"]
blocks: ["PAP-174", "PAP-61"]
key: "data-layer/audit-log"
url: "https://linear.app/paperos/issue/PAP-38/build-append-only-audit-log-with-actor-human-or-agent-diff-and-reason"
source: "plan/specs/bucket-0.json (round-1 canonical spec JSON)"
---

# PAP-38: Build append-only audit log with actor (human or agent), diff and reason fields

**Goal**

Record every mutation in the platform as an immutable `audit_event` with who (human or agent), what changed (before/after/diff), why (a reason string agents must supply), and the request/session that caused it, so Justin can answer "who changed this and why" for any row and reviewers can trace agent behaviour to data.

**Scope**

In:
- Append-only guarantees: table owned by `paperos_owner`; `paperos_app` has INSERT and SELECT only; triggers reject UPDATE/DELETE; monthly partitions with 24-month retention and archival to MinIO as Parquet (`data-layer/file-storage` bucket).
- Capture mechanism: Postgres trigger-based capture on every tenant table (generic `paperos.audit_trigger()` reading `app.actor_id`, `app.actor_kind`, `app.request_id`, `app.reason` session vars) so writes from any path (API, sync replay, imports) are logged; API middleware sets the vars (`data-layer/api-layer`).
- Diff computation in the trigger via `jsonb` comparison producing `{ field: { from, to } }`, excluding `updated_at`, and redacting columns listed in a `paperos.audit_redactions` table (e.g. `password_hash`, tokens).
- `audit.list` and `audit.forEntity` oRPC procedures with cursor pagination and filters (actor, action, entity type, date range); RLS applies.
- `<AuditTrail entityType entityId/>` component in `packages/ui` rendering a timeline with actor avatar, agent badge, reason and expandable diff.
- Reason enforcement: mutations from agents (`actor_kind = 'agent'`) require non-empty `app.reason`; humans optional; API exposes `reason` as an optional field on all `update/archive` procedures, and the orchestrator passes the Linear issue key by default.
- Export: `audit.export` to CSV for a date range.

Out: analytics dashboards (`data-layer/observability`), prompt/response logging (`collab/prompt-log-store`, which links to audit via `request_id`), legal hold.

**Spec**

- Trigger attached automatically by the RLS generator (`data-layer/rls-tenancy`) to every table with `tenant_id`; opt-out list for high-churn tables (e.g. presence) in `packages/db/src/audit/exclusions.ts`.
- Event `action` values: `insert|update|delete|restore|bypass_read` (bypass reads logged by API when `app.bypass` is on).
- Partition management: `pg_partman` if available in the image, else a monthly cron function creating partitions 3 months ahead; tests verify next-month partition exists.
- Archival job: monthly, copies partitions older than 24 months to `audit/<yyyy>/<mm>.parquet` via `duckdb` in a worker, then detaches and drops after checksum verify.
- Hash chain: each event stores `prev_hash` and `hash = sha256(prev_hash || canonical json)` per tenant to detect tampering; verification script `pnpm audit:verify`.
- Performance: trigger adds under 15 percent overhead on a 10k-row bulk update (bench); bulk imports may set `app.audit_mode = 'summary'` to write one event per batch.

**Definition of done**

- Every write through the API to a seeded tenant produces an event with correct actor, diff and request id (integration test).
- UPDATE/DELETE on `audit_event` as `paperos_app` fails (test); hash chain verification passes and detects a tampered row in a test.
- Agent mutation without reason rejected (test); human allowed.
- `<AuditTrail/>` on the settings example page; screenshots at 375, 768, 1024, 1280, 1920 with light/dark.
- Bench results committed; partition creation test.
- `docs/data/audit.md`; CHANGELOG; Linear comment with preview URL.

**Edge cases**

- Large `jsonb` columns (documents) produce huge diffs: cap stored `before/after` at 64 KB each and store a `truncated` flag plus hash.
- Cascading deletes generate many events in one transaction: all share `request_id`; UI groups them.
- Actor context missing (cron job): `actor_kind = 'system'`, `actor_id` null, `reason` = job name; never silent.
- Timezone display: stored UTC, rendered in viewer's timezone with absolute tooltip.
- Redaction list changes later: historical events not rewritten; documented.
- Partition for current month missing after restore: trigger falls back to default partition and alerts.

**Dependencies**

`data-layer/core-entities` (table), `data-layer/rls-tenancy` (trigger attachment), `data-layer/api-layer` (context vars). Consumed by `identity/impersonation`, `identity/agent-principals`, `collab/prompt-log-store`, `business-core/ledger`, `agents/prompt-logging-hook`.

**Agent**

Built by Forge (Schema Wright) with Iris (Component Crafter) for `<AuditTrail/>`. Reviewed by Sentinel (Security Auditor primary, Code Reviewer secondary).

**Size**

M: triggers and partitions are known patterns; the hash chain and reason enforcement are small but must be correct.
