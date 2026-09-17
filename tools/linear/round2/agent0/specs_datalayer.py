SPECS = {}

SPECS["PAP-30"] = dict(
Goal="""Stand up production and staging Postgres 17 on the PAP-25 host under Coolify with continuous WAL archiving, nightly base backups, point-in-time recovery proven by a drill, PgBouncer in front, logical replication on for Electric (PAP-36), and every extension later issues need pre-installed.""",
Scope="""In:

* Coolify services exported as `ops/compose/postgres.yml` for `pg-prod` and `pg-staging` on `pgvector/pgvector:pg17`.
* `pgBackRest` sidecar shipping WAL to bucket `paperos-backups/pg` (PAP-25): nightly full, hourly incremental, 14-day retention; daily `verify`; weekly automated restore drill.
* Roles `paperos_owner`, `paperos_app` (`NOBYPASSRLS`), `paperos_readonly`, `electric` (replication), `paperos_backup`.
* Tuning for 8 GB: `shared_buffers 2GB`, `work_mem 16MB`, `max_connections 200`, `wal_level logical`, `max_replication_slots 10`, `max_wal_size 2GB`.
* PgBouncer (transaction mode) for the API; direct connections for Electric and Hocuspocus.
* `postgres_exporter` for PAP-40.

Out: schema (PAP-32), the local compose stack (PAP-42), MinIO (PAP-37).""",
Spec="""* `ops/db/init/*.sql` on first boot: roles, databases `paperos_prod` and `paperos_staging`, extensions `vector`, `pg_trgm`, `pgcrypto`, `pg_stat_statements`, `citext`, `ALTER SYSTEM` settings.
* Secrets in Coolify env from sops; names match `serverEnvSchema` (PAP-17): `DATABASE_URL` (app via PgBouncer), `DATABASE_URL_MIGRATOR` (owner, direct), `DATABASE_URL_ELECTRIC`.
* `ops/db/README.md`: connection strings per role, psql access over the tailnet, PITR procedure with exact commands, RPO 1 h, RTO 30 min.
* Weekly drill result posted to Linear via PAP-97 when available, else logged.
* Password rotation runbook updating Coolify env and reloading PgBouncer without downtime.""",
**{"Interface contract": """Provides:

* Env vars `DATABASE_URL`, `DATABASE_URL_MIGRATOR`, `DATABASE_URL_READONLY`, `DATABASE_URL_ELECTRIC` per environment, stored in `ops/secrets/<env>-db.enc.yaml`.
* Role semantics: `paperos_app` is subject to RLS (PAP-34 relies on `NOBYPASSRLS`); `paperos_owner` runs migrations (PAP-32, PAP-26); `electric` has `REPLICATION` and a publication `electric_pub` (PAP-36).
* Extensions guaranteed present: `vector` (PAP-39), `pg_trgm` (PAP-39), `pgcrypto` (field-encryption issue, PAP-38 hashes), `pg_stat_statements` (PAP-40), `citext` (PAP-33).
* Metrics endpoint `postgres_exporter:9187` on the internal network (PAP-40).
* Backup repo path `paperos-backups/pg/<env>` (object-storage DR issue restores from it).

Consumes: host, Coolify, buckets and sops (PAP-25)."""},
**{"Definition of done": """* Both instances reachable through PgBouncer with TLS from a test container; `SELECT version()` shows 17.x and all extensions.
* WAL archives in the bucket; `pgbackrest info` shows a full backup.
* Restore drill: recover staging to 10 minutes earlier and find a row inserted then deleted (transcript).
* Screenshots of the Coolify service page, `pgbackrest info` and exporter metrics at 1280 and 1920.
* `ops/db/README.md`, ADR `0003-postgres-hosting.md`, CHANGELOG, Linear comment with the drill transcript."""},
**{"Test plan": """* Unit: `bats` test that `init/*.sql` runs idempotently twice on a local `pgvector:pg17` container.
* Integration: connect as each role and assert `rolbypassrls`, `rolreplication`, `SHOW wal_level`, publication existence.
* Backup: `pgbackrest verify` in CI against a scratch stanza; scheduled drill script asserts the deleted row is present.
* Failure: stop MinIO, write 100 rows, restart, assert WAL catch-up and `archive_command` alerts (log).
* Ops: disk-usage alert fires in a test by lowering the threshold."""},
Demo="""Reviewer runs `psql "$DATABASE_URL_READONLY" -c "select version(); \\dx"` over the tailnet, then `pgbackrest --stanza=staging info` and opens the exporter metrics in Grafana or `curl`. Under 90 seconds.""",
**{"Edge cases": """* MinIO unavailable during archive: writes continue, WAL accumulates, alert at 70 percent disk.
* PgBouncer transaction mode breaks `LISTEN/NOTIFY` and session `SET`: documented; `SET LOCAL` only (PAP-32 lint).
* Coolify redeploy must keep the named volume (tested).
* Cluster in UTC; app converts.
* Replication slot left by a dead Electric instance fills the disk: `max_slot_wal_keep_size 4GB` and a monitor."""},
Dependencies="""PAP-25 (hard). Unblocks PAP-26, PAP-36 (logical replication), PAP-40 (exporter), PAP-140. Schema work starts on PAP-42, not here.""",
Agent="""Built by Forge (Ops Runner). Reviewed by Sentinel (Security Auditor).""",
Size="""M: compose, init scripts, backup sidecar and one drill.""",
)

SPECS["PAP-31"] = dict(
Goal="""Confirm or overturn ElectricSQL plus PGlite for local-first sync by benchmarking Zero, PowerSync and Replicache on PaperOS's real core entities, and record the decision as an ADR that PAP-36 implements without further debate. Time-boxed to 1.5 agent-days.""",
Scope="""In:

* Rubric (weights agreed with Atlas): Postgres-native change capture, tenant-scoped partial sync, offline writes and conflict model, RLS story, bundle size, browser and Tauri WebView support, self-host and licence (PAP-212), maturity, TypeScript ergonomics, cost of exit.
* Spike `spikes/sync-bench/` with a 10k-row `tasks` table under `tenant_id`: initial sync of a 2k-row shape, incremental latency p50 and p95, replay of 200 offline writes, memory in Chrome and WebView, cold start on a mid-range Android emulator.
* Coexistence notes with Yjs (PAP-140) and RLS (PAP-34).
* ADR `docs/adr/0004-local-first-sync.md`.

Out: production integration (PAP-36), CRDT choice (PAP-139).""",
Spec="""* Each engine gets at most 3 hours; unknowns become rubric penalties.
* Versions: ElectricSQL 1.x HTTP shapes plus PGlite 0.3; Zero current with zero-cache; PowerSync self-hosted plus web SDK; Replicache with an oRPC push/pull server; baseline TanStack Query with a hand-rolled outbox.
* Permission path scored: per-user role respecting RLS, proxy, or own rules language.
* Hard criteria: self-hosts in Docker on the VPS, acceptable licence, runs in Tauri WebView.
* Results JSON in `spikes/sync-bench/results/*.json`, rendered to a Markdown table by script; three runs, median reported.
* Migration-cost estimate from winner to runner-up in hours.""",
**{"Interface contract": """Provides:

* ADR 0004 with a `decision` block PAP-36 copies verbatim: engine, versions, persistence per target, permission path (`proxy` expected), known limits.
* `spikes/sync-bench/results/summary.json` schema `{ engine, initialSyncMs, incrementalP50Ms, incrementalP95Ms, replay200Ms, heapMb, coldStartMs, score }` reused by PAP-147 load tests as a baseline.
* Registry entry draft for PAP-216.

Consumes: rubric format (PAP-210), licence tiers (PAP-212), RLS context contract (PAP-34, read from its spec)."""},
**{"Definition of done": """* Spike code merged under `spikes/` (excluded from `turbo build`); results and table committed.
* ADR approved by Atlas and Nova on the PR.
* Browser harness recordings at 375 and 1280.
* Registry entry drafted; PAP-36 description updated with the chosen libraries and versions; CHANGELOG; Linear comment."""},
**{"Test plan": """* Bench: Vitest bench for server-side measures; Playwright for browser heap and timing; Android emulator cold start via `adb` script; each three runs, median kept.
* Correctness: after replay of 200 offline writes, row count and checksums match the server for every engine.
* Permission: cross-tenant shape request must fail for every engine; result recorded per engine.
* Review: every score in the table cites the results file or a source URL."""},
Demo="""Reviewer opens the ADR, reads the decision block and the scores table, then runs `pnpm --filter sync-bench bench:electric` to reproduce one engine's numbers locally in about a minute.""",
**{"Edge cases": """* Engine needs superuser or disables RLS: hard fail.
* Cloud easy, self-host undocumented: score self-host only.
* BSL or ELv2 terms: recorded with a re-open trigger.
* PGlite WASM memory on Android WebView tested specifically.
* Shapes over 10k rows: note pagination strategy."""},
Dependencies="""None; ready now. Blocks PAP-36; informs PAP-143, PAP-148, PAP-214.""",
Agent="""Researched by Scout (Library Evaluator) paired with Forge. Reviewed by Atlas and Nova.""",
Size="""M: 1.5 agent-days, time-boxed.""",
)

