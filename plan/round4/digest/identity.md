# Round 4 digest: Identity, Roles & Audiences (`identity`)

Benchmarks: Auth0 / Okta (tenant policies, MFA, device flow), Clerk (organizations, custom roles, sessions UI), Better Auth plugins (passkey, organization, twoFactor, apiKey, captcha, deviceAuthorization, sso, scim), Keycloak (roles, service accounts), WorkOS (SSO, SCIM, org-to-org), Ory Kratos/Keto, Cerbos and Oso (policy explain, playground), OpenFGA / Zanzibar (relations and sharing), Supabase Auth (RLS integration), GitHub sharing model (per-resource roles, link visibility)

## Feature matrix

| Feature | Status | Covered by | Note |
|---|---|---|---|
| Auth library ADR (Better Auth vs Lucia vs Clerk vs Auth.js) | covered | PAP-56 |  |
| Passkeys, magic link, Google and GitHub OAuth | covered | PAP-57, PAP-223, PAP-224 |  |
| Password authentication | gap | - | intentionally not offered (blueprint non-goal); documented in the sign-in copy |
| Phone or SMS OTP factor | gap | - | not planned for v0.1; Twilio adapter exists in growth (PAP-404) if needed |
| Tauri deep-link bearer sessions and keychain storage | covered | PAP-225 |  |
| OIDC provider for Forgejo and embedded tools | covered | PAP-226 |  |
| CLI and headless login (device flow) | gap | r4/identity/device-flow-login | gh/flyctl parity; `paperos create` needs it |
| Sign-in abuse controls: CAPTCHA, lockout, disposable domains | gap | r4/identity/auth-abuse-controls | PAP-223 only rate-limits sign-in |
| Session listing, device labels and revoke | partial | PAP-220, r4/identity/sessions-stepup | split child |
| TOTP, backup codes and account recovery | partial | PAP-220, r4/identity/mfa-recovery | split child |
| Step-up authentication for sensitive actions | partial | r4/identity/sessions-stepup | child of PAP-220 |
| Tenant session and MFA policy (idle, absolute, require MFA, IP allowlist) | gap | r4/identity/session-policy | Auth0/WorkOS parity |
| Email verification and email change | covered | PAP-224, PAP-62 | profile page owns change |
| Account linking across providers | partial | PAP-223 | link by verified email; amendment adds `accountLinking` config |
| Audience model and segments | covered | PAP-55 | keystone spec |
| Organizations, workspaces, `withTenant`, session variables | partial | PAP-58, r4/identity/tenancy-core | split child; 412 corrected to 400 |
| Invitations, tenant switcher, org pages | partial | PAP-58, r4/identity/tenancy-ui | split child |
| First-run onboarding wizard | covered | PAP-367 | app-shell |
| Tenant lifecycle and deletion grace | covered | PAP-432 | data-layer |
| Policy model, evaluator, explain | covered | PAP-227 |  |
| SQL predicate compiler and RLS helpers | covered | PAP-228 |  |
| Spec adapter, `authorize()` middleware, `useCan` | covered | PAP-229 |  |
| Permission matrix tests at policy, HTTP and UI level | covered | PAP-64 |  |
| Custom roles and permission sets | gap | r4/identity/custom-roles | brief: different customer and staff types as configuration |
| Per-resource grants and sharing (ReBAC-lite) | gap | r4/identity/resource-grants | views, docs, canvases each needed it |
| Public or guest links with expiry and passcode | gap | r4/identity/resource-grants | folded into grants; PAP-396 keeps pay tokens |
| Field-level permissions and response masking | gap | r4/identity/field-permissions | Hasura column privileges parity |
| Permission change propagation to sessions, rooms and shapes | gap | r4/identity/permission-propagation | three consumers assumed the topic |
| Access checker / policy playground UI | gap | r4/identity/access-checker | Cerbos playground parity; CLI explain exists |
| Entitlements from plans | covered | PAP-178 | business-core |
| Agents as principals with scoped keys | partial | PAP-60, r4/identity/agent-keys | split child |
| Agent attribution, badge and quotas | partial | PAP-60, r4/identity/agent-attribution-quotas | split child |
| Delegated authority (agent acting for a person) | gap | r4/identity/delegated-authority | PAP-61 leaves semantics to nobody |
| Internal service principals and service-to-service auth | gap | r4/identity/service-principals | collab server, worker, orchestrator have no principal |
| Staff impersonation with audit and customer visibility | covered | PAP-61 |  |
| Customer portal frame and login | partial | PAP-62, r4/identity/portal-frame | split child |
| Portal profile, security, billing stub, preferences | partial | PAP-62, r4/identity/portal-account-pages | split child |
| Staff console frame, navigation, audience filter | partial | PAP-63, r4/identity/console-frame | split child |
| Console admin pages | partial | PAP-63, r4/identity/console-admin-pages | split child |
| Enterprise SSO (OIDC, SAML) with domain verification | covered | PAP-65, PAP-230 | deferred |
| SCIM provisioning | covered | PAP-231 | deferred |
| SSO enforcement and break-glass | covered | PAP-232 | deferred |
| Auto-join organisation by verified email domain (without SSO) | partial | PAP-230 | only inside the deferred SSO child; acceptable for v0.1 |
| Tenant API keys, webhooks and SDK for developers | covered | PAP-222 | deferred |
| Privacy tooling: DSAR export and erasure, consent, legal pages | covered | PAP-221 | deferred |
| Security threat model and hardening baseline | covered | PAP-219 |  |
| Founder root of trust and revoke-all | covered | PAP-301 |  |
| Security telemetry for auth anomalies | covered | PAP-356 | quality |
| Test-mode `login-as` and audience fixtures | covered | PAP-240 | quality |
| Partner or reseller managed tenants | gap | r4/identity/partner-managed-tenants | deferred to v0.2; agency pack needs it |
| User profile and preferences model | covered | PAP-33, PAP-62 | `user.attributes` |
| Login history visible to the user | covered | PAP-61, PAP-220 | access history embed |
| Identity contract, conformance and kernel wiring | covered | PAP-456, PAP-457, PAP-458 |  |
| Presence privacy per audience | covered | PAP-141 | realtime; amendment on awareness filtering |

