---
identifier: "PAP-677"
title: "Docs and spec reviewer definition: fourth Gate 2 reviewer for PRs that change specs, docs, prompts, ADRs or changelogs"
project: "quality"
projectName: "Quality Pipeline"
phase: "P1"
type: "Build"
priority: 3
surfaces: ["Developer"]
milestone: "Gates 1 and 2 on every PR"
state: "Backlog"
parent: "PAP-81"
children: []
blockedBy: ["PAP-78", "PAP-79", "PAP-239", "PAP-243", "PAP-299", "PAP-713", "PAP-714"]
blocks: ["PAP-85", "PAP-88", "PAP-241", "PAP-253"]
key: "r4/quality/docs-and-spec-reviewer"
url: "https://linear.app/paperos/issue/PAP-677/docs-and-spec-reviewer-definition-fourth-gate-2-reviewer-for-prs-that"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:20:28.909Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 2
dueDate: "2026-09-25"
cycle: null
---

# PAP-677: Docs and spec reviewer definition: fourth Gate 2 reviewer for PRs that change specs, docs, prompts, ADRs or changelogs

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Build S

**Goal**

PAP-79 ships a `docs-and-changelog` rubric and an `agent-behaviour` rubric, but PAP-81 only defines correctness, security and spec-conformance reviewers and lists non-code artefacts as out of scope, so a third of the PRs in this build (specs, docs, prompts, ADRs, memory) get no Gate 2 review. This child adds the fourth reviewer, path-filtered to those files, so Quill's and Atlas's output is reviewed like code.

**Scope**

* In: `.claude/agents/reviewers/docs-and-spec.md` (Sentinel sub-character definition), rubric embedding from PAP-79 `docs-and-changelog.md` and `agent-behaviour.md`, path filter in `review.yml`, seeded fixtures under `ops/quality/seeded-prs/docs/`, calibration cases, `docs/quality/review-agents.md` section.
* Out: the harness (PAP-243), code reviewers (PAP-244, PAP-245), the spec validator itself (PAP-115 runs in Gate 1).

**Spec**

* Trigger: PR changes files under `specs/**`, `docs/**`, `.claude/**`, `docs/adr/**`, `CHANGELOG*` or `packages/agents/prompts/**` and no `apps/**` or `packages/**` source; mixed PRs run this reviewer in addition to the three others.
* Checks: every `must` has a verifying check named beside it (Quill's rule), links resolve, ADR has status, alternatives and consequences (PAP-130 template), spec passes `pnpm spec validate` and declares states and edge cases, prompt changes keep the PAP-285 style rules (no model names, mechanism-linked limits) and the word budget, changelog entries cite PRs, memory entries carry provenance, no untrusted instruction text (PAP-299 scanner result attached).
* Output `Finding[]` with `rubricId` from `RUB-DOC-*` and `RUB-AGENT-*`, `rubricCoverage`, statuses `gate/2-docs` (added to the PAP-239 registry) and folded into `gate/2-review`; severities: broken link or failing spec S1, style S2, wording S3.
* Cost cap $1 per PR; `maxTurns: 20`; read-only tools.

**Interface contract**

* Provides: `ReviewerDefinition` `docs-and-spec`, status `gate/2-docs`, the `RUB-DOC-*` coverage report shape.
* Consumes: PAP-243 harness, PAP-79 rubrics, PAP-115 validator output, PAP-299 scanner, PAP-285 lint rules.

**Definition of done**

* Seeded PRs (dangling link, ADR without alternatives, spec missing an empty state, prompt naming a model) each caught at the mapped severity; a clean docs PR yields zero blockers.
* Calibration agreement at or above 0.8 on five docs cases added to the PAP-79 set.
* Cost under $1 average across 10 PRs; docs section written.

**Test plan**

* Unit: path filter decision table, severity mapping, coverage report writer.
* E2E: seeded docs PRs through the harness nightly with the real model; mocked SDK on PRs.

**Demo**

Open the seeded ADR PR without alternatives and read the review: S1 citing `RUB-DOC-03` with the template link; open the clean PR beside it. Under one minute.

**Edge cases**

* PR is a generated file only (`roster.json`, docs tables): reviewer posts `n/a` and passes.
* Very large doc (Blueprint rewrite): reviewer reviews the diff hunks, not the whole file, and says so.
* Prompt change without an eval run: S1 pointing at the prompt change-control rule (agents project).

**Dependencies**

Hard: PAP-243, PAP-79. Soft: PAP-115, PAP-299, PAP-285, PAP-130.

**Agent**

Builder: Sentinel (Code Reviewer) with Quill on the rubric. Reviewer: Sentinel (Edge Case Hunter).

**Size**

S: half a session.
