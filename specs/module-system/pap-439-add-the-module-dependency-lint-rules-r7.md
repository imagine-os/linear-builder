---
identifier: "PAP-439"
title: "Add the module dependency lint rules (R7 to R11) and the generated, committed dependency map with Linear identifiers"
project: "module-system"
projectName: "Module System & Swap Tooling"
phase: "P0"
type: "Infra"
priority: 1
surfaces: ["Developer"]
milestone: "Contracts and conformance wired"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-78", "PAP-305", "PAP-433"]
blocks: ["PAP-306", "PAP-440", "PAP-445", "PAP-550", "PAP-552", "PAP-761"]
key: "module-system/dependency-lint-and-map"
url: "https://linear.app/paperos/issue/PAP-439/add-the-module-dependency-lint-rules-r7-to-r11-and-the-generated"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:21:08.931Z"
model: "claude-opus-5"
effort: "medium"
estimate: 3
dueDate: "2026-09-27"
cycle: null
---

# PAP-439: Add the module dependency lint rules (R7 to R11) and the generated, committed dependency map with Linear identifiers

**Model / Effort:** Opus 5 / medium

**Goal**

Make the import graph obey the manifests and make the graph visible. PAP-305 gives us `ownership.json` and generated dependency-cruiser rules; this issue adds the module-system rules (R7 contracts importable by all, R8 no module imports another module's implementation, R9 contracts import only core and contracts and stay acyclic, R10 kernel imports no module, R11 conformance imports only from tests), and `pnpm gen:dep-map`, which writes `docs/platform/dependency-map.json` and a Mermaid rendering from manifests plus the real import graph, with the Linear identifiers that own each edge. Gate 1 fails on undeclared edges or a stale map (`docs/module-system.md` section 3).

**Scope**

In:

* Rules R7 to R11 added to the `allowedDeps` source in `ownership.json` and to the generated `.dependency-cruiser.cjs`; Biome `noRestrictedImports` mirror for editor feedback.
* `pnpm gen:dep-map`: nodes (modules, contracts, kernel), edges (`requires`, `fills`, `publishes`, `subscribes`, `imports`), each edge annotated with the Linear identifiers from the manifests' `issues` field and `ownership.json`; outputs JSON and Mermaid; `--undeclared` lists import edges with no manifest edge.
* Gate 1 steps `deps` (violations) and `dep-map` (stale or undeclared) in PAP-78's workflow.
* Blueprint hook: `tools/blueprint/build_v3.js` reads `dependency-map.json` when present (the dependency views are another agent's issue; this issue only guarantees the file shape and a stable schema `dependency-map.schema.json`).
* Linear mirror export: `pnpm gen:dep-map --linear` emits the expected `blocks` edges (contract issue blocks consumer Build issues) for PAP-306's weekly re-audit to diff.

Out: fixing violations in modules (their wire issues), the Blueprint rendering, the weekly audit itself (PAP-306).

**Spec**

* Violation messages: rule id, offending import, module owner to ask, and the manifest edge that would legalise it, for example `R8 packages/crm -> packages/views/src/compiler.ts: resolve @paperos/contract-tables.ViewQueryPort from the kernel (owner: tables)`.
* The map is deterministic (sorted nodes and edges) so diffs are readable; regeneration in CI must be byte-identical to the committed file.
* Contract graph acyclicity is checked in the map job; a cycle fails with the path.
* Type-only imports count as imports for R8; `import type` across modules is still a coupling.
* Runtime under 20 s on the full template.

**Interface contract**

Provides: rules R7 to R11, `pnpm gen:dep-map` (JSON, Mermaid, `--undeclared`, `--linear`), `dependency-map.schema.json`, Gate 1 steps `deps` and `dep-map`. Consumes: PAP-305 `ownership.json` and rule generator, PAP-78 Gate 1, manifest validator, PAP-264 lint rule `@paperos/no-cross-module-import` (subsumed by R8). Consumed by: every `Wire <module>` issue (zero undeclared edges is their exit criterion), PAP-306 weekly re-audit, the docs generator, the Blueprint dependency views, PAP-24 template guide.

**Test plan**

* Fixtures: one passing and one failing sample per rule under `tools/deps/fixtures/`; the failing ones produce the exact messages.
* Map: golden `dependency-map.json` for the fixture workspace; determinism (run twice, identical); acyclicity failure fixture.
* Gate: a PR introducing an undeclared import fails `dep-map` with the edge named; a PR editing the map by hand fails as stale.
* Performance: full template under 20 s.

**Definition of done**

* Rules and generator merged; Gate 1 steps live; `dependency-map.json` committed for the template with every existing edge declared or listed in a dated `undeclared.baseline.json` that the wire issues burn down.
* `docs/platform/dependency-map.md` rendered Mermaid; Linear comment.

**Edge cases**

* Baseline violations from code written before this issue: allowed through `undeclared.baseline.json` with an expiry date; new violations never.
* Generated code (PAP-120 codegen output) importing a module: the generator is the culprit; the message names the generator id.
* `apps/*` importing modules directly for boot wiring: allowed only in `apps/*/src/kernel.ts` (explicit exception in R8).
* A contract importing another contract creating a cycle through types only: still a cycle; split the shared type into contract-zero.

**Dependencies**

Blocked by PAP-305, PAP-78, module-system/manifest-schema. Blocks PAP-306.

**Agent**

Built by Forge. Reviewed by Sentinel.

**Size**

M

**Demo**

Reviewer runs `pnpm gen:dep-map --undeclared` and sees the baseline list shrinking as wire issues land; adds `import { compile } from '@paperos/views/src/compiler'` to `packages/crm` and Gate 1 fails with the R8 message naming the port to resolve instead. Under a minute.
