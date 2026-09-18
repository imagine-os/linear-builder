---
identifier: "PAP-661"
title: "Navigation components: NavList with nesting and router-aware active state, Breadcrumb, Pagination, Link, Stepper and Kbd"
project: "design-system"
projectName: "Design System"
phase: "P1"
type: "Build"
priority: 2
surfaces: ["Developer"]
milestone: "Component library covers app shell needs"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-68", "PAP-70", "PAP-238"]
blocks: ["PAP-62", "PAP-63", "PAP-120", "PAP-582", "PAP-584"]
key: "r4/design-system/navigation-components"
url: "https://linear.app/paperos/issue/PAP-661/navigation-components-navlist-with-nesting-and-router-aware-active"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:20:31.726Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 3
dueDate: "2026-09-25"
cycle: null
---

# PAP-661: Navigation components: NavList with nesting and router-aware active state, Breadcrumb, Pagination, Link, Stepper and Kbd

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Build M

**Goal**

Polaris, Atlassian, Carbon and Primer all ship navigation primitives; PaperOS's twenty core components and layout frames leave the sidebar list, breadcrumbs and pagination for each shell to invent. Build them once so the console (PAP-63), portal (PAP-62) and codegen (PAP-120) render navigation from `app.spec.yaml` identically.

**Scope**

In: `packages/ui/src/navigation/{NavList,NavItem,NavGroup,Breadcrumb,Pagination,Link,Stepper,Kbd}.tsx` with `meta.ts` spec ids and stories; router adapter `useActiveMatch` for TanStack Router (PAP-16) without importing the router in `packages/ui` (adapter injected by the shell).

Out: `AppFrame` and drawers (PAP-70), command palette (PAP-290), tabs (PAP-238), tenant switcher (PAP-63 owns its data).

**Spec**

* `NavList` vertical list with `NavGroup` (collapsible, remembers state in `localStorage` under `pos.nav.<appId>`, try/catch), `NavItem { href, icon: IconName, label, badge?, exact? }`, nested items to depth 3 with indentation, `aria-current="page"` from `useActiveMatch`, roving tabindex (PAP-152 hook when present, native Tab otherwise), collapsed rail mode showing icons with tooltips at `sidebar` container widths under 80 px.
* `Breadcrumb` from `{ label, href? }[]` with overflow into a Menu when more than four crumbs or when the container is narrow, `aria-label="Breadcrumb"`, current item not a link; `Pagination` cursor mode (`hasPrev`, `hasNext`, page size select) and page mode (numbers with ellipsis), `aria-label` per control, keyboard operable.
* `Link` wraps the router link adapter with external detection (`rel="noopener"`, external icon), `variant: 'inline'|'standalone'`, visited styling off by default; `Stepper` horizontal and vertical with states `complete|current|upcoming|error`, clickable when `linear: false`, `aria-current="step"`.
* `Kbd` renders chords from PAP-150 `formatChord(platform)` (`⌘K` on macOS, `Ctrl+K` elsewhere) with `<kbd>` semantics; used by `ShortcutHint` (PAP-290) and the help sheet.
* All components use logical properties (RTL), tokens only, sizes `sm|md`, and register `meta.ts` with `slots` so codegen can place `NavList` into `AppFrame.nav`.

**Interface contract**

Provides: components with spec ids `ui.navList`, `ui.navItem`, `ui.navGroup`, `ui.breadcrumb`, `ui.pagination`, `ui.link`, `ui.stepper`, `ui.kbd`; `NavAdapterProvider` (router adapter injection); `useActiveMatch`. Consumes: Menu, Tooltip, Select (PAP-237, PAP-238), `AppFrame` container names (PAP-70), `Icon` (PAP-68), `formatChord` (PAP-150, soft), roving tabindex (PAP-152, soft), router slot contract (PAP-16, adapter only). Consumed by PAP-63 console, PAP-62 portal, PAP-120 codegen navigation, PAP-290 `ShortcutHint`, PAP-367 onboarding wizard (Stepper).

**Definition of done**

* Eight components merged with stories including collapsed rail, nested groups, overflow breadcrumb and RTL; `play` tests for NavGroup collapse, Pagination keyboard and Stepper navigation; `vitest-axe` clean.
* Screenshots at 320, 375, 768, 1024, 1280, 1536, 1920 light and dark; `docs/design/navigation.md`; changelog; Linear comment on PAP-63 and PAP-62.

**Test plan**

* Unit: active match with `exact` and nested routes; breadcrumb overflow decision by count and width; pagination ellipsis maths; chord formatting per platform; group state persistence with a throwing `localStorage`.
* Interaction: collapse and expand a group by keyboard; rail mode tooltips; pagination page-size change announces.
* E2E: none (Storybook; shells cover routing).

**Demo**

Reviewer opens Storybook `Navigation/NavList playground`, collapses the sidebar container to rail width, expands a nested group by keyboard, then opens `Breadcrumb` with eight crumbs at 375 and sees the overflow menu. Under one minute.

**Edge cases**

* Two items match the current route: deepest wins.
* Badge count over 99: `99+`.
* Stepper with 12 steps at 320 px: vertical fallback.
* External link inside Tauri: opens in the system browser via the shell adapter (PAP-19).

**Dependencies**

PAP-238 (hard), PAP-70 (hard, container names), PAP-68 (hard, icons). Soft: PAP-150, PAP-152, PAP-16. Blocks PAP-63, PAP-62 navigation and PAP-120's navigation emission.

**Agent**

Builder: Iris (Component Crafter). Reviewer: Sentinel (Visual Inspector).

**Size**

M: one session.
