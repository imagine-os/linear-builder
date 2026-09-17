DESCRIPTIONS = {}

DESCRIPTIONS["PAP-55"] = """**Goal**

Define the single vocabulary every page spec, policy, view and campaign uses to say who: principal types, tenant roles, customer tiers, partners, admins, agents, and composable segments for everything in between. Ship it as typed code in `packages/core` plus a document, so specs validate against real audience ids instead of free text.

**Scope**

* In: `docs/specs/audience-model.md`; `packages/core/src/audience/` with Zod schemas, types, `matches`, `describe`, `BUILTIN_AUDIENCES`; the segment expression language; the `audiences:` shape for `app.spec.yaml`.
* Out: evaluating permissions (PAP-59), storing memberships (PAP-58), behavioural marketing segments (PAP-195 extends this with usage attributes).

**Spec**

* `principal.ts`: `PrincipalType = 'human' | 'agent' | 'service' | 'anonymous'`; `Principal = { id, type, tenantId: string | null, attributes: Record<string, string | number | boolean | string[]> }` (attributes such as `tier`, `staffRole`, `partnerId`, `character`, `emailVerified`, `mfa`, `actingFor`). This is the canonical actor type; PAP-35's API context and PAP-60 import it rather than redefining it.
* `role.ts`: `TenantRole = 'owner' | 'admin' | 'staff' | 'member' | 'viewer'`, mapped one-to-one to Better Auth organization roles in PAP-58; custom roles are named strings that must extend one of the five.
* `audience.ts`: `Audience = { id: kebab-case, name, description, match: Segment }`; `Segment = { all } | { any } | { not } | { attr, op: eq|neq|in|gte|lte|exists, value }` with shorthand leaves `{ role }`, `{ principalType }`, `{ tier }`, `{ audience: id }`; depth limit 6; `matches(principal, segment)` is pure and under 50 µs.
* Built-ins: `anonymous`, `authenticated`, `customer`, `customer-free`, `customer-pro`, `customer-enterprise`, `staff`, `staff-support`, `staff-finance`, `admin`, `owner`, `partner`, `agent`, `developer`, `everyone`, each with a matching and a non-matching example principal.
* Composition: audiences reference others by id with cycle detection; apps add audiences in `app.spec.yaml` under `audiences: Record<string, Omit<Audience, 'id'>>` (shape agreed with PAP-117); page specs may only reference declared or built-in ids and `spec validate` enforces it.
* `describe(segment)` renders text such as "staff whose staffRole is support, or admins"; `AUDIENCE_MODEL_VERSION = 1`, changes need an ADR.

**Interface contract**

* Provides (from `@paperos/core/audience`): types `Principal`, `PrincipalType`, `TenantRole`, `Audience`, `AudienceId`, `Segment`; functions `matches`, `describe`, `validateAudiences`; constants `BUILTIN_AUDIENCES`, `AUDIENCE_MODEL_VERSION`; JSON Schema for the `audiences:` section.
* Consumers: PAP-59 (policy `audiences` field), PAP-116 and PAP-117 (spec validation), PAP-63 `AudienceFilter`, PAP-64 fixture principals, PAP-240 `testUsers`, PAP-195, PAP-103 (agent principal attributes).
* Requires: nothing at runtime.

**Definition of done**

* Package exports the API above; typecheck and Biome clean.
* Vitest: 100 percent branch coverage of `matches`; cycle and depth tests; `fast-check` property that `not(not(x))` equals `x` and that `all([])` matches everyone.
* Document merged with the built-in table and two worked examples: a customer who is also a partner; an agent acting for a staff member.
* Comment left on PAP-117 confirming the `audiences:` shape; Atlas confirms `agent` attributes match PAP-103.
* Changelog entry under "Platform"; Linear comment with the doc link and coverage report.

**Test plan**

* Unit: every operator including arrays (`eq` matches any element, `in` intersects), unknown attribute returns false and never throws, shorthand leaves, audience references, `describe` snapshots for all built-ins.
* Property: 10 000 random principals against random segments, de Morgan equivalences hold.
* Bench: `tinybench` median under 50 µs at depth 6.
* Contract: JSON Schema round-trips a fixture `app.spec.yaml`.

**Demo**

Run `pnpm audience explain --principal fixtures/customer-partner.json` and read which built-in audiences match and why; then break a fixture `app.spec.yaml` with a cyclic audience and watch `pnpm spec validate` name the cycle. Under one minute.

**Edge cases**

* Multi-tenant user: one `Principal` per active tenant; PAP-58 sets it.
* Anonymous principal on a public tenant page: `anonymous` ignores `tenantId`.
* Agent impersonating a human: `actingFor` attribute; `agent` still matches and policies must check `actingFor` explicitly.
* App-specific tier names (`plan: basic`): apps map their own attributes; built-in tiers are examples.

**Dependencies**

None blocking. Consumers listed above.

**Agent**

Quill (Page Spec Writer) writes the document; Forge (Schema Wright) implements. Reviewed by Sentinel (Code Reviewer) and Atlas.

**Size**

M: small code, permanent decisions.
"""

