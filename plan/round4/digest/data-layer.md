# Round 4 digest: Data Layer & Database (`data-layer`)

Benchmarks: Supabase (auto REST, RLS, storage, realtime), Hasura (auto CRUD, column permissions), Prisma / Drizzle (schema as code), ElectricSQL / PGlite, PowerSync, Zero / Replicache, Convex (transactional functions, scheduler), Neon / PlanetScale (database branching), pgAudit and pg_stat_statements, squawk (migration lint), pg-boss / Inngest / Trigger.dev, Sentry and OpenTelemetry

## Feature matrix

| Feature | Status | Covered by | Note |
|---|---|---|---|
| Postgres 17 provisioning, roles, extensions, PgBouncer | covered | PAP-30 | Hetzner/Coolify, pgvector image, four roles |
| Continuous WAL archiving and PITR with weekly restore drill | covered | PAP-30 | pgBackRest, RPO 1 h, RTO 30 min |
| Object storage, Yjs, orchestrator and key backups | partial | PAP-354, r4/data-layer/platform-backups | restic jobs and escrow split into a child |
| Whole-platform DR drill with measured RPO/RTO | partial | PAP-354, r4/data-layer/platform-dr-drill | drill split into a child; first run before RC |
| Tenant-scoped point-in-time restore | gap | r4/data-layer/tenant-pitr-restore | Neon-style branch restore; deferred to v0.2 |
| Local dev stack with per-worktree databases | covered | PAP-42 | docker compose, session-start hook |
| Ephemeral per-PR / preview databases (branching) | gap | r4/data-layer/preview-databases | PlanetScale/Neon parity; PAP-26 and PAP-365 need it |
| Schema as code, migrations, seeds | covered | PAP-32 | Drizzle, destructive guard, seed profiles |
| Migration safety lint, dry run, rollback, backfills | gap | r4/data-layer/migration-safety | squawk-style checks; nothing rehearses migrations |
| Per-module migration folders and removal | covered | PAP-32, PAP-265 | app-shell owns module integration |
| Core entity model with Zod types and ER docs | covered | PAP-33 | seven shared tables |
| Row-level security with generated policies and harness | covered | PAP-34 | FORCE RLS, fail closed, `expectTenantIsolation` |
| Permission predicates compiled into RLS | covered | PAP-228 | identity owns; data-layer consumes |
| Field-level masking of responses | gap | r4/identity/field-permissions | owned by identity in round 4; repository applies it |
| Typed API server, middleware chain, error mapping | covered | PAP-267 | Hono 4 + oRPC |
| Routers, typed client, `callAs` | covered | PAP-268 | core routers hand-written |
| Generic entity factory: repository + CRUD router + events + shapes | gap | r4/data-layer/entity-factory | Supabase/Hasura auto-CRUD parity; biggest productivity gap |
| OpenAPI, Scalar docs, health, staging deploy | covered | PAP-269 |  |
| Generated TypeScript SDK for external developers | covered | PAP-222 | identity, deferred |
| Shared value types (Money, ActorRef, EntityRef, cursors, errors) | covered | PAP-302 | contract-zero |
| Shared filter grammar with SQL and memory evaluators | covered | PAP-279 | keystone spec |
| Domain event envelope and topic registry | partial | PAP-303, r4/data-layer/events-core | package half split out so consumers start day one |
| Transactional outbox dispatcher, fan-out, dead-letter, replay | partial | PAP-303, r4/data-layer/events-outbox-dispatcher | worker half split out |
| Event schema registry, upcasters, dual publish | covered | PAP-436 | module-system |
| Idempotency keys and batch endpoint | partial | PAP-304, r4/data-layer/idempotency-batch | split from rate limiting |
| Postgres-backed rate limiting per actor, key, IP, tenant | partial | PAP-304, r4/data-layer/rate-limits | split; replaces four hand-rolled limiters |
| Local-first sync: Electric service and tenant-scoped shape proxy | covered | PAP-270 |  |
| PGlite client, schema generation, read hooks | covered | PAP-271 |  |
| Offline write outbox with leader election | covered | PAP-272, PAP-148 | realtime hardens it |
| Sync engine ADR (Electric vs Zero vs PowerSync vs Replicache) | covered | PAP-31 |  |
| Local data protection: wipe on sign-out/revocation, non-cacheable shapes | gap | r4/data-layer/local-data-protection | lost-device story missing |
| Object storage with presigned uploads and image variants | covered | PAP-37 | MinIO, sharp |
| Malware scanning of uploads | gap | r4/data-layer/upload-scanning | PAP-37 names ClamAV as follow-up |
| Document previews (PDF/office thumbnails) | gap | r4/data-layer/document-previews | deferred to v0.2 |
| Append-only audit log with actor, diff, reason, hash chain | covered | PAP-38 |  |
| Database-level audit (pgAudit) and DB health checks | gap | r4/data-layer/pgaudit-db-health | B4 boundary detection |
| Keyword search with registry, tsvector, trigram, facets | partial | PAP-39, r4/data-layer/search-keyword | split from embeddings |
| Semantic and hybrid search with embeddings | partial | PAP-39, r4/data-layer/search-semantic | split; provider behind an interface |
| OpenTelemetry tracing, slow queries, dashboards | covered | PAP-40 |  |
| Living data dictionary | covered | PAP-41 | reads the PII registry after round 4 |
| Background jobs runtime (pg-boss) | partial | PAP-43, r4/data-layer/jobs-core | core split from admin page |
| Jobs admin page, metrics, dead-letter requeue | partial | PAP-43, r4/data-layer/jobs-admin | split |
| Durable multi-step workflows and approvals | covered | PAP-174, PAP-388 | tables automations own it |
| Transactional email package with sandbox and suppression | covered | PAP-370 |  |
| Server-side field encryption with rotation and leak scanner | covered | PAP-353 |  |
| Config and secrets port for modules | covered | PAP-444, PAP-17 | module-system and app-shell |
| PII classification registry | partial | PAP-355, r4/data-layer/pii-registry | split; single owner of `pii.json` |
| Retention jobs, anonymisation, legal hold | partial | PAP-355, r4/data-layer/retention-jobs | split |
| Tenant hard purge (export first, tombstone) | partial | PAP-355, r4/data-layer/tenant-purge | split; destructive path reviewed as security |
| Tenant lifecycle: states, deletion request, quotas | covered | PAP-432 |  |
| Per-tenant sequences and human-readable keys | gap | r4/data-layer/tenant-sequences | invoices, tickets, employees all need it |
| Soft delete, trash and restore | covered | PAP-32, PAP-334 | tables owns the UI |
| Record field history and undo | covered | PAP-333, PAP-38 | tables |
| Bulk operations with server batching | covered | PAP-334, PAP-304 |  |
| Tenant export in open formats | covered | PAP-205, PAP-420 | migration |
| Usage metering and quotas | covered | PAP-391, PAP-432 | business-core meters; lifecycle counts |
| Maintenance / read-only mode | gap | r4/data-layer/maintenance-mode | needed by DR, migrations, key rotation |
| Feature flags | covered | PAP-366 | app-shell |
| Custom domains and host-based tenant resolution | covered | PAP-431 | app-shell |
| Read replicas / analytics database | gap | - | non-goal for v0.1; PAP-183 reports run on primary; ADR later |
| Multi-region or data residency | gap | - | non-goal; documented in threat model gap register |
| HTTP caching and ETags on read procedures | gap | - | low value with local-first reads; revisit v0.2 |
| Module contract, conformance and kernel wiring | covered | PAP-448, PAP-451, PAP-454 |  |
| Cold-builder cookbook: add an entity in ten minutes | partial | r4/data-layer/entity-factory, PAP-24 | cookbook ships with the factory |