## New issues

| Key | Title | Parent | Size | Model | Deferred |
|---|---|---|---|---|---|
| `r4/identity/tenancy-core` | Organization plugin mapped onto `tenants` and `workspaces`, `withTenant` middleware setting the RLS session variables, `org.*` procedures and tenancy events | PAP-58 | M | Opus 5 / medium |  |
| `r4/identity/tenancy-ui` | Invitations with email and `/invite/$token`, `TenantSwitcher`, `useTenant()` with sync remount, org settings pages with specs and the `tenantChanged` broadcast | PAP-58 | M | Sonnet 5 / high |  |
| `r4/identity/mfa-recovery` | TOTP second factor with backup codes, the `/auth/recover` flow that requires TOTP or a code before a new passkey, and the new-device, two-factor-enabled and recovery-used emails | PAP-220 | M | Opus 5 / high |  |
| `r4/identity/sessions-stepup` | Session and device listing with revoke, `requireRecentAuth()` step-up with `ReauthDialog`, sign-in alerts and the `SecurityPage` mounted in portal and console | PAP-220 | M | Sonnet 5 / high |  |
| `r4/identity/console-frame` | Console layout and slots, `fromAppSpec` navigation, tenant and workspace switchers in the sidebar, `AudienceFilter` and `registerConsoleSection` for modules | PAP-63 | M | Sonnet 5 / high |  |
| `r4/identity/console-admin-pages` | Seven console admin pages with specs: overview, members, roles, audit, impersonations entry, agents, general and branding settings | PAP-63 | M | Sonnet 5 / high |  |
| `r4/identity/portal-frame` | Portal layout with top bar, bottom tab bar and left rail, `PortalNav` from `app.spec.yaml`, login and home pages with specs, states and the PWA install placement | PAP-62 | M | Sonnet 5 / high |  |
| `r4/identity/portal-account-pages` | Portal profile, security, billing stub and notification preference pages with specs, optimistic save through the write queue and the unsaved-changes prompt | PAP-62 | M | Sonnet 5 / medium |  |
| `r4/identity/agent-keys` | Agent users synced from the roster, Better Auth `apiKey()` with the `pos_agent_` prefix and metadata, `withScopes()` intersection with the scope map and the `pnpm agents:key` CLI for the orchestrator | PAP-60 | M | Opus 5 / high |  |
| `r4/identity/agent-attribution-quotas` | Agent attribution and quotas: `X-PaperOS-Actor` header, audit fields for character, session and issue, the `ActorBadge` component and per-character daily quotas emitting `agent.quota.exceeded` | PAP-60 | S | Sonnet 5 / medium |  |
| `r4/identity/custom-roles` | Custom roles and permission sets: tenant-defined roles extending a base role, a permission picker with `explain`, assignment rules, immutability of system roles and audited changes | - | M | Sonnet 5 / high |  |
| `r4/identity/resource-grants` | Per-resource grants and share links: `resource_grant` table, `hasRelation` policy operator compiled to SQL, `ShareDialog` primitive and signed guest links for anonymous access with expiry and passcode | - | M | Opus 5 / high |  |
| `r4/identity/field-permissions` | Field-level permissions: policy `fields:` allow and deny lists, response masking in the repository and oRPC output, write rejection per field, `useCan` for fields and spec `data.fields[].access` | - | M | Opus 5 / high |  |
| `r4/identity/permission-propagation` | Permission change propagation: `permission.changed` topic, versioned server-side policy cache, client refetch of `permissions.mine`, Hocuspocus room re-check and Electric shape invalidation | - | S | Opus 5 / medium |  |
| `r4/identity/auth-abuse-controls` | Sign-in and sign-up abuse controls: Turnstile challenge on public auth and forms, disposable-domain list, progressive lockout per email and IP, and `auth.lockout` security events | - | S | Opus 5 / medium |  |
| `r4/identity/service-principals` | Internal service principals: `service` users for the worker, collab server, Electric proxy and orchestrator, short-lived signed service tokens through `SecretsPort`, `requireService()` middleware and the service call matrix | - | M | Opus 5 / high |  |
| `r4/identity/delegated-authority` | Delegated authority for agents: `actingFor` evaluation as the intersection of delegator permissions and agent scopes, delegation grants with expiry and consent, dual-actor audit and the "Forge for Justin" badge | - | M | Opus 5 / high |  |
| `r4/identity/session-policy` | Tenant session and MFA policy: per-audience idle and absolute timeouts, MFA required for staff and admins, trusted devices, sign-up domain allowlist and IP allowlist for staff, enforced by `requireSession` | - | S | Opus 5 / medium |  |
| `r4/identity/access-checker` | Console access checker: pick a principal, action and resource, see the decision with matched policies, spec lines, field rules and the SQL predicate, and save the case as a permission-matrix fixture | - | S | Sonnet 5 / medium |  |
| `r4/identity/device-flow-login` | CLI and headless login: OAuth device authorization flow for `paperos login`, keychain token storage, `paperos whoami`, `--as-agent` key exchange and the approval page | - | S | Sonnet 5 / medium |  |
| `r4/identity/partner-managed-tenants` | Partner-managed tenants: partner organisation links, delegated administration across client tenants with scoped roles, a partner switcher and client-visible partner access history | - | M | Sonnet 5 / low | yes |

