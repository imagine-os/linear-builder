# data-layer — Data Layer & Database
PHASE P0 prio 1 dependsOn []
SUMMARY: Postgres 17 with row-level security, Drizzle schema-as-code, a typed API, local-first sync, files, search and audit.
DESC: Goal: every app gets a production-grade, multi-tenant data foundation without writing infrastructure. Postgres is the single source of truth, Drizzle defines the schema and migrations in TypeScript, and RLS policies enforce tenant isolation even against buggy agent-written queries. A typed RPC layer generates Zod schemas from the database so front-end hooks are always in sync. ElectricSQL shapes and PGlite give local-first reads and an offline write queue on every target. Core entities (tenant, workspace, user, membership, role, audit event, file) are shared by all other projects. Object storage, full-text plus vector search, an append-only audit log and OpenTelemetry observability round it out. Non-goals: multi-database support or a custom query language.
MILESTONES: ['Postgres + Drizzle baseline 2026-09-19: Database provisioned, schema and migrations flowing, core entities modelled', 'Local-first sync working 2026-09-24: Electric shapes and PGlite deliver offline reads and queued writes', 'Tenant-safe and observable 2026-09-30: RLS tested, audit log, search, tracing and data dictionary live']


## PAP-30 [P0 Infra M prio1 Backlog] Provision Postgres 17 on the self-hosted VPS with automated backups and point-in-time recovery
key=data-layer/postgres-provision milestone=Postgres + Drizzle baseline agent=Built by Forge (Ops Runner sub-agent). Reviewed by Sentinel 
blockedBy=['PAP-25'] blocks=['PAP-26']
GOAL: Stand up the production and staging Postgres 17 instances on the Hetzner VPS under Coolify, with continuous WAL archiving to object storage, nightly base backups, point-in-time recovery proven by a drill, and the extensions every later issue needs (pgvector, pg_trgm, pgcrypto, pg_stat_statements) pre-installed.
SCOPE: In:

