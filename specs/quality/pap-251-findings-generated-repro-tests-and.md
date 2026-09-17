---
identifier: "PAP-251"
title: "Findings, generated repro tests and nightly library run"
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
blockedBy: ["PAP-250"]
blocks: []
key: "quality/edge-case-hunter/findings-repros-nightly"
url: "https://linear.app/paperos/issue/PAP-251/findings-generated-repro-tests-and-nightly-library-run"
source: "Linear snapshot 2026-09-17T13:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T04:04:42.069Z"
model: "claude-sonnet-5"
effort: "medium"
---

# PAP-251: Findings, generated repro tests and nightly library run

**Goal**

Close the loop: publish `edgecases.json` and the PR matrix comment, generate reproducible Playwright tests for failures in a companion PR, and run the full scenario library nightly on `main` with deduplicated Linear issues for new S1 findings.

**Scope**

* In: `report()` producing `GateReport<'edgecases'>`, "Edge cases" sticky comment with the pass/fail matrix, status `gate/4-edge`, repro generator writing `apps/web/e2e/generated/<page>/<scenarioId>.spec.ts` marked `test.fixme` into an `edge-case-repros` PR against the same branch via the bot, nightly `edge-nightly.yml` over all pages with Linear issue creation through PAP-97 (dry-run first), dedupe by finding ID and with PAP-84 overflow findings by bbox overlap.
* Out: planning and execution (siblings).

**Spec**

* Findings include `repro: 'pnpm edge:run --page <id> --scenario <sid>'` and evidence refs.
* Repro test template renders the scenario steps as Playwright code with the fixture setup; lint and typecheck clean; PR body links the finding IDs.
* Nightly: all pages, full library, results to `reports/edgecases.json` on `main`, Linear issues titled `Edge case: <page> <scenario>` labelled `Bug`, assigned to the owning character via `.mailmap`; dedupe key stored in the issue body.

**Interface contract**

* Provides: `edgecases.json`, comment section, repro PR convention, nightly Linear issue template.
* Requires: siblings, `packages/contracts`, PAP-97 webhooks, PAP-48 bot, PAP-84 `vision.json` for dedupe.
* Consumers: PAP-88 certification, PAP-89 digest, PAP-110.

**Definition of done**

* PR touching an example page shows the matrix with at least 15 executed scenarios and evidence for failures (link).
* Repro PR opened for a seeded failure, passes lint and typecheck (link).
* Nightly dry run lists the Linear issues it would create (screenshot); one live creation verified and then closed by Atlas.
* `docs/quality/edge-cases.md` complete; changelog under "Quality".

**Test plan**

* Unit: report writer, repro template snapshot, dedupe.
* Integration: nightly workflow on the sandbox repo.

**Demo**

Open the PR's "Edge cases" comment, click a failed cell, copy the repro command, run it locally and see the same failure. Under two minutes.

**Edge cases**

* More than 10 failures: repro PR groups by page, caps at 10 with a list of the rest.
* Linear rate limit: batched creation, retry after 60 s.

**Dependencies**

Both sibling children (hard). Soft: PAP-97, PAP-48, PAP-84.

**Agent**

Built by Sentinel (Edge Case Hunter). Reviewed by Atlas (Linear policy).

**Size**

S.
