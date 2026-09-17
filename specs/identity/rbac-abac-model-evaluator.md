---
identifier: "PAP-227"
title: "Policy model, evaluator and explain mode"
project: "identity"
projectName: "Identity, Roles & Audiences"
phase: "P0"
type: "Build"
priority: 1
surfaces: ["Developer"]
milestone: "Auth works across web and desktop"
state: "Backlog"
parent: "PAP-59"
children: []
blockedBy: ["PAP-279", "PAP-55"]
blocks: ["PAP-228", "PAP-229"]
key: "identity/rbac-abac/model-evaluator"
url: "https://linear.app/paperos/issue/PAP-227/policy-model-evaluator-and-explain-mode"
source: "Linear snapshot 2026-09-17T06:03Z (round-2 issue)"
---

# PAP-227: Policy model, evaluator and explain mode

**Goal**

Define the policy language and the in-memory `can()` evaluator that every other layer must agree with: deny-wins, explainable, benchmarked, fully covered.

**Scope**

* In: `packages/permissions/src/model.ts` (Zod), `evaluate.ts`, `builtin-policies.ts` for the five roles, `explain()`, CLI `pnpm permissions explain`, fixtures for the built-in audiences, `tinybench` benchmark.
* Out: SQL compilation, spec adapter, middleware, hook (siblings).

**Spec**

* `Policy = { id, effect: 'allow' | 'deny', audiences: AudienceId[], actions: Action[], resource: ResourceType | '*', condition?: Condition, global?: boolean, source: { specPath, line } }`; `Action` grammar `<entity>.<verb>` with verbs `read | list | create | update | delete | export | share | impersonate | manage`, plus `page.view` and `page.action:<name>`.
* `Condition = { all } | { any } | { not } | { path, op: eq|neq|in|contains|gte|lte|isNull, ref? | value? }`; paths rooted at `resource.` or `actor.`; depth limit 8.
* `can(actor: Principal, action, resource, ctx) => Decision { allowed, matched, explain() }`; audiences resolved with `matches()` from PAP-55; order: any matching deny wins, else any allow, else deny.
* Built-in policies: owner and admin `*.manage`; staff read/list/create/update on resources tagged `staff`; member scoped read; viewer read only.
* Benchmark: median under 20 µs with 200 policies; test fails above 100 µs.

**Interface contract**

* Provides: types `Policy`, `Action`, `Condition`, `Decision`, `ResourceRef`; `can()`, `explain()`, `BUILTIN_POLICIES`, `parseAction()`.
* Requires: PAP-55 `Principal`, `AudienceId`, `matches()`.
* Consumers: siblings, PAP-60 `withScopes()`, PAP-64 tests, PAP-178 entitlements.

**Definition of done**

* 100 percent branch coverage of `evaluate.ts`; property test (`fast-check`) that adding a deny never increases allowed outcomes.
* Benchmark numbers in the PR.
* `pnpm permissions explain --actor fixtures/staff-support.json --action invoice.update --resource invoice:123` prints matched policies with spec path and line.
* `docs/platform/permissions.md` sections "Model" and "Algorithm".

**Test plan**

* Unit: every op, arrays with `contains`, `isNull`, unknown path returns false not throw, depth limit error.
* Property: 10 000 random policy sets, deny-wins invariant, determinism.
* Bench: `tinybench` run in CI as informational, threshold as a test.

**Demo**

Run the explain CLI for three fixtures (customer, support, agent) against `invoice.update` and read the three verdicts with their sources. Under one minute.

**Edge cases**

* Policy referencing an undeclared audience: load-time validation error with path.
* Resource with `tenantId` null: matches only `global: true` policies.
* Condition comparing two actor paths: allowed, documented.

**Dependencies**

PAP-55 (hard). Blocks the two sibling children.

**Agent**

Built by Forge (lead). Reviewed by Sentinel (Security Auditor, Edge Case Hunter).

**Size**

M.
