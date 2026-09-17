---
identifier: "PAP-64"
title: "Generate permission matrix tests from page specs covering who can see and do what on every page"
project: "identity"
projectName: "Identity, Roles & Audiences"
phase: "P1"
type: "Review"
priority: 1
surfaces: ["Developer"]
milestone: "Agent principals and enterprise"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-59", "PAP-116", "PAP-122", "PAP-229", "PAP-240"]
blocks: []
key: "identity/permission-tests"
url: "https://linear.app/paperos/issue/PAP-64/generate-permission-matrix-tests-from-page-specs-covering-who-can-see"
source: "Linear snapshot 2026-09-17T13:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T06:22:47.788Z"
---

# PAP-64: Generate permission matrix tests from page specs covering who can see and do what on every page

**Goal**

Generate, from every page spec's `access` section, an executable permission matrix at three levels: policy (`can()`), HTTP (real procedures through the API with per-audience sessions) and UI (Playwright asserting denied actions are hidden or disabled). When a policy or spec drifts, CI fails with a readable matrix diff.

**Scope**

* In: `packages/permission-tests` generator emitting Vitest and Playwright suites, fixture principals per audience, the matrix report and diff, Gate 1 and Gate 3 wiring, spec-conformance hook, docs.
* Out: the access format (PAP-116), the engine (PAP-59), manual security testing, and the policy-level assertions PAP-122 already generates (imported here as the single source; this issue adds HTTP and UI levels plus the report).

**Spec**

* Fixtures: `fixtures/principals/*.json`, one per built-in audience (PAP-55) plus app-declared ones, produced by `pnpm permissions:fixtures` from `app.spec.yaml`, each verified with `matches` to hit exactly its audience and no narrower one.
* Generator `src/generate.ts` (`pnpm permissions:test:generate`) loads `specs/**/page.spec.yaml`, converts `access` through PAP-229's adapter and writes to `generated/` (git-ignored):
  1. `unit/<page>.test.ts`: `can(fixture, action, resource)` per `(audience, action)` with resource fixtures from `specs/fixtures/resources/<entity>.json` including an `ownedBy` variant.
  2. `http/<page>.test.ts`: API on PGlite via the PAP-34 harness, tenants A and B seeded, sessions minted through PAP-240 `login-as`, each declared query and mutation called and expected 200 or 403; cross-tenant variants expect 403 or empty.
  3. `ui/<page>.spec.ts` (Playwright) for pages with `access.uiTest: true`: log in per audience, assert denied actions absent (`hiddenWhenDenied`) or disabled, using the `data-action="<name>"` attributes PAP-120 emits.
* Report `src/report.ts`: `reports/permission-matrix.md` and `.json` (pages × audiences, allow/deny cells) diffed against `docs/reports/permission-matrix.md`; the PR comment posts the diff when cells change; unexplained changes are blockers for the spec-conformance reviewer (PAP-244) unless `access.changeNote` explains them.
* CI: Gate 1 runs generation plus unit and http suites sharded by page, budget 3 minutes; UI suite runs in Gate 3. Every spec must declare `access`; missing ones fail generation with the path.

**Interface contract**

* Provides: `permission-matrix.json` (`{ pages: [{ route, audiences: Record<AudienceId, Record<action, 'allow' | 'deny'>> }] }`) consumed by PAP-244 and PAP-89; `access.uiTest` and `access.changeNote` spec keys (agreed with PAP-116); fixture principals reused by PAP-240 `testUsers`; `data-action` attribute contract with PAP-120.
* Requires: PAP-59 and PAP-229 adapter, PAP-116 format, PAP-34 harness, PAP-240 `login-as`, PAP-78 job slot, PAP-120 attributes, PAP-246 Playwright projects.

**Definition of done**

* Generator runs over current specs (auth, org, portal, console, examples) and produces passing suites; Gate 1 time increase under 90 s (numbers in PR).
* Flipping one policy in a fixture branch fails exactly the expected cells with spec path and line (CI screenshot).
* Cross-tenant HTTP tests prove denial for every mutating action on every page.
* Matrix report committed and rendered in the PR comment (screenshot at 1280); UI suite runs for portal and console pages.
* Security Auditor reviews fixture realism; Quill confirms readability; changelog under "Quality".

**Test plan**

* Unit: fixture generation hits exactly one audience; generator output snapshots for three example specs; report diff on a seeded cell change.
* Integration: http suite on PGlite with two tenants; session minting without sign-in routes.
* E2E: UI suite on `/portal/profile` and `/console/people/members` at 1280.
* Meta: generation determinism (two runs, identical files).

**Demo**

Change `access.actions.delete.audiences` on the members spec to include `customer`, run `pnpm permissions:test:generate && pnpm test --filter permission-tests`, and read the failing cell naming the spec line; revert and watch it pass. Under two minutes.

**Edge cases**

* Declared action never implemented: http test skips with a warning; PAP-122 owns the required-component check.
* Condition on data not in fixtures (`resource.status = paid`): both variants generated from the literal.
* Contradictory audience in `app.spec.yaml`: fixture generation fails with an explanation.
* Two specs share a route with different access: generator errors naming both.
* Hundreds of pages: report groups by route prefix and collapses unchanged sections.

**Dependencies**

PAP-59, PAP-116, PAP-240 (hard). Soft: PAP-34, PAP-78, PAP-120, PAP-122, PAP-246.

**Agent**

Sentinel (Security Auditor designs the matrix; Code Reviewer implements) with Forge on the API harness. Reviewed by Forge and Quill; Atlas approves the gate timing.

**Size**

M.