SPECS["PAP-32"] = dict(
Goal="""Make the schema TypeScript: Drizzle defines every table, `drizzle-kit` generates SQL migrations that run in CI and on deploy, and deterministic seeds give developers and tests a realistic multi-tenant dataset in seconds. Starts on the PAP-42 local stack, not the VPS.""",
Scope="""In:

* `packages/db` with `drizzle-orm` 0.44.x, `drizzle-kit` 0.31.x, postgres.js, `drizzle.config.ts`, schema barrel, `createDb()`, `migrate.ts`.
* Scripts `db:generate`, `db:migrate`, `db:check` (CI fails on drift), `db:studio`, `db:seed --profile minimal|demo|load`.
* CI: Postgres from `ops/compose/dev.yml`, migrate from zero, seed `minimal`, run tests; migrate-from-previous-release job.
* Coolify pre-deploy hook running `db:migrate` (PAP-26).
* Per-module migration folders `drizzle/<module>/` prepared for PAP-28.

Out: entity definitions (PAP-33), RLS (PAP-34), Postgres hosting (PAP-30).""",
Spec="""* Config: `dialect postgresql`, `schema ./src/schema/*.ts`, `out ./drizzle`, `casing snake_case`, migrations table `_migrations`, `strict`, `verbose`.
* `createDb({ role: 'app'|'owner'|'readonly', tenantId?, actorId?, actorKind?, requestId?, reason? })` runs `SET LOCAL app.*` at the start of every transaction; `withTenant(db, ctx, fn)`.
* Helpers `id()` (uuidv7), `tenantId()`, `timestamps()`, `softDelete()`, `jsonb<T>()`, `money()` (bigint minor units).
* Migration 0000: extensions, `uuid_generate_v7()`, `set_updated_at()`.
* Custom SQL via `drizzle/custom/*.sql` for triggers and policies.
* Destructive guard: generated SQL with `DROP TABLE|DROP COLUMN` needs `ALLOW_DESTRUCTIVE=1`.
* Seeds idempotent via `uuidv5(namespace, key)`; refuse in production without `--i-know`.
* Migrator session sets `lock_timeout 5s` and `statement_timeout`.""",
**{"Interface contract": """Provides (from `@paperos/db`):

* `createDb`, `withTenant`, `type Db`, `type TenantContext = { tenantId: string; actorId?: string; actorKind: 'human'|'agent'|'service'|'system'; requestId?: string; reason?: string }` (the session-variable contract PAP-34 policies and PAP-38 triggers read).
* Column helpers above; `schema/index.ts` barrel other projects extend by adding files under `schema/<domain>/`.
* Scripts `pnpm db:*`; env `DATABASE_URL`, `DATABASE_URL_MIGRATOR` (PAP-17 names).
* Seed profiles and the `seed(profile)` function used by PAP-86 test-mode endpoints.
* Lint rule package `@paperos/config-biome/db` banning session `SET` and `timestamp` without tz.

Consumes: `ops/compose/dev.yml` and the per-worktree database (PAP-42)."""},
**{"Definition of done": """* Empty database to `db:migrate && db:seed --profile demo` under 30 s locally; CI green.
* `db:check` fails on an unmigrated schema edit (proven in a test commit).
* Vitest: session vars set, seed idempotency, destructive guard, migration transactionality.
* Drizzle Studio screenshots at 1280 and 1920; terminal screenshot of a migration.
* `packages/db/README.md`, ADR `0005-drizzle-conventions.md`, CHANGELOG, Linear comment; staging migrated through the Coolify hook (log)."""},
**{"Test plan": """* Unit: `createDb` issues `SET LOCAL` for every context key; `withTenant` restores context after nested transactions; guard regex on 20 SQL fixtures.
* Integration (CI compose): migrate from zero, seed each profile twice, assert identical row counts; fault injection kills the migrator mid-file and asserts rollback.
* Upgrade path: checkout previous tag, migrate, checkout head, migrate, `db:check` clean.
* Lint: rule fixtures for `SET` and `timestamp`.
* Performance: `load` seed under 3 minutes on CI."""},
Demo="""Reviewer runs `pnpm stack up && pnpm db:migrate && pnpm db:seed --profile demo && pnpm db:studio`, opens Studio and browses three seeded tenants; then edits a column and runs `pnpm db:check` to watch it fail. Under 2 minutes.""",
**{"Edge cases": """* Two branches generate `0007`: CI rejects duplicates; rebase-and-regenerate documented (PAP-46).
* Long migration on a hot table: `CONCURRENTLY` index pattern documented.
* PgBouncer transaction mode is safe because `SET LOCAL` is transaction-scoped.
* Seeds against production refused.
* Module-scoped migrations of a disabled module treated as ignorable (PAP-28)."""},
Dependencies="""PAP-42 (hard). Soft: PAP-30 (staging target via PAP-26). Unblocks PAP-33, PAP-41, PAP-43, PAP-57, PAP-100, PAP-129, PAP-175.""",
Agent="""Built by Forge (Schema Wright). Reviewed by Sentinel (Code Reviewer).""",
Size="""M: one package with strong conventions.""",
)