DESCRIPTIONS["PAP-56"] = """**Goal**

Confirm the authentication choice before it is wired into every surface: compare Better Auth, Lucia, Clerk and Auth.js against PaperOS's hard requirements with a hands-on spike in the browser and in a Tauri 2 webview, and record the result as an ADR that PAP-57 executes with exact package versions.

**Scope**

* In: rubric comparison, a spike per finalist (at minimum Better Auth and one alternative) proving passkeys and organization membership on web and in Tauri on Linux and macOS, the ADR, the plugin and version list.
* Out: production wiring (PAP-57), SSO and SCIM depth (PAP-65; the ADR notes each candidate's path).

**Spec**

* `docs/decisions/ADR-000X-authentication.md` in the MADR format from PAP-44, scored on PAP-209 criteria plus requirement columns: self-hostable on Postgres (hard), organizations and teams, passkeys, magic link, Google and GitHub OAuth, Tauri-compatible session strategy (bearer or webview cookie), API keys for agents, OIDC provider capability (PAP-45 needs it), enterprise SSO client, SCIM story, TypeScript quality, licence, weekly downloads and last release (with retrieval date), Drizzle adapter.
* Spike `spikes/auth/<candidate>/` excluded from the production workspace: a Vite React page with passkey sign-up, magic-link sign-in (console-logged), create organization, invite, switch; run in the browser and in `tauri dev`. Record WebAuthn availability in WebKitGTK (expected missing; document the system-browser plus `paperos://auth/callback` fallback) and in WKWebView.
* Hosted providers: state data-residency implications and monthly cost at 10 000 MAU.
* Output the exact package list and versions (`better-auth`, passkey, organization, magic-link, API-key, OIDC provider plugins, Drizzle adapter) and known bugs with issue links.
* Time box 6 agent-hours; unfinished verification is recorded as risk.

**Interface contract**

* Provides: the ADR (status Accepted or Proposed), `spikes/auth/README.md`, a `versions.json` under `spikes/auth/` that PAP-57 children copy into `package.json`, and a findings section "Tauri" that PAP-225 implements.
* Consumers: PAP-57 and its children (PAP-223 to PAP-226), PAP-214 (shares findings), PAP-65 (SSO notes).
* Requires: nothing.

**Definition of done**

* ADR merged; if the recommendation differs from Better Auth, the ADR is Proposed and a Needs Justin item is opened with a five-line summary.
* Comparison table complete for all four candidates; every cell filled or marked "not verified" with reason.
* Spike code committed with run instructions; screenshots at 1280 (web) and of the Tauri window on Linux and macOS.
* Tauri passkey behaviour documented with the fallback decision; `versions.json` present.
* Sentinel Security Auditor reviews session and token notes; Scout reviews scoring; changelog entry under "Docs".

**Test plan**

* Spike smoke: each candidate's page completes sign-up, sign-in, organization create and switch in Chromium (recorded once, not CI).
* Tauri: the same flow in `tauri dev` on Linux (expect passkey unavailable) and macOS.
* Review: Atlas checks every hard requirement has evidence, not a vendor claim.

**Demo**

Open the ADR's comparison table, then `cd spikes/auth/better-auth && pnpm dev`, register a passkey and create an organization in the browser; open the Linux Tauri screenshot showing the fallback message. Under two minutes.

**Edge cases**

* Candidate lacks a Drizzle adapter: score it, note the custom adapter cost.
* Passkeys fail in the webview but pass in the browser: expected on Linux; still recommend passkey-first with fallback.
* Breaking release mid-spike: pin the tested version and cite the migration guide.
* Google OAuth test-app limits: spike with GitHub, mark Google unverified.
* Evidence contradicts the plan: escalate to Needs Justin rather than agree silently.

**Dependencies**

None blocking. Soft: PAP-209 (criteria), PAP-214 (shared findings).

**Agent**

Scout (Library Evaluator) drives; Forge (Tauri Smith) runs the Tauri spike. Reviewed by Sentinel (Security Auditor); Atlas approves the ADR.

**Size**

S: time-boxed research producing a decision.
"""

DESCRIPTIONS["PAP-57"] = """**Goal**

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
"""

DESCRIPTIONS["PAP-58"] = """**Goal**

Make tenancy real for users: organizations are tenants, workspaces are teams inside them, members are invited by email, and the active tenant follows every request so the RLS boundary from PAP-34 applies to humans, not only to tests.

**Scope**

* In: Better Auth `organization` plugin mapped onto `tenants` and `workspaces`, invitation flow and email, `TenantSwitcher` and `useTenant()`, `withTenant` middleware setting RLS session variables, ownership transfer, deletion with grace period, org pages with specs, tests.
* Out: policy evaluation beyond the five roles (PAP-59), SSO and SCIM (PAP-65), billing (PAP-177), first-run onboarding wizard (app-shell gap issue; `/org/new` is its entry point).

**Spec**

* Plugin: `organization({ teams: { enabled: true, maximumTeams: 50 }, allowUserToCreateOrganization: true, organizationLimit: 10, creatorRole: 'owner', roles via createAccessControl({ owner, admin, staff, member, viewer }), sendInvitationEmail })` in `packages/auth`; client `organizationClient()`.
* Schema mapping through the plugin's `schema` option: `organization` is `tenants`, `team` is `workspaces` (PAP-33); `membership` gains `role` enum and `attributes jsonb` (`staffRole`, `tier`, `agent`), `tenants` gains `slug` unique, `logoFileId`, `deletedAt`. One table per concept.
* Active tenant in `session.activeOrganizationId`; `withTenant` verifies membership and runs `SET LOCAL app.tenant_id, app.principal_id, app.role, app.attrs` inside the request transaction; tenant-scoped procedures without an active tenant return 412 `TENANT_REQUIRED`.
* Invitations: `organization.inviteMember` with role; email `invitation.tsx`; landing `/invite/$token` signs in (magic link if new) and accepts; 7-day expiry; resend and revoke; `beforeInvite` hook point for PAP-178 limits.
* Pages and specs `specs/pages/org/*.spec.yaml`: `/org/new`, `/org/settings/general`, `/org/settings/members` (grid view if PAP-165 exists, else PAP-71 table), `/org/settings/workspaces`, `/invite/$token`, `/org/switch`.
* Components: `TenantSwitcher` (Popover with search, recent, create), `RoleBadge`, `InviteMemberDialog`; `useTenant()` returns `{ tenant, workspace, role, switchTenant, switchWorkspace }` and remounts the Electric sync provider on change (PAP-36).
* Lifecycle: owner transfers to an admin; last owner cannot leave; deletion sets `deletedAt`, hides the tenant, hard-deletes after 30 days by a PAP-43 job, audited.

**Interface contract**

* Provides: `withTenant` middleware and the session-variable contract (`app.tenant_id`, `app.principal_id`, `app.role`, `app.attrs`) consumed by PAP-34 policies and PAP-228 RLS helpers; `useTenant()`, `TenantSwitcher`, `RoleBadge`, `InviteMemberDialog`; procedures `org.create`, `org.invite`, `org.acceptInvite`, `org.switch`, `org.transferOwnership`, `org.delete`; events `tenant.created`, `membership.changed`, `tenant.deleted` for the domain event catalogue; BroadcastChannel message `tenantChanged`.
* Requires: PAP-57 (PAP-223 server child suffices), PAP-33 tables, PAP-34 policies, PAP-35 oRPC, PAP-37 logos (soft), PAP-67 components (soft).
* Tables: `tenants`, `workspaces`, `membership`, `invitation`.

**Definition of done**

* Create tenant, create workspace, invite, accept as second user, switch, leave: Playwright e2e (feeds PAP-86) and Vitest API tests pass.
* Cross-tenant: member of A calling a scoped procedure with B's id gets 403; PAP-34 harness passes with variables set by `withTenant`.
* Invitation email renders (React Email preview screenshot); expired token shows a clear message.
* Screenshots of `/org/settings/members` and the open `TenantSwitcher` at seven widths, light and dark; axe clean; keyboard-only switcher verified.
* `docs/platform/tenancy.md` with a sequence diagram of context propagation; changelog under "Identity"; Sentinel Security Auditor signs off on the middleware.

**Test plan**

* Unit: role enum mapping, slug reserved words, invitation expiry and case-insensitive email match.
* Integration: `withTenant` sets all four variables inside the transaction (assert via `current_setting` in a test procedure); 412 without active tenant; deletion job hard-deletes after the grace period with a faked clock.
* E2E: the flow above at 1280 and 375.
* Visual: members page and switcher stories at seven widths.

**Demo**

Sign in, create "Acme", invite a second seeded user, accept in another browser context, switch tenants from the switcher and watch the members list change; call a scoped procedure with the wrong tenant id in DevTools and read the 403. Under two minutes.

**Edge cases**

* Invite to a tenant the user already belongs to: role update only if the inviter may raise roles, else a no-op message.
* Active tenant deleted mid-session: 412, client redirects to `/org/switch`.
* Zero tenants after leaving: `/org/new` with pending invitations listed.
* Two tabs, different tenants: server-side session shares one active tenant; second tab receives `tenantChanged` and reloads.

**Dependencies**

PAP-57 (hard). Soft: PAP-33, PAP-34, PAP-35, PAP-37, PAP-67, PAP-43.

**Agent**

Forge (Schema Wright) for schema and middleware; Iris (Component Crafter) for switcher and pages. Reviewed by Sentinel (Security Auditor, Code Reviewer, Visual Inspector).

**Size**

M.
"""

