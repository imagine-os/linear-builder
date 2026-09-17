---
key: "spec-builder/layout-codegen/templates"
title: "Layout codegen: Printer, route and view templates, two-file ownership and determinism"
project: "spec-builder"
parent: "PAP-120"
phase: "P1"
type: "Build"
priority: null
size: "M"
surfaces: ["Developer"]
milestone: null
intendedState: "Backlog"
blockedBy: []
blocks: ["spec-builder/layout-codegen/wiring", "spec-builder/layout-codegen/examples"]
source: "round2/agent2/new_spec.py"
linearDocument: "https://linear.app/paperos/document/round-2-pending-issues-spec-builder-11-c314e290076b"
identifier: "PAP-314"
status: "created"
createdAt: "2026-09-17"
---

# Layout codegen: Printer, route and view templates, two-file ownership and determinism

**Goal**

Build the codegen core: type-checked TypeScript templates with a `Printer` for indentation and import dedupe, the route file (created once), the regenerated view file, the logic stub file (created once) and the stories file, the two-file ownership rule with `--force`, Biome formatting and byte-identical determinism checked by `--check`.

**Scope**

* In: `packages/spec/src/codegen/{printer,page}.ts`, `templates/{route,view,logic,stories}.ts`, `pnpm spec gen:page <id> [--all] [--check] [--force]`, banner with spec hash, `docs/spec/codegen.md` ownership section.
* Out: state, slot and event wiring (`spec-builder/layout-codegen/wiring`), the example run (`spec-builder/layout-codegen/examples`).

**Spec**

* `Printer`: `line()`, `indent()`, `import(name, from)` with dedupe and sorted output, `block()`; templates are functions `(ctx: TemplateContext) => string`.
* Route: `createFileRoute('<route>')({ component, validateSearch?, staticData: { spec: '<id>' } })`; created if absent, otherwise compared: same `staticData.spec` leaves it; different aborts with the conflict.
* View: `<IdView>` placeholder rendering the component tree via `resolveComponent()` (PAP-74) with `data-spec-key`, props from the spec after schema validation, `children` recursed; wiring child adds states and events.
* Logic: `export const actions = { <name>: async (ctx) => { /* TODO */ } }` typed from `logic.actions`; created once; renamed actions leave `// TODO(unused)`.
* Stories: one story per `states` key with mocked hooks (wired fully by the wiring child).
* Determinism: sorted imports, LF, no timestamps; banner `// generated from specs/pages/<id>.spec.yaml sha256:<hash>`; `--check` regenerates in memory and diffs; Biome formats output.

**Interface contract**

* Provides: `Printer`, `TemplateContext = { spec, app, registry, hooks?, options }`, `generatePage(ctx): GeneratedFiles`, CLI, ownership rule (`owned: generator | human`) per output, banner format shared with PAP-119.
* Consumers: wiring child extends templates; PAP-124 preview compiles the view template in-browser; PAP-105 `page-from-spec`; PAP-29 drill.
* Requires: PAP-114 schema, PAP-74 `resolveComponent` and registry (hard).

**Definition of done**

* Snapshots for minimal and maximal fixtures; `--check` drift test; refusal to overwrite owned files test; `--force` test.
* Generating twice is byte-identical in CI.
* Docs ownership section; changelog; Linear comment.

**Test plan**

* Unit: `Printer` import dedupe and ordering, banner hash, conflict detection, recursion depth warning at 12.
* Integration: generated files typecheck in `apps/web` for the fixtures.
* No UI in this child.

**Demo**

Run `pnpm spec gen:page customer-invoices`, open the three files, edit the logic stub, regenerate and see the logic file untouched while the view banner hash changes only when the spec changes. One minute.

**Edge cases**

* Unknown component: dev renders `<MissingComponent id>`, `--check` errors.
* Props equal to schema defaults: omitted.
* Tree deeper than 12 levels: warning.
* Route file hand-edited beyond `staticData`: left alone; only `staticData.spec` compared.
* Biome unavailable: unformatted with a warning; drift check formats before comparing.

**Dependencies**

Blocked by PAP-114, PAP-74 (through the parent). Blocks both sibling children.

**Agent**

Built by Nova; reviewed by Sentinel (Code Reviewer).

**Size**

M
