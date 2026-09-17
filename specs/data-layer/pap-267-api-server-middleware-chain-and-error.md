---
identifier: "PAP-267"
title: "API server, middleware chain and error mapping (apps/api on Hono 4)"
project: "data-layer"
projectName: "Data Layer & Database"
phase: "P0"
type: "Build"
priority: 1
surfaces: ["Developer"]
milestone: "Postgres + Drizzle baseline"
state: "Backlog"
parent: "PAP-35"
children: []
blockedBy: ["PAP-33"]
blocks: ["PAP-268", "PAP-270", "PAP-304"]
key: "child/PAP-35/12"
url: "https://linear.app/paperos/issue/PAP-267/api-server-middleware-chain-and-error-mapping-appsapi-on-hono-4"
source: "Linear snapshot 2026-09-17T13:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T06:43:05.951Z"
model: "claude-opus-5"
effort: "medium"
---

# PAP-267: API server, middleware chain and error mapping (apps/api on Hono 4)

**Goal**

Stand up `apps/api` hosting oRPC on Hono 4 with the full middleware chain: request id, logging, auth (signed dev token stub until PAP-57), tenant resolution, `withTenant` database context, error mapping, audit and OTel hooks, replacing the `healthz` stub from PAP-26.

**Scope**

In: server bootstrap, middleware modules, `Principal` import from PAP-55, error code enum, context type, graceful shutdown, `statement_timeout`, 1 MB body limit, env from PAP-17, Dockerfile alignment with PAP-26.

Out: routers and client (child 2), docs and deploy (child 3), rate limiting (separate issue).

**Spec**

* Middleware order fixed and tested: requestId, logger, auth, tenant, db, audit vars, otel, errorMap.
* Tenant from `x-tenant` header or subdomain; missing on tenant-scoped procedure is `VALIDATION` 400.
* RLS errors (`42501`) map to `NOT_FOUND` for reads, `FORBIDDEN` for writes.
* Dev token stub enabled only when `NODE_ENV !== 'production'` and `AUTH_DEV_TOKEN` set; test asserts production refuses.

**Interface contract**

Provides: `os` builder with `Context`, `tenantProcedure`, `publicProcedure`, `ApiErrorCode`, headers `x-request-id`. Consumes: `Principal` (PAP-55), `createDb`/`withTenant` (PAP-32), session vars (PAP-34, PAP-38), env (PAP-17).

* Contract source: [Interface & Data Contracts](<https://linear.app/paperos/document/paperos-interface-and-data-contracts-d40e6a4d227c>) §1 (`Principal` from `@paperos/core/audience` is the type of `Context.actor`; RLS context is set with `SET LOCAL app.tenant_id, app.actor_id, app.actor_kind, app.request_id, app.reason, app.bypass`, and `app.actor_id` equals `app.principal_id` until the names are unified); §4 (headers `x-tenant`, `Idempotency-Key`, `X-PaperOS-Reason`, `X-PaperOS-Env`, `traceparent` in and `x-request-id`, `X-PaperOS-Actor` out; error body `{ code, message, requestId, details?, retryAfter? }`; RLS `42501` maps to `NOT_FOUND` on reads and `FORBIDDEN` on writes; `TENANT_REQUIRED` is retired in favour of 400 `VALIDATION`); §6 row "API middleware, error codes, headers".

**Definition of done**

* Server runs locally against the PAP-42 stack; `/healthz` and `/__version` respond.
* Vitest for chain order, tenant resolution matrix, error mapping table, production guard.
* Structured logs include request id and tenant.

**Test plan**

* Unit: each middleware in isolation and the composed chain; error map from `ORPCError` and Postgres codes.
* Integration (CI compose): tenant-scoped call without header is 400; RLS denial mapped correctly; 1 MB body 413; slow query cancelled at 2 s.
* Security: `AUTH_DEV_TOKEN` in production mode refused at boot.

**Demo**

Reviewer runs `pnpm dev:api`, calls `curl -H "x-tenant: acme" -H "authorization: Bearer $DEV_TOKEN" localhost:3000/api/v1/rpc/health` and then omits the tenant header to read the 400 message. Under a minute.

**Edge cases**

* Subdomain and header disagree: 400.
* Principal in several tenants: header required.

**Dependencies**

PAP-33, PAP-32 (hard). Soft: PAP-34, PAP-55, PAP-17. Blocks children 2 and 3.

**Agent**

Built by Forge. Reviewed by Sentinel (Security Auditor).

**Size**

M