DESCRIPTIONS["PAP-59"] = """**Goal**

Build the permission engine every layer shares: one `can(actor, action, resource, ctx)` combining role grants with attribute policies from page specs, evaluated identically in the API, compiled to SQL for RLS and list filters, and driving UI affordances through `useCan`. Deny by default, explainable on request. This issue is the umbrella for three children.

**Children**

1. PAP-227 Policy model, evaluator and explain mode (M) - blocks the other two.
2. PAP-228 SQL predicate compiler and RLS helpers (M).
3. PAP-229 Spec adapter, oRPC middleware and `useCan` hook (M).

**Scope**

* In (across children): `packages/permissions` model, evaluator, built-in role policies, explain CLI, SQL compiler, RLS generator, spec adapter, `authorize()` middleware, `PermissionProvider` and `useCan`, design-system `can` props, docs and benchmarks.
* Out: the access-section YAML format (PAP-116 defines it; PAP-229 adapts), agent keys and scopes (PAP-60), generated matrix tests (PAP-64), entitlements (PAP-178 adds policies).

**Spec**

Detailed specs live in the children. Cross-child invariants:

* One semantics: `can()` and `toPredicate()` must agree on every input; the property test in PAP-228 is the contract.
* Deny wins over allow regardless of specificity; no precedence rules.
* Policies carry `source: { specPath, line }` so every 403 and every matrix diff can point at a file.
* Actor is the PAP-55 `Principal`; audiences are resolved with `matches()`.

**Interface contract**

* Provides (from `@paperos/permissions`): types `Policy`, `Action`, `Condition`, `Decision`, `ResourceRef`; `can()`, `explain()`, `BUILTIN_POLICIES`; `toPredicate()`, `toRlsPolicy()`, `withPermissionFilter()`, `permissionColumns`; `accessToPolicies()`; `authorize()` middleware; procedure `permissions.mine`; `PermissionProvider`, `useCan()`; `can` prop on Button, IconButton, Menu.Item.
* Requires: PAP-55 audience model, PAP-34 session variables and harness, PAP-58 `withTenant`, PAP-35 oRPC, PAP-67 components, PAP-116 final access shape (soft).
* Consumers: PAP-60 `withScopes`, PAP-61 impersonation actions, PAP-64, PAP-116, PAP-140 Yjs auth hook, PAP-39 search filters, PAP-131, PAP-172, PAP-178.

**Definition of done**

* All three children Done.
* Integration test below green; benchmark table and RLS harness results in the PR.
* `docs/platform/permissions.md` complete (algorithm, verb table, three worked examples: customer sees own invoices, support may impersonate, agents may not delete); changelog under "Identity".
* Quill confirms the adapter matches PAP-116; Sentinel Security Auditor signs off.

**Test plan**

Integration test `packages/permissions/test/umbrella.test.ts` on PGlite:

* Load the three example specs (PAP-125) plus built-ins; for each of the twelve fixture principals and each declared action, assert `can()` equals the row count of `toPredicate()` applied to a two-tenant fixture, and that `toRlsPolicy()` installed in the harness yields the same visible rows.
* `authorize()` returns 403 with explain text in dev and generic text in production build.
* `useCan` story matrix screenshots at 375 and 1280.
* Bench: `can` median under 20 µs with 200 policies.

**Demo**

Run `pnpm permissions explain --actor fixtures/staff-support.json --action invoice.update --resource invoice:123` and read the matched policy with its spec line; open Storybook "Permissions" and switch the actor control to watch Delete hide; open the generated `invoices.sql`. Under two minutes.

**Edge cases**

Cross-child: a policy referencing an undeclared audience fails at load in every child identically (shared validator); resources without `tenantId` only match `global: true` policies in both engines; attribute changes mid-session are seen by the server immediately and by the client after `session.updated`.

**Dependencies**

PAP-55, PAP-34 (hard). Soft: PAP-116, PAP-35, PAP-58, PAP-67.

**Agent**

Forge leads (Schema Wright on PAP-228); Iris on component props. Sentinel (Security Auditor mandatory, Edge Case Hunter on property tests) reviews.

**Size**

L, split into 3 children (M, M, M).
"""

