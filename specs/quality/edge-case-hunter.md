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
blockedBy: ["PAP-114", "PAP-239", "PAP-240", "PAP-244", "PAP-245", "PAP-81"]
blocks: []
key: "quality/edge-case-hunter"
url: "https://linear.app/paperos/issue/PAP-85/build-gate-4-edge-case-hunter-agent-generating-adversarial-inputs"
source: "plan/specs/bucket-2.json (round-1 canonical spec JSON)"
---

# PAP-85: Build gate 4: edge-case hunter agent generating adversarial inputs, empty/huge/unicode states, network failure and slow-device scenarios from page specs

**Goal**

Build Gate 4: an agent that reads each changed page's spec and derives adversarial scenarios (empty, huge, unicode and RTL data, invalid input, network failure, slow device, permission denied, concurrent edits) then executes them with Playwright, files structured findings, and hands failing scenarios back as reproducible tests so happy-path coverage stops being the ceiling.

**Scope**

In:
- `packages/agents/src/edgecases/`: `planScenarios(spec, diff)` (Claude generates a scenario matrix from the page spec's data, logic, states, access and edge-cases sections plus the rubric's edge-case checklist), `runScenarios(plan)` (Playwright executor with fixtures for each scenario class), `report()` (findings in the shared schema).
- Scenario classes and fixtures: `data.empty`, `data.huge` (10k rows, 50k-char strings), `data.unicode` (emoji, combining marks, RTL Arabic and Hebrew, CJK, zero-width), `input.invalid` (types, bounds, injection strings), `network.offline|slow3g|flaky` (Playwright `route` with delays and aborts), `device.slowCpu` (CDP `Emulation.setCPUThrottlingRate 6`), `auth.denied|expired`, `concurrency.doubleSubmit|staleWrite`, `time.dstBoundary|leapDay|farFuture`.
- Generic oracles: no unhandled exception, no console error, no infinite spinner beyond 10s, declared states render (empty, error, offline, no-permission from the spec), no layout overflow (reuses DOM metrics), form errors announced, data survives reload.
- Output: `reports/edgecases.json`, PR comment "Edge cases" with pass/fail matrix, statuses `gate/4-edge`; S0/S1 rules from the rubric.
- Failing scenarios saved as generated Playwright tests under `apps/web/e2e/generated/<page>/<scenarioId>.spec.ts` in a `edge-case-repros` PR against the same branch, marked `test.fixme` until fixed so they document the gap.
- Scenario memory: `ops/quality/edge-scenarios.yaml` accumulates useful scenarios per component type for reuse across pages.

Out: fuzzing APIs directly (later), load testing (`realtime/load-test`), security exploitation (`quality/security-scans`).

**Spec**

- Plan schema: `{ pageId, scenarios: [{ id, class, description, setup: { seed?, route?, viewport?, auth? }, steps, expect: [oracleId or custom] , severityIfFails }] }`, capped at 30 scenarios per page, prioritised by spec-declared risk and diff size.
- Prompt `.claude/agents/reviewers/edge-case-hunter.md` includes the spec, the diff summary, the fixture catalogue, prior scenarios for the same component types, and outputs JSON only.
- Executor uses `quality/playwright-matrix` fixtures; runs at `sm-375` and `xl-1280` by default; seeds via the test seed endpoint with generated payloads from `@faker-js/faker` with a fixed seed and unicode corpora in `ops/quality/corpora/`.
- Budget: planning under $2 and execution under 8 minutes per PR across 2 shards; excess scenarios deferred to the nightly run on `main`.
- Findings include the reproduction command `pnpm edge:run --page <id> --scenario <sid>` and a screenshot or video evidence ref.
- Nightly run on `main` executes the full scenario library for all pages and opens Linear issues for new S1 findings (deduped by finding ID) via `pm-linear/webhooks`.

**Definition of done**

- On a PR touching a page with a spec, the hunter posts a matrix with at least 15 scenarios executed and evidence for failures (link).
- Seeded defects (unhandled empty list, crash on emoji name, missing offline state, double submit creating duplicates) are each caught with correct severity.
- Generated repro tests PR opened for failures and passes lint and typecheck.
- Clean page yields zero S0/S1 and a green `gate/4-edge`.
- Nightly run wired with dry-run Linear issue creation shown; `docs/quality/edge-cases.md`; CHANGELOG entry; Linear comment with matrix screenshot.

**Edge cases**

- Page without a spec: hunter posts S1 "no spec" (validator should already block) and runs only generic oracles.
- Scenario itself is flaky (network fixture timing): repeat 3 times, report only consistent failures, log flakes to `quality/flake-quarantine`.
- Huge data seeding slow: cap seeding at 20s and fall back to client-side mock via MSW for `data.huge`.
- Destructive scenarios against shared staging: hunter only runs against the ephemeral preview with its own seeded tenant.
- Scenario plan generation returns duplicates or invalid classes: schema validation drops them and logs counts.
- Findings duplicating `quality/screenshot-annotation` overflow findings: dedupe by page and bbox overlap over 0.6.

**Dependencies**

`spec-builder/schema` and `quality/review-agents` (hard: spec shape and SDK harness). Soft: `quality/playwright-matrix` fixtures, `quality/screenshot-annotation` DOM metrics, `data-layer/api-layer` seed endpoint, `pm-linear/webhooks`. Consumed by `quality/release-train`, `quality/review-report`, `agents/eval-harness`.

**Agent**

Built by Sentinel (Edge Case Hunter sub-agent). Reviewed by Nova (realism of data scenarios) and Atlas (budget).

**Size**

L: planner, executor with nine fixture classes, oracles, repro generation and nightly mode.
