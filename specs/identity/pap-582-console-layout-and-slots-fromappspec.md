---
identifier: "PAP-582"
title: "Console layout and slots, `fromAppSpec` navigation, tenant and workspace switchers in the sidebar, `AudienceFilter` and `registerConsoleSection` for modules"
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
blockedBy: ["PAP-16", "PAP-58", "PAP-438", "PAP-447", "PAP-578", "PAP-579", "PAP-661"]
blocks: ["PAP-583", "PAP-596"]
key: "r4/identity/console-frame"
url: "https://linear.app/paperos/issue/PAP-582/console-layout-and-slots-fromappspec-navigation-tenant-and-workspace"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:11.617Z"
model: "claude-sonnet-5"
effort: "high"
estimate: 3
dueDate: "2026-09-30"
cycle: null
---

# PAP-582: Console layout and slots, `fromAppSpec` navigation, tenant and workspace switchers in the sidebar, `AudienceFilter` and `registerConsoleSection` for modules

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / high — Build M

**Goal**

First half of PAP-63: the frame every admin module mounts into. `console.layout.tsx` on the shell slots, navigation generated from `app.spec.yaml` and filtered by audience, the switchers from PAP-58 in the sidebar header, the reusable `AudienceFilter` and the registration API modules use to add sections, without any of the seven pages yet.

**Scope**

In: `apps/web/src/console/console.layout.tsx` with slots `nav` (sidebar 240 px, icon rail 768 to 1023 px, drawer under 768 px), `commandBar`, `main`, `inspector` (360 px at 1280 px and above, sheet below), `banner`; `packages/core/src/nav/fromAppSpec.ts` reading `navigation.console`; `registerConsoleSection(section, items)`; `AudienceFilter` in `packages/ui` emitting a PAP-55 `Segment` and persisting per user per page; access `audiences: [staff, admin, owner, agent]` with `DeniedState` for customers; per-slot error boundaries and skeletons; `PopOutButton` hooks (PAP-21, hidden outside Tauri); `data-testid` prefixes `console.*`; spec `specs/pages/console/layout.spec.yaml`.

Out: The seven admin pages (sibling PAP-583), module content, notifications bell (PAP-136), command palette (PAP-151 fills the slot).

**Spec**

* `navigation.console: [{ id, label, icon, route, audiences, badgeSource? }]` in `app.spec.yaml`; items the actor's audiences do not match are hidden; sections Overview, Data, People, Agents, Settings; modules append through `registerConsoleSection` and their manifest `slots.fills` (`shell.nav`, PAP-433).
* Switchers from PAP-579 in the sidebar header, searchable and keyboard operable; workspace switcher hidden when the tenant has one workspace.
* `AudienceFilter` chips compose `staffRole`, `tier`, `principalType` and declared audiences into a `Segment`; impossible segments (staff AND anonymous) detected with `matches` on fixtures and shown as 'no one matches' without a server call; value stored in `user.attributes.filters[pageId]`.
* Error boundary per slot renders `ErrorState` (PAP-234) with the request id; skeleton per slot for loading.
* Layout renders on PAP-70 `AppFrame` when present, plain regions otherwise; theming from PAP-75 when present.

**Interface contract**

Provides: `console.layout.tsx` slot names, `fromAppSpec()` and the `navigation.console` shape, `registerConsoleSection`, `AudienceFilter` (`value: Segment`, `onChange`), `SettingRow` convention, test-id prefixes.

Consumes: Routes and layouts (PAP-16), switchers and `useTenant` (PAP-579), audiences (PAP-55), `AppFrame` (PAP-70, soft), states (PAP-234), primitives (PAP-67), window manager (PAP-21, soft), palette (PAP-151, soft). Consumed by the sibling pages, PAP-61, PAP-75, PAP-113, PAP-189, PAP-183, PAP-222, PAP-232, PAP-221, PAP-588, PAP-596.

**Definition of done**

* Navigation hides entries per audience (Vitest with support, admin and agent fixture principals); customer principal gets the denied state; agent sees Overview and Agents only.
* Screenshots of the empty frame with switchers and filter at seven widths in light, dark and high contrast; drawer at 375; keyboard order verified; axe zero serious.
* Spec validates; `registerConsoleSection` used by one fixture module; docs `docs/product/staff-console.md` section 'Frame'; changelog under Staff.

**Test plan**

* Unit: `fromAppSpec` filtering and ordering, `AudienceFilter` segment output and impossible-segment detection, section registration ordering.
* E2E: Playwright at 1280 and 375: open console as admin, switch tenant, open the drawer, filter chips persist across reload.

**Demo**

As seeded admin open `/console`, switch to the second tenant, add a 'support staff' chip and reload to see it persist; resize to 375 for the drawer. Under two minutes.

**Edge cases**

* Nav entry to an unshipped route: hidden, dev warning, conformance flag.
* Only one tenant and one workspace: switchers collapse to labels.
* Pop-out then main window closes: pop-out closes, placement remembered (PAP-262).

**Dependencies**

Blocked by PAP-16 and PAP-579 (hard). Soft: PAP-70, PAP-55, PAP-234, PAP-67, PAP-21, PAP-151, PAP-75. Blocks the sibling PAP-583.

**Agent**

Builder: Iris (Component Crafter). Reviewer: Sentinel (Visual Inspector; Code Reviewer).

**Size**

M: one session.

*Round 4 critique fix (2026-09-18):* resolved 4 round-4 file keys in this description to Linear identifiers: `r4/identity/access-checker` = PAP-596, `r4/identity/console-admin-pages` = PAP-583, `r4/identity/custom-roles` = PAP-588, `r4/identity/tenancy-ui` = PAP-579.
