---
identifier: "PAP-28"
title: "Make every platform capability a removable module: module manifests, `modules:` in app.spec.yaml, `paperos create --without`, per-tenant module toggles and dead-code checks"
project: "app-shell"
projectName: "Universal App Shell & Repo Template"
phase: "P1"
type: "Build"
priority: 2
surfaces: ["Developer", "Staff"]
milestone: "Multi-monitor and PWA polish"
state: "Backlog"
parent: null
children: ["PAP-265", "PAP-266", "PAP-264"]
blockedBy: ["PAP-117", "PAP-22"]
blocks: ["PAP-126", "PAP-29"]
key: "app-shell/feature-modules"
url: "https://linear.app/paperos/issue/PAP-28/make-every-platform-capability-a-removable-module-module-manifests"
source: "plan/specs/gaps.json (round-1 canonical spec JSON)"
---

# PAP-28: Make every platform capability a removable module: module manifests, `modules:` in app.spec.yaml, `paperos create --without`, per-tenant module toggles and dead-code checks

**Goal**

The brief's premise is "build everything into the template, then remove what an app does not need". Nothing in the plan makes removal cheap: packages are wired by imports, routes are files, navigation is hand-written. This issue defines a module contract so that every capability project (tables, collab, realtime, business-core, growth, migration, agents UI) registers itself as a module, an app declares which modules it uses in `app.spec.yaml`, `paperos create` can omit modules at generation time, and tenants can toggle optional modules at runtime.

**Scope**

In:
- Module manifest `module.ts` exported by each capability package: `{ id, title, version, routes, navItems, entities, permissions, jobs, settingsSchema, integrations, dependsOn: moduleIds, optional: boolean }` validated by Zod; `packages/core/modules` registry that loads manifests listed in `app.spec.yaml` `modules:` and refuses unknown or dependency-incomplete sets.
- `app.spec.yaml` `modules:` section (coordinated with `spec-builder/app-level-spec`): `enabled`, `defaultForNewTenants`, `tenantToggleable`; the spec validator fails a page spec that references a component or entity from a disabled module.
- Router integration: `app-shell/router-layouts` composes the route tree from enabled modules' `routes`; navigation from `navItems`; `identity/rbac-abac` loads `permissions`; `data-layer/jobs-queue` registers `jobs`; `data-layer/drizzle-schema` migration sets are per module and applied only for enabled modules (a module's tables live in its own Postgres schema).
- `paperos create <app> --without payroll,crm` and `--only tables,collab`: removes packages from the workspace, strips manifests, updates `app.spec.yaml`, runs `pnpm i`, and verifies the build; `--dry-run` lists what would go.
- Runtime toggles: tenant setting `modules.enabled[]` (staff settings page, spec under `specs/pages/admin/modules.page.spec.yaml`), enforced in router, nav, permissions and API (`data-layer/api-layer` middleware rejects procedures of disabled modules with 404, not 403); aligns with `business-core/entitlements`, which can drive the toggle from a plan.
- Dead-code gate: `knip` in CI reports unused exports and packages; `pnpm modules:check` asserts that removing a module leaves no dangling imports (each module is removed in a matrix job against the template).
- Docs `docs/platform/modules.md`: how to write a module, dependency rules, what "optional" must guarantee (no other module imports it directly; cross-module calls go through `packages/core/events`).

Out: a marketplace or third-party plugin loading at runtime, micro-frontends, per-user feature flags (`app-shell/env-config` runtime flags cover experiments).

**Spec**

- Core (non-removable) modules: `shell`, `identity`, `data`, `design-system`, `spec`, `input`, `i18n`; every other project is optional and must declare `optional: true`.
- Cross-module coupling only via events (`packages/core/events`: `emit('invoice.paid', payload)`) or explicit `dependsOn`; a lint rule bans direct imports across optional module boundaries.
- Manifest `entities` reference Drizzle tables; `pnpm db:migrate` applies `drizzle/<module>/*.sql` for enabled modules only and records the module in `_migrations_modules`.
- A disabled optional module's data is retained; re-enabling is instant; deletion is a separate explicit `pnpm modules:purge <id>` with a Needs Justin gate for production tenants (destructive class per `libraries/mcp-servers`).
- `paperos create` templates the module list into the Linear project it creates (`pm-linear/configure-workspace` labels), so agents know which modules exist in that app.

**Definition of done**

- Template with all modules builds; `paperos create demo --without payroll,crm,growth` produces a repo that builds, passes `pnpm check` and shows no CRM or payroll navigation (screenshots).
- CI matrix removes each optional module in turn from the template and the build stays green (workflow link).
- Tenant admin disables `canvas` at runtime: route returns 404, nav item disappears, API procedure rejected, data retained; re-enable restores (Playwright test).
- Spec validator rejects a page referencing a disabled module's component with a readable error (test).
- `knip` report clean on the template.
- `docs/platform/modules.md`, ADR, `CHANGELOG.md`, Linear comment.

**Edge cases**

- Module A optional, module B depends on A, tenant disables A: the settings page blocks with the dependency list; the API enforces the same rule.
- A migration from a disabled module was already applied on a tenant database: retained; `pnpm db:check` treats module-scoped migrations of disabled modules as ignorable.
- Removing a module at create time that the design system's Storybook stories import: stories live inside the module package, so they leave with it; `design-system/storybook` globs only enabled packages.
- Two modules registering the same route path: registry fails at boot with both module IDs.
- Business templates (`migration/business-templates`) that require a module: the seed pack declares `requiresModules` and the importer refuses or prompts to enable.
- Mobile Tauri bundle size: disabled modules must be tree-shaken from the web bundle; `quality/perf-budgets` asserts the `--without` build is smaller.

**Dependencies**

`app-shell/create-cli` (the CLI this extends), `spec-builder/app-level-spec` (`modules:` section). Soft: `app-shell/router-layouts`, `identity/rbac-abac`, `data-layer/jobs-queue`, `business-core/entitlements`, `data-layer/drizzle-schema`. Consumed by `spec-builder/business-profile`, `migration/business-templates`, `app-shell/new-app-drill`.

**Agent**

Built by Forge (Platform Engineer) with Quill (Page Spec Writer) for the spec section and Atlas confirming the module boundaries against the project list. Reviewed by Sentinel (Code Reviewer) and Nova (owner of the largest optional modules).

**Size**

L: it touches routing, permissions, migrations, the CLI and CI, and it forces every capability package to adopt a manifest; budget two sessions plus one per adopting project.
