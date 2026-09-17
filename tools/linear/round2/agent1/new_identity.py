# New issues for the identity project: gaps and children of L issues.
# Each entry: key (stable, for idempotency), title, project, milestone, phase, type, surfaces,
# priority, size, state, blockedBy (identifiers or keys), blocks (identifiers or keys), parent (identifier), description.

P = "identity"
MS1 = "Auth works across web and desktop"
MS2 = "Roles and audiences enforced end to end"
MS3 = "Agent principals and enterprise"

GAPS = [
{
 "key": "identity/threat-model", "project": P, "milestone": MS1, "phase": "P0", "type": "Spec",
 "surfaces": ["Developer", "Agent"], "priority": 1, "size": "M", "state": "Ready for Claude",
 "blockedBy": [], "blocks": ["PAP-80", "PAP-60"],
 "title": "Write the security threat model and hardening baseline: STRIDE per trust boundary, CSP and security headers, CSRF, secret rotation runbook, incident response playbook",
 "description": """**Goal**

Write the one document every security check points at: a STRIDE threat model per trust boundary (browser, Tauri webview, API, Postgres, orchestrator, agent sessions, forges, VPS), the hardening baseline every app inherits (headers, CSP, CSRF, cookies, rate limits), a secret rotation runbook and an incident response playbook. Gate 2's security reviewer, the Semgrep local rules and Sentinel's audits check against it instead of against opinion.

**Scope**

* In: `docs/security/threat-model.md`, `docs/security/hardening-baseline.md`, `docs/security/secret-rotation.md`, `docs/security/incident-response.md`; the machine-readable control list `ops/security/controls.yaml`; a `securityHeaders()` Hono middleware in `packages/core/src/security/` that implements the baseline; a header check in Gate 1.
* Out: penetration testing, the scanners themselves (PAP-80), WAF, SOC 2 evidence collection.

**Spec**

* Trust boundaries and assets table: for each boundary list entry points, data crossing it, authentication used, STRIDE threats, existing controls, gaps with an owning issue key. The orchestrator (holds Linear, forge and Claude keys) is boundary T1 and gets its own section: key storage in sops, least-privilege bot accounts (PAP-48), per-session agent keys (PAP-60), network egress allowlist.
* Baseline: `Content-Security-Policy` with nonces (`script-src 'self' 'nonce-…'`, `connect-src` limited to API, Electric and Hocuspocus origins, `frame-ancestors 'none'`), `Strict-Transport-Security` 2 years preload, `X-Content-Type-Options`, `Referrer-Policy: strict-origin-when-cross-origin`, `Permissions-Policy` minimal, `Cross-Origin-Opener-Policy: same-origin`. CSRF: origin check on all mutating routes plus `SameSite=Lax` cookies; bearer tokens on Tauri exempt. Rate limits per route class. Cookie names and flags. Upload rules (type sniffing, SVG sanitising). Logging rules (never tokens, never full emails in prompt logs).
* `controls.yaml`: `{ id: SEC-<area>-<nn>, statement, boundary, verify: lint|test|scan|manual, owner, issues: [PAP-…] }`; at least 40 controls.
* Rotation runbook: every secret class (DB, Resend, Stripe, forge tokens, Better Auth secret, agent keys, sops age keys) with rotation steps, blast radius and the command that proves the old value is dead.
* Incident playbook: severity levels, who is paged (Justin via Needs Justin and email), containment steps per boundary, evidence to preserve, 72-hour disclosure checklist, post-mortem template.

**Interface contract**

* Provides: `securityHeaders(options)` middleware exported from `packages/core/src/security/headers.ts`; `CSP_NONCE` request-context key; `controls.yaml` consumed by PAP-80 (Semgrep rule ids reference `SEC-*`), PAP-81 (security reviewer prompt lists controls), PAP-79 (`security.md` rubric cites control ids).
* Requires: nothing at runtime; references PAP-17 secret storage and PAP-25 sops layout by path.

**Definition of done**

* Four documents merged; every trust boundary has a STRIDE table with no empty cell (gaps name an issue).
* `controls.yaml` validates against its Zod schema and has 40 or more controls, 25 with `verify: lint|test|scan`.
* `securityHeaders()` applied in `apps/api` and the header check passes in Gate 1 on the example app.
* Sentinel Security Auditor and Atlas approve; Justin reads the incident playbook and confirms the paging channel in one comment.
* Changelog entry under "Security"; Linear comment linking the model.

**Test plan**

* Unit: `securityHeaders()` sets every header from the baseline (snapshot); nonce differs per request; CSP report-only toggle works.
* Integration: Playwright loads `/` and `/auth/sign-in` at 375 and 1280 with CSP enforced, zero console CSP violations; an inline script without nonce is blocked (seeded).
* Schema: `controls.yaml` Vitest validation; every `issues` key exists in the Linear snapshot export.
* Manual: rotation runbook dry-run for the Resend key on staging, timed.

**Demo**

Open `docs/security/threat-model.md`, jump to the orchestrator boundary table, then run `curl -I https://staging.<domain>/` and read the headers; run `pnpm security:controls --verify lint` to list controls with their check status. Under two minutes.

**Edge cases**

* CSP breaks Storybook or the Pages demo: those hosts use a documented relaxed policy, never the app.
* Tauri `tauri://localhost` origin: CSP and CSRF rules list it explicitly; the model notes IPC as a boundary.
* Embedded OSS products (PAP-215) with inline scripts: allowed only behind their own route prefix with a per-route CSP.
* A control has no possible automated check: `verify: manual` with a review cadence field, never omitted.
* Model contradicts an existing spec: the spec changes; open an issue and link it from the gap cell.

**Dependencies**

None blocking. Consumers: PAP-80, PAP-81, PAP-60, PAP-106, PAP-57 children (headers and cookie flags).

**Agent**

Written by Sentinel (Security Auditor sub-agent); Forge implements the middleware. Reviewed by Atlas; Justin confirms paging.

**Size**

M: a writing task with one small middleware; the value is in completeness.
"""},
{
 "key": "identity/session-device-management", "project": P, "milestone": MS2, "phase": "P1", "type": "Build",
 "surfaces": ["Customer", "Staff"], "priority": 2, "size": "M", "state": "Backlog",
 "blockedBy": ["PAP-57"], "blocks": [],
 "title": "Build session and device management: list and revoke sessions, TOTP fallback for passkeys, account recovery codes",
 "description": """**Goal**

Give every user control and a way back in: a security page listing active sessions and devices with one-click revoke, TOTP as a second factor and as the fallback when a passkey device is lost, and single-use recovery codes. Passkey-first (PAP-57) stays the default; this issue makes it safe to rely on.

**Scope**

* In: Better Auth `twoFactor()` plugin (TOTP and backup codes), session listing and revocation through `authClient.listSessions` and `revokeSession`, device naming from user agent, `SecurityPage` component mounted in the portal (`/portal/security`, PAP-62) and console (`/console/settings/security`, PAP-63), step-up prompts for sensitive actions, email notices on new device sign-in.
* Out: SMS factors, hardware key attestation policies, enterprise MFA enforcement (PAP-65 `enforce`), impersonation history (PAP-61 owns it, the page embeds it).

**Spec**

* Server: add `twoFactor({ issuer: appName, otpOptions: { period: 30, digits: 6 }, backupCodes: { amount: 10, length: 10 } })` to `packages/auth/src/server.ts`; sessions table already has `userAgent`, `ipAddress`; add `deviceLabel` and `lastSeenAt` columns via a migration.
* Step-up: `requireRecentAuth(maxAgeSeconds = 300)` helper for oRPC procedures tagged `sensitive` (passkey delete, email change, recovery code regeneration, tenant deletion); UI opens a `ReauthDialog` that accepts passkey or TOTP.
* Recovery flow: `/auth/recover` accepts email, sends a magic link, then requires TOTP or a recovery code before allowing a new passkey to be registered; every step audited.
* Page sections: Passkeys (from PAP-57 `/auth/passkeys` component), Two-factor (enable with QR via `qrcode` package, confirm code, show codes once, regenerate), Sessions (table with device label, location from IP country only, last seen, current badge, Revoke and Revoke all others), Access history (PAP-61 embed), Sign-in alerts toggle.
* Emails: `new-device.tsx`, `two-factor-enabled.tsx`, `recovery-used.tsx` React Email templates.

**Interface contract**

* Provides: `requireRecentAuth()` in `packages/auth/src/server.ts`; `ReauthDialog` and `SecurityPage` in `packages/auth/src/ui/`; audit events `auth.session.revoked`, `auth.2fa.enabled`, `auth.recovery.used` (PAP-38 shape).
* Requires: PAP-57 server and client, `useSession`; PAP-62 and PAP-63 route slots; Resend transport from PAP-57.
* Tables: `session` (extended), `twoFactor` (plugin), `backupCode` (plugin, hashed).

**Definition of done**

* Enable TOTP, sign out, sign in with password-less magic link plus TOTP, revoke another session and see it end within one request (Playwright e2e).
* Recovery: delete the only passkey in a test, recover with a code, register a new passkey; used codes cannot be reused.
* Step-up: a sensitive procedure called with a 10-minute-old session returns 401 `REAUTH_REQUIRED`; after reauth it succeeds.
* Screenshots of the security page at 320, 375, 768, 1024, 1280, 1536, 1920 light and dark in both shells; axe clean.
* Sentinel Security Auditor signs off on code hashing and rate limits on `/auth/recover`; docs `docs/platform/account-security.md`; changelog under "Identity".

**Test plan**

* Unit: TOTP verification window (±1 step), backup code single use, device label parser for 10 user agents.
* Integration: session revocation invalidates cookie cache within `cookieCache.maxAge`; `requireRecentAuth` boundary at exactly 300 s with a fake clock.
* E2E: enable 2FA, recover, revoke; mobile 375 and desktop 1280.
* Visual: page stories at seven widths; RTL story.

**Demo**

Sign in, open `/portal/security`, enable two-factor with the QR (authenticator app or `oathtool`), open a second browser, revoke it from the first, watch it bounce to sign-in. Under two minutes.

**Edge cases**

* Time drift on the authenticator: accept one step either side, never more.
* User loses passkey and codes: support impersonation cannot bypass; documented owner-verified manual path via Needs Justin.
* Session list of 200 entries (agents): paginate, show agents in a separate tab.
* Revoking the current session: confirm dialog, then redirect to sign-in.
* Tauri bearer sessions: appear as devices with the OS name; revocation clears Stronghold on next launch.

**Dependencies**

PAP-57 (hard). Soft: PAP-62, PAP-63 (mount points), PAP-38 (audit), PAP-61 (access history embed).

**Agent**

Built by Forge (lead) with Iris (Component Crafter) on the page. Reviewed by Sentinel (Security Auditor, Visual Inspector).

**Size**

M: plugin wiring plus one dense settings page and a recovery flow.
"""},
{
 "key": "identity/privacy-dsar", "project": P, "milestone": MS3, "phase": "P2", "type": "Build",
 "surfaces": ["Customer", "Staff"], "priority": 2, "size": "M", "state": "Backlog",
 "blockedBy": ["PAP-58", "PAP-43"], "blocks": [],
 "title": "Build privacy tooling: per-user data export and erasure (DSAR), consent records, privacy/terms/cookie pages in the portal",
 "description": """**Goal**

Let a tenant answer a data subject request without engineering: export everything about one person, erase or anonymise them across every module while keeping ledgers and audit chains intact, record consent, and serve the privacy, terms and cookie pages every business needs. PAP-205 exports a tenant; this issue handles one human.

**Scope**

* In: `packages/privacy` with a subject registry (which tables hold personal data, by column), DSAR job types `privacy.export` and `privacy.erase` on the jobs queue (PAP-43), owner approval step, export bundle, anonymisation strategies, consent table and banner, legal pages with tenant-editable Markdown, request log in the console.
* Out: cookie consent for the marketing site (Webflow, PAP-193), legal text authoring, cross-border transfer assessments.

**Spec**

* Registry: `packages/privacy/src/registry.ts` collects `personalData` annotations from Drizzle schemas (`pii: 'identifier' | 'contact' | 'content' | 'financial'`) plus module registrations; `pnpm privacy:registry` prints the coverage table and fails if a column named `email|phone|name|address` lacks an annotation.
* Export: job gathers rows per registered table where `user_id` or `contact_id` matches, comments and docs authored, files owned (signed URLs), audit events as actor; renders JSON and a human-readable HTML index into a zip in object storage with a 7-day signed link; Postgres reads run under the subject's tenant with RLS.
* Erase: strategies per column `delete | null | hash | pseudonym | retain-legal`; financial documents and ledger lines keep a pseudonym (`Erased user 8f3a`) and the audit chain keeps hashes; Better Auth account deleted last; sessions revoked first. Runs as one transaction per table with a resumable checkpoint.
* Consent: table `consent_record (id, tenant_id, subject_id, purpose, granted, version, source, at)`; `ConsentBanner` for portal users on first visit; purposes declared in `app.spec.yaml` `privacy.purposes`.
* Pages: `/portal/legal/privacy`, `/terms`, `/cookies` rendering tenant Markdown from `tenant.legal jsonb` with version and effective date; console editor at `/console/settings/legal`.
* Requests: `/console/settings/privacy/requests` list with state `requested → approved → running → done`, owner approval required for erase, 30-day SLA timer.

**Interface contract**

* Provides: `registerPersonalData(table, columns)` for modules (growth CRM, business-core, collab); jobs `privacy.export`, `privacy.erase`; events `privacy.request.completed`; routes `privacy.request.create/approve/list` (oRPC).
* Requires: PAP-43 jobs, PAP-58 tenant ownership roles, PAP-37 storage, PAP-38 audit, PAP-179 pseudonym rule for ledgers.
* Tables: `privacy_request`, `consent_record`, `tenant.legal`.

**Definition of done**

* Export for a seeded user with CRM contact, comments, files and invoices yields a zip whose index lists every source table (test asserts table set equals registry).
* Erase then export yields nothing personal; the invoice PDF still renders with the pseudonym; ledger `verifyChain` passes.
* Registry coverage check fails on a seeded unannotated `phone` column.
* Console request flow and portal legal pages screenshotted at 375 and 1280, light and dark; axe clean.
* Sentinel Security Auditor reviews retention exceptions; docs `docs/platform/privacy.md`; changelog under "Identity".

**Test plan**

* Unit: strategy functions, registry validation, SLA timer.
* Integration: export and erase jobs against PGlite fixtures with three modules registered; idempotent re-run after a crash at table 3.
* E2E: owner approves a request, job completes, subject downloads the bundle.
* Visual: request list and legal page stories at seven widths.

**Demo**

In the console open Privacy requests, create an erase request for the seeded customer, approve, watch the job finish, then open that customer's invoice: the name reads `Erased user`. Under two minutes with the seeded tenant.

**Edge cases**

* Subject exists in two tenants: request is per tenant; the other tenant is untouched.
* Erase requested during an open dispute: `retain-legal` hold flag blocks with a reason.
* Files shared with others: ownership transfers to the tenant, content kept, attribution pseudonymised.
* Export larger than 2 GB: streamed zip, multipart upload.
* Consent version bumped: banner reappears once; old records kept.

**Dependencies**

PAP-58, PAP-43 (hard). Soft: PAP-37, PAP-38, PAP-179, PAP-205 (shares exporters), PAP-187 (CRM registration).

**Agent**

Built by Forge (Schema Wright) with Iris on the pages. Reviewed by Sentinel (Security Auditor) and Ledger (financial retention).

**Size**

M: registry plus two jobs and three small pages; correctness of the erase strategies is the risk.
"""},
{
 "key": "identity/tenant-api-keys-webhooks", "project": P, "milestone": MS3, "phase": "P2", "type": "Build",
 "surfaces": ["Developer"], "priority": 2, "size": "M", "state": "Backlog",
 "blockedBy": ["PAP-35", "PAP-59", "PAP-43"], "blocks": [],
 "title": "Build tenant API keys and outbound webhooks for developers: scoped keys, per-key limits, signed webhook deliveries with retries, developer settings page and generated TypeScript SDK",
 "description": """**Goal**

Give the developer audience a real surface: tenant-scoped API keys with scopes and limits, outbound webhooks with signed, retried deliveries, a developer settings page, and a generated TypeScript SDK from the OpenAPI document PAP-35 already serves. Agent keys (PAP-60) stay separate; this is for customers' own integrations.

**Scope**

* In: Better Auth `apiKey()` second key class with prefix `pos_live_` and `pos_test_`, scope model reusing `withScopes()` from PAP-60, per-key rate limits and daily quotas, `webhook_endpoint` and `webhook_delivery` tables, delivery worker on the jobs queue with HMAC signatures and exponential retries, developer page at `/console/developers`, SDK package `@paperos/sdk` generated with `openapi-typescript` plus a thin fetch client, docs.
* Out: OAuth apps and third-party marketplaces, GraphQL, per-key billing (business-core later).

**Spec**

* Keys: metadata `{ tenantId, name, scopes, environment: 'live' | 'test', createdBy }`; test keys hit the same API with `X-PaperOS-Env: test` and are limited to tenants flagged `sandbox`; scopes are `<entity>:<read|write>` strings validated against the registry of oRPC procedures (PAP-35 exposes `procedureScopes()`).
* Limits: plugin rate limit 600 requests per minute default, configurable per key; quota `requests_per_day` in `api_key.attributes`; 429 with `Retry-After`; usage counters in `api_key_usage (key_id, day, count)`.
* Webhooks: endpoint `{ id, tenant_id, url, secret, events: string[], active, failure_count }`; deliveries `{ id, endpoint_id, event, payload jsonb, attempt, status, response_code, next_at }`; signature header `PaperOS-Signature: t=<unix>,v1=<hmac-sha256>`; retries at 1 m, 5 m, 30 m, 2 h, 12 h then `active=false` with an email; events come from the domain event catalogue (`packages/core/events`, data-layer) filtered by tenant.
* Developer page: keys table (create with scope picker, shown once, revoke, last used), webhooks table (add, test-send, delivery log with redelivery), API reference link to Scalar docs.
* SDK: `pnpm sdk:build` runs `openapi-typescript` on `/api/openapi.json`, wraps in `createClient({ apiKey, baseUrl })` with typed errors and pagination helpers; published to the GitHub Packages registry per release (PAP-52).

**Interface contract**

* Provides: `requireApiKey(scopes)` oRPC middleware; `emitWebhook(event, payload, tenantId)`; `@paperos/sdk`; events `webhook.delivery.failed`.
* Requires: PAP-35 OpenAPI and procedure registry, PAP-59 `can()` and `withScopes()` via PAP-60, PAP-43 jobs, `packages/core/events` catalogue.
* Tables: `api_key` (plugin), `api_key_usage`, `webhook_endpoint`, `webhook_delivery`.

**Definition of done**

* Create a key with `invoice:read`, call the SDK, receive data; call `invoice.update` and receive 403 (Vitest integration).
* Webhook: subscribe a local receiver, trigger `invoice.paid` on the seeded tenant, receive a signed delivery; break the receiver, see five retries and deactivation (compressed schedule).
* Signature verification snippet in docs passes against real deliveries.
* Developer page screenshots at 375, 768, 1280, 1920 light and dark; axe clean.
* Sentinel Security Auditor signs off on key hashing and SSRF protections; docs `docs/platform/developers.md`; changelog under "Developer".

**Test plan**

* Unit: signature encode/verify, retry schedule, scope validation.
* Integration: quota counter rollover at midnight UTC; test key blocked on a live tenant.
* E2E: create key, test-send webhook, redeliver from the log.
* Visual: page stories at seven widths.

**Demo**

Open `/console/developers`, create a test key, run `npx tsx examples/list-invoices.ts` with it, then add a webhook to a `smee.io` URL and click Test send; the delivery appears with a 200. Under two minutes.

**Edge cases**

* Webhook URL points at private IPs or the API itself: rejected (SSRF allowlist of public ranges).
* Endpoint returns 200 slowly (over 10 s): counted as timeout, retried.
* Key used from a tenant the creator has left: keys belong to the tenant, keep working until revoked.
* Event payload contains PII of an erased user (privacy issue): deliveries older than 30 days are purged.
* SDK and API version skew: `X-PaperOS-Version` header, SDK warns on mismatch.

**Dependencies**

PAP-35, PAP-59, PAP-43 (hard). Soft: PAP-60 (scope helpers), PAP-63 (console host), data-layer events catalogue, PAP-52 (publishing).

**Agent**

Built by Forge (lead). Reviewed by Sentinel (Security Auditor) and Quill (SDK docs).

**Size**

M: two plugin-backed features and a generated SDK; the webhook worker is the only real service.
"""},
]

