---
identifier: "PAP-678"
title: "Create the quality sandbox repo `imagine-os/paperos-qa-sandbox` with the seeded-defect catalogue every gate's Definition of done rehearses against"
project: "quality"
projectName: "Quality Pipeline"
phase: "P0"
type: "Infra"
priority: 1
surfaces: ["Developer"]
milestone: "Gates 1 and 2 on every PR"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-13", "PAP-51", "PAP-526"]
blocks: ["PAP-90", "PAP-243", "PAP-244", "PAP-245", "PAP-246", "PAP-251", "PAP-254"]
key: "r4/quality/quality-sandbox-repo-and-seeded-defects"
url: "https://linear.app/paperos/issue/PAP-678/create-the-quality-sandbox-repo-imagine-ospaperos-qa-sandbox-with-the"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:20:27.865Z"
model: "claude-opus-5"
effort: "high"
estimate: 2
dueDate: "2026-09-25"
cycle: null
---

# PAP-678: Create the quality sandbox repo `imagine-os/paperos-qa-sandbox` with the seeded-defect catalogue every gate's Definition of done rehearses against

**Model / Effort:** Opus 5 (`claude-opus-5`) / high — Infra S

**Goal**

Eleven quality specs (PAP-81, 90, 241, 243, 244, 245, 246, 251, 254, 306, 308 and the new security suite) prove themselves on "the sandbox repo" and on seeded PRs, and no issue creates either. This issue provisions `imagine-os/paperos-qa-sandbox` from the template with `forge bootstrap`, mirrors it on Forgejo, and commits a catalogue of seeded defects as branches so every gate has the same deterministic thing to catch.

**Scope**

* In: repo `imagine-os/paperos-qa-sandbox` created from `paperos-template` (PAP-13) via `forge bootstrap` (PAP-51) with mirror, CI and labels; `ops/quality/seeded-defects.yaml` (catalogue) and one branch `seed/<id>` per defect; `pnpm qa:seed --open <id>` opening the seeded PR idempotently; `docs/quality/sandbox.md`; a `rehearsal` label on the repo.
* Out: the gates themselves; fixture data for tests (PAP-240); the eval fixture repos (PAP-309 pins the template SHA).

**Spec**

* Catalogue entry `{ id, gate: 1|2|3|4|security|flake|release, branch, description, expected: { reviewer, severity, rubricId?, oracle? }, owner }`; initial set: Gate 1 type error, lint error, failing test, bad commit message, drifted generated file (PAP-78); Gate 2 authz bug, null-handling bug, missing empty state, off-by-one pagination, unwired event, cross-tenant query (PAP-244, PAP-245); Gate 3 2 px Button padding, portal heading colour (PAP-82); vision 375 px overflow, low-contrast dark badge (PAP-84); Gate 4 unhandled empty list, emoji-name crash, missing offline state, double submit (PAP-85); security fake AWS key, `lodash@4.17.15`, `dangerouslySetInnerHTML`, procedure without `authorize` (PAP-80); flaky test with 30 percent random failure (PAP-90); perf 300 KB import on the dashboard (PAP-87); release missing status and `testMode: true` (PAP-254).
* `pnpm qa:seed --open <id>` rebases the seed branch on `main`, opens or updates one PR titled `seed(<gate>): <id>` labelled `rehearsal` and `seed:<id>`, and posts the expected findings as a PR comment for the calibration diff; `--close-all` closes seeds after a rehearsal.
* The repo runs the same `ci.yml` as the template; secrets are the bot's (PAP-48); nightly `qa:seed --open --all` keeps the seeds rebased so gates can rehearse any morning.
* Catalogue is validated in CI; every entry's `expected` references a rubric id that exists (PAP-79).

**Interface contract**

* Provides: repo and mirror, `seeded-defects.yaml` schema and catalogue, `pnpm qa:seed`, label `rehearsal`, the `seed:<id>` label grammar consumed by PAP-241 calibration and PAP-310 evals.
* Consumes: PAP-13 template, PAP-51 bootstrap, PAP-48 bot, PAP-79 rubric ids; the gate issues consume the seeds.

**Definition of done**

* Repo exists on both forges with CI green on `main`; `forge bootstrap` output attached.
* Catalogue with at least 24 seeds validates; every branch rebases cleanly and `qa:seed --open` opens 24 PRs then `--close-all` closes them (recording).
* PAP-78 seeded failures each turn Gate 1 red on their PR (links), proving the seeds work before Gate 2 exists.
* Docs page; changelog under "Quality"; Linear comment with the catalogue table.

**Test plan**

* Unit: catalogue schema, branch naming, idempotent PR open and update.
* E2E: open, rebase and close cycle on the live sandbox repo.

**Demo**

Run `pnpm qa:seed --open gate2-authz`, open the PR, read the expected-findings comment, then watch Gate 1 stay green and (once PAP-245 lands) the security reviewer post the S0. Under two minutes.

**Edge cases**

* Template moves fast and seeds stop rebasing: nightly job opens a `seed-rot` issue listing the branches that failed to rebase.
* A seed becomes a real bug in the template: the catalogue marks it `promoted` with the fixing PR and the seed is regenerated.
* Fork PR semantics: seeds are same-repo branches so secrets are available; a separate `fork/` seed exercises the no-secrets path once.
* Repo used for evals by mistake: PAP-309 pins fixtures to template tarballs, never this repo.

**Dependencies**

Hard: PAP-13, PAP-51. Soft: PAP-48, PAP-79, PAP-46.

**Agent**

Builder: Forge (Ops Runner) with Sentinel (Code Reviewer) on the catalogue. Reviewer: Sentinel (Code Reviewer).

**Size**

S: half a session.