## New issues

| Key | Title | Parent | Size | Model | Deferred |
|---|---|---|---|---|---|
| `r4/data-layer/events-core` | Domain event envelope, `defineTopic` registry, in-transaction `publish()`, testing helpers and the generated catalogue doc | PAP-303 | M | Opus 5 / high |  |
| `r4/data-layer/events-outbox-dispatcher` | Outbox dispatcher job `events.dispatch`: per-subject ordering, fan-out to in-process, job, live-event, webhook and orchestrator sinks, dead-letter and `events:replay` | PAP-303 | M | Opus 5 / high |  |
| `r4/data-layer/idempotency-batch` | Idempotency middleware: `Idempotency-Key` contract, `idempotency_keys` table with replay semantics, `withIdempotencyKey()` client helper and `POST /api/v1/rpc/batch` | PAP-304 | M | Opus 5 / high |  |
| `r4/data-layer/rate-limits` | Postgres-backed rate limiting: `rate_limit_bucket`, `paperos.rate_limit_hit()`, actor, API-key, IP and tenant scopes, public-route registry and hot-reloaded `ops/api/limits.yml` | PAP-304 | M | Opus 5 / high |  |
| `r4/data-layer/pii-registry` | `pii()` Drizzle column annotation and registry: generated `pii.json`, the unannotated-column lint, and wiring into audit redaction, OTel filtering, the data dictionary and exports | PAP-355 | S | Sonnet 5 / medium |  |
| `r4/data-layer/retention-jobs` | Retention policy `ops/data/retention.yaml`, the nightly `retention.run` job with delete, anonymise and partition-drop strategies, legal hold flags and the audit summary per table | PAP-355 | M | Sonnet 5 / medium |  |
| `r4/data-layer/tenant-purge` | Export-first tenant hard-purge job `tenant.purge`: FK-order deletion generator, sessions, keys, Yjs and MinIO cleanup, `tenant_tombstone` and `pnpm tenant:verify-purged` | PAP-355 | M | Opus 5 / high |  |
| `r4/data-layer/platform-backups` | Platform backup jobs: restic for MinIO buckets, hourly orchestrator schema dumps, daily Coolify and Caddy exports, the off-site key escrow bundle and `backup_age_seconds` alerts | PAP-354 | M | Opus 5 / medium |  |
| `r4/data-layer/platform-dr-drill` | Monthly platform disaster-recovery drill `ops/dr/platform-drill.sh`: fresh Hetzner host, escrow decrypt, restore Postgres, MinIO, Yjs and orchestrator state, smoke suite, RPO and RTO report | PAP-354 | M | Opus 5 / medium |  |
| `r4/data-layer/jobs-core` | `@paperos/jobs` core on pg-boss: `defineJob`, `enqueue`, `schedule`, `withIdempotency`, tenant and actor context, retries, dead-letter and the `apps/worker` entry with Dockerfile | PAP-43 | M | Opus 5 / high |  |
| `r4/data-layer/jobs-admin` | `/admin/jobs` staff page and `jobs.list|get|requeue|cancel` procedures with dead-letter requeue, `paperos_jobs_*` metrics and the dev banner for pending jobs without a worker | PAP-43 | S | Sonnet 5 / medium |  |
| `r4/data-layer/search-keyword` | Search registry and keyword search: `registerSearchable`, `search_document` with tsvector and trigram indexes, upsert triggers, deferred mode and `search.query` keyword mode with facets and `can()` post-filter | PAP-39 | M | Sonnet 5 / high |  |
| `r4/data-layer/search-semantic` | Semantic and hybrid search: `EmbeddingProvider`, `search.embed` job, pgvector HNSW column, RRF fusion, reindex on model change and the `<SearchResults/>` component | PAP-39 | M | Sonnet 5 / medium |  |
| `r4/data-layer/entity-factory` | Build the entity factory: `defineEntity()` yields the Drizzle repository, CRUD oRPC router, Zod DTOs, shape registration, audit reason handling and `record.*` events from one declaration | - | L | Opus 5 / high |  |
| `r4/data-layer/migration-safety` | Migration safety: squawk-style lint for generated SQL, expand-contract checklist, `db:migrate --dry-run` against a staging snapshot, `db:rollback` to the previous release and long backfills as jobs | - | M | Sonnet 5 / high |  |
| `r4/data-layer/preview-databases` | Ephemeral preview databases: template-cloned per-PR and per-preview-slot databases with a seed profile, migration smoke, TTL teardown, `pnpm db:branch` and the `DATABASE_URL` handoff to the deploy pipeline | - | M | Sonnet 5 / medium |  |
| `r4/data-layer/tenant-sequences` | Per-tenant sequences and human-readable keys: `defineSequence`, gapless and prefixed formats, `recordKey()` column helper, reservation API and yearly reset | - | S | Sonnet 5 / medium |  |
| `r4/data-layer/local-data-protection` | Local data protection for PGlite and Tauri caches: sign-out and revocation wipe, `cacheable: false` shapes for sensitive tables, encrypted-column sync lint and the device data policy in page specs | - | S | Opus 5 / high |  |
| `r4/data-layer/pgaudit-db-health` | Enable pgAudit for DDL, role and bypass sessions and add database health checks: bloat, vacuum, index usage, replication slot lag and connection saturation dashboards with alerts | - | S | Sonnet 5 / medium |  |
| `r4/data-layer/upload-scanning` | Malware scanning for uploads: ClamAV sidecar, `files.scan` job, `quarantined` status, download block and staff release flow | - | S | Sonnet 5 / medium |  |
| `r4/data-layer/maintenance-mode` | Platform maintenance and read-only mode: `maintenance` flag, API 503 with `Retry-After` for writes, outbox-aware client banner and `pnpm ops:maintenance on|off|status` | - | S | Sonnet 5 / low |  |
| `r4/data-layer/tenant-pitr-restore` | Tenant-scoped point-in-time restore: PITR into a scratch database, tenant extract, diff preview and selective re-import through the import engine | - | M | Opus 5 / medium | yes |
| `r4/data-layer/document-previews` | Document previews: PDF and office thumbnails and page renders through a `files.preview` job, preview variants in `FileDto` and a viewer fallback | - | S | Sonnet 5 / low | yes |

