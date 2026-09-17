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
children: []
blockedBy: ["PAP-224", "PAP-57"]
blocks: ["PAP-177", "PAP-221", "PAP-230", "PAP-231", "PAP-62", "PAP-63", "PAP-65", "PAP-86"]
key: "identity/org-tenancy"
url: "https://linear.app/paperos/issue/PAP-58/implement-organizations-workspaces-invitations-and-tenant-switching"
source: "plan/specs/bucket-1.json (round-1 canonical spec JSON)"
---

# PAP-58: Implement organizations, workspaces, invitations and tenant switching

**Goal**

Implement multi-tenant membership on top of Better Auth: organizations are tenants, workspaces are teams inside them, members are invited by email, and users switch the active tenant with every request and RLS policy following. This makes the tenant boundary from data-layer/rls-tenancy real for users rather than only for tests.

**Scope**

- In: Better Auth organization plugin configuration, tenant and workspace mapping to core entities, invitation flow with email, tenant switcher component and hook, per-request tenant context for API and RLS, ownership transfer, tenant deletion with grace period, tests and pages.
- Out: role and permission evaluation beyond the built-in five roles (identity/rbac-abac), enterprise SSO/SCIM (identity/sso-scim), billing per tenant (business-core/stripe-billing).

**Spec**

In `imagine-os/paperos-template`:

- Plugin: add `organization({ teams: { enabled: true, maximumTeams: 50 }, allowUserToCreateOrganization: true, organizationLimit: 10, creatorRole: 'owner', roles: { owner, admin, staff, member, viewer } via access control `createAccessControl` , sendInvitationEmail })` to the server in `packages/auth`; client plugin `organizationClient()`.
- Schema mapping: Better Auth `organization` maps onto the `tenants` table and `team` onto `workspaces` from data-layer/core-entities; use the plugin's `schema` option to rename tables and fields so there is one table per concept, not two. `membership` gains `role` (enum above) and `attributes jsonb` (staffRole, tier) consumed by the audience model. Add `slug` unique per tenant, `logoFileId` (data-layer/file-storage), `deletedAt` for grace period.
- Active tenant: stored in the session (`session.activeOrganizationId`); oRPC middleware `withTenant` reads it, verifies membership, and runs `SET LOCAL app.tenant_id = $1; SET LOCAL app.principal_id = $2; SET LOCAL app.role = $3` inside the request transaction so data-layer/rls-tenancy policies apply. Requests with no active tenant to tenant-scoped procedures return 412 `TENANT_REQUIRED`.
- Invitations: `POST /api/auth/organization/invite-member` with email and role; email template `invitation.tsx`; landing route `/invite/$token` that signs the user in (magic link if new) and accepts; expiry 7 days; resend and revoke from the members page; invitee count limited per tenant plan later (business-core/entitlements hook point `beforeInvite`).
- Pages and specs (`specs/pages/org/*.spec.yaml`): `/org/new` (name, slug auto-suggested, logo), `/org/settings/general`, `/org/settings/members` (table via the grid view if tables/grid-view exists, else a simple list from design-system/data-display), `/org/settings/workspaces`, `/invite/$token`, `/org/switch`.
- Components in `packages/ui` consumers: `TenantSwitcher` (Popover with search, recent tenants, create new), `RoleBadge`, `InviteMemberDialog`. Hook `useTenant()` returns `{ tenant, workspace, role, switchTenant, switchWorkspace }` and updates Electric shape subscriptions on change (data-layer/local-first-sync) by remounting the sync provider.
- Ownership transfer: owner may transfer to an admin; last owner cannot leave; tenant deletion sets `deletedAt`, hides the tenant, hard-deletes after 30 days via a job (Inngest or cron per libraries/backend-landscape choice), and is audited.

**Definition of done**

- Create tenant, create workspace, invite, accept, switch tenant and leave flows pass Playwright e2e (feeding quality/e2e-flows) and Vitest API tests.
- Cross-tenant test: a member of tenant A calling a tenant-scoped procedure with tenant B's id gets 403; RLS test from data-layer/rls-tenancy passes with the session variables set by `withTenant`.
- Invitation email renders (React Email preview screenshot) and expired tokens show a clear message.
- Screenshots of `/org/settings/members` and `TenantSwitcher` open at the seven widths, light and dark.
- axe clean on all org pages; keyboard-only switcher usage verified.
- `docs/platform/tenancy.md` with a sequence diagram of tenant context propagation; changelog entry under "Identity".
- Sentinel Security Auditor signs off on the middleware; Linear comment with demo link and e2e video.

**Edge cases**

- User invited to a tenant they already belong to: invitation accepted as a role update only if the inviter's role permits raising roles; otherwise no-op with a message.
- Invitation email address differs in case from the sign-in email: compare case-insensitively after normalisation.
- Active tenant deleted while a session is open: middleware returns 412 and the client redirects to `/org/switch`.
- User has 0 tenants after leaving: redirected to `/org/new` with the option to accept pending invitations.
- Slug collision with a reserved word (`api`, `admin`, `auth`, `dev`): reserved list enforced server-side and suggested alternative shown.
- Two tabs with different active tenants: session is server-side per device, so both share one active tenant; the second tab receives a `tenantChanged` BroadcastChannel event (realtime/multi-window-sync) and reloads its data.

**Dependencies**

- identity/better-auth (server and client). Soft: data-layer/core-entities and data-layer/rls-tenancy (tables and policies), data-layer/api-layer (middleware), design-system/primitives, data-layer/file-storage (logos).

**Agent**

- Builds: Forge (Schema Wright sub-agent) for schema and middleware; Iris (Component Crafter) for the switcher and pages.
- Reviews: Sentinel (Security Auditor, Code Reviewer, Visual Inspector).

**Size**

M: well-supported by the plugin, but tenant context must be correct at every layer.
