---
identifier: "PAP-679"
title: "Review fix loop: turn a Gate 2 `REQUEST_CHANGES` into a builder re-queue with the findings in the prompt, two rounds maximum, then escalate"
project: "quality"
projectName: "Quality Pipeline"
phase: "P0"
type: "Build"
priority: 1
surfaces: ["Developer"]
milestone: "Gates 1 and 2 on every PR"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-108", "PAP-243", "PAP-281"]
blocks: ["PAP-88"]
key: "r4/quality/review-fix-loop"
url: "https://linear.app/paperos/issue/PAP-679/review-fix-loop-turn-a-gate-2-request-changes-into-a-builder-re-queue"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:20:26.662Z"
model: "claude-opus-5"
effort: "high"
estimate: 3
dueDate: "2026-09-25"
cycle: null
---

# PAP-679: Review fix loop: turn a Gate 2 `REQUEST_CHANGES` into a builder re-queue with the findings in the prompt, two rounds maximum, then escalate

**Model / Effort:** Opus 5 (`claude-opus-5`) / high — Build M

**Goal**

Reviewers post findings (PAP-243) and PAP-108 defines the `review-to-build` handoff, but nothing turns a red `gate/2-review` into a fix session without a human: the cost model assumes a 30 percent bounce rate and re-review, so the loop must be mechanical. This issue wires it: a blocking review re-queues the issue to the original character with the must-fix list in the prompt, the fix commit triggers an incremental re-review, and after two rounds the dispute escalates to Atlas, then Justin.

**Scope**

* In: orchestrator handler on `pull_request_review` with `REQUEST_CHANGES` from a reviewer bot (PAP-97 event), `fixRound` counter on `sessions`, prompt template `prompts/fix-round.md` (must-fix findings, rubric ids, suggestion diffs, `Resolved in <sha>` convention), re-review trigger label `re-review` (PAP-81), state moves `In Review -> In Progress -> In Review`, escalation after round 2 via PAP-108 `escalate`, metrics `review.bounce`, `docs/quality/review-fix-loop.md`.
* Out: the reviewers and harness (PAP-243), autofix of S2/S3 by the reviewer itself (never), merging (Atlas Merger).

**Spec**

* Trigger: any reviewer status `gate/2-*` turns `fail` on a PR linked to an `In Review` issue; the handler collects `Finding[]` with severity S0 or S1 from the review artefacts (`review.json`) and builds a `review-to-build` handoff (PAP-108) addressed to the issue's builder character.
* Re-queue: issue moves to `In Progress`, `sessions.fix_round` increments, a session launches on the same worktree and branch with `prompts/fix-round.md`: the must-fix list, the reviewer's suggestion diffs, the instruction to reply to each finding with `Resolved in <sha>` or a one-paragraph dispute, and the ban on force-pushing; budget for a fix round is 50 percent of the issue's size allowance (PAP-111).
* Fix commit pushed: the PR gets label `re-review`; PAP-243 runs incremental mode on the new diff, updates findings in place, and the statuses recompute; S2 and S3 never trigger a round.
* Round cap: after `fix_round = 2` with an open S0 or S1, the handler posts an `escalate` handoff to Atlas with both positions; Atlas may waive (S1 only, recorded as a waiver) or file a Needs Justin card (S0 or disputed security finding), matching the Sentinel escalation rules.
* Metrics: `review_bounce(issue, round, findings, cost)` feeds PAP-98 (bounce cost) and PAP-241 (disputed findings are calibration input).

**Interface contract**

* Provides: handler `onReviewRequestChanges`, prompt template `fix-round.md`, `sessions.fix_round`, label `re-review` trigger contract, metric `review.bounce`, escalation path.
* Consumes: PAP-243 statuses and `review.json`, PAP-97 review events and `linearComment`, PAP-281 transitions and `launchSession` (PAP-282), PAP-108 handoff kinds, PAP-111 budget hook, PAP-98 metering.

**Definition of done**

* Seeded PR (sandbox) with an S1 null-handling bug: reviewer blocks, a fix session starts within one poll, pushes a fix, re-review resolves the finding and `gate/2-review` turns green (recording).
* Round cap test: a session that disputes twice produces exactly one `escalate` handoff to Atlas and no third round.
* S2-only review never triggers a round (test); fix-round budget enforced at 50 percent.
* Docs; changelog under "Quality"; Linear comment with the recording and bounce metrics.

**Test plan**

* Unit: finding filter (S0/S1 only), round counter, prompt rendering with suggestion diffs, escalation decision table.
* E2E: sandbox seeded PR through reviewer, fix session and re-review with the real harness nightly; mocked SDK on PRs.

**Demo**

Open the seeded PR: red `gate/2-review`, then the fix session's `Session started` comment on the issue, the fix commit, `Resolved in <sha>` replies and the green re-review. Two minutes of watching.

**Edge cases**

* Reviewer finding is wrong: the builder disputes once with a reason; the reviewer either resolves it or the second dispute escalates; nobody edits findings by hand.
* Fix session cannot reproduce (flaky test): posts `flake-suspected`, PAP-90 collector classifies, round not counted.
* PR from a character whose daily budget is exhausted: the round waits with `budget-hold` and Atlas is notified after four hours (PAP-108 rule).
* Multiple reviewers block at once: one round handles all findings; rounds are per PR, not per reviewer.

**Dependencies**

Hard: PAP-243, PAP-281, PAP-108. Soft: PAP-97, PAP-282, PAP-111, PAP-98, PAP-241.

**Agent**

Builder: Atlas (Dispatcher) with Sentinel (Code Reviewer) on the prompt. Reviewer: Sentinel (Code Reviewer).

**Size**

M: one session.