SPECS["PAP-33"] = dict(
Goal="""Model the seven shared entities every app and project extends: `tenant`, `workspace`, `user`, `membership`, `role`, `audit_event`, `file`. Output is Drizzle schema, Zod types, an ER diagram and a written contract; the canonical `Principal` type is declared by PAP-55 in `packages/core` and this issue's `user.kind` maps onto it.""",
Scope="""In:

* Tables in `packages/db/src/schema/core/*.ts` with relations, indexes, constraints and comments.
* `drizzle-zod` schemas in `packages/db/src/zod/core.ts` (insert, select, update).
* ER diagram and `docs/data/core-entities.md` with invariants and ownership.
* `demo` seeds; consumer notes for identity, audiences, files, audit.
* `tenant_module` reserved for PAP-28.

Out: RLS (PAP-34), API (PAP-35), UI, PM, finance and CRM entities.""",
Spec="""* `tenant`: `id`, `slug` unique, `name`, `plan`, `settings jsonb`, `branding jsonb`, `locale`, `timezone`, timestamps, `deleted_at`.
* `workspace`: `tenant_id`, `slug` unique per tenant, `name`, `kind default|team|project`, `settings jsonb`; default workspace created by trigger.
* `user` (global): `email citext unique`, `name`, `avatar_file_id`, `locale`, `timezone`, `kind human|agent|service`, `agent_character`, `disabled_at`; `email` nullable only when `kind <> 'human'`. Better Auth owns credentials keyed to `user.id`.
* `membership`: `tenant_id`, `workspace_id` nullable, `user_id`, `role_id`, `status invited|active|suspended`, `invited_by`; unique `(tenant_id, workspace_id, user_id)`.
* `role`: `tenant_id` nullable for system roles, `key`, `name`, `permissions jsonb`, `is_system`; seeded `owner`, `admin`, `staff`, `customer`, `agent`, `viewer`.
* `audit_event`: uuidv7, `tenant_id`, actor columns, `action`, `entity_type`, `entity_id`, `before`, `after`, `diff`, `reason`, `request_id`, monthly partitions (PAP-38 fills behaviour).
* `file`: `tenant_id`, `key`, `size`, `sha256`, `mime`, `status pending|ready|failed`, `variants jsonb`, `uploaded_by`.""",
**{"Interface contract": """Provides:

* Drizzle exports `tenant`, `workspace`, `user`, `membership`, `role`, `auditEvent`, `file` and relations from `@paperos/db/schema/core`; Zod `TenantSelect`, `UserInsert` and friends from `@paperos/db/zod/core`.
* Invariants other projects rely on: every tenant row has one default workspace; `membership` rows never cross tenants; system roles are immutable through the app role.
* `user.kind` values equal `Principal['kind']` in PAP-55; `role.permissions` strings are `resource:action` in PAP-59's grammar.
* `file` columns are the contract PAP-37 completes; `audit_event` columns are the contract PAP-38 completes.

Consumes: helpers and `createDb` (PAP-32). Coordinates with PAP-55 and PAP-56 (audience tables reference `membership`)."""},
**{"Definition of done": """* Migration generated and applied on staging; `db:check` clean.
* Vitest constraints: cross-tenant membership rejected, default workspace created, system role edit rejected, agent user without email accepted, human without email rejected.
* Zod schemas snapshot-tested; ER diagram renders; contract doc reviewed by Sentinel (Security Auditor) and Quill.
* Studio screenshots at 1280 and 1920; CHANGELOG; ADR `0006-core-entities.md`; consumers notified by comment."""},
**{"Test plan": """* Unit: pgTAP-style SQL tests for each CHECK and unique constraint; trigger test for the default workspace.
* Integration: seed `demo`, assert three tenants, 40 users, memberships consistent; `drizzle-zod` parse of every seeded row.
* Static: schema barrel exports snapshot; `@owner data-layer` tag present on every file (PAP-41 reads it).
* Visual: ER diagram rendered on GitHub and Studio screenshots at 1280 and 1920."""},
Demo="""Reviewer runs `pnpm db:seed --profile demo && pnpm db:studio`, opens `membership` filtered to one tenant, tries to insert a row pointing at another tenant's workspace in Studio and receives the constraint error. Under 2 minutes.""",
**{"Edge cases": """* Email case and unicode normalised at the API; `citext` in storage.
* User with zero tenants: allowed; the onboarding wizard issue handles it.
* Tenant soft delete cascades logically; hard purge is the tenant-lifecycle issue.
* Missing future audit partition: PAP-38 creates three months ahead.
* File row without object: PAP-37 reconciliation."""},
Dependencies="""PAP-32 (hard). Coordinates with PAP-55, PAP-56, PAP-57. Unblocks PAP-34, PAP-35, PAP-37, PAP-38, PAP-39, PAP-57, PAP-100, PAP-129, PAP-175, PAP-187, PAP-205.""",
Agent="""Specified and built by Forge (Schema Wright) with Quill drafting the contract doc. Reviewed by Sentinel.""",
Size="""M: seven tables and a document.""",
)

SPECS["PAP-34"] = dict(
Goal="""Enforce tenant isolation inside Postgres with row-level security so a buggy agent-written query on the app role cannot touch another tenant's rows, and prove it continuously with a harness that auto-enrols every new table.""",
Scope="""In:

* `ENABLE` and `FORCE ROW LEVEL SECURITY` on every table with `tenant_id`; policies generated from one template.
* Session contract `app.tenant_id`, `app.actor_id`, `app.actor_kind`, `app.bypass` set via `SET LOCAL` by `createDb` (PAP-32).
* Generator `packages/db/src/rls/generate.ts` emitting `drizzle/custom/00xx_rls.sql`; global-table read policies for `user` and system `role`.
* Harness `packages/db/test/rls.harness.test.ts` introspecting `information_schema`.
* `docs/data/tenancy.md`.

Out: permission engine (PAP-59), API context (PAP-35).""",
Spec="""* `paperos_app` has `NOBYPASSRLS`; `paperos_owner` bypasses only in the migrator connection; `paperos_readonly` is subject to RLS.
* Fail closed: `current_setting('app.tenant_id', true)` coalesced to the nil UUID.
* `user` readable when sharing a tenant with the actor (EXISTS on `membership`) or being the actor; system roles readable by all.
* `app.bypass = 'on'` allowed only for the owner role through an audited API path (PAP-38 records `bypass_read`).
* Electric role reads with RLS bypassed; shapes filtered by `tenant_id` in the proxy (PAP-36).
* Generator idempotent (`DROP POLICY IF EXISTS` then `CREATE`); it also attaches PAP-38's audit trigger to every enrolled table.
* Views require `security_invoker = true`; `SECURITY DEFINER` banned outside the `paperos` schema.""",
**{"Interface contract": """Provides:

* Session variables `app.tenant_id`, `app.actor_id`, `app.actor_kind`, `app.request_id`, `app.reason`, `app.bypass` as the single database context contract (PAP-32 sets, PAP-35 supplies, PAP-38 reads, PAP-36 mirrors in the proxy).
* SQL function `paperos.current_tenant()` for use in policies and generated view SQL (PAP-163).
* Generator hook `registerPolicyOverride(table, sql)` for tables needing custom policies (PAP-100, PAP-179).
* Harness exported as a Vitest helper `expectTenantIsolation(db)` that PAP-60 and PAP-80 reuse.

Consumes: tables (PAP-33), roles (PAP-30 in staging, PAP-42 locally)."""},
**{"Definition of done": """* Harness passes on all core tables and fails when a test table lacks a policy (shown in the PR).
* Vitest: fail-closed with no context; bypass only with owner role; `EXPLAIN` shows the `tenant_id` index used.
* SQL tests committed in `packages/db/test/sql/`.
* Security Auditor sign-off comment.
* Terminal screenshots of harness output and `\\d+` policies at 1280; `docs/data/tenancy.md`; ADR `0007-rls-tenancy.md`; CHANGELOG; Linear comment."""},
**{"Test plan": """* Harness: for each tenant table, SELECT, INSERT, UPDATE, DELETE as tenant A against tenant B rows; expect zero rows or `42501`.
* Unit: generator output snapshot for a fixture schema including a nullable `tenant_id` table and a partitioned table.
* Negative: `INSERT ... ON CONFLICT` across tenants fails; `SET` (session) rejected by lint.
* Performance: `EXPLAIN ANALYZE` on a 100k-row `load` seed shows index scan; p95 overhead under 10 percent versus RLS off (bench committed).
* Bypass: audited path logs `bypass_read`; non-owner bypass attempt raises."""},
Demo="""Reviewer runs `pnpm --filter db test rls.harness` and watches every table pass, then adds a `scratch` table with `tenant_id` and no policy in a branch and reruns to watch the harness name it. Under 2 minutes.""",
**{"Edge cases": """* Nullable `tenant_id` handled explicitly; never leaks.
* Partition policies verified on each partition.
* Bulk COPY uses the owner role with explicit `app.tenant_id`.
* Materialised views need `security_invoker`.
* Missing context in a cron job: fail closed, PAP-43 sets `actor_kind = 'system'` with a tenant when needed."""},
Dependencies="""PAP-33 (hard). Consumed by PAP-35, PAP-36, PAP-38, PAP-39, PAP-59, PAP-60, PAP-80.""",
Agent="""Built by Forge (Schema Wright). Reviewed by Sentinel (Security Auditor).""",
Size="""M: one generator, one harness, strong proofs.""",
)