## Amendments to existing specs

* **PAP-58** (Spec): Corrections from the Contracts document §1 and §4: (1) a tenant-scoped procedure without an active tenant returns `400 VALIDATION` with `details[0].issue = 'tenant-required'`; `412 TENANT_REQUIRED` is retired. (2) `withTenant` sets `app.actor_id` to the same value as `app.principal_id` and also sets `app.actor_kind` and `app.request_id`, so PAP-34 policies and PAP-38 triggers read one contract. Work is split into `r4/identity/tenancy-core` (middleware, plugin mapping, procedures) and `r4/identity/tenancy-ui` (invitations, switcher, pages).
* **PAP-223** (Interface contract): Add exports for non-HTTP consumers: `verifySessionToken(token) -> Principal | null` and `verifyApiKey(key) -> Principal | null` (the latter delegating to the PAP-60 plugin once it lands), used by the Hocuspocus `onAuthenticate` hook (PAP-140) and the Electric shape proxy (PAP-270). Configure `account: { accountLinking: { enabled: true, trustedProviders: ['google', 'github'] } }` so a verified-email OAuth sign-in links to the existing user rather than creating a duplicate; test both.
* **PAP-229** (Spec): `PermissionProvider` also refetches on the `permission.changed` topic (`r4/identity/permission-propagation`) delivered through the push transport or a 30 s version poll of `permissions.version`; `useCan` gains an optional `{ field }` argument once `r4/identity/field-permissions` lands and returns `'loading'` for unknown fields until then.
* **PAP-60** (Spec): Rate limiting: replace the plugin's in-memory `rateLimit` with `rateLimit('apiKey')` from `r4/data-layer/rate-limits` so limits survive restarts and are shared by both API replicas; the "state lost on restart" edge case is then void. Work is split into `r4/identity/agent-keys` and `r4/identity/agent-attribution-quotas`.
* **PAP-61** (Spec): Realtime boundary: an impersonation session in `read` mode connects to Hocuspocus rooms with `connection.readOnly = true` and never publishes awareness under the customer's identity (the collab server reads `session.impersonation` through `verifySessionToken`); `write` mode publishes awareness as "Support (viewing as Ada)". `impersonation.start|stop` publish `permission.changed` so open rooms and shapes re-evaluate (`r4/identity/permission-propagation`).
* **PAP-220** (Definition of done): Make the security sign-off concrete: `/auth/recover` and TOTP verification allow 5 attempts per 15 minutes per account and per IP, then lock with a neutral message (`r4/identity/auth-abuse-controls` owns the lockout table); backup codes hashed with argon2id (memory 64 MB, iterations 3); a used TOTP step cannot be replayed within its window; tests for each. Work is split into `r4/identity/mfa-recovery` and `r4/identity/sessions-stepup`.
* **PAP-63** (Interface contract): `registerConsoleSection(section, items)` is the extension point for round-4 pages: `r4/identity/custom-roles` (roles edit mode), `r4/identity/access-checker`, `r4/identity/session-policy` and `r4/data-layer/jobs-admin`; items carry `audiences` and an optional `can` guard and render nothing when denied. Work is split into `r4/identity/console-frame` and `r4/identity/console-admin-pages`.
* **PAP-62** (Spec): Work is split into `r4/identity/portal-frame` and `r4/identity/portal-account-pages`; `registerPortalSection(id, component)` lets PAP-177 (billing), PAP-136 (preferences) and PAP-221 (legal) replace stubbed sections without editing the portal package. Delete account routes to PAP-221 when present, else `users.requestDeletion` with the PAP-432 grace explanation.

