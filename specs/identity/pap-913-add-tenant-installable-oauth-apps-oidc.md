---
identifier: "PAP-913"
title: "Add tenant-installable OAuth apps: OIDC provider for third-party apps with consent screens, client registration, scopes mapped to API key scopes, token introspection and revocation"
project: "identity"
projectName: "Identity, Roles & Audiences"
phase: "P2"
type: "Build"
priority: 4
surfaces: ["Developer"]
milestone: "Agent principals and enterprise"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-38", "PAP-60", "PAP-220", "PAP-222", "PAP-226", "PAP-581", "PAP-587"]
blocks: []
key: "r4/identity/oauth-provider-apps"
url: "https://linear.app/paperos/issue/PAP-913/add-tenant-installable-oauth-apps-oidc-provider-for-third-party-apps"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:51:41.818Z"
model: "claude-opus-5"
effort: "high"
estimate: 3
dueDate: null
cycle: null
---

# PAP-913: Add tenant-installable OAuth apps: OIDC provider for third-party apps with consent screens, client registration, scopes mapped to API key scopes, token introspection and revocation

**Model / Effort:** Opus 5 (`claude-opus-5`) / high — Build M

**Goal**

Let other software log in as a PaperOS user with permission: extend the PAP-226 OIDC provider (built for Forgejo SSO) into a tenant-facing OAuth 2.1 and OIDC authorization server where tenants register client apps, users see a consent screen listing scopes, scopes map to the PAP-222 API key scope model, tokens can be introspected and revoked, and every grant appears in session management (PAP-220).

**Scope**

In: Better Auth OIDC provider plugin configuration: `oauth_client` (tenant, name, redirect URIs, PKCE required, scopes allowed, logo, status), authorization code with PKCE only, refresh tokens with rotation, `introspect` and `revoke` endpoints, JWKS per tenant. Consent screen page (spec) with scope descriptions from the PAP-222 scope registry; grants listed under `/portal/settings/security` and the console with revoke; developer page section in `/console/developers` for client registration. Audit (PAP-38) of grants and revocations; rate limits on token endpoints (PAP-304).

Out: Dynamic client registration. Device flow. Acting as an OAuth client to third parties (PAP-57).

**Spec**

* Scopes never exceed the granting user's permissions; tokens carry the user principal and the client id; `can()` evaluates the user with a `via: client` attribute so policies may restrict clients
* Refresh token reuse detection revokes the family
* Client secrets hashed; public clients use PKCE only

**Interface contract**

Provides: OAuth 2.1 and OIDC authorization server for tenants, `oauth_client`, consent screen, grants management, introspection and revocation. Consumes: OIDC provider base (PAP-226), API key scopes (PAP-222), agent principals model (PAP-60), sessions (PAP-220), audit (PAP-38), rate limits (PAP-304). Consumed by: tenants' integrations, future marketplace extensions (module-system v0.3), assistant BYO tools (v0.3).

**Definition of done**

* A sample third-party app completes login with consent, calls the API with a scoped token, is revoked from the portal and loses access; refresh reuse detection tested; conformance against an OIDC certification test subset
* Every new page has a `page.spec.yaml` (PAP-114) that passes the validator, declared loading, empty, error and denied states, and Gate 3 screenshots at 375, 768, 1024 and 1920 in light and dark themes.
* Linear comment on the issue with the evidence links (PR, gate artefacts, recording or report) and the module docs page updated where the interface changed.

**Test plan**

* Unit: scope intersection; PKCE; rotation.
* Integration: full code flow with recorded client; introspection; revocation propagation.
* Isolation: the PAP-34 cross-tenant harness auto-enrols every new table; one negative case per new oRPC procedure proves `NOT_FOUND` on a foreign tenant row.

**Demo**

Register "Zapier-like app" in the developer page, log in from the sample app, approve two scopes, list the grant in the portal and revoke it.

**Edge cases**

* User removed from the tenant: all grants for that tenant revoke immediately
* Module disabled for the tenant (PAP-266): routes return `MODULE_DISABLED` (409), slot fills unmount and the manifest declares the dependency so consumers fail closed rather than half-render.

**Dependencies**

PAP-226, PAP-222 (hard), PAP-60, PAP-220, PAP-38 (hard), PAP-304 (soft).

**Agent**

Builder: Forge. Reviewer: Sentinel (Security Auditor).

**Size**

M: one session.
