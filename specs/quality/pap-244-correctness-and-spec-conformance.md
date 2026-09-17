---
identifier: "PAP-244"
title: "Correctness and spec-conformance reviewer definitions"
project: "quality"
projectName: "Quality Pipeline"
phase: "P0"
type: "Build"
priority: 1
surfaces: ["Agent", "Developer"]
milestone: "Gates 1 and 2 on every PR"
state: "Backlog"
parent: "PAP-81"
children: []
blockedBy: ["PAP-243"]
blocks: ["PAP-85", "PAP-88", "PAP-241"]
key: "quality/review-agents/correctness-spec"
url: "https://linear.app/paperos/issue/PAP-244/correctness-and-spec-conformance-reviewer-definitions"
source: "Linear snapshot 2026-09-17T13:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T04:04:40.934Z"
---

# PAP-244: Correctness and spec-conformance reviewer definitions

**Goal**

Write and calibrate the two reviewers that judge whether the code works and whether it matches its page spec, each embedding its rubric and proving itself on seeded bugs and the calibration set.

**Scope**

* In: `.claude/agents/reviewers/correctness.md` and `spec-conformance.md` (Sentinel sub-characters), rubric embedding from PAP-79 `correctness.md` and `spec-conformance.md`, spec resolution from changed routes, seeded-bug fixtures, calibration run, docs.
* Out: harness (sibling), security reviewer (sibling).

**Spec**

* Correctness prompt: checks types versus runtime, null and empty handling, error paths, async ordering, idempotency, transactions, timezone and locale, pagination, cleanup, test presence and meaning; must run `pnpm test --filter <pkg>` for changed packages and cite output for any claim about tests.
* Spec-conformance prompt: resolves specs from changed route files and PR body; checks page has a spec, components match `registry.json` (PAP-74), access section implemented (PAP-59 adapter output), all declared states rendered, events wired, spec edge cases have tests, `rules.json` respected (PAP-76); missing Linear link is S1.
* Both output `rubricCoverage` with `checked | n/a` per rubric ID; confidence under 0.5 becomes `question`; `autofixable` findings include a suggestion diff.
* Seeded fixtures under `ops/quality/seeded-prs/`: null-handling bug, missing empty state, off-by-one pagination, unwired event.

**Interface contract**

* Provides: two `ReviewerDefinition`s registered with the harness; rubric coverage report shape.
* Requires: sibling harness; PAP-79 rubrics and calibration set; PAP-74 `registry.json`; PAP-76 `rules.json` (soft, skip when absent).

**Definition of done**

* Seeded null-handling and pagination bugs caught at S1 by correctness; seeded missing empty state and unwired event caught by spec-conformance; clean PR yields zero blockers.
* Calibration agreement at or above 0.8 for both on the 15-case set (numbers in PR).
* Cost per reviewer under $2 average across 10 PRs.
* `docs/quality/review-agents.md` sections for both reviewers.

**Test plan**

* Integration: seeded PRs through the harness in CI (nightly, mocked SDK on PRs).
* Calibration: `pnpm review:calibrate --reviewer correctness`.
* Regression: prompt changes must keep agreement above threshold (PAP-110 later).

**Demo**

Open the seeded "missing empty state" PR in the sandbox repo and read the spec-conformance review: the finding cites the spec line and `registry.json` entry. Under one minute.

**Edge cases**

* Spec absent: S1 "no spec" and generic review.
* Tests fail in Gate 1 already: reviewer references `gate1.json`, does not re-run.
* Generated files changed: capped at S2 pointing to the generator.

**Dependencies**

Sibling harness child (hard). Soft: PAP-74, PAP-76.

**Agent**

Built by Sentinel (Code Reviewer sub-agent); Quill checks the spec-conformance prompt. Reviewed by Atlas.

**Size**

M.
