---
identifier: "PAP-63"
title: "Ship the staff console shell with tenant switcher, audience filters and admin navigation"
project: "identity"
projectName: "Identity, Roles & Audiences"
phase: "P1"
type: "Build"
priority: 2
surfaces: ["Staff"]
milestone: "Agent principals and enterprise"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-16", "PAP-58", "PAP-438", "PAP-447"]
blocks: []
key: "identity/staff-console-shell"
url: "https://linear.app/paperos/issue/PAP-63/ship-the-staff-console-shell-with-tenant-switcher-audience-filters-and"
source: "Linear snapshot 2026-09-17T15:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T15:11:29.700Z"
model: "claude-sonnet-5"
effort: "high"
---

# PAP-63: Ship the staff console shell with tenant switcher, audience filters and admin navigation

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / high — Build M

**Goal**

Ship the reference staff surface every app inherits: a console at `/console` with tenant and workspace switchers, an `AudienceFilter`, navigation generated from `app.spec.yaml`, and the admin pages identity already needs (overview, members, roles, audit, agents, settings). It hosts every later admin module and demonstrates the customer/staff split with PAP-62.

**Scope**

* In: `console.layout.tsx` on PAP-70 `AppFrame`, switchers, `AudienceFilter`, `fromAppSpec` navigation, seven admin pages with specs, pop-out hooks, per-slot error boundaries, tests and screenshots.
* Out: module content (CRM, finance add routes under `/console/*`), org chart (PAP-113), notifications (PAP-136), impersonation list content (PAP-61), SSO and SCIM pages (PAP-232), developer page (PAP-222).

**Spec**

* Layout slots: `nav` (sidebar 240 px, icon rail 768-1023 px, drawer under 768 px), `commandBar` (PAP-151 palette when present, else search stub), `main`, `inspector` (360 px at 1280 px and above, sheet below), `banner`. Access `audiences: [staff, admin, owner, agent]`; customers get `DeniedState` (PAP-234) with a portal link.
* Navigation: `packages/core/src/nav/fromAppSpec.ts` reads `navigation.console: [{ id, label, icon, route, audiences, badgeSource? }]`; items the actor's audiences do not match are hidden; sections Overview, Data, People, Agents, Settings.
* Switchers: `TenantSwitcher` and `WorkspaceSwitcher` from PAP-58 in the sidebar header, searchable and keyboard operable.
* `AudienceFilter` (`packages/ui`): chip filter emitting a PAP-55 `Segment` (for example staffRole = support AND tier = pro); persists per user per page in `user.attributes.filters`; reused by PAP-195.
* Pages and specs (`specs/pages/console/*.spec.yaml`): `/console` overview (members, active agents from PAP-60, open Linear items via PAP-101 when available else stub, recent audit); `/console/people/members` (PAP-165 grid if present, else PAP-71 table; role edit, invite dialog, audience filter); `/console/people/roles` (five roles plus custom, policies rendered from PAP-59 `explain`, read-only); `/console/security/audit` (PAP-38 list with actor badges and impersonation markers, cursor paginated); `/console/security/impersonations` (nav entry only; PAP-61 fills); `/console/agents` (agent principals, key counts, last activity); `/console/settings/general` and `/console/settings/branding` (PAP-75 when present).
* Multi-window: `PopOutButton` on inspector and main registering with PAP-21; hidden outside Tauri.
* Every slot has its own error boundary and skeleton.

**Interface contract**

* Provides: `console.layout.tsx` slot names; `fromAppSpec()` and the `navigation.console` app-spec shape; `AudienceFilter` (`value: Segment`, `onChange`); `registerConsoleSection(section, items)` for modules; settings page conventions (`SettingRow`); `data-testid` prefixes `console.*`.
* Requires: PAP-58 switchers, PAP-16 layouts, PAP-70 `AppFrame` (soft: plain divs until merged), PAP-55, PAP-59 explain, PAP-38 audit list, PAP-60 agent list, PAP-67, PAP-71, PAP-234, PAP-151 (soft), PAP-21 (soft), PAP-165 (soft).
* Consumers: PAP-61, PAP-75 branding route, PAP-113, PAP-189, PAP-183, PAP-222, PAP-232, PAP-221.

**Definition of done**

* Seven specs validate; conformance tests pass; navigation hides entries per audience (Vitest with support, admin and agent fixture principals).
* Screenshots of overview, members and audit at seven widths in light, dark and high-contrast; video of tenant switch, filter members, open inspector, pop out on desktop.
* Sidebar, switchers and filter keyboard operable; axe zero serious; focus order verified.
* Customer principal gets the denied state; agent principal sees Overview and Agents only (test).
* Lighthouse performance above 85 at 1280 with 1 000 fixture members; docs `docs/product/staff-console.md`; changelog under "Staff".

**Test plan**

* Unit: `fromAppSpec` filtering and section ordering; `AudienceFilter` segment output and impossible-segment detection via `matches` on fixtures.
* Integration: audit page cursor pagination against 1 million seeded rows (PGlite subset in CI, full nightly).
* E2E: the recorded flow at 1280; drawer navigation at 375.
* Visual: three pages × seven widths × three themes; RTL story for the sidebar.

**Demo**

As seeded admin open `/console`, switch to the second tenant, filter Members to "support staff", open one member in the inspector, then pop it out to a second window on desktop; open `/console/people/roles` and expand a policy's explain. Under two minutes.

**Edge cases**

* Only the owner exists: Members shows an invite call to action.
* Nav entry to an unshipped route: hidden, dev warning, conformance flag.
* Impossible segment (staff AND anonymous): "no one matches" without a server call.
* Pop-out then main window closes: pop-out closes, placement remembered.

**Dependencies**

PAP-58, PAP-16 (hard). Soft: PAP-70, PAP-59, PAP-55, PAP-38, PAP-60, PAP-151, PAP-21, PAP-165, PAP-234.

**Agent**

Iris (Component Crafter) for layout and components; Quill (Page Spec Writer) for specs; Nova's Views Engineer assists if the grid exists. Reviewed by Sentinel (Visual Inspector, Code Reviewer); Atlas confirms the module extension contract.

**Size**

M.
