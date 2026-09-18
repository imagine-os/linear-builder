---
identifier: "PAP-57"
title: "Install Better Auth with passkeys, magic link, Google/GitHub OAuth and sessions for web and Tauri"
project: "identity"
projectName: "Identity, Roles & Audiences"
phase: "P0"
type: "Build"
priority: 1
surfaces: ["Staff"]
milestone: "Auth works across web and desktop"
state: "Backlog"
parent: null
children: ["PAP-224", "PAP-225", "PAP-226", "PAP-223"]
blockedBy: ["PAP-33", "PAP-56"]
blocks: ["PAP-58", "PAP-86", "PAP-140", "PAP-220", "PAP-230", "PAP-231", "PAP-240", "PAP-511", "PAP-578", "PAP-580", "PAP-797", "PAP-815", "PAP-866", "PAP-900"]
key: "identity/better-auth"
url: "https://linear.app/paperos/issue/PAP-57/install-better-auth-with-passkeys-magic-link-googlegithub-oauth-and"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T12:56:50.551Z"
model: null
effort: null
estimate: null
dueDate: "2026-09-23"
cycle: null
---

# PAP-57: Install Better Auth with passkeys, magic link, Google/GitHub OAuth and sessions for web and Tauri

**Model / Effort:** set on children (umbrella is never claimed)

**Goal**

Install Better Auth as the one authentication server for every PaperOS app: passkeys, magic links, Google and GitHub OAuth, cookie sessions on web and bearer sessions on Tauri, an OIDC provider for Forgejo, all on the Drizzle schema from PAP-33. This issue is the umbrella for four children; it is done when the children are merged and the integration test below passes.

**Children**

1. PAP-223 Better Auth server, Drizzle schema merge and session helpers (M) - the foundation; blocks the other three.
2. PAP-224 Auth UI pages and magic-link email delivery (M).
3. PAP-225 Tauri deep-link and secure-token session flow (M).
4. PAP-226 OIDC provider endpoints for Forgejo SSO (S).

**Scope**

* In (across children): `packages/auth` server and client, schema merge, `/api/auth/*`, `requireSession()`, auth pages with specs, Resend transport, Tauri deep-link exchange and keychain storage, OIDC provider and Forgejo client seed, security settings from the hardening baseline (PAP-219).
* Out: organizations (PAP-58), agent keys (PAP-60), session management and 2FA (PAP-220), SSO client and SCIM (PAP-65).

**Spec**

Detailed specs live in the children. Cross-child rules that must hold:

* One `user` table: Better Auth's `user` is the core `users` entity (same UUID) with `principalType` and `attributes jsonb`; no second user table anywhere.
* One principal type: `Principal` from PAP-55 is what `requireSession()` returns; PAP-35 imports it.
* Versions come from PAP-56's `versions.json`; no child bumps independently.
* Copy lives in `packages/auth/src/copy.ts`; cookie and header settings follow PAP-219.

**Interface contract**

* Provides: `auth` server instance and `authClient`; `getSession(request)`, `requireSession(ctx)`, `useSession()`, `useSignIn()`, `useSignOut()`; `<SignInForm>`, `<PasskeyList>`; routes `/api/auth/*`, `/api/auth/token/exchange`, `/api/auth/oauth2/*`, `/.well-known/openid-configuration`; `AuditSink` interface; deep-link scheme `paperos://auth/callback`; `SecretStore` key `auth.token`.
* Requires: PAP-33 `users`, PAP-32 migrations, PAP-56 versions, PAP-17 env schema and `SecretStore`, PAP-19 deep-link plugin, PAP-67 primitives (soft), PAP-42 Mailpit.
* Tables: `user` (merged), `session`, `account`, `verification`, `passkey`, `oauthApplication`, `oauthAccessToken`.
* Consumers: PAP-58, PAP-59 adapter, PAP-60, PAP-86, PAP-140 auth hook, PAP-240 `login-as`, PAP-45 OIDC.

**Definition of done**

* All four children Done and their DoDs verified by Sentinel.
* Integration test (below) green in CI on the ephemeral stack and once manually on Tauri Linux and macOS (video attached).
* `docs/platform/auth.md` complete with a Mermaid flow diagram covering web, Tauri and OIDC; changelog entry under "Identity".
* Linear comment with the Pages demo link (mock mode), the Tauri video and the Forgejo login screenshot.

**Test plan**

Integration test `apps/web/e2e/functional/auth-umbrella.spec.ts` plus API tests:

* Web: passkey sign-up (virtual authenticator) then sign-out then magic-link sign-in via Mailpit then GitHub OAuth via mocked provider; each yields a session whose principal has `type: 'human'` and the same user id.
* API: `requireSession()` 401 without credentials, 200 with cookie and with bearer; the 11th sign-in attempt in a minute returns 429.
* Tauri: bearer exchange after deep link; restart persistence; sign-out clears `SecretStore`.
* OIDC: `openid-client` conformance flow yields an id_token with `sub`, `email`, `groups`.
* Visual: `/auth/sign-in` at 320, 375, 768, 1024, 1280, 1536, 1920 light and dark; axe zero serious.

**Demo**

On the Pages preview sign in with a passkey, sign out, request a magic link and open it from Mailpit; then click "Sign in with PaperOS" on the Forgejo dev instance and land there as the same user. Under two minutes.

**Edge cases**

Cross-child: a user created by OIDC consent before the UI child merges must still see the consent page unstyled rather than fail; the Tauri child must work when the UI child's copy file is missing (fallback strings); version drift between children is caught by a `versions.json` check in Gate 1.

**Dependencies**

PAP-33, PAP-56 (hard). Soft: PAP-17, PAP-19, PAP-35, PAP-67, PAP-45. Blocked by PAP-219 for header and cookie settings only (soft; adopt defaults if late).

**Agent**

Forge leads (Tauri Smith for PAP-225); Iris (Component Crafter) on PAP-224. Sentinel (Security Auditor mandatory) reviews every child and runs the umbrella test.

**Size**

L, split into 4 children (M, M, M, S).
