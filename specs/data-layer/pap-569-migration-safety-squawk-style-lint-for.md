---
identifier: "PAP-569"
title: "Migration safety: squawk-style lint for generated SQL, expand-contract checklist, `db:migrate --dry-run` against a staging snapshot, `db:rollback` to the previous release and long backfills as jobs"
project: "data-layer"
projectName: "Data Layer & Database"
phase: "P1"
type: "Build"
priority: 2
surfaces: ["Developer"]
milestone: "Local-first sync working"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-32"]
blocks: []
key: "r4/data-layer/migration-safety"
url: "https://linear.app/paperos/issue/PAP-569/migration-safety-squawk-style-lint-for-generated-sql-expand-contract"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:20:46.454Z"
model: "claude-sonnet-5"
effort: "high"
estimate: 3
dueDate: "2026-09-25"
cycle: null
---

# PAP-569: Migration safety: squawk-style lint for generated SQL, expand-contract checklist, `db:migrate --dry-run` against a staging snapshot, `db:rollback` to the previous release and long backfills as jobs

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / high — Build M

**Goal**

PAP-32 guards `DROP` and sets lock timeouts, but nothing stops an agent from shipping `ALTER TABLE ... ADD COLUMN NOT NULL` without a default on a hot table, an index without `CONCURRENTLY`, or a type change that rewrites a million rows during a deploy. With twenty sessions generating migrations, safety has to be mechanical: lint the SQL, rehearse on a snapshot, keep a way back, and move slow data changes out of the deploy path.

**Scope**

In: `packages/db/src/safety/{lint,rules,report}.ts` with `pnpm db:lint` in Gate 1, rule set adapted from squawk (unsafe NOT NULL, missing CONCURRENTLY, type rewrite, rename without view, FK without index, `VALIDATE CONSTRAINT` separation), `pnpm db:migrate --dry-run --snapshot` restoring the latest staging base backup into a scratch database (PAP-30) and timing each statement, `pnpm db:rollback --to <tag>` applying reverse migrations for the last release train, `defineBackfill()` producing a pg-boss job with batches and progress, `docs/data/migrations.md`.

Out: Module-swap expand-contract adapters (PAP-443 uses this lint), Drizzle conventions (PAP-32), schema editor migrations for custom datasets (PAP-332).

**Spec**

* Lint runs on `drizzle/*.sql` and `drizzle/custom/*.sql` in the PR diff; each finding has an id `MIG-nn`, severity and a rewrite suggestion; `-- db-lint: allow MIG-04 reason=...` suppressions expire after 30 days.
* Expand-contract checklist generated for renames and type changes: add, dual-write (trigger or app), backfill job, verify, contract in a later release; the checklist is a PR comment and a `docs/data/migrations/<id>.md` stub.
* Dry run: restore snapshot (or `load` seed when no snapshot), run pending migrations under `statement_timeout 30s`, report per-statement duration, lock waits and table rewrites; fails on any rewrite of a table over 1M rows.
* Rollback: every migration folder may include `down.sql`; `db:rollback --to v0.1.0-rc.1` applies downs in reverse for migrations after the tag, refuses when a down is missing (destructive step) and prints the manual path; PITR (PAP-30) remains the last resort.
* `defineBackfill({ name, table, batch: 5000, select, update })` yields a resumable job with progress in `jobs.idempotency` and a `verify` query; the migration itself only adds the column.
* Coolify pre-deploy hook (PAP-26) runs lint and, on release tags, the dry run against the latest snapshot before `db:migrate`.

**Interface contract**

Provides: `pnpm db:lint`, rule ids `MIG-*`, `db:migrate --dry-run --snapshot`, `db:rollback --to`, `defineBackfill`, checklist generator, docs.

Consumes: Drizzle workflow and guard (PAP-32), base backups (PAP-30), jobs (PAP-43, soft: inline runner), deploy hook (PAP-26, soft), Gate 1 (PAP-78). Consumed by PAP-443, PAP-430 template upgrades, every schema PR.

**Definition of done**

* Lint catches the five seeded unsafe fixtures and passes the safe rewrites; suppression expiry enforced (test).
* Dry run against a staging snapshot produces the timing report on a test PR (screenshot); a synthetic 1M-row rewrite fails it.
* Rollback from head to the previous tag and forward again leaves `db:check` clean (CI upgrade-path job extended).
* `defineBackfill` fixture processes 100k rows in batches with resume after a kill; docs; CHANGELOG; Linear comment.

**Test plan**

* Unit: each rule on positive and negative SQL fixtures, suppression parser and expiry, checklist renderer, backfill batch cursor.
* E2E: CI compose: snapshot restore into a scratch database, dry run of pending migrations, report JSON validated; rollback and re-migrate sequence.

**Demo**

Reviewer adds `ALTER TABLE membership ADD COLUMN tier text NOT NULL;` to a scratch migration, runs `pnpm db:lint` and reads `MIG-01` with the suggested default, then runs the dry run and reads the timing table. Under two minutes.

**Edge cases**

* Migration touches a partitioned table: dry run reports per-partition timings; lint requires `CONCURRENTLY` per partition.
* Down migration loses data by design: refused; the manual runbook path is printed.
* No staging snapshot yet (before PAP-30 lands): dry run uses the `load` seed and says so.
* Two branches generate the same migration number: PAP-32's CI check stays the owner.

**Dependencies**

Blocked by PAP-32 (hard). Soft: PAP-30, PAP-43, PAP-26, PAP-78. Consumed by PAP-443, PAP-430.

**Agent**

Builder: Forge (Schema Wright). Reviewer: Sentinel (Code Reviewer; Edge Case Hunter for the lint fixtures).

**Size**

M: one session.
