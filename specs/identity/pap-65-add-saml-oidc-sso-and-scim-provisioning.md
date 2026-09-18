---
identifier: "PAP-65"
title: "Add SAML/OIDC SSO and SCIM provisioning for enterprise tenants"
project: "identity"
projectName: "Identity, Roles & Audiences"
phase: "P2"
type: "Build"
priority: 3
surfaces: ["Staff"]
milestone: "Agent principals and enterprise"
state: "Backlog"
parent: null
children: ["PAP-232", "PAP-230", "PAP-231"]
blockedBy: ["PAP-58", "PAP-579"]
blocks: []
key: "identity/sso-scim"
url: "https://linear.app/paperos/issue/PAP-65/add-samloidc-sso-and-scim-provisioning-for-enterprise-tenants"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T13:49:22.921Z"
model: null
effort: null
estimate: null
dueDate: "2026-09-30"
cycle: null
---

# PAP-65: Add SAML/OIDC SSO and SCIM provisioning for enterprise tenants

**Model / Effort:** set on children (umbrella is never claimed)

**Goal**

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
