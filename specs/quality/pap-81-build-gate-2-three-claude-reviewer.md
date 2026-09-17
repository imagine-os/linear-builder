---
identifier: "PAP-81"
title: "Build gate 2: three Claude reviewer agents (correctness, security, spec-conformance) posting structured PR reviews"
project: "quality"
projectName: "Quality Pipeline"
phase: "P0"
type: "Build"
priority: 1
surfaces: ["Agent", "Developer"]
milestone: "Gates 1 and 2 on every PR"
state: "Backlog"
parent: null
children: ["PAP-243", "PAP-244", "PAP-245"]
blockedBy: ["PAP-78", "PAP-79", "PAP-239", "PAP-299"]
blocks: ["PAP-85", "PAP-88", "PAP-241", "PAP-253"]
key: "quality/review-agents"
url: "https://linear.app/paperos/issue/PAP-81/build-gate-2-three-claude-reviewer-agents-correctness-security-spec"
source: "Linear snapshot 2026-09-17T15:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T14:54:17.309Z"
model: null
effort: null
---

# PAP-81: Build gate 2: three Claude reviewer agents (correctness, security, spec-conformance) posting structured PR reviews

**Model / Effort:** set on children (umbrella is never claimed)

**Goal**

Build Gate 2: three Claude reviewer agents (correctness, security, spec-conformance) that run after Gate 1 on every PR, review against the shared rubrics, post one structured GitHub or Forgejo review each with inline comments, and set statuses that block merge on blockers. This replaces the human code review Justin cannot supply. Umbrella for three children.

**Children**

1. PAP-243 Review harness: SDK runner, input assembly, finding validation and posting (M) - blocks the other two.
2. PAP-244 Correctness and spec-conformance reviewer definitions (M).
3. PAP-245 Security reviewer definition and `security.json` ingestion (S).

**Scope**

* In (across children): `packages/agents/src/review/`, three reviewer definitions under `.claude/agents/reviewers/`, `review.yml` workflow, posting to both forges, idempotent re-review, cost capture, calibration.
* Out: autofix PRs, non-code artifacts, human review UI, ongoing calibration measurement (PAP-241), vision review (PAP-84).

**Spec**

Details live in the children. Cross-child rules:

* Reviewers never `APPROVE`; `REQUEST_CHANGES` on any S0 or more than 3 S1, else `COMMENT`; aggregate `gate/2-review` is the merge gate.
* All findings are `packages/contracts` `Finding`s with deterministic IDs; inline comments carry `<!-- finding:<id> -->` so re-runs update instead of duplicate.
* Tools are read-only; any write or network attempt is denied and logged as an S2 agent-behaviour finding.
* Every reviewer emits `rubricCoverage` so silence is distinguishable from a skipped check.

**Interface contract**

* Provides: `runReview()`, `ReviewerDefinition`, `postReview()`; statuses `gate/2-correctness`, `gate/2-security`, `gate/2-spec`, `gate/2-review`; `reports/review-cost.json`; label `re-review` trigger; the review comment format from PAP-79.
* Requires: PAP-78 `workflow_run` and `gate1.json`, PAP-79 rubrics and calibration set, PAP-239 schemas, PAP-80 `security.json`, PAP-48 bot identities, PAP-49 PR template fields, PAP-74 `registry.json` and PAP-76 `rules.json` (soft), PAP-107 prompt-log hook (soft).
* Consumers: PAP-85 (reuses the harness), PAP-84 (runner with image input), PAP-88 certification, PAP-241 calibration, PAP-110 evals, PAP-89.
* Contract source: [Interface & Data Contracts](<https://linear.app/paperos/document/paperos-interface-and-data-contracts-d40e6a4d227c>) §5 (`packages/contracts` is owned by quality through PAP-239: every `reports/*.json` named above is a `GateReport<kind>` validated by `validateArtifact()`, JSON Schema generated from Zod 4 per §1); §3 (gate results reach the bus as `review.gate_failed` and `review.ready` through PAP-97; artifact `version` bumps keep a reader for 30 days); §6 row "Gate artifacts" (provider PAP-239; consumers PAP-78 to PAP-90, PAP-97, PAP-137, PAP-110). Until PAP-239 merges, write the shape exactly as its Interface contract states and import the schema when it lands. Also [Security & Threat Model](<https://linear.app/paperos/document/paperos-security-and-threat-model-51fd5fd8929c>) §6 (PR diffs, fork PRs and imported documents are T3 and are wrapped in `<untrusted source= tier=>` blocks; only the orchestrator's rendered prompt and Justin's comments instruct the reviewer) and §3 (the security reviewer checks the STRIDE rows and PAP-219 `controls.yaml`, reading PAP-80 `security.json` as its baseline).

**Definition of done**

* All three children Done.
* Integration test below green on the sandbox repo; example review links and a cost table in the Linear comment.
* `docs/quality/review-agents.md` (how to read, re-run, waive); changelog entry.

**Test plan**

Umbrella run on the sandbox repo:

* Seeded PR containing an authz bug, a null-handling bug and a missing empty state: security catches the first at S0, correctness the second at S1, spec-conformance the third at S1; a clean PR yields `COMMENT` with zero blockers and green statuses.
* Push a fix commit: fixed findings get "Resolved in <sha>", no duplicate comments, incremental diff reviewed.
* Calibration: all three reviewers at or above 0.8 agreement on the 15-case set.
* Cost: under $6 average per PR across 10 PRs; each reviewer under 6 minutes, gate under 10.
* Posting works on GitHub and on the Forgejo dev instance.

**Demo**

Open the seeded PR: three reviews, inline comments with rubric ids and suggestion diffs, red `gate/2-review`; open the clean PR beside it with green statuses and the cost line in the job summary. Under one minute.

**Edge cases**

Cross-child: PR over 10 000 lines gets one S1 "split this PR" and a spec-plus-security-only review; API outage yields `status: error` never green; a reviewer contradicting `gate1.json` must cite command output or is downgraded; Sentinel's own PRs are still reviewed.

**Dependencies**

PAP-78, PAP-79, PAP-239 (hard). Soft: PAP-80, PAP-48, PAP-49, PAP-74, PAP-76, PAP-107.

**Agent**

Sentinel (Code Reviewer and Security Auditor write their own prompts) with Atlas providing the SDK harness pattern shared with PAP-96. Reviewed by Atlas and Forge; Quill checks the spec-conformance prompt.

**Size**

L, split into 3 children (M, M, S).

**Module boundary**

This umbrella is the Quality Pipeline half of the PaperOS Module System (`docs/module-system.md`). The `quality` module implements `@paperos/contract-quality` (gate artefact schemas, finding and severity taxonomy, gate runner, RC manifest, test seed port). Reviewers, the orchestrator and the digest read artefacts only through these schemas; the module may import `@paperos/core`, `@paperos/contract-forge`, `@paperos/contract-pm-linear` and its own packages. Its manifest declares `provides: [{ contract: '@paperos/contract-quality', version: '0.1.0' }]`, `owner: { agent: 'Sentinel', project: 'quality' }` and `swapRisk: 'medium'`. The contract package is published by `PAP-462`, proven by `PAP-463` and bound into `@paperos/kernel` by `PAP-464`; children of this issue inherit this boundary and may not add a dependency the manifest does not declare (lint rules R7 to R11).
