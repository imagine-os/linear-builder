---
identifier: "PAP-462"
title: "Publish @paperos/contract-quality v0.1 with manifest"
project: "quality"
projectName: "Quality Pipeline"
phase: "P0"
type: "Spec"
priority: 1
surfaces: ["Developer"]
milestone: "Gates 1 and 2 on every PR"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-79", "PAP-239", "PAP-433"]
blocks: ["PAP-83", "PAP-84", "PAP-89", "PAP-137", "PAP-463", "PAP-464"]
key: "module/quality/contract"
url: "https://linear.app/paperos/issue/PAP-462/publish-paperoscontract-quality-v01-with-manifest"
source: "Linear snapshot 2026-09-17T15:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T14:54:13.216Z"
model: "claude-opus-5"
effort: "high"
---

# PAP-462: Publish @paperos/contract-quality v0.1 with manifest

**Model / Effort:** Opus 5 / high

**Goal**

Publish `@paperos/contract-quality` v0.1 and the `quality` module manifest so every other module codes against a versioned package instead of `packages/contracts/quality (moved from packages/contracts), .github/workflows, tools/gates` internals (`docs/module-system.md` sections 1 to 3). The contract holds only types, Zod schemas, event topics, route signatures, slot definitions and port interfaces; the implementation stays where the existing issues put it. Swap risk is declared `medium`, which decides how much of the swap playbook a rewrite must follow.

**Scope**

In:

* `packages/contracts/quality/` published as `@paperos/contract-quality` (workspace-private, `0.1.0`): `src/index.ts`, `ports.ts`, `events.ts`, `routes.ts`, `slots.ts` as applicable, an empty `conformance/` (filled by the conformance issue) and `fixtures/`.
* `module.ts` via `defineModule()` (PAP-264 shape) extended with `provides: [{ contract: '@paperos/contract-quality', version: '0.1.0' }]`, `requires`, `capabilities`, `slots`, `events`, `owner: { agent: 'Sentinel', project: 'quality' }`, `swapRisk: 'medium'`, `kind: 'tooling'`, plus the generated `module.manifest.json`.
* `ownership.json` `contracts` entry (PAP-305 file) and the generated `docs/platform/contracts/quality.md` (a `typedoc` stub until the docs generator lands).

Out: runtime behaviour, React, Drizzle tables, network calls; the conformance suite and the kernel binding (own issues). Nothing already fixed by PAP-79, PAP-239 is redesigned; it is packaged.

**Spec**

Ports and schemas exported at v0.1:

* Gate artefact schemas `gate1.json`, `security.json`, `visual.json`, `review.json`, `edge.json`, `perf.json` and the new `conformance.json` (PAP-239)
* `ReviewFinding` and the severity taxonomy (PAP-79), `Rubric` schema for reviewer agents
* `GateRunnerPort`: `run(gate, prRef)`, `artefacts(prRef)`, `baseline.update(visual)` (PAP-243, PAP-247)
* `RcManifest` for release candidates and the digest input (PAP-88, PAP-89)
* `TestSeedPort` (`/__test/seed`, `/__test/reset` contract; PAP-240)

Events declared with `defineTopic()` (payload schemas, version 1): `review.gate_failed`, `review.ready`, `release.candidate`, `gate.flaky_quarantined`.

Requires (manifest `requires[]`): \* `@paperos/contract-forge` ^0.1 (PR and commit refs)

* `@paperos/contract-pm-linear` ^0.1 (issue refs, Needs Justin card shape)

Rules: Zod 4 only, JSON Schema generated; no `z.bigint()` on wire schemas (PAP-302 codec); one sentence and one fixture per port method; `size-limit` under 50 KB minified; lint R9 passes; manifest `dependsOn` is derived from `requires`.

**Interface contract**

Provides: `@paperos/contract-quality@0.1.0` with the exports above; `module.manifest.json` valid against `manifest.schema.json`; `ownership.json` `contracts.quality`. Consumes: the manifest schema and validator (`PAP-433`), contract-zero (`@paperos/core/types|filter|events`), the decisions in PAP-79 (Write review rubrics and a severity taxonomy shared by all r), PAP-239 (Specify the gate artifact contract: one schema package for g). Consumed by: PAP-83 and PAP-84 (video and vision gates), PAP-89 (digest), PAP-137 (screenshot comments), PAP-97 (orchestrator status), PAP-110 (eval harness scoring), and the module's conformance and wire issues.

**Test plan**

* Static: lint rules R7 to R9; generated JSON Schema committed and unchanged; `size-limit`; `tsc --noEmit` with `exactOptionalPropertyTypes`.
* Unit: every schema accepts its valid fixture and rejects its invalid one (one artefact per gate (passing and failing), twelve findings across the severity taxonomy, two RC manifests, one seed and reset trace); `defineTopic` registrations resolve at import; the manifest validates and its `requires` resolve against the other manifests.
* Review: Atlas confirms no implementation leaked into the package.

**Definition of done**

* Package merged, `0.1.0` in the workspace changeset; manifest validates; compatibility matrix shows every `requires` as `ok` or a named pending provider.
* `docs/platform/contracts/quality.md` generated; short ADR `docs/adr/00xx-contract-quality.md` recording what was pinned.
* Comments on PAP-83, PAP-84, PAP-89, PAP-137 that their Interface contract sections now import from `@paperos/contract-quality`; Linear comment here with the docs link.

**Edge cases**

* A port the implementation has not built yet: declared `@experimental` with a fixture; conformance marks it `pending`, never `passed`.
* A type two modules want (for example `Money`) belongs to contract-zero; the validator rejects a schema whose `$id` collides with a core one.
* Implementation disagrees with the contract after merge: the contract wins; the implementation issue gets a comment and a fix child.

**Dependencies**

Blocked by `PAP-433` and PAP-79, PAP-239. Blocks PAP-83, PAP-84, PAP-89, PAP-137, `PAP-463` and `PAP-464`. Soft: docs generator, compatibility matrix job.

**Agent**

Specified by Sentinel (Quality Pipeline owner). Reviewed by Atlas and Atlas (contract ownership).

**Size**

M

**Demo**

Reviewer runs `pnpm contract:show quality` and sees the seven artefact schemas; validates a real `gate1.json` from a PR against it and a hand-broken one, which fails with the path. Under a minute.
