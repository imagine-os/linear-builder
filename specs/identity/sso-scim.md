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
blockedBy: ["PAP-58"]
blocks: []
key: "identity/sso-scim"
url: "https://linear.app/paperos/issue/PAP-65/add-samloidc-sso-and-scim-provisioning-for-enterprise-tenants"
source: "plan/specs/bucket-1.json (round-1 canonical spec JSON)"
---

# PAP-65: Add SAML/OIDC SSO and SCIM provisioning for enterprise tenants

**Goal**

Give enterprise tenants single sign-on through their own SAML 2.0 or OIDC identity provider and automated user lifecycle through SCIM 2.0, configured entirely in the console by a tenant owner, so no app code changes are required when an enterprise customer arrives.

**Scope**

- In: Better Auth SSO plugin configuration for OIDC and SAML per tenant, domain verification, console pages for IdP setup and SCIM tokens, a SCIM 2.0 server (Users and Groups) mapping to memberships and roles, JIT provisioning rules, enforcement options (SSO required), tests against reference IdP payloads, docs.
- Out: IdP-initiated deep linking to arbitrary pages (login lands on `/console` or `/portal`), SCIM for customers (staff only in this build), and directory sync beyond Users and Groups.

**Spec**

In `imagine-os/paperos-template`:

- Plugin: add `sso()` from Better Auth's SSO package (versions per identity/auth-research) to `packages/auth` with `provisionUser` hook creating the membership in the tenant that owns the verified email domain, `defaultRole: 'member'`, and `organizationProvisioning: { disabled: false, defaultRole }`. Store provider config per tenant in the `ssoProvider` table extended with `tenantId`, `type: 'oidc' | 'saml'`, `domains: string[]`, `enforce: boolean`, `jitRole`, `groupRoleMap jsonb`.
- Domain verification: owner adds `acme.com`; we issue a TXT record `paperos-verify=<token>`; a job checks DNS (`dns.resolveTxt`) and marks verified; SSO applies only to verified domains. Sign-in page from identity/better-auth detects a verified domain from the email and redirects to the tenant's IdP.
- SAML specifics: SP metadata at `/api/auth/sso/saml2/sp/metadata?tenant=<slug>`, ACS URL, signed assertions required, encryption optional, certificate rotation with two active certs. OIDC specifics: discovery URL, client id and secret (encrypted at rest with the app key from app-shell/env-config), PKCE.
- SCIM 2.0 server (`apps/api/src/scim/`): endpoints under `/scim/v2/` - `ServiceProviderConfig`, `ResourceTypes`, `Schemas`, `Users` (GET list with `filter` supporting `eq` on `userName` and `externalId`, `startIndex`, `count`; POST; GET by id; PUT; PATCH with `add/replace/remove` operations including `active`; DELETE), `Groups` (same, with `members` patch). Auth by per-tenant bearer token (`scimToken` table, hashed, shown once, revocable, expiry optional). Mapping: `userName` -> email, `active=false` -> membership `suspendedAt` set and sessions revoked, `externalId` stored, `Groups` -> roles via `groupRoleMap` (for example `IdP group "Finance" -> staffRole finance`). Responses follow RFC 7644 error format; ETags supported for `If-Match`.
- Console pages and specs (`specs/pages/console/sso.spec.yaml`, `scim.spec.yaml`): `/console/settings/sso` (choose type, paste metadata URL or XML, download SP metadata, verify domain, test login button, enforce toggle with a warning about lockout and a break-glass owner passkey exception), `/console/settings/scim` (generate token, base URL, group-to-role mapping editor, sync log of last 100 SCIM requests).
- Enforcement: when `enforce` is on, password-less local methods are disabled for that domain except owners with a registered passkey; magic links to those domains are refused with a message.
- Tests: SAML flow tested with a `samlify`-based mock IdP; OIDC with a mock provider (`oauth2-mock-server`); SCIM conformance with recorded request fixtures from Okta and Microsoft Entra documentation plus property tests for PATCH semantics.

**Definition of done**

- Owner configures OIDC and SAML in the console and logs in via each (Playwright with mock IdPs; video attached).
- Domain verification job verifies a TXT record in a test zone (or a mocked resolver in CI) and unverified domains never trigger SSO redirects.
- SCIM suite: create, update, deactivate, reactivate, delete user; create group and add member changes role; filters and pagination work; all fixtures pass; wrong token returns 401 in SCIM error format.
- Deactivated user's sessions are revoked within one request (test).
- Enforcement: a magic-link request for an enforced domain is refused; owner break-glass works (tests).
- Screenshots of both console pages at the seven widths, light and dark; axe clean.
- Sentinel Security Auditor signs off on certificate handling, token storage and replay protection (SAML `InResponseTo`, OIDC nonce).
- Docs `docs/platform/enterprise-sso-scim.md` with Okta and Entra setup guides; changelog entry under "Identity"; Linear comment with video and SCIM fixture results.

**Edge cases**

- Same email domain claimed by two tenants: second verification fails with guidance; subdomains are distinct domains.
- SCIM PATCH with unsupported path (`emails[type eq "work"].value`): implement the common filter path form; unknown paths return 400 `invalidPath`.
- IdP sends a user whose email already exists as a customer in another tenant: create a staff membership in the enterprise tenant; do not alter the other tenant.
- SAML certificate expired on the IdP side: login fails with a clear console error and an admin notification; no silent fallback to unsigned.
- SCIM token leaked: revocation from the console; all subsequent requests 401; sync log shows the last successful call.
- IdP clock skew beyond 5 minutes: assertion rejected; error text names skew as the likely cause.

**Dependencies**

- identity/org-tenancy (tenant settings, memberships). Soft: identity/better-auth (plugin host), identity/rbac-abac (group-to-role effects), data-layer/audit-log, app-shell/env-config (encryption key), identity/staff-console-shell (pages host).

**Agent**

- Builds: Forge (lead) for plugin and SCIM server; Iris (Component Crafter) for console pages.
- Reviews: Sentinel (Security Auditor mandatory, Code Reviewer, Edge Case Hunter with the SCIM fixtures).

**Size**

L: two federation protocols plus a SCIM server with conformance fixtures, all security-critical.