## Amendments to existing specs

* **PAP-41** (Spec): Ownership change (round 4): `pii.json` is generated by the PII registry child `r4/data-layer/pii-registry` (`pnpm pii:build`), not by this generator. The dictionary reads `packages/db/generated/pii.json` and renders the `kind` and `subject` badges; `dictionary:check` fails when the file is stale. Remove the `pii: boolean` key from `dictionary.yaml` in favour of the schema annotation.
* **PAP-30** (Spec): Add: (1) `pgaudit` to the pre-installed extensions with `pgaudit.log = 'ddl, role'` (consumed by `r4/data-layer/pgaudit-db-health`); (2) the data volume for `pg-prod` and `pg-staging` lives on an encrypted Hetzner volume (LUKS via cloud-init) so data at rest is covered independently of PAP-353; document the unlock procedure in `ops/db/README.md`; (3) template databases `tpl_minimal` and `tpl_demo` reserved names for `r4/data-layer/preview-databases`.
* **PAP-35** (Interface contract): Correction: the context type imports `Principal` from `@paperos/core/audience` (PAP-55), not `@paperos/core/principal`; the Contracts document §1 and PAP-267 already use the audience path. Umbrella text updated so children do not diverge.
* **PAP-39** (Edge cases): Add: `vector(1024)` fixes the dimension per column, so a model with different dimensions is a migration (new column, backfill, swap), not a reindex; `pnpm search:migrate-dims` in `r4/data-layer/search-semantic` owns it. Reindex on model change applies only to same-dimension models.
* **PAP-304** (Spec): Tighten the failure mode: fail-open for authenticated actors lasts at most 60 s per incident, then the limiter fails closed for everyone; every degraded minute emits a security event (PAP-356) in addition to the log line. Chain order is owned jointly by the two children `r4/data-layer/rate-limits` and `r4/data-layer/idempotency-batch`; whichever merges second updates the PAP-267 order test.
* **PAP-271** (Edge cases): Add: sign-out, session revocation and tenant switch wipe the local PGlite database and `y-indexeddb` stores unless the outbox holds unsent writes and the user keeps them (`r4/data-layer/local-data-protection` owns `wipe()`); shapes may declare `cacheable: false` and are then held in memory only; the registry lint refuses `encrypted()` columns in persisted shapes.
* **PAP-43** (Definition of done): Add evidence items: (1) the worker exposes `/healthz` and `/metrics` and a missing heartbeat for 60 s in production fires an alert (PAP-40); (2) a job enqueued with `tenantId` runs its handler inside `withTenant` and the PAP-34 harness proves it cannot read another tenant (test); (3) enqueue from tenant A with `tenantId` of tenant B is refused with `FORBIDDEN`.
* **PAP-37** (Spec): Add the scanning hook: `files.complete` sets `status = 'scanning'` when the scanner is configured (`r4/data-layer/upload-scanning`) and `ready` otherwise; `files.getUrl` refuses non-`ready` files with `FILE_NOT_READY`; the `file` status enum gains `scanning | quarantined` now so the later child needs no migration.

