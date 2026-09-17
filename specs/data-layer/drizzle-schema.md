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
blocks: ["PAP-129", "PAP-240", "PAP-33", "PAP-41", "PAP-43"]
key: "data-layer/drizzle-schema"
url: "https://linear.app/paperos/issue/PAP-32/set-up-drizzle-orm-schema-as-code-with-migration-workflow-and-seed"
source: "plan/specs/bucket-0.json (round-1 canonical spec JSON)"
---

# PAP-32: Set up Drizzle ORM schema-as-code with migration workflow and seed scripts

**Goal**

Make the database schema TypeScript: Drizzle ORM defines every table, `drizzle-kit` generates SQL migrations that run in CI and on deploy, and seed scripts give developers and tests a realistic multi-tenant dataset in seconds.

**Scope**

In:
- `packages/db/` with `drizzle-orm` 0.44.x, `drizzle-kit` 0.31.x, `postgres` (postgres.js) driver, `drizzle.config.ts`, `src/schema/index.ts` barrel, `src/client.ts` (pooled client factory taking a role and tenant context), `src/migrate.ts`.
- Migration workflow: `pnpm db:generate` (diff to `drizzle/*.sql` with `--name`), `pnpm db:migrate` (applies with `paperos_owner`), `pnpm db:check` fails CI if schema and migrations diverge, `pnpm db:studio`.
- Seeds: `src/seed/` using `drizzle-seed` with deterministic seeds; profiles `minimal` (1 tenant, 3 users), `demo` (3 tenants, 40 users, realistic names), `load` (50 tenants, 100k rows for `data-layer/observability`).
- CI job: spin Postgres via `ops/compose/dev.yml`, migrate from zero, seed `minimal`, run tests; also test migrate-from-previous-release to catch destructive changes.
- Deploy hook: Coolify pre-deploy command runs `pnpm db:migrate` against staging then prod, with `--dry-run` output stored as an artifact.
- Conventions doc: naming (`snake_case`, plural tables), `id uuid default gen_random_uuid()` or UUIDv7 via `uuid_generate_v7()` function shipped in migration 0000, `tenant_id` first FK on every tenant-scoped table, `created_at/updated_at/deleted_at` timestamptz, soft delete default.

Out: the actual entity tables (`data-layer/core-entities`), RLS (`data-layer/rls-tenancy`), API.

**Spec**

- `drizzle.config.ts`: `dialect:'postgresql'`, `schema:'./src/schema/*.ts'`, `out:'./drizzle'`, `casing:'snake_case'`, `migrations:{ table:'_migrations', schema:'public' }`, `strict:true`, `verbose:true`.
- Client factory `createDb({ role:'app'|'owner'|'readonly', tenantId?, actorId? })` returns a Drizzle instance whose every transaction runs `SET LOCAL app.tenant_id = $1; SET LOCAL app.actor_id = $2;` first (consumed by RLS later). Expose `withTenant(db, ctx, fn)`.
- Helper columns in `src/schema/_shared.ts`: `id()`, `tenantId()`, `timestamps()`, `softDelete()`, `jsonb<T>()`.
- Migration 0000 creates extensions, `uuid_generate_v7()`, `set_updated_at()` trigger function.
- Custom migration escape hatch: `drizzle/custom/*.sql` appended via `drizzle-kit generate --custom` for triggers and policies.
- Destructive-change guard: script parses generated SQL for `DROP TABLE|DROP COLUMN` and requires `ALLOW_DESTRUCTIVE=1`.
- Seeds are idempotent (upsert by deterministic UUID derived from `uuidv5(namespace, key)`).

**Definition of done**

- From an empty database `pnpm db:migrate && pnpm db:seed --profile demo` completes under 30 s locally; CI job green.
- `pnpm db:check` fails when a schema edit lacks a migration (proven in a test commit).
- Vitest: client factory sets session vars; seed idempotency; destructive guard.
- Drizzle Studio screenshot at 1280 and 1920 showing seeded tables; terminal output screenshot of migration run.
- `packages/db/README.md` with workflow and conventions; ADR `0005-drizzle-conventions.md`; CHANGELOG; Linear comment with CI run link.
- Staging migrated via Coolify hook and logs attached.

**Edge cases**

- Two parallel agent branches both generate migration `0007`: CI rejects duplicate indices; doc the rebase-and-regenerate procedure (`forge/branch-policy`).
- Migration partially applied after crash: each file runs in a transaction; verify with a fault-injection test.
- Long-running migration locking a hot table: require `lock_timeout = '5s'` and `statement_timeout` in migrator session; document `CONCURRENTLY` index pattern.
- PgBouncer transaction mode and `SET LOCAL`: works because it is transaction-scoped; `SET` (session) is banned by lint rule.
- Seeds running against prod: refuse if `NODE_ENV=production` unless `--i-know`.
- Timezone-less `timestamp` columns: Biome/custom lint forbids; only `timestamptz`.

**Dependencies**

`data-layer/local-dev-stack` (hard: provides `ops/compose/dev.yml`, the per-worktree database and CI service containers). `data-layer/postgres-provision` is soft (staging and production targets, wired by `app-shell/app-deploy-pipeline`). Unblocks `data-layer/core-entities`, `data-layer/data-dictionary`, `identity/better-auth` (Better Auth Drizzle adapter), `pm-linear/pm-data-model`, `business-core/finance-data-model`.

**Agent**

Built by Forge (Schema Wright sub-agent). Reviewed by Sentinel (Code Reviewer; Security Auditor for role separation).

**Size**

M: well-trodden tooling, but the tenant-context client and the CI guards define how every later table is written.
