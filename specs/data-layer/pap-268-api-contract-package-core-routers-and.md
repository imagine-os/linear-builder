---
identifier: "PAP-268"
title: "API contract package, core routers and typed client with callAs test utility"
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
blockedBy: ["PAP-33", "PAP-267", "PAP-302"]
blocks: ["PAP-269", "PAP-272", "PAP-276", "PAP-437", "PAP-454"]
key: "child/PAP-35/13"
url: "https://linear.app/paperos/issue/PAP-268/api-contract-package-core-routers-and-typed-client-with-callas-test"
source: "Linear snapshot 2026-09-17T15:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T13:42:12.337Z"
model: "claude-opus-5"
effort: "medium"
---

# PAP-268: API contract package, core routers and typed client with callAs test utility

**Model / Effort:** Opus 5 (`claude-opus-5`) / medium — Build M, P0 in data-layer

**Goal**

Publish `packages/api-contract` (Zod from `drizzle-zod` plus DTOs, routers `tenants`, `workspaces`, `users.me`, `memberships`, `roles`, `files` stubs, `health`) and `packages/api-client` (`@orpc/client` fetch link, `@orpc/tanstack-query` utils, auth and tenant header injection, retry policy), plus `callAs(principal)` for tests.

**Scope**

In: routers with `list|get|create|update|archive` convention and `{ cursor, limit, filter?: FilterTree, sort? }` inputs; `pnpm gen:api` stale check; client package; test utility; `users.me` on the dashboard example route.

Out: server chain (child 1), OpenAPI docs and deploy (child 3).

**Spec**

* `filter` typed as `FilterTree` from the data-layer filter grammar issue; until it merges, `filter` is `unknown` with a TODO tracked there.
* Client: `createClient(baseUrl, { getToken, getTenant })`; retries only idempotent verbs.
* `callAs(fixture)` builds a context with a fake principal and a per-test tenant.

**Interface contract**

Provides: `AppRouter`, `createClient`, `orpc.*` query utils, `callAs`, DTO types. Consumes: server builder (child 1), Zod schemas (PAP-33). Consumed by PAP-119, PAP-163, PAP-36 and every business router.

**Definition of done**

* Every core router happy and forbidden path tested through `callAs`; wrong input fails typecheck (`expectTypeOf`).
* Dashboard renders `users.me`; screenshots at 375, 1024, 1920.
* `pnpm gen:api --check` green in Gate 1.

**Test plan**

* Unit: router handlers with fake db; pagination cursor round trip; client header injection and retry policy.
* Type: input inference tests.
* Integration (CI compose): `memberships.list` across two tenants never leaks.
* Visual: dashboard at three widths.

**Demo**

Reviewer opens the dashboard on the preview pointed at a local API and sees their user name from `users.me`; in the terminal `pnpm test --filter api-contract` shows the forbidden-path tests. Under a minute.

**Edge cases**

* Cursor tampering: signed cursors rejected with `VALIDATION`.
* `limit` above 100 clamped.

**Dependencies**

Child 1 (hard), PAP-33. Soft: filter grammar issue. Blocks child 3.

**Agent**

Built by Forge. Reviewed by Sentinel (Code Reviewer).

**Size**

M