## Cross-project suggestions

* **app-shell**: Preview deploys (PAP-26) and warm pools (PAP-365) consume `r4/data-layer/preview-databases` — PAP-26 posts a preview URL but names no database; the branch script returns the `DATABASE_URL*` set in PAP-17 names and drops on PR close.
* **business-core**: Invoice, quote and receipt numbering (PAP-180) should consume `r4/data-layer/tenant-sequences` — Gapless per-tenant numbering is a legal requirement in several jurisdictions and PAP-180 currently implies its own counter.
* **tables**: Custom datasets (PAP-161, PAP-332) should register through `defineEntity()` where the schema is code — Keeps code datasets and custom datasets on one repository and router shape so PAP-333 and PAP-334 have one path.
* **quality**: Security telemetry (PAP-356) should ingest pgAudit lines and `rate_limit_degraded` events — Both are new detection sources from `r4/data-layer/pgaudit-db-health` and `r4/data-layer/rate-limits`.
* **module-system**: Migration adapter kit (PAP-443) should reuse `pnpm db:lint` and `defineBackfill` from `r4/data-layer/migration-safety` — Avoids two batch runners and two sets of safety rules for expand-contract changes.
* **pm-linear**: Weekly re-audit (PAP-306) runs `pnpm tenant:purge --dry-run` and `pii:build --check` as drift checks — New tables without a tenant mapping or PII annotation should surface weekly, not at purge time.

## What was missing and why it matters

1. No generic entity path: PAP-268 hand-writes routers and PAP-448 only declares `RepositoryPort<T>`, so every module (PM, CRM, finance, import) would re-implement CRUD, cursors, audit and events differently; `defineEntity()` makes conformance the default and is what a cold session reaches for first.
2. Four umbrella-sized M issues (PAP-303, PAP-304, PAP-355, PAP-354) each hid two or three sessions of work behind one identifier; splitting them lets the pure packages (envelope, idempotency, PII registry, backup jobs) land days before the workers, drills and destructive jobs that depend on pg-boss or MinIO.
3. Migrations were guarded but never rehearsed: nothing lints unsafe SQL, restores a snapshot for a dry run, or offers a rollback, which matters when twenty agent sessions generate schema changes in parallel.
4. Local-first shipped without a lost-device story: PGlite and Tauri caches were never wiped on sign-out or revocation and specs could not say 'never cache this dataset'.
5. Operational gaps behind the threat model: no database-level audit (pgAudit), no malware scan on uploads, no maintenance mode for migrations and DR, no per-PR databases for previews, and no per-tenant human-readable numbering that invoices and tickets legally need.