DESCRIPTIONS["PAP-60"] = """**Goal**

Make Claude agents first-class principals: one agent user per character, scoped API keys with rate limits and quotas minted per session by the orchestrator, and visible attribution on every mutation, comment and presence indicator, all going through the same `can()` as humans.

**Scope**

* In: agent principal records synced from the roster, Better Auth `apiKey()` plugin configuration, scope intersection `withScopes()`, rate limits and quotas, attribution fields and `ActorBadge`, audit integration, `pnpm agents:key` CLI for the orchestrator, docs.
* Out: character definitions (PAP-103, PAP-104), MCP allowlists (PAP-106), presence rendering (PAP-146), customer developer keys (PAP-222).

**Spec**

* Data: `users` rows with `principalType = 'agent'` and `attributes: { character, subAgent?, lead }`; `pnpm agents:sync` reads `.claude/agents/*.md` frontmatter (PAP-104) and upserts one user per lead character, member of each tenant with role `staff` and attribute `agent: true` so the `agent` audience matches.
* Keys: `apiKey({ defaultPrefix: 'pos_agent_', rateLimit: { enabled: true, timeWindow: 60_000, maxRequests: 600 } })`; metadata `{ character, issue?, session?, scopes }`; expiry 7 days for session keys, 90 days for character keys; hashed at rest; only a character key with `agent.key.create` may mint session keys.
* Scopes: `withScopes(actor, scopes)` in `packages/permissions` intersects policies with patterns (`repo:write`, `linear:comment`, `specs:write`, `prod:read-only`) mapped from plan access lists by `packages/agents/src/scope-map.ts`; a key whose scopes exclude the action is denied even when the role allows.
* Attribution: every oRPC mutation records `actorId`, `actorType`, `character`, `onBehalfOf?`, `sessionId`, `issueKey` to PAP-38; responses carry `X-PaperOS-Actor: agent:forge`; `ActorBadge` in `packages/ui` renders the agent glyph and character colour with tooltip "Forge (agent) on PAP-123".
* Quotas: per-character daily quota in `ops/agents/quotas.yml`; exceeding returns 429 with `Retry-After` and emits `agent.quota.exceeded` (PAP-111 consumes).
* CLI: `pnpm agents:key create --character forge --issue PAP-123 --ttl 8h --scopes repo:write,linear:comment | list | revoke <id> | rotate --character forge`, JSON output.

**Interface contract**

* Provides: `withScopes()`, `ScopePattern` type and `scope-map.ts`; `ActorBadge`; `AgentPrincipalAttributes` type; CLI JSON shapes; events `agent.quota.exceeded`, `agent.key.created`, `agent.key.revoked`; header `X-PaperOS-Actor`.
* Requires: PAP-59 `can()`, PAP-57 server for the plugin, PAP-104 roster frontmatter, PAP-38 audit sink, PAP-219 key-handling controls.
* Consumers: PAP-96 orchestrator (mints keys), PAP-111 cost controls, PAP-146 presence, PAP-107 prompt log (session id), PAP-222 (reuses `withScopes`).
* Tables: `apikey` (plugin), `agent_quota_usage`.

**Definition of done**

* `pnpm agents:sync` creates nine agent users idempotently; second run makes no changes (test).
* Session key with `linear:comment` only: 403 on `invoice.update`, 200 on allowed calls (Vitest integration).
* 601st request in a minute returns 429 with `Retry-After`; daily quota exceeded emits the event.
* Audit rows for agent mutations carry character, session and issue (test against PAP-38 or its mock).
* Keys never logged (grep test during creation); Security Auditor confirms hashing and expiry.
* `ActorBadge` stories (human, agent, agent on behalf of) at 375 and 1280 light and dark; axe clean; docs `docs/platform/agent-principals.md` with the scope table and minting sequence diagram; changelog under "Identity".

**Test plan**

* Unit: scope-map coverage for all nine characters, scope intersection cases, quota arithmetic across midnight UTC.
* Integration: mint via character key, use, expire with faked clock, revoke on issue Done (webhook stub).
* E2E: an agent comment in the example app shows the badge and tooltip.
* Visual: badge stories.

**Demo**

Run `pnpm agents:key create --character forge --issue PAP-123 --ttl 1h --scopes linear:comment`, call a read procedure with it (200), then `invoice.update` (403 with explain), then `pnpm agents:key list` showing last-used. Under two minutes.

**Edge cases**

* Character removed from roster: `agents:sync --prune` deactivates and revokes; history stays.
* Key used after its issue is Done: orchestrator revokes on state change; server soft-checks the Linear cache and logs.
* Parallel sessions for one character: distinct session keys; audit distinguishes.
* Rate-limit state lost on restart: accepted, documented with a Redis option later.

**Dependencies**

PAP-59, PAP-219 (hard). Soft: PAP-104, PAP-38, PAP-96, PAP-111, PAP-146.

**Agent**

Forge leads; Atlas's Dispatcher validates minting from the orchestrator side. Reviewed by Sentinel (Security Auditor, Code Reviewer); Iris reviews `ActorBadge`.

**Size**

M.
"""

