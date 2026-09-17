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
blockedBy: ["PAP-115", "PAP-240", "PAP-78"]
blocks: ["PAP-64"]
key: "spec-builder/conformance-tests"
url: "https://linear.app/paperos/issue/PAP-122/generate-conformance-tests-from-specs-access-matrix-required"
source: "plan/specs/bucket-4.json (round-1 canonical spec JSON)"
---

# PAP-122: Generate conformance tests from specs (access matrix, required components, states) into CI gate 1

**Goal**

Derive tests from specs automatically so a page that drifts from its spec fails gate 1 without anyone writing a test: the access matrix is checked against the permission engine, required components and states are asserted in a render, and edge cases become tracked test stubs. Spec drift becomes a red build, not a review comment.

**Scope**

In:
- `pnpm spec gen:tests [id] [--all]` in `packages/spec/src/codegen/tests.ts` writing `apps/web/src/generated/__tests__/<id>.conformance.test.tsx` (Vitest 3 + Testing Library 16, jsdom) and `apps/web/e2e/generated/<id>.routes.spec.ts` (Playwright).
- Unit-level assertions per page: (a) render `<Id View>` with mocked data hooks for every entry of `states` and assert the state component and copy appear; (b) every `components[].key` with `data-spec-key` is present in the success state; (c) every `events[].to` route exists in `routeTree.gen.ts`; (d) access matrix: for each audience in `app.spec.yaml` and each of `page.view` plus `page.action:<name>`, call `can(actorFixture(audience), action, page)` from `identity/rbac-abac` with policies from `spec-builder/access-section` and assert the expected boolean from the compiled matrix; (e) each `edgeCases[]` with `test: unit` becomes `it.todo('<id>: <scenario>')` unless a file `apps/web/src/pages/<id>.edge.test.tsx` exports a test with that id, in which case it is imported.
- Playwright: for each audience, log in via the shared fixture from `quality/playwright-matrix`, visit the route, expect 200 and the page `h1` when allowed, or the denied state when not; `test: e2e` edge cases become `test.fixme`.
- Runs inside the `test` job of `quality/ci-gate1`; JUnit output tagged `suite=conformance`; `generated-drift` fails when spec hash in the banner differs.
- Coverage report `reports/spec-conformance.json` `{ pages, statesCovered, actionsCovered, edgeCasesImplemented, todo }` posted by `pm-linear/webhooks` into the Linear comment.

Out: writing real edge-case implementations, visual checks (gate 3), permission tests for non-page resources (`identity/permission-tests`).

**Spec**

- Actor fixtures come from `packages/permissions/fixtures/<audience>.json`, generated from `app.spec.yaml` audiences with attributes filled from `segment`.
- Data hooks are mocked with `vi.mock('../generated/<id>.data')` returning state-specific values (`status: 'pending'`, empty array, `error`).
- Denied state test also asserts no data hook was called (no data leakage on denied pages).
- Generated test files are not edited by hand; page-specific tests live beside the logic file.
- `it.todo` count per page is tracked; a page may not move to `status: built` with more than zero todos of `test: unit` (validator rule `SPEC_EDGE_TODO`).

**Definition of done**

- Vitest snapshots of generated tests for minimal and maximal fixtures; a mutated spec (removed component, changed audience) makes the generated test fail (demonstrated in CI with a seeded PR).
- Three example pages produce green conformance suites; total runtime under 20 s.
- Playwright route suite runs for two audiences per page in the matrix at 375 and 1280.
- `reports/spec-conformance.json` appears in a Linear comment through the webhook pipeline.
- `docs/spec/conformance.md`; CHANGELOG entry; Linear comment with green and red run links.

**Edge cases**

- Page with `public: true`: anonymous actor fixture used; login skipped in Playwright.
- Component conditionally rendered by logic (only when data exists): mark `optional: true` in the spec to exclude it from the presence assertion.
- Access condition depends on resource attributes (`resource.status`): matrix evaluates with a representative fixture per condition branch, both true and false.
- Hundreds of pages: generated Vitest sharded by the CI matrix; each file independent.
- Spec `status: draft`: tests generated but skipped with `describe.skip` and a reason, so drafts do not block gate 1.
- Edge-case id renamed: the imported test no longer matches and becomes a todo; validator warns about orphaned edge tests.

**Dependencies**

`spec-builder/validator` (hard), `quality/ci-gate1` (hard, test job and drift). `spec-builder/access-section` and `identity/rbac-abac` for the matrix; `spec-builder/layout-codegen` for `data-spec-key`; `quality/playwright-matrix` for login fixtures. Consumed by `quality/review-agents` spec-conformance reviewer.

**Agent**

Built by Sentinel (Code Reviewer sub-agent as builder) with Quill on spec semantics. Reviewed by Nova and Sentinel (Security Auditor for matrix correctness).

**Size**

M: generation is mechanical; the access matrix and fixtures need rigour.
