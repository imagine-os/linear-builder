---
identifier: "PAP-114"
title: "Define the page.spec.yaml schema: purpose, logic, access, data, integrations, layout, components, states, events, edge cases"
project: "spec-builder"
projectName: "Spec Builder"
phase: "P0"
type: "Spec"
priority: 1
surfaces: ["Agent", "Developer"]
milestone: "Spec schema and validator"
state: "Ready for Claude"
parent: null
children: []
blockedBy: []
blocks: ["PAP-74", "PAP-85", "PAP-115", "PAP-116", "PAP-117", "PAP-119", "PAP-120", "PAP-121", "PAP-123", "PAP-124", "PAP-132", "PAP-207", "PAP-249", "PAP-311", "PAP-314", "PAP-320", "PAP-376", "PAP-426"]
key: "spec-builder/schema"
url: "https://linear.app/paperos/issue/PAP-114/define-the-pagespecyaml-schema-purpose-logic-access-data-integrations"
source: "Linear snapshot 2026-09-17T13:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T13:06:16.745Z"
---

# PAP-114: Define the page.spec.yaml schema: purpose, logic, access, data, integrations, layout, components, states, events, edge cases

**Goal**

Define the canonical `page.spec.yaml` format every PaperOS page must have: a Zod 4 schema in `packages/spec` with generated JSON Schema for editors and TypeScript types for codegen. Validator, codegen, conformance tests, canvas and permission engine all read this contract, so it lands first and changes only through ADRs.