DESCRIPTIONS["PAP-61"] = """**Goal**

Let authorised staff see exactly what a customer sees, read-only by default and with an explicit, reasoned, time-boxed write mode, while every action is recorded against both identities and the customer can see who looked.

**Scope**

* In: `impersonation.start/stop/current` procedures, permission actions, session representation, read-only enforcement, `ImpersonationBanner`, audit records with `impersonatorId`, customer-visible access history, admin review page, optional customer email on write mode, tests.
* Out: agent `onBehalfOf` semantics beyond the marker (PAP-60), live co-browsing (PAP-149).

**Spec**

* Actions `user.impersonate` (read) and `user.impersonate.write`, granted by built-in policy to `staff-support` and `admin`, constrained to customers of tenants the actor belongs to; both evaluated by PAP-59 `can()`.
* Procedures in `apps/api/src/routes/impersonation.ts`: `start({ targetUserId, reason (min 10 chars), mode: 'read' | 'write', ttlMinutes <= 60, linearIssue? })`, `stop()`, `current()`; wraps Better Auth `admin` plugin `impersonateUser`; the session stores `impersonation: { impersonatedBy, reason, mode, expiresAt, id }`; the staff session is kept and restored on stop.
* Read-only: `withTenant` (PAP-58) rejects procedures tagged `mutation` with 403 `IMPERSONATION_READ_ONLY` when mode is `read`; the client disables the Electric write queue and `useCan` returns false for mutating actions; external authority-bearing links (Stripe portal) are disabled.
* Banner: `ImpersonationBanner` in `packages/ui`, mounted in the `banner` slot of both shells: fixed top, warning tokens, "Viewing as Ada Lovelace (customer) - read-only - 27:14 remaining - Stop", countdown announced every 5 minutes, persists across navigation and Tauri windows (PAP-145 broadcast).
* Audit: every request during impersonation writes `actorId = target`, `impersonatorId = staff`, `reason`, `impersonationId` (PAP-38); `impersonation.started` and `impersonation.ended` events; customers see "Account access history" on `/portal/security` (PAP-62, PAP-220); tenants may hide it, default visible.
* Review page `/console/security/impersonations` (spec `specs/pages/console/impersonations.spec.yaml`) listing sessions with links to audit events.

**Interface contract**

* Provides: procedures above; `useImpersonation()` hook (`{ active, target, mode, expiresAt, stop }`); `ImpersonationBanner`; `AccessHistoryList` component for PAP-220's page; audit event kinds; session field `impersonation`.
* Requires: PAP-59 actions and `useCan`, PAP-58 `withTenant`, PAP-38 audit, PAP-57 admin plugin, shells PAP-62 and PAP-63 (soft mount points), PAP-145 (soft).
* Consumers: PAP-60 (`onBehalfOf` marker semantics), PAP-141 presence (hide phantom cursor), PAP-89 (impersonation counts in digest, optional).

**Definition of done**

* Support user starts read-only impersonation, sees the customer's portal, is blocked on a mutation with the specific error, stops; write mode with reason allows the mutation and records both ids (Playwright e2e plus Vitest).
* TTL expiry: request after expiry returns 401 and the banner reports expiry (faked clock).
* `member` cannot start (403 with explain in dev); owners can never be impersonated; nested start returns 409.
* Banner screenshots at seven widths light and dark in both shells; axe clean.
* Audit events verified; customer history shows the session; docs `docs/platform/impersonation.md`; changelog under "Identity"; video of the full flow.

**Test plan**

* Unit: permission decision table (actor role × target role × mode), TTL clamp, reason length.
* Integration: mutation rejection in read mode across three tagged procedures; audit rows for start, action, stop; expiry.
* E2E: full flow at 1280; banner on mobile 375.
* Visual: banner stories in both shells, RTL.

**Demo**

As seeded support staff open Members, choose Ada, "View as customer" with a reason, browse her portal with the banner counting down, try to save her profile and read the read-only error, press Stop; then open Ada's security page to see the access entry. Under two minutes.

**Edge cases**

* Target leaves the tenant mid-session: middleware ends impersonation, 410.
* Presence: customer never sees a cursor with their own name; staff sees "Support (viewing as you)".
* Reason contains sensitive text: stored, redacted in prompt logs by PAP-129 rules.
* Staff session expires first: impersonation ends with it.

**Dependencies**

PAP-59, PAP-38 (hard). Soft: PAP-62, PAP-63, PAP-141, PAP-145, PAP-220.

**Agent**

Forge for procedures and middleware; Iris (Component Crafter) for the banner. Reviewed by Sentinel (Security Auditor mandatory, Visual Inspector, Edge Case Hunter).

**Size**

M.
"""