CHILDREN = {
"PAP-57": [
{
 "key": "identity/better-auth/server-schema-session", "type": "Build", "size": "M",
 "title": "Better Auth server, Drizzle schema merge and session helpers",
 "description": """**Goal**

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
"""},
{
 "key": "identity/better-auth/ui-pages-email", "type": "Build", "size": "M",
 "title": "Auth UI pages and magic-link email delivery",
 "description": """**Goal**

Ship the sign-in, verify, passkey management and callback pages with page specs, plus the Resend-backed magic-link email, so a human can get into any PaperOS app on the web with a passkey, a link or Google/GitHub.

**Scope**

* In: `/auth/sign-in`, `/auth/verify`, `/auth/passkeys`, `/auth/callback` in `apps/web` with specs under `specs/pages/auth/`, `packages/auth/src/client.ts` with `authClient` and hooks, React Email template `magic-link.tsx`, Resend transport with sandbox allowlist, copy file for i18n, screenshots.
* Out: server config (sibling), Tauri deep links (sibling), org pages (PAP-58).

**Spec**

* Client: `createAuthClient({ baseURL, plugins: [passkeyClient(), magicLinkClient(), bearerClient()] })`; hooks `useSession`, `useSignIn`, `useSignOut`; `SignInForm` component with passkey button (conditional UI via `PublicKeyCredential.isConditionalMediationAvailable`), email field for magic link, Google and GitHub buttons.
* Pages use design-system primitives (Button, Input, Field, Toast) and the portal layout when present; copy in `packages/auth/src/copy.ts`.
* Email: `sendMagicLink` implementation using Resend with `RESEND_API_KEY`; in `PAPEROS_ENV != production` only `*@e2e.local` and an allowlist receive mail, everything else goes to Mailpit (PAP-42).
* Errors: expired link, used link, unknown provider account, rate limited, each with a specific message and retry action.

**Interface contract**

* Provides: `authClient`, `useSession()`, `<SignInForm>`, `<PasskeyList>` (reused by session management and PAP-62), `sendMagicLink` implementation registered into the server child.
* Requires: server child; PAP-67 primitives; PAP-16 routes; Mailpit from PAP-42.

**Definition of done**

* Passkey sign-up and sign-in work in Chromium and WebKit (Playwright with virtual authenticator); magic link works via Mailpit in CI and Resend sandbox once manually.
* Google and GitHub OAuth pass with `msw`-mocked providers in CI; live GitHub run logged once.
* Four page specs validate; screenshots at 320, 375, 768, 1024, 1280, 1536, 1920 light and dark; axe zero serious.
* Email renders in React Email preview (screenshot) and in Mailpit.

**Test plan**

* Unit: form validation, error mapping table.
* E2E: three sign-in methods, expired link path, passkey cancel path.
* Visual: sign-in story at seven widths; email preview snapshot.

**Demo**

Open `/auth/sign-in` on the Pages preview, sign in with a passkey (or request a link and open Mailpit), land on `/`, open `/auth/passkeys` and add a second passkey. Under two minutes.

**Edge cases**

* Conditional UI unsupported: show the passkey button explicitly.
* Link opened on another device: landing page names the signed-in account.
* Resend outage: honest error and log, never fake success.

**Dependencies**

Sibling "Better Auth server, Drizzle schema merge and session helpers" (hard), PAP-67 (soft: proceed with unstyled primitives if late).

**Agent**

Built by Iris (Component Crafter) with Forge on the transport. Reviewed by Sentinel (Visual Inspector, Code Reviewer).

**Size**

M.
"""},
{
 "key": "identity/better-auth/tauri-session", "type": "Build", "size": "M",
 "title": "Tauri deep-link and secure-token session flow",
 "description": """**Goal**

Make the same sign-in work inside Tauri 2 on Linux and macOS: OAuth and magic links complete in the system browser, return through `paperos://auth/callback`, exchange a one-time token for a bearer session stored in the OS keychain, and survive restarts.

**Scope**

* In: deep-link registration and handling (`tauri-plugin-deep-link`), one-time token exchange endpoint `/api/auth/token`, bearer storage through the `SecretStore` interface (`tauri-plugin-stronghold` desktop, secure-storage shim mobile), client transport switch, passkey capability detection with magic-link fallback, restart persistence, startup URL handling.
* Out: web cookies (sibling), mobile store submission (PAP-20 owns).

**Spec**

* Server: `POST /api/auth/token/exchange { code }` accepts a 60-second single-use code minted at the end of OAuth or magic-link completion when the request carried `client=tauri`; returns a bearer token bound to the device name.
* Client: `authClient` gains `transport: 'bearer'` when `window.__TAURI__` exists; token read from `SecretStore.get('auth.token')` on boot, written on exchange, cleared on sign-out; `Authorization: Bearer` on every API call.
* Deep link: register scheme `paperos` in `tauri.conf.json`; handler routes `auth/callback?code=…` both at runtime and from the launch arguments (cold start).
* Passkeys: `PublicKeyCredential` undefined on WebKitGTK; the sign-in form hides the passkey button and opens the system browser for magic link or OAuth.

**Interface contract**

* Provides: `/api/auth/token/exchange`, `SecretStore` usage contract (`auth.token`), `openExternalAuth(url)` helper.
* Requires: PAP-19 desktop scaffold and deep-link plugin, PAP-17 `SecretStore` interface, sibling server child.

**Definition of done**

* Linux and macOS dev builds sign in via GitHub OAuth in the system browser and land back signed in; app restart keeps the session (video).
* Cold-start deep link (app closed) signs in correctly (test via `xdg-open paperos://…`).
* Token never appears in logs or the URL bar after exchange (grep test).
* Sign-out clears the keychain entry (assert `SecretStore.get` is null).

**Test plan**

* Unit: transport selection, code expiry and single use.
* Integration: exchange endpoint replay returns 400 `CODE_USED`.
* Manual on both OSes with recording; Windows noted as untested until a runner exists.

**Demo**

`pnpm tauri dev`, click "Continue with GitHub", finish in the browser, watch the desktop window flip to signed in; quit and relaunch, still signed in. Under two minutes.

**Edge cases**

* Deep link arrives with no pending sign-in: ignored with a toast.
* Keychain locked or unavailable: fall back to in-memory session with a warning banner.
* Two windows: token shared through the store; sign-out broadcasts via BroadcastChannel.

**Dependencies**

Sibling server child (hard), PAP-19 (hard for the desktop shell). Soft: PAP-20.

**Agent**

Built by Forge (Tauri Smith sub-agent). Reviewed by Sentinel (Security Auditor).

**Size**

M.
"""},
{
 "key": "identity/better-auth/oidc-provider", "type": "Build", "size": "S",
 "title": "OIDC provider endpoints for Forgejo SSO",
 "description": """**Goal**

Expose PaperOS as an OpenID Connect provider so Forgejo (PAP-45) and later embedded tools sign users in with their PaperOS account, removing a second password store.

**Scope**

* In: Better Auth `oidcProvider({ loginPage: '/auth/sign-in' })` plugin, client registration seed `pnpm auth:register-client forgejo`, discovery document, consent screen, Forgejo auth-source configuration snippet and runbook, tests against a standards-based client.
* Out: acting as an OIDC client for enterprise IdPs (PAP-65), SCIM.

**Spec**

* Endpoints under `/api/auth/oauth2/`: `authorize`, `token`, `userinfo`, `jwks`, and `/.well-known/openid-configuration`; scopes `openid email profile`; PKCE required for public clients; refresh tokens off for Forgejo.
* Client seed writes `oauthApplication` row with redirect URI `https://forge.<domain>/user/oauth2/paperos/callback`, prints client id and secret once, stores the secret hash.
* Consent screen page `/auth/consent` (spec under `specs/pages/auth/`) listing scopes; skipped for first-party clients flagged `trusted`.
* Claims: `sub` = user id, `email`, `email_verified`, `name`, `picture`, `groups` from tenant roles (staff flag) for Forgejo team mapping.

**Interface contract**

* Provides: discovery URL, `registerOidcClient(name, redirectUris, trusted)` script, `groups` claim shape `paperos:staff | paperos:admin`.
* Requires: sibling server child. Consumer: PAP-45 auth source, PAP-54 in-app git browsing.

**Definition of done**

* `openid-client` conformance test signs in through the provider and receives an id_token with the claims above (Vitest).
* Forgejo dev instance configured per runbook logs in with a PaperOS account (screenshot).
* JWKS rotation documented; keys stored via `SecretStore`.
* Docs `docs/platform/auth.md` section "OIDC provider".

**Test plan**

* Unit: claim mapping for staff and non-staff users.
* Integration: authorization code with PKCE, replay rejected, wrong redirect URI rejected.
* E2E: Forgejo login flow recorded once.

**Demo**

Open the Forgejo dev URL, click "Sign in with PaperOS", approve consent, land in Forgejo as the same user. Under one minute.

**Edge cases**

* User with no staff role: `groups` empty; Forgejo assigns no team.
* Clock skew: id_token `iat` tolerance 60 s documented.
* Client secret rotated: old secret invalid immediately; runbook step.

**Dependencies**

Sibling server child (hard). Soft: PAP-45 (consumer).

**Agent**

Built by Forge. Reviewed by Sentinel (Security Auditor).

**Size**

S.
"""},
],
"PAP-59": [
{
 "key": "identity/rbac-abac/model-evaluator", "type": "Build", "size": "M",
 "title": "Policy model, evaluator and explain mode",
 "description": """**Goal**

Define the policy language and the in-memory `can()` evaluator that every other layer must agree with: deny-wins, explainable, benchmarked, fully covered.

**Scope**

* In: `packages/permissions/src/model.ts` (Zod), `evaluate.ts`, `builtin-policies.ts` for the five roles, `explain()`, CLI `pnpm permissions explain`, fixtures for the built-in audiences, `tinybench` benchmark.
* Out: SQL compilation, spec adapter, middleware, hook (siblings).

**Spec**

* `Policy = { id, effect: 'allow' | 'deny', audiences: AudienceId[], actions: Action[], resource: ResourceType | '*', condition?: Condition, global?: boolean, source: { specPath, line } }`; `Action` grammar `<entity>.<verb>` with verbs `read | list | create | update | delete | export | share | impersonate | manage`, plus `page.view` and `page.action:<name>`.
* `Condition = { all } | { any } | { not } | { path, op: eq|neq|in|contains|gte|lte|isNull, ref? | value? }`; paths rooted at `resource.` or `actor.`; depth limit 8.
* `can(actor: Principal, action, resource, ctx) => Decision { allowed, matched, explain() }`; audiences resolved with `matches()` from PAP-55; order: any matching deny wins, else any allow, else deny.
* Built-in policies: owner and admin `*.manage`; staff read/list/create/update on resources tagged `staff`; member scoped read; viewer read only.
* Benchmark: median under 20 µs with 200 policies; test fails above 100 µs.

**Interface contract**

* Provides: types `Policy`, `Action`, `Condition`, `Decision`, `ResourceRef`; `can()`, `explain()`, `BUILTIN_POLICIES`, `parseAction()`.
* Requires: PAP-55 `Principal`, `AudienceId`, `matches()`.
* Consumers: siblings, PAP-60 `withScopes()`, PAP-64 tests, PAP-178 entitlements.

**Definition of done**

* 100 percent branch coverage of `evaluate.ts`; property test (`fast-check`) that adding a deny never increases allowed outcomes.
* Benchmark numbers in the PR.
* `pnpm permissions explain --actor fixtures/staff-support.json --action invoice.update --resource invoice:123` prints matched policies with spec path and line.
* `docs/platform/permissions.md` sections "Model" and "Algorithm".

**Test plan**

* Unit: every op, arrays with `contains`, `isNull`, unknown path returns false not throw, depth limit error.
* Property: 10 000 random policy sets, deny-wins invariant, determinism.
* Bench: `tinybench` run in CI as informational, threshold as a test.

**Demo**

Run the explain CLI for three fixtures (customer, support, agent) against `invoice.update` and read the three verdicts with their sources. Under one minute.

**Edge cases**

* Policy referencing an undeclared audience: load-time validation error with path.
* Resource with `tenantId` null: matches only `global: true` policies.
* Condition comparing two actor paths: allowed, documented.

**Dependencies**

PAP-55 (hard). Blocks the two sibling children.

**Agent**

Built by Forge (lead). Reviewed by Sentinel (Security Auditor, Edge Case Hunter).

**Size**

M.
"""},
{
 "key": "identity/rbac-abac/sql-compiler-rls", "type": "Build", "size": "M",
 "title": "SQL predicate compiler and RLS helpers",
 "description": """**Goal**

Compile the same policies to SQL so list endpoints filter in the database and Postgres RLS enforces the boundary even if application code forgets, with a property test proving SQL and `can()` agree.

**Scope**

* In: `compile-sql.ts` with `toPredicate()` and `toRlsPolicy()`, session-variable contract, Drizzle helpers `withPermissionFilter(query, actor, action)`, PGlite property test, migration generator for policies on core tables.
* Out: evaluator (sibling), middleware (sibling).

**Spec**

* `toPredicate(actor, action, resourceType) => SQL` produces a Drizzle `sql` fragment over the resource table's columns; actor attributes are inlined as parameters.
* `toRlsPolicy(resourceType, action) => string` emits `CREATE POLICY` using `current_setting('app.principal_id')`, `app.tenant_id`, `app.role`, `app.attrs::jsonb`; conditions on `actor.attributes.*` compile to `current_setting('app.attrs', true)::jsonb ->> key`; `contains` uses `?`.
* Column mapping: `resource.<field>` resolves through a per-table `permissionColumns` map exported next to the Drizzle table (PAP-33 convention) so renamed columns fail at typecheck.
* `pnpm permissions:rls:generate` writes `packages/db/src/rls/<table>.sql` for tables tagged `rls: true`, applied by PAP-34's harness.

**Interface contract**

* Provides: `toPredicate`, `toRlsPolicy`, `withPermissionFilter`, `permissionColumns` type; session variables `app.principal_id`, `app.tenant_id`, `app.role`, `app.attrs` (set by PAP-58 `withTenant`).
* Requires: sibling evaluator, PAP-34 session-variable harness and PGlite fixtures, PAP-33 tables.

**Definition of done**

* Property test: 10 000 random actor/resource pairs, SQL predicate result equals `can()` on PGlite for `invoices` and `files` fixtures.
* Generated RLS applied in the PAP-34 harness: cross-tenant and cross-owner reads return zero rows; writes fail.
* Unsupported condition shape produces a compile-time error naming the policy id.
* Docs section "SQL compilation".

**Test plan**

* Unit: each op to SQL snapshot; parameter binding (no string interpolation).
* Property: agreement test above.
* Integration: RLS in PGlite and in Postgres 17 (compose) nightly.

**Demo**

`pnpm permissions:rls:generate && pnpm test --filter permissions -t agreement`; open the generated `invoices.sql` and read the policy for `invoice.read`. Under two minutes.

**Edge cases**

* Policy with `in` over an empty list: compiles to `false`.
* jsonb attribute typed number vs string: compare as text with documented casting.
* Table lacks a column a policy references: typecheck failure, not runtime.

**Dependencies**

Sibling evaluator child (hard), PAP-34 (hard for the harness).

**Agent**

Built by Forge (Schema Wright). Reviewed by Sentinel (Security Auditor).

**Size**

M.
"""},
{
 "key": "identity/rbac-abac/adapter-middleware-hook", "type": "Build", "size": "M",
 "title": "Spec adapter, oRPC middleware and useCan hook",
 "description": """**Goal**

Connect the engine to the three places it is used: page specs (adapter from `access:` sections), the API (`authorize()` middleware) and the UI (`useCan()` with `PermissionProvider`), with Storybook stories that show each affordance.

**Scope**

* In: `from-spec.ts` adapter (draft shape until PAP-116 finalises), `authorize(action, resolveResource)` oRPC middleware with dev-mode explain, `PermissionProvider`, `useCan`, `hiddenWhenDenied` and `disabledWhenDenied` props on design-system Button and Menu items, policy fetch endpoint `permissions.mine`.
* Out: engine and SQL (siblings), matrix tests (PAP-64).

**Spec**

* Adapter: `accessToPolicies(section: AccessSection, source) => Policy[]`; draft `AccessSection = { view: AudienceId[], actions: Record<name, { audiences, condition? }> }` marked `@draft` and swapped when PAP-116 lands; loader reads `specs/**/page.spec.yaml` and `app.spec.yaml`.
* Middleware: `authorize('invoice.update', ({ input }) => ({ type: 'invoice', id: input.id }))` runs `can()` after `withTenant`; 403 body `{ code: 'FORBIDDEN', explain? }` with explain only when `PAPEROS_ENV !== 'production'`.
* Client: `permissions.mine` returns the actor's applicable policies (compressed); `PermissionProvider` caches per session and tenant, refetches on `session.updated` and tenant switch; `useCan(action, resource) => boolean | 'loading'`.
* Design system: Button, IconButton, Menu.Item accept `can?: { action, resource }` and apply hidden or disabled behaviour with a tooltip reason.

**Interface contract**

* Provides: `authorize()`, `PermissionProvider`, `useCan()`, `accessToPolicies()`, procedure `permissions.mine`.
* Requires: sibling evaluator; PAP-35 oRPC; PAP-58 `withTenant`; PAP-67 components; PAP-116 final shape (soft).

**Definition of done**

* 403 responses carry explain text in dev and a generic message in prod (tests).
* Fixture specs (three pages) convert to policies with correct sources; Quill confirms alignment with PAP-116.
* Storybook stories for allowed, denied-hidden, denied-disabled, loading; screenshots at 375 and 1280.
* Docs section "Using permissions".

**Test plan**

* Unit: adapter on fixture specs, invalid audience error.
* Integration: middleware with a fake resolver, tenant switch refetch.
* Visual: four stories; axe on disabled-with-tooltip.

**Demo**

Open the Storybook "Permissions" group, toggle the actor control between customer and support, watch the Delete button hide and disable; then call a denied procedure in dev and read the explain. Under two minutes.

**Edge cases**

* `useCan` before policies load: returns `'loading'`; components render disabled, never allowed.
* Resource id unknown client-side (create actions): resource `{ type }` only.
* Spec declares an action with no policy: adapter emits an explicit deny with source.

**Dependencies**

Sibling evaluator child (hard). Soft: PAP-116, PAP-35, PAP-58, PAP-67.

**Agent**

Built by Forge with Iris on component props. Reviewed by Sentinel (Code Reviewer) and Quill (spec alignment).

**Size**

M.
"""},
],
"PAP-65": [
{
 "key": "identity/sso-scim/sso-plugin-domains", "type": "Build", "size": "M",
 "title": "SSO plugin: OIDC and SAML per tenant with domain verification",
 "description": """**Goal**

Let a tenant owner connect an OIDC or SAML 2.0 identity provider and have users with verified email domains sign in through it, with JIT provisioning into the right tenant and role.

**Scope**

* In: Better Auth `sso()` plugin configuration, `ssoProvider` table extension, domain verification job, sign-in page redirect logic, SAML SP metadata and certificate rotation, OIDC with PKCE, provisioning hook, mock-IdP tests.
* Out: SCIM (sibling), console pages and enforcement (sibling).

**Spec**

* `ssoProvider` gains `tenantId`, `type: 'oidc' | 'saml'`, `domains text[]`, `enforce boolean`, `jitRole`, `groupRoleMap jsonb`, `certs jsonb` (two active certificates).
* Domain verification: `tenant_domain (tenant_id, domain, token, verified_at)`; TXT record `paperos-verify=<token>`; job `sso.verifyDomain` (PAP-43) checks `dns.resolveTxt` hourly until verified or 7 days.
* Sign-in: after the email is typed, `/api/auth/sso/lookup?email=` returns the provider for a verified domain and the form redirects; unverified domains never redirect.
* SAML: SP metadata at `/api/auth/sso/saml2/sp/metadata?tenant=<slug>`, ACS at `/api/auth/sso/saml2/callback/<providerId>`, signed assertions required, `InResponseTo` and 5-minute skew enforced.
* OIDC: discovery URL, client id and secret encrypted with the server-side secret helper (data-layer), PKCE, nonce.
* `provisionUser`: create membership in the domain's tenant with `jitRole`, map IdP groups through `groupRoleMap`.

**Interface contract**

* Provides: procedures `sso.provider.create/update/test`, `sso.domain.add/verify`, `/api/auth/sso/lookup`; events `sso.domain.verified`, `sso.login.failed`.
* Requires: PAP-57 server, PAP-58 memberships, PAP-43 jobs, server-side encryption helper.
* Tables: `ssoProvider` (extended), `tenant_domain`.

**Definition of done**

* OIDC login via `oauth2-mock-server` and SAML login via a `samlify` mock IdP pass in Playwright (video).
* Domain verification passes with a mocked resolver; unverified domain does not redirect (test).
* Expired IdP certificate fails with a clear error and no unsigned fallback.
* Sentinel Security Auditor signs off on replay protection and secret storage.

**Test plan**

* Unit: `groupRoleMap` mapping, domain normalisation, skew check.
* Integration: both protocols end to end with mocks; certificate rotation with two active certs.
* Security: assertion replay rejected; nonce mismatch rejected.

**Demo**

Add `acme.test` as a domain with the mocked resolver, configure the mock OIDC IdP, type `ada@acme.test` on the sign-in page and land signed in as a member of Acme. Under two minutes.

**Edge cases**

* Same domain claimed by two tenants: second fails with guidance.
* IdP user email exists as a customer elsewhere: staff membership added here only.
* Subdomains are distinct domains.

**Dependencies**

PAP-57, PAP-58 (hard). Soft: PAP-43. Blocks the console sibling.

**Agent**

Built by Forge (lead). Reviewed by Sentinel (Security Auditor mandatory).

**Size**

M.
"""},
{
 "key": "identity/sso-scim/scim-server", "type": "Build", "size": "M",
 "title": "SCIM 2.0 server for Users and Groups",
 "description": """**Goal**

Provide an RFC 7644 SCIM 2.0 server so Okta, Entra and similar directories create, update, deactivate and delete staff users and map groups to roles automatically.

**Scope**

* In: `apps/api/src/scim/` endpoints, per-tenant bearer tokens, filter parsing, PATCH semantics, ETags, mapping to memberships and roles, sync log, conformance fixtures from Okta and Entra documentation.
* Out: SCIM for customers, attributes beyond Users and Groups, console UI (sibling).

**Spec**

* Routes under `/scim/v2/`: `ServiceProviderConfig`, `ResourceTypes`, `Schemas`, `Users` (list with `filter` supporting `eq` on `userName` and `externalId`, `startIndex`, `count`; POST; GET; PUT; PATCH `add/replace/remove` including `active`; DELETE), `Groups` (same plus `members` patch).
* Auth: `scimToken (id, tenant_id, hash, created_by, expires_at, revoked_at)`; token shown once; 401 in SCIM error format.
* Mapping: `userName` to email; `active=false` sets `membership.suspendedAt` and revokes sessions; `externalId` stored; group membership drives roles via `groupRoleMap`.
* Responses: RFC 7644 schemas and error format; ETags with `If-Match` support; pagination defaults `count=100`.
* Sync log: `scim_request (tenant_id, at, method, path, status, body_digest)` last 1 000 kept per tenant.

**Interface contract**

* Provides: SCIM base URL per tenant, `scim.token.create/revoke` procedures, `scim_request` view for the console sibling; events `scim.user.deactivated`.
* Requires: PAP-58 memberships and roles, PAP-57 session revocation, sibling SSO child's `groupRoleMap`.
* Tables: `scimToken`, `scim_request`, `membership.externalId`, `membership.suspendedAt`.

**Definition of done**

* Fixture suite: create, update, deactivate, reactivate, delete user; create group, add member changes role; filters and pagination; all Okta and Entra fixtures pass.
* Deactivated user's sessions are revoked within one request (test).
* Wrong or revoked token returns 401 in SCIM error format.
* Property test for PATCH: applying operations then reading back equals expected document.

**Test plan**

* Unit: filter parser, PATCH path parser including `emails[type eq "work"].value`.
* Integration: full fixture replay against PGlite.
* Security: token hashing, rate limit 120 requests per minute per token.

**Demo**

Create a SCIM token, run `pnpm scim:replay fixtures/okta` against the dev API and watch the members list gain three users and one lose access. Under two minutes.

**Edge cases**

* Unsupported PATCH path: 400 `invalidPath`.
* Duplicate `userName` on POST: 409 `uniqueness`.
* Token leaked: revocation, subsequent 401, log shows last success.

**Dependencies**

PAP-58 (hard), PAP-57 (hard). Blocks the console sibling.

**Agent**

Built by Forge. Reviewed by Sentinel (Security Auditor, Edge Case Hunter with fixtures).

**Size**

M.
"""},
{
 "key": "identity/sso-scim/console-enforcement-docs", "type": "Build", "size": "M",
 "title": "Console SSO and SCIM settings pages, enforcement and enterprise docs",
 "description": """**Goal**

Make SSO and SCIM self-serve: console pages for IdP setup, domain verification, SCIM tokens and group mapping, the `enforce` option with a break-glass path, and Okta and Entra guides.

**Scope**

* In: `/console/settings/sso` and `/console/settings/scim` pages with specs, enforcement logic on sign-in, break-glass for owners with passkeys, sync log view, `docs/platform/enterprise-sso-scim.md`.
* Out: protocol implementations (siblings).

**Spec**

* SSO page: choose type, paste metadata URL or XML, download SP metadata, domain list with verification status and TXT instructions, Test login button (opens a popup, reports claims received), Enforce toggle with lockout warning.
* SCIM page: generate token (shown once), base URL, group-to-role mapping editor (grid if PAP-165 exists, else list), sync log of last 100 requests with status.
* Enforcement: when `enforce` is on for a verified domain, magic links and OAuth for that domain are refused with a message; owners with a registered passkey may still sign in locally (break-glass), audited as `auth.breakglass`.
* Docs: setup guides with screenshots for Okta and Entra, troubleshooting table.

**Interface contract**

* Provides: pages, `sso.enforcement.check(email)` used by the sign-in form, audit events `auth.breakglass`.
* Requires: sibling SSO and SCIM children, PAP-63 console host, PAP-67 components.

**Definition of done**

* Owner configures OIDC and SAML in the console and logs in via each with mock IdPs (Playwright video).
* Enforcement refuses a magic link for an enforced domain; owner break-glass works (tests).
* Screenshots of both pages at seven widths, light and dark; axe clean.
* Docs merged; changelog under "Identity".

**Test plan**

* E2E: configure, verify, test login, enforce, break-glass.
* Unit: enforcement decision table (domain verified or not, enforce on or off, owner passkey or not).
* Visual: two pages at seven widths.

**Demo**

Open `/console/settings/sso`, paste the mock IdP metadata, click Test login, see the claims; toggle Enforce and try a magic link for that domain on the sign-in page. Under two minutes.

**Edge cases**

* Enforce turned on with zero owners holding passkeys: blocked with instructions.
* Mapping editor with 500 groups: search and paging.
* Token generation twice: previous token revoked with confirmation.

**Dependencies**

Both sibling children (hard), PAP-63 (soft: mount under a temporary route if the console is late).

**Agent**

Built by Iris (Component Crafter) with Forge on enforcement. Reviewed by Sentinel (Security Auditor, Visual Inspector); Quill reviews docs.

**Size**

M.
"""},
],
}

SIBLING_BLOCKS = {
 "identity/better-auth/server-schema-session": ["identity/better-auth/ui-pages-email", "identity/better-auth/tauri-session", "identity/better-auth/oidc-provider"],
 "identity/rbac-abac/model-evaluator": ["identity/rbac-abac/sql-compiler-rls", "identity/rbac-abac/adapter-middleware-hook"],
 "identity/sso-scim/sso-plugin-domains": ["identity/sso-scim/console-enforcement-docs"],
 "identity/sso-scim/scim-server": ["identity/sso-scim/console-enforcement-docs"],
}
