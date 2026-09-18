---
identifier: "PAP-583"
title: "Seven console admin pages with specs: overview, members, roles, audit, impersonations entry, agents, general and branding settings"
project: "identity"
projectName: "Identity, Roles & Audiences"
phase: "P1"
type: "Build"
priority: 2
surfaces: ["Staff"]
milestone: "Agent principals and enterprise"
state: "Backlog"
parent: "PAP-63"
children: []
blockedBy: ["PAP-582"]
blocks: ["PAP-658", "PAP-894"]
key: "r4/identity/console-admin-pages"
url: "https://linear.app/paperos/issue/PAP-583/seven-console-admin-pages-with-specs-overview-members-roles-audit"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:11.776Z"
model: "claude-sonnet-5"
effort: "high"
estimate: 3
dueDate: "2026-09-30"
cycle: null
---

# PAP-583: Seven console admin pages with specs: overview, members, roles, audit, impersonations entry, agents, general and branding settings

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / high — Build M

**Goal**

Second half of PAP-63: the admin pages identity already needs, each with a spec, mounted in the frame. They prove the customer/staff split with PAP-62 and give later modules the pattern for their own console pages.

**Scope**

In: Specs `specs/pages/console/{overview,members,roles,audit,impersonations,agents,settings-general,settings-branding}.spec.yaml` and routes: `/console` overview (members count, active agents from PAP-60, open Linear items via PAP-101 when available else stub, recent audit); `/console/people/members` (PAP-165 grid if present, else PAP-71 table; role edit, invite dialog, audience filter); `/console/people/roles` (five roles plus custom, policies rendered from PAP-227 `explain`, read-only here; editing is PAP-588); `/console/security/audit` (PAP-38 list with actor badges and impersonation markers, cursor paginated); `/console/security/impersonations` (nav entry; PAP-61 fills); `/console/agents` (agent principals, key counts, last activity); `/console/settings/general` and `/console/settings/branding` (PAP-75 when present, else stub with `data-stub`).

Out: Frame, navigation and filter (sibling), role editing (PAP-588), impersonation content (PAP-61), SSO/SCIM pages (PAP-232), developer page (PAP-222), org chart (PAP-113).

**Spec**

* Every spec declares purpose, access audiences, data (procedures and shapes), states (loading, empty, error, denied) and edge cases; codegen (PAP-120) scaffolds, pages fill in.
* Members: `org.members.list` with cursor and `AudienceFilter` segment as a `FilterTree`; role edit through `org.members.updateRole`; invite through `InviteMemberDialog`; 1,000 fixture members render with Lighthouse performance above 85 at 1280.
* Audit: `audit.list` cursor pagination against 1 million seeded rows (PGlite subset in CI, full nightly); impersonated rows carry the marker from PAP-61 audit fields.
* Agents: rows from `users where kind = 'agent'` with key counts (PAP-60) and last activity (PAP-288 `/status`, soft); links to the prompt log (PAP-135, soft).
* Settings: `SettingRow` and `DangerZone` shared with PAP-62; general holds name, slug, locale, timezone, delete organisation (PAP-432 request flow).

**Interface contract**

Provides: Seven routes and specs, `MembersTable`, `RolesList`, `AuditList`, `AgentsList` components reusable by other surfaces, stub convention `data-stub`.

Consumes: Frame and registration (sibling), tenancy procedures and dialogs (PAP-578, PAP-579), `explain` (PAP-227), audit list (PAP-38, soft), agent principals (PAP-60, soft), grid (PAP-165, soft) or table (PAP-71), branding (PAP-75, soft), Linear items (PAP-101, soft), status (PAP-288, soft), spec schema and codegen (PAP-114, PAP-120).

**Definition of done**

* Seven specs validate and conformance tests pass; screenshots of overview, members and audit at seven widths in three themes; video of tenant switch, filter members, open a member in the inspector, pop out on desktop.
* Audit pagination test at one million rows nightly; members Lighthouse above 85; axe zero serious.
* Docs `docs/product/staff-console.md` page catalogue; changelog under Staff.

**Test plan**

* Unit: members filter to `FilterTree`, role edit permission gating, agents row mapping, stub detection.
* E2E: the recorded flow at 1280; drawer navigation at 375; customer denied on every route.

**Demo**

Open `/console`, filter Members to support staff, open one member in the inspector, pop it out on desktop, then expand a policy explain on the roles page. Under two minutes.

**Edge cases**

* Only the owner exists: Members shows an invite call to action.
* Roles page with 50 custom roles: grouped by base role, searchable.
* Audit row for a purged tenant: actor shown as `Erased`; link disabled.

**Dependencies**

Blocked by PAP-582 (hard). Soft: PAP-227, PAP-38, PAP-60, PAP-165, PAP-71, PAP-75, PAP-101, PAP-288, PAP-120, PAP-432.

**Agent**

Builder: Quill (Page Spec Writer) writes specs; Iris (Component Crafter) builds. Reviewer: Sentinel (Visual Inspector; Code Reviewer).

**Size**

M: one session.

*Round 4 critique fix (2026-09-18):* resolved 4 round-4 file keys in this description to Linear identifiers: `r4/identity/console-frame` = PAP-582, `r4/identity/custom-roles` = PAP-588, `r4/identity/tenancy-core` = PAP-578, `r4/identity/tenancy-ui` = PAP-579.
