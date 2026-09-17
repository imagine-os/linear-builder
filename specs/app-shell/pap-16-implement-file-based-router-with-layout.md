---
identifier: "PAP-16"
title: "Implement file-based router with layout slots (nav, sidebar, inspector, command bar) driven by page specs"
project: "app-shell"
projectName: "Universal App Shell & Repo Template"
phase: "P0"
type: "Build"
priority: 1
surfaces: ["Developer"]
milestone: "Template scaffolds and runs on web"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-13"]
blocks: ["PAP-21", "PAP-22", "PAP-24", "PAP-54", "PAP-62", "PAP-63", "PAP-70", "PAP-128", "PAP-261", "PAP-262", "PAP-277", "PAP-438", "PAP-447", "PAP-453"]
key: "app-shell/router-layouts"
url: "https://linear.app/paperos/issue/PAP-16/implement-file-based-router-with-layout-slots-nav-sidebar-inspector"
source: "Linear snapshot 2026-09-17T15:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T14:54:11.299Z"
model: "claude-sonnet-5"
effort: "high"
---

# PAP-16: Implement file-based router with layout slots (nav, sidebar, inspector, command bar) driven by page specs

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / high — Build M

**Goal**

Give every PaperOS app one file-based, fully typed router whose pages render inside a layout with named slots (nav, sidebar, main, inspector, command bar, status bar), with slot contents chosen by the page's `page.spec.yaml`. Agents add a page by adding a spec and a route file; the shell does the rest.

**Scope**

In:

* TanStack Router 1.x with the Vite plugin, routes in `apps/web/src/routes/`.
* `packages/core/src/shell/`: `<AppShell>`, slot registry, `useLayout()`.
* Spec-to-layout adapter reading the `layout` section (interim type in `packages/spec/src/interim.ts` until PAP-116).
* Route metadata: title, breadcrumb, `audience` string (enforced later by PAP-59), default slot visibility.
* Not-found, error boundary and pending routes.
* Panel state in search params (`?inspector=open&sidebar=collapsed`) validated with Zod 4.

Out: navigation content, auth guards, window detach (PAP-21), route codegen (PAP-120).

**Spec**

* `__root.tsx` renders `<AppShell>`; `_app.tsx` for authenticated pages, `_public.tsx` for marketing and auth; examples `index.tsx`, `_app/dashboard.tsx`, `_app/settings/index.tsx`.
* Grid areas `nav | sidebar | main | inspector`, `commandbar` overlay, `statusbar` bottom; sidebar collapses to a drawer under `md`, inspector under `lg` (interim media queries; PAP-21 replaces them with container queries).
* Slot API: `registerSlot(name, Component, { priority, when })`; pages call `useLayout({ sidebar: <Filters/> })` or declare `layout.slots.sidebar: FiltersPanel` resolved through the component registry (PAP-69).
* Route export: `createFileRoute('/_app/dashboard')({ component, loader, validateSearch, staticData: { spec: 'dashboard' } })`.
* `useSpec(routeId)` loads the parsed spec; `vite-plugin-paperos-specs` imports `specs/**/*.yaml` as JSON.
* `<Slot name="commandbar"/>` reserved for PAP-151.

**Interface contract**

Provides (from `@paperos/core/shell`):

* `AppShell`, `Slot`, `registerSlot`, `useLayout`, `useSpec`, `useShellSearch`; types `SlotName = 'nav'|'sidebar'|'main'|'inspector'|'commandbar'|'statusbar'`, `RouteStaticData = { spec?: string; audience?: string; title?: string }`.
* Route tree type `AppRouter` exported from `apps/web/src/routeTree.gen.ts` for typed `Link`.
* Convention: route file path mirrors `specs/pages/<name>.spec.yaml`.
* Search-param schema `ShellSearch = { inspector?: 'open'|'closed'; sidebar?: 'expanded'|'collapsed' }`.

Consumes: `LayoutSection` from `@paperos/spec` (interim until PAP-116), component registry `resolveComponent(name)` from PAP-69, `BREAKPOINTS` from PAP-14. PAP-28 later composes the route tree from module manifests through `composeRoutes(modules)`, which this issue exposes as a stub.

**Definition of done**

* Three example routes render in the shell; a typed `Link` to a missing route fails typecheck.
* Vitest: slot registry, search validation, spec adapter on three fixtures.
* Playwright at all seven widths: drawers at 375 and 768, inspector drawer at 1024, full grid at 1280+; not-found and error routes captured.
* `docs/shell/routing.md` explains adding a route plus spec in under 10 steps; CHANGELOG; Linear comment with preview links.

**Test plan**

* Unit: slot priority resolution, `when` predicates, `ShellSearch` fallbacks on invalid values, adapter mapping for three spec fixtures.
* Type: `expectTypeOf` test that `Link to="/nope"` errors.
* Integration: Testing Library renders `AppShell` with a fake route and asserts slot content.
* E2E: Playwright visits all example routes at 320, 375, 768, 1024, 1280, 1536, 1920; asserts drawer versus grid mode via `data-layout` attribute; screenshots light and dark.
* Error path: route throwing in loader renders the error boundary with a retry button.

**Demo**

Reviewer opens the Pages preview, navigates `/`, `/dashboard`, `/settings`, resizes the window from 1920 to 375 watching sidebar and inspector fold into drawers, appends `?inspector=open` to the URL and sees the inspector open. Under 2 minutes.

**Edge cases**

* Spec names a component missing from the registry: visible `<MissingComponent/>` in dev, logged and hidden in prod.
* Two registrations with equal priority: last wins with a dev warning.
* Invalid search params fall back to defaults.
* Nested layouts under `_app/settings/*` never double-render nav.
* Width under 320 scrolls horizontally rather than overlapping.

**Dependencies**

PAP-13 (hard). Soft: PAP-116 schema, PAP-70 layout components. Unblocks PAP-22, PAP-24, PAP-21, PAP-54, PAP-62, PAP-63, PAP-70, PAP-128.

**Agent**

Built by Forge. Reviewed by Sentinel (Code Reviewer) and Quill (spec adapter naming).

**Size**

M: one library, one adapter, three example routes.

**Module boundary**

This issue is the Universal App Shell & Repo Template half of the PaperOS Module System (`docs/module-system.md`). The `app-shell` module implements `@paperos/contract-app-shell` (slots, route contribution, layout, window manager, config and secrets, flags, i18n, native capabilities). It may import `@paperos/core`, any `@paperos/contract-*` and its own packages; it must never import another module's implementation package, and modules reach the shell only through slot fills and route contributions declared in their manifests. Its manifest declares `provides: [{ contract: '@paperos/contract-app-shell', version: '0.1.0' }]`, `owner: { agent: 'Forge', project: 'app-shell' }` and `swapRisk: 'critical'`. The contract package is published by PAP-447 (`module/app-shell/contract`), proven by PAP-450 (`module/app-shell/conformance`) and bound into `@paperos/kernel` by PAP-453 (`module/app-shell/wire`); children of this issue inherit this boundary and may not add a dependency the manifest does not declare (lint rules R7 to R11).