**Read first.** Read before coding: [Blueprint](<https://linear.app/paperos/document/paperos-core-platform-blueprint-0c2115fe48f1>) → [Interface & Data Contracts](<https://linear.app/paperos/document/paperos-interface-and-data-contracts-d40e6a4d227c>) → your project's `Contract` section (Linear project content) → your character sheet ([Roster](<https://linear.app/paperos/document/paperos-agent-roster-org-chart-and-character-index-fc7ea7f41ff3>)) → [Execution Schedule](<https://linear.app/paperos/document/paperos-execution-schedule-1fa3d38d6795>) for your start day and the branch-start rule. Contracts §2 rows "Page" and "Component" fix `meta.id`, the section list and `status: ready`; §1 makes Zod 4 the schema language with JSON Schema generated, never hand-written; [Golden Path](<https://linear.app/paperos/document/new-app-in-ten-minutes-the-golden-path-0f49429f566e>) §4 shows what is generated from the spec.

**Scope**

* In: `packages/spec/src/schema/page.ts`, `packages/spec/schema/page.spec.schema.json`, fixtures (valid and invalid), `docs/spec/page-spec.md`, the format ADR, `migrateSpec()` skeleton, the `specVersion` field.
* Out: final `access` (PAP-116), `data` (PAP-119), `integrations` (PAP-121) shapes, which ship here as interim placeholders; the validator CLI (PAP-115); i18n of copy (PAP-375); versioning tooling, explicitly: codemods, `x-deprecated` metadata, rule `SPEC_DEPRECATED`, `paperos-spec migrate` and the 300-fixture rehearsal are not built here. They were the pending issue `spec-builder/spec-versioning`, which Linear cannot create (issue cap, PAP-91 NJ-1) and which nothing in this build requires; this issue ships only the `migrate/` skeleton in Spec so that follow-up has a fixed home when it is created.

**Spec**

* Sections: `meta` (`id`, `title`, `route`, `surface: customer | staff | developer | agent | public`, `owner`, `status: draft | ready | built | deprecated`, `specVersion: 1`), `purpose` (`summary`, `successMetric`), `logic.actions` (`steps[]`, `guard`, `effects[]`, `onError`), `access`, `data`, `integrations`, `layout` (`template: app | public | focus | kiosk`, `slots`), `components` (tree `{ id: ComponentRef, key, props, slot, events, children }`), `states` (`loading`, `empty`, `error`, `offline`, `denied`, custom; each `{ copy, component? }`), `events` (`{ on, to: RouteRef, guard?, kind }`), `edgeCases[]` (`{ id, scenario, expected, test: unit | e2e | manual }`).
* File `specs/pages/<id>.spec.yaml`; `meta.id` equals the filename stem; first line points at the JSON Schema.
* `status: ready` requires `access`, `data` or `x-static: true`, three edge cases and resolvable `events[].to`; component `events` values must reference `logic.actions`.
* `RouteRef` accepts TanStack `$param` syntax; `ComponentRef` regex agreed with PAP-74; `states.copy` strings are plain until PAP-375 adds message ids (`x-i18n` reserved).
* YAML anchors and merge keys resolved before validation; errors carry `line` and `col` of the merged document.
* `packages/spec/src/migrate/` skeleton (the whole versioning deliverable of this issue): `versions.ts` exporting `CURRENT_SPEC_VERSION = 1` and `SPEC_VERSIONS = [{ version: 1, schema: PageSpecSchema, codemodsFrom: {} }]`; an exported `Codemod` interface type (`{ id, description, apply(doc: YAML.Document): Change[] }`) with no implementations; `migrateSpec(doc, to = CURRENT_SPEC_VERSION)` that returns the document unchanged for `specVersion: 1` (missing treated as 1 with the warning above) and throws a `SpecIssue` with code `SPEC_UNSUPPORTED_VERSION` for any other version; `docs/spec/versioning.md` stub naming the follow-up scope (version registry, codemod helpers `renameKey|moveKey|mapEnum|wrapValue`, `paperos-spec migrate --dry-run`, `x-deprecated` and `SPEC_DEPRECATED`, weekly 300-fixture rehearsal). Unit tests: identity for v1, error for v2, `x-*` keys untouched.

**Interface contract**

* Provides: `@paperos/spec` exporting `PageSpec`, `PageSpecSchema`, `ComponentRef`, `RouteRef`, `SpecIssue = { code, severity, message, path, line, col, hint }`, `parseSpec(yaml): Result<PageSpec, SpecIssue[]>`, `migrateSpec(doc)`, the JSON Schema, `specVersion` constant.
* Consumers: PAP-115 rules, PAP-116, PAP-119, PAP-121 (section schemas extend this file), PAP-120 and PAP-122 codegen, PAP-123 graph, PAP-124 editor, PAP-16 `useSpec` (replaces its interim type), PAP-74 registry, PAP-85 edge-case hunter, PAP-132 canvas loader.
* Requires: nothing hard; `ComponentRef` pattern from PAP-74 (interim regex acceptable).

**Definition of done**

* Fixtures parse; each invalid fixture fails with expected `code`, `line`, `col`; JSON Schema snapshot committed.
* `pnpm spec schema:build` idempotent; drift wired into gate 1 (PAP-78).
* VS Code autocompletion screenshot on a fixture.
* `docs/spec/page-spec.md` generated with every field; ADR registered in PAP-130.
* `@paperos/spec` types consumed by PAP-16; changelog; Linear comment with links.

**Test plan**

* Unit (Vitest): parse every fixture; codes `SPEC_DUP_KEY`, `SPEC_BAD_ROUTE`, `SPEC_ACTION_UNBOUND`, `SPEC_READY_INCOMPLETE`, `SPEC_TOO_LARGE`; anchor resolution positions; BOM and CRLF normalisation.
* Property: `parseSpec(stringify(spec))` round-trips for generated valid specs.
* Snapshot: JSON Schema.
* No UI; no breakpoints.

**Demo**

Open `fixtures/valid/customer-invoices.spec.yaml` in VS Code and trigger completion on `layout.template`; then run `pnpm spec parse fixtures/invalid/dup-key.spec.yaml` and read `SPEC_DUP_KEY` with both line numbers. Under one minute.

**Edge cases**

* Duplicate `components[].key`: error listing both lines.
* Route with `:param`: rejected, `$param` only.
* Spec over 200 KB: warn, suggest splitting.
* `specVersion` missing: treated as 1 with a warning.
* Unknown top-level key without `x-` prefix: error; `x-*` passes through untouched.

**Dependencies**

None hard (`readyNow`). Soft: PAP-74. Blocks PAP-115, PAP-116, PAP-117, PAP-119, PAP-120, PAP-121, PAP-123, PAP-124, PAP-132, PAP-85, PAP-74. The future spec-versioning tooling issue depends on this `migrate/` skeleton; nothing live depends on that tooling.

**Agent**

Built by Quill (Page Spec Writer); reviewed by Atlas for architecture and Nova for codegen fit.

**Size**

M
