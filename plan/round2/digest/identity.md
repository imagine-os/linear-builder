# identity — Identity, Roles & Audiences
PHASE P0 prio 1 dependsOn ['data-layer']
SUMMARY: Better Auth with passkeys and organizations, a role+attribute permission engine driven by page specs, and audiences from customer tiers to staff to agents.
DESC: Goal: any app knows exactly who is acting, which tenant they belong to and what they may do, whether they are a customer, a staff member, a partner, an admin or a Claude agent. Better Auth provides passkeys, magic links, OAuth and organizations across web and Tauri. The audience model treats segments as composable so 'everything in between' is a configuration, not a rewrite. The permission engine combines roles with attribute policies declared in page specs, backed by Postgres RLS, and permission matrix tests are generated from those specs. Agents are first-class principals with scoped keys and visible attribution. Separate customer portal and staff console shells demonstrate the split. Non-goals: building our own auth protocol or password storage.
MILESTONES: ['Auth works across web and desktop 2026-09-20: Sign-in, sessions, organizations and audience model defined', 'Roles and audiences enforced end to end 2026-09-25: Permission engine, impersonation, portal and console shells', 'Agent principals and enterprise 2026-09-30: Agent keys, permission tests, SSO/SCIM']


## PAP-55 [P0 Spec M prio1 Ready for Claude] Specify the audience model: customer tiers, staff roles, partners, admins, agents and composable segments in between
key=identity/audience-model milestone=Auth works across web and desktop agent=* Builds: Quill (Page Spec Writer sub-agent) for the model d
blockedBy=[] blocks=['PAP-59']
GOAL: Define the single vocabulary every page spec, policy, view and campaign uses to say who: principal types, tenant roles, customer tiers, partners, admins, agents, and composable segments for everything in between. Ship it as a typed schema and a document so specs are validated against real audience names rather than free text.
SCOPE: * In: the audience model document, Zod schema and TypeScript types in `packages/core`, the segment expression language, seed audiences for the template app, and the `audiences` section shape for `app.spec.yaml`.
* Out: evaluating permissions (identity/rbac-abac), storing memberships (identity/org-tenancy), and marketing segments over behavioural data (growth/segments extends this model with usage attributes).
SPEC(first 1200): Document `docs/specs/audience-model.md` and code in `packages/core/src/audience/`:

* `principal.ts`: `PrincipalType = 'human' | 'agent' | 'service' | 'anonymous'`. A `Principal` has `id`, `type`, `tenantId | null`, `attributes: Record<string, string | number | boolean | string[]>` (for example `tier`, `staffRole`, `partnerId`, `character`, `emailVerified`, `mfa`).
* `role.ts`: tenant roles as a fixed enum `owner | admin | staff | member | viewer` (maps to Better Auth organization roles in identity/org-tenancy); optional custom roles per tenant are named strings that must extend one of the five as a base.
* `audience.ts`: an `Audience` is `{ id: kebab-case, name, description, match: Segment }`. `Segment` is a recursive expression: `{ all: Segment[] } | { any: Segment[] } | { not: Segment } | { attr: string, op: 'eq' | 'neq' | 'in' | 'gte' | 'lte' | 'exists', value }` plus shorthand leaves `{ role: TenantRole }`, `{ principalType: PrincipalType }`, `{ tier: string }`. Depth limited to 6; evaluated in under 50 microseconds per principal by `matches(principal, segment)` (pure function, no I/O).
* Built-in audiences exported as `BUILTIN_AUDIENCES`: `anonymous`, `authenticated`, `custom
DOD:
* `packages/core/src/audience` exports schemas, types, `matches`, `describe`, `BUILTIN_AUDIENCES`; typecheck and Biome clean.
* Vitest: 100 per cent branch coverage of `matches`, cycle detection test, depth-limit test, property-based test with `fast-check` that `not(not(x))` equals `x` for random principals.
* Document merged with a table of built-in audiences and worked examples for "customer who is also a partner" and "agent acting for a staff member".
* `app.spec.yaml` shape documented and referenced by spec-builder/app-level-spec (comment left on that issue).
* Sentinel Code Reviewer and Quill approve; Atlas confirms agent audience matches agents/character-schema fields.
* Storybook or docs page not required; Linear comment with the doc link and coverage report.
* Changelog entry under "Platform".
EDGE:
* Principal belongs to several tenants: `Principal` is always tenant-scoped; multi-tenant users are represented as one principal per active tenant (identity/org-tenancy sets it).
* Attribute is an array (`staffRole: ['support', 'finance']`): `eq` on arrays matches any element; `in` intersects; documented.
* Unknown attribute referenced in a segment: `exists` returns false, other ops return false (never throw); `spec validate` warns.
* Anonymous principal with a tenant (public portal page): allowed; `anonymous` audience ignores tenantId.
* Agent impersonating a human (identity/impersonation): principal carries `actingFor` attribute; built-in `agent` still matches, and the model documents that policies must check `actingFor` explicitly.
* Tier names differ per app (clinic uses `plan: basic`): apps map their own attributes in `app.spec.yaml`; built-in tiers are examples, not requirements.
DEPS: * None blocking. Consumers: identity/rbac-abac, spec-builder/access-section, spec-builder/app-level-spec, identity/staff-console-shell (audience filters), growth/segments, agents/character-schema.


## PAP-56 [P0 Research S prio2 Ready for Claude] Compare Better Auth, Lucia, Clerk and Auth.js for self-hosting, organizations and passkeys; write ADR
key=identity/auth-research milestone=Auth works across web and desktop agent=* Builds: Scout (Library Evaluator sub-agent) drives the com
blockedBy=[] blocks=['PAP-57']
GOAL: Confirm the auth choice before it is wired into every surface: compare Better Auth, Lucia, Clerk and Auth.js against PaperOS's hard requirements (self-hosting, organizations, passkeys, Tauri support, agent API keys, OIDC provider for Forgejo SSO) with a hands-on spike, and record the result as an ADR that identity/better-auth executes.
SCOPE: * In: rubric-based comparison, a minimal spike per finalist proving passkeys and organization membership in a web app and in a Tauri 2 webview on Linux and macOS, the ADR, and a list of plugins and versions to adopt.
* Out: production wiring (identity/better-auth), SSO/SCIM depth (identity/sso-scim, though the ADR must note each candidate's path).
SPEC(first 1200): Deliverables in `imagine-os/paperos-template`:

* `docs/decisions/ADR-000X-authentication.md` (next free number) in the MADR format used by forge/vcs-decision-adr, with a comparison table scored on the libraries/eval-rubric criteria plus these requirement columns: self-hostable with Postgres (hard), organizations/teams plugin, passkeys (WebAuthn) registration and login, magic link, Google and GitHub OAuth, session strategy suitable for Tauri (bearer token or cookie in webview), API keys for agents, OIDC/OAuth2 provider capability (needed by forge/forgejo-deploy), SAML/OIDC SSO client for enterprise, SCIM story, TypeScript quality, licence, weekly npm downloads and last release date (with retrieval date), Drizzle adapter availability.
* Spike directory `spikes/auth/` (excluded from the production build via `pnpm` workspace ignore) with one sub-folder per finalist that reaches the spike stage (at minimum Better Auth and one alternative): a Vite React page with sign-up via passkey, sign-in via magic link (console-logged), create organization, invite member, switch active organization; run in the browser and inside a Tauri 2 dev window. Record findings, notably WebAuthn availability in
DOD:
* ADR merged with status Accepted (or Proposed and moved to Needs Justin if the recommendation differs from the plan's Better Auth decision).
* Comparison table complete for all four candidates, every cell filled or marked "not verified" with reason.
* Spike code committed under `spikes/auth/` with a README describing how to run each in browser and Tauri; screenshots at 1280 (web) and the Tauri window on Linux and macOS attached.
* Passkey behaviour in Tauri on Linux and macOS documented with the fallback decision.
* Package and plugin list with versions and Drizzle adapter compatibility recorded.
* Sentinel Security Auditor reviews the session and token handling notes; Scout (Library Evaluator) reviews rubric scoring.
* Linear comment summarising the recommendation in five lines; changelog entry under "Docs".
EDGE:
* A candidate has no Drizzle adapter: score it but note the maintenance burden of a custom adapter.
* Passkeys work in browser but not in the Tauri webview: this is expected on Linux; the ADR must still recommend a passkey-first design with graceful fallback, not abandon passkeys.
* Better Auth releases a breaking version during the spike: pin the version tested and note the migration guide.
* Rate limits on Google OAuth test app: use GitHub OAuth for the spike and document Google as configured but unverified.
* Justin already has strong preference from the plan: the ADR still needs evidence; if evidence contradicts the plan, escalate to Needs Justin rather than silently agree.
DEPS: * None blocking. Soft: libraries/eval-rubric (criteria), libraries/backend-landscape (shares findings; link both ways). Consumer: identity/better-auth.


## PAP-57 [P0 Build L prio1 Backlog] Install Better Auth with passkeys, magic link, Google/GitHub OAuth and sessions for web and Tauri
key=identity/better-auth milestone=Auth works across web and desktop agent=* Builds: Forge (lead) with the Tauri Smith sub-agent for na
blockedBy=['PAP-56', 'PAP-33'] blocks=['PAP-140', 'PAP-58']
GOAL: Install Better Auth as the one authentication server for every PaperOS app: passkeys, magic links, Google and GitHub OAuth, cookie sessions on web and secure token sessions on Tauri desktop and mobile, backed by the Drizzle schema from data-layer/core-entities. Every later identity issue plugs into this package.
SCOPE: * In: `packages/auth` (server config, Drizzle adapter, plugins, client), API mounting, email delivery for magic links, Tauri deep-link flow and secure token storage, sign-in/sign-up/verify UI pages, session helpers for oRPC procedures, OIDC provider endpoints for Forgejo SSO, tests.
* Out: organizations and invitations (identity/org-tenancy), API keys for agents (identity/agent-principals), SSO client and SCIM (identity/sso-scim), billing.
SPEC(first 1200): In `imagine-os/paperos-template`:

* `packages/auth/src/server.ts`: `betterAuth({ database: drizzleAdapter(db, { provider: 'pg' }), plugins: [passkey(), magicLink({ sendMagicLink }), oidcProvider({ loginPage: '/auth/sign-in' }), bearer(), openAPI()], socialProviders: { google, github }, session: { expiresIn: 30d, updateAge: 1d, cookieCache: { enabled: true, maxAge: 5m } }, advanced: { cookiePrefix: 'paperos', useSecureCookies: true }, trustedOrigins: [web origin, 'paperos://', 'tauri://localhost', 'http://tauri.localhost'] })`. Use the versions recorded by identity/auth-research. Email via Resend (`RESEND_API_KEY` from app-shell/env-config) with a React Email template in `packages/auth/emails/magic-link.tsx`.
* Schema: run `npx @better-auth/cli generate` into `packages/db/src/schema/auth.ts`, then adapt so `user` extends the `users` core entity from data-layer/core-entities rather than duplicating it (`user.id` is the same UUID; add columns `principalType` default `human`, `attributes jsonb`). Migration via drizzle-kit in the standard workflow.
* Mounting: `apps/api/src/routes/auth.ts` mounts `auth.handler` at `/api/auth/*`; oRPC context builder `getSession(request)` attaches `{ se
DOD:
* Sign-up and sign-in with passkey work in Chrome and Safari; magic link works end to end with Resend sandbox; Google and GitHub OAuth work on web (Playwright e2e with recorded OAuth via `msw` for CI, live run once manually and logged).
* Tauri desktop (Linux, macOS) signs in via deep link and persists the session across restarts; Linux falls back to magic link when passkeys are unavailable (video attached).
* `requireSession()` returns 401 without a session and a typed principal with one (Vitest).
* Forgejo OIDC login succeeds against the provider endpoints (screenshot).
* Page specs validate; Playwright screenshots of `/auth/sign-in` at 320, 375, 768, 1024, 1280, 1536, 1920 light and dark.
* axe has no serious violations on auth pages.
* Docs `docs/platform/auth.md` (setup, env vars, flows diagram in Mermaid) merged; changelog entry under "Identity".
* Linear comment with the Pages demo link (mock mode) and video.
EDGE:
* Magic link opened on a different device than requested: Better Auth verifies by token, not device; the landing page states which account was signed in.
* Passkey registration cancelled midway: no orphan credential; UI returns to the sign-in state with a retry.
* Deep link received while the Tauri app is closed: the OS launches the app; the client handles the URL on startup, not only at runtime.
* Clock skew on a client breaks JWT-style checks: sessions are database-backed; document that OIDC id_tokens allow 60 s skew.
* User exists with email but tries Google OAuth with the same email: account linking enabled only for verified emails; otherwise prompt to sign in with the original method.
* Resend outage: the sign-in page shows a retry message and logs the failure; no fake success.
DEPS: * data-layer/core-entities (user table to extend), identity/auth-research (versions and Tauri findings). Soft: app-shell/env-config (secrets), app-shell/tauri-desktop (deep-link plugin), data-layer/api-layer (oRPC context), design-system/primitives, forge/forgejo-deploy (OIDC consumer).


## PAP-58 [P0 Build M prio1 Backlog] Implement organizations, workspaces, invitations and tenant switching
key=identity/org-tenancy milestone=Auth works across web and desktop agent=* Builds: Forge (Schema Wright sub-agent) for schema and mid
blockedBy=['PAP-57'] blocks=['PAP-177', 'PAP-86', 'PAP-65', 'PAP-63', 'PAP-62']
GOAL: Implement multi-tenant membership on top of Better Auth: organizations are tenants, workspaces are teams inside them, members are invited by email, and users switch the active tenant with every request and RLS policy following. This makes the tenant boundary from data-layer/rls-tenancy real for users rather than only for tests.
SCOPE: * In: Better Auth organization plugin configuration, tenant and workspace mapping to core entities, invitation flow with email, tenant switcher component and hook, per-request tenant context for API and RLS, ownership transfer, tenant deletion with grace period, tests and pages.
* Out: role and permission evaluation beyond the built-in five roles (identity/rbac-abac), enterprise SSO/SCIM (identity/sso-scim), billing per tenant (business-core/stripe-billing).
SPEC(first 1200): In `imagine-os/paperos-template`:

* Plugin: add `organization({ teams: { enabled: true, maximumTeams: 50 }, allowUserToCreateOrganization: true, organizationLimit: 10, creatorRole: 'owner', roles: { owner, admin, staff, member, viewer } via access control `createAccessControl` , sendInvitationEmail })` to the server in `packages/auth`; client plugin `organizationClient()`.
* Schema mapping: Better Auth `organization` maps onto the `tenants` table and `team` onto `workspaces` from data-layer/core-entities; use the plugin's `schema` option to rename tables and fields so there is one table per concept, not two. `membership` gains `role` (enum above) and `attributes jsonb` (staffRole, tier) consumed by the audience model. Add `slug` unique per tenant, `logoFileId` (data-layer/file-storage), `deletedAt` for grace period.
* Active tenant: stored in the session (`session.activeOrganizationId`); oRPC middleware `withTenant` reads it, verifies membership, and runs `SET LOCAL app.tenant_id = $1; SET LOCAL app.principal_id = $2; SET LOCAL app.role = $3` inside the request transaction so data-layer/rls-tenancy policies apply. Requests with no active tenant to tenant-scoped procedures return 4
DOD:
* Create tenant, create workspace, invite, accept, switch tenant and leave flows pass Playwright e2e (feeding quality/e2e-flows) and Vitest API tests.
* Cross-tenant test: a member of tenant A calling a tenant-scoped procedure with tenant B's id gets 403; RLS test from data-layer/rls-tenancy passes with the session variables set by `withTenant`.
* Invitation email renders (React Email preview screenshot) and expired tokens show a clear message.
* Screenshots of `/org/settings/members` and `TenantSwitcher` open at the seven widths, light and dark.
* axe clean on all org pages; keyboard-only switcher usage verified.
* `docs/platform/tenancy.md` with a sequence diagram of tenant context propagation; changelog entry under "Identity".
* Sentinel Security Auditor signs off on the middleware; Linear comment with demo link and e2e video.
EDGE:
* User invited to a tenant they already belong to: invitation accepted as a role update only if the inviter's role permits raising roles; otherwise no-op with a message.
* Invitation email address differs in case from the sign-in email: compare case-insensitively after normalisation.
* Active tenant deleted while a session is open: middleware returns 412 and the client redirects to `/org/switch`.
* User has 0 tenants after leaving: redirected to `/org/new` with the option to accept pending invitations.
* Slug collision with a reserved word (`api`, `admin`, `auth`, `dev`): reserved list enforced server-side and suggested alternative shown.
* Two tabs with different active tenants: session is server-side per device, so both share one active tenant; the second tab receives a `tenantChanged` BroadcastChannel event (realtime/multi-window-sync) and reloads its data.
DEPS: * identity/better-auth (server and client). Soft: data-layer/core-entities and data-layer/rls-tenancy (tables and policies), data-layer/api-layer (middleware), design-system/primitives, data-layer/file-storage (logos).


## PAP-59 [P0 Build L prio1 Backlog] Build permission engine combining role-based grants with attribute policies declared in page specs
key=identity/rbac-abac milestone=Auth works across web and desktop agent=* Builds: Forge (lead) with Schema Wright for SQL compilatio
blockedBy=['PAP-34', 'PAP-55'] blocks=['PAP-178', 'PAP-172', 'PAP-131', 'PAP-64', 'PAP-61', 'PAP-60']
GOAL: Build the permission engine every layer shares: one `can(actor, action, resource, context)` that combines role-based grants with attribute policies declared in page specs, evaluates identically in the API, compiles to SQL predicates for Postgres RLS and where-clauses, and drives UI affordances through a `useCan` hook. Deny by default, explainable on request.
SCOPE: * In: `packages/permissions` with the policy model, evaluator, SQL compiler, spec loader, explain mode, React hook, oRPC middleware, Drizzle RLS helpers, fixtures and benchmarks.
* Out: the access-section YAML format itself (spec-builder/access-section defines it; this issue consumes it via an adapter), agent keys (identity/agent-principals), generated matrix tests (identity/permission-tests).
SPEC(first 1200): `packages/permissions` in `imagine-os/paperos-template`:

* Model (`src/model.ts`, Zod): `Policy = { id, effect: 'allow' | 'deny', audiences: AudienceId[] (from identity/audience-model), actions: Action[] , resource: ResourceType | '*', condition?: Condition, source: { specPath, line } }`. `Action` is a dotted string `<entity>.<verb>` with verbs `read | list | create | update | delete | export | share | impersonate | manage` and page-level `page.view` and `page.action:<name>`. `Condition` is a small typed expression tree: `{ all | any | not }`, and leaves comparing a resource path to a literal or an actor path (`{ path: 'resource.ownerId', op: 'eq', ref: 'actor.id' }`, ops `eq | neq | in | contains | gte | lte | isNull`). No arbitrary code, so it can compile to SQL.
* Evaluation (`src/evaluate.ts`): `can(actor: Principal, action, resource: { type, id?, attrs? }, ctx: { tenantId }) => Decision { allowed, matched: PolicyId[], explain(): string }`. Order: explicit deny wins, then any allow, else deny. Role grants are expressed as built-in policies for the five roles (`owner` and `admin` get `*.manage`; `staff` gets `*.read/list/create/update` on staff resources; `member` and `viewer` 
DOD:
* Evaluator has 100 per cent branch coverage; property test asserts SQL predicate and in-memory `can` agree on 10 000 random actor/resource pairs (using PGlite for SQL).
* Benchmark shows under 20 microseconds median for `can` with 200 policies (numbers in PR).
* `toRlsPolicy` output applied to the `invoices` fixture table in the data-layer/rls-tenancy harness; cross-tenant and cross-owner reads fail.
* oRPC 403 responses include explain text in dev and a generic message in prod (tests).
* `useCan` demonstrated in Storybook with a story per outcome (screenshots at 375 and 1280).
* Draft or final spec adapter has fixture specs and tests; Quill confirms alignment with spec-builder/access-section.
* Docs merged; changelog entry under "Identity"; Linear comment with benchmark table and Storybook link.
EDGE:
* Policy references an audience not declared: loader fails validation with file and line; never silently denies at runtime.
* Resource without a tenantId (global reference data): `resource.tenantId` null matches only policies marked `global: true`.
* Conflicting allow and deny at different specificity: deny always wins; documented, no precedence by specificity.
* Actor attributes change mid-session (promoted to admin): `PermissionProvider` refetches on `session.updated` events; server always evaluates fresh.
* Condition compares to an array attribute (`actor.attributes.regions contains resource.region`): supported by `contains`; SQL uses `?` jsonb operator.
* More than 1 000 policies in one app: loader warns and the benchmark test fails above 100 microseconds so growth is noticed.
DEPS: * identity/audience-model (principal and audience types), data-layer/rls-tenancy (session variables and harness). Soft: spec-builder/access-section (adapter contract), data-layer/api-layer (middleware), identity/org-tenancy (`withTenant`).


## PAP-60 [P1 Build M prio1 Backlog] Make agents first-class principals with scoped API keys, rate limits and visible attribution
key=identity/agent-principals milestone=Agent principals and enterprise agent=* Builds: Forge (lead); Atlas's Dispatcher sub-agent validat
blockedBy=['PAP-59'] blocks=['PAP-146']
GOAL: Make Claude agents first-class principals: each character gets scoped API keys, per-key rate limits and quotas, and everything an agent does is attributed visibly in audit logs, presence and UI, with the same `can()` checks as humans. This is what keeps the audit trail honest when most contributors are agents.
SCOPE: * In: agent principal records, API key issuance and rotation via Better Auth's API key plugin, scope model derived from character access lists, rate limiting, attribution headers and UI badge, audit integration, a CLI for the orchestrator, and docs.
* Out: defining characters (agents/character-schema, agents/roster-v1), MCP tool allowlists (agents/tool-scopes), presence rendering (realtime/agent-presence consumes the attribution).
SPEC(first 1200): In `imagine-os/paperos-template`:

* Data: `users` rows with `principalType = 'agent'` and `attributes: { character: 'forge', subAgent?: 'schema-wright', lead: 'atlas' }`; one agent user per lead character, created by `pnpm agents:sync` reading `.claude/agents/*.md` frontmatter from agents/roster-v1 (name, role, reportsTo, access). Agents are members of tenants with role `staff` plus attribute `agent: true`; the audience model's `agent` audience matches them.
* Keys: Better Auth `apiKey()` plugin with `defaultPrefix: 'pos_agent_'`, `rateLimit: { enabled: true, timeWindow: 60_000, maxRequests: per-scope default 600 }`, metadata `{ character, issue?: 'PAP-123', session?: id, scopes: string[] }`, expiry default 7 days for session-scoped keys and 90 days for character keys. Keys are hashed at rest by the plugin; only the orchestrator (pm-linear/orchestrator) mints session keys using a character key with `agent.key.create` permission.
* Scopes: `packages/permissions` gains `withScopes(actor, scopes)` that intersects the actor's policies with scope patterns (for example `repo:write`, `linear:comment`, `specs:write`, `prod:read-only`) mapped from the plan.json access lists by `packages/ag
DOD:
* `pnpm agents:sync` creates nine agent users idempotently; second run makes no changes (test).
* A session key with `linear:comment` only receives 403 on `invoice.update` and 200 on allowed calls (Vitest integration).
* Rate limit test: the 601st request in a minute returns 429 with `Retry-After`.
* Audit rows for agent mutations include character, session and issue fields (test against data-layer/audit-log or its interface mock).
* `ActorBadge` stories for human, agent and agent-on-behalf-of, screenshots at 375 and 1280, light and dark; axe clean.
* Keys never logged: test greps server logs during key creation.
* Security Auditor confirms hashing and expiry; docs and changelog entry under "Identity"; Linear comment with Storybook link.
EDGE:
* Character removed from the roster: `agents:sync --prune` deactivates the user and revokes keys; history and attribution remain.
* Key used after its issue moved to Done: orchestrator revokes on state change; server also rejects keys whose `issue` metadata is closed if the Linear cache says so (soft check, logged).
* Two sessions for one character run in parallel: separate session keys with different `session` metadata; audit distinguishes them.
* Agent acts on behalf of a human (approved impersonation): `onBehalfOf` set and identity/impersonation rules apply; badge shows both.
* Clock drift between orchestrator and API: expiry evaluated server-side only.
* Plugin rate limit resets on server restart: acceptable for now; documented as a known gap with a Redis-backed option later.
DEPS: * identity/rbac-abac (`can`, scope intersection). Soft: agents/roster-v1 (source of characters), data-layer/audit-log, pm-linear/orchestrator (key minting), agents/cost-controls (quota events), realtime/agent-presence (badge).


## PAP-61 [P1 Build M prio2 Backlog] Add staff 'view as customer' impersonation with full audit trail
key=identity/impersonation milestone=Roles and audiences enforced end to end agent=* Builds: Forge (lead) for endpoints and middleware; Iris (C
blockedBy=['PAP-38', 'PAP-59'] blocks=[]
GOAL: Let authorised staff see exactly what a specific customer sees, in read-only mode by default and with an explicit, reasoned, time-boxed write mode, while every action is recorded against both identities. Support and QA stop guessing, and customers can trust the audit trail.
SCOPE: * In: start and stop impersonation endpoints, permission and reason capture, session representation, the persistent banner, read-only enforcement, audit records with `impersonatorId`, customer-visible history, admin review page, tests.
* Out: agent impersonation of humans beyond the `onBehalfOf` marker (identity/agent-principals), and customer-initiated screen sharing (realtime/followmode covers live co-browsing).
SPEC(first 1200): In `imagine-os/paperos-template`:

* Permission: new actions `user.impersonate` (read-only) and `user.impersonate.write`, granted by built-in policy to `staff-support` and `admin` audiences respectively, further constrained by the tenant (staff may only impersonate customers of tenants they belong to). Both go through `can()` from identity/rbac-abac.
* Endpoints (oRPC, `apps/api/src/routes/impersonation.ts`): `impersonation.start({ targetUserId, reason: string (min 10 chars), mode: 'read' | 'write', ttlMinutes <= 60 })`, `impersonation.stop()`, `impersonation.current()`. Implementation uses Better Auth's `admin` plugin `impersonateUser` under the hood but wraps it so the resulting session stores `impersonatedBy`, `reason`, `mode`, `expiresAt`, `linearIssue?` in the session record; the original staff session is kept and restored on stop.
* Read-only enforcement: `withTenant` middleware inspects `session.impersonation.mode`; for `read`, any oRPC procedure tagged `mutation` returns 403 `IMPERSONATION_READ_ONLY` before executing; Electric write queue is disabled client-side and the UI shows disabled states via `useCan` returning false for all mutating actions.
* Banner: `ImpersonationB
DOD:
* Support user can start read-only impersonation, see the customer's portal, is blocked on a mutation with the specific error, and stops; write mode with reason allows the mutation and records both ids (Playwright e2e and Vitest).
* Session auto-expires at TTL; a request after expiry returns 401 and the banner reports expiry (test with faked clock).
* A `member` role user cannot start impersonation (403 with explain in dev).
* Banner screenshots at the seven widths, light and dark, in both shells; axe clean; countdown announced to screen readers every 5 minutes only.
* Audit events verified in the log with correct fields; customer history page shows the session.
* Docs `docs/platform/impersonation.md` with policy and privacy notes; changelog entry under "Identity"; Linear comment with video of the full flow.
EDGE:
* Impersonating another staff member or an admin: denied unless the actor is `owner`; never allow impersonating an owner.
* Nested impersonation attempt: `start` while already impersonating returns 409.
* Target user deleted or leaves the tenant mid-session: middleware ends the impersonation and returns 410.
* Staff opens the customer's Stripe customer portal link during impersonation: external links that carry authority are disabled in read mode and flagged in the UI.
* Realtime presence: the customer must not see a phantom presence cursor labelled with their own name; presence shows "Support (viewing as you)" to staff and is hidden from the customer (realtime/presence hook).
* Reason contains sensitive data: stored as-is but redacted in prompt logs via collab/prompt-log-store rules.
DEPS: * identity/rbac-abac (actions and enforcement), data-layer/audit-log (records). Soft: identity/customer-portal-shell and identity/staff-console-shell (banner mount points), realtime/presence, realtime/multi-window-sync.


## PAP-62 [P1 Build M prio2 Backlog] Ship the customer-facing portal shell (login, profile, billing entry) separate from the staff console
key=identity/customer-portal-shell milestone=Roles and audiences enforced end to end agent=* Builds: Iris (Component Crafter) for pages and components;
blockedBy=['PAP-16', 'PAP-58'] blocks=[]
GOAL: Ship the reference customer-facing surface every PaperOS app inherits: a portal shell at `/portal` with login, profile, security, billing entry and notifications pages, deliberately separate from the staff console so the two audiences never share navigation or affordances by accident. Every page has a spec and is rendered from the shared layout slots.
SCOPE: * In: portal layout, navigation, five pages with specs, empty and error states, responsive behaviour at all widths, PWA install prompt placement, theming hooks, tests and screenshots.
* Out: real billing (business-core/stripe-billing fills the billing page; here it is an entry point with a stub state), notification delivery (collab/notifications), marketing pages (growth/landing-forms).
SPEC(first 1200): In `imagine-os/paperos-template` (apps/web plus specs):

* Route group `/portal` using app-shell/router-layouts with layout `portal.layout.tsx`: top bar (logo from tenant theme, page title, `ActorBadge`/avatar menu), bottom tab bar under 768 px and left rail at 768 px and above, no inspector slot, optional `ImpersonationBanner` slot (identity/impersonation). Access: `audiences: [customer, anonymous for /portal/login]` in every spec; staff visiting `/portal` are allowed (they may be customers too) but see a subtle "You are staff - open console" link.
* Pages and specs (`specs/pages/portal/*.spec.yaml`, each with purpose, access, data, layout, components, states and edge cases):
  1. `/portal/login` - reuses auth components from identity/better-auth with tenant branding and a "Continue as guest" option only when the app spec enables anonymous access.
  2. `/portal` (Home) - greeting, account status card, quick links from `app.spec.yaml` `portal.quickLinks` (default: Profile, Billing, Support).
  3. `/portal/profile` - name, avatar upload (data-layer/file-storage), email (change requires verification), locale and timezone, preferred contact method; optimistic save via Electric write q
DOD:
* Six page specs validate with `spec validate`; conformance tests generated (spec-builder/conformance-tests when available, else the draft runner) and passing.
* Playwright screenshots for every page at 320, 375, 768, 1024, 1280, 1536, 1920 in light, dark and high-contrast; video of login -> profile edit -> security -> sign out.
* Vision inspection (quality/screenshot-annotation) reports no overflow or truncation; axe has zero serious or critical issues.
* Permission test: a `staff` principal without customer membership sees the console link; an `anonymous` principal is redirected from `/portal/profile` to `/portal/login` with return URL.
* Works offline for read (cached shell and last data) with a visible offline indicator.
* Lighthouse performance and accessibility above 90 at 375 and 1280.
* Docs `docs/product/customer-portal.md` describing how an app extends the portal; changelog entry under "Customer"; Linear comment with Pages demo link and screenshots.
EDGE:
* Tenant has no logo or brand palette: default theme; no broken image.
* Customer belongs to several tenants: Home shows a tenant picker card; the switcher from identity/org-tenancy is reused in a customer-friendly variant.
* Email change to an address already used by another account: server rejects; UI explains without revealing whether the other account exists beyond "cannot use this email".
* Very long names or RTL locales: layout tested with 80-character names and `ar` locale in a story.
* Account deletion requested while an active subscription exists: blocked with guidance until billing cancels (hook for business-core).
* Session revoked from another device while the page is open: next request returns 401 and the shell redirects to login preserving the path.
DEPS: * identity/org-tenancy (membership, switcher), app-shell/router-layouts (layouts). Soft: identity/better-auth, design-system/layout-components, design-system/theming, data-layer/file-storage, app-shell/pwa, business-core/stripe-billing (fills billing later).


## PAP-63 [P1 Build M prio2 Backlog] Ship the staff console shell with tenant switcher, audience filters and admin navigation
key=identity/staff-console-shell milestone=Roles and audiences enforced end to end agent=* Builds: Iris (Component Crafter) for layout and components
blockedBy=['PAP-16', 'PAP-58'] blocks=[]
GOAL: Ship the reference staff-facing surface every app inherits: a console at `/console` with tenant switcher, audience filters, admin navigation and the settings pages that identity issues already need (members, roles, audit, agents, security). It is the host for future admin modules and demonstrates the customer/staff split alongside identity/customer-portal-shell.
SCOPE: * In: console layout with sidebar, command bar slot and inspector, tenant and workspace switcher, `AudienceFilter` component, navigation generated from `app.spec.yaml`, admin pages with specs, responsive behaviour including multi-window pop-out hooks, tests and screenshots.
* Out: module content such as CRM or finance pages (those projects add routes under `/console/*`), the org chart (agents/org-chart-ui), notification centre (collab/notifications).
SPEC(first 1200): In `imagine-os/paperos-template`:

* Route group `/console` using app-shell/router-layouts layout `console.layout.tsx` with slots: `nav` (collapsible sidebar, 240 px, icon rail at 768-1023 px, drawer under 768 px), `commandBar` (input/command-registry palette trigger when available, else a search stub), `main`, `inspector` (right panel 360 px at 1280 px and above, sheet below), `banner` (impersonation). Access: `audiences: [staff, admin, owner, agent]`; customers hitting `/console` get a 403 page with a link back to the portal.
* Navigation: generated by `packages/core/src/nav/fromAppSpec.ts` from `app.spec.yaml` `navigation.console` entries `{ id, label, icon, route, audiences, badgeSource? }`; items the actor's audiences do not match are hidden, not disabled; sections: Overview, Data, People, Agents, Settings.
* Switchers: `TenantSwitcher` from identity/org-tenancy in the sidebar header plus `WorkspaceSwitcher`; both keyboard operable and searchable.
* `AudienceFilter` (`packages/ui`): a chip-based filter that emits a `Segment` from identity/audience-model (for example staff role = support AND tier = pro), used by list pages to filter people and later by growth/segments; persists
DOD:
* Seven specs validate; conformance tests pass; navigation hides entries for audiences the actor lacks (Vitest with fixture principals for support staff, admin and agent).
* Screenshots of Overview, Members and Audit at the seven widths in light, dark and high-contrast; video of tenant switch -> filter members -> open inspector -> pop out (desktop).
* Sidebar, switchers and audience filter fully keyboard operable; axe zero serious issues; focus order verified.
* A customer principal gets the 403 page; an agent principal sees Overview and Agents only (test).
* Lighthouse performance above 85 at 1280 with the members table populated with 1 000 fixture rows.
* Docs `docs/product/staff-console.md` describing how a module adds a nav entry and page; changelog entry under "Staff"; Linear comment with Pages demo link and video.
EDGE:
* Tenant with 0 members other than the owner: Members page shows an invite call to action, not an empty table.
* Navigation entry points to a route that does not exist yet (module not shipped): entry hidden and a dev-only console warning emitted; conformance test flags it.
* Audience filter produces an impossible segment (staff AND anonymous): filter shows "no one matches" immediately using `matches` on fixtures, no server call.
* Window narrower than 320 px (split-screen phones): layout stays usable with horizontal scroll confined to tables.
* Inspector popped out and then the main window closes: pop-out window closes too and placement is remembered (app-shell/breakpoints-windows API).
* Audit log has 1 million rows: page requests are server-paginated with cursor; no client-side full loads.
DEPS: * identity/org-tenancy (switchers, membership), app-shell/router-layouts (layout slots). Soft: identity/rbac-abac, identity/audience-model, data-layer/audit-log, design-system/layout-components, input/command-registry, app-shell/breakpoints-windows, tables/grid-view.


## PAP-64 [P1 Review M prio1 Backlog] Generate permission matrix tests from page specs covering who can see and do what on every page
key=identity/permission-tests milestone=Agent principals and enterprise agent=* Builds: Sentinel (Security Auditor sub-agent designs the m
blockedBy=['PAP-122', 'PAP-116', 'PAP-59'] blocks=[]
GOAL: Generate, from the `access` section of every page spec, an executable permission matrix: for each page and each declared action, tests assert that every audience that should be allowed is allowed and every other audience is denied, at the policy level, the HTTP level and the UI level. When a policy or spec drifts, CI fails with a readable matrix diff.
SCOPE: * In: a generator producing Vitest suites and a Playwright suite from specs, fixture principals per audience, a matrix report, CI wiring into gate 1 and a spec-conformance hook for gate 2, and docs.
* Out: writing the access-section format (spec-builder/access-section) or the engine (identity/rbac-abac); manual security testing (Sentinel's Security Auditor still reviews); the policy-level matrix assertions, which `spec-builder/conformance-tests` already generates and this issue imports (its compiled matrix is the single source; this issue adds the HTTP and UI levels and the matrix report).
SPEC(first 1200): In `imagine-os/paperos-template`, package `packages/permission-tests`:

* Fixtures: `fixtures/principals/*.json`, one per built-in audience from identity/audience-model (anonymous, customer-free, customer-pro, customer-enterprise, staff, staff-support, staff-finance, admin, owner, partner, agent, developer) plus any app-declared audience, generated by `pnpm permissions:fixtures` which reads `app.spec.yaml` and writes a principal that matches exactly that audience and no narrower one (verified with `matches`).
* Generator `src/generate.ts` (`pnpm permissions:test:generate`): loads all `specs/**/page.spec.yaml`, converts `access` via the adapter from identity/rbac-abac, and emits into `generated/` (git-ignored, produced in CI and locally):
  1. `unit/<page>.test.ts` - for each `(audience, action)` pair calls `can(fixture, action, resourceFixture)` and expects the spec's verdict; resources come from `specs/fixtures/resources/<entity>.json` with an `ownedBy` variant so `owner-only` conditions are exercised for both matching and non-matching owners.
  2. `http/<page>.test.ts` - spins up the API with PGlite via the test harness from data-layer/rls-tenancy, seeds tenants A and B, signs in
DOD:
* Generator runs over the current specs (auth, org, portal, console, dev pages) and produces passing suites; total gate-1 time increase under 90 s (numbers in PR).
* Intentionally flipping one policy in a fixture branch makes exactly the expected cells fail with a readable message including spec path and line (screenshot of CI output).
* Cross-tenant http tests prove denial for every mutating action on every page.
* Matrix report committed and rendered in the PR comment (screenshot at 1280).
* UI suite runs for at least the portal and console pages with `uiTest: true`.
* Sentinel Security Auditor reviews fixtures for realism; Quill confirms report readability.
* Changelog entry under "Quality"; Linear comment with the matrix link and timing.
EDGE:
* Spec declares an action the page never implements: http test skips with a warning and the conformance reviewer is notified (spec-builder/conformance-tests owns the required-component check).
* Condition depends on data not in fixtures (for example `resource.status = paid`): generator creates both a matching and a non-matching resource variant automatically from the condition literal.
* Audience declared in `app.spec.yaml` has no possible principal (contradictory segment): fixture generation fails with an explanation rather than emitting a vacuous test.
* Two specs share a route with different access (bug): generator errors with both paths.
* Better Auth rate limits during http tests with 12 principals: test helper mints sessions directly through the adapter, bypassing sign-in routes.
* Matrix grows to hundreds of pages: report groups by route prefix and collapses unchanged sections.
DEPS: * identity/rbac-abac (engine and adapter), spec-builder/access-section (format). Soft: data-layer/rls-tenancy (harness), quality/ci-gate1 (wiring), spec-builder/layout-codegen (`data-action` attributes), quality/playwright-matrix (UI suite runner).


## PAP-65 [P2 Build L prio3 Backlog] Add SAML/OIDC SSO and SCIM provisioning for enterprise tenants
key=identity/sso-scim milestone=Agent principals and enterprise agent=* Builds: Forge (lead) for plugin and SCIM server; Iris (Com
blockedBy=['PAP-58'] blocks=[]
GOAL: Give enterprise tenants single sign-on through their own SAML 2.0 or OIDC identity provider and automated user lifecycle through SCIM 2.0, configured entirely in the console by a tenant owner, so no app code changes are required when an enterprise customer arrives.
SCOPE: * In: Better Auth SSO plugin configuration for OIDC and SAML per tenant, domain verification, console pages for IdP setup and SCIM tokens, a SCIM 2.0 server (Users and Groups) mapping to memberships and roles, JIT provisioning rules, enforcement options (SSO required), tests against reference IdP payloads, docs.
* Out: IdP-initiated deep linking to arbitrary pages (login lands on `/console` or `/portal`), SCIM for customers (staff only in this build), and directory sync beyond Users and Groups.
SPEC(first 1200): In `imagine-os/paperos-template`:

* Plugin: add `sso()` from Better Auth's SSO package (versions per identity/auth-research) to `packages/auth` with `provisionUser` hook creating the membership in the tenant that owns the verified email domain, `defaultRole: 'member'`, and `organizationProvisioning: { disabled: false, defaultRole }`. Store provider config per tenant in the `ssoProvider` table extended with `tenantId`, `type: 'oidc' | 'saml'`, `domains: string[]`, `enforce: boolean`, `jitRole`, `groupRoleMap jsonb`.
* Domain verification: owner adds `acme.com`; we issue a TXT record `paperos-verify=<token>`; a job checks DNS (`dns.resolveTxt`) and marks verified; SSO applies only to verified domains. Sign-in page from identity/better-auth detects a verified domain from the email and redirects to the tenant's IdP.
* SAML specifics: SP metadata at `/api/auth/sso/saml2/sp/metadata?tenant=<slug>`, ACS URL, signed assertions required, encryption optional, certificate rotation with two active certs. OIDC specifics: discovery URL, client id and secret (encrypted at rest with the app key from app-shell/env-config), PKCE.
* SCIM 2.0 server (`apps/api/src/scim/`): endpoints under `/scim/v2/`
DOD:
* Owner configures OIDC and SAML in the console and logs in via each (Playwright with mock IdPs; video attached).
* Domain verification job verifies a TXT record in a test zone (or a mocked resolver in CI) and unverified domains never trigger SSO redirects.
* SCIM suite: create, update, deactivate, reactivate, delete user; create group and add member changes role; filters and pagination work; all fixtures pass; wrong token returns 401 in SCIM error format.
* Deactivated user's sessions are revoked within one request (test).
* Enforcement: a magic-link request for an enforced domain is refused; owner break-glass works (tests).
* Screenshots of both console pages at the seven widths, light and dark; axe clean.
* Sentinel Security Auditor signs off on certificate handling, token storage and replay protection (SAML `InResponseTo`, OIDC nonce).
* Docs `docs/platform/enterprise-sso-scim.md` with Okta and Entra setup guides; changelog entry under "Identity"; Linear comment with video and SCIM fixture results.
EDGE:
* Same email domain claimed by two tenants: second verification fails with guidance; subdomains are distinct domains.
* SCIM PATCH with unsupported path (`emails[type eq "work"].value`): implement the common filter path form; unknown paths return 400 `invalidPath`.
* IdP sends a user whose email already exists as a customer in another tenant: create a staff membership in the enterprise tenant; do not alter the other tenant.
* SAML certificate expired on the IdP side: login fails with a clear console error and an admin notification; no silent fallback to unsigned.
* SCIM token leaked: revocation from the console; all subsequent requests 401; sync log shows the last successful call.
* IdP clock skew beyond 5 minutes: assertion rejected; error text names skew as the likely cause.
DEPS: * identity/org-tenancy (tenant settings, memberships). Soft: identity/better-auth (plugin host), identity/rbac-abac (group-to-role effects), data-layer/audit-log, app-shell/env-config (encryption key), identity/staff-console-shell (pages host).
