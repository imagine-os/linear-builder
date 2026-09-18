---
identifier: "PAP-85"
title: "Build gate 4: edge-case hunter agent generating adversarial inputs, empty/huge/unicode states, network failure and slow-device scenarios from page specs"
project: "quality"
projectName: "Quality Pipeline"
phase: "P1"
type: "Build"
priority: 1
surfaces: ["Agent"]
milestone: "Visual and video gates"
state: "Backlog"
parent: null
children: ["PAP-251", "PAP-249", "PAP-250"]
blockedBy: ["PAP-81", "PAP-114", "PAP-239", "PAP-240", "PAP-243", "PAP-244", "PAP-245", "PAP-677"]
blocks: ["PAP-843"]
key: "quality/edge-case-hunter"
url: "https://linear.app/paperos/issue/PAP-85/build-gate-4-edge-case-hunter-agent-generating-adversarial-inputs"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:31:01.574Z"
model: null
effort: null
estimate: null
dueDate: "2026-09-26"
cycle: null
---

# PAP-85: Build gate 4: edge-case hunter agent generating adversarial inputs, empty/huge/unicode states, network failure and slow-device scenarios from page specs

**Model / Effort:** set on children (umbrella is never claimed)

**Goal**

Build Gate 4: an agent that reads each changed page's spec and derives adversarial scenarios (empty, huge, unicode and RTL data, invalid input, network failure, slow device, permission denied, concurrent edits, odd dates), executes them with Playwright, files structured findings and hands failures back as reproducible tests, so happy-path coverage stops being the ceiling. Umbrella for three children.

**Children**

1. PAP-249 Scenario planner from specs with fixture catalogue (M) - blocks the executor.
2. PAP-250 Playwright executor and generic oracles (M) - also blocked by PAP-240.
3. PAP-251 Findings, generated repro tests and nightly library run (S).

**Scope**

* In (across children): `packages/agents/src/edgecases/` planner, executor, oracles, report; nine scenario classes with fixtures and corpora; scenario memory; `edgecases.json`; PR matrix comment; repro PR generation; nightly library run with Linear issues.
* Out: API fuzzing, load testing (PAP-147), security exploitation (PAP-80), flake handling (PAP-90 consumes).

**Spec**

Details live in the children. Cross-child rules:

* Plans are schema-validated JSON capped at 30 scenarios per page; invalid entries are dropped and counted, never executed.
* Oracles are generic and pure; page-specific expectations come only from the spec's declared states and edge cases.
* Destructive scenarios run only against the ephemeral preview with a tenant seeded by PAP-240; never staging.
* Budget: planning under $2 and execution under 8 minutes per PR across 2 shards; overflow defers to nightly.

**Interface contract**

* Provides: `ScenarioPlan`, `SCENARIO_CLASSES`, `Oracle` interface, `planScenarios()`, `runScenarios()`, `report()`; `reports/edgecases.json` (`GateReport<'edgecases'>` with `data.matrix`), status `gate/4-edge`, "Edge cases" comment section, repro test convention `apps/web/e2e/generated/<page>/<scenarioId>.spec.ts`, nightly Linear issue template, `ops/quality/edge-scenarios.yaml` memory, corpora in `ops/quality/corpora/`.
* Requires: PAP-114 spec schema, PAP-243 runner, PAP-240 seed and `loginAs`, PAP-246 projects and DOM metrics, PAP-239 schema, PAP-79 checklist, PAP-97 webhooks (soft), PAP-48 bot (soft), PAP-84 `vision.json` for dedupe (soft).
* Consumers: PAP-88 certification, PAP-89 section 3, PAP-110 evals, PAP-90 flake input, PAP-241 escaped-defect source.
* Contract source: [Interface & Data Contracts](<https://linear.app/paperos/document/paperos-interface-and-data-contracts-d40e6a4d227c>) §5 (`packages/contracts` is owned by quality through PAP-239: every `reports/*.json` named above is a `GateReport<kind>` validated by `validateArtifact()`, JSON Schema generated from Zod 4 per §1); §3 (gate results reach the bus as `review.gate_failed` and `review.ready` through PAP-97; artifact `version` bumps keep a reader for 30 days); §6 row "Gate artifacts" (provider PAP-239; consumers PAP-78 to PAP-90, PAP-97, PAP-137, PAP-110). Until PAP-239 merges, write the shape exactly as its Interface contract states and import the schema when it lands. `reports/edgecases.json` is `GateReport<'edgecases'>` with `data.matrix`; the spec it reads is the §2 "Page" contract (PAP-114).

**Definition of done**

* All three children Done.
* Integration run below green; matrix screenshot and repro PR link in the Linear comment.
* `docs/quality/edge-cases.md`; changelog entry.

**Test plan**

Umbrella run on a PR touching an example page:

* At least 15 scenarios executed across six or more classes with evidence for failures; the matrix comment and `gate/4-edge` status post.
* Seeded defects (unhandled empty list, crash on emoji name, missing offline state, double submit creating duplicates) each caught by the correct oracle at the planned severity.
* Repro PR opened for the failures, passing lint and typecheck; a clean page yields zero S0/S1.
* Nightly dry run lists Linear issues it would create; planning under $2 and execution under 8 minutes.

**Demo**

Open the "Edge cases" comment on the seeded PR, click the red `data.unicode` cell, copy the `pnpm edge:run --page … --scenario …` command, run it locally and watch the emoji crash reproduce with a screenshot. Under two minutes.

**Edge cases**

Cross-child: a page without a spec gets S1 "no spec" and generic oracles only; flaky scenarios are repeated three times and only consistent failures are reported; findings overlapping PAP-84 overflow boxes above 0.6 IoU are deduped.

**Dependencies**

PAP-114, PAP-81 (PAP-243 harness) (hard); PAP-240 (hard for PAP-250). Soft: PAP-246, PAP-84, PAP-97, PAP-48, PAP-239.

**Agent**

Sentinel (Edge Case Hunter) builds all children. Reviewed by Nova (data realism), Forge (fixtures) and Atlas (budget, Linear policy).

**Size**

L, split into 3 children (M, M, S).
