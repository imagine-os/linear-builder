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
children: ["PAP-264", "PAP-265", "PAP-266"]
blockedBy: ["PAP-22", "PAP-117", "PAP-303", "PAP-305"]
blocks: ["PAP-29", "PAP-126"]
key: "app-shell/feature-modules"
url: "https://linear.app/paperos/issue/PAP-28/make-every-platform-capability-a-removable-module-module-manifests"
source: "Linear snapshot 2026-09-17T13:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T13:05:01.144Z"
---

# PAP-28: Make every platform capability a removable module: module manifests, `modules:` in app.spec.yaml, `paperos create --without`, per-tenant module toggles and dead-code checks

**Goal**

Umbrella: make every platform capability a removable module so the brief's "build everything in, remove what an app does not need" is cheap. Capability projects export a manifest, `app.spec.yaml` lists modules, `paperos create --without` omits them, tenants toggle optional ones at runtime, and dead-code checks keep the template honest. Three children; closes on the CI removal matrix.

**Scope**

Children:

1. **PAP-264** — Module manifest and registry (`module.ts` contract, Zod schema, `packages/core/modules` loader, dependency resolution, `knip` baseline).
2. **PAP-265** — Router, spec, permissions, jobs and migrations integration (route tree composition in PAP-16, `modules:` validator rule with PAP-117, per-module migration sets in PAP-32, `permissions` into PAP-59, `jobs` into PAP-43).
3. **PAP-266** — `paperos create --without`, tenant module toggles and the CI removal matrix (settings page, runtime 404 and API rejection, retained data, purge command behind Needs Justin).

Out: business template seed packs (PAP-207), entitlement pricing (PAP-178).

**Spec**

* Core modules `shell`, `identity`, `data`, `design-system`, `spec`, `input`, `i18n` are non-removable; everything else declares `optional: true`.
* Cross-module coupling only via `emit()` from `packages/core/events` (data-layer event bus issue) or explicit `dependsOn`; lint bans direct imports across optional boundaries.
* `drizzle/<module>/*.sql` applied for enabled modules only; `_migrations_modules` records them.
* Disabled module data is retained; `pnpm modules:purge <id>` is a separate destructive command.
* `paperos create` writes the module list into the Linear project description.

**Interface contract**

Provides (from `@paperos/core/modules`):

* `ModuleManifest = { id, title, version, routes, navItems, entities, permissions, jobs, settingsSchema, integrations, dependsOn: string[], optional: boolean }` and `defineModule()`.
* `loadModules(appSpec)` returning `ResolvedModules`; `composeRoutes(modules)` (PAP-16 stub filled here); `useModuleEnabled(id)`.
* Table `tenant_module` (`tenant_id`, `module_id`, `enabled`, `updated_by`) and oRPC `modules.list|toggle`.
* `app.spec.yaml` `modules:` shape agreed with PAP-117: `{ enabled: string[], defaultForNewTenants: string[], tenantToggleable: string[] }`.

Consumes: event bus `emit` (data-layer events issue), `can()` (PAP-59), `defineJob` (PAP-43), migration runner (PAP-32), CLI (PAP-22), validator (PAP-117, PAP-118).

* Contract source: [Interface & Data Contracts](<https://linear.app/paperos/document/paperos-interface-and-data-contracts-d40e6a4d227c>) §3 (module `emit` publishes the outbox envelope `{ id: uuidv7, topic, version, occurredAt, tenantId, actor: ActorRef, subject: EntityRef, requestId?, causationId?, correlationId?, idempotencyKey?, payload }`; topics are `<entity>.<past-tense-verb>` registered with `defineTopic`, publishing an unregistered topic fails at boot); §5 (optional modules import only `@paperos/core`, `@paperos/db`, `@paperos/ui`, `@paperos/spec`, `@paperos/views` and events; a lint rule bans other cross-module imports); §6 rows "Module manifest" and "Domain event envelope" (provider: pending contracts issue B `contracts/domain-events`; until it exists, implement `emit` against the §3 envelope verbatim in `packages/core/events`).

**Definition of done**

* All three children Done.
* Integration test: `paperos create demo --without payroll,crm,growth` builds, passes `pnpm check` and shows no CRM or payroll navigation; CI matrix removing each optional module stays green; tenant admin disables `canvas` at runtime and the route 404s, nav item vanishes, API rejects, data survives re-enable.
* `knip` clean; `docs/platform/modules.md`, ADR, CHANGELOG, Linear comment.

**Test plan**

* Unit: manifest Zod validation, dependency resolution (missing, cyclic, disabled parent), route collision detection.
* Static: boundary lint rule with passing and failing fixtures; `knip` in Gate 1.
* Integration: migration runner applies only enabled modules on a fresh database; `_migrations_modules` asserted.
* E2E: Playwright toggles `canvas` off and on as tenant admin; customer principal cannot see the settings page.
* CI matrix: one job per optional module with `--without <id>`.

**Demo**

Reviewer opens Settings, Modules as tenant admin, switches off Canvas, sees the nav item disappear and `/canvas` return the not-found page, switches it back on and the data is intact. Under 90 seconds.

**Edge cases**

* B depends on A, tenant disables A: settings blocks with the dependency list; API enforces the same.
* Already-applied migration of a disabled module: retained and ignorable in `db:check`.
* Storybook globs only enabled packages.
* Two modules claim one route: boot fails naming both.
* Seed pack requiring a module: importer refuses or prompts to enable.

**Dependencies**

PAP-22, PAP-117 (hard), data-layer event bus issue (coupling rule). Soft: PAP-16, PAP-32, PAP-43, PAP-59, PAP-178. Consumed by PAP-29, PAP-126, PAP-207.

**Agent**

Built by Forge (Platform Engineer) with Quill on the spec section. Reviewed by Sentinel.

**Size**

L as an umbrella; children are M, M, M.
