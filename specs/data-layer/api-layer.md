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
children: ["PAP-268", "PAP-267", "PAP-269"]
blockedBy: ["PAP-33"]
blocks: ["PAP-119", "PAP-129", "PAP-163", "PAP-193", "PAP-222", "PAP-242", "PAP-36", "PAP-39", "PAP-40"]
key: "data-layer/api-layer"
url: "https://linear.app/paperos/issue/PAP-35/expose-a-typed-api-via-orpc-with-zod-schemas-generated-from-drizzle"
source: "plan/specs/bucket-0.json (round-1 canonical spec JSON)"
---

# PAP-35: Expose a typed API via oRPC with Zod schemas generated from Drizzle

**Goal**

Expose the database through a typed RPC layer with oRPC so React hooks, Tauri clients and agents share one contract: Zod input/output schemas derived from Drizzle, OpenAPI generated for external callers, and every procedure running inside the tenant context that RLS expects.

**Scope**

In:
- `apps/api/` Node 22 server (Hono 4 adapter) hosting oRPC 1.x routers, deployed as a Docker service on the VPS via Coolify (`ops/compose/api.yml`).
- `packages/api-contract/` with routers, Zod 4 schemas (from `drizzle-zod` in `data-layer/core-entities` plus hand-written DTOs), and the inferred `RouterClient` type.
- `packages/api-client/`: browser/Tauri client with `@orpc/client` fetch link, `@orpc/tanstack-query` utils, auth header injection, request id, retry policy.
- Middleware chain: request id, logging, auth (Better Auth session -> `actor`), tenant resolution (header `x-tenant` or subdomain), `withTenant` DB context, error mapping, audit hook (`data-layer/audit-log`), OTel span (`data-layer/observability`).
- Core routers: `tenants`, `workspaces`, `users.me`, `memberships`, `roles`, `files` (stubs completed by `data-layer/file-storage`), `health`.
- OpenAPI 3.1 doc served at `/api/openapi.json` and Scalar UI at `/api/docs`.
- Codegen script `pnpm gen:api` that regenerates Zod from Drizzle and fails CI if output is stale.

Out: auth server itself (`identity/better-auth`), realtime (`realtime/*`), sync (`data-layer/local-first-sync`), business routers.

**Spec**

- Procedure convention: `router.<entity>.<verb>` with verbs `list`, `get`, `create`, `update`, `archive`; list inputs `{ cursor?, limit<=100, filter?, sort? }` returning `{ items, nextCursor }`.
- Errors: `ORPCError` codes `UNAUTHORIZED`, `FORBIDDEN`, `NOT_FOUND`, `CONFLICT`, `VALIDATION`, `RATE_LIMITED`, `INTERNAL`; RLS denials surface as `NOT_FOUND` for reads and `FORBIDDEN` for writes.
- Context type: `{ requestId, actor: { id, kind, tenantId, roles[] } | null, db, tenantId, log, span }`.
- Rate limit per actor: 600/min default via in-memory token bucket now, Redis later.
- Client hooks: `orpc.users.me.queryOptions()`, `orpc.tenants.list.infiniteOptions()`; SSR-free.
- Test utilities `packages/api-contract/test/` providing `callAs(actorFixture)`.
- Deployment: health endpoint `/api/health` checks DB and returns build SHA; graceful shutdown; env from `serverEnvSchema` (`app-shell/env-config`).
- API versioning: path prefix `/api/v1`; breaking changes require ADR.

**Definition of done**

- `apps/api` deployed to staging; `/api/health` and `/api/docs` reachable over TLS.
- Vitest: middleware chain, error mapping, every core router happy path and forbidden path through `callAs`; contract type test that a client call with a wrong input fails typecheck.
- `pnpm gen:api` stale check green; OpenAPI validated with `@redocly/cli lint`.
- Web `apps/web` renders `users.me` on the dashboard example route; screenshots at 375, 1024, 1920 including Scalar docs page.
- `docs/data/api.md` (conventions, adding a router, client usage); CHANGELOG; Linear comment with staging docs URL.

**Edge cases**

- Missing tenant header on a tenant-scoped call: 400 with clear message, never default to first tenant.
- Actor member of several tenants: header required; `users.me` lists tenants.
- Payload above 1 MB: reject 413; file uploads never pass through RPC.
- Clock skew and retries on non-idempotent `create`: idempotency key header stored 24 h.
- Zod schema drift from Drizzle after a migration: CI stale check catches it.
- Slow query above 2 s: cancelled via `statement_timeout` and reported to observability.

**Dependencies**

`data-layer/core-entities` (hard), `data-layer/rls-tenancy` (context contract), `identity/better-auth` (session verification; stub with a signed dev token until merged), `app-shell/env-config`. Unblocks `data-layer/local-first-sync`, `data-layer/observability`, `spec-builder/data-section`, `pm-linear/linear-sync`, all business routers.

**Agent**

Built by Forge. Reviewed by Sentinel (Code Reviewer and Security Auditor) with Nova checking hook ergonomics.

**Size**

L: server, contract, client and codegen must land together for the type chain to be real.