SPECS["PAP-35"] = dict(
Goal="""Umbrella: expose the database through oRPC so React hooks, Tauri clients and agents share one contract: Zod schemas derived from Drizzle, OpenAPI for external callers, every procedure inside the RLS tenant context. Three children; closes when `users.me` renders on staging through the typed client. Rate limiting and idempotency move to the data-layer rate-limit issue; the `Principal` type comes from PAP-55.""",
Scope="""Children:

1. API server, middleware chain and error mapping (`apps/api` on Hono 4, request id, auth stub with signed dev token, tenant resolution, `withTenant`, error codes, audit and OTel hooks).
2. API contract package and typed client (`packages/api-contract` with Zod from `drizzle-zod`, core routers `tenants`, `workspaces`, `users.me`, `memberships`, `roles`, `files` stubs, `health`; `packages/api-client` with `@orpc/tanstack-query`; `callAs` test utility).
3. OpenAPI docs, staging deploy and health (Scalar at `/api/docs`, `/api/health`, Coolify deploy through PAP-26, `redocly lint`).

Out: rate limiting and idempotency (separate issue), file upload bodies (PAP-37), realtime.""",
Spec="""* Procedures `router.<entity>.<verb>` with verbs `list|get|create|update|archive`; list input `{ cursor?, limit<=100, filter?: FilterTree, sort? }` returning `{ items, nextCursor }`; `FilterTree` comes from the data-layer filter grammar issue.
* Errors: `UNAUTHORIZED`, `FORBIDDEN`, `NOT_FOUND`, `CONFLICT`, `VALIDATION`, `RATE_LIMITED`, `INTERNAL`; RLS denials read as `NOT_FOUND`, write as `FORBIDDEN`.
* Context `{ requestId, principal: Principal | null, tenantId, db, log, span }` with `Principal` imported from `@paperos/core/principal` (PAP-55).
* Tenant from header `x-tenant` or subdomain; missing header on a tenant-scoped call is 400.
* Path prefix `/api/v1`; payloads over 1 MB rejected 413; `statement_timeout 2s` per procedure.
* Env from `serverEnvSchema` (PAP-17); graceful shutdown.""",
**{"Interface contract": """Provides:

* `AppRouter` type and `createClient(baseUrl, { getToken, getTenant })` from `@paperos/api-client`; hooks via `orpc.<entity>.<verb>.queryOptions()` and `infiniteOptions()`.
* Server helpers from `@paperos/api-contract/server`: `os` (oRPC builder with context), `tenantProcedure`, `publicProcedure`, `defineRouter(name, routes)` that modules (PAP-28) register with.
* `callAs(principalFixture)` test utility.
* HTTP: `/api/v1/rpc/*`, `/api/v1/openapi.json`, `/api/docs`, `/api/health`, `/healthz`, `/__version`; headers `x-request-id`, `x-tenant`, `traceparent`.
* Error code enum `ApiErrorCode`.

Consumes: `Principal` (PAP-55), session verification (PAP-57; dev-token stub until then), `createDb`/`withTenant` (PAP-32), RLS context (PAP-34), `FilterTree` (filter grammar issue), audit vars (PAP-38), spans (PAP-40)."""},
**{"Definition of done": """* All three children Done.
* Integration test: `apps/api` on staging serves `/api/health` and `/api/docs` over TLS; `apps/web` dashboard renders `users.me` through the typed client; a client call with a wrong input fails typecheck.
* `pnpm gen:api --check` and `redocly lint` green; `docs/data/api.md`; CHANGELOG; Linear comment with the staging docs URL."""},
**{"Test plan": """* Unit: middleware chain order, error mapping table, tenant resolution (header, subdomain, missing, mismatch).
* Contract: every core router happy and forbidden path through `callAs`; `expectTypeOf` tests for input inference.
* Integration (CI compose): RLS denial mapped to `NOT_FOUND`; 1 MB payload rejected; slow query cancelled at 2 s.
* E2E: Playwright loads the dashboard route and asserts `users.me` name at 375, 1024, 1920; Scalar page screenshot.
* Lint: OpenAPI validated on every PR."""},
Demo="""Reviewer opens `https://staging.PAPEROS_DOMAIN/api/docs`, calls `users.me` from the Scalar console with the dev token and tenant header, then opens the web dashboard showing the same user. Under 90 seconds.""",
**{"Edge cases": """* Actor in several tenants: header required; `users.me` lists tenants.
* Zod drift after a migration caught by the stale check.
* Retries on `create`: covered by the idempotency issue; until then documented as unsafe.
* Auth stub must be impossible to enable in production (env guard test)."""},
Dependencies="""PAP-33 (hard). Soft: PAP-34, PAP-55, PAP-57, PAP-17. Unblocks PAP-36, PAP-39, PAP-40, PAP-119, PAP-129, PAP-163 and every business router.""",
Agent="""Built by Forge. Reviewed by Sentinel (Code Reviewer and Security Auditor).""",
Size="""L as an umbrella; children are M, M, S.""",
)

SPECS["PAP-36"] = dict(
Goal="""Umbrella: give every target instant, offline-capable reads and queued writes with the engine PAP-31 chose (default ElectricSQL shapes plus PGlite). Tenant-scoped shapes stream into a local database, React hooks read locally, writes go through oRPC via an outbox that replays on reconnect. Three children; closes on the offline edit demo.""",
Scope="""Children:

1. Electric service deployment and tenant-scoped shape proxy (`ops/compose/electric.yml`, `electric` role, `GET /api/sync/shape` with server-set `where`, table allowlist).
2. PGlite client, schema generation and read hooks (`pnpm gen:pglite`, `defineShape`, `SyncClient`, `useShape`, `useLiveQuery`, IndexedDB and Tauri file persistence).
3. Offline write outbox and sync indicator (`_outbox` table, `mutate()` with optimistic updater, replay with backoff, leader election, `<SyncIndicator/>`, demo route).

Out: multi-client conflict UX (PAP-143), full offline queue semantics and ordering (PAP-148 extends this outbox), view compilation (PAP-163).""",
Spec="""* Core shapes: `workspaces`, `memberships`, `users` (tenant members, limited columns), `files` (metadata); other packages register their own.
* Proxy `GET /api/sync/shape?table=&offset=&handle=&live=` forwards to Electric with `where tenant_id = <principal tenant>` appended; non-registered tables denied; response streamed.
* `gen:pglite` emits `packages/sync/generated/schema.sql` for registered tables, versioned by hash; mismatch resets the local database but keeps the outbox.
* Outbox rows `{ id uuidv7, procedure, input, createdAt, attempts, lastError, status }`; backoff 1 s to 60 s, 20 attempts, then `failed` with retry or discard UI.
* Warn above 200 MB local storage; shapes support `columns`.""",
**{"Interface contract": """Provides (from `@paperos/sync`):

* `defineShape({ table, where?, columns? })`, `registerShape(shape)`, `useShape(shape)`, `useLiveQuery(sql, params)`, `mutate(procedure, input, { optimistic })`, `useSyncStatus(): { state: 'online'|'offline'|'syncing'|'error', pending: number }`.
* Shape registry consumed by PAP-143 (record sync), PAP-163 (shape eligibility), PAP-148 (queue extension).
* Route `GET /api/sync/shape` and error `SHAPE_FORBIDDEN` (403); header `x-sync-schema-hash`.
* Local tables `_outbox`, `_sync_meta`.
* Component `SyncIndicator` in `@paperos/ui`.

Consumes: publication and `electric` role (PAP-30), RLS context semantics for the proxy (PAP-34), oRPC client and `Principal` (PAP-35), ADR decision block (PAP-31), `useOnline` (PAP-18)."""},
**{"Definition of done": """* All three children Done.
* Integration test: `/_app/sync-demo` lists workspaces from PGlite; rename one offline, reload, go online, the write replays (Playwright with `setOffline`; recording); cross-tenant shape request returns 403; 2k-row initial shape under 1.5 s on CI.
* Electric on staging, health checked from `/api/health`; `docs/data/sync.md`; CHANGELOG; Linear comment with recording and preview."""},
**{"Test plan": """* Unit: outbox state machine, backoff schedule, schema-hash reset preserving the outbox, leader election with two fake tabs.
* Integration (CI compose with Electric): shape proxy appends `where`, denies unknown tables, streams `live` responses; PGlite schema generated matches Drizzle for registered tables.
* E2E: offline edit and replay; two tabs open, only one replays (`navigator.locks`).
* Bench: initial 2k-row load timed in CI, committed.
* Visual: `<SyncIndicator/>` four states at 375, 768, 1280, 1920; demo route at seven widths."""},
Demo="""Reviewer opens `/_app/sync-demo` on staging, toggles DevTools offline, renames a workspace (indicator shows one pending), reloads (edit persists locally), goes online and watches the indicator clear while the server row updates. Under 2 minutes.""",
**{"Edge cases": """* Server rejects a replayed write with `FORBIDDEN`: mark failed, surface reason, roll back the optimistic row.
* Expired shape handle after long offline: full re-fetch, outbox kept.
* Safari private mode: in-memory PGlite with banner.
* Tombstones for rows deleted while offline: local rows removed; outbox writes fail cleanly.
* Server timestamps only; never compare client clocks."""},
Dependencies="""PAP-31, PAP-35 (hard), PAP-30 (logical replication) and PAP-34 (proxy semantics), both now encoded. Unblocks PAP-143, PAP-148, PAP-163, PAP-23.""",
Agent="""Built by Forge with Nova (CRDT Engineer) pairing on the outbox. Reviewed by Sentinel.""",
Size="""L as an umbrella; children are M, M, M.""",
)

