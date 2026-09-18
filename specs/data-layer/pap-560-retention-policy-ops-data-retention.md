---
identifier: "PAP-560"
title: "Retention policy `ops/data/retention.yaml`, the nightly `retention.run` job with delete, anonymise and partition-drop strategies, legal hold flags and the audit summary per table"
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
blockedBy: ["PAP-38", "PAP-43", "PAP-565"]
blocks: []
key: "r4/data-layer/retention-jobs"
url: "https://linear.app/paperos/issue/PAP-560/retention-policy-opsdataretentionyaml-the-nightly-retentionrun-job"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:07.686Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 3
dueDate: "2026-09-30"
cycle: null
---

# PAP-560: Retention policy `ops/data/retention.yaml`, the nightly `retention.run` job with delete, anonymise and partition-drop strategies, legal hold flags and the audit summary per table

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Build M

**Goal**

Second child of PAP-355: enforce storage limitation. A declarative retention file names how long each table keeps rows and what happens after (delete, anonymise column by column, or drop whole partitions), a nightly job executes it in time-boxed batches, legal hold suspends it per tenant or user, and every run leaves an audit summary so the release digest (PAP-88) can report rows removed.

**Scope**

In: `ops/data/retention.yaml` with Zod schema, `packages/db/src/retention/{schema,plan,run,strategies}.ts`, job `retention.run` (PAP-43), `tenant.legal_hold` and `user.legal_hold` columns with reason, oRPC `retention.preview` (staff), `docs/data/retention.md`.

Out: PII annotations (PAP-559), tenant purge (PAP-561), backups expiry (PAP-30, PAP-354), marketing consent (PAP-405).

**Spec**

* Entry shape `{ table, column: created_at|updated_at|ended_at, keep: Duration, action: delete|anonymise|drop_partition, anonymise?: { [column]: 'null'|'hash'|'truncate_ip'|'pseudonym' }, tenantOverride?: { min, max } }`; defaults from PAP-355: `audit_event` 24 months (archive then drop), `prompt_event` 180 days, `session` 90 days after expiry, `impersonation` 24 months, `webhook_delivery` 30 days, `import_run_item` 90 days, analytics events 13 months anonymised after 90 days.
* Tenant overrides within `[min, max]` stored in `tenant.settings.retention`; defaults per PAP-126 compliance profile (7-year finance retention); tables tagged `immutable` (PAP-179, PAP-180 documents) are refused at schema validation.
* Job runs nightly at 02:00 UTC, batches of 5,000 with `SELECT ... FOR UPDATE SKIP LOCKED`, per-run time box 30 minutes, resumes next night; partitioned tables drop whole partitions when every row is past retention.
* Legal hold: `legal_hold = true` on a tenant or user skips every row in that scope and lists it in the run report; setting or clearing a hold requires a reason and is audited.
* One `audit_event` per table per run with `{ deleted, anonymised, skippedHeld, durationMs }` and `actor_kind = 'system'`; `retention.completed` event for PAP-88.
* `retention.preview` returns counts per table that the next run would touch, for the staff usage page (PAP-432).

**Interface contract**

Provides: `retention.yaml` schema, job `retention.run`, event `retention.completed`, `legal_hold` flags and oRPC `retention.preview`, `legalHold.set` with reason.

Consumes: Jobs (PAP-43), audit summary rows (PAP-38), partitions (PAP-38 helper), `pii.json` for anonymisation defaults (PAP-559, soft), compliance profile (PAP-126, soft). Consumed by PAP-88 digest, PAP-432 usage page, PAP-221 (erasure strategies reuse `strategies.ts`).

**Definition of done**

* Retention run on a seeded database deletes and anonymises exactly the expected rows (fixture with rows straddling each boundary); audit summary rows present.
* Legal hold on one tenant leaves its rows untouched and the report names it; immutable-table entry rejected at validation.
* Partition-drop path proven on `audit_event` with a synthetic 25-month-old partition; time box observed with a 1-minute override.
* `docs/data/retention.md`; CHANGELOG under Security; Linear comment with the run report.

**Test plan**

* Unit: schema validation (unknown table, immutable table, override outside bounds), boundary arithmetic with fake clock, each anonymisation strategy, batch planner and resume cursor.
* E2E: CI compose: seed, run the job twice (second run is a no-op), assert counts and the `retention.completed` event payload.

**Demo**

Reviewer opens `retention.preview` on the staff usage page, sets a legal hold on the demo tenant with a reason, runs `pnpm jobs:run retention.run --now` and reads the report showing held rows skipped. Under two minutes.

**Edge cases**

* Row referenced by an FK from a retained table: delete fails; the planner orders tables by FK depth and reports blockers instead of crashing.
* Tenant override shorter than the legal minimum: rejected with the bound named.
* Anonymised row later exported (PAP-205): export shows the pseudonym; documented.
* Clock jump or DST: schedule in UTC; boundary uses `now()` from the database.

**Dependencies**

Blocked by PAP-43 (jobs) and PAP-38 (audit, partitions). Soft: PAP-559, PAP-126, PAP-432. Consumed by PAP-88, PAP-221.

**Agent**

Builder: Forge (Schema Wright). Reviewer: Sentinel (Security Auditor; Ledger reviews finance table entries).

**Size**

M: one session.

*Round 4 critique fix (2026-09-18):* resolved 2 round-4 file keys in this description to Linear identifiers: `r4/data-layer/pii-registry` = PAP-559, `r4/data-layer/tenant-purge` = PAP-561.
