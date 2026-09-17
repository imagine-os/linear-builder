---
identifier: "PAP-32"
title: "Set up Drizzle ORM schema-as-code with migration workflow and seed scripts"
project: "data-layer"
projectName: "Data Layer & Database"
phase: "P0"
type: "Build"
priority: 1
surfaces: ["Developer"]
milestone: "Postgres + Drizzle baseline"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-42"]
blocks: ["PAP-33", "PAP-41", "PAP-43", "PAP-129", "PAP-240", "PAP-334", "PAP-353", "PAP-443"]
key: "data-layer/drizzle-schema"
url: "https://linear.app/paperos/issue/PAP-32/set-up-drizzle-orm-schema-as-code-with-migration-workflow-and-seed"
source: "Linear snapshot 2026-09-17T15:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T13:40:57.451Z"
model: "claude-opus-5"
effort: "medium"
---

# PAP-32: Set up Drizzle ORM schema-as-code with migration workflow and seed scripts

**Model / Effort:** Opus 5 (`claude-opus-5`) / medium — Build M, P0 in data-layer

**Goal**

Make the schema TypeScript: Drizzle defines every table, `drizzle-kit` generates SQL migrations that run in CI and on deploy, and deterministic seeds give developers and tests a realistic multi-tenant dataset in seconds. Starts on the PAP-42 local stack, not the VPS.

**Scope**

In:

* `packages/db` with `drizzle-orm` 0.44.x, `drizzle-kit` 0.31.x, postgres.js, `drizzle.config.ts`, schema barrel, `createDb()`, `migrate.ts`.
* Scripts `db:generate`, `db:migrate`, `db:check` (CI fails on drift), `db:studio`, `db:seed --profile minimal|demo|load`.
* CI: Postgres from `ops/compose/dev.yml`, migrate from zero, seed `minimal`, run tests; migrate-from-previous-release job.
* Coolify pre-deploy hook running `db:migrate` (PAP-26).
* Per-module migration folders `drizzle/<module>/` prepared for PAP-28.

Out: entity definitions (PAP-33), RLS (PAP-34), Postgres hosting (PAP-30).

**Spec**

* Config: `dialect postgresql`, `schema ./src/schema/*.ts`, `out ./drizzle`, `casing snake_case`, migrations table `_migrations`, `strict`, `verbose`.
* `createDb({ role: 'app'|'owner'|'readonly', tenantId?, actorId?, actorKind?, requestId?, reason? })` runs `SET LOCAL app.*` at the start of every transaction; `withTenant(db, ctx, fn)`.
* Helpers `id()` (uuidv7), `tenantId()`, `timestamps()`, `softDelete()`, `jsonb<T>()`, `money()` (bigint minor units).
* Migration 0000: extensions, `uuid_generate_v7()`, `set_updated_at()`.
* Custom SQL via `drizzle/custom/*.sql` for triggers and policies.
* Destructive guard: generated SQL with `DROP TABLE|DROP COLUMN` needs `ALLOW_DESTRUCTIVE=1`.
* Seeds idempotent via `uuidv5(namespace, key)`; refuse in production without `--i-know`.
* Migrator session sets `lock_timeout 5s` and `statement_timeout`.

**Interface contract**

Provides (from `@paperos/db`):

* `createDb`, `withTenant`, `type Db`, `type TenantContext = { tenantId: string; actorId?: string; actorKind: 'human'|'agent'|'service'|'system'; requestId?: string; reason?: string }` (the session-variable contract PAP-34 policies and PAP-38 triggers read).
* Column helpers above; `schema/index.ts` barrel other projects extend by adding files under `schema/<domain>/`.
* Scripts `pnpm db:*`; env `DATABASE_URL`, `DATABASE_URL_MIGRATOR` (PAP-17 names).
* Seed profiles and the `seed(profile)` function used by PAP-86 test-mode endpoints.
* Lint rule package `@paperos/config-biome/db` banning session `SET` and `timestamp` without tz.

Consumes: `ops/compose/dev.yml` and the per-worktree database (PAP-42).

**Definition of done**

* Empty database to `db:migrate && db:seed --profile demo` under 30 s locally; CI green.
* `db:check` fails on an unmigrated schema edit (proven in a test commit).
* Vitest: session vars set, seed idempotency, destructive guard, migration transactionality.
* Drizzle Studio screenshots at 1280 and 1920; terminal screenshot of a migration.
* `packages/db/README.md`, ADR `0005-drizzle-conventions.md`, CHANGELOG, Linear comment; staging migrated through the Coolify hook (log).

**Test plan**

* Unit: `createDb` issues `SET LOCAL` for every context key; `withTenant` restores context after nested transactions; guard regex on 20 SQL fixtures.
* Integration (CI compose): migrate from zero, seed each profile twice, assert identical row counts; fault injection kills the migrator mid-file and asserts rollback.
* Upgrade path: checkout previous tag, migrate, checkout head, migrate, `db:check` clean.
* Lint: rule fixtures for `SET` and `timestamp`.
* Performance: `load` seed under 3 minutes on CI.

**Demo**

Reviewer runs `pnpm stack up && pnpm db:migrate && pnpm db:seed --profile demo && pnpm db:studio`, opens Studio and browses three seeded tenants; then edits a column and runs `pnpm db:check` to watch it fail. Under 2 minutes.

**Edge cases**

* Two branches generate `0007`: CI rejects duplicates; rebase-and-regenerate documented (PAP-46).
* Long migration on a hot table: `CONCURRENTLY` index pattern documented.
* PgBouncer transaction mode is safe because `SET LOCAL` is transaction-scoped.
* Seeds against production refused.
* Module-scoped migrations of a disabled module treated as ignorable (PAP-28).

**Dependencies**

PAP-42 (hard). Soft: PAP-30 (staging target via PAP-26). Unblocks PAP-33, PAP-41, PAP-43, PAP-57, PAP-100, PAP-129, PAP-175.

**Agent**

Built by Forge (Schema Wright). Reviewed by Sentinel (Code Reviewer).

**Size**

M: one package with strong conventions.