SPECS["PAP-37"] = dict(
Goal="""Let any app accept files safely: MinIO per environment, presigned direct uploads from browser and native, server-side validation, automatic image variants and tenancy-respecting signed downloads. Variants run on PAP-43 jobs; this is the reference consumer of that package.""",
Scope="""In:

* MinIO via Coolify (`ops/compose/minio.yml`): buckets `paperos-prod`, `paperos-staging`; versioning on; lifecycle purging `pending/` after 24 h; console VPN-only.
* `packages/files` server procedures `files.createUpload`, `files.complete`, `files.getUrl`, `files.delete`, `files.list` registered in PAP-35.
* Variants job `files.variants` (`thumb 256`, `md 1024`, `lg 2048` in WebP and AVIF via `sharp` 0.34).
* Client `uploadFile(file, { onProgress })` with multipart resume; `<FileDrop/>` in `@paperos/ui`.
* Nightly reconciliation job.

Out: document previews, virus scanning (Trivy covers images only; ClamAV is a follow-up), CDN.""",
Spec="""* Key layout `<tenant_id>/<yyyy>/<mm>/<file_id>/<slug>`; client filename never trusted for keys; `Content-Disposition` set on GET.
* Presign with `@aws-sdk/client-s3` and `s3-request-presigner`; `x-amz-checksum-sha256` required on PUT.
* `files.complete` HEADs the object, verifies size and sha256, sniffs MIME with `file-type`, rejects rows not `pending` for this actor, enqueues variants.
* Variants only for `image/*` up to 50 MP; EXIF stripped; SVG served with `Content-Security-Policy: sandbox`; HEIC converted.
* Download URLs valid 15 minutes, generated after an RLS-scoped row fetch.
* Every create, complete and delete emits an `audit_event` (PAP-38).""",
**{"Interface contract": """Provides:

* oRPC `files.*` procedures with `FileDto = { id, name, mime, size, status, variants: Record<'thumb'|'md'|'lg', { webp: string; avif: string }>, createdAt }`.
* Client `uploadFile`, `useUpload()`, `FileDrop`; server helper `getSignedUrl(fileId, { variant? })` for other routers (PAP-131 attachments, PAP-72 logo, PAP-185 receipts).
* Job `files.variants` defined with `defineJob` (PAP-43).
* Env `S3_ENDPOINT`, `S3_BUCKET`, `S3_ACCESS_KEY`, `S3_SECRET_KEY` (PAP-17 names).
* Bucket `paperos-<env>` layout the object-storage DR issue backs up.

Consumes: `file` table (PAP-33), API host (PAP-35), jobs (PAP-43), audit (PAP-38), camera capability for mobile uploads (PAP-20, soft)."""},
**{"Definition of done": """* Upload a 5 MB JPEG from web and from the Android emulator camera; variants within 10 s (recording).
* Multipart resume: pause at 60 percent, reload, resume, complete (Playwright).
* Vitest: presign params, complete validation, key sanitisation, variant queue; integration against MinIO in CI.
* Cross-tenant `getUrl` returns `NOT_FOUND`.
* `<FileDrop/>` states at 375, 768, 1280, 1920; `docs/data/files.md`; CHANGELOG; Linear comment."""},
**{"Test plan": """* Unit: slug sanitiser with traversal and control characters; MIME sniff versus header mismatch; size and hash mismatch; zero-byte rejection.
* Integration (CI compose with MinIO): full create, PUT, complete, variants, getUrl round trip; lifecycle rule verified by setting a 1-minute expiry in test.
* Permission: `callAs(tenantB)` on tenant A's file returns `NOT_FOUND`.
* E2E: Playwright drag-and-drop upload and resume; Android emulator camera upload recorded.
* Visual: five `<FileDrop/>` states at four widths, light and dark."""},
Demo="""Reviewer drags a photo onto `<FileDrop/>` on the settings example page, watches progress, sees the thumbnail appear, opens the signed URL in a new tab and reloads it after 15 minutes to see it expire. Under 2 minutes (expiry checked later).""",
**{"Edge cases": """* Same content twice: allowed; `sha256` index enables dedupe later.
* MinIO down during `complete`: 503 with retry-after.
* Leaked presigned URL: 15-minute expiry documented as a bearer secret.
* Object without row: quarantined prefix by reconciliation.
* Mobile upload on cellular: chunk size 5 MB, resume on reconnect."""},
Dependencies="""PAP-33, PAP-43 (hard). Soft: PAP-38, PAP-20. Consumed by PAP-72, PAP-131, PAP-134, PAP-185, growth issues.""",
Agent="""Built by Forge (Ops Runner for MinIO, Platform Engineer for the service). Reviewed by Sentinel (Security Auditor).""",
Size="""M: one service, one job, one component.""",
)

SPECS["PAP-38"] = dict(
Goal="""Record every mutation as an immutable `audit_event` with who (human, agent, service or system), what changed (before, after, diff), why (a reason agents must supply) and which request caused it, so Justin can answer "who changed this and why" for any row and reviewers can trace agent behaviour to data.""",
Scope="""In:

* Append-only guarantees: table owned by `paperos_owner`; app role has INSERT and SELECT; triggers reject UPDATE and DELETE; monthly partitions, 24-month retention, Parquet archival to MinIO.
* Generic trigger `paperos.audit_trigger()` attached by the PAP-34 generator, reading `app.actor_id`, `app.actor_kind`, `app.request_id`, `app.reason`.
* Diff `{ field: { from, to } }` excluding `updated_at`; redaction via `paperos.audit_redactions` fed by PAP-41's `pii.json`.
* Per-tenant hash chain; `pnpm audit:verify`.
* oRPC `audit.list`, `audit.forEntity`; `<AuditTrail/>` in `@paperos/ui`.

Out: retention enforcement for other tables (retention issue), log shipping (PAP-40).""",
Spec="""* Actions `insert|update|delete|restore|bypass_read`.
* Opt-out list for high-churn tables in `packages/db/src/audit/exclusions.ts`.
* Partitions three months ahead via `pg_partman` or a monthly cron; default partition as safety net with alert.
* Archival monthly: partitions older than 24 months to `audit/<yyyy>/<mm>.parquet` via DuckDB in a PAP-43 job, then detach and drop after checksum.
* `hash = sha256(prev_hash || canonical json)` per tenant.
* Overhead under 15 percent on a 10k-row bulk update; `app.audit_mode = 'summary'` writes one event per batch for imports.
* Agent writes without `app.reason` are rejected; human writes may omit it.""",
**{"Interface contract": """Provides:

* Session variables read: `app.actor_id`, `app.actor_kind`, `app.request_id`, `app.reason`, `app.audit_mode` (set by PAP-32 `createDb`, supplied by PAP-35 middleware and PAP-43 workers).
* Table `paperos.audit_redactions (table_name, column_name)` populated from `pii.json` (PAP-41).
* oRPC `audit.list({ actor?, action?, entityType?, entityId?, from?, to?, cursor? })` and `audit.forEntity(entityType, entityId)`; `AuditEventDto`.
* Component `AuditTrail` with props `{ entityType, entityId }`.
* SQL helper `paperos.audit_summary_begin()` for bulk imports (PAP-199).
* Jobs `audit.partitions`, `audit.archive` (PAP-43).

Consumes: `audit_event` table (PAP-33), generator hook (PAP-34), context vars (PAP-35), jobs (PAP-43), bucket (PAP-37)."""},
**{"Definition of done": """* Every API write on a seeded tenant produces an event with correct actor, diff and request id (integration test).
* UPDATE and DELETE as `paperos_app` fail; hash-chain verification passes and detects a tampered row.
* Agent mutation without reason rejected; human allowed.
* `<AuditTrail/>` on the settings example page at 375, 768, 1024, 1280, 1920, light and dark.
* Bench committed; partition test; `docs/data/audit.md`; CHANGELOG; Linear comment."""},
**{"Test plan": """* SQL: trigger tests for insert, update, delete, restore; redaction of a listed column; `truncated` flag on a 100 KB jsonb.
* Unit: canonical JSON and hash chain; `audit:verify` on a fixture with one tampered row.
* Integration: `callAs(agent)` update without reason raises `VALIDATION`; cascading delete shares one `request_id`.
* Bench: 10k-row bulk update with and without trigger, committed with numbers.
* Visual: `AuditTrail` grouped by request at five widths."""},
Demo="""Reviewer edits a workspace name on the settings page, opens the Audit tab and sees the event with actor, before and after, reason and request id, then runs `pnpm audit:verify --tenant <slug>` for a green chain. Under 90 seconds.""",
**{"Edge cases": """* Large jsonb: before and after capped at 64 KB each with hash and `truncated`.
* Cron actor: `actor_kind = 'system'`, reason equals job name.
* Redaction list changes: history not rewritten.
* Missing current partition after restore: default partition plus alert.
* Timezone: stored UTC, rendered in the viewer's zone."""},
Dependencies="""PAP-33 (hard). Soft: PAP-34, PAP-35, PAP-43, PAP-37, PAP-41. Consumed by PAP-61, PAP-64, PAP-129, PAP-179, PAP-114.""",
Agent="""Built by Forge (Schema Wright) with Iris on `<AuditTrail/>`. Reviewed by Sentinel (Security Auditor).""",
Size="""M: trigger, chain, two procedures, one component.""",
)

