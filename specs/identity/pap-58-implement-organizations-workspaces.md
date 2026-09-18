---
identifier: "PAP-58"
title: "Implement organizations, workspaces, invitations and tenant switching"
project: "identity"
projectName: "Identity, Roles & Audiences"
phase: "P0"
type: "Build"
priority: 1
surfaces: ["Staff"]
milestone: "Auth works across web and desktop"
state: "Backlog"
parent: null
children: ["PAP-579", "PAP-578"]
blockedBy: ["PAP-57", "PAP-224"]
blocks: ["PAP-62", "PAP-63", "PAP-65", "PAP-86", "PAP-177", "PAP-221", "PAP-230", "PAP-231", "PAP-367", "PAP-458", "PAP-506", "PAP-582", "PAP-584", "PAP-831"]
key: "identity/org-tenancy"
url: "https://linear.app/paperos/issue/PAP-58/implement-organizations-workspaces-invitations-and-tenant-switching"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:28:37.625Z"
model: null
effort: null
estimate: null
dueDate: "2026-09-23"
cycle: null
---

# PAP-58: Implement organizations, workspaces, invitations and tenant switching

**Model / Effort:** Opus 5 (`claude-opus-5`) / medium — Build M, P0 in identity

**Goal**

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

*Round 4 amendment (2026-09-18):*
Corrections from the Contracts document §1 and §4: (1) a tenant-scoped procedure without an active tenant returns `400 VALIDATION` with `details[0].issue = 'tenant-required'`; `412 TENANT_REQUIRED` is retired. (2) `withTenant` sets `app.actor_id` to the same value as `app.principal_id` and also sets `app.actor_kind` and `app.request_id`, so PAP-34 policies and PAP-38 triggers read one contract. Work is split into PAP-578 (middleware, plugin mapping, procedures) and PAP-579 (invitations, switcher, pages).

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

*Round 4 critique fix (2026-09-18):* resolved 2 round-4 file keys in this description to Linear identifiers: `r4/identity/tenancy-core` = PAP-578, `r4/identity/tenancy-ui` = PAP-579.
