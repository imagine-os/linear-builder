---
identifier: "PAP-493"
title: "Publish @paperos/contract-libraries v0.1 with manifest"
project: "libraries"
projectName: "Library Discovery & Integration"
phase: "P0"
type: "Spec"
priority: 1
surfaces: ["Developer"]
milestone: "Core adoptions decided"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-209", "PAP-433"]
blocks: ["PAP-216", "PAP-217", "PAP-218", "PAP-495", "PAP-497"]
key: "module/libraries/contract"
url: "https://linear.app/paperos/issue/PAP-493/publish-paperoscontract-libraries-v01-with-manifest"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:20:59.904Z"
model: "claude-opus-5"
effort: "high"
estimate: 2
dueDate: "2026-09-24"
cycle: null
---

# PAP-493: Publish @paperos/contract-libraries v0.1 with manifest

**Model / Effort:** Opus 5 / high

**Goal**

Publish `@paperos/contract-libraries` v0.1 and the `libraries` module manifest so every other module codes against a versioned package instead of `docs/libraries, tools/libraries, renovate.json, .github/workflows/license.yml` internals (`docs/module-system.md` sections 1 to 3). The contract holds only types, Zod schemas, event topics, route signatures, slot definitions and port interfaces; the implementation stays where the existing issues put it. Swap risk is declared `low`, which decides how much of the swap playbook a rewrite must follow.

**Scope**

In:

* `packages/contracts/libraries/` published as `@paperos/contract-libraries` (workspace-private, `0.1.0`): `src/index.ts`, `ports.ts`, `events.ts`, `routes.ts`, `slots.ts` as applicable, an empty `conformance/` (filled by the conformance issue) and `fixtures/`.
* `module.ts` via `defineModule()` (PAP-264 shape) extended with `provides: [{ contract: '@paperos/contract-libraries', version: '0.1.0' }]`, `requires`, `capabilities`, `slots`, `events`, `owner: { agent: 'Scout', project: 'libraries' }`, `swapRisk: 'low'`, `kind: 'process'`, plus the generated `module.manifest.json`.
* `ownership.json` `contracts` entry (PAP-305 file) and the generated `docs/platform/contracts/libraries.md` (a `typedoc` stub until the docs generator lands).

Out: runtime behaviour, React, Drizzle tables, network calls; the conformance suite and the kernel binding (own issues). Nothing already fixed by PAP-209 is redesigned; it is packaged.

**Spec**

Ports and schemas exported at v0.1:

* `LibraryRecord` (adopted, trialing, rejected; owner, ADR link, license, rubric scores; PAP-216)
* `EvaluationRubric` scores and weights (PAP-209) and `AdrFrontmatter` (status, alternatives, issues; PAP-130 compatible)
* `LicensePolicy` (allow, review, block lists) consumed by the CI check (PAP-211) and `McpConnectorRecord` (PAP-210)
* `RenovateGroup` schema (PAP-217) and `ScoutReport` (PAP-218)

Events declared with `defineTopic()` (payload schemas, version 1): `library.adopted|rejected|trialing`, `scout.report.published`.

Requires (manifest `requires[]`): \* `@paperos/contract-collab` ^0.1 (registry pages in the docs engine)

* `@paperos/contract-quality` ^0.1 (license check as a gate step)

Rules: Zod 4 only, JSON Schema generated; no `z.bigint()` on wire schemas (PAP-302 codec); one sentence and one fixture per port method; `size-limit` under 50 KB minified; lint R9 passes; manifest `dependsOn` is derived from `requires`.

**Interface contract**

Provides: `@paperos/contract-libraries@0.1.0` with the exports above; `module.manifest.json` valid against `manifest.schema.json`; `ownership.json` `contracts.libraries`. Consumes: the manifest schema and validator (`module-system/manifest-schema`), contract-zero (`@paperos/core/types|filter|events`), the decisions in PAP-209 (Define the library evaluation rubric (license, maintenance, ). Consumed by: PAP-216 (registry), PAP-217 (Renovate), PAP-218 (Scout routine), PAP-211 license policy, every ADR, and the module's conformance and wire issues.

**Test plan**

* Static: lint rules R7 to R9; generated JSON Schema committed and unchanged; `size-limit`; `tsc --noEmit` with `exactOptionalPropertyTypes`.
* Unit: every schema accepts its valid fixture and rejects its invalid one (twelve library records (four per status), three ADRs, the license policy with one allowed, one review and one blocked package, two Scout reports); `defineTopic` registrations resolve at import; the manifest validates and its `requires` resolve against the other manifests.
* Review: Atlas confirms no implementation leaked into the package.

**Definition of done**

* Package merged, `0.1.0` in the workspace changeset; manifest validates; compatibility matrix shows every `requires` as `ok` or a named pending provider.
* `docs/platform/contracts/libraries.md` generated; short ADR `docs/adr/00xx-contract-libraries.md` recording what was pinned.
* Comments on PAP-216, PAP-217, PAP-218 that their Interface contract sections now import from `@paperos/contract-libraries`; Linear comment here with the docs link.

**Edge cases**

* A port the implementation has not built yet: declared `@experimental` with a fixture; conformance marks it `pending`, never `passed`.
* A type two modules want (for example `Money`) belongs to contract-zero; the validator rejects a schema whose `$id` collides with a core one.
* Implementation disagrees with the contract after merge: the contract wins; the implementation issue gets a comment and a fix child.

**Dependencies**

Blocked by `module-system/manifest-schema` and PAP-209. Blocks PAP-216, PAP-217, PAP-218, `module/libraries/conformance` and `module/libraries/wire`. Soft: docs generator, compatibility matrix job.

**Agent**

Specified by Scout (Library Discovery & Integration owner). Reviewed by Atlas and Atlas (contract ownership).

**Size**

S

**Demo**

Reviewer runs `pnpm contract:show libraries` and validates the registry fixtures; adds a package under SSPL and the policy check blocks it with the rule name. Under a minute.
