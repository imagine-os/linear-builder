---
identifier: "PAP-57"
title: "Install Better Auth with passkeys, magic link, Google/GitHub OAuth and sessions for web and Tauri"
project: "identity"
projectName: "Identity, Roles & Audiences"
phase: "P0"
type: "Build"
priority: 1
surfaces: ["Customer", "Staff"]
milestone: "Auth works across web and desktop"
state: "Backlog"
parent: null
children: ["PAP-224", "PAP-225", "PAP-226", "PAP-223"]
blockedBy: ["PAP-33", "PAP-56"]
blocks: ["PAP-140", "PAP-220", "PAP-240", "PAP-58", "PAP-86"]
key: "identity/better-auth"
url: "https://linear.app/paperos/issue/PAP-57/install-better-auth-with-passkeys-magic-link-googlegithub-oauth-and"
source: "plan/specs/bucket-1.json (round-1 canonical spec JSON)"
---

# PAP-57: Install Better Auth with passkeys, magic link, Google/GitHub OAuth and sessions for web and Tauri

**Goal**

Install Better Auth as the one authentication server for every PaperOS app: passkeys, magic links, Google and GitHub OAuth, cookie sessions on web and secure token sessions on Tauri desktop and mobile, backed by the Drizzle schema from data-layer/core-entities. Every later identity issue plugs into this package.

**Scope**

- In: `packages/auth` (server config, Drizzle adapter, plugins, client), API mounting, email delivery for magic links, Tauri deep-link flow and secure token storage, sign-in/sign-up/verify UI pages, session helpers for oRPC procedures, OIDC provider endpoints for Forgejo SSO, tests.
- Out: organizations and invitations (identity/org-tenancy), API keys for agents (identity/agent-principals), SSO client and SCIM (identity/sso-scim), billing.

**Spec**

In `imagine-os/paperos-template`:

- `packages/auth/src/server.ts`: `betterAuth({ database: drizzleAdapter(db, { provider: 'pg' }), plugins: [passkey(), magicLink({ sendMagicLink }), oidcProvider({ loginPage: '/auth/sign-in' }), bearer(), openAPI()], socialProviders: { google, github }, session: { expiresIn: 30d, updateAge: 1d, cookieCache: { enabled: true, maxAge: 5m } }, advanced: { cookiePrefix: 'paperos', useSecureCookies: true }, trustedOrigins: [web origin, 'paperos://', 'tauri://localhost', 'http://tauri.localhost'] })`. Use the versions recorded by identity/auth-research. Email via Resend (`RESEND_API_KEY` from app-shell/env-config) with a React Email template in `packages/auth/emails/magic-link.tsx`.
- Schema: run `npx @better-auth/cli generate` into `packages/db/src/schema/auth.ts`, then adapt so `user` extends the `users` core entity from data-layer/core-entities rather than duplicating it (`user.id` is the same UUID; add columns `principalType` default `human`, `attributes jsonb`). Migration via drizzle-kit in the standard workflow.
- Mounting: `apps/api/src/routes/auth.ts` mounts `auth.handler` at `/api/auth/*`; oRPC context builder `getSession(request)` attaches `{ session, user, principal }` (principal built with `packages/core` audience types); helper `requireSession()` throws 401.
- Client: `packages/auth/src/client.ts` exports `authClient = createAuthClient({ baseURL, plugins: [passkeyClient(), magicLinkClient(), bearerClient()] })` and React hooks `useSession`, `useSignIn`, `useSignOut`; on Tauri the client uses bearer tokens stored via `tauri-plugin-stronghold` (desktop) or the mobile secure-storage shim from app-shell/tauri-mobile, exposed through the `SecretStore` interface defined in app-shell/env-config.
- Tauri flow: OAuth and magic links open the system browser; the callback redirects to `paperos://auth/callback?token=...`, handled by `tauri-plugin-deep-link`, which exchanges the one-time token for a session via `/api/auth/token`. Passkeys are attempted in-webview and fall back to magic link when `PublicKeyCredential` is undefined (Linux WebKitGTK).
- Pages (apps/web, with page specs under `specs/pages/auth/`): `/auth/sign-in` (passkey button, email for magic link, Google and GitHub buttons), `/auth/verify` (magic link landing), `/auth/passkeys` (manage passkeys), `/auth/callback`. Components from design-system primitives; copy in `packages/auth/src/copy.ts` for later i18n.
- OIDC provider: register a client for Forgejo (`forge/forgejo-deploy` SSO switch) via a seed script `pnpm auth:register-client forgejo`; scopes `openid email profile`.
- Security: rate limit `/api/auth/*` (Better Auth built-in, 10 requests/minute per IP on sign-in routes), CSRF via origin check, `SameSite=Lax` cookies, session revocation on password-less account deletion, audit hook posting `auth.signin`, `auth.signout`, `auth.passkey.added` to data-layer/audit-log when available (else `console` sink behind an interface).

**Definition of done**

- Sign-up and sign-in with passkey work in Chrome and Safari; magic link works end to end with Resend sandbox; Google and GitHub OAuth work on web (Playwright e2e with recorded OAuth via `msw` for CI, live run once manually and logged).
- Tauri desktop (Linux, macOS) signs in via deep link and persists the session across restarts; Linux falls back to magic link when passkeys are unavailable (video attached).
- `requireSession()` returns 401 without a session and a typed principal with one (Vitest).
- Forgejo OIDC login succeeds against the provider endpoints (screenshot).
- Page specs validate; Playwright screenshots of `/auth/sign-in` at 320, 375, 768, 1024, 1280, 1536, 1920 light and dark.
- axe has no serious violations on auth pages.
- Docs `docs/platform/auth.md` (setup, env vars, flows diagram in Mermaid) merged; changelog entry under "Identity".
- Linear comment with the Pages demo link (mock mode) and video.

**Edge cases**

- Magic link opened on a different device than requested: Better Auth verifies by token, not device; the landing page states which account was signed in.
- Passkey registration cancelled midway: no orphan credential; UI returns to the sign-in state with a retry.
- Deep link received while the Tauri app is closed: the OS launches the app; the client handles the URL on startup, not only at runtime.
- Clock skew on a client breaks JWT-style checks: sessions are database-backed; document that OIDC id_tokens allow 60 s skew.
- User exists with email but tries Google OAuth with the same email: account linking enabled only for verified emails; otherwise prompt to sign in with the original method.
- Resend outage: the sign-in page shows a retry message and logs the failure; no fake success.

**Dependencies**

- data-layer/core-entities (user table to extend), identity/auth-research (versions and Tauri findings). Soft: app-shell/env-config (secrets), app-shell/tauri-desktop (deep-link plugin), data-layer/api-layer (oRPC context), design-system/primitives, forge/forgejo-deploy (OIDC consumer).

**Agent**

- Builds: Forge (lead) with the Tauri Smith sub-agent for native flows; Iris (Component Crafter) polishes the auth pages.
- Reviews: Sentinel (Security Auditor mandatory, Code Reviewer, Visual Inspector).

**Size**

L: several login methods across three platforms plus an OIDC provider, all security-sensitive.
