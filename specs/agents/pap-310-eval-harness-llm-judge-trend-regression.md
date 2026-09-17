---
identifier: "PAP-310"
title: "Eval harness: LLM judge, trend, regression issues, nightly schedule and report page"
project: "agents"
projectName: "Agent Characters & Orgs"
phase: "P1"
type: "Build"
priority: 1
surfaces: ["Agent"]
milestone: "Sub-agents, skills and evals live"
state: "Backlog"
parent: "PAP-110"
children: []
blockedBy: ["PAP-308", "PAP-309"]
blocks: []
key: "agents/eval-harness/judge"
url: "https://linear.app/paperos/issue/PAP-310/eval-harness-llm-judge-trend-regression-issues-nightly-schedule-and"
source: "Linear snapshot 2026-09-17T13:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T13:05:02.333Z"
model: "claude-sonnet-5"
effort: "high"
---

# PAP-310: Eval harness: LLM judge, trend, regression issues, nightly schedule and report page

**Goal**

Close the loop: an LLM judge scores rubric tasks with strict JSON output, a combined score feeds a per-character trend, regressions open or update a Linear issue, a nightly run under a budget cap keeps the numbers current, and a report page shows the state of the org at a glance.

**Scope**

* In: `packages/agents/evals/src/{judge,trend,regress,report}.ts`, nightly workflow `.github/workflows/evals-nightly.yml` (03:00 UTC), `docs/agents/evals.md` regeneration, regression issue template, judge agreement check.
* Out: runner and tasks (sibling children), eval of reviewer misses on real PRs (PAP-241).

**Spec**

* Judge: Sentinel Code Reviewer definition on `claude-fable-5-1` at `high`, input rubric, summarised transcript and diff; output constrained to `judge.schema.json` `{ criteria: [{ id, score: 0-5, justification }], overall }`; stored in `judge_json`.
* Combined score: `0.6 * deterministicRatio + 0.4 * judgeNormalised` when both exist, else the one available; disagreement flag when deterministic passes and judge under 2.
* Trend: per character and task over the last 14 runs; regression when score drops more than 15 percent from the seven-run median or a check that passed three consecutive times fails; flaky tasks need two consecutive regressions.
* Regression issue `Eval regression: <character>/<task>` (Type Review, Character label Sentinel, project agents) created or updated with a table and transcript diff links; one issue per character per night.
* Nightly: all non-flaky tasks, cap $60 through PAP-111 `--cap`, remaining tasks `skipped-budget`; report regenerated with a table and 14-day sparkline per character; runs logged with `issueKey: EVAL`.

**Interface contract**

* Provides: `judge(task, result): Judgement`, `combinedScore()`, `detectRegressions(runs): Regression[]`, `pnpm evals report`, `docs/agents/evals.md`, the regression issue template, `judge.schema.json`.
* Consumers: PAP-112 links the report; PAP-113 optional score badge; PAP-306 eval section; PAP-241 reuses the judge agreement method.
* Requires: sibling children, PAP-111 cap, PAP-91 ids for issue creation, PAP-105 `linear-update` for posting.

**Definition of done**

* Judge agreement: 20 judged outputs spot-checked by Sentinel with agreement above 80 percent (recorded).
* Regression proven by breaking Iris's prompt on a branch and observing the issue (screenshot).
* Full nightly run completes under three hours and under cap; report screenshot at 1280 px.
* Changelog; Linear comment with the first baseline table.

**Test plan**

* Unit: combined score cases, regression rule with synthetic histories and fake clock, flaky handling, one-issue-per-character dedupe.
* Integration: judge with a recorded transcript against the schema; report renderer snapshot.
* e2e: nightly run in staging; the Iris break test.
* Visual: report page at 1280 px only.

**Demo**

Run `pnpm evals report` and read the trend table; then `pnpm evals regress --simulate iris` to see the regression issue draft printed with its table. One minute.

**Edge cases**

* Judge output fails schema: retry once, then `judge: null`, deterministic only.
* Model outage mid-run: run `incomplete`, no regressions filed.
* Two regressions for one character: one issue, table of both.
* Task version bumped: trend resets; no regression against old versions.
* Report exceeds Linear comment size: link to the docs page with a five-line summary.

**Dependencies**

Blocked by PAP-308, PAP-309. Uses PAP-111, PAP-105.

**Agent**

Built by Sentinel (lead); reviewed by Atlas.

**Size**

M