SPECS["PAP-39"] = dict(
Goal="""One search API over any entity: packages register searchable fields once, Postgres keeps a `tsvector` and optional `pgvector` embedding current, and `search.query` returns ranked, tenant-scoped, permission-filtered results that the command bar, knowledge search and table filters reuse.""",
Scope="""In:

* Registry `packages/search/src/registry.ts`: `registerSearchable({ entity, table, titleField, bodyFields, facets, weight, embed, route })`; core registrations `workspace`, `user`, `file`.
* Table `search_document` with `tsv` (GIN), `embedding vector(1024)` (HNSW), `pg_trgm` GIN on `title`, `facets jsonb`; RLS like any tenant table.
* Triggers calling `paperos.search_upsert(entity_type, id)`; embeddings via PAP-43 job through `EmbeddingProvider` (OpenAI-compatible endpoint, self-hosted `text-embeddings-inference` on staging).
* `search.query({ q, mode: 'keyword'|'semantic'|'hybrid', entityTypes?, facets?, limit })` with RRF fusion and a `can()` post-filter.
* `<SearchResults/>` in `@paperos/ui`.

Out: cross-source unification UI (PAP-138), command palette (PAP-151).""",
Spec="""* Language `english` default; per-tenant `settings.search.language`; `simple` fallback.
* Body cap 100 KB with flag; model name stored per row; reindex when the model changes.
* Latency at 100k docs: keyword p95 under 80 ms, hybrid under 250 ms.
* Facets as jsonb containment; top 5 values per key returned.
* Soft-deleted rows drop their document.
* Registry validated at boot against Drizzle types and live columns.
* Bulk imports set `app.search_mode = 'deferred'` then reindex.""",
**{"Interface contract": """Provides (from `@paperos/search`):

* `registerSearchable(def)`, `SearchableDef` type, `search.query` procedure returning `{ items: [{ entityType, entityId, title, snippet, score, href, facets }], facetCounts }`.
* Job `search.embed` (PAP-43) and `EmbeddingProvider` interface `{ model, dims, embed(texts): Promise<number[][]> }`.
* Session var `app.search_mode` read by triggers.
* Component `SearchResults` with empty and error states.

Consumes: tables (PAP-33), RLS (PAP-34), API host (PAP-35), jobs (PAP-43), `can()` post-filter (PAP-59; allow-all stub until merged), `vector` and `pg_trgm` extensions (PAP-30, PAP-42)."""},
**{"Definition of done": """* "acme" on the demo seed returns the Acme workspace and members ranked sensibly; "acmee" still finds it (recording).
* Semantic mode works against the staging embedding container.
* Vitest: registry validation, query builder, RRF; integration for triggers and post-filter (cross-tenant never appears).
* Bench at 100k docs committed.
* `<SearchResults/>` at 375, 768, 1280, 1920 including empty and error; `docs/data/search.md`; CHANGELOG; Linear comment."""},
**{"Test plan": """* Unit: registry rejects unknown columns and duplicate entities; RRF fusion determinism; query sanitiser for stop-word-only input.
* Integration (CI compose): insert, update, soft-delete a workspace and assert `search_document` follows; deferred mode batches; embeddings job with a fake provider.
* Permission: `callAs(tenantB)` never sees tenant A; `can()` denial removes a hit.
* Bench: `load` seed, keyword and hybrid p95 recorded.
* Visual: results, empty, error, loading at four widths."""},
Demo="""Reviewer types "acme" into the search box on the dashboard, sees workspace and members grouped by type, misspells it as "acmee" and still gets the workspace, then switches to semantic mode and searches "billing team". Under a minute.""",
**{"Edge cases": """* Empty query returns recent items.
* Provider down: keyword results still return; job retries.
* Non-English content in `english` config documented; `simple` per tenant.
* Entity registered twice: boot error naming both packages.
* Very long titles truncated in snippets, full on hover."""},
Dependencies="""PAP-33, PAP-43 (hard), PAP-34, PAP-35 and PAP-59 (now encoded). Consumed by PAP-138, PAP-151, PAP-166, PAP-189.""",
Agent="""Built by Forge (Schema Wright) with Nova on hooks. Reviewed by Sentinel.""",
Size="""M: registry, table, triggers, one procedure and a component.""",
)

