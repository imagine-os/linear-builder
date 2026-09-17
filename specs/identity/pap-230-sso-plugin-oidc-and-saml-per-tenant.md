---
identifier: "PAP-230"
title: "SSO plugin: OIDC and SAML per tenant with domain verification"
project: "identity"
projectName: "Identity, Roles & Audiences"
phase: "P2"
type: "Build"
priority: 4
surfaces: ["Staff"]
milestone: "Agent principals and enterprise"
state: "Backlog"
parent: "PAP-65"
children: []
blockedBy: ["PAP-58", "PAP-353"]
blocks: ["PAP-232"]
key: "identity/sso-scim/sso-plugin-domains"
url: "https://linear.app/paperos/issue/PAP-230/sso-plugin-oidc-and-saml-per-tenant-with-domain-verification"
source: "Linear snapshot 2026-09-17T13:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T13:05:04.815Z"
model: "claude-sonnet-5"
effort: "low"
---

# PAP-230: SSO plugin: OIDC and SAML per tenant with domain verification

**Goal**

Deferred to v0.2 by the Execution Schedule (NJ-14 stop-loss 09-27 can reinstate). Not claimable before 10-01.

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
