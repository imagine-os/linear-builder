---
identifier: "PAP-74"
title: "Map every component to a spec-builder component ID with props schema so page specs reference real components"
project: "design-system"
projectName: "Design System"
phase: "P1"
type: "Spec"
priority: 1
surfaces: ["Developer", "Agent"]
milestone: "Component library covers app shell needs"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-114", "PAP-238", "PAP-67"]
blocks: ["PAP-120"]
key: "design-system/component-spec-mapping"
url: "https://linear.app/paperos/issue/PAP-74/map-every-component-to-a-spec-builder-component-id-with-props-schema"
source: "plan/specs/bucket-2.json (round-1 canonical spec JSON)"
---

# PAP-74: Map every component to a spec-builder component ID with props schema so page specs reference real components

**Goal**

Give every design-system component a stable spec ID and a machine-readable props schema so `page.spec.yaml` files reference real components, the validator can reject unknown components or bad props, and codegen can emit correct JSX. This is the bridge between the design system and the spec builder.

**Scope**

In:
- Convention: each component folder's `meta.ts` exports `defineComponentMeta({ specId, displayName, category, props: z.object(...), slots, events, a11y, examples, since })`.
- Generator `pnpm --filter ui registry:build` producing `packages/ui/registry.json` (JSON Schema per component via `zod-to-json-schema`) and `packages/spec/src/generated/components.ts` (TypeScript union of spec IDs and prop types).
- Spec-side resolver `packages/spec/src/components.ts`: `resolveComponent(specId)` returning the lazy React component and its meta; used by `app-shell/router-layouts` slot registry and `spec-builder/layout-codegen`.
- Validation rules for `spec-builder/validator`: unknown `specId`, unknown prop, wrong type, missing required prop, deprecated component.
- Documentation: `docs/spec/components.md` auto-generated table (id, description, props, slots, example YAML).
- Coverage: all primitives, layout, data-display, Icon and Illustration mapped.

Out: designing the spec schema (`spec-builder/schema`), writing codegen (`spec-builder/layout-codegen`), non-UI packages.

**Spec**

- Spec ID grammar: `ui.<camelCaseName>` for design system, `app.<name>` reserved for app-local components registered through the same API; regex `^(ui|app)\.[a-z][A-Za-z0-9]*$`.
- `props` schema is Zod 4; only JSON-serialisable props are exposed to specs (no functions); event handlers declared in `events: ['onClick', 'onChange']` and bound by codegen to spec `logic` actions.
- `slots: { name: { multiple: boolean, accepts?: specId[] } }` so `AppFrame.sidebar` can restrict what goes in.
- `examples: [{ title, yaml }]` snippets validated at build time against the schema.
- `registry.json` shape: `{ version, generatedAt, components: { [specId]: { displayName, category, schema, slots, events, a11y, deprecated?, since } } }`; committed and drift-checked in CI.
- YAML usage in a page spec (agree final key names in `spec-builder/schema`; interim):
  `components: - id: ui.button  props: { variant: primary, size: md }  slot: main  events: { onClick: actions.save }`
- Resolver uses `import.meta.glob('../../ui/src/**/meta.ts')` in dev and a generated static map in prod to keep tree-shaking.
- Deprecation: `deprecated: { since, replaceWith }` produces a validator warning and a codemod hint.

**Definition of done**

- Every exported component has `meta.ts`; a Vitest test fails if an exported component lacks meta or has an invalid ID.
- `registry.json` and `components.ts` generated, committed, drift-checked in Gate 1.
- Validator rules delivered as a plugin to `spec-builder/validator` with tests for the five error types (or as a standalone `validateComponentUsage()` if the validator is not merged yet).
- Three example page specs in `specs/pages/examples/` validate and resolve to real components; render screenshot at 375 and 1280.
- `docs/spec/components.md` generated; CHANGELOG entry; Linear comment with the doc and registry links.

**Edge cases**

- Two components claim the same `specId`: build fails naming both files.
- Polymorphic `render`/`asChild` props are not spec-exposed; codegen uses named alternatives (`href` produces a link).
- Union props (`size: 'sm'|'md'|'lg'`) must emit JSON Schema enums for editor autocompletion in `spec-builder/spec-editor-ui`.
- Props with defaults: schema includes `default` so the editor can show it and codegen can omit it.
- Renamed component: keep old ID deprecated for one minor version with `replaceWith`.
- Circular slot acceptance (`A` accepts `B` accepts `A`): allowed but depth-limited to 10 in the validator.

**Dependencies**

`design-system/primitives` and `spec-builder/schema` (hard, for final key names; start with the interim shape and adapt). Consumed by `spec-builder/validator`, `spec-builder/layout-codegen`, `spec-builder/spec-editor-ui`, `app-shell/router-layouts`, `quality/edge-case-hunter`.

**Agent**

Built by Iris (Component Crafter) with Quill (Page Spec Writer) owning the YAML shape. Reviewed by Sentinel (Code Reviewer) and Atlas for the contract.

**Size**

M: mechanical per component, but the ID and schema contract must be agreed with the spec builder before it is generated everywhere.
