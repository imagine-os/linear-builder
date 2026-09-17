---
identifier: "PAP-35"
title: "Expose a typed API via oRPC with Zod schemas generated from Drizzle"
project: "data-layer"
projectName: "Data Layer & Database"
phase: "P0"
type: "Build"
priority: 1
surfaces: ["Developer"]
milestone: "Postgres + Drizzle baseline"
state: "Backlog"
parent: null
children: ["PAP-267", "PAP-268", "PAP-269"]
blockedBy: ["PAP-33"]
blocks: ["PAP-36", "PAP-39", "PAP-40", "PAP-119", "PAP-129", "PAP-163", "PAP-193", "PAP-222", "PAP-242", "PAP-312", "PAP-335"]
key: "data-layer/api-layer"
url: "https://linear.app/paperos/issue/PAP-35/expose-a-typed-api-via-orpc-with-zod-schemas-generated-from-drizzle"
source: "Linear snapshot 2026-09-17T13:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T06:43:05.865Z"
---

# PAP-35: Expose a typed API via oRPC with Zod schemas generated from Drizzle

**Goal**

Umbrella: expose the database through oRPC so React hooks, Tauri clients and agents share one contract: Zod schemas derived from Drizzle, OpenAPI for external callers, every procedure inside the RLS tenant context. Three children; closes when `users.me` renders on staging through the typed client. Rate limiting and idempotency move to the data-layer rate-limit issue; the `Principal` type comes from PAP-55.

**Scope**

Children:

1. **PAP-267** — API server, middleware chain and error mapping (`apps/api` on Hono 4, request id, auth stub with signed dev token, tenant resolution, `withTenant`, error codes, audit and OTel hooks).
2. **PAP-268** — API contract package and typed client (`packages/api-contract` with Zod from `drizzle-zod`, core routers `tenants`, `workspaces`, `users.me`, `memberships`, `roles`, `files` stubs, `health`; `packages/api-client` with `@orpc/tanstack-query`; `callAs` test utility).
3. **PAP-269** — OpenAPI docs, staging deploy and health (Scalar at `/api/docs`, `/api/health`, Coolify deploy through PAP-26, `redocly lint`).

Out: rate limiting and idempotency (separate issue), file upload bodies (PAP-37), realtime.

**Spec**

* Procedures `router.<entity>.<verb>` with verbs `list|get|create|update|archive`; list input `{ cursor?, limit<=100, filter?: FilterTree, sort? }` returning `{ items, nextCursor }`; `FilterTree` comes from the data-layer filter grammar issue.
* Errors: `UNAUTHORIZED`, `FORBIDDEN`, `NOT_FOUND`, `CONFLICT`, `VALIDATION`, `RATE_LIMITED`, `INTERNAL`; RLS denials read as `NOT_FOUND`, write as `FORBIDDEN`.
* Context `{ requestId, principal: Principal | null, tenantId, db, log, span }` with `Principal` imported from `@paperos/core/principal` (PAP-55).
* Tenant from header `x-tenant` or subdomain; missing header on a tenant-scoped call is 400.
* Path prefix `/api/v1`; payloads over 1 MB rejected 413; `statement_timeout 2s` per procedure.
* Env from `serverEnvSchema` (PAP-17); graceful shutdown.

**Interface contract**

Provides:

* `AppRouter` type and `createClient(baseUrl, { getToken, getTenant })` from `@paperos/api-client`; hooks via `orpc.<entity>.<verb>.queryOptions()` and `infiniteOptions()`.
* Server helpers from `@paperos/api-contract/server`: `os` (oRPC builder with context), `tenantProcedure`, `publicProcedure`, `defineRouter(name, routes)` that modules (PAP-28) register with.
* `callAs(principalFixture)` test utility.
* HTTP: `/api/v1/rpc/*`, `/api/v1/openapi.json`, `/api/docs`, `/api/health`, `/healthz`, `/__version`; headers `x-request-id`, `x-tenant`, `traceparent`.
* Error code enum `ApiErrorCode`.

Consumes: `Principal` (PAP-55), session verification (PAP-57; dev-token stub until then), `createDb`/`withTenant` (PAP-32), RLS context (PAP-34), `FilterTree` (filter grammar issue), audit vars (PAP-38), spans (PAP-40).

* Contract source: [Interface & Data Contracts](<https://linear.app/paperos/document/paperos-interface-and-data-contracts-d40e6a4d227c>) §1 (`Principal` is imported from `@paperos/core/audience` for `Context.actor`, never redefined here); §4 Internal API conventions (transport `/api/v1/rpc/<router>.<procedure>` plus OpenAPI 3.1 REST, auth and tenant headers, procedure shape with `filter?: FilterTree` and signed keyset cursors, `ORPCError` codes, `/api/v1` versioning; the in-memory rate limit here is the interim until pending contracts issue C); §6 rows "API middleware, error codes, headers" and "Routers, client, pagination".

**Definition of done**

* All three children Done.
* Integration test: `apps/api` on staging serves `/api/health` and `/api/docs` over TLS; `apps/web` dashboard renders `users.me` through the typed client; a client call with a wrong input fails typecheck.
* `pnpm gen:api --check` and `redocly lint` green; `docs/data/api.md`; CHANGELOG; Linear comment with the staging docs URL.

**Test plan**

* Unit: middleware chain order, error mapping table, tenant resolution (header, subdomain, missing, mismatch).
* Contract: every core router happy and forbidden path through `callAs`; `expectTypeOf` tests for input inference.
* Integration (CI compose): RLS denial mapped to `NOT_FOUND`; 1 MB payload rejected; slow query cancelled at 2 s.
* E2E: Playwright loads the dashboard route and asserts `users.me` name at 375, 1024, 1920; Scalar page screenshot.
* Lint: OpenAPI validated on every PR.

**Demo**

Reviewer opens `https://staging.PAPEROS_DOMAIN/api/docs`, calls `users.me` from the Scalar console with the dev token and tenant header, then opens the web dashboard showing the same user. Under 90 seconds.

**Edge cases**

* Actor in several tenants: header required; `users.me` lists tenants.
* Zod drift after a migration caught by the stale check.
* Retries on `create`: covered by the idempotency issue; until then documented as unsafe.
* Auth stub must be impossible to enable in production (env guard test).

**Dependencies**

PAP-33 (hard). Soft: PAP-34, PAP-55, PAP-57, PAP-17. Unblocks PAP-36, PAP-39, PAP-40, PAP-119, PAP-129, PAP-163 and every business router.

**Agent**

Built by Forge. Reviewed by Sentinel (Code Reviewer and Security Auditor).

**Size**

L as an umbrella; children are M, M, S.