## Cross-project suggestions

* **realtime**: Hocuspocus (PAP-140) subscribes to `permission.changed` and awareness filtering uses `verifySessionToken` — PAP-140 re-checks permissions every 5 minutes; the topic from `r4/identity/permission-propagation` makes it seconds and closes rooms on revocation.
* **tables**: View sharing (PAP-172) and record pages (PAP-333) consume `r4/identity/resource-grants` and `r4/identity/field-permissions` — Avoids a second grants table for views and gives the grid a rule for hiding masked columns.
* **collab**: Tenant docs (PAP-379) and canvas overlays (PAP-321) use `ShareDialog` and `hasRelation` from `r4/identity/resource-grants` — Both need per-document sharing and guest links; one dialog and one policy operator.
* **agents**: Orchestrator (PAP-96) mints `actingFor` keys only against a live delegation (`r4/identity/delegated-authority`) and services use `mintServiceToken` — Closes the "agent acting for an admin is an admin" hole and gives the orchestrator a principal of its own.
* **app-shell**: `paperos create` and `paperos upgrade` (PAP-22, PAP-430) authenticate through `r4/identity/device-flow-login` — The golden path currently has no way to call the PaperOS API as the person running it.
* **quality**: Security telemetry (PAP-356) ingests `auth.lockout`, `auth.captcha_failed`, `service.denied` and `auth.device.approved` — New detection sources from the abuse controls, service principals and device flow.
* **spec-builder**: Access section (PAP-116) gains `fields[].access` and custom-role audience references — Field permissions and tenant roles must be declarable in page specs to be tested by PAP-64.
* **tables**: `r4/tables/field-level-permissions` should compile `FieldDef.permissions` into `Policy.fields` and call `maskFields` from `r4/identity/field-permissions` — Round-4 dedup: one masking function and one explain path for entity and custom datasets instead of `fieldMask` and `maskFields` side by side.

## What was missing and why it matters

1. Authorization stopped at roles and rows: nothing let a tenant define its own roles, share one record or document with one person or a link, or hide a column from an audience; three new primitives (custom roles, resource grants, field permissions) turn the brief's 'different types of customers and staff' into configuration.
2. Three consumers (Hocuspocus rooms, the shape proxy, the client policy cache) assumed a `permission.changed` signal nobody emitted, so a removed staff member would have kept live data open; the propagation issue closes it in seconds.
3. Agents acting for people had a marker but no semantics: `actingFor` now means the intersection of delegator permissions and agent scopes under an expiring, consented delegation, and internal services finally have principals and tokens of their own.
4. Five M issues (PAP-58, PAP-220, PAP-62, PAP-63, PAP-60) each carried two sessions of work on or near the auth critical chain; splitting them lets the middleware, TOTP, frames and keys land before pages, recovery and quotas.
5. Public auth had rate limits but no abuse controls, no tenant session policy and no way for a CLI or a Claude session to sign in as a person; captcha and lockout, session policy and the device flow fill those with standard Better Auth plugins.
