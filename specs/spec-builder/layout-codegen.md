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
children: []
blockedBy: ["PAP-114", "PAP-234", "PAP-74"]
blocks: ["PAP-29"]
key: "spec-builder/layout-codegen"
url: "https://linear.app/paperos/issue/PAP-120/generate-page-scaffolds-layout-component-tree-loadingemptyerror-states"
source: "plan/specs/bucket-4.json (round-1 canonical spec JSON)"
---

# PAP-120: Generate page scaffolds (layout, component tree, loading/empty/error states) from specs

**Goal**

Turn a validated page spec into a working page skeleton: the TanStack route file, the layout slot wiring, the component tree as JSX bound to real design-system components, and loading, empty, error, offline and denied states. An agent building a page starts from a rendering scaffold and only writes logic.

**Scope**

In:
- `pnpm spec gen:page <id> [--all] [--check]` in `packages/spec/src/codegen/page.ts` producing for `meta.route = /_app/invoices`:
  - `apps/web/src/routes/_app/invoices.tsx` (created once, never overwritten): exports `Route = createFileRoute('/_app/invoices')({ component: InvoicesPage, validateSearch, staticData: { spec: 'customer-invoices' } })` and imports the generated view.
  - `apps/web/src/generated/pages/customer-invoices.view.tsx` (always regenerated): `<InvoicesView>` rendering the component tree, slots via `useLayout()` from `app-shell/router-layouts`, and a `states` switch using `ui.skeleton`, `ui.emptyState`, `ui.errorState`, `ui.offlineBanner` from `design-system/data-display`, and a `DeniedState` when `useCan('page.view')` is false.
  - `apps/web/src/pages/customer-invoices.logic.ts` (created once): typed stubs for every `logic.actions` entry (`export const actions = { markPaid: async (ctx) => { /* TODO */ } }`) and the data hooks import from `spec-builder/data-section`.
  - `apps/web/src/generated/pages/customer-invoices.stories.tsx`: one Storybook story per state with mocked hooks.
- Component resolution through `resolveComponent(specId)` from `design-system/component-spec-mapping`; props emitted from spec `props` after schema validation; `events` bound to `actions.<name>`; `children` recursed; every element gets `data-spec-key={key}` for conformance tests and comment anchors.
- Formatting with Biome after emit; imports sorted; generated banner with spec hash so `--check` fails when the spec changed and the view was not regenerated (drift job in gate 1).

Out: writing business logic, data hook generation (`spec-builder/data-section`), visual design decisions, non-React targets.

**Spec**

- Templates are TypeScript functions in `packages/spec/src/codegen/templates/` using tagged strings, not a template language, so they are type-checked; a `Printer` helper handles indentation and import dedupe.
- Two-file pattern is the rule: `*.view.tsx` is owned by the generator, route and logic files are owned by humans and agents; the generator refuses to touch them unless `--force`.
- Layout template `app|public|focus|kiosk` maps to the shell layouts of `app-shell/router-layouts`; unknown slot names fail generation.
- Unknown component in dev renders `<MissingComponent id>`; in `--check` mode it is an error.
- Search params from `data.queries[].filter[].param: search.*` generate a Zod 4 `validateSearch` schema.
- Generation is deterministic: same spec and registry produce byte-identical output; verified by generating twice in CI.

**Definition of done**

- Vitest: template snapshots for minimal and maximal fixtures, slot mapping, event binding, `--check` drift detection, refusal to overwrite owned files.
- The three example specs from `spec-builder/spec-docs` generate, typecheck and render; Playwright screenshots of each state at 320, 375, 768, 1024, 1280, 1536 and 1920 in light and dark.
- Storybook stories appear in the `design-system/storybook` deploy (link).
- Generating a page then running `spec-builder/conformance-tests` passes with zero manual edits.
- `docs/spec/codegen.md` including the two-file pattern; CHANGELOG entry; Linear comment with screenshots and story links.

**Edge cases**

- Spec changes a component `key`: view regenerates; logic file keeps old handler with a `// TODO(unused)` marker rather than silent deletion.
- Route file already exists with a different `staticData.spec`: generation aborts with the conflict.
- Component tree deeper than 12 levels: warning, still generated.
- Props containing a value the schema marks as default: omitted from JSX to keep output short.
- Spec `layout.template: kiosk` before `app-shell/linux-kiosk` exists: falls back to `focus` with a warning.
- Biome unavailable: emit unformatted with a warning; drift check formats before comparing.

**Dependencies**

`spec-builder/schema` (hard), `design-system/component-spec-mapping` (hard, resolver and registry). Soft: `spec-builder/data-section` (hooks; stubs otherwise), `app-shell/router-layouts` (slot API), `design-system/data-display` (state components; plain fallbacks otherwise). Consumed by `agents/skills-library` `page-from-spec`.

**Agent**

Built by Nova with Iris (Component Crafter) on component emission. Reviewed by Sentinel (Code Reviewer, spec-conformance reviewer) and Forge for router integration.

**Size**

L: deterministic codegen with an ownership model and story generation across many components.
