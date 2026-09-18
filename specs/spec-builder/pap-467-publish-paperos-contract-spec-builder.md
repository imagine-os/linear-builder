---
identifier: "PAP-467"
title: "Publish @paperos/contract-spec-builder v0.1 with manifest"
project: "spec-builder"
projectName: "Spec Builder"
phase: "P1"
type: "Spec"
priority: 2
surfaces: ["Developer"]
milestone: "Spec schema and validator"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-114", "PAP-117", "PAP-433"]
blocks: ["PAP-249", "PAP-320", "PAP-361", "PAP-362", "PAP-470", "PAP-473"]
key: "module/spec-builder/contract"
url: "https://linear.app/paperos/issue/PAP-467/publish-paperoscontract-spec-builder-v01-with-manifest"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:21:04.294Z"
model: "claude-sonnet-5"
effort: "high"
estimate: 3
dueDate: "2026-09-24"
cycle: null
---

# PAP-467: Publish @paperos/contract-spec-builder v0.1 with manifest

**Model / Effort:** Sonnet 5 / high

**Goal**

Publish `@paperos/contract-spec-builder` v0.1 and the `spec-builder` module manifest so every other module codes against a versioned package instead of `packages/spec, specs/` internals (`docs/module-system.md` sections 1 to 3). The contract holds only types, Zod schemas, event topics, route signatures, slot definitions and port interfaces; the implementation stays where the existing issues put it. Swap risk is declared `high`, which decides how much of the swap playbook a rewrite must follow.

**Scope**

In:

* `packages/contracts/spec-builder/` published as `@paperos/contract-spec-builder` (workspace-private, `0.1.0`): `src/index.ts`, `ports.ts`, `events.ts`, `routes.ts`, `slots.ts` as applicable, an empty `conformance/` (filled by the conformance issue) and `fixtures/`.
* `module.ts` via `defineModule()` (PAP-264 shape) extended with `provides: [{ contract: '@paperos/contract-spec-builder', version: '0.1.0' }]`, `requires`, `capabilities`, `slots`, `events`, `owner: { agent: 'Quill', project: 'spec-builder' }`, `swapRisk: 'high'`, `kind: 'tooling and runtime'`, plus the generated `module.manifest.json`.
* `ownership.json` `contracts` entry (PAP-305 file) and the generated `docs/platform/contracts/spec-builder.md` (a `typedoc` stub until the docs generator lands).

Out: runtime behaviour, React, Drizzle tables, network calls; the conformance suite and the kernel binding (own issues). Nothing already fixed by PAP-114, PAP-117 is redesigned; it is packaged.

**Spec**

Ports and schemas exported at v0.1:

* `PageSpec` and `AppSpec` Zod schemas with every section (purpose, logic, access, data, integrations, layout, components, states, events, edgeCases, flags, modules; PAP-114, PAP-117)
* `SpecValidatorPort`: `validate(spec) -> Diagnostics` with stable rule ids (PAP-115)
* `GeneratorPlugin` interface `defineGenerator({ id, inputs, emit })` so codegen targets (layout, hooks, tests, flow graph) are adapters (PAP-120, PAP-122, PAP-123, PAP-362)
* `FlowGraph` output type (pages, transitions, roles) consumed by the canvas (PAP-320)
* `ComponentRef` (`ui.<name>` from design-system) and `AccessSection` compiling to identity policies (PAP-116)

Events declared with `defineTopic()` (payload schemas, version 1): `spec.changed`, `spec.validated`, `spec.generated`.

Requires (manifest `requires[]`): \* `@paperos/contract-design-system` ^0.1 (component ids)

* `@paperos/contract-identity` ^0.1 (policy shape for `access`)
* `@paperos/contract-data-layer` ^0.1 (`FilterTree` in `data`)
* `@paperos/contract-app-shell` ^0.1 (route and slot meta)

Rules: Zod 4 only, JSON Schema generated; no `z.bigint()` on wire schemas (PAP-302 codec); one sentence and one fixture per port method; `size-limit` under 50 KB minified; lint R9 passes; manifest `dependsOn` is derived from `requires`.

**Interface contract**

Provides: `@paperos/contract-spec-builder@0.1.0` with the exports above; `module.manifest.json` valid against `manifest.schema.json`; `ownership.json` `contracts.spec-builder`. Consumes: the manifest schema and validator (`module-system/manifest-schema`), contract-zero (`@paperos/core/types|filter|events`), the decisions in PAP-114 (Define the page.spec.yaml schema: purpose, logic, access, da), PAP-117 (Define app.spec.yaml (audiences, navigation, entities, integ). Consumed by: PAP-361 (entity-derived specs), PAP-362 (`paperos gen`), PAP-249 (scenario planner), PAP-320 (canvas loader), PAP-118 (authoring skill), PAP-64 (permission matrix tests), and the module's conformance and wire issues.

**Test plan**

* Static: lint rules R7 to R9; generated JSON Schema committed and unchanged; `size-limit`; `tsc --noEmit` with `exactOptionalPropertyTypes`.
* Unit: every schema accepts its valid fixture and rejects its invalid one (the three fully specified example pages (PAP-125), one `app.spec.yaml`, eight invalid specs (one per rule family), two flow graphs, one generator run manifest); `defineTopic` registrations resolve at import; the manifest validates and its `requires` resolve against the other manifests.
* Review: Sentinel confirms no implementation leaked into the package.

**Definition of done**

* Package merged, `0.1.0` in the workspace changeset; manifest validates; compatibility matrix shows every `requires` as `ok` or a named pending provider.
* `docs/platform/contracts/spec-builder.md` generated; short ADR `docs/adr/00xx-contract-spec-builder.md` recording what was pinned.
* Comments on PAP-361, PAP-362, PAP-249, PAP-320 that their Interface contract sections now import from `@paperos/contract-spec-builder`; Linear comment here with the docs link.

**Edge cases**

* A port the implementation has not built yet: declared `@experimental` with a fixture; conformance marks it `pending`, never `passed`.
* A type two modules want (for example `Money`) belongs to contract-zero; the validator rejects a schema whose `$id` collides with a core one.
* Implementation disagrees with the contract after merge: the contract wins; the implementation issue gets a comment and a fix child.

**Dependencies**

Blocked by `module-system/manifest-schema` and PAP-114, PAP-117. Blocks PAP-361, PAP-362, PAP-249, PAP-320, `module/spec-builder/conformance` and `module/spec-builder/wire`. Soft: docs generator, compatibility matrix job.

**Agent**

Specified by Quill (Spec Builder owner). Reviewed by Sentinel and Atlas (contract ownership).

**Size**

M

**Demo**

Reviewer runs `pnpm contract:show spec-builder` and validates the three example pages; breaks the `access` section and gets rule id `ACCESS_UNKNOWN_AUDIENCE` with a line number. Under a minute.
