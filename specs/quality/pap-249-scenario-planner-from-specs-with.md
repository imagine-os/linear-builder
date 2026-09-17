---
identifier: "PAP-249"
title: "Scenario planner from specs with fixture catalogue"
project: "quality"
projectName: "Quality Pipeline"
phase: "P1"
type: "Build"
priority: 1
surfaces: ["Agent"]
milestone: "Visual and video gates"
state: "Backlog"
parent: "PAP-85"
children: []
blockedBy: ["PAP-114", "PAP-239", "PAP-243"]
blocks: ["PAP-250"]
key: "quality/edge-case-hunter/planner"
url: "https://linear.app/paperos/issue/PAP-249/scenario-planner-from-specs-with-fixture-catalogue"
source: "Linear snapshot 2026-09-17T13:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T06:22:42.056Z"
model: "claude-sonnet-5"
effort: "high"
---

# PAP-249: Scenario planner from specs with fixture catalogue

**Goal**

Turn a page spec and a diff into a prioritised scenario plan: a Claude planning step constrained by a schema, a catalogue of nine scenario classes with fixtures and corpora, and scenario memory that reuses good scenarios per component type.

**Scope**

* In: `packages/agents/src/edgecases/planScenarios(spec, diff)`, plan schema, prompt `.claude/agents/reviewers/edge-case-hunter.md`, fixture catalogue definitions (`data.empty|huge|unicode`, `input.invalid`, `network.offline|slow3g|flaky`, `device.slowCpu`, `auth.denied|expired`, `concurrency.doubleSubmit|staleWrite`, `time.dstBoundary|leapDay|farFuture`), corpora in `ops/quality/corpora/`, scenario memory `ops/quality/edge-scenarios.yaml`, budget cap.
* Out: execution (sibling), findings and repros (sibling).

**Spec**

* Plan schema: `{ pageId, scenarios: [{ id, class, description, setup: { seed?, route?, viewport?, auth? }, steps, expect: oracleId[], severityIfFails }] }`; cap 30 per page prioritised by spec-declared risk and diff size.
* Prompt inputs: spec sections `data`, `logic`, `states`, `access`, `edge cases`, diff summary, fixture catalogue, prior scenarios for the same component types (from memory), PAP-79 edge-case checklist; output JSON only, validated by Zod, invalid entries dropped and counted.
* Corpora: unicode (emoji, combining marks, RTL Arabic and Hebrew, CJK, zero-width), injection strings, boundary numbers, dates around DST and leap day; `@faker-js/faker` seed 42.
* Budget: planning under $2 per PR; over budget defers to nightly.

**Interface contract**

* Provides: `ScenarioPlan` type, `SCENARIO_CLASSES`, `planScenarios()`, corpora files, memory format.
* Requires: PAP-114 spec schema, PAP-79 checklist, sibling harness from PAP-81 (SDK runner).
* Consumers: sibling executor, PAP-110 evals.

**Definition of done**

* Plans for the three example specs (PAP-125) contain 15 to 30 valid scenarios each covering at least six classes.
* Invalid model output is dropped with counts (test with a corrupted fixture).
* Memory grows after a run and is reused on the next plan (test).
* Planning cost under $2 across 10 runs.

**Test plan**

* Unit: schema validation, prioritisation, memory merge.
* Integration: planner against fixture specs with mocked SDK and one live run nightly.

**Demo**

`pnpm edge:plan --spec specs/pages/examples/customer-list.page.spec.yaml` and read the JSON: 20 scenarios across empty, huge, unicode, offline, denied and double-submit. Under one minute.

**Edge cases**

* Spec without edge cases section: planner relies on classes and warns.
* Duplicate scenarios across runs: deduped by class plus normalised description.

**Dependencies**

PAP-114, PAP-81 harness child (hard). Blocks the executor sibling.

**Agent**

Built by Sentinel (Edge Case Hunter sub-agent). Reviewed by Nova (data realism) and Atlas (budget).

**Size**

M.
