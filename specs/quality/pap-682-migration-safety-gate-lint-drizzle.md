---
identifier: "PAP-682"
title: "Migration safety gate: lint Drizzle migrations for destructive DDL, missing down path, long locks and RLS gaps; require the `migration-ack` checkbox for irreversible changes"
project: "quality"
projectName: "Quality Pipeline"
phase: "P1"
type: "Infra"
priority: 2
surfaces: ["Developer"]
milestone: "Gates 1 and 2 on every PR"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-32", "PAP-78"]
blocks: ["PAP-254"]
key: "r4/quality/migration-safety-gate"
url: "https://linear.app/paperos/issue/PAP-682/migration-safety-gate-lint-drizzle-migrations-for-destructive-ddl"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:20:26.745Z"
model: "claude-opus-5"
effort: "medium"
estimate: 2
dueDate: "2026-09-25"
cycle: null
---

# PAP-682: Migration safety gate: lint Drizzle migrations for destructive DDL, missing down path, long locks and RLS gaps; require the `migration-ack` checkbox for irreversible changes

**Model / Effort:** Opus 5 (`claude-opus-5`) / medium — Infra S

**Goal**

Twenty agents writing Drizzle migrations against a live Postgres with RLS is the fastest path to data loss. PAP-254 certification asks for a `migrations reversible` flag from PAP-32 and the digest for an acknowledgement checkbox, but no gate inspects the SQL. This job parses every new migration, flags destructive or locking statements and tables created without RLS, and turns irreversible changes into an explicit acknowledgement.

**Scope**

* In: `ops/ci/migrations/lint-migrations.ts` over `packages/db/migrations/**` new in the PR, rule set `ops/ci/migrations/rules.yaml`, Gate 1 job `migrations` with `reports/migrations.json` (`GateReport<'migrations'>`), the `migration-ack` PR checkbox and label, `pnpm db:lint-migrations`, `docs/quality/migrations.md`; feeds PAP-254 `certify.ts` `migrationsReversible`.
* Out: running migrations (PAP-32), the expand-contract kit (PAP-443), backups (PAP-30).

**Spec**

* Rules with severities: `DROP TABLE|COLUMN|SCHEMA`, `TRUNCATE`, `ALTER COLUMN ... TYPE` on a populated table, `DELETE` or `UPDATE` without `WHERE` are S0 `destructive`; `ADD COLUMN NOT NULL` without default, `CREATE INDEX` without `CONCURRENTLY`, `ALTER TABLE ... SET NOT NULL` on large tables are S1 `locking`; `CREATE TABLE` without `ENABLE ROW LEVEL SECURITY` and a `tenant_id` policy is S0 `rls-gap` (PAP-34 helpers expected); migration without a matching `down` or an `-- irreversible: <reason>` header is S1.
* Parser: `pgsql-ast-parser` over each SQL file with a fallback regex pass; Drizzle's `meta/_journal.json` is checked for ordering conflicts between two PRs (duplicate index).
* Irreversible path: an S0 `destructive` rule can be accepted only when the PR body checkbox `[x] migration-ack: <reason>` is present and the PR carries label `migration-ack` added by Atlas; the acknowledgement is copied into `certification.json` and the digest's risks section (PAP-89, PAP-254).
* Output `reports/migrations.json` with `data.migrations: [{ file, reversible, findings }]`; status `gate/1-migrations`.
* The `expand-contract` pattern from PAP-443 is the suggested fix text in every destructive finding.

**Interface contract**

* Provides: `reports/migrations.json`, status `gate/1-migrations`, label and checkbox contract `migration-ack`, `migrationsReversible` input for PAP-254, rules file schema.
* Consumes: PAP-78 job slot and comment, PAP-32 migrations layout and journal, PAP-34 RLS helpers, PAP-239 schema, PAP-443 patterns (soft).

**Definition of done**

* Seeded migrations (drop column, index without CONCURRENTLY, table without RLS, missing down) each produce the mapped finding (links); a clean expand-contract migration passes.
* `migration-ack` flow: the drop-column PR passes only with the checkbox and label; `certification.json` carries the reason (test).
* Journal conflict between two sandbox PRs detected (test).
* Docs; changelog under "Quality"; Linear comment with the seeded results.

**Test plan**

* Unit: rule matcher on 40 SQL fixtures, journal conflict detection, checkbox parser.
* E2E: sandbox seeded PRs; certification input read by a PAP-254 unit test.

**Demo**

Open the seeded drop-column PR: red `gate/1-migrations` with the S0 and the expand-contract suggestion; tick `migration-ack`, add the label and watch it pass with the reason echoed. Under one minute.

**Edge cases**

* Generated migration from `drizzle-kit` that reorders columns: only the SQL is judged, not the generator.
* Dev-only migration for `paperos_dev_*` databases (PAP-42): path-excluded.
* Very large SQL file: parser timeout 30 s falls back to regex rules and says so.
* Rule false positive on a `DROP` inside a `DO $$` block creating a temp table: `-- lint: allow <rule> <reason>` inline suppression with expiry, same grammar as PAP-80.

**Dependencies**

Hard: PAP-78, PAP-32. Soft: PAP-34, PAP-239, PAP-443, PAP-254.

**Agent**

Builder: Sentinel (Security Auditor) with Forge (Schema Wright). Reviewer: Sentinel (Code Reviewer).

**Size**

S: half a session.
