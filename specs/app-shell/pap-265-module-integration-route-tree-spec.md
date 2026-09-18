---
identifier: "PAP-265"
title: "Module integration: route tree, spec validator, permissions, jobs and per-module migrations"
project: "app-shell"
projectName: "Universal App Shell & Repo Template"
phase: "P1"
type: "Build"
priority: 2
surfaces: ["Developer"]
milestone: "Multi-monitor and PWA polish"
state: "Backlog"
parent: "PAP-28"
children: []
blockedBy: ["PAP-264", "PAP-433", "PAP-434", "PAP-438", "PAP-447", "PAP-537"]
blocks: ["PAP-266"]
key: "child/PAP-28/10"
url: "https://linear.app/paperos/issue/PAP-265/module-integration-route-tree-spec-validator-permissions-jobs-and-per"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T13:56:13.002Z"
model: "claude-sonnet-5"
effort: "high"
estimate: 3
dueDate: "2026-09-29"
cycle: null
---

# PAP-265: Module integration: route tree, spec validator, permissions, jobs and per-module migrations

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / high — Build M

**Goal**

Make enabled modules the source of routes, navigation, permissions, jobs and migration sets: PAP-16 composes the route tree from manifests, the spec validator rejects references to disabled modules, PAP-59 loads `permissions`, PAP-43 registers `jobs`, and `db:migrate` applies `drizzle/<module>/*.sql` for enabled modules only.

**Scope**

In: `composeRoutes(modules)` implementation; nav from `navItems`; validator rule in PAP-118; permission and job registration hooks; migration runner changes and `_migrations_modules` table; `pnpm db:check` module awareness.

Out: runtime toggles and CLI (child 3).

**Spec**

* Route tree generated at build time by the Vite plugin from enabled modules; disabled module routes do not exist in the bundle.
* Validator error `MODULE_DISABLED` with module id and component or entity name.
* Migration runner records `(module_id, migration)`; disabled-module migrations already applied are ignorable in `db:check`.

**Interface contract**

Provides: `composeRoutes`, validator rule, `_migrations_modules` table, `registerModulePermissions`, `registerModuleJobs`. Consumes: registry (child 1), PAP-16, PAP-118, PAP-59, PAP-43, PAP-32.

**Definition of done**

* Template builds with route tree from manifests; a disabled optional module leaves no route in the bundle (assert by `grep` on `dist`).
* Validator test for `MODULE_DISABLED`; migration runner test on a fresh database; permissions and jobs registered (tests).

**Test plan**

* Unit: `composeRoutes` on fixtures; validator fixture with a disabled module reference.
* Integration (CI compose): migrate with module A enabled, then disabled; `_migrations_modules` rows and `db:check` behaviour asserted.
* Build: bundle grep for a disabled module's route path returns nothing.

**Demo**

Reviewer disables the example module in `app.spec.yaml`, runs `pnpm build` and `pnpm spec:validate` on a page using its component, reads the `MODULE_DISABLED` error, then runs `pnpm db:migrate` and sees the module's migrations skipped. Under 2 minutes.

**Edge cases**

* Migration of a disabled module previously applied: retained.
* Module adds a permission string already defined by core: boot error.

**Dependencies**

Child 1 (hard), PAP-16, PAP-32, PAP-118, PAP-59, PAP-43 (soft). Blocks child 3.

**Agent**

Built by Forge with Quill on validator wording. Reviewed by Sentinel.

**Size**

M
