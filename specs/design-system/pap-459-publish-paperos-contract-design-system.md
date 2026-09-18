---
identifier: "PAP-459"
title: "Publish @paperos/contract-design-system v0.1 with manifest"
project: "design-system"
projectName: "Design System"
phase: "P0"
type: "Spec"
priority: 1
surfaces: ["Developer"]
milestone: "Component library covers app shell needs"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-66", "PAP-74", "PAP-433"]
blocks: ["PAP-234", "PAP-235", "PAP-314", "PAP-460", "PAP-461", "PAP-672"]
key: "module/design-system/contract"
url: "https://linear.app/paperos/issue/PAP-459/publish-paperoscontract-design-system-v01-with-manifest"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:21:06.144Z"
model: "claude-opus-5"
effort: "high"
estimate: 3
dueDate: "2026-09-25"
cycle: null
---

# PAP-459: Publish @paperos/contract-design-system v0.1 with manifest

**Model / Effort:** Opus 5 / high

**Goal**

Publish `@paperos/contract-design-system` v0.1 and the `design-system` module manifest so every other module codes against a versioned package instead of `packages/ui, packages/tokens` internals (`docs/module-system.md` sections 1 to 3). The contract holds only types, Zod schemas, event topics, route signatures, slot definitions and port interfaces; the implementation stays where the existing issues put it. Swap risk is declared `high`, which decides how much of the swap playbook a rewrite must follow.

**Scope**

In:

* `packages/contracts/design-system/` published as `@paperos/contract-design-system` (workspace-private, `0.1.0`): `src/index.ts`, `ports.ts`, `events.ts`, `routes.ts`, `slots.ts` as applicable, an empty `conformance/` (filled by the conformance issue) and `fixtures/`.
* `module.ts` via `defineModule()` (PAP-264 shape) extended with `provides: [{ contract: '@paperos/contract-design-system', version: '0.1.0' }]`, `requires`, `capabilities`, `slots`, `events`, `owner: { agent: 'Iris', project: 'design-system' }`, `swapRisk: 'high'`, `kind: 'runtime'`, plus the generated `module.manifest.json`.
* `ownership.json` `contracts` entry (PAP-305 file) and the generated `docs/platform/contracts/design-system.md` (a `typedoc` stub until the docs generator lands).

Out: runtime behaviour, React, Drizzle tables, network calls; the conformance suite and the kernel binding (own issues). Nothing already fixed by PAP-66, PAP-74 is redesigned; it is packaged.

**Spec**

Ports and schemas exported at v0.1:

* Component id registry: `ui.<name>` with a props JSON Schema per id, generated from the component source (PAP-74); state component ids `ui.errorState`, `ui.deniedState`, `ui.offlineBanner`, `ui.flagDisabled` (PAP-234, PAP-366)
* `TokenSet` (W3C DTCG JSON schema, PAP-66) and `ThemePort`: `resolveTheme(branding) -> CssVariables`, `brandingToInlineCss` (PAP-75, PAP-235)
* `IconPort` (`icon(name)` with the tree-shaken set from PAP-68) and `MotionTokens` (PAP-72)
* `ComponentContract` per registered id: props schema, slots the component accepts, a11y requirements, states

Events declared with `defineTopic()` (payload schemas, version 1): `theme.changed`.

Requires (manifest `requires[]`): \* none hard; `@paperos/contract-app-shell` ^0.1 optional for slot prop typing

Rules: Zod 4 only, JSON Schema generated; no `z.bigint()` on wire schemas (PAP-302 codec); one sentence and one fixture per port method; `size-limit` under 50 KB minified; lint R9 passes; manifest `dependsOn` is derived from `requires`.

**Interface contract**

Provides: `@paperos/contract-design-system@0.1.0` with the exports above; `module.manifest.json` valid against `manifest.schema.json`; `ownership.json` `contracts.design-system`. Consumes: the manifest schema and validator (`PAP-433`), contract-zero (`@paperos/core/types|filter|events`), the decisions in PAP-66 (Define design tokens (color, type, space, radius, motion, el), PAP-74 (Map every component to a spec-builder component ID with prop). Consumed by: PAP-314 (layout codegen), PAP-234 (state components), PAP-235 (email and PDF theme), PAP-120 codegen, PAP-124 spec editor, PAP-71 and PAP-164 cell renderers, and the module's conformance and wire issues.

**Test plan**

* Static: lint rules R7 to R9; generated JSON Schema committed and unchanged; `size-limit`; `tsc --noEmit` with `exactOptionalPropertyTypes`.
* Unit: every schema accepts its valid fixture and rejects its invalid one (the twenty core component ids with one valid and one invalid props sample each, three token sets (light, dark, high contrast), two tenant brandings, one RTL layout case); `defineTopic` registrations resolve at import; the manifest validates and its `requires` resolve against the other manifests.
* Review: Sentinel confirms no implementation leaked into the package.

**Definition of done**

* Package merged, `0.1.0` in the workspace changeset; manifest validates; compatibility matrix shows every `requires` as `ok` or a named pending provider.
* `docs/platform/contracts/design-system.md` generated; short ADR `docs/adr/00xx-contract-design-system.md` recording what was pinned.
* Comments on PAP-314, PAP-234, PAP-235 that their Interface contract sections now import from `@paperos/contract-design-system`; Linear comment here with the docs link.

**Edge cases**

* A port the implementation has not built yet: declared `@experimental` with a fixture; conformance marks it `pending`, never `passed`.
* A type two modules want (for example `Money`) belongs to contract-zero; the validator rejects a schema whose `$id` collides with a core one.
* Implementation disagrees with the contract after merge: the contract wins; the implementation issue gets a comment and a fix child.

**Dependencies**

Blocked by `PAP-433` and PAP-66, PAP-74. Blocks PAP-314, PAP-234, PAP-235, `PAP-460` and `PAP-461`. Soft: docs generator, compatibility matrix job.

**Agent**

Specified by Iris (Design System owner). Reviewed by Sentinel and Atlas (contract ownership).

**Size**

M

**Demo**

Reviewer runs `pnpm contract:show design-system` and sees every `ui.*` id with its schema; edits a fixture to pass `variant: "huge"` to `ui.button` and the conformance run fails with the schema path. Under a minute.
