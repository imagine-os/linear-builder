---
identifier: "PAP-240"
title: "Build test-mode seed and reset endpoints (`/__test/seed`, `/__test/reset`) with deterministic fixtures per audience, before Gate 3"
project: "quality"
projectName: "Quality Pipeline"
phase: "P0"
type: "Build"
priority: 1
surfaces: ["Developer"]
milestone: "Gates 1 and 2 on every PR"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-32", "PAP-57", "PAP-224"]
blocks: ["PAP-64", "PAP-82", "PAP-85", "PAP-86", "PAP-87", "PAP-122", "PAP-247", "PAP-250", "PAP-357", "PAP-363"]
key: "quality/test-mode-seed"
url: "https://linear.app/paperos/issue/PAP-240/build-test-mode-seed-and-reset-endpoints-testseed-testreset-with"
source: "Linear snapshot 2026-09-17T13:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T06:22:45.357Z"
---

# PAP-240: Build test-mode seed and reset endpoints (`/__test/seed`, `/__test/reset`) with deterministic fixtures per audience, before Gate 3

**Goal**

Give every automated suite the same deterministic world: a `PAPEROS_TEST_MODE` guarded `/__test/*` API that seeds named fixture sets, mints sessions for one test user per audience and resets test tenants, so Gate 3 can screenshot authenticated pages in P0 instead of waiting for the P1 e2e issue.

**Scope**

* In: `apps/api/src/test-mode/` routes `seed`, `reset`, `login-as`, `clock`; fixture catalogue `packages/testing/fixtures/` (`minimal`, `portal`, `console`, `tables-100`, `tables-10k`, `finance`), `testUsers` per built-in audience from PAP-55, Playwright fixtures `apps/web/e2e/support/` (`seed()`, `loginAs(audience)`, `reset()`, cached storage state), build-time stripping outside test mode, docs.
* Out: production data seeding (PAP-32 owns migrations and dev seed), mail sink (PAP-42), e2e specs (PAP-86).

**Spec**

* Guard: routes registered only when `PAPEROS_TEST_MODE=1`; the production Docker build sets the flag off and a Vite define removes client helpers; a Gate 1 check greps the production bundle for `__test` and fails on a hit.
* `POST /__test/seed { fixture, tenantSlug? } -> { tenantId, users: Record<audience, { id, email }>, records }`: fixtures are TypeScript modules exporting a deterministic builder using `@faker-js/faker` with seed 42; ids are UUIDv5 from `(fixture, entity, index)` so screenshots are stable.
* `POST /__test/login-as { audience, tenantId } -> Set-Cookie` minting a Better Auth session directly through the adapter (no sign-in routes, no rate limits).
* `POST /__test/reset { tenantSlugPrefix = 'e2e-' }` truncates tenants matching the prefix in dependency order; refuses non-prefixed slugs.
* `POST /__test/clock { now }` pins server time for the request context (jobs, `RelativeTime`).
* Playwright: `loginAs('staff-support')` caches storage state per audience per worker; `seed('portal')` once per project.

**Interface contract**

* Provides: routes above; `testUsers` map keyed by `AudienceId`; fixtures `FixtureName`; Playwright fixtures `seed`, `loginAs`, `reset`, `clock`; `PAPEROS_TEST_MODE` env contract.
* Requires: PAP-32 schema and migrations, PAP-57 server child (session minting via adapter), PAP-55 audience ids, PAP-33 core entities.
* Consumers: PAP-82, PAP-83, PAP-84, PAP-85, PAP-86, PAP-87, PAP-64, PAP-110.

**Definition of done**

* `seed('portal')` twice yields identical ids and row counts (test); `reset` removes only `e2e-` tenants.
* `loginAs` for all twelve built-in audiences returns a session whose principal matches that audience and no narrower one (`matches` check).
* Production bundle check passes; a seeded leak of `__test` fails it.
* Playwright smoke: log in as customer, open `/portal`, screenshot at 375 and 1280 in CI.
* `docs/quality/testing.md` section "Test mode"; changelog under "Quality".

**Test plan**

* Unit: fixture determinism, UUIDv5 ids, reset prefix guard.
* Integration: routes absent when the flag is off (404), present when on; `login-as` cookie works against a protected procedure.
* Security: Sentinel Security Auditor verifies the guard and the build check.

**Demo**

`PAPEROS_TEST_MODE=1 pnpm dev`, then `curl -X POST :3000/__test/seed -d '{"fixture":"portal"}'`, `curl -c c.txt -X POST :3000/__test/login-as -d '{"audience":"customer-pro"}'`, open `/portal` with that cookie and see Ada's seeded dashboard. Under two minutes.

**Edge cases**

* Two shards seeding the same fixture: tenant slug includes shard and worker index.
* Fixture references a module not installed (finance before PAP-175): fixture skipped with a clear message.
* Clock pinned and forgotten: reset on `reset()` and at request end.
* Test mode accidentally on in staging: `/healthz` reports `testMode: true` and the release certification (PAP-88) blocks.

**Dependencies**

PAP-32, PAP-57 (hard; the server child suffices). Soft: PAP-33, PAP-55, PAP-42.

**Agent**

Built by Sentinel (Code Reviewer sub-agent) with Forge on the session minting. Reviewed by Forge and Sentinel Security Auditor.

**Size**

M: a handful of routes and fixtures; determinism and the guard are what matter.
