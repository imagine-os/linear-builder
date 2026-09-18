---
identifier: "PAP-561"
title: "Export-first tenant hard-purge job `tenant.purge`: FK-order deletion generator, sessions, keys, Yjs and MinIO cleanup, `tenant_tombstone` and `pnpm tenant:verify-purged`"
project: "data-layer"
projectName: "Data Layer & Database"
phase: "P1"
type: "Build"
priority: 2
surfaces: ["Developer"]
milestone: "Tenant-safe and observable"
state: "Backlog"
parent: "PAP-355"
children: []
blockedBy: ["PAP-33", "PAP-38", "PAP-43", "PAP-565"]
blocks: ["PAP-221", "PAP-859", "PAP-896", "PAP-897", "PAP-898", "PAP-902"]
key: "r4/data-layer/tenant-purge"
url: "https://linear.app/paperos/issue/PAP-561/export-first-tenant-hard-purge-job-tenantpurge-fk-order-deletion"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:20:47.289Z"
model: "claude-opus-5"
effort: "high"
estimate: 3
dueDate: "2026-09-30"
cycle: null
---

# PAP-561: Export-first tenant hard-purge job `tenant.purge`: FK-order deletion generator, sessions, keys, Yjs and MinIO cleanup, `tenant_tombstone` and `pnpm tenant:verify-purged`

**Model / Effort:** Opus 5 (`claude-opus-5`) / high — Build M

**Goal**

Third child of PAP-355 and the destructive one: after PAP-432's grace period, remove every trace of a tenant (rows, files, documents, keys, sessions) in a resumable, audited job that refuses to run without a completed export and leaves only a tombstone. This is the backstop GDPR relies on, so it is generated from the schema, verified by a script, and reviewed as security-sensitive.

**Scope**

In: Job `tenant.purge` and `tenant.export_before_purge`, `packages/db/src/purge/{order,run,verify}.ts` (FK-order generator from `information_schema`), `tenant_tombstone (tenant_id, purged_at, export_sha256, row_counts jsonb)`, `pnpm tenant:verify-purged <id>`, `pnpm tenant:purge --dry-run`, Needs Justin gate for tenants with paid history in the last 90 days, `docs/data/tenant-purge.md`.

Out: Grace period, states and cancel flow (PAP-432), export format (PAP-205, PAP-420), per-user erasure (PAP-221), backup expiry (documented, PAP-30 and PAP-354).

**Spec**

* Preconditions: tenant state `deleted` with `deleted_at + grace <= now()`, `legal_hold = false`, a completed export whose `sha256` is recorded, and either no paid history in 90 days or an approved PAP-94 decision card; otherwise the job exits `refused` with the reason.
* Sequence: revoke sessions and keys (PAP-223, PAP-60), delete Yjs rooms for the tenant (PAP-140 admin route), delete the MinIO prefix (PAP-37), delete rows table by table in FK order using `paperos_owner` inside an audited `app.bypass` transaction per table (PAP-34, PAP-38 `bypass_read`), retire data keys (PAP-353), write the tombstone last.
* FK-order generator walks `information_schema.referential_constraints` at run time and fails the dry run when a tenant-scoped table lacks a `tenant_id` mapping (PAP-432 usage page shows it as unknown).
* Resumable: checkpoint per table in `tenant_purge_run`; a crash resumes at the next table; the tenant is already inaccessible so partial state is invisible.
* `tenant:verify-purged` counts rows in every tenant table, objects under the prefix, Yjs rooms and data keys; prints zeros or names the leftovers; exit code non-zero on leftovers.
* Events `tenant.purged` (consumed by PAP-432 for the state transition) and one `audit_event` per table with counts; PAP-88 digest line.

**Interface contract**

Provides: Jobs `tenant.purge`, `tenant.export_before_purge`, table `tenant_tombstone`, table `tenant_purge_run`, scripts `tenant:verify-purged`, `tenant:purge --dry-run`, event `tenant.purged`, FK-order generator `purgeOrder()` (reused by PAP-221 and PAP-422).

Consumes: Jobs (PAP-43), core entities (PAP-33), export job (PAP-205 or PAP-420, soft: refuses without one), files (PAP-37), Yjs admin route (PAP-140), keys (PAP-353), sessions and agent keys (PAP-223, PAP-60), RLS bypass and audit (PAP-34, PAP-38), decision cards (PAP-94). Consumed by PAP-432, PAP-221, PAP-422.

**Definition of done**

* Purge of a seeded tenant with tables, files, docs and encrypted secrets leaves zero rows, zero objects and a tombstone whose `export_sha256` matches the day-0 export (compressed schedule in tests); `tenant:verify-purged` prints zeros.
* Crash injected after table 3: rerun resumes and completes; exactly-once counts in the tombstone.
* Refusal paths tested: legal hold, missing export, paid history without approval, table without tenant mapping (dry run).
* `docs/data/tenant-purge.md` including the backup caveat; CHANGELOG under Security; Linear comment with the verification output.

**Test plan**

* Unit: FK-order generator on a fixture schema with cycles (deferrable constraints) and partitions, precondition matrix, checkpoint resume, verify script parsing.
* E2E: staging tenant deleted with a 1-minute grace override: export link works, purge completes, verify prints zeros, tombstone row present, Grafana shows the `bypass_read` audit events.

**Demo**

Reviewer runs `pnpm tenant:purge --dry-run <id>` and reads the ordered table list, then lets the job run on the seeded tenant and finishes with `pnpm tenant:verify-purged <id>`. Two minutes.

**Edge cases**

* Shared global rows (`user` in two tenants): memberships deleted, user retained; PAP-221 handles the person.
* Backups still contain the data: documented; restores of a purged tenant re-run the tombstone check and purge again (PAP-354 drill step).
* Ledger periods locked (PAP-179): the tenant's ledger is deleted with the tenant; per-user erasure keeps pseudonyms.
* Table added later without the mapping: dry run fails weekly in the PAP-306 re-audit until fixed.

**Dependencies**

Blocked by PAP-43 and PAP-33 (hard). Soft: PAP-205/PAP-420 (refuses without an export), PAP-37, PAP-140, PAP-353, PAP-34, PAP-38, PAP-94, PAP-432 (schedules it). Blocks PAP-221.

**Agent**

Builder: Forge (Schema Wright). Reviewer: Sentinel (Security Auditor; Ledger for finance tables).

**Size**

M: one session.
