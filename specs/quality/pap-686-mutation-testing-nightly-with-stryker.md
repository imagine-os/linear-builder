---
identifier: "PAP-686"
title: "Mutation testing nightly with Stryker on `packages/core`, `packages/permissions` and `packages/finance`: mutation score floor and survivors as S2 findings"
project: "quality"
projectName: "Quality Pipeline"
phase: "P2"
type: "Infra"
priority: 4
surfaces: ["Developer"]
milestone: "Edge-case hunting and release trains"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-78", "PAP-681"]
blocks: []
key: "r4/quality/mutation-testing-nightly"
url: "https://linear.app/paperos/issue/PAP-686/mutation-testing-nightly-with-stryker-on-packagescore"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:26.865Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 2
dueDate: null
cycle: null
---

# PAP-686: Mutation testing nightly with Stryker on `packages/core`, `packages/permissions` and `packages/finance`: mutation score floor and survivors as S2 findings

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Infra S

**Goal**

Deferred to v0.2 by round 4 (not claimable before 2026-10-01; NJ-14 can reinstate). Coverage says a line ran, not that a test would notice it breaking. For the three packages where a silent bug costs most (shared core types and filters, the permission evaluator, the ledger), a nightly Stryker run reports the mutation score and lists surviving mutants as S2 findings for the owning character.

**Scope**

* In: `stryker.config.mjs` per target package, nightly job `mutation.yml` (Sunday and on label `mutation`), `reports/mutation.json` (`GateReport<'mutation'>` kind), survivors mapped to `Finding[]` with file and line, score floor in `ops/quality/budgets.yaml`, `docs/quality/mutation.md`.
* Out: mutation testing of UI packages, running on every PR, fixing the surviving mutants.

**Spec**

* `@stryker-mutator/core` with the Vitest runner, `incremental: true` and the incremental file cached between nights; mutators default set minus `StringLiteral` on message catalogues; `concurrency: 4`; per-package time box 40 minutes.
* Floor: `packages/permissions` 85, `packages/finance` 80, `packages/core` 75 mutation score; below floor opens one Linear issue for the owner (PAP-305 `ownership.json`) deduped per package; survivors above floor listed as S2 in the report only.
* `reports/mutation.json` `data.packages: [{ name, score, killed, survived, timeout, noCoverage, survivors: [{ file, line, mutator }] }]`; Pages HTML report at `/nightly/<date>/mutation/`.
* Label `mutation` on a PR runs the incremental set for changed files only, informational.

**Interface contract**

* Provides: `reports/mutation.json`, workflow `mutation.yml`, floor entries in `budgets.yaml`, HTML report URL.
* Consumes: PAP-78 Vitest setup and Turbo tasks, diff coverage job for the changed-file set, PAP-305 ownership, PAP-239 schema.

**Definition of done**

* Three packages scored on three consecutive Sundays; report page linked from the digest appendix.
* Seeded weak test (asserting only truthiness) leaves a surviving mutant listed with file and line (link).
* Floor breach opens the owner issue once (test); docs; changelog under "Quality".

**Test plan**

* Unit: report mapping, floor comparison, dedupe of owner issues.
* E2E: nightly run on staging runners with the incremental cache verified to shorten the second run.

**Demo**

Open the Sunday mutation report: scores per package and the survivor list; click a survivor to its line in the forge. Under one minute.

**Edge cases**

* Run exceeds the time box: partial score reported with `timeout: true`, never a fake floor pass.
* Equivalent mutants: `// Stryker disable next-line <mutator>: <reason>` with the same expiry grammar as other suppressions.
* Package split or renamed: config keyed by `ownership.json` entries.

**Dependencies**

Hard: PAP-78, PAP-681. Soft: PAP-305, PAP-239.

**Agent**

Builder: Sentinel (Edge Case Hunter). Reviewer: Sentinel (Code Reviewer).

**Size**

S: half a session.

*Round 4 critique fix (2026-09-18):* resolved 1 round-4 file key in this description to Linear identifiers: `r4/quality/diff-coverage-gate` = PAP-681.