* Coolify service definitions (exported as `ops/compose/postgres.yml` for reproducibility) for `pg-prod` and `pg-staging` using the `pgvector/pgvector:pg17` image (or `postgres:17` plus extension build; record choice).
* `pgBackRest` (preferred) or `WAL-G` sidecar shipping WAL to a MinIO bucket `pg-backups` (MinIO deployed here minimally; full file service is `data-layer/file-storage`); nightly full, hourly incremental, 14-day retention.
* Roles: `paperos_owner` (migrations only, `DATABASE_URL_MIGRATOR`), `paperos_app` (runtime, `NOBYPASSRLS`), `paperos_readonly` (reporting/agents), `electric` (logical replication), `paperos_backup`.
* Config tuned for 8 GB box: `shared_buffers 2GB`, `work_mem 16MB`, `max_connections 200` behind PgBouncer (transaction mode, `pgbouncer` container) except Electric which needs a direct connection.
* `wal_level = logical`, `max_replication_slots 10`, `m
SPEC(first 1200): * Secrets via Coolify env; documented names match `serverEnvSchema` in `app-shell/env-config`.
* `ops/db/init/*.sql` run on first boot: create roles, databases `paperos_prod`/`paperos_staging`, extensions, `ALTER SYSTEM` settings.
* Backup verification: daily `pgbackrest verify` plus a weekly automated restore drill (cron in Coolify) posting result to Linear via `pm-linear/webhooks` when available, else to a log.
* `ops/db/README.md`: connection strings per role, how to get a psql shell, PITR procedure with exact commands, RPO 1 h, RTO 30 min targets.
* `pnpm db:up` brings a local Postgres 17 with the same init scripts via Docker Compose for developers and CI (`ops/compose/dev.yml`).
DOD:
* Both instances reachable through PgBouncer with TLS from the API container; `SELECT version()` shows 17.x and all extensions installed.
* WAL archives appear in MinIO; `pgbackrest info` shows a full backup.
* Restore drill run: recover staging to a point 10 minutes earlier and confirm a deliberately inserted then deleted row is present; transcript attached.
* Local `pnpm db:up` works on Linux and macOS; CI uses the same compose file.
* Screenshots of Coolify service page, `pgbackrest info`, and exporter metrics (1280 and 1920).
* `ops/db/README.md` complete; ADR `docs/adr/0003-postgres-hosting.md`; CHANGELOG; Linear comment with drill transcript link.
EDGE:
* MinIO unavailable during archive: `archive_command` failure must not stop writes; WAL accumulates; alert when disk over 70 percent.
* Disk full on VPS: `pg_wal` on same volume; set `max_wal_size 2GB` and monitor.
* PgBouncer transaction mode breaks `LISTEN/NOTIFY` and prepared statements: document; Electric and Hocuspocus connect directly.
* Coolify redeploy recreating the container must not lose data: named volume, tested.
* Time zone: cluster in UTC; app converts.
* Password rotation: procedure that updates Coolify env and reloads PgBouncer without downtime.
DEPS: `app-shell/vps-coolify-bootstrap` (hard: host, Coolify, tailnet, object storage for WAL archives, sops). Unblocks `app-shell/app-deploy-pipeline` (staging and production databases), `data-layer/local-first-sync` (logical replication), `realtime/yjs-server`, `identity/better-auth` on staging. Schema work itself starts on `data-layer/local-dev-stack`, not here.


## PAP-31 [P0 Research M prio1 Ready for Claude] Evaluate Zero, ElectricSQL, PowerSync and Replicache for local-first sync and write an ADR
key=data-layer/sync-research milestone=Postgres + Drizzle baseline agent=Researched by Scout (Library Evaluator) paired with Forge (S
blockedBy=[] blocks=['PAP-36']
GOAL: Confirm or overturn the plan's default of ElectricSQL + PGlite for local-first sync by benchmarking it against Zero, PowerSync and Replicache on PaperOS's real core entities, and record the decision as an ADR that `data-layer/local-first-sync` implements without further debate.
SCOPE: In:

* Rubric (weights agreed with Atlas): Postgres-native change capture, partial sync/shapes by tenant, offline writes and conflict model, RLS/permission story, bundle size, browser and Tauri WebView support, self-hostability and licence (per `libraries/license-policy`), maturity/maintenance, TypeScript ergonomics, cost of exit.
* Spike repo `spikes/sync-bench/` with a 10k-row `tasks` table under `tenant_id`, measuring: initial sync time for a 2k-row shape, incremental update latency (p50/p95), offline queue replay of 200 writes, memory footprint in Chrome and WebView, cold-start time on a mid-range Android emulator.
* Written evaluation of how each engine coexists with Yjs (documents) and with Postgres RLS.
* ADR `docs/adr/0004-local-first-sync.md`.

Out: production integration (that is `data-layer/local-first-sync`), CRDT text/canvas choice (`realtime/realtime-research`).
SPEC(first 1200): * Time-box: 1.5 agent-days total; each engine gets a spike no longer than 3 hours; unknowns become explicit rubric penalties rather than more research.
* Benchmark harness: Vitest bench plus Playwright for browser measurements; results written as JSON to `spikes/sync-bench/results/*.json` and rendered into a Markdown table by a script.
* Engines and versions to test: ElectricSQL 1.x (HTTP shapes) + PGlite 0.3; Zero (Rocicorp) current release with zero-cache; PowerSync self-hosted service + web SDK; Replicache with a custom push/pull server on oRPC.
* Evaluate permission enforcement path: does the engine respect RLS via a per-user Postgres role, require a proxy, or need its own rules language? Score accordingly, referencing `data-layer/rls-tenancy`.
* Include a "do nothing" baseline: TanStack Query with optimistic updates and a hand-rolled outbox.
* Decision criteria: engine must self-host in Docker on the existing VPS, be MIT/Apache/BSL-with-acceptable-terms, and support Tauri WebView.
* Deliver a migration-cost estimate from the winner to the runner-up (hours), to keep the exit door documented.
DOD:
* Spike code merged under `spikes/` (excluded from `turbo build`), results JSON and generated table committed.
* ADR with decision, scores, rejected options and re-open criteria approved by Atlas and Nova (comment on PR).
* Benchmark screenshots/recordings of the browser harness at 375 and 1280.
* `libraries/registry` entry drafted for the chosen engine (or an issue comment for Scout to add).
* CHANGELOG entry noting the decision; Linear comment linking the ADR and results table.
* `data-layer/local-first-sync` description updated with the exact libraries and versions chosen.
EDGE:
* Engine requires Postgres superuser or disables RLS: hard fail on rubric.
* Vendor cloud is easy but self-host is undocumented: score self-host only.
* Licence change risk (BSL/ELv2): record and require ADR re-open if terms change.
* Benchmark noise on shared CI runners: run three times, report median.
* PGlite in Tauri WebView on Android (WASM memory limits): test specifically.
* Shapes over 10k rows: note limits and pagination strategy.
DEPS: None; ready now. Blocks `data-layer/local-first-sync`; informs `realtime/record-sync`, `realtime/offline-queue`, `libraries/data-landscape`.


## PAP-32 [P0 Build M prio1 Backlog] Set up Drizzle ORM schema-as-code with migration workflow and seed scripts
key=data-layer/drizzle-schema milestone=Postgres + Drizzle baseline agent=Built by Forge (Schema Wright sub-agent). Reviewed by Sentin
blockedBy=['PAP-42'] blocks=['PAP-43', 'PAP-41', 'PAP-33']
GOAL: Make the database schema TypeScript: Drizzle ORM defines every table, `drizzle-kit` generates SQL migrations that run in CI and on deploy, and seed scripts give developers and tests a realistic multi-tenant dataset in seconds.
SCOPE: In:

* `packages/db/` with `drizzle-orm` 0.44.x, `drizzle-kit` 0.31.x, `postgres` (postgres.js) driver, `drizzle.config.ts`, `src/schema/index.ts` barrel, `src/client.ts` (pooled client factory taking a role and tenant context), `src/migrate.ts`.
* Migration workflow: `pnpm db:generate` (diff to `drizzle/*.sql` with `--name`), `pnpm db:migrate` (applies with `paperos_owner`), `pnpm db:check` fails CI if schema and migrations diverge, `pnpm db:studio`.
* Seeds: `src/seed/` using `drizzle-seed` with deterministic seeds; profiles `minimal` (1 tenant, 3 users), `demo` (3 tenants, 40 users, realistic names), `load` (50 tenants, 100k rows for `data-layer/observability`).
* CI job: spin Postgres via `ops/compose/dev.yml`, migrate from zero, seed `minimal`, run tests; also test migrate-from-previous-release to catch destructive changes.
* Deploy hook: Coolify pre-deploy command runs `pnpm db:mig
SPEC(first 1200): * `drizzle.config.ts`: `dialect:'postgresql'`, `schema:'./src/schema/*.ts'`, `out:'./drizzle'`, `casing:'snake_case'`, `migrations:{ table:'_migrations', schema:'public' }`, `strict:true`, `verbose:true`.
* Client factory `createDb({ role:'app'|'owner'|'readonly', tenantId?, actorId? })` returns a Drizzle instance whose every transaction runs `SET LOCAL app.tenant_id = $1; SET LOCAL app.actor_id = $2;` first (consumed by RLS later). Expose `withTenant(db, ctx, fn)`.
* Helper columns in `src/schema/_shared.ts`: `id()`, `tenantId()`, `timestamps()`, `softDelete()`, `jsonb<T>()`.
* Migration 0000 creates extensions, `uuid_generate_v7()`, `set_updated_at()` trigger function.
* Custom migration escape hatch: `drizzle/custom/*.sql` appended via `drizzle-kit generate --custom` for triggers and policies.
* Destructive-change guard: script parses generated SQL for `DROP TABLE|DROP COLUMN` and requires `ALLOW_DESTRUCTIVE=1`.
* Seeds are idempotent (upsert by deterministic UUID derived from `uuidv5(namespace, key)`).
DOD:
* From an empty database `pnpm db:migrate && pnpm db:seed --profile demo` completes under 30 s locally; CI job green.
* `pnpm db:check` fails when a schema edit lacks a migration (proven in a test commit).
* Vitest: client factory sets session vars; seed idempotency; destructive guard.
* Drizzle Studio screenshot at 1280 and 1920 showing seeded tables; terminal output screenshot of migration run.
* `packages/db/README.md` with workflow and conventions; ADR `0005-drizzle-conventions.md`; CHANGELOG; Linear comment with CI run link.
* Staging migrated via Coolify hook and logs attached.
EDGE:
* Two parallel agent branches both generate migration `0007`: CI rejects duplicate indices; doc the rebase-and-regenerate procedure (`forge/branch-policy`).
* Migration partially applied after crash: each file runs in a transaction; verify with a fault-injection test.
* Long-running migration locking a hot table: require `lock_timeout = '5s'` and `statement_timeout` in migrator session; document `CONCURRENTLY` index pattern.
* PgBouncer transaction mode and `SET LOCAL`: works because it is transaction-scoped; `SET` (session) is banned by lint rule.
* Seeds running against prod: refuse if `NODE_ENV=production` unless `--i-know`.
* Timezone-less `timestamp` columns: Biome/custom lint forbids; only `timestamptz`.
DEPS: `data-layer/local-dev-stack` (hard: provides `ops/compose/dev.yml`, the per-worktree database and CI service containers). `data-layer/postgres-provision` is soft (staging and production targets, wired by `app-shell/app-deploy-pipeline`). Unblocks `data-layer/core-entities`, `data-layer/data-dictionary`, `identity/better-auth` (Better Auth Drizzle adapter), `pm-linear/pm-data-model`, `business-core/finance-data-model`.


## PAP-33 [P0 Spec M prio1 Backlog] Model core platform entities: tenant, workspace, user, membership, role, audit_event, file
key=data-layer/core-entities milestone=Postgres + Drizzle baseline agent=Specified and built by Forge (Schema Wright) with Quill draf
blockedBy=['PAP-32'] blocks=['PAP-187', 'PAP-175', 'PAP-129', 'PAP-100', 'PAP-57', 'PAP-39', 'PAP-38', 'PAP-37', 'PAP-35', 'PAP-34']
GOAL: Model the seven shared entities every PaperOS app and every other project extends: `tenant`, `workspace`, `user`, `membership`, `role`, `audit_event` and `file`. This is a Spec issue: the output is the Drizzle schema files, the ER diagram, and the written contract other projects code against.
SCOPE: In:

* Drizzle tables in `packages/db/src/schema/core/*.ts` with relations, indexes, constraints and comments (Drizzle column `.comment()` where supported, otherwise `COMMENT ON` in custom migration for `data-layer/data-dictionary`).
* Zod schemas via `drizzle-zod` exported from `packages/db/src/zod/core.ts` (insert/select/update).
* ER diagram (Mermaid) and a data contract doc `docs/data/core-entities.md` stating invariants and ownership.
* Seed data for the entities in the `demo` profile.
* Interface notes for consumers: identity (Better Auth tables map onto `user`/`membership`), audiences (`identity/audience-model` adds `audience` tables referencing `membership`), files (`data-layer/file-storage`), audit (`data-layer/audit-log`).

Out: RLS policies (`data-layer/rls-tenancy`), API endpoints, UI, PM/finance/CRM entities (other projects).
SPEC(first 1200): * `tenant`: `id`, `slug` unique, `name`, `plan` (text, entitlements later), `settings jsonb`, `branding jsonb` (theme tokens for `design-system/theming`), timestamps, soft delete.
* `workspace`: `id`, `tenant_id`, `slug` unique per tenant, `name`, `kind` (`default|team|project`), `settings jsonb`; every tenant gets one default workspace via trigger.
* `user`: `id`, `email citext unique`, `name`, `avatar_file_id`, `locale`, `timezone`, `kind` (`human|agent|service`), `agent_character` nullable (name from `agents/character-schema`), `disabled_at`. Global, not tenant-scoped; Better Auth owns credentials in its own tables keyed to `user.id`.
* `membership`: `id`, `tenant_id`, `workspace_id` nullable (null = tenant-wide), `user_id`, `role_id`, `status` (`invited|active|suspended`), `invited_by`, unique `(tenant_id, workspace_id, user_id)`.
* `role`: `id`, `tenant_id` nullable (null = system role), `key`, `name`, `permissions jsonb` (array of `resource:action` strings; engine in `identity/rbac-abac`), `is_system`. System roles seeded: `owner`, `admin`, `staff`, `customer`, `agent`, `viewer`.
* `audit_event`: `id uuidv7`, `tenant_id`, `actor_user_id`, `actor_kind`, `action`, `entity_type`
DOD:
* Migration generated and applied on staging; `pnpm db:check` clean.
* Vitest: constraint tests (cross-tenant membership rejected, default workspace created, system role edit rejected).
* `drizzle-zod` schemas exported and snapshot-tested.
* ER diagram renders; contract doc reviewed by identity (Sentinel Security Auditor) and Quill.
* Drizzle Studio screenshot of seeded data at 1280 and 1920.
* CHANGELOG; ADR `0006-core-entities.md`; Linear comment linking doc and PR; consumers' issues (`identity/audience-model`, `data-layer/file-storage`, `data-layer/audit-log`) notified by comment.
EDGE:
* Email case and unicode: `citext` plus normalisation at API.
* User belongs to zero tenants (just signed up): allowed; UI handles onboarding.
* Deleting a tenant: soft delete cascades logically, hard purge is a separate job (`migration/export` first).
* Agent users without email: `email` nullable only when `kind <> 'human'` (CHECK).
* Audit partitions missing for a future month: `pg_partman` or a monthly cron creates 3 months ahead.
* File row exists but object missing: `status` reconciliation job in `data-layer/file-storage`.
DEPS: `data-layer/drizzle-schema` (hard). Coordinate with `identity/audience-model` and `identity/better-auth` (they extend `user`/`membership`). Unblocks `data-layer/rls-tenancy`, `data-layer/api-layer`, `data-layer/file-storage`, `data-layer/audit-log`, `data-layer/search`.


## PAP-34 [P0 Build M prio1 Backlog] Implement Postgres row-level security policies for multi-tenant isolation with a cross-tenant test harness
key=data-layer/rls-tenancy milestone=Postgres + Drizzle baseline agent=Built by Forge (Schema Wright). Reviewed by Sentinel (Securi
blockedBy=['PAP-33'] blocks=['PAP-59']
GOAL: Enforce tenant isolation inside Postgres with row-level security so that even a buggy agent-written query using the application role cannot read or write another tenant's rows, and prove it continuously with a cross-tenant test harness that any new table is automatically enrolled in.
SCOPE: In:

* RLS enabled and forced (`ENABLE` + `FORCE ROW LEVEL SECURITY`) on every table with a `tenant_id` column; policies generated from a single template.
* Session context contract: `app.tenant_id`, `app.actor_id`, `app.actor_kind`, `app.bypass` (owner-only) set via `SET LOCAL` by the client factory from `data-layer/drizzle-schema`.
* Policy generator `packages/db/src/rls/generate.ts` producing `drizzle/custom/00xx_rls.sql`: `tenant_isolation` (`USING tenant_id = current_setting('app.tenant_id')::uuid`) for SELECT/UPDATE/DELETE and `WITH CHECK` for INSERT/UPDATE; global tables (`user`, system `role`) get explicit read policies.
* Cross-tenant harness `packages/db/test/rls.harness.test.ts`: introspects `information_schema` for tenant tables, and for each attempts SELECT/INSERT/UPDATE/DELETE as tenant A against tenant B rows; expects zero rows/`42501` errors; fails if any table lacks RLS.
SPEC(first 1200): * Roles: `paperos_app` has `NOBYPASSRLS`; `paperos_owner` runs migrations and has `BYPASSRLS` only in the migrator connection; `paperos_readonly` subject to RLS.
* Missing context fails closed: policies use `current_setting('app.tenant_id', true)` and `COALESCE(...,'00000000-0000-0000-0000-000000000000')::uuid` so no context means no rows.
* Global tables policy: `user` readable when the user shares a tenant with the actor (EXISTS on `membership`) or is the actor; system roles readable by all.
* Cross-tenant admin (platform staff) uses `app.bypass = 'on'` only through an audited API path (`data-layer/audit-log` records it) and only with the owner role.
* Electric replication role reads with RLS bypassed but shapes filtered by `tenant_id` (documented handoff to `data-layer/local-first-sync`).
* Generator is idempotent and re-runnable (`DROP POLICY IF EXISTS` then `CREATE`).
* Doc `docs/data/tenancy.md`: context contract, how to add a table, how to add a custom policy, bypass rules.
DOD:
* Harness passes on all core tables and fails when a test table is added without a policy (demonstrated in PR).
* Vitest: fail-closed with no context; bypass only with owner role; `EXPLAIN` uses index.
* pgTAP or SQL-level tests for policies committed in `packages/db/test/sql/`.
* Security Auditor sign-off comment on PR.
* Screenshot of harness output and `\d+` showing policies (terminal, 1280).
* `docs/data/tenancy.md`; ADR `0007-rls-tenancy.md`; CHANGELOG; Linear comment with CI run.
EDGE:
* Table with `tenant_id` nullable (system-wide records): policy must handle NULL explicitly, never leak.
* Views and materialised views: `security_invoker = true` required; lint enforces.
* Functions with `SECURITY DEFINER`: banned except in `paperos` schema reviewed by Security Auditor.
* Bulk COPY/import (`migration/import-framework`) needs owner role with explicit `app.tenant_id`.
* `INSERT ... ON CONFLICT` across tenants must fail, not update.
* Partitioned `audit_event`: policies applied on parent propagate; verify on each partition.
DEPS: `data-layer/core-entities` (hard). Consumed by `identity/rbac-abac`, `identity/permission-tests`, `data-layer/api-layer` (context setting), `data-layer/local-first-sync`, `quality/security-scans`.


## PAP-35 [P0 Build L prio1 Backlog] Expose a typed API via oRPC with Zod schemas generated from Drizzle
key=data-layer/api-layer milestone=Postgres + Drizzle baseline agent=Built by Forge. Reviewed by Sentinel (Code Reviewer and Secu
blockedBy=['PAP-33'] blocks=['PAP-163', 'PAP-119', 'PAP-40', 'PAP-36']
GOAL: Expose the database through a typed RPC layer with oRPC so React hooks, Tauri clients and agents share one contract: Zod input/output schemas derived from Drizzle, OpenAPI generated for external callers, and every procedure running inside the tenant context that RLS expects.
SCOPE: In:

* `apps/api/` Node 22 server (Hono 4 adapter) hosting oRPC 1.x routers, deployed as a Docker service on the VPS via Coolify (`ops/compose/api.yml`).
* `packages/api-contract/` with routers, Zod 4 schemas (from `drizzle-zod` in `data-layer/core-entities` plus hand-written DTOs), and the inferred `RouterClient` type.
* `packages/api-client/`: browser/Tauri client with `@orpc/client` fetch link, `@orpc/tanstack-query` utils, auth header injection, request id, retry policy.
* Middleware chain: request id, logging, auth (Better Auth session -> `actor`), tenant resolution (header `x-tenant` or subdomain), `withTenant` DB context, error mapping, audit hook (`data-layer/audit-log`), OTel span (`data-layer/observability`).
* Core routers: `tenants`, `workspaces`, `users.me`, `memberships`, `roles`, `files` (stubs completed by `data-layer/file-storage`), `health`.
* OpenAPI 3.1 doc served at 
SPEC(first 1200): * Procedure convention: `router.<entity>.<verb>` with verbs `list`, `get`, `create`, `update`, `archive`; list inputs `{ cursor?, limit<=100, filter?, sort? }` returning `{ items, nextCursor }`.
* Errors: `ORPCError` codes `UNAUTHORIZED`, `FORBIDDEN`, `NOT_FOUND`, `CONFLICT`, `VALIDATION`, `RATE_LIMITED`, `INTERNAL`; RLS denials surface as `NOT_FOUND` for reads and `FORBIDDEN` for writes.
* Context type: `{ requestId, actor: { id, kind, tenantId, roles[] } | null, db, tenantId, log, span }`.
* Rate limit per actor: 600/min default via in-memory token bucket now, Redis later.
* Client hooks: `orpc.users.me.queryOptions()`, `orpc.tenants.list.infiniteOptions()`; SSR-free.
* Test utilities `packages/api-contract/test/` providing `callAs(actorFixture)`.
* Deployment: health endpoint `/api/health` checks DB and returns build SHA; graceful shutdown; env from `serverEnvSchema` (`app-shell/env-config`).
* API versioning: path prefix `/api/v1`; breaking changes require ADR.
DOD:
* `apps/api` deployed to staging; `/api/health` and `/api/docs` reachable over TLS.
* Vitest: middleware chain, error mapping, every core router happy path and forbidden path through `callAs`; contract type test that a client call with a wrong input fails typecheck.
* `pnpm gen:api` stale check green; OpenAPI validated with `@redocly/cli lint`.
* Web `apps/web` renders `users.me` on the dashboard example route; screenshots at 375, 1024, 1920 including Scalar docs page.
* `docs/data/api.md` (conventions, adding a router, client usage); CHANGELOG; Linear comment with staging docs URL.
EDGE:
* Missing tenant header on a tenant-scoped call: 400 with clear message, never default to first tenant.
* Actor member of several tenants: header required; `users.me` lists tenants.
* Payload above 1 MB: reject 413; file uploads never pass through RPC.
* Clock skew and retries on non-idempotent `create`: idempotency key header stored 24 h.
* Zod schema drift from Drizzle after a migration: CI stale check catches it.
* Slow query above 2 s: cancelled via `statement_timeout` and reported to observability.
DEPS: `data-layer/core-entities` (hard), `data-layer/rls-tenancy` (context contract), `identity/better-auth` (session verification; stub with a signed dev token until merged), `app-shell/env-config`. Unblocks `data-layer/local-first-sync`, `data-layer/observability`, `spec-builder/data-section`, `pm-linear/linear-sync`, all business routers.


## PAP-36 [P1 Build L prio1 Backlog] Integrate PGlite and ElectricSQL shapes for local-first reads with an offline write queue
key=data-layer/local-first-sync milestone=Local-first sync working agent=Built by Forge with Nova (CRDT Engineer) pairing on the outb
blockedBy=['PAP-31', 'PAP-35'] blocks=['PAP-143']
GOAL: Give every target instant, offline-capable reads and queued writes: the engine chosen in `data-layer/sync-research` (default ElectricSQL shapes + PGlite) streams tenant-scoped shapes into a local database in the browser or Tauri WebView, React hooks read locally, and writes go to the oRPC API through an outbox that replays when connectivity returns.
SCOPE: In:

* `packages/sync/`: shape definitions (`defineShape(table, where, columns)`), `SyncClient` lifecycle (start/stop/reset), `useShape()` and `useLiveQuery()` hooks over PGlite live queries, `Outbox` for writes.
* Electric sync service deployed via Coolify (`ops/compose/electric.yml`) connected directly to Postgres with the `electric` replication role; shapes gated by an auth proxy route in `apps/api` (`/api/sync/shape`) that validates the session and injects `tenant_id = <actor tenant>` into the `where` clause so clients cannot request other tenants' data.
* PGlite 0.3 with IndexedDB persistence in browsers and file persistence in Tauri (`apps/desktop` data dir), schema mirrored from Drizzle via a generated `pglite-schema.sql`.
* Outbox: local `_outbox` table `{ id uuidv7, procedure, input jsonb, created_at, attempts, last_error, status }`; optimistic local mutation applied to PGlite, 
SPEC(first 1200): * Shapes for core entities: `workspaces`, `memberships` (own tenant), `users` (members of tenant, limited columns), `files` (metadata only). Additional projects register shapes in their packages.
* Shape proxy: `GET /api/sync/shape?table=&offset=&handle=&live=` forwards to Electric with server-set `where`; deny tables not in the registry; response streamed.
* PGlite schema generation: `pnpm gen:pglite` produces `packages/sync/generated/schema.sql` from Drizzle (tables in shape registry only); versioned with a hash; mismatch triggers reset.
* Write path: `mutate(orpc.tasks.update, input, { optimistic: (db) => ... })`; when online and outbox empty, call directly; otherwise enqueue.
* Replay: exponential backoff 1s..60s, max 20 attempts, then `status:'failed'` with UI to retry/discard.
* Storage limits: warn when local DB above 200 MB; shapes support `columns` to trim.
* Tauri: PGlite via Node-less WASM in WebView; on Android fall back to memory + IndexedDB per sync-research findings.
DOD:
* Demo route `/_app/sync-demo` lists workspaces from PGlite; editing a name offline, reloading, going online replays the write (Playwright test with `setOffline`; recording).
* Cross-tenant shape request through the proxy returns 403 (test).
* Vitest: outbox state machine, backoff, schema-hash reset; bench of initial shape load for 2k rows under 1.5 s on CI runner.
* Electric deployed on staging; health checked from `/api/health`.
* Screenshots of `<SyncIndicator/>` states at 375, 768, 1280, 1920 and of the demo route at all 7 widths.
* `docs/data/sync.md`; CHANGELOG; Linear comment with recording and preview URL.
EDGE:
* Two tabs both replaying the outbox: leader election via `navigator.locks`.
* Server rejects replayed write with `FORBIDDEN` (permission changed while offline): mark failed, surface reason, roll back optimistic row.
* Shape handle expired after long offline: full re-fetch, preserve outbox.
* IndexedDB blocked (Safari private mode): fall back to in-memory PGlite with banner.
* Deleted rows while offline: tombstones arrive via shape; local rows removed; outbox writes to them fail cleanly.
* Clock skew affecting `updated_at` comparisons: server timestamps only.
DEPS: `data-layer/api-layer` and `data-layer/sync-research` (hard), `data-layer/rls-tenancy` (proxy semantics), `data-layer/postgres-provision` (logical replication on). Unblocks `realtime/record-sync`, `realtime/offline-queue`, `tables/query-compiler` (local execution), `app-shell/linux-kiosk` resilience.


## PAP-37 [P1 Build M prio2 Backlog] Add S3-compatible object storage (MinIO) with signed uploads and image variants
key=data-layer/file-storage milestone=Local-first sync working agent=Built by Forge (Ops Runner for MinIO, core for service). Rev
blockedBy=['PAP-43', 'PAP-33'] blocks=['PAP-185']
GOAL: Let any app accept files safely: a MinIO S3-compatible bucket per environment, presigned direct-to-storage uploads from browser and native targets, server-side validation, automatic image variants (thumbnails, WebP/AVIF) and signed download URLs that respect tenancy.
SCOPE: In:

* MinIO deployed via Coolify (`ops/compose/minio.yml`) with buckets `paperos-prod`, `paperos-staging`, `pg-backups` (from `data-layer/postgres-provision`), versioning on, lifecycle rule purging `pending` objects after 24 h; TLS via Caddy; console restricted to VPN.
* `packages/files/` server: `files.createUpload` (returns presigned PUT, key, file row `status:'pending'`), `files.complete` (HEAD object, verify size and sha256, sniff MIME with `file-type`, set `ready`, enqueue variants), `files.getUrl` (presigned GET 15 min), `files.delete` (soft delete + lifecycle purge), `files.list` — all as oRPC procedures in `data-layer/api-layer`.
* Variants worker: in-process queue (pg-boss 10.x on Postgres) generating `thumb 256`, `md 1024`, `lg 2048` as WebP and AVIF with `sharp` 0.34; stored under `variants/<id>/<name>.<ext>`; `file.variants` JSON updated.
* Client `packages/files/client`: `u
SPEC(first 1200): * Key layout: `<tenant_id>/<yyyy>/<mm>/<file_id>/<sanitised-filename>`; never trust client filename for key; `Content-Disposition` set on GET.
* Presign with `@aws-sdk/client-s3` + `@aws-sdk/s3-request-presigner` against MinIO endpoint; `x-amz-checksum-sha256` required on PUT.
* `files.complete` rejects mismatched size/sha256, disallowed MIME (server-sniffed, not header), and files whose row is not `pending` for this actor.
* Variant generation only for `image/*` up to 50 MP; SVG stored as-is but served with `Content-Type: image/svg+xml` and `Content-Security-Policy: sandbox`.
* EXIF stripped from variants; original retained.
* Reconciliation job nightly: rows `ready` without object -> `failed`; objects without rows -> quarantined prefix.
* Download URLs generated per request after RLS-scoped row fetch, so tenancy is enforced by the row lookup.
* Audit: every create/complete/delete emits `audit_event` via `data-layer/audit-log`.
DOD:
* Upload a 5 MB JPEG from web and from Android emulator camera; variants appear within 10 s; recording attached.
* Multipart resume test: pause at 60 percent, reload, resume, complete (Playwright).
* Vitest: presign params, complete validation (size, hash, MIME), key sanitisation, variant queue; integration test against MinIO in CI compose.
* Cross-tenant `getUrl` returns `NOT_FOUND` (test).
* Screenshots of `<FileDrop/>` idle, dragging, progress, error, done at 375, 768, 1280, 1920.
* `docs/data/files.md`; CHANGELOG; Linear comment with recording and staging console screenshot.
EDGE:
* Filename with path traversal or unicode control chars: sanitised to safe slug plus extension.
* Zero-byte file: rejected.
* Same content uploaded twice: allowed, but `sha256` index enables dedupe UI later.
* HEIC from iPhone: converted to JPEG variants; original kept.
* MinIO down during `complete`: procedure returns 503 with retry-after; client retries with backoff.
* Presigned URL leaked: 15-minute expiry; documents that download URLs are bearer secrets.
DEPS: `data-layer/core-entities` (file table), `data-layer/api-layer` (procedures), `data-layer/audit-log` (soft), `app-shell/tauri-mobile` (camera path, soft). Consumed by `collab/comments` (attachments), `collab/screenshot-annotations`, `design-system/theming` (logo upload), `growth/*`.


## PAP-38 [P1 Build M prio2 Backlog] Build append-only audit log with actor (human or agent), diff and reason fields
key=data-layer/audit-log milestone=Local-first sync working agent=Built by Forge (Schema Wright) with Iris (Component Crafter)
blockedBy=['PAP-33'] blocks=['PAP-61']
GOAL: Record every mutation in the platform as an immutable `audit_event` with who (human or agent), what changed (before/after/diff), why (a reason string agents must supply), and the request/session that caused it, so Justin can answer "who changed this and why" for any row and reviewers can trace agent behaviour to data.
SCOPE: In:

* Append-only guarantees: table owned by `paperos_owner`; `paperos_app` has INSERT and SELECT only; triggers reject UPDATE/DELETE; monthly partitions with 24-month retention and archival to MinIO as Parquet (`data-layer/file-storage` bucket).
* Capture mechanism: Postgres trigger-based capture on every tenant table (generic `paperos.audit_trigger()` reading `app.actor_id`, `app.actor_kind`, `app.request_id`, `app.reason` session vars) so writes from any path (API, sync replay, imports) are logged; API middleware sets the vars (`data-layer/api-layer`).
* Diff computation in the trigger via `jsonb` comparison producing `{ field: { from, to } }`, excluding `updated_at`, and redacting columns listed in a `paperos.audit_redactions` table (e.g. `password_hash`, tokens).
* `audit.list` and `audit.forEntity` oRPC procedures with cursor pagination and filters (actor, action, entity type, dat
SPEC(first 1200): * Trigger attached automatically by the RLS generator (`data-layer/rls-tenancy`) to every table with `tenant_id`; opt-out list for high-churn tables (e.g. presence) in `packages/db/src/audit/exclusions.ts`.
* Event `action` values: `insert|update|delete|restore|bypass_read` (bypass reads logged by API when `app.bypass` is on).
* Partition management: `pg_partman` if available in the image, else a monthly cron function creating partitions 3 months ahead; tests verify next-month partition exists.
* Archival job: monthly, copies partitions older than 24 months to `audit/<yyyy>/<mm>.parquet` via `duckdb` in a worker, then detaches and drops after checksum verify.
* Hash chain: each event stores `prev_hash` and `hash = sha256(prev_hash || canonical json)` per tenant to detect tampering; verification script `pnpm audit:verify`.
* Performance: trigger adds under 15 percent overhead on a 10k-row bulk update (bench); bulk imports may set `app.audit_mode = 'summary'` to write one event per batch.
DOD:
* Every write through the API to a seeded tenant produces an event with correct actor, diff and request id (integration test).
* UPDATE/DELETE on `audit_event` as `paperos_app` fails (test); hash chain verification passes and detects a tampered row in a test.
* Agent mutation without reason rejected (test); human allowed.
* `<AuditTrail/>` on the settings example page; screenshots at 375, 768, 1024, 1280, 1920 with light/dark.
* Bench results committed; partition creation test.
* `docs/data/audit.md`; CHANGELOG; Linear comment with preview URL.
EDGE:
* Large `jsonb` columns (documents) produce huge diffs: cap stored `before/after` at 64 KB each and store a `truncated` flag plus hash.
* Cascading deletes generate many events in one transaction: all share `request_id`; UI groups them.
* Actor context missing (cron job): `actor_kind = 'system'`, `actor_id` null, `reason` = job name; never silent.
* Timezone display: stored UTC, rendered in viewer's timezone with absolute tooltip.
* Redaction list changes later: historical events not rewritten; documented.
* Partition for current month missing after restore: trigger falls back to default partition and alerts.
DEPS: `data-layer/core-entities` (table), `data-layer/rls-tenancy` (trigger attachment), `data-layer/api-layer` (context vars). Consumed by `identity/impersonation`, `identity/agent-principals`, `collab/prompt-log-store`, `business-core/ledger`, `agents/prompt-logging-hook`.


## PAP-39 [P1 Build M prio2 Backlog] Add full-text and vector search (tsvector + pgvector) over any entity through a search registry
key=data-layer/search milestone=Local-first sync working agent=Built by Forge (Schema Wright) with Nova consulting on hook 
blockedBy=['PAP-43', 'PAP-33'] blocks=['PAP-138']
GOAL: Provide one search API over any entity: packages register searchable fields once, Postgres keeps a `tsvector` and (optionally) a `pgvector` embedding up to date, and a single `search.query` procedure returns ranked, tenant-scoped, permission-filtered results that the command bar, knowledge search and table filters all reuse.
SCOPE: In:

* Search registry `packages/search/src/registry.ts`: `registerSearchable({ entity, table, titleField, bodyFields[], facets[], weight, embed: boolean, route: (row) => href })`; core entities registered: `workspace`, `user` (name/email), `file` (filename, metadata).
* Storage: a central `search_document` table (`tenant_id`, `entity_type`, `entity_id`, `title`, `body`, `tsv tsvector generated`, `embedding vector(1024)` nullable, `facets jsonb`, `updated_at`) with GIN on `tsv`, HNSW on `embedding`, `pg_trgm` GIN on `title` for fuzzy; RLS as any tenant table.
* Indexing: triggers on source tables call `paperos.search_upsert(entity_type, id)` which builds the document via per-entity SQL functions generated from the registry; a pg-boss job computes embeddings asynchronously via a provider interface (`EmbeddingProvider`: `openai-compatible` default pointing at a self-hosted `text-embeddings
SPEC(first 1200): * Language: `english` config default; per-tenant `settings.search.language` used in generated function.
* Body field length cap 100 KB per document; larger bodies truncated with flag.
* Embeddings: 1024-dim default (bge-m3 or `text-embedding-3-small` at 1024); model name stored per row so mixed models are never compared; reindex when model changes.
* Latency targets on `load` seed (100k docs): keyword p95 under 80 ms, hybrid p95 under 250 ms; bench committed.
* Facets: `jsonb` containment filters, e.g. `{ status: 'active' }`; counts returned for the top 5 facet values per key.
* Deleted/soft-deleted rows remove their document (trigger on `deleted_at`).
* Registry validation at boot fails if a registered field does not exist (typecheck via Drizzle types plus runtime check).
DOD:
* Searching "acme" on demo seed returns the Acme workspace and its members ranked sensibly; typo "acmee" still finds it (trigram); recording attached.
* Semantic mode returns relevant results with the local embedding container on staging (or documented paid provider).
* Vitest: registry validation, query builder, RRF fusion; integration test for triggers and permission post-filter (cross-tenant never appears).
* Bench results at 100k docs committed.
* `<SearchResults/>` screenshots at 375, 768, 1280, 1920 including empty and error states.
* `docs/data/search.md` (how to register an entity); CHANGELOG; Linear comment with preview URL.
EDGE:
* Empty or whitespace query: return recent items instead of error.
* Queries with only stop words: trigram path.
* Non-English content in an `english` config: documented limitation; `simple` config fallback per tenant.
* Embedding provider down: keyword results still return; job retries.
* Entity registered twice by two packages: boot error naming both.
* Massive bulk import: triggers batch via `app.search_mode = 'deferred'` and a reindex afterwards.
DEPS: `data-layer/core-entities` (hard), `data-layer/rls-tenancy`, `data-layer/api-layer`, `identity/rbac-abac` (post-filter; stub allow-all until merged). Consumed by `collab/knowledge-search`, `input/command-registry`, `tables/filter-sort-group-ui`, `growth/crm-views`.


## PAP-40 [P2 Infra M prio2 Backlog] Wire OpenTelemetry tracing, slow-query logging and Grafana dashboards for API and sync
key=data-layer/observability milestone=Tenant-safe and observable agent=Built by Forge (Ops Runner). Reviewed by Sentinel (Code Revi
blockedBy=['PAP-35'] blocks=[]
GOAL: Make latency and errors visible per route, per tenant and per agent: OpenTelemetry traces from the web client through the API to Postgres, slow-query logging, and Grafana dashboards on the VPS that reviewers and the release digest can link to, so performance regressions are seen before customers report them.
SCOPE: In:

* Observability stack via Coolify (`ops/compose/observability.yml`): Grafana 11, Prometheus, Loki, Tempo, OpenTelemetry Collector (OTLP gRPC/HTTP), `postgres_exporter` (from `data-layer/postgres-provision`), `node_exporter`, cAdvisor; all behind Caddy with Better Auth SSO or Grafana OAuth when `identity/better-auth` lands, VPN-only until then.
* API instrumentation: `@opentelemetry/sdk-node` 2.x with auto-instrumentations for HTTP, `pg`/postgres.js, `undici`; oRPC middleware creating a span per procedure with attributes `paperos.tenant_id`, `paperos.actor_kind`, `paperos.actor_id`, `paperos.procedure`, `paperos.request_id`, `linear.issue` when supplied by agents.
* Web/Tauri instrumentation: `@opentelemetry/sdk-trace-web` with fetch instrumentation and `traceparent` propagation to the API; Web Vitals (LCP, INP, CLS) exported as metrics; sampled 10 percent in prod, 100 percent in sta
SPEC(first 1200): * Env: `OTEL_EXPORTER_OTLP_ENDPOINT`, `OTEL_SERVICE_NAME`, `OTEL_TRACES_SAMPLER=parentbased_traceidratio`, `OTEL_TRACES_SAMPLER_ARG` per env (`app-shell/env-config`).
* Request id equals trace id where possible; API returns `x-request-id` and `traceparent` headers; error toasts show the short id for support.
* PII policy: never attach emails, names or payload bodies to spans; tenant and actor ids only; enforced by a span processor that drops disallowed attribute keys and a test.
* Retention: Tempo 7 days, Loki 14 days, Prometheus 30 days on the 8 GB box; documented sizing.
* Load profile: run the `load` seed plus a k6 script `ops/observability/k6/api-smoke.js` (200 VUs, 5 min) on staging to validate dashboards populate and alerts fire under induced errors.
DOD:
* A trace from a click in the web app to a Postgres query appears in Tempo with tenant attributes (screenshot).
* All six dashboards provisioned from JSON on a fresh Grafana (no manual clicks); screenshots at 1280 and 1920.
* Induced 5xx storm fires the error alert and creates a Linear issue or email (evidence attached).
* Vitest: PII attribute filter, request id propagation; k6 run summary committed.
* Web Vitals from the Pages demo visible bucketed by breakpoint.
* `docs/ops/observability.md`; CHANGELOG; Linear comment with Grafana links (VPN note).
EDGE:
* Collector down: SDK must not block requests; batch exporter with drop-on-full queue.
* High-cardinality attributes (request id as a metric label): forbidden in metrics, allowed in traces; lint test.
* Ad blockers blocking browser OTLP export: send via API proxy path `/api/otel` instead.
* Clock skew between VPS and clients: spans use server-received time for ordering in dashboards.
* Disk pressure from logs: Loki retention plus Docker log rotation.
* Sampling hiding rare errors: always sample when span has error status (tail-based via collector).
DEPS: `data-layer/api-layer` (hard), `data-layer/postgres-provision` (exporter). Consumed by `quality/perf-budgets`, `quality/release-train` (digest links), `realtime/load-test`, `pm-linear/credit-metering` (agent attribution), `agents/cost-controls`.


## PAP-41 [P2 Docs S prio3 Backlog] Generate a living data dictionary from the Drizzle schema into the docs system
key=data-layer/data-dictionary milestone=Tenant-safe and observable agent=Built by Quill (Spec and Documentation Lead) with Forge (Sch
blockedBy=['PAP-128', 'PAP-32'] blocks=[]
GOAL: Generate a living data dictionary from the Drizzle schema so anyone (Justin, agents, future staff) can browse every table, column, relation, index, RLS policy and audit setting inside the product's docs engine, with descriptions kept next to the code and regenerated on every merge.
SCOPE: In:

* Generator `packages/db/src/dictionary/generate.ts`: introspects Drizzle schema objects (tables, columns, types, defaults, relations, indexes, checks) plus live database metadata via `information_schema`/`pg_policies`/`pg_trigger` on a migrated dev database, merges column comments and a `dictionary.yaml` sidecar for prose, emits `docs/data/dictionary/*.md` (one page per table) and `dictionary.json`.
* Content per table: purpose, owner project (from a `@owner` tag in schema file comments), columns table (name, type, nullable, default, description, PII flag), relations (in/out), indexes, RLS policies with SQL, audit inclusion, search registration, seeds present, linked issues.
* ER diagrams: Mermaid `erDiagram` per domain (core, identity, pm, finance, crm) and a whole-schema diagram.
* Docs engine integration (`collab/docs-engine`): pages carry front-matter (`title`, `owner`, `genera
SPEC(first 1200): * `dictionary.yaml` schema: `tables.<name>.description`, `tables.<name>.columns.<col>.{description, pii: boolean, example}`; validated with Zod; unknown keys fail.
* PII flags feed the OTel attribute filter (`data-layer/observability`) and the audit redaction table (`data-layer/audit-log`) through a generated `pii.json`, making the dictionary the single source for sensitivity.
* Diagram grouping via `@domain` tag; cross-domain relations drawn dashed.
* Output is deterministic (sorted keys) to keep diffs small.
* `dictionary.json` shape: `{ generatedAt, schemaHash, tables: [{ name, domain, owner, description, columns:[...], relations:[...], indexes:[...], policies:[...], audited, searchable }] }` consumed by `spec-builder/data-section` to validate that page specs reference real tables and columns.
* Rendering component `<DataDictionaryTable/>` uses the design system table (`design-system/data-display`) for column lists, with anchors per column for deep links from specs.
DOD:
* Dictionary generated for all tables existing at merge time; 100 percent description coverage for core entities.
* `--check` stale detection proven in PR; schema-change PR comment appears on a test PR.
* Vitest: YAML validation, determinism (two runs identical), PII export, Mermaid output snapshot.
* Rendered pages in the docs engine at 375, 768, 1024, 1280, 1920 (screenshots), including one table page and the ER diagram.
* `pii.json` consumed by observability filter test.
* `docs/data/dictionary/README.md` on maintaining descriptions; CHANGELOG; Linear comment with in-app docs link.
EDGE:
* Table exists in database but not in Drizzle (e.g. Better Auth or pg-boss internal tables): listed under "External" with a note, not an error.
* Enum types and arrays render readable types.
* Partitioned tables list the parent only, with partition strategy noted.
* Views and materialised views included with their definition SQL.
* Column renamed: YAML key mismatch fails with suggestion of the nearest name.
* Very wide tables (80+ columns): page collapses groups by prefix.
DEPS: `data-layer/drizzle-schema` and `collab/docs-engine` (hard). Soft: `data-layer/rls-tenancy` (policies), `data-layer/audit-log`, `data-layer/search`, `design-system/data-display`. Consumed by `spec-builder/data-section`, `migration/import-framework` (mapping targets), `agents/character-docs`.


## PAP-42 [P0 Infra S prio1 Backlog] Ship the local dev stack: docker compose with Postgres 17, MinIO, Mailpit and Hocuspocus, per-worktree databases and a SessionStart hook so parallel Claude sessions never share state
key=data-layer/local-dev-stack milestone=Postgres + Drizzle baseline agent=Built by Forge (Platform Engineer). Reviewed by Sentinel (Co
blockedBy=['PAP-13'] blocks=['PAP-32']
GOAL: Give every Claude Code session, every CI job and Justin's laptop an identical, disposable backing stack in one command, so that the dozens of parallel sessions this plan relies on never collide on a shared database. `data-layer/drizzle-schema` already references `ops/compose/dev.yml` for its CI job and `libraries/backend-landscape` scores libraries on their `docker compose up` story, but no issue creates that file or the isolation rules. This issue does, and it is the reason `data-layer/drizzle-schema` no longer needs the production VPS before it can start.
SCOPE: In:

* `ops/compose/dev.yml`: `postgres` (`pgvector/pgvector:pg17`, `wal_level=logical` for Electric later, init script creating roles `paperos_owner`, `paperos_app`, `electric`), `minio` (S3 API on 9000, console on 9001, bucket `paperos-dev` created by an init job), `mailpit` (SMTP 1025, UI 8025, used by `identity/better-auth` magic links locally), `hocuspocus` placeholder service enabled by profile `--profile realtime` once `realtime/yjs-server` publishes an image; profiles `core`, `realtime`, `sync` (Electric), `full`.
* `pnpm stack up|down|reset|logs` scripts in `packages/config-scripts` wrapping compose with the project name derived from the git worktree: `paperos-<branch-slug>` so two worktrees run two stacks on different host ports (port offset derived from a hash of the branch, printed on `up`).
* Per-worktree database: `DATABASE_URL` written to `.env.local` by `pnpm stack up`; d
SPEC(first 1200): * Host ports: base 5432/9000/9001/8025/1234 plus `offset = hash(branch) % 50 * 100`; the offset is deterministic so a session can reconnect after restart.
* Compose project name and DB name are derived by `packages/config-scripts/src/worktree.ts` (`git rev-parse --abbrev-ref HEAD`, slugified, max 40 chars); `main` maps to offset 0.
* Data volumes are per project name, so `pnpm stack down` keeps data and `pnpm stack reset` removes it; `pnpm stack prune` removes stacks for branches that no longer exist.
* `pnpm stack up` completes in under 60 s on a warm image cache and waits for `pg_isready` before returning.
* Seeds come from `data-layer/drizzle-schema` when present; until then the hook prints "no migrations yet" and succeeds.
* The hook is safe to run concurrently (flock on `.stack.lock`).
DOD:
* Two worktrees on different branches run `pnpm stack up` simultaneously and each connects to its own database on different ports (terminal transcript attached).
* Fresh clone plus `pnpm i && pnpm stack up && pnpm test` passes with zero manual steps on Linux and macOS (GitHub Actions matrix log for Linux; macOS run recorded once).
* Claude Code session started in a worktree shows the hook output and can run `pnpm db:migrate` immediately (screenshot of the session start).
* `ci-services.yml` used by at least one Vitest job hitting Postgres.
* Mailpit shows a message sent by a smoke test through `SMTP_URL` (screenshot).
* `docs/dev/local-stack.md`, `CHANGELOG.md` entry, Linear comment.
EDGE:
* Docker not installed or daemon down (common in a fresh Claude Code web session): hook prints install instructions and the option `PAPEROS_STACK=remote` to use the shared staging database read-only; tests requiring a database are skipped with a visible warning, not silently passing.
* Port collision with an unrelated local service: `pnpm stack up --offset <n>` override, persisted in `.env.local`.
* Branch names with slashes and unicode: slug function tested; collisions after truncation append a 4-char hash.
* Apple Silicon: `pgvector/pgvector:pg17` is multi-arch; verify `minio` and `mailpit` tags are too.
* Stale volumes from many branches filling disk: `pnpm stack prune` and a note in the session playbook's end-of-session checklist.
* CI service containers do not support compose profiles: the reusable workflow lists services explicitly and asserts the env names match `dev.yml` via a un
DEPS: `app-shell/monorepo-scaffold` (scripts folder, `.claude/` folder). Unblocks `data-layer/drizzle-schema` (which no longer waits for the VPS), `identity/better-auth` (Mailpit), `data-layer/file-storage` (MinIO), `realtime/yjs-server` (local profile), `quality/ci-gate1` (service containers), `pm-linear/session-playbook` (hook behaviour). Soft: `app-shell/env-config` for env names.


## PAP-43 [P1 Build M prio1 Backlog] Build the background jobs and scheduler package (pg-boss) with retries, idempotency keys, cron, dead-letter queue and an admin view
key=data-layer/jobs-queue milestone=Local-first sync working agent=Built by Forge (Platform Engineer). Reviewed by Sentinel (Co
blockedBy=['PAP-214', 'PAP-32'] blocks=['PAP-205', 'PAP-199', 'PAP-194', 'PAP-191', 'PAP-190', 'PAP-174', 'PAP-136', 'PAP-39', 'PAP-37']
GOAL: Provide the one background-work runtime that eight later issues already assume by name (`data-layer/file-storage` variants worker, `data-layer/search` indexing, `collab/notifications` delivery, `growth/social-scheduler`, `growth/outreach-sequences`, `growth/attribution` rollups, `migration/import-framework`, `migration/export`) but none owns. `libraries/backend-landscape` decides between pg-boss, Graphile Worker, Inngest and [Trigger.dev](<http://Trigger.dev>); this issue implements the winner (default pg-boss, Postgres-native, no Redis) as `packages/jobs` with the guarantees those consumers need: at-least-once delivery, idempotent handlers, ordered retries, cron, and visibility for staff.
SCOPE: In:

* `packages/jobs/`: `defineJob({ name, schema (Zod), handler, retry, concurrency, singletonKey })` registry; typed `enqueue(job, input, { idempotencyKey, runAt, priority, tenantId })`; `schedule(job, cron, input)`; worker entry `apps/worker` (own Dockerfile through `app-shell/app-deploy-pipeline`) that loads every registered job from packages.
* pg-boss 10.x on the application Postgres in schema `jobs`; tenant context and actor propagated into the handler so `data-layer/audit-log` records `actor_kind = 'system'` with the job name as reason.
* Idempotency: `idempotencyKey` maps to pg-boss `singletonKey` for enqueue-dedup plus a `jobs.idempotency` table for handler-side exactly-once effects (`withIdempotency(key, fn)`).
* Retry policy defaults: 5 attempts, exponential backoff 10 s to 10 min; per-job override; poison messages land in `jobs.dead_letter` with input and last error; requeu
SPEC(first 1200): * Job names are `domain.action` (`files.variants`, `search.upsert`, `notify.deliver`, `outreach.step`, `import.chunk`); the registry rejects duplicates at boot.
* Payloads validated with the job's Zod schema on enqueue and on dequeue (schema drift after a deploy fails safe into dead-letter, not a crash).
* Per-tenant concurrency: `concurrency: { perTenant: n }` implemented with pg-boss `singletonKey = tenantId` groups; documented limits.
* Graceful shutdown: worker drains for up to 30 s on SIGTERM (Coolify redeploys), unfinished jobs return to the queue.
* Clock: `runAt` and cron evaluated in UTC; tenant timezone conversions happen in the consumer.
* Maintenance: pg-boss archive after 7 days, delete after 30; `jobs.dead_letter` kept 90 days.
DOD:
* 1,000 enqueued jobs processed by two worker replicas with zero duplicates of an idempotent effect (test asserts one row per key).
* Kill a worker mid-job: the job re-runs on the other replica and the idempotency guard prevents a double effect (test log).
* Cron job fires at the scheduled minute in a 3-minute test window; admin view shows the run.
* Dead-letter requeue from the admin page succeeds; permission test proves customers cannot see `/admin/jobs`.
* Consumer migration: `data-layer/file-storage` variants worker converted to `packages/jobs` in this PR as the reference consumer.
* Docs `docs/platform/jobs.md` (how to define, enqueue, test a job), ADR update to `libraries/backend-landscape`, `CHANGELOG.md`, Linear comment with metrics screenshot.
EDGE:
* Postgres failover mid-poll: pg-boss reconnects with backoff; jobs in `active` past their `expireInSeconds` are retried.
* A handler that never resolves: per-job timeout (default 5 min) converts to a failure; long imports chunk themselves (`migration/import-framework`).
* Thundering herd after downtime: 10,000 due cron runs on restart; `singletonKey` per schedule collapses them to one.
* Tenant deleted while jobs are queued: handler checks tenant existence and completes as `skipped`.
* Very large payloads: inputs over 64 KB are rejected at enqueue; consumers store the blob (`data-layer/file-storage`) and pass a reference.
* Local dev without a worker running: `pnpm dev` starts the inline worker; a banner in the dev shell warns when jobs are pending with no worker.
DEPS: `data-layer/drizzle-schema` (database, migrations, `jobs` schema), `libraries/backend-landscape` (final library choice; this spec defaults to pg-boss). Soft: `data-layer/audit-log`, `data-layer/observability`, `identity/rbac-abac`, `tables/grid-view`, `app-shell/app-deploy-pipeline` (worker image). Consumed by `data-layer/file-storage`, `data-layer/search`, `collab/notifications`, `growth/social-scheduler`, `growth/outreach-sequences`, `growth/attribution`, `migration/import-framework`, `migration/export`, `tables/automations`.
