---
identifier: "PAP-74"
title: "Map every component to a spec-builder component ID with props schema so page specs reference real components"
project: "design-system"
projectName: "Design System"
phase: "P1"
type: "Spec"
priority: 1
surfaces: ["Agent", "Developer"]
milestone: "Component library covers app shell needs"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-67", "PAP-114", "PAP-238"]
blocks: ["PAP-120", "PAP-314"]
key: "design-system/component-spec-mapping"
url: "https://linear.app/paperos/issue/PAP-74/map-every-component-to-a-spec-builder-component-id-with-props-schema"
source: "Linear snapshot 2026-09-17T13:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T06:22:47.788Z"
---

# PAP-74: Map every component to a spec-builder component ID with props schema so page specs reference real components

**Goal**

Give every design-system component a stable spec ID and a machine-readable props schema so `page.spec.yaml` files reference real components, the validator rejects unknown components or bad props, and codegen emits correct JSX. This is the bridge between the design system and the spec builder.

**Scope**

* In: `defineComponentMeta` convention finalised, `pnpm --filter ui registry:build` producing `registry.json` and `packages/spec/src/generated/components.ts`, `resolveComponent(specId)`, validator rules for PAP-115, auto-generated `docs/spec/components.md`, coverage of primitives, layout, data display, states, pickers, Icon and Illustration.
* Out: the spec schema itself (PAP-114), codegen (PAP-120), non-UI packages.

**Spec**

* `meta.ts` exports `defineComponentMeta({ specId, displayName, category, props: z.object(...), slots, events, a11y, examples, since, deprecated? })`; ID grammar `^(ui|app|print)\.[a-z][A-Za-z0-9]*$` (`app.` for app-local components registered through the same API, `print.` for PAP-235).
* `props` is Zod 4 and JSON-serialisable only; event handlers live in `events: ['onClick', 'onChange']` and are bound by codegen to spec `logic` actions; unions emit JSON Schema enums; defaults included.
* `slots: { [name]: { multiple: boolean, accepts?: specId[] } }` so `ui.appFrame.sidebar` can restrict content; circular acceptance depth-limited to 10.
* `examples: [{ title, yaml }]` validated at build time.
* `registry.json`: `{ version, generatedAt, components: { [specId]: { displayName, category, schema, slots, events, a11y, deprecated?, since } } }`, committed and drift-checked in Gate 1.
* Resolver: `import.meta.glob('../../ui/src/**/meta.ts')` in dev, generated static map in prod to preserve tree-shaking.
* Interim YAML usage until PAP-114 fixes key names: `components: - id: ui.button  props: { variant: primary, size: md }  slot: main  events: { onClick: actions.save }`.

**Interface contract**

* Provides: `registry.json`, `components.ts` (`SpecComponentId` union and `SpecComponentProps<Id>`), `resolveComponent()`, `validateComponentUsage(spec) => ValidationError[]` (error kinds `unknown-component`, `unknown-prop`, `wrong-type`, `missing-required`, `deprecated`), `defineComponentMeta`, `docs/spec/components.md`.
* Requires: PAP-67 children and every component issue supplying `meta.ts` (PAP-70, PAP-71, PAP-72, PAP-233, PAP-234, PAP-68); PAP-114 final key names (soft, interim shape).
* Consumers: PAP-115 validator, PAP-120 codegen, PAP-124 editor autocompletion, PAP-16 slot registry, PAP-85 planner (component types), PAP-76 related-component lists, PAP-244 spec-conformance reviewer.

**Definition of done**

* Every exported component has `meta.ts`; a Vitest test fails when one is missing or its ID is invalid.
* `registry.json` and `components.ts` generated, committed, drift-checked in Gate 1.
* Validator rules delivered as a PAP-115 plugin (or standalone `validateComponentUsage`) with tests for the five error kinds.
* Three example specs in `specs/pages/examples/` validate and resolve to real components; rendered screenshots at 375 and 1280.
* `docs/spec/components.md` generated; changelog entry; Linear comment with doc and registry links.

**Test plan**

* Unit: ID regex, duplicate ID build failure naming both files, JSON Schema emission for unions and defaults, slot acceptance and depth limit, deprecation warning with `replaceWith`.
* Integration: the three example specs through `validateComponentUsage`; resolver returns lazy components in dev and static in prod build.
* Contract: PAP-120 fixture renders `ui.button` from YAML; PAP-124 autocompletion reads enums.
* Meta: registry build determinism.

**Demo**

Edit `specs/pages/examples/customer-list.page.spec.yaml` to use `ui.buton` and `size: huge`, run `pnpm spec validate` and read the two errors with suggestions; fix and open the generated `docs/spec/components.md` entry for `ui.button`. Under one minute.

**Edge cases**

* `render`/`asChild` polymorphism not spec-exposed; codegen uses named alternatives (`href` produces a link).
* Renamed component: old ID deprecated one minor version with `replaceWith`.
* App-local component collides with a `ui.` ID: build fails.

**Dependencies**

PAP-67 children (hard), PAP-114 (hard for final names; start interim). Soft: PAP-70, PAP-71, PAP-72, PAP-68, PAP-233, PAP-234.

**Agent**

Iris (Component Crafter) with Quill (Page Spec Writer) owning the YAML shape. Reviewed by Sentinel (Code Reviewer) and Atlas for the contract.

**Size**

M.
