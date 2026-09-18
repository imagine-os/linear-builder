---
identifier: "PAP-588"
title: "Custom roles and permission sets: tenant-defined roles extending a base role, a permission picker with `explain`, assignment rules, immutability of system roles and audited changes"
project: "identity"
projectName: "Identity, Roles & Audiences"
phase: "P1"
type: "Build"
priority: 2
surfaces: ["Staff"]
milestone: "Roles and audiences enforced end to end"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-227", "PAP-578"]
blocks: []
key: "r4/identity/custom-roles"
url: "https://linear.app/paperos/issue/PAP-588/custom-roles-and-permission-sets-tenant-defined-roles-extending-a-base"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:12.901Z"
model: "claude-sonnet-5"
effort: "high"
estimate: 3
dueDate: "2026-09-25"
cycle: null
---

# PAP-588: Custom roles and permission sets: tenant-defined roles extending a base role, a permission picker with `explain`, assignment rules, immutability of system roles and audited changes

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / high — Build M

**Goal**

The brief asks for different types of customers and staff as configuration, not a rewrite. PAP-55 allows custom roles that extend one of the five base roles and PAP-33 stores `role.permissions`, but no issue lets a tenant owner create 'Finance viewer' or 'Support lead', pick what it may do, and assign it. Clerk, Auth0 and Keycloak all ship this; without it every app hardcodes roles.

**Scope**

In: Procedures `roles.list|create|update|archive|assign`, `role.base_role` and `role.policies jsonb` (an array of PAP-227 `Policy` fragments, allow-only), permission picker UI grouping actions by entity from the procedure registry (`procedureScopes()`, PAP-268) and page spec actions (PAP-116), `explain` preview of the effective permissions for a fixture principal, console page `/console/people/roles` edit mode (extends PAP-583), audit of every change, `docs/platform/roles.md`.

Out: Base roles and the policy language (PAP-55, PAP-227), per-resource grants (PAP-589), entitlement gating (PAP-178), SCIM group mapping (PAP-231).

**Spec**

* A custom role is `{ key, name, baseRole: TenantRole, policies: Policy[] }`; its effective permission set is base role policies plus its own allows; a custom role can never grant more than `admin` and never `*.manage`; deny policies stay platform-owned.
* Picker shows every `<entity>.<verb>` known to the registry with the current base decision; toggling adds an allow policy with `source: { specPath: 'tenant-role:<key>' }` so `explain` and PAP-64 matrices can cite it.
* Assignment through `org.members.updateRole` accepts custom role keys; a member's `Principal.attributes.role` carries the custom key and `baseRole` for `matches()` (PAP-55) so audiences keep working.
* System roles immutable (PAP-33 invariant); archiving a role in use requires choosing a replacement; changes publish `permission.changed` (PAP-591).
* Policies from custom roles compile to SQL like any other (PAP-228) because they use the same `Policy` shape; the property test covers a fixture custom role.

**Interface contract**

Provides: Procedures `roles.*`, columns `role.base_role`, `role.policies`, `RolePicker` component, `effectivePermissions(roleKey)`, docs.

Consumes: Policy model and `explain` (PAP-227), SQL compiler (PAP-228), tenancy and membership procedures (PAP-578), procedure registry (PAP-268), spec actions (PAP-116, soft), console pages (PAP-583, soft), audit (PAP-38), propagation (PAP-591, soft). Consumed by PAP-231 group mapping, PAP-64 matrices, PAP-63 roles page.

**Definition of done**

* Owner creates 'Finance viewer' extending `viewer` with `invoice.read|list`, assigns it, and the member sees invoices but cannot edit (Playwright plus `callAs`); `explain` names the tenant role as the source.
* Attempt to grant `*.manage` or exceed admin refused; system role edit refused; archive-in-use requires a replacement (tests).
* Property test agreement between `can()` and `toPredicate()` includes a custom role fixture; screenshots of the editor at 768 and 1280; docs; changelog under Identity.

**Test plan**

* Unit: effective permission composition, ceiling checks, picker grouping from the registry, archive replacement rule.
* E2E: create, assign, verify access in the portal as the member, archive with replacement; matrix report (PAP-64) shows the new column.

**Demo**

Create 'Support lead' from `staff`, tick `user.impersonate`, assign it to a seeded staff member, then run the explain CLI for that member. Under two minutes.

**Edge cases**

* Fifty custom roles: picker and lists searchable; roles page grouped by base role.
* Role referenced by a page spec `access` audience: audiences match on `baseRole` unless the spec names the custom key explicitly.
* Two tenants define the same key: keys are per tenant; system keys reserved.

**Dependencies**

Blocked by PAP-227 and PAP-578 (hard). Soft: PAP-228, PAP-268, PAP-116, PAP-38, PAP-583, PAP-591.

**Agent**

Builder: Forge (Platform Engineer) with Iris on the picker. Reviewer: Sentinel (Security Auditor; Code Reviewer).

**Size**

M: one session.

*Round 4 critique fix (2026-09-18):* resolved 4 round-4 file keys in this description to Linear identifiers: `r4/identity/console-admin-pages` = PAP-583, `r4/identity/permission-propagation` = PAP-591, `r4/identity/resource-grants` = PAP-589, `r4/identity/tenancy-core` = PAP-578.
