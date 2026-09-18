---
identifier: "PAP-231"
title: "SCIM 2.0 server for Users and Groups"
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
blockedBy: ["PAP-57", "PAP-58", "PAP-226", "PAP-579"]
blocks: ["PAP-232"]
key: "identity/sso-scim/scim-server"
url: "https://linear.app/paperos/issue/PAP-231/scim-20-server-for-users-and-groups"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:51:43.804Z"
model: "claude-sonnet-5"
effort: "low"
estimate: 3
dueDate: null
cycle: null
---

# PAP-231: SCIM 2.0 server for Users and Groups

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / low — Deferred label (excluded from Oct-1 scope)

**Goal**

Deferred to v0.2 by the Execution Schedule (NJ-14 stop-loss 09-27 can reinstate). Not claimable before 10-01.

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
