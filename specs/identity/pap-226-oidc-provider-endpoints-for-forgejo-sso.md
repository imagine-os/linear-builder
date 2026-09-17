---
identifier: "PAP-226"
title: "OIDC provider endpoints for Forgejo SSO"
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
blockedBy: ["PAP-223"]
blocks: []
key: "identity/better-auth/oidc-provider"
url: "https://linear.app/paperos/issue/PAP-226/oidc-provider-endpoints-for-forgejo-sso"
source: "Linear snapshot 2026-09-17T13:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T04:04:36.750Z"
---

# PAP-226: OIDC provider endpoints for Forgejo SSO

**Goal**

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
