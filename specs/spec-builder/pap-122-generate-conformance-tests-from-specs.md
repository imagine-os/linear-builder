---
identifier: "PAP-122"
title: "Generate conformance tests from specs (access matrix, required components, states) into CI gate 1"
project: "spec-builder"
projectName: "Spec Builder"
phase: "P1"
type: "Build"
priority: 1
surfaces: ["Developer"]
milestone: "Codegen and conformance tests"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-78", "PAP-115", "PAP-240"]
blocks: ["PAP-64", "PAP-362"]
key: "spec-builder/conformance-tests"
url: "https://linear.app/paperos/issue/PAP-122/generate-conformance-tests-from-specs-access-matrix-required"
source: "Linear snapshot 2026-09-17T13:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T04:50:47.792Z"
---

# PAP-122: Generate conformance tests from specs (access matrix, required components, states) into CI gate 1

**Goal**

Derive tests from specs automatically so a page that drifts from its spec fails gate 1 without anyone writing a test: the access matrix is checked against the permission engine, required components and states are asserted in a render, routes are verified and edge cases become tracked stubs. Spec drift becomes a red build, not a review comment.

**Scope**

* In: `pnpm spec gen:tests [id] [--all]` writing Vitest conformance files and Playwright route suites, actor fixtures, `reports/spec-conformance.json`, `docs/spec/conformance.md`.
* Out: hand-written page tests (live beside the logic file), visual baselines (PAP-82), reviewer prompts (PAP-81).

**Spec**

* Unit file `apps/web/src/generated/__tests__/<id>.conformance.test.tsx` (Vitest 3, Testing Library 16, jsdom): render the view for every `states` entry with mocked hooks and assert the state component and copy; assert every `components[].key` via `data-spec-key` in the success state (unless `optional: true`); assert every `events[].to` exists in `routeTree.gen.ts`; access matrix from PAP-116 `accessMatrix` evaluated with PAP-59 `can()` for every audience and action; denied state asserts no data hook call; `edgeCases[]` with `test: unit` become `it.todo` or import a named test from `pages/<id>.edge.test.ts`.
* Playwright file `apps/web/e2e/generated/<id>.routes.spec.ts`: for two audiences per page, log in via PAP-240 `login-as`, load the route at 375 and 1280 px, assert the success or denied state.
* Actor fixtures `packages/permissions/fixtures/<audience>.json` generated from the app spec; hooks mocked with `vi.mock('../generated/<id>.data')`.
* `status: draft` pages generate `describe.skip` with a reason; `SPEC_EDGE_TODO` blocks `status: built` with open unit todos.

**Interface contract**

* Provides: `pnpm spec gen:tests`, generated files (never hand-edited), `reports/spec-conformance.json` (`{ pages: [{ id, passed, failed, todos, matrixChecks }] }`) uploaded as a gate artifact per PAP-239, the `pages/<id>.edge.test.ts` naming convention for imported edge tests.
* Consumers: PAP-78 gate 1 test job, PAP-97 status comment (conformance section), PAP-81 spec-conformance reviewer, PAP-64 (matrix checks feed its report), PAP-125 examples, PAP-102 and PAP-113 page specs.
* Requires: PAP-115 report, PAP-78 job and drift, PAP-116 matrix, PAP-59 `can()`, PAP-120 `data-spec-key`, PAP-240 login fixtures, PAP-239 artifact schema.

**Definition of done**

* Snapshots of generated tests for minimal and maximal fixtures; a mutated spec (removed component, changed audience) makes the generated test fail in a seeded PR.
* Three example pages produce green suites; total under 20 s.
* Playwright route suite runs for two audiences per page at 375 and 1280 px.
* `reports/spec-conformance.json` appears in a Linear status comment; docs; changelog; Linear comment with green and red run links.

**Test plan**

* Unit: generator snapshots; matrix evaluation both branches of resource conditions; optional components; draft skip.
* Integration: run generated suites for the examples in CI; sharding across the matrix.
* e2e: generated Playwright suites at 375 and 1280 px against test-mode seeds.
* Visual: none beyond the route suite's success and denied screenshots.

**Demo**

Remove the `invoiceTable` component from the example spec's `components`, run `pnpm spec gen:tests customer-invoices && pnpm vitest run customer-invoices`: the presence assertion fails naming the key; restore and rerun green. One minute.

**Edge cases**

* `public: true`: anonymous fixture, login skipped.
* Conditionally rendered component: `optional: true` excludes it.
* Resource-dependent access: representative fixture per condition branch.
* Hundreds of pages: files independent, sharded.
* Edge-case id renamed: orphaned test becomes a todo with a warning.

**Dependencies**

Blocked by PAP-115, PAP-78. Uses PAP-116, PAP-59, PAP-120, PAP-240, PAP-239. Blocks PAP-64.

**Agent**

Built by Sentinel (Code Reviewer sub-agent as builder) with Quill on docs; reviewed by Atlas.

**Size**

M
