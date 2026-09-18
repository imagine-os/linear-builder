---
identifier: "PAP-545"
title: "Kernel test kit: `createTestKernel({ modules, doubles, tenant, actor })` wiring memory doubles from every contract's `conformance/memory`, `withImpl`, request-scope helpers and Vitest matchers"
project: "module-system"
projectName: "Module System & Swap Tooling"
phase: "P1"
type: "Build"
priority: 1
surfaces: ["Developer"]
milestone: "Contracts and conformance wired"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-434", "PAP-441", "PAP-537", "PAP-541"]
blocks: []
key: "r4/module-system/test-kernel"
url: "https://linear.app/paperos/issue/PAP-545/kernel-test-kit-createtestkernel-modules-doubles-tenant-actor-wiring"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:05.088Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 2
dueDate: "2026-09-27"
cycle: null
---

# PAP-545: Kernel test kit: `createTestKernel({ modules, doubles, tenant, actor })` wiring memory doubles from every contract's `conformance/memory`, `withImpl`, request-scope helpers and Vitest matchers

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Build S

**Goal**

Every module test that touches another module today either imports its implementation (forbidden by R8) or hand-rolls a fake. The contracts already ship memory doubles for conformance; a test kernel that binds them by default turns "test my module against everything else" into one line, which is what lets twenty parallel sessions test without Postgres and without each other.

**Scope**

In:

* `packages/kernel/testing.ts`: `createTestKernel({ modules?: ModuleManifest[], doubles?: Record<contract, factory>, tenant?, actor? })` that loads the manifests, binds each required contract to its `conformance/memory` double unless a real module or override is given, and returns `{ kernel, scope, resolve, emitted() }`.
* Helpers: `withImpl(kernel, token, impl)` for side-by-side tests, `asActor(scope, principal)` and `asTenant(scope, id)` building request scopes from PAP-55 fixtures, `emitted(topic)` capturing events through a memory outbox (PAP-303 envelope), `advanceFlags(kernel, { "module.x.impl": "v2" })` for swap tests.
* Vitest matchers: `toHaveEmitted(topic, payloadMatcher)`, `toResolveImpl(token, name)`.
* `docs/platform/testing.md` with the recipe and three worked examples (unit test of a consumer, side-by-side impl test, slot fill test through `KernelProvider`).

Out: the doubles themselves (per-contract conformance issues), the runner (PAP-441), Playwright fixtures (PAP-240).

**Spec**

* A missing double for a required contract fails the test kernel with `DOUBLE_MISSING <contract>` and the path where the conformance issue should add it.
* Doubles are fresh per test (no shared state) and dispose with the kernel.
* Boot of a test kernel with all eighteen doubles under 50 ms so unit suites stay fast.
* Test kernel refuses to bind a real module whose manifest declares `kind: service` without an explicit `allowServices: true` (keeps unit tests hermetic).

**Interface contract**

Provides: `createTestKernel`, helpers, matchers, the recipe doc; consumed by every `Wire <module>` issue and module unit tests, PAP-450 and siblings (real-adapter runs use `withImpl`), PAP-446 (drill rehearsal), PAP-105 `page-from-spec` skill (tests it generates), PAP-122 conformance test generator.

Consumes: kernel API and scopes (PAP-434), `conformance/memory` convention (PAP-441), principal fixtures (PAP-55), event envelope (PAP-303), flags (PAP-366, soft).

**Definition of done**

* Sample module (PAP-542) consumer test written with the kit runs without Postgres in under 100 ms; side-by-side test flips `good` to `v2` and asserts identical output.
* `DOUBLE_MISSING` path tested; doc with three examples; Linear comment.

**Test plan**

* Unit: default double binding; override precedence; scope helpers; matchers; disposal isolation across 500 tests.
* E2E: CI: `pnpm test` across the template uses the kit in at least two modules once wire issues adopt it (tracked by a grep in the DoD of those issues).

**Demo**

Reviewer opens `packages/sample/src/greet.test.ts`, sees `const { resolve } = createTestKernel({ modules: [sampleManifest] })`, runs it green in 80 ms, then swaps to `withImpl(..., "bad")` and watches the ordering assertion fail. Under a minute.

**Edge cases**

* Double behaviour diverges from the real adapter: that is a conformance failure of the double, surfaced by PAP-441 `--impl memory,real` diff, not by this kit.
* Test needs two tenants: two scopes from one kernel; RLS semantics are emulated by the doubles' tenant filter.
* React component test: `KernelProvider` from PAP-537 accepts the test kernel.

**Dependencies**

Hard: PAP-434, PAP-441. Soft: PAP-55, PAP-303, PAP-366, PAP-542, PAP-537.

**Agent**

Builder: Sentinel (Code Reviewer sub-agent as builder) with Forge. Reviewer: Sentinel (Edge Case Hunter).

**Size**

S: half a session.

*Round 4 critique fix (2026-09-18):* resolved 2 round-4 file keys in this description to Linear identifiers: `r4/module-system/kernel-integrations` = PAP-537, `r4/module-system/sample-module` = PAP-542.
