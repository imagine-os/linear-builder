---
identifier: "PAP-86"
title: "Write end-to-end flow tests for auth, tenant switch, CRUD and realtime presence"
project: "quality"
projectName: "Quality Pipeline"
phase: "P1"
type: "Build"
priority: 2
surfaces: ["Developer"]
milestone: "Visual and video gates"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-224", "PAP-240", "PAP-26", "PAP-57", "PAP-58"]
blocks: ["PAP-156", "PAP-90"]
key: "quality/e2e-flows"
url: "https://linear.app/paperos/issue/PAP-86/write-end-to-end-flow-tests-for-auth-tenant-switch-crud-and-realtime"
source: "plan/specs/bucket-2.json (round-1 canonical spec JSON)"
---

# PAP-86: Write end-to-end flow tests for auth, tenant switch, CRUD and realtime presence

**Goal**

Provide functional end-to-end smoke coverage of the core platform, distinct from screenshots: sign-in with each method, organisation and workspace creation, invitation and tenant switch, record CRUD through the API-backed UI, and realtime presence between two users, run on every PR against the preview build and nightly against staging.

**Scope**

In:
- `apps/web/e2e/functional/` Playwright project `functional` (Chromium at 1280, plus a `mobile` run at 375 for the same specs nightly) with specs: `auth.spec.ts` (passkey via virtual authenticator, magic link via a test mail sink, OAuth via stubbed provider), `tenancy.spec.ts` (create org, create workspace, invite, accept as second user, switch, leave), `crud.spec.ts` (create, edit, list filter, delete, undo on the example entity from `data-layer/core-entities`), `presence.spec.ts` (two browser contexts, cursors and avatars appear and disappear, agent participant badge if `realtime/agent-presence` exists), `permissions.spec.ts` (customer cannot reach staff console; staff without role denied).
- Test infrastructure: `apps/web/e2e/support/` with `testUsers` per audience, `seed()` and `reset()` against the `/__test/*` endpoints (enabled only when `PAPEROS_TEST_MODE=1`), `mailsink` client (Mailpit in compose), `webauthn` virtual authenticator via CDP.
- Ephemeral backend per PR: `ops/compose/preview.yml` starting Postgres, API, Hocuspocus and Mailpit in the CI job with migrations and seeds; `main` nightly runs against staging.
- Reporter: Playwright HTML + JUnit; traces on first retry; status `gate/3-e2e`.
- Tagging `@smoke` (runs on PRs, under 5 minutes) and `@full` (nightly).

Out: visual comparison, load, payment flows (business-core adds its own), native Tauri e2e (later via `tauri-driver`).

**Spec**

- Playwright config `apps/web/playwright.functional.config.ts`: `baseURL` from env, `storageState` per audience cached in `beforeAll`, `retries: 2` in CI with flake reporting to `quality/flake-quarantine`, `trace: 'on-first-retry'`, `video: 'retain-on-failure'`.
- Passkeys: `CDPSession.send('WebAuthn.enable')` and `addVirtualAuthenticator({ protocol: 'ctap2', transport: 'internal', hasResidentKey: true, hasUserVerification: true, isUserVerified: true })`.
- Magic link: poll Mailpit API `GET /api/v1/messages` filtered by recipient, extract link, visit; timeout 15s.
- OAuth: `identity/better-auth` exposes a `mock` provider in test mode; tests assert callback handling only.
- Presence: contexts A and B join the same document route; assert `getByTestId('presence-avatar')` count and cursor element for the other user within 3s; disconnect B and assert removal within 10s.
- Data isolation: every test creates its own tenant with a unique slug; `reset()` only truncates test tenants (slug prefix `e2e-`).
- Test IDs: `data-testid` naming convention `area.element[.modifier]` documented in `docs/quality/testing.md`; components accept `testId` prop where dynamic.

**Definition of done**

- Five specs pass on a PR against the ephemeral stack in under 5 minutes for `@smoke` (link).
- Nightly `@full` including the 375 run passes on staging (link).
- Seeded regression (breaking tenant switch) fails with a trace attached (link).
- Traces and videos retained on failure and linked in the job summary.
- `docs/quality/testing.md` covers running locally with `pnpm e2e`, test-mode endpoints and test IDs; CHANGELOG entry; Linear comment with report links.

**Edge cases**

- Test-mode endpoints must be impossible to enable in production: guarded by env and by a build-time check that strips them unless `PAPEROS_TEST_MODE` is set; security reviewer verifies.
- Two shards creating tenants with the same slug: slug includes shard and worker index.
- Mail arrives out of order or duplicated: match by a unique token embedded in the email address (`user+<uuid>@e2e.local`).
- Presence test timing on slow runners: use generous timeouts and `expect.poll`, not sleeps.
- OAuth provider not stubbed yet: test skipped with a clear reason, not silently passed.
- Ephemeral Postgres slow to start: healthcheck wait loop with 60s cap and readable failure.

**Dependencies**

`identity/org-tenancy` (hard, and by extension `identity/better-auth`). Soft: `data-layer/api-layer` (CRUD target and test endpoints), `realtime/presence` (presence spec skipped until merged), `quality/playwright-matrix` (shared image and fixtures), `data-layer/postgres-provision` (compose pieces). Consumed by `quality/flake-quarantine`, `quality/release-train`, `identity/permission-tests` (pattern).

**Agent**

Built by Sentinel (Code Reviewer sub-agent writing tests) with Forge (Ops Runner) on the ephemeral compose. Reviewed by Forge and Nova (presence).

**Size**

M: five specs plus the ephemeral stack; auth stubs are the fiddly part.