SPECS["PAP-40"] = dict(
Goal="""Make latency and errors visible per route, tenant and agent: OpenTelemetry traces from the web client through the API to Postgres, slow-query logging and Grafana dashboards on the VPS that reviewers and the release digest link to, so regressions are seen before customers report them.""",
Scope="""In:

* Stack via Coolify (`ops/compose/observability.yml`): Grafana 11, Prometheus, Loki, Tempo, OTel Collector, `postgres_exporter` (PAP-30), `node_exporter`, cAdvisor; VPN-only until PAP-57 SSO.
* API: `@opentelemetry/sdk-node` 2.x auto-instrumentation plus an oRPC middleware span with `paperos.tenant_id`, `paperos.actor_kind`, `paperos.actor_id`, `paperos.procedure`, `paperos.request_id`, `linear.issue`.
* Web and Tauri: `sdk-trace-web` with fetch instrumentation, `traceparent` propagation, Web Vitals as metrics; 10 percent sampling in production, 100 percent on staging, always on error.
* Six dashboards provisioned from JSON; alerts for 5xx rate, p95 latency, slow queries, disk.
* Client error reports from the app-shell error-handling issue land in the same collector.

Out: business analytics (PAP-194), cost metering (PAP-99 consumes attributes).""",
Spec="""* Env `OTEL_EXPORTER_OTLP_ENDPOINT`, `OTEL_SERVICE_NAME`, `OTEL_TRACES_SAMPLER`, `OTEL_TRACES_SAMPLER_ARG` (PAP-17).
* Request id equals trace id where possible; API returns `x-request-id` and `traceparent`; error toasts show the short id.
* PII policy: no emails, names or bodies on spans; a span processor drops disallowed keys using `pii.json` (PAP-41) plus a static denylist.
* Retention: Tempo 7 days, Loki 14, Prometheus 30.
* k6 script `ops/observability/k6/api-smoke.js` (200 VUs, 5 min) on staging validates dashboards and alerts.
* Browser export via `/api/otel` proxy to defeat ad blockers.""",
**{"Interface contract": """Provides:

* Span attribute names above as the metering contract for PAP-99 and PAP-114.
* Headers `x-request-id`, `traceparent` on every API response (PAP-35 emits, this issue standardises).
* Endpoint `POST /api/otel` (OTLP/HTTP proxy) used by the web SDK and the client error-reporting issue.
* Grafana dashboards `api-overview`, `tenant-latency`, `postgres`, `sync`, `web-vitals`, `host`, provisioned from `ops/observability/dashboards/*.json`; alert routes to Linear via PAP-97 or email.
* Metrics `paperos_kiosk_*` scraped from PAP-23 health.

Consumes: API middleware hook (PAP-35), exporter (PAP-30), `pii.json` (PAP-41), env schema (PAP-17), SSO (PAP-57, soft)."""},
**{"Definition of done": """* A trace from a web click to a Postgres query appears in Tempo with tenant attributes (screenshot).
* Six dashboards provisioned on a fresh Grafana with no manual clicks; screenshots at 1280 and 1920.
* Induced 5xx storm fires the alert and creates a Linear issue or email (evidence).
* Vitest: PII filter, request id propagation; k6 summary committed.
* Web Vitals from the Pages demo bucketed by breakpoint; `docs/ops/observability.md`; CHANGELOG; Linear comment."""},
**{"Test plan": """* Unit: span processor drops `user.email` and any key in `pii.json`; sampler keeps error spans at 0 percent ratio.
* Integration (CI compose with collector): a request through `apps/api` yields a trace with the expected attributes (assert via Tempo API).
* Load: k6 run on staging; dashboards populate; p95 panel matches k6 summary within 10 percent.
* Alerting: inject 5xx for 2 minutes with a feature toggle; alert fires; evidence saved.
* Visual: six dashboards at 1280 and 1920."""},
Demo="""Reviewer clicks a button on staging, copies the request id from the toast footer, pastes it into Grafana Explore and follows the trace from browser span to SQL statement, then opens the tenant-latency dashboard. Under 2 minutes over the tailnet.""",
**{"Edge cases": """* Collector down: batch exporter drops on full queue, never blocks.
* High-cardinality metric labels forbidden; lint test.
* Clock skew: server receive time orders dashboards.
* Log disk pressure: Loki retention plus Docker log rotation.
* Rare errors under sampling: tail-based always-on-error in the collector."""},
Dependencies="""PAP-35 (hard), PAP-30 (exporter, now encoded). Soft: PAP-41, PAP-57, PAP-97. Consumed by PAP-87, PAP-88, PAP-99, PAP-114, PAP-147.""",
Agent="""Built by Forge (Ops Runner). Reviewed by Sentinel (Code Reviewer).""",
Size="""M: compose stack, two SDK setups, six dashboards.""",
)

SPECS["PAP-41"] = dict(
Goal="""Generate a living data dictionary from the Drizzle schema so Justin, agents and future staff can browse every table, column, relation, index, RLS policy and audit setting in the docs engine, with descriptions kept beside the code and regenerated on every merge. Its `pii.json` output is the single source for sensitivity used by audit redaction, OTel filtering and the retention issue.""",
Scope="""In:

* Generator `packages/db/src/dictionary/generate.ts` merging Drizzle objects, live `information_schema`, `pg_policies`, `pg_trigger` and a `dictionary.yaml` sidecar into `docs/data/dictionary/*.md` and `dictionary.json`.
* Per-table content: purpose, owner project (`@owner`), columns (type, nullable, default, description, PII, retention), relations, indexes, policies, audit inclusion, search registration, seeds, linked issues.
* Mermaid ER diagrams per `@domain` and whole schema.
* `pii.json`, `--check` stale detection, PR comment on schema change.
* `<DataDictionaryTable/>` rendering in PAP-128.

Out: editing descriptions in-app, external tables' semantics.""",
Spec="""* `dictionary.yaml`: `tables.<name>.description`, `columns.<col>.{ description, pii: boolean, retention?: string, example }`; Zod-validated; unknown keys fail.
* Deterministic output (sorted keys).
* `dictionary.json`: `{ generatedAt, schemaHash, tables: [{ name, domain, owner, description, columns, relations, indexes, policies, audited, searchable, retention }] }`.
* Front-matter `title`, `owner`, `generated: true`, `sourceHash`.
* Cross-domain relations drawn dashed; wide tables collapse column groups by prefix.""",
**{"Interface contract": """Provides:

* `dictionary.json` consumed by PAP-119 (spec data-section validation), PAP-199 (mapping targets), PAP-115.
* `pii.json` `{ [table]: string[] }` consumed by PAP-38 redactions, PAP-40 span filter and the retention issue.
* Scripts `pnpm dictionary:generate`, `pnpm dictionary:check` (Gate 1 via PAP-78).
* Tags `@owner <project>`, `@domain <name>`, `@pii`, `@retention <duration>` in schema file comments as the annotation convention for every schema author.

Consumes: schema (PAP-32), policies (PAP-34), audit exclusions (PAP-38), search registry (PAP-39), docs engine (PAP-128), table component (PAP-71)."""},
**{"Definition of done": """* Dictionary for every table at merge time; 100 percent description coverage for core entities.
* `--check` stale detection proven; schema-change PR comment on a test PR.
* Vitest: YAML validation, determinism, PII export, Mermaid snapshot.
* Rendered pages at 375, 768, 1024, 1280, 1920 including one table page and the ER diagram.
* `pii.json` consumed by the PAP-40 filter test; README on maintaining descriptions; CHANGELOG; Linear comment."""},
**{"Test plan": """* Unit: two runs produce byte-identical output; YAML with a renamed column fails with the nearest-name suggestion; Mermaid snapshot for a three-table fixture.
* Integration (CI compose): generate against the migrated dev database; external tables (Better Auth, pg-boss) listed under External.
* Contract: `dictionary.json` validates against its JSON schema; PAP-119 fixture consumes it.
* Visual: five widths of a table page and the ER diagram in the docs engine."""},
Demo="""Reviewer opens the in-app docs, navigates Data, Dictionary, `membership`, reads columns with PII badges and the RLS policy SQL, clicks a relation to `role`, then views the core ER diagram. Under a minute.""",
**{"Edge cases": """* Table in database but not Drizzle: External section, not an error.
* Enums and arrays rendered readably.
* Partitioned tables show parent with strategy.
* Views include definition SQL.
* Eighty-plus columns collapse by prefix."""},
Dependencies="""PAP-32, PAP-128 (hard). Soft: PAP-34, PAP-38, PAP-39, PAP-71. Consumed by PAP-119, PAP-199, PAP-115, the retention issue.""",
Agent="""Built by Quill (Documentation Lead) with Forge (Schema Wright) on introspection. Reviewed by Sentinel.""",
Size="""S: a generator and templates.""",
)