DESCRIPTIONS["PAP-62"] = """**Goal**

Ship the reference customer-facing surface every app inherits: a portal at `/portal` with login, home, profile, security, billing entry and notification preferences, separate from the staff console so the two audiences never share navigation by accident. Every page has a spec and renders from shared layout slots.

**Scope**

* In: `portal.layout.tsx`, `PortalNav`, six pages with specs, all declared states, responsive behaviour at every width, PWA install prompt placement, theming hooks, tests and screenshots.
* Out: real billing (PAP-177 fills the stub), notification delivery (PAP-136), session and 2FA logic (PAP-220 provides the components this page embeds), marketing pages (PAP-193).

**Spec**

* Route group `/portal` on PAP-16 layouts: top bar (tenant logo, title, `ActorBadge` avatar menu), bottom tab bar under 768 px and left rail at 768 px and above, no inspector, `banner` slot for `ImpersonationBanner` (PAP-61). Access: `audiences: [customer]`, `anonymous` for `/portal/login`; staff may visit and see a "You are staff - open console" link.
* Pages and specs (`specs/pages/portal/*.spec.yaml`): `/portal/login` (PAP-224 `SignInForm` with tenant branding, guest option only when the app spec enables anonymous access); `/portal` home (greeting, `AccountStatusCard`, quick links from `app.spec.yaml` `portal.quickLinks`); `/portal/profile` (name, avatar via PAP-37, email change with verification, locale and timezone, contact method; optimistic save via PAP-36 with a saved indicator); `/portal/security` (embeds PAP-220 `SecurityPage`, PAP-61 `AccessHistoryList`, delete account with 30-day grace); `/portal/billing` (plan, payment method, invoices; without PAP-177 renders `EmptyState` "Billing is not configured" with `data-stub`); `/portal/notifications` (channel toggles stored in `user.attributes.notificationPrefs` until PAP-136).
* Components: `PortalNav`, `AccountStatusCard`, `SettingRow`, `DangerZone` from PAP-67 and PAP-71; copy in `apps/web/src/portal/copy.ts`.
* States: loading (Skeleton), empty, error, offline via PAP-234 components; forms validate with Zod shared with the API; unsaved-changes prompt; PWA install banner on home after the second visit (PAP-18).
* Theming: PAP-75 runtime theme when present, else default tokens; logo falls back to app name.

**Interface contract**

* Provides: `portal.layout.tsx` slot names `topbar`, `nav`, `main`, `banner`; `PortalNav` reading `app.spec.yaml` `navigation.portal`; `portal.quickLinks` app-spec key; `data-stub` attribute convention for stubbed sections; `SettingRow` and `DangerZone` for module settings pages.
* Requires: PAP-58 membership and switcher, PAP-16 layouts, PAP-224 sign-in form, PAP-67, PAP-71, PAP-234 states, PAP-75 (soft), PAP-37 (soft), PAP-220 and PAP-61 embeds (soft: placeholders if late), PAP-18 install hook.
* Consumers: PAP-177 (billing page), PAP-136 (preferences page), PAP-180 (invoices list), PAP-221 (legal pages), PAP-193 (sign-up handoff).

**Definition of done**

* Six specs validate; conformance tests (PAP-122 or draft runner) pass.
* Screenshots of every page at 320, 375, 768, 1024, 1280, 1536, 1920 light, dark and high-contrast; video of login, profile edit, security, sign out.
* PAP-84 vision inspection reports no overflow or truncation; axe zero serious or critical.
* Staff principal sees the console link; anonymous principal is redirected from `/portal/profile` to login with return URL (tests).
* Offline read works with the indicator; Lighthouse performance and accessibility above 90 at 375 and 1280.
* Docs `docs/product/customer-portal.md` (how an app extends the portal); changelog under "Customer".

**Test plan**

* Unit: nav generation from app spec, quick-link defaults, stub detection.
* Integration: profile save round-trip through the write queue; email-change verification path.
* E2E: the recorded flow; redirect for anonymous; multi-tenant customer sees the tenant picker.
* Visual: seven widths × three themes; RTL and 80-character-name stories.

**Demo**

Open the Pages preview as the seeded customer: land on home, edit the display name and watch the saved indicator, open Security and see passkeys and access history, open Billing and see the honest stub. Under two minutes.

**Edge cases**

* No tenant logo or palette: default theme, no broken image.
* Customer in several tenants: tenant picker card on home using a customer-friendly `TenantSwitcher` variant.
* Email already used elsewhere: server rejects; UI says only "cannot use this email".
* Session revoked elsewhere: next request 401, redirect preserving path.
* Deletion with an active subscription: blocked with guidance (hook for PAP-177).

**Dependencies**

PAP-58, PAP-16 (hard). Soft: PAP-224, PAP-67, PAP-71, PAP-234, PAP-75, PAP-37, PAP-18, PAP-220, PAP-61, PAP-177.

**Agent**

Quill (Page Spec Writer) writes the six specs first; Iris (Component Crafter) builds. Reviewed by Sentinel (Visual Inspector across the matrix, Code Reviewer, Edge Case Hunter).

**Size**

M.
"""

