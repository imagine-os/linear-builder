---
identifier: "PAP-264"
title: "Module manifest contract and registry (packages/core/modules)"
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
blockedBy: ["PAP-117"]
blocks: ["PAP-265"]
key: "child/PAP-28/9"
url: "https://linear.app/paperos/issue/PAP-264/module-manifest-contract-and-registry-packagescoremodules"
source: "Linear snapshot 2026-09-17T06:03Z (round-2 issue)"
---

# PAP-264: Module manifest contract and registry (packages/core/modules)

**Goal**

Define `ModuleManifest`, `defineModule()` and the registry that loads manifests listed in `app.spec.yaml`, resolves dependencies and refuses unknown or incomplete sets, plus the lint rule banning direct imports across optional module boundaries and a `knip` baseline.

**Scope**

In: Zod schema, registry, dependency resolver, route-collision detection, boundary lint rule, `knip` config; convert `shell`, `identity`, `data`, `design-system`, `spec`, `input`, `i18n` into core manifests and one optional example module.

Out: router and database integration (child 2), CLI and tenant toggles (child 3).

**Spec**

* Manifest fields per the parent; `dependsOn` resolved topologically; cycles and missing deps fail at boot with module ids.
* `loadModules(appSpec): ResolvedModules` pure and synchronous for use in Vite config and the server.
* Lint rule reports import paths crossing from one optional module package to another unless listed in `dependsOn`.

**Interface contract**

Provides: `ModuleManifest`, `defineModule`, `loadModules`, `ResolvedModules`, lint rule `@paperos/no-cross-module-import`. Consumes: `app.spec.yaml` shape agreed with PAP-117; event bus `emit` (data-layer events issue) as the sanctioned coupling.

**Definition of done**

* Core manifests plus one optional example load; unit tests for resolver and collisions; lint rule fixtures; `knip` clean on the template.
* `docs/platform/modules.md` contract section written.

**Test plan**

* Unit: schema rejects unknown fields; resolver on chains, diamonds, cycles, missing; route collision names both modules.
* Static: lint rule passing and failing fixtures; `knip` in Gate 1.
* Type: `defineModule` infers `settingsSchema` type.

**Demo**

Reviewer runs `pnpm modules:list` to print the resolved module graph, edits `app.spec.yaml` to disable `identity` and watches `pnpm dev` fail with "core module cannot be disabled". Under a minute.

**Edge cases**

* Two manifests with the same id from different packages: boot error.
* Optional module with no routes or entities: allowed.

**Dependencies**

PAP-117 (shape), PAP-13. Blocks children 2 and 3.

**Agent**

Built by Forge (Platform Engineer). Reviewed by Sentinel.

**Size**

M
