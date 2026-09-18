---
identifier: "PAP-578"
title: "Organization plugin mapped onto `tenants` and `workspaces`, `withTenant` middleware setting the RLS session variables, `org.*` procedures and tenancy events"
project: "identity"
projectName: "Identity, Roles & Audiences"
phase: "P0"
type: "Build"
priority: 1
surfaces: ["Staff"]
milestone: "Auth works across web and desktop"
state: "Backlog"
parent: "PAP-58"
children: []
blockedBy: ["PAP-33", "PAP-34", "PAP-57", "PAP-223"]
blocks: ["PAP-62", "PAP-63", "PAP-86", "PAP-177", "PAP-458", "PAP-579", "PAP-582", "PAP-584", "PAP-588", "PAP-589", "PAP-591", "PAP-595", "PAP-598"]
key: "r4/identity/tenancy-core"
url: "https://linear.app/paperos/issue/PAP-578/organization-plugin-mapped-onto-tenants-and-workspaces-withtenant"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:10.719Z"
model: "claude-opus-5"
effort: "medium"
estimate: 3
dueDate: "2026-09-23"
cycle: null
---

# PAP-578: Organization plugin mapped onto `tenants` and `workspaces`, `withTenant` middleware setting the RLS session variables, `org.*` procedures and tenancy events

**Model / Effort:** Opus 5 (`claude-opus-5`) / medium — Build M

**Goal**

First half of PAP-58, on the two-half-day-slack auth chain (33 → 223 → 224 → 58): make the active tenant follow every request so the PAP-34 RLS boundary applies to humans. The organization plugin maps onto the existing `tenants` and `workspaces` tables, `withTenant` sets the session variables inside the request transaction, and the `org.*` procedures and events exist for the UI half.

**Scope**

In: `packages/auth/src/organization.ts` (plugin config with the `schema` mapping `organization -> tenants`, `team -> workspaces`, roles via `createAccessControl`), migration adding `membership.role`, `membership.attributes jsonb`, `tenants.slug`, `tenants.logoFileId`, `tenants.deletedAt`, `withTenant` middleware in `apps/api`, procedures `org.create|switch|transferOwnership|delete|leave`, `org.members.list|updateRole|remove`, events `tenant.created|deleted`, `membership.changed`, `docs/platform/tenancy.md` with the context propagation diagram.

Out: Invitations, pages, `TenantSwitcher`, `useTenant()` (sibling PAP-579); policies (PAP-59); SSO and SCIM (PAP-65); billing (PAP-177); onboarding (PAP-367).

**Spec**

* Plugin: `organization({ teams: { enabled: true, maximumTeams: 50 }, organizationLimit: 10, creatorRole: 'owner', roles: owner|admin|staff|member|viewer })`; versions from PAP-56.
* `withTenant` verifies membership of the principal in the tenant from `session.activeOrganizationId` (or `x-tenant` header / subdomain per Contracts §4) and runs `SET LOCAL app.tenant_id, app.principal_id, app.actor_id, app.role, app.attrs, app.actor_kind, app.request_id` inside the request transaction; `app.actor_id` equals `app.principal_id` (Contracts §1).
* Missing or mismatched tenant on a tenant-scoped procedure is `400 VALIDATION` (Contracts §4 retires `412 TENANT_REQUIRED`); header and subdomain disagreeing is also 400.
* Lifecycle: owner may transfer to an admin; the last owner cannot leave; `org.delete` sets `deletedAt` and hands the grace period to PAP-432 (`requestDeletion`), never hard-deletes here.
* Events published with `publish(tx, ...)` from PAP-555 (soft: in-process emitter with the same signature until it lands); `membership.changed` also triggers `permission.changed` (PAP-591).
* `org.members.updateRole` refuses raising a role above the caller's own; system roles immutable (PAP-33 invariant).

**Interface contract**

Provides: `withTenant` middleware and the session-variable contract, procedures `org.*` and `org.members.*`, events above, `TenantContext` builder, `requireTenantRole(role)` helper.

Consumes: Better Auth server (PAP-223), core tables (PAP-33), RLS harness (PAP-34), oRPC chain (PAP-267), event bus (PAP-555, soft), lifecycle (PAP-432, soft). Consumed by the sibling, PAP-62, PAP-63, PAP-86, PAP-177, PAP-228, PAP-458, PAP-140.

**Definition of done**

* Integration: `withTenant` sets all seven variables inside the transaction (asserted through `current_setting` in a test procedure); the PAP-34 harness passes with variables set by the middleware.
* Member of A calling a scoped procedure with B's tenant gets 400 or 403 per the matrix; `updateRole` above own role refused; last owner cannot leave (Vitest through `callAs`).
* Migration applies on an empty database and on the PAP-33 seed with no duplicate columns; `tenant.created` event observed with `expectEvent`.
* `docs/platform/tenancy.md` sequence diagram; changelog under Identity; Sentinel Security Auditor signs off on the middleware.

**Test plan**

* Unit: role enum mapping, slug reserved words, tenant resolution matrix (session, header, subdomain, mismatch), ownership transfer rules.
* E2E: API-level Playwright: create tenant, add a second seeded member, switch, call a scoped procedure with the wrong tenant id and read the 400; runs on the ephemeral stack.

**Demo**

Reviewer runs `pnpm tsx examples/tenancy.ts` which creates Acme, switches the session to it, calls a scoped procedure and prints the `current_setting` values, then repeats with the wrong tenant to show the 400. Under a minute.

**Edge cases**

* Principal in several tenants with no active one: 400 with `details[0].issue = 'tenant-required'` and the list of tenant slugs so the client can show the picker.
* Active tenant deleted mid-session: 400 with `tenant-gone`; the sibling redirects to `/org/switch`.
* Agent key scoped to a tenant (PAP-60): tenant taken from key metadata; a differing header is refused.

**Dependencies**

Blocked by PAP-223, PAP-33, PAP-34 (hard). Soft: PAP-267, PAP-432, PAP-555, PAP-591. Blocks PAP-62, PAP-63, PAP-86, PAP-177, PAP-458 and the sibling PAP-579.

**Agent**

Builder: Forge (Schema Wright). Reviewer: Sentinel (Security Auditor).

**Size**

M: one session.

*Round 4 critique fix (2026-09-18):* resolved 3 round-4 file keys in this description to Linear identifiers: `r4/data-layer/events-core` = PAP-555, `r4/identity/permission-propagation` = PAP-591, `r4/identity/tenancy-ui` = PAP-579.