DESCRIPTIONS["PAP-63"] = """**Goal**

Ship the reference staff surface every app inherits: a console at `/console` with tenant and workspace switchers, an `AudienceFilter`, navigation generated from `app.spec.yaml`, and the admin pages identity already needs (overview, members, roles, audit, agents, settings). It hosts every later admin module and demonstrates the customer/staff split with PAP-62.

**Scope**

* In: `console.layout.tsx` on PAP-70 `AppFrame`, switchers, `AudienceFilter`, `fromAppSpec` navigation, seven admin pages with specs, pop-out hooks, per-slot error boundaries, tests and screenshots.
* Out: module content (CRM, finance add routes under `/console/*`), org chart (PAP-113), notifications (PAP-136), impersonation list content (PAP-61), SSO and SCIM pages (PAP-232), developer page (PAP-222).

**Spec**

* Layout slots: `nav` (sidebar 240 px, icon rail 768-1023 px, drawer under 768 px), `commandBar` (PAP-151 palette when present, else search stub), `main`, `inspector` (360 px at 1280 px and above, sheet below), `banner`. Access `audiences: [staff, admin, owner, agent]`; customers get `DeniedState` (PAP-234) with a portal link.
* Navigation: `packages/core/src/nav/fromAppSpec.ts` reads `navigation.console: [{ id, label, icon, route, audiences, badgeSource? }]`; items the actor's audiences do not match are hidden; sections Overview, Data, People, Agents, Settings.
* Switchers: `TenantSwitcher` and `WorkspaceSwitcher` from PAP-58 in the sidebar header, searchable and keyboard operable.
* `AudienceFilter` (`packages/ui`): chip filter emitting a PAP-55 `Segment` (for example staffRole = support AND tier = pro); persists per user per page in `user.attributes.filters`; reused by PAP-195.
* Pages and specs (`specs/pages/console/*.spec.yaml`): `/console` overview (members, active agents from PAP-60, open Linear items via PAP-101 when available else stub, recent audit); `/console/people/members` (PAP-165 grid if present, else PAP-71 table; role edit, invite dialog, audience filter); `/console/people/roles` (five roles plus custom, policies rendered from PAP-59 `explain`, read-only); `/console/security/audit` (PAP-38 list with actor badges and impersonation markers, cursor paginated); `/console/security/impersonations` (nav entry only; PAP-61 fills); `/console/agents` (agent principals, key counts, last activity); `/console/settings/general` and `/console/settings/branding` (PAP-75 when present).
* Multi-window: `PopOutButton` on inspector and main registering with PAP-21; hidden outside Tauri.
* Every slot has its own error boundary and skeleton.

**Interface contract**

* Provides: `console.layout.tsx` slot names; `fromAppSpec()` and the `navigation.console` app-spec shape; `AudienceFilter` (`value: Segment`, `onChange`); `registerConsoleSection(section, items)` for modules; settings page conventions (`SettingRow`); `data-testid` prefixes `console.*`.
* Requires: PAP-58 switchers, PAP-16 layouts, PAP-70 `AppFrame` (soft: plain divs until merged), PAP-55, PAP-59 explain, PAP-38 audit list, PAP-60 agent list, PAP-67, PAP-71, PAP-234, PAP-151 (soft), PAP-21 (soft), PAP-165 (soft).
* Consumers: PAP-61, PAP-75 branding route, PAP-113, PAP-189, PAP-183, PAP-222, PAP-232, PAP-221.

**Definition of done**

* Seven specs validate; conformance tests pass; navigation hides entries per audience (Vitest with support, admin and agent fixture principals).
* Screenshots of overview, members and audit at seven widths in light, dark and high-contrast; video of tenant switch, filter members, open inspector, pop out on desktop.
* Sidebar, switchers and filter keyboard operable; axe zero serious; focus order verified.
* Customer principal gets the denied state; agent principal sees Overview and Agents only (test).
* Lighthouse performance above 85 at 1280 with 1 000 fixture members; docs `docs/product/staff-console.md`; changelog under "Staff".

**Test plan**

* Unit: `fromAppSpec` filtering and section ordering; `AudienceFilter` segment output and impossible-segment detection via `matches` on fixtures.
* Integration: audit page cursor pagination against 1 million seeded rows (PGlite subset in CI, full nightly).
* E2E: the recorded flow at 1280; drawer navigation at 375.
* Visual: three pages × seven widths × three themes; RTL story for the sidebar.

**Demo**

As seeded admin open `/console`, switch to the second tenant, filter Members to "support staff", open one member in the inspector, then pop it out to a second window on desktop; open `/console/people/roles` and expand a policy's explain. Under two minutes.

**Edge cases**

* Only the owner exists: Members shows an invite call to action.
* Nav entry to an unshipped route: hidden, dev warning, conformance flag.
* Impossible segment (staff AND anonymous): "no one matches" without a server call.
* Pop-out then main window closes: pop-out closes, placement remembered.

**Dependencies**

PAP-58, PAP-16 (hard). Soft: PAP-70, PAP-59, PAP-55, PAP-38, PAP-60, PAP-151, PAP-21, PAP-165, PAP-234.

**Agent**

Iris (Component Crafter) for layout and components; Quill (Page Spec Writer) for specs; Nova's Views Engineer assists if the grid exists. Reviewed by Sentinel (Visual Inspector, Code Reviewer); Atlas confirms the module extension contract.

**Size**

M.
"""

DESCRIPTIONS["PAP-64"] = """**Goal**

Generate, from every page spec's `access` section, an executable permission matrix at three levels: policy (`can()`), HTTP (real procedures through the API with per-audience sessions) and UI (Playwright asserting denied actions are hidden or disabled). When a policy or spec drifts, CI fails with a readable matrix diff.

**Scope**

* In: `packages/permission-tests` generator emitting Vitest and Playwright suites, fixture principals per audience, the matrix report and diff, Gate 1 and Gate 3 wiring, spec-conformance hook, docs.
* Out: the access format (PAP-116), the engine (PAP-59), manual security testing, and the policy-level assertions PAP-122 already generates (imported here as the single source; this issue adds HTTP and UI levels plus the report).

**Spec**

* Fixtures: `fixtures/principals/*.json`, one per built-in audience (PAP-55) plus app-declared ones, produced by `pnpm permissions:fixtures` from `app.spec.yaml`, each verified with `matches` to hit exactly its audience and no narrower one.
* Generator `src/generate.ts` (`pnpm permissions:test:generate`) loads `specs/**/page.spec.yaml`, converts `access` through PAP-229's adapter and writes to `generated/` (git-ignored):
  1. `unit/<page>.test.ts`: `can(fixture, action, resource)` per `(audience, action)` with resource fixtures from `specs/fixtures/resources/<entity>.json` including an `ownedBy` variant.
  2. `http/<page>.test.ts`: API on PGlite via the PAP-34 harness, tenants A and B seeded, sessions minted through PAP-240 `login-as`, each declared query and mutation called and expected 200 or 403; cross-tenant variants expect 403 or empty.
  3. `ui/<page>.spec.ts` (Playwright) for pages with `access.uiTest: true`: log in per audience, assert denied actions absent (`hiddenWhenDenied`) or disabled, using the `data-action="<name>"` attributes PAP-120 emits.
* Report `src/report.ts`: `reports/permission-matrix.md` and `.json` (pages × audiences, allow/deny cells) diffed against `docs/reports/permission-matrix.md`; the PR comment posts the diff when cells change; unexplained changes are blockers for the spec-conformance reviewer (PAP-244) unless `access.changeNote` explains them.
* CI: Gate 1 runs generation plus unit and http suites sharded by page, budget 3 minutes; UI suite runs in Gate 3. Every spec must declare `access`; missing ones fail generation with the path.

**Interface contract**

* Provides: `permission-matrix.json` (`{ pages: [{ route, audiences: Record<AudienceId, Record<action, 'allow' | 'deny'>> }] }`) consumed by PAP-244 and PAP-89; `access.uiTest` and `access.changeNote` spec keys (agreed with PAP-116); fixture principals reused by PAP-240 `testUsers`; `data-action` attribute contract with PAP-120.
* Requires: PAP-59 and PAP-229 adapter, PAP-116 format, PAP-34 harness, PAP-240 `login-as`, PAP-78 job slot, PAP-120 attributes, PAP-246 Playwright projects.

**Definition of done**

* Generator runs over current specs (auth, org, portal, console, examples) and produces passing suites; Gate 1 time increase under 90 s (numbers in PR).
* Flipping one policy in a fixture branch fails exactly the expected cells with spec path and line (CI screenshot).
* Cross-tenant HTTP tests prove denial for every mutating action on every page.
* Matrix report committed and rendered in the PR comment (screenshot at 1280); UI suite runs for portal and console pages.
* Security Auditor reviews fixture realism; Quill confirms readability; changelog under "Quality".

**Test plan**

* Unit: fixture generation hits exactly one audience; generator output snapshots for three example specs; report diff on a seeded cell change.
* Integration: http suite on PGlite with two tenants; session minting without sign-in routes.
* E2E: UI suite on `/portal/profile` and `/console/people/members` at 1280.
* Meta: generation determinism (two runs, identical files).

**Demo**

Change `access.actions.delete.audiences` on the members spec to include `customer`, run `pnpm permissions:test:generate && pnpm test --filter permission-tests`, and read the failing cell naming the spec line; revert and watch it pass. Under two minutes.

**Edge cases**

* Declared action never implemented: http test skips with a warning; PAP-122 owns the required-component check.
* Condition on data not in fixtures (`resource.status = paid`): both variants generated from the literal.
* Contradictory audience in `app.spec.yaml`: fixture generation fails with an explanation.
* Two specs share a route with different access: generator errors naming both.
* Hundreds of pages: report groups by route prefix and collapses unchanged sections.

**Dependencies**

PAP-59, PAP-116, PAP-240 (hard). Soft: PAP-34, PAP-78, PAP-120, PAP-122, PAP-246.

**Agent**

Sentinel (Security Auditor designs the matrix; Code Reviewer implements) with Forge on the API harness. Reviewed by Forge and Quill; Atlas approves the gate timing.

**Size**

M.
"""

