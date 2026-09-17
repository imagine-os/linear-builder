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
blocks: ["PAP-128", "PAP-21", "PAP-22", "PAP-24", "PAP-261", "PAP-262", "PAP-277", "PAP-54", "PAP-62", "PAP-63", "PAP-70"]
key: "app-shell/router-layouts"
url: "https://linear.app/paperos/issue/PAP-16/implement-file-based-router-with-layout-slots-nav-sidebar-inspector"
source: "plan/specs/bucket-0.json (round-1 canonical spec JSON)"
---

# PAP-16: Implement file-based router with layout slots (nav, sidebar, inspector, command bar) driven by page specs

**Goal**

Give every PaperOS app one file-based, fully typed router whose pages are wrapped in a layout with named slots (nav, sidebar, main, inspector, command bar, status bar) and whose slot contents are chosen by the page's `page.spec.yaml`. Agents add a page by adding a spec and a route file; the shell does the rest.

**Scope**

In:
- TanStack Router 1.x with the Vite plugin for file-based route generation in `apps/web/src/routes/`.
- `packages/core/src/shell/` layout engine: `<AppShell>` root layout, `Slot` registry, `useLayout()` hook.
- Spec-to-layout adapter reading the `layout` section of a page spec (schema owned by `spec-builder/schema`; until it lands, use the interim type in `packages/spec/src/interim.ts` and mark TODO).
- Route metadata: title, breadcrumb, required audience (string, enforced later by `identity/rbac-abac`), default slot visibility.
- Not-found, error boundary and pending (suspense) routes.
- Deep-linkable panel state via search params (`?inspector=open&sidebar=collapsed`) validated with Zod 4.

Out: real navigation content, auth guards (identity), multi-window detach (`app-shell/breakpoints-windows`), codegen of route files (`spec-builder/layout-codegen`).

**Spec**

- Routes: `__root.tsx` renders `<AppShell>`; `_app.tsx` layout route for authenticated area; `_public.tsx` for marketing/auth pages; example pages `index.tsx`, `_app/dashboard.tsx`, `_app/settings/index.tsx`.
- `AppShell` grid: CSS grid areas `nav | sidebar | main | inspector` with `commandbar` overlay and `statusbar` bottom; container-query aware (widths from `app-shell/device-matrix-research`), collapses sidebar under `md` and inspector under `lg` into drawers.
- Slot API: `registerSlot(name, Component, { priority, when })`; pages call `useLayout({ sidebar: <Filters/>, inspector: <Details/> })` or declare in spec `layout.slots.sidebar: FiltersPanel` resolved through a component registry (`design-system/component-spec-mapping`).
- Route file exports `Route = createFileRoute('/_app/dashboard')({ component, loader, validateSearch, staticData: { spec: 'dashboard' } })`; `staticData.spec` points at `specs/pages/dashboard.spec.yaml`.
- `useSpec(routeId)` loads the parsed spec (bundled at build time via a Vite plugin `vite-plugin-paperos-specs` that imports `specs/**/*.yaml` as JSON).
- Command bar slot reserved for `input/command-registry`; expose `<Slot name="commandbar" />` only.
- Preloading: `defaultPreload: 'intent'`, `defaultPreloadStaleTime: 30_000`.
- Scroll restoration on; focus moved to `main h1` on navigation (`input/focus-management` will refine).

**Definition of done**

- Three example routes render inside the shell; typed `Link` to a missing route fails typecheck.
- Vitest: slot registry, search-param validation, spec adapter mapping (fixtures for 3 specs).
- Playwright: navigate all example routes; sidebar collapses to drawer at 375 and 768; inspector drawer at 1024; full grid at 1280, 1536, 1920. Screenshots at all 7 widths attached.
- Not-found and thrown-error routes screenshot-tested.
- `docs/shell/routing.md` explains adding a route + spec in under 10 steps; CHANGELOG entry.
- Linear comment with Pages preview links to each example route.

**Edge cases**

- Spec references a component not in the registry: render a visible `<MissingComponent name/>` placeholder in dev, log error and hide in prod.
- Two pages register the same slot with equal priority: last-write wins with a dev warning.
- Search params with invalid values: fall back to defaults, never crash.
- Route file exists without a spec: allowed in dev, blocked in CI by `spec-builder/validator`.
- Window narrower than 320: shell still scrolls horizontally rather than overlapping.
- Nested layouts under `_app/settings/*` must not double-render nav.

**Dependencies**

`app-shell/monorepo-scaffold` (hard). Soft: `spec-builder/schema` (interim type until then), `design-system/layout-components` (uses plain divs until then). Unblocks `app-shell/create-cli`, `app-shell/template-docs`, `spec-builder/layout-codegen`, `identity/customer-portal-shell`, `identity/staff-console-shell`.

**Agent**

Built by Forge. Reviewed by Sentinel (Code Reviewer) and Quill for spec-adapter correctness.

**Size**

M: the router is off-the-shelf, but the slot engine and spec adapter are the contract every page relies on.
