---
identifier: "PAP-223"
title: "Better Auth server, Drizzle schema merge and session helpers"
project: "identity"
projectName: "Identity, Roles & Audiences"
phase: "P0"
type: "Build"
priority: 1
surfaces: ["Customer", "Staff"]
milestone: "Auth works across web and desktop"
state: "Backlog"
parent: "PAP-57"
children: []
blockedBy: ["PAP-33", "PAP-56"]
blocks: ["PAP-224", "PAP-225", "PAP-226", "PAP-458"]
key: "identity/better-auth/server-schema-session"
url: "https://linear.app/paperos/issue/PAP-223/better-auth-server-drizzle-schema-merge-and-session-helpers"
source: "Linear snapshot 2026-09-17T15:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T13:42:01.604Z"
model: "claude-opus-5"
effort: "high"
---

# PAP-223: Better Auth server, Drizzle schema merge and session helpers

**Model / Effort:** Opus 5 (`claude-opus-5`) / high — security-sensitive title keyword: Auth

**Goal**

Stand up the Better Auth server in `packages/auth` on the Drizzle schema, merged with the core `users` entity, and expose the session helpers every oRPC procedure uses. This child is the foundation the other three PAP-57 children plug into.

**Scope**

* In: `packages/auth/src/server.ts` configuration, generated schema adapted to core `users`, migration, `/api/auth/*` mounting, `getSession()` and `requireSession()`, `Principal` construction, audit hook interface, rate limits and cookie settings from the hardening baseline.
* Out: UI pages, emails, Tauri flow, OIDC provider (siblings).

**Spec**

* `betterAuth({ database: drizzleAdapter(db, { provider: 'pg' }), plugins: [passkey(), magicLink({ sendMagicLink }), bearer(), openAPI()], socialProviders: { google, github }, session: { expiresIn: 30d, updateAge: 1d, cookieCache: { enabled: true, maxAge: 5m } }, advanced: { cookiePrefix: 'paperos', useSecureCookies: true }, trustedOrigins })`; versions from PAP-56.
* Schema: `npx @better-auth/cli generate` into `packages/db/src/schema/auth.ts`; `user` extends core `users` (same UUID, adds `principalType` default `human`, `attributes jsonb`); one drizzle-kit migration.
* Mount at `/api/auth/*` in `apps/api/src/routes/auth.ts`; oRPC context builder attaches `{ session, user, principal }`; `requireSession()` throws 401 `UNAUTHENTICATED`.
* `sendMagicLink` and `socialProviders` are injected so siblings supply the real implementations; a `console` sink is the default in tests.
* Audit: `onSignIn`, `onSignOut`, `onPasskeyAdded` hooks post `auth.*` events to an `AuditSink` interface (PAP-38 implements it later).

**Interface contract**

* Provides: `auth` instance, `getSession(request)`, `requireSession(ctx)`, `Principal` (from `packages/core/src/audience`, PAP-55), `AuditSink` interface, `AuthConfig` injection points (`sendMagicLink`, `secretStore`).
* Requires: PAP-33 `users` table, PAP-32 migrations, `RESEND_API_KEY` and OAuth secrets via PAP-17 env schema.
* Tables: `user` (merged), `session`, `account`, `verification`, `passkey`.

**Definition of done**

* Migration applies cleanly on an empty database and on the PAP-33 seed; `user` has no duplicate columns.
* `requireSession()` returns 401 without a cookie or bearer and a typed principal with one (Vitest).
* Passkey registration and sign-in pass through the server with a virtual authenticator (Playwright API-level test).
* Rate limit on sign-in routes returns 429 on the 11th request in a minute.
* `docs/platform/auth.md` section "Server" merged.

**Test plan**

* Unit: principal builder for human and agent users; cookie flags snapshot.
* Integration: sign-in, session refresh at `updateAge`, sign-out revocation, bearer header path.
* Security: cookie `Secure`, `HttpOnly`, `SameSite=Lax` asserted; origin mismatch rejected.

**Demo**

`pnpm dev:api`, then `curl -X POST /api/auth/sign-in/magic-link -d '{"email":"a@e2e.local"}'` and read the link from the console sink; visit it, call `GET /api/rpc/me` and see the principal JSON. Under two minutes.

**Edge cases**

* Existing `users` row without an auth account: sign-in via magic link links it by verified email.
* Database-backed sessions and clock skew: no JWT verification in this child.
* Two API instances: cookie cache is per instance; revocation is seen within 5 minutes worst case (documented).

**Dependencies**

PAP-33, PAP-56 (hard). Blocks the three sibling children.

**Agent**

Built by Forge (lead). Reviewed by Sentinel (Security Auditor).

**Size**

M.
