---
identifier: "PAP-681"
title: "Diff coverage gate: per-PR patch coverage from Vitest `lcov`, 80 percent floor on changed lines, uncovered-line annotations and a coverage delta in the sticky comment"
project: "quality"
projectName: "Quality Pipeline"
phase: "P1"
type: "Infra"
priority: 3
surfaces: ["Developer"]
milestone: "Gates 1 and 2 on every PR"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-78"]
blocks: ["PAP-686"]
key: "r4/quality/diff-coverage-gate"
url: "https://linear.app/paperos/issue/PAP-681/diff-coverage-gate-per-pr-patch-coverage-from-vitest-lcov-80-percent"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:20:27.501Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 2
dueDate: "2026-09-25"
cycle: null
---

# PAP-681: Diff coverage gate: per-PR patch coverage from Vitest `lcov`, 80 percent floor on changed lines, uncovered-line annotations and a coverage delta in the sticky comment

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Infra S

**Goal**

PAP-78 enforces a 70 percent lines floor per package, which lets a PR add 400 untested lines to a well-covered package. Agent-written code needs the Codecov-style check: coverage of the lines this PR changed, annotated inline, with the delta against `main`, so reviewers and Gate 2 can see what was never executed.

**Scope**

* In: `ops/ci/coverage/diff-cover.ts` (parses merged `lcov.info` and `git diff -U0 origin/main`), Gate 1 job `coverage` after `test`, `reports/coverage.json` as a `GateReport<'coverage'>` kind added to PAP-239, inline `::warning` annotations on uncovered changed lines, "Coverage" section in the sticky comment, `ops/ci/coverage.budget.json`.
* Out: raising package floors, mutation testing (own issue), e2e coverage instrumentation.

**Spec**

* Vitest runs with `coverage.reporter: ['lcov', 'json-summary']` per package (Turbo task outputs); the job merges `lcov.info` files, maps paths to the repo root and intersects with changed lines from `git diff -U0 --diff-filter=AM origin/main...HEAD`.
* Patch coverage = covered changed lines / coverable changed lines; floor 80 percent (`budget.json`, per-path overrides for `**/*.stories.tsx`, generated files and `ops/**` at 0); below the floor the job fails with S1; between 80 and 90 percent warns.
* Delta: total coverage of `main` fetched from the last `main` run artefact; comment shows `patch 84% (floor 80) | total 71.2% (+0.3)`.
* Annotations: `::warning file=<path>,line=<n>::uncovered changed line` capped at 50 per PR with a count of the rest; Gate 2 correctness reviewer receives `coverage.json` in its context (PAP-243 assembler) so it can cite untested branches.
* Docs-only and generated-only PRs skip the job with `status: skipped`.

**Interface contract**

* Provides: `reports/coverage.json`, status `gate/1-coverage` (registry addition), comment section, `coverage.budget.json` schema, `diff-cover.ts` reusable by PAP-242 for API packages.
* Consumes: PAP-78 `test` job artefacts and sticky comment, PAP-239 schema, PAP-243 context assembler (soft).

**Definition of done**

* Seeded PR adding 40 untested lines fails at 0 percent patch coverage with annotations (link); adding tests turns it green (link).
* `main` delta computed on three consecutive PRs; missing baseline degrades to patch-only with a note.
* Job under 30 s on top of `test`; docs section; changelog under "Quality".

**Test plan**

* Unit: lcov merge and path mapping, diff hunk parsing with renames, floor and override matching, delta math.
* E2E: sandbox seeded PR; docs-only PR skips.

**Demo**

Open the seeded PR's "Coverage" section: patch 0 percent in red, click an inline warning on an uncovered line, push a test and watch it turn green. Under one minute.

**Edge cases**

* Renamed file: `--diff-filter=AM` plus rename detection maps old lines correctly; pure renames coverable lines zero.
* Coverage instrumentation breaks a package (ESM edge): package opts out in `budget.json` with a reason and expiry.
* Monorepo path aliases in lcov: normalised through the Vite config `root`.
* PR touching only `*.d.ts`: zero coverable lines, `skipped`.

**Dependencies**

Hard: PAP-78. Soft: PAP-239, PAP-243.

**Agent**

Builder: Forge (Ops Runner) with Sentinel (Code Reviewer). Reviewer: Sentinel (Code Reviewer).

**Size**

S: half a session.