SPECS["PAP-42"] = dict(
Goal="""Give every Claude Code session, CI job and Justin's laptop an identical, disposable backing stack in one command so the dozens of parallel sessions never collide on a shared database. This is why PAP-32 no longer waits for the VPS.""",
Scope="""In:

* `ops/compose/dev.yml`: `postgres` (`pgvector/pgvector:pg17`, `wal_level=logical`, init roles), `minio` (bucket `paperos-dev`), `mailpit`, `hocuspocus` placeholder; profiles `core`, `realtime`, `sync`, `full`.
* `pnpm stack up|down|reset|logs|prune` in `packages/config-scripts`, project name and ports derived from the git worktree.
* Per-worktree `DATABASE_URL` written to `.env.local`; `.claude/hooks/session-start.sh` runs `stack up`, migrations and seeds when present.
* Reusable `ci-services.yml` with the same service versions and env names.
* `docs/dev/local-stack.md`.

Out: production services, schema (PAP-32).""",
Spec="""* Ports: base 5432, 9000, 9001, 8025, 1234 plus `offset = hash(branch) % 50 * 100`; `main` is offset 0; deterministic across restarts.
* `worktree.ts` slugifies `git rev-parse --abbrev-ref HEAD` to 40 chars; truncation collisions append a 4-char hash.
* Volumes per project name: `down` keeps data, `reset` removes, `prune` removes stacks for deleted branches.
* `stack up` under 60 s warm, waits for `pg_isready`, holds `flock .stack.lock`.
* `PAPEROS_STACK=remote` uses the shared staging database read-only when Docker is missing; database tests skip with a visible warning.
* `ci-services.yml` env names asserted against `dev.yml` by a unit test.""",
**{"Interface contract": """Provides:

* Scripts `pnpm stack *`; env written to `.env.local`: `DATABASE_URL`, `DATABASE_URL_MIGRATOR`, `S3_ENDPOINT`, `S3_ACCESS_KEY`, `S3_SECRET_KEY`, `S3_BUCKET=paperos-dev`, `SMTP_URL`, `YJS_URL`, `ELECTRIC_URL` (names from PAP-17).
* Roles `paperos_owner`, `paperos_app`, `paperos_readonly`, `electric` identical to PAP-30 so PAP-34 tests run locally.
* Reusable workflow `imagine-os/paperos-template/.github/workflows/ci-services.yml` with service containers for PAP-78 and every Vitest job that needs Postgres, MinIO or Mailpit.
* Hook `.claude/hooks/session-start.sh` contract for PAP-93: prints stack status, ports and next steps; exit 0 always.

Consumes: scripts folder and `.claude/` (PAP-13)."""},
**{"Definition of done": """* Two worktrees on different branches run `stack up` simultaneously and connect to different databases on different ports (transcript).
* Fresh clone plus `pnpm i && pnpm stack up && pnpm test` passes on Linux and macOS with zero manual steps.
* A Claude Code session in a worktree shows the hook output and can run `db:migrate` immediately (screenshot).
* `ci-services.yml` used by at least one Vitest job hitting Postgres; Mailpit shows a smoke-test message (screenshot).
* `docs/dev/local-stack.md`; CHANGELOG; Linear comment."""},
**{"Test plan": """* Unit: slug function on slashes, unicode and long names; port offset determinism; env-name parity between `dev.yml` and `ci-services.yml`.
* Integration: CI job starts two stacks with different `--offset` and asserts distinct `pg_isready` ports; `reset` drops data; `prune` removes a stack for a deleted branch.
* Hook: run in a fresh worktree with and without Docker; assert messages and exit 0.
* Smoke: SMTP send to Mailpit, S3 put to `paperos-dev`, `SELECT 1` via `paperos_app`."""},
Demo="""Reviewer creates a second worktree with `scripts/worktree.sh new PAP-999`, runs `pnpm stack up` in both, sees two different port sets printed, connects with `psql` to each and then runs `pnpm stack prune` after deleting the branch. Under 2 minutes with warm images.""",
**{"Edge cases": """* Docker missing: install instructions and the `remote` option; never silent passes.
* Port collision: `--offset <n>` persisted.
* Apple Silicon: all images multi-arch, verified.
* Disk full of stale volumes: `prune` plus the end-of-session checklist in PAP-93.
* CI has no compose profiles: services listed explicitly."""},
Dependencies="""PAP-13 (hard). Soft: PAP-17. Unblocks PAP-32, PAP-57, PAP-37, PAP-140, PAP-78, PAP-93.""",
Agent="""Built by Forge (Platform Engineer). Reviewed by Sentinel (Code Reviewer).""",
Size="""S: one compose file, one script package, one hook.""",
)

SPECS["PAP-43"] = dict(
Goal="""Provide the one background-work runtime eight later issues assume by name: `packages/jobs` on pg-boss 10.x (Postgres-native, no Redis; PAP-214 confirms or overrides) with at-least-once delivery, idempotent handlers, ordered retries, cron, a dead-letter queue and a staff admin view. The transactional outbox for domain events (events issue) and the tenant-lifecycle purge job build on it.""",
Scope="""In:

* `defineJob({ name, schema, handler, retry, concurrency, singletonKey, timeout })` registry; `enqueue(job, input, { idempotencyKey, runAt, priority, tenantId })`; `schedule(job, cron, input)`.
* `apps/worker` entry with its own Dockerfile (PAP-26) loading every registered job.
* pg-boss schema `jobs`; tenant and actor context propagated so PAP-38 records `actor_kind = 'system'`.
* `withIdempotency(key, fn)` backed by `jobs.idempotency`.
* Retries 5 attempts, backoff 10 s to 10 min; `jobs.dead_letter` with requeue.
* `/admin/jobs` page (staff only) using PAP-165 grid.

Out: durable workflows and human approvals (PAP-174 automations), event catalogue (events issue).""",
Spec="""* Job names `domain.action`; duplicates rejected at boot.
* Payload validated on enqueue and dequeue; drift fails into dead-letter, not a crash.
* `concurrency: { perTenant: n }` via `singletonKey = tenantId` groups.
* SIGTERM drains 30 s; unfinished jobs return to the queue.
* `runAt` and cron in UTC.
* Archive after 7 days, delete after 30; dead-letter kept 90 days.
* Inputs over 64 KB rejected; store blobs in PAP-37 and pass a reference.
* `pnpm dev` runs an inline worker; dev shell banner when jobs are pending without a worker.""",
**{"Interface contract": """Provides (from `@paperos/jobs`):

* `defineJob`, `enqueue`, `schedule`, `withIdempotency`, `JobContext = { tenantId?, actorId?, requestId, attempt, log }`; `JobDefinition<TInput>` type.
* Tables `jobs.*` (pg-boss), `jobs.idempotency (key, completed_at, result)`, `jobs.dead_letter`.
* oRPC `jobs.list|get|requeue|cancel` (staff only) and page `/admin/jobs`.
* Docker image `ghcr.io/imagine-os/<app>-worker` (PAP-26).
* Metrics `paperos_jobs_*` for PAP-40.

Consumers by name: `files.variants` (PAP-37), `search.upsert|embed` (PAP-39), `audit.partitions|archive` (PAP-38), `notify.deliver` (PAP-136), `outreach.step` (PAP-191), `social.publish` (PAP-190), `attribution.rollup` (PAP-194), `import.chunk` (PAP-199), `export.run` (PAP-205), `events.dispatch` (events issue), `tenant.purge` (lifecycle issue). Consumes: schema and migrations (PAP-32), library decision (PAP-214), audit vars (PAP-38), `can()` for the admin page (PAP-59)."""},
**{"Definition of done": """* 1,000 jobs processed by two replicas with zero duplicate effects (one row per key).
* Worker killed mid-job: reruns on the other replica; idempotency guard prevents a double effect (log).
* Cron fires within a 3-minute window; admin view shows the run.
* Dead-letter requeue works; customer principal cannot open `/admin/jobs`.
* PAP-37 variants converted to `packages/jobs` as the reference consumer.
* `docs/platform/jobs.md`, ADR note, CHANGELOG, Linear comment with metrics screenshot."""},
**{"Test plan": """* Unit: registry duplicate rejection; schema validation on both sides; backoff schedule; `withIdempotency` under concurrent callers.
* Integration (CI compose): two worker processes, 1,000 enqueues with 500 distinct keys, assert 500 effects; SIGKILL one worker mid-handler; per-tenant concurrency limit observed.
* Cron: `*/1 * * * *` job asserted within 3 minutes.
* Permission: `callAs(customer)` on `jobs.list` returns `FORBIDDEN`.
* Visual: `/admin/jobs` at 768, 1280, 1920 with a dead-letter row."""},
Demo="""Reviewer opens `/admin/jobs` as staff, enqueues a demo job that fails twice then succeeds from the "Run demo" button, watches attempts and the retry schedule update live, then requeues a dead-letter row. Under 90 seconds.""",
**{"Edge cases": """* Postgres failover mid-poll: reconnect; expired `active` jobs retried.
* Handler never resolves: per-job timeout, default 5 minutes.
* Thundering herd after downtime: `singletonKey` per schedule collapses runs.
* Tenant deleted while queued: handler completes as `skipped`.
* Schema drift after deploy: dead-letter with a clear error."""},
Dependencies="""PAP-32, PAP-214 (hard). Soft: PAP-26, PAP-38, PAP-40, PAP-59, PAP-165. Unblocks PAP-37, PAP-39, PAP-136, PAP-174, PAP-190, PAP-191, PAP-194, PAP-199, PAP-205 and the events, email, DR and lifecycle issues.""",
Agent="""Built by Forge (Platform Engineer). Reviewed by Sentinel (Code Reviewer).""",
Size="""M: one package, one worker app, one admin page.""",
)