DESCRIPTIONS["PAP-65"] = """**Goal**

Give enterprise tenants single sign-on through their own OIDC or SAML 2.0 identity provider and automated staff lifecycle through SCIM 2.0, configured entirely in the console by a tenant owner. This issue is the umbrella for three children; it is done when they are merged and the integration test below passes. The audit rates this unlikely to ship by 2026-10-01; it stays P2 and the children may slip individually.

**Children**

1. PAP-230 SSO plugin: OIDC and SAML per tenant with domain verification (M).
2. PAP-231 SCIM 2.0 server for Users and Groups (M).
3. PAP-232 Console SSO and SCIM settings pages, enforcement and enterprise docs (M) - blocked by the other two.

**Scope**

* In (across children): Better Auth `sso()` configuration, `ssoProvider` extension, domain verification, SAML SP metadata and certificate rotation, OIDC with PKCE, JIT provisioning and group-to-role mapping, SCIM server with tokens and sync log, console pages, enforcement with break-glass, Okta and Entra guides.
* Out: IdP-initiated deep links to arbitrary pages, SCIM for customers, directory sync beyond Users and Groups, MFA policies (PAP-220).

**Spec**

Detailed specs live in the children. Cross-child invariants:

* One `groupRoleMap` shape `{ [idpGroup: string]: TenantRole | customRole }` used by both SSO JIT provisioning and SCIM group patches.
* Domain ownership is the only thing that turns SSO on; unverified domains never redirect and never accept SCIM writes.
* Deactivation from either path (SCIM `active=false`, IdP removal on next login) sets `membership.suspendedAt` and revokes sessions within one request.
* Secrets (OIDC client secret, SAML private keys, SCIM tokens) are encrypted or hashed through the server-side secret helper; never in `attributes jsonb`.

**Interface contract**

* Provides: procedures `sso.provider.*`, `sso.domain.*`, `sso.enforcement.check`, `scim.token.*`; endpoints `/api/auth/sso/*`, `/scim/v2/*`; events `sso.domain.verified`, `scim.user.deactivated`, `auth.breakglass`; console pages `/console/settings/sso`, `/console/settings/scim`.
* Requires: PAP-57 server, PAP-58 memberships and roles, PAP-59 role effects, PAP-43 jobs, PAP-63 console host, PAP-38 audit, server-side encryption helper (data-layer).
* Tables: `ssoProvider` (extended), `tenant_domain`, `scimToken`, `scim_request`, `membership.externalId`, `membership.suspendedAt`.
* Consumers: PAP-224 sign-in form (domain lookup), PAP-220 (enforce interacts with 2FA), PAP-221 (SCIM-created users in DSAR registry).

**Definition of done**

* All three children Done.
* Integration test below green with mock IdPs; video attached.
* Sentinel Security Auditor signs off on certificate handling, token storage, replay protection (`InResponseTo`, nonce) and break-glass auditing.
* `docs/platform/enterprise-sso-scim.md` with Okta and Entra guides; changelog under "Identity".

**Test plan**

Integration test `apps/web/e2e/functional/enterprise.spec.ts` against the ephemeral stack:

* Owner verifies `acme.test` (mocked resolver), configures the mock OIDC IdP, a new user `ada@acme.test` signs in from the public sign-in page and lands as `member` of Acme; switch the provider to SAML and repeat with the `samlify` mock.
* SCIM replay of the Okta fixture creates three users, one group patch promotes one to `staff-finance`, one deactivation revokes an active session within the same request.
* Enforce on: magic link for `acme.test` refused; owner passkey break-glass succeeds and is audited.
* Screenshots of both console pages at seven widths light and dark; axe clean.

**Demo**

In the console add the mock IdP and verify the domain, then in a private window type `ada@acme.test` on the sign-in page and watch the redirect and JIT membership; run `pnpm scim:replay fixtures/okta` and refresh Members. Under two minutes.

**Edge cases**

Cross-child: a SCIM-created user whose domain later loses verification keeps membership but loses SSO login; a user deactivated by SCIM who signs in via SSO is refused with a clear message; two tenants claiming one domain is rejected at verification, so SCIM cannot create the conflict.

**Dependencies**

PAP-58 (hard). Soft: PAP-57, PAP-59, PAP-43, PAP-63, PAP-38, PAP-220.

**Agent**

Forge leads protocol work; Iris (Component Crafter) on console pages. Sentinel (Security Auditor mandatory, Edge Case Hunter with SCIM fixtures) reviews every child.

**Size**

L, split into 3 children (M, M, M).
"""
