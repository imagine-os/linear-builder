---
identifier: "PAP-110"
title: "Create an eval harness with golden tasks per character, scored nightly, regressions flagged in Linear"
project: "agents"
projectName: "Agent Characters & Orgs"
phase: "P1"
type: "Build"
priority: 1
surfaces: ["Agent"]
milestone: "Sub-agents, skills and evals live"
state: "Backlog"
parent: null
children: ["PAP-308", "PAP-309", "PAP-310"]
blockedBy: ["PAP-104", "PAP-105", "PAP-287"]
blocks: []
key: "agents/eval-harness"
url: "https://linear.app/paperos/issue/PAP-110/create-an-eval-harness-with-golden-tasks-per-character-scored-nightly"
source: "Linear snapshot 2026-09-17T13:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T13:06:17.696Z"
---

# PAP-110: Create an eval harness with golden tasks per character, scored nightly, regressions flagged in Linear

**Goal**

Measure the agents themselves: a harness runs golden tasks for every character nightly, scores outputs with deterministic checks and an LLM judge, tracks the trend and opens a Linear issue when a character regresses. Prompt, skill and model changes get judged by numbers. Umbrella for three children; relabelled `Type/Build` because it builds a harness.

**Scope**

* Children (build in order, 2 can start after 1's task format is fixed):
  * PAP-308: task format, runner, deterministic graders and results table.
  * PAP-309: the golden task set (three per lead, one per sub, about 55) with fixture repos.
  * PAP-310: LLM judge, trend, regression issues, nightly schedule and report page.
* Out: product e2e (quality project), end-user feature prompts, vendor benchmarks.

**Spec**

* Layout `packages/agents/evals/tasks/<character>/<task-id>/{task.yaml, expected/, grade.ts | rubric.md}`; `task.yaml`: `prompt`, `fixtures`, `allowedTools`, `maxTurns`, `budgetUsd`, `version`, `flaky`.
* Runner `pnpm evals run [--character] [--task] [--model] [--effort]` launches through the Agent SDK with the PAP-106 bundle in a throwaway worktree; cheap mode Sonnet `low` for skill PRs under $5.
* Grading: deterministic first (tests pass, files exist, schema valid, footer present, no `scope-denied` events), then judge (Sentinel Code Reviewer definition, strict JSON output) 0-5 per rubric criterion; weighted final score; both stored.
* Table `orchestrator.eval_runs(run_id, character, task, task_version, model, score, checks_json, judge_json, cost_usd, duration_ms, transcript_ref, git_sha, at)`.
* Regression: score drops more than 15 percent from the seven-run median, or a check that passed three times fails: create or update `Eval regression: <character>/<task>` (Type Review, Character Sentinel). Nightly 03:00 UTC, cap $60 via PAP-111, all runs logged with `issueKey: EVAL`.

**Interface contract**

* Provides: `pnpm evals {run,list,report}`, `eval_runs` table, `EvalResult` Zod type, `docs/agents/evals.md` regenerated nightly, the regression issue template, judge schema `judge.schema.json`.
* Consumers: PAP-104 prompt PRs (smoke gate), PAP-105 skill PRs (cheap mode), PAP-111 (cap), PAP-113 (score per character optional), PAP-241 (Gate 2 calibration reuses the seeded-bug fixture and F1 scorer), PAP-306 (eval trend section).
* Requires: PAP-104 roster and smoke transcripts as fixtures, PAP-105 skills, PAP-106 bundles, PAP-98 cost, PAP-111 caps, Linear ids from PAP-91.

**Definition of done**

* All three children Done.
* Full nightly run under three hours and under cap; results table screenshot at 1280 px.
* Regression detection proven by breaking Iris's prompt on a branch and observing the Linear issue (screenshot).
* Judge agreement above 80 percent on 20 spot-checked outputs.
* Report page renders; changelog; Linear comment with first baseline.

**Test plan**

* Umbrella integration: `pnpm evals run --all --model claude-sonnet-5 --effort low` on CI produces a table for all characters; determinism check on graders.
* Regression rule tested with synthetic run histories (fake clock).
* Visual: report page at 1280 px only.

**Demo**

Run `pnpm evals run --character quill --task page-spec-invoices` and watch the deterministic checks and judge score print with a transcript link; then `pnpm evals report` to see the trend table. Two minutes.

**Edge cases**

* Flaky task: run three times, median; cannot trigger regressions alone.
* Model outage: run `incomplete`, retried next night.
* Checks pass but judge low: report both, flag disagreement.
* Budget cap mid-run: remaining `skipped-budget`.
* Fixture repo drifts: pinned to a template SHA; weekly bump job re-baselines.

**Dependencies**

Blocked by PAP-104, PAP-105. Uses PAP-106, PAP-111, PAP-98.

**Agent**

Built by Sentinel (lead) with Atlas on the runner; reviewed by Quill for task clarity.

**Size**

L (umbrella; children M, M, M)
