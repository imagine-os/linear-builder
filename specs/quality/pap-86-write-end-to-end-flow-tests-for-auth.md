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
blockedBy: ["PAP-26", "PAP-57", "PAP-58", "PAP-224", "PAP-240"]
blocks: ["PAP-90", "PAP-156"]
key: "quality/e2e-flows"
url: "https://linear.app/paperos/issue/PAP-86/write-end-to-end-flow-tests-for-auth-tenant-switch-crud-and-realtime"
source: "Linear snapshot 2026-09-17T13:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T06:22:45.357Z"
---

# PAP-86: Write end-to-end flow tests for auth, tenant switch, CRUD and realtime presence

**Goal**

Provide functional end-to-end coverage of the core platform, distinct from screenshots: sign-in with each method, organisation and workspace creation, invitation and tenant switch, record CRUD, permissions and realtime presence between two users, run on every PR against an ephemeral stack and nightly against staging.

**Scope**

* In: Playwright project `functional` (`apps/web/e2e/functional/`) with `auth`, `tenancy`, `crud`, `presence`, `permissions` specs; `@smoke` (PRs, under 5 minutes) and `@full` (nightly, plus a 375 mobile run); ephemeral backend `ops/compose/preview.yml` (Postgres, API, Hocuspocus, Mailpit); Mailpit client; WebAuthn virtual authenticator; reporter, traces and videos on failure; status `gate/3-e2e`.
* Out: visual comparison (PAP-82), load, payment flows (business-core), native Tauri e2e, seeding and login fixtures (PAP-240 owns `seed()`, `loginAs()`, `reset()`, `testUsers`; this issue consumes them).

**Spec**

* Config `apps/web/playwright.functional.config.ts`: `baseURL` from env, storage state per audience from PAP-240, `retries: 2` in CI writing retried tests to `flakes-delta.json` (PAP-90), `trace: 'on-first-retry'`, `video: 'retain-on-failure'`.
* `auth.spec.ts`: passkey via CDP `WebAuthn.enable` and `addVirtualAuthenticator({ protocol: 'ctap2', transport: 'internal', hasResidentKey: true, hasUserVerification: true, isUserVerified: true })`; magic link by polling Mailpit `GET /api/v1/messages` for `user+<uuid>@e2e.local` within 15 s; OAuth via PAP-224's test-mode mock provider; each asserts the same user id.
* `tenancy.spec.ts`: create org and workspace, invite, accept as a second context, switch, leave (PAP-58); `crud.spec.ts`: create, edit, list filter, delete, undo on the PAP-33 example entity; `permissions.spec.ts`: customer cannot reach `/console`, staff without role denied; `presence.spec.ts`: two contexts on one document, avatar and cursor appear within 3 s and vanish within 10 s of disconnect (PAP-141), agent badge when PAP-146 exists; skipped with reason until PAP-141 merges.
* Isolation: every test creates its own `e2e-<shard>-<worker>-<uuid>` tenant; `reset()` truncates only that prefix.
* `data-testid` convention `area.element[.modifier]` documented in `docs/quality/testing.md`; components accept `testId`.

**Interface contract**

* Provides: the `functional` project and tags, `docs/quality/testing.md` test-id convention (used by PAP-83 flows and PAP-64 UI suite), `ops/compose/preview.yml` reused by PAP-85, PAP-242 and PAP-253, `mailsink` client, `webauthn` fixture, status `gate/3-e2e`, JUnit and HTML reports.
* Requires: PAP-58 (hard), PAP-57 (hard), PAP-240 fixtures (hard), PAP-35 CRUD target, PAP-42 compose pieces, PAP-141 (soft), PAP-26 images for staging.
* Consumers: PAP-90 (first flake source, report shape), PAP-88 nightly and certification, PAP-64, PAP-253.

**Definition of done**

* Five specs pass on a PR against the ephemeral stack in under 5 minutes for `@smoke` (link).
* Nightly `@full` including the 375 run passes on staging (link).
* Seeded regression (broken tenant switch) fails with a trace attached (link).
* Traces and videos retained on failure and linked in the job summary.
* `docs/quality/testing.md` covers `pnpm e2e`, tags and test ids; changelog entry; Linear comment with report links.

**Test plan**

* The suite itself at 1280 (PR) and 375 (nightly).
* Infrastructure: Postgres health wait with a 60 s cap and readable failure; Mailpit out-of-order delivery matched by token; OAuth mock missing skips with reason.
* Isolation: two workers creating tenants concurrently never collide (slug includes shard and worker).
* Flake: `expect.poll` everywhere, no sleeps; three consecutive green `@smoke` runs.

**Demo**

Run `pnpm e2e --grep @smoke --headed` against `pnpm dev:preview` and watch sign-in, org creation, invitation acceptance in a second window and a tenant switch complete; open the HTML report. Under two minutes.

**Edge cases**

* Test-mode endpoints in production: impossible by PAP-240's guard and bundle check; Security Auditor verifies here too.
* Duplicate magic links: token match, not recipient match.
* Slow runners: generous timeouts via `expect.poll`.
* Presence not merged: spec skipped visibly, never silently passing.

**Dependencies**

PAP-58, PAP-57, PAP-240 (hard). Soft: PAP-35, PAP-42, PAP-141, PAP-146, PAP-26.

**Agent**

Sentinel (Code Reviewer writes tests) with Forge (Ops Runner) on the compose stack. Reviewed by Forge and Nova (presence).

**Size**

M.
