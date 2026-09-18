---
identifier: "PAP-741"
title: "Generate the backend from entities: Drizzle tables with RLS, a reviewed migration, oRPC entity routers and Electric shape registrations as `paperos gen` plugins"
project: "spec-builder"
projectName: "Spec Builder"
phase: "P1"
type: "Build"
priority: 1
surfaces: ["Developer"]
milestone: "Codegen and conformance tests"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-32", "PAP-228", "PAP-268", "PAP-739"]
blocks: ["PAP-362", "PAP-364"]
key: "r4/spec-builder/entity-backend-codegen"
url: "https://linear.app/paperos/issue/PAP-741/generate-the-backend-from-entities-drizzle-tables-with-rls-a-reviewed"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:34.800Z"
model: "claude-opus-5"
effort: "high"
estimate: 5
dueDate: "2026-09-26"
cycle: null
---

# PAP-741: Generate the backend from entities: Drizzle tables with RLS, a reviewed migration, oRPC entity routers and Electric shape registrations as `paperos gen` plugins

**Model / Effort:** Opus 5 (`claude-opus-5`) / high — Build L

**Goal**

The golden path (§4) lists `packages/db/src/schema/app.ts`, `migrations/0001_app.sql` and `apps/api/src/generated/routers.ts` among the files `paperos gen` emits at C3. No issue owns them: PAP-362 registers nine generators and none writes a table or a router, so generated hooks (PAP-312) would call procedures that do not exist.

**Scope**

In: generators `db-schema`, `db-migration`, `routers`, `shapes` in `packages/spec/src/codegen/backend/` registered with PAP-362's `defineGenerator`; Drizzle emission per entity with implicit columns, indexes, relations and RLS via PAP-228 helpers; `drizzle-kit generate` wrapped so the migration is created once and reviewed in PR #1; oRPC routers `<entity>.list|get|create|update|archive|restore` per Contracts §4 with `authorize()` (PAP-229) and `FilterTree` list input; `defineShape` registrations (PAP-271) for entities with `sync: live` pages; `docs/spec/backend-codegen.md`. Out: custom procedures (hand-written in `apps/api/src/procedures/`), business logic; the PAP-161 `registerDataset` call is emitted as one line per entity, the `ViewSpec` comes from PAP-361.

**Spec**

* Ownership: `generated/**` rewritten every run with the spec-hash banner; `migrations/*.sql` created once with a `-- generated from app.spec.yaml sha256:` header; a later entity change adds a new migration, never edits an old one; `--check` flags a schema whose migration is missing.
* Every table: `tenant_id` first, six implicit columns, soft delete, `uuid_generate_v7()`, audit trigger (PAP-38), RLS policies `select|insert|update|delete` from the entity's access rows through PAP-116 `toPolicies` and PAP-228's SQL compiler; `pii` fields land in `pii.json` for PAP-41 and PAP-355.
* Routers: list input `{ cursor?, limit<=100, filter?: FilterTree, sort? }`, keyset cursors (PAP-268), `Idempotency-Key` on create, `X-PaperOS-Reason` required for agents; `internal` fields stripped for `customer.*` at the DTO layer; relations expand one hop with `include`.
* Determinism: sorted entities and columns, no timestamps; typecheck of `apps/api` and `packages/db` output is part of the drift job.
* Budget: 20 entities generate in under 3 s; their migration applies on the PAP-42 stack in under 10 s.

**Interface contract**

Provides: the four generators, `generateBackend(app): GeneratedFiles`, migration naming convention, `pii.json`, `registerDataset` lines. Consumes: `Field` grammar, `AppSpec` (PAP-117), Drizzle workflow (PAP-32), RLS helpers and SQL compiler (PAP-228, PAP-34), router conventions (PAP-268, PAP-267), `authorize` (PAP-229), `toPolicies` (PAP-116), audit trigger (PAP-38), `defineShape` (PAP-271), `FilterTree` (PAP-279). Consumed by: PAP-362, PAP-312 hooks, PAP-361 pages, PAP-364, PAP-429, PAP-41.

**Definition of done**

* Clinic fixture: tables, one migration, routers and shapes generated; migration applies on the compose stack; `callAs(customer)` sees own rows only and `callAs(staff)` all (PAP-34 harness); `internal` field absent from the customer DTO.
* Two runs byte-identical; `--check` red after adding a field without regenerating; typecheck green.
* `docs/spec/backend-codegen.md`; adapters registered in PAP-362 (comment there); CHANGELOG entry; Linear comment with the generated tree.

**Test plan**

* Unit: column mapping per `FieldType`, implicit columns, relation `onDelete`, RLS policy emission per access shape, DTO stripping of `internal`, router snapshot minimal and maximal.
* Integration (Postgres in CI): migrate, seed 100 rows, list with a `FilterTree`, cursor pages, RLS matrix via `callAs`, audit rows written with `reason`.
* E2E: PAP-313's `customer-invoices` page runs against generated procedures instead of hand-written ones (branch-start).

**Demo**

Run `paperos gen --only db-schema,db-migration,routers` on the clinic app, `pnpm db:migrate`, then call `appointments.list` as a patient and as staff from the API playground and compare row counts. Under two minutes.

**Edge cases**

* Entity renamed: new migration creates the new table; the old one gets a `-- deprecated` marker and a Needs Justin note if it holds rows (destructive migrations are never generated).
* Relation to `user`: joins the PAP-33 table, never a generated one.
* Two entities in a cycle of `cascade` deletes: error at generation.
* Module disabled (PAP-266): its entities' tables still generated but migrations tagged with `module_id` for PAP-265's runner.
* Custom procedure with the same name as a generated one: generation fails naming both files.

**Dependencies**

Hard: PAP-739, PAP-32, PAP-228, PAP-268. Soft: PAP-116, PAP-229, PAP-38, PAP-271, PAP-34, PAP-41, PAP-265. Blocks PAP-362 (adapter registration), PAP-364.

**Agent**

Builder: Forge (Schema Wright) with Quill on the spec side. Reviewer: Sentinel (Security Auditor for RLS and DTO stripping).

**Size**

L: two sessions (tables and migration; routers and shapes).

*Round 4 critique fix (2026-09-18):* resolved 1 round-4 file key in this description to Linear identifiers: `r4/spec-builder/entity-field-grammar` = PAP-739.
