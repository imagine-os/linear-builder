---
identifier: "PAP-120"
title: "Generate page scaffolds (layout, component tree, loading/empty/error states) from specs"
project: "spec-builder"
projectName: "Spec Builder"
phase: "P1"
type: "Build"
priority: 1
surfaces: ["Developer"]
milestone: "Codegen and conformance tests"
state: "Backlog"
parent: null
children: ["PAP-314", "PAP-315", "PAP-316"]
blockedBy: ["PAP-74", "PAP-114", "PAP-234"]
blocks: ["PAP-29", "PAP-362", "PAP-375"]
key: "spec-builder/layout-codegen"
url: "https://linear.app/paperos/issue/PAP-120/generate-page-scaffolds-layout-component-tree-loadingemptyerror-states"
source: "Linear snapshot 2026-09-17T15:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T14:57:21.851Z"
model: null
effort: null
---

# PAP-120: Generate page scaffolds (layout, component tree, loading/empty/error states) from specs

**Model / Effort:** set on children (umbrella is never claimed)

**Goal**

Turn a validated page spec into a working page skeleton: the TanStack route file, layout slot wiring, the component tree as JSX bound to real design-system components, and loading, empty, error, offline and denied states. An agent building a page starts from a rendering scaffold and only writes logic. Umbrella for three children.

**Scope**

* Children (build in order):
  * PAP-314: codegen templates and two-file ownership rules.
  * PAP-315: state wiring, slot mapping and event binding.
  * PAP-316: example specs generated, screenshotted and conformance-tested.
* Out: business logic, data hooks (PAP-119), design decisions, non-React targets, i18n of copy (PAP-375).

**Spec**

* `pnpm spec gen:page <id> [--all] [--check] [--force]` produces the route file (created once), `generated/pages/<id>.view.tsx` (always regenerated), `pages/<id>.logic.ts` (created once, typed stubs per `logic.actions`), and `<id>.stories.tsx` (one story per state).
* Components resolve through `resolveComponent()` from PAP-74; every element gets `data-spec-key`; `events` bind to `actions.<name>`; state components come from PAP-234 (`ErrorState`, `DeniedState`, `OfflineBanner`, `IntegrationUnavailable`, `LoadingPage`) and PAP-71 (`EmptyState`, `Skeleton`).
* Templates are type-checked TypeScript functions with a `Printer` for indentation and import dedupe; Biome formats output; generation is deterministic and the banner carries the spec hash for `--check`.
* Layout templates map to PAP-16 shells; unknown slots fail; search params from `data` filters produce a Zod `validateSearch`.

**Interface contract**

* Provides: `generatePage(spec, registry, options): GeneratedFiles`, the CLI, `data-spec-key` attribute convention, `data-action` attribute on event-bound elements (used by PAP-64 and PAP-122), the two-file ownership rule documented in `docs/spec/codegen.md`, `MissingComponent` dev fallback.
* Consumers: PAP-105 `page-from-spec` skill, PAP-122 (`data-spec-key`), PAP-124 preview compiles templates in-browser, PAP-125 examples, PAP-29 new-app drill, PAP-126 regenerates on terminology change.
* Requires: PAP-114 schema, PAP-74 registry and resolver (hard), PAP-234 state components, PAP-16 slot API, PAP-119 hooks (stubs otherwise), PAP-59 `useCan`.

**Definition of done**

* All three children Done.
* Umbrella: the three PAP-125 example specs generate, typecheck, render; generating a page then running PAP-122 passes with zero manual edits; screenshots of each state at 320, 375, 768, 1024, 1280, 1536 and 1920 px in light and dark; Storybook stories deployed.
* Docs including the two-file pattern; changelog; Linear comment with screenshots and story links.

**Test plan**

* Umbrella integration: generate all examples twice, assert byte-identical output; typecheck `apps/web`; run conformance suites.
* Visual: seven-width matrix per state through gate 3, both themes.
* e2e: Playwright loads each example route and asserts `data-spec-key` presence for the success state.

**Demo**

Run `pnpm spec gen:page customer-invoices`, open the route and see the table scaffold with an empty state; edit `states.empty.copy` in the spec, regenerate, reload: the copy changes and the logic file is untouched. Ninety seconds.

**Edge cases**

* Component `key` renamed: view regenerates; logic keeps the old handler with `// TODO(unused)`.
* Route file exists with another `staticData.spec`: abort with the conflict.
* Tree deeper than 12: warning.
* `kiosk` template before PAP-23 exists: falls back to `focus` with warning.
* Biome unavailable: unformatted output with warning; drift check formats before compare.

**Dependencies**

Blocked by PAP-114, PAP-74, PAP-234. Soft: PAP-119, PAP-16, PAP-59. Blocks PAP-29, PAP-375.

**Agent**

Built by Nova with Iris (Component Crafter) on component emit; reviewed by Sentinel (spec-conformance).

**Size**

L (umbrella; children M, M, S)

**Module boundary**

This umbrella is the Spec Builder half of the PaperOS Module System (`docs/module-system.md`). The `spec-builder` module implements `@paperos/contract-spec-builder` (`PageSpec`, `AppSpec`, validator port, generator plugin interface, flow graph, component refs). Codegen targets are generator plugins registered through the contract; consumers read specs through the schemas and never parse YAML themselves. The module may import `@paperos/core`, `contract-design-system`, `contract-identity`, `contract-data-layer`, `contract-app-shell` and its own package. Its manifest declares `provides: [{ contract: '@paperos/contract-spec-builder', version: '0.1.0' }]`, `owner: { agent: 'Quill', project: 'spec-builder' }` and `swapRisk: 'high'`. The contract package is published by PAP-467 (`module/spec-builder/contract`), proven by PAP-470 (`module/spec-builder/conformance`) and bound into `@paperos/kernel` by PAP-473 (`module/spec-builder/wire`); children of this issue inherit this boundary and may not add a dependency the manifest does not declare (lint rules R7 to R11).
