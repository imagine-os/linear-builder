---
identifier: "PAP-579"
title: "Invitations with email and `/invite/$token`, `TenantSwitcher`, `useTenant()` with sync remount, org settings pages with specs and the `tenantChanged` broadcast"
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
blockedBy: ["PAP-224", "PAP-578"]
blocks: ["PAP-62", "PAP-63", "PAP-65", "PAP-86", "PAP-177", "PAP-221", "PAP-230", "PAP-231", "PAP-367", "PAP-458", "PAP-506", "PAP-582", "PAP-584", "PAP-831"]
key: "r4/identity/tenancy-ui"
url: "https://linear.app/paperos/issue/PAP-579/invitations-with-email-and-invitedollartoken-tenantswitcher-usetenant"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:10.909Z"
model: "claude-sonnet-5"
effort: "high"
estimate: 3
dueDate: "2026-09-23"
cycle: null
---

# PAP-579: Invitations with email and `/invite/$token`, `TenantSwitcher`, `useTenant()` with sync remount, org settings pages with specs and the `tenantChanged` broadcast

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / high — Build M

**Goal**

Second half of PAP-58: what humans touch. Invite by email with a landing page that signs in or signs up and accepts, switch tenants and workspaces from a searchable switcher, and let every consumer read `useTenant()`; the org settings pages ship with specs so PAP-63 can mount them.

**Scope**

In: Procedures `org.invite|resendInvite|revokeInvite|acceptInvite`, table `invitation` (plugin) with 7-day expiry and `beforeInvite` hook point (PAP-178 limits), React Email `invitation.tsx` through `sendEmail` (PAP-370, soft: Resend directly until it lands), pages and specs `specs/pages/org/{new,settings-general,settings-members,settings-workspaces,invite,switch}.spec.yaml`, components `TenantSwitcher`, `WorkspaceSwitcher`, `RoleBadge`, `InviteMemberDialog`, hook `useTenant()` returning `{ tenant, workspace, role, switchTenant, switchWorkspace }` that remounts the Electric sync provider (PAP-271) on change, BroadcastChannel message `tenantChanged`.

Out: Middleware and procedures for the tenant itself (sibling), console shell (PAP-63), onboarding wizard (PAP-367), SSO domain lookup (PAP-230).

**Spec**

* Invitation: `org.invite({ email, role, workspaceId? })` refuses roles above the caller's; existing member gets a role update only when the inviter may raise roles; case-insensitive email match; `/invite/$token` signs in (magic link if new) and accepts, then lands on `/org/switch`.
* Switcher: Popover with search, recent tenants, create action; keyboard operable; customer-friendly variant for PAP-62; hidden when the user has one tenant.
* `useTenant()` reads the session's active tenant; `switchTenant` calls `org.switch`, publishes `tenantChanged` on `paperos:<userId>` so other tabs reload, wipes or remounts local sync per PAP-572 (soft) and PAP-271.
* Pages use PAP-67 primitives and the PAP-71 table (grid from PAP-165 when present) for members; every page declares states and `access` audiences; copy in `packages/auth/src/copy.ts`.
* Zero tenants after leaving: `/org/new` lists pending invitations; the onboarding wizard (PAP-367) later replaces `/org/new` as the entry point.

**Interface contract**

Provides: `useTenant()`, `TenantSwitcher`, `WorkspaceSwitcher`, `RoleBadge`, `InviteMemberDialog`, procedures `org.invite*|acceptInvite`, route `/invite/$token`, specs above, message `tenantChanged`.

Consumes: Sibling procedures and middleware, sign-in form and pages (PAP-224), email package (PAP-370, soft), primitives (PAP-67, soft), table (PAP-71) or grid (PAP-165, soft), sync client (PAP-271, soft), routes and layouts (PAP-16). Consumed by PAP-62, PAP-63, PAP-86, PAP-367, PAP-582, PAP-584.

**Definition of done**

* Create tenant, create workspace, invite, accept as second user in another context, switch, leave: Playwright e2e (feeds PAP-86) green at 1280 and 375.
* Invitation email renders (React Email preview screenshot); expired token shows a clear message; resend and revoke tested.
* Screenshots of `/org/settings/members` and the open `TenantSwitcher` at seven widths, light and dark; axe clean; keyboard-only switcher verified.
* Six specs validate; changelog under Identity.

**Test plan**

* Unit: invitation expiry and case-insensitive match, role-raise refusal, switcher filtering and recent ordering, `tenantChanged` handling.
* E2E: the flow above plus: second tab receives `tenantChanged` and reloads to the new tenant within 500 ms; invite to an existing member updates the role only.

**Demo**

Sign in, create Acme, invite a seeded user, accept in a second browser context, switch tenants from the switcher and watch the members list change. Under two minutes.

**Edge cases**

* Invite link opened while signed in as a different account: page names the account and offers to switch.
* Invitation to a domain with SSO enforcement (PAP-230, deferred): accepted normally until enforcement exists; noted.
* Tenant logo missing: initials avatar.
* 1,000 members: table paginates through `org.members.list` cursors.

**Dependencies**

Blocked by PAP-578 (hard) and PAP-224 (hard, sign-in on the invite landing). Soft: PAP-370, PAP-67, PAP-71, PAP-165, PAP-271, PAP-16, PAP-178. Consumed by PAP-62, PAP-63, PAP-86.

**Agent**

Builder: Iris (Component Crafter) with Forge on procedures. Reviewer: Sentinel (Visual Inspector; Code Reviewer).

**Size**

M: one session.

*Round 4 critique fix (2026-09-18):* resolved 4 round-4 file keys in this description to Linear identifiers: `r4/data-layer/local-data-protection` = PAP-572, `r4/identity/console-frame` = PAP-582, `r4/identity/portal-frame` = PAP-584, `r4/identity/tenancy-core` = PAP-578.
