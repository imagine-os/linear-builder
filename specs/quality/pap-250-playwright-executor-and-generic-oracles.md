---
identifier: "PAP-250"
title: "Playwright executor and generic oracles"
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
blockedBy: ["PAP-240", "PAP-249"]
blocks: ["PAP-251"]
key: "quality/edge-case-hunter/executor-oracles"
url: "https://linear.app/paperos/issue/PAP-250/playwright-executor-and-generic-oracles"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T13:56:18.234Z"
model: "claude-sonnet-5"
effort: "high"
estimate: 3
dueDate: "2026-09-26"
cycle: null
---

# PAP-250: Playwright executor and generic oracles

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / high — Build M

**Goal**

Execute a scenario plan deterministically with Playwright: fixtures for every scenario class, generic oracles that decide pass or fail without page-specific code, and evidence capture.

**Scope**

* In: `runScenarios(plan)` with fixture implementations (route interception for network, CDP CPU throttling, clock control, seeded data via test mode, auth via `loginAs`, double-submit and stale-write helpers), oracle set (no unhandled exception, no console error, no spinner over 10 s, declared states render, no overflow via DOM metrics, form errors announced, data survives reload), evidence capture (screenshot or video per failure), two-shard run at `sm-375` and `xl-1280`.
* Out: planning (sibling), reporting and repros (sibling).

**Spec**

* Fixtures: `network.slow3g` = 400 ms latency and 400 kbps via `route`; `network.flaky` aborts 20 percent of requests deterministically by hash; `device.slowCpu` = `Emulation.setCPUThrottlingRate 6`; `data.huge` seeds 10k rows or falls back to MSW mocks after 20 s; `time.*` via `page.clock` and the test-mode `clock` route.
* Oracles are pure functions over `{ page, console, network, domMetrics, spec }` returning `Finding[]` in the contracts shape with `severityIfFails` from the plan.
* Flaky scenario rule: repeat failures 3 times, report only consistent ones, log flakes to PAP-90's delta format.
* Budget: execution under 8 minutes per PR across 2 shards; deferred scenarios listed.

**Interface contract**

* Provides: `runScenarios()`, `Oracle` interface, fixture registry, `reports/edgecases.raw.json`.
* Requires: sibling planner, PAP-82 matrix fixtures and DOM metrics (PAP-84 emits them), test-mode seed, `loginAs`.

**Definition of done**

* Seeded defects (unhandled empty list, crash on emoji name, missing offline state, double submit creating duplicates) each fail the correct oracle with evidence.
* Clean example page yields zero S0/S1.
* Fixture determinism: same plan twice gives identical outcomes (test).
* Docs section "Executor and oracles".

**Test plan**

* Unit: each oracle on synthetic inputs; flaky request hashing.
* Integration: seeded defect pages in the example app.
* Perf: budget check on the two-shard run.

**Demo**

`pnpm edge:run --page customer-list --scenario data.unicode-1` against the dev app and watch the emoji-name crash reproduce with a screenshot in `reports/`. Under two minutes.

**Edge cases**

* Destructive scenario on shared staging: refused; executor only targets ephemeral previews.
* Huge seeding too slow: MSW fallback flagged in the finding.

**Dependencies**

Sibling planner child (hard), test-mode seed issue (hard). Soft: PAP-82, PAP-84.

**Agent**

Built by Sentinel (Edge Case Hunter). Reviewed by Forge (fixtures) and Nova.

**Size**

M.
