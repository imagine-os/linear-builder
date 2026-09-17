---
identifier: "PAP-110"
title: "Create an eval harness with golden tasks per character, scored nightly, regressions flagged in Linear"
project: "agents"
projectName: "Agent Characters & Orgs"
phase: "P1"
type: "Review"
priority: 1
surfaces: ["Agent"]
milestone: "Sub-agents, skills and evals live"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-104", "PAP-105"]
blocks: []
key: "agents/eval-harness"
url: "https://linear.app/paperos/issue/PAP-110/create-an-eval-harness-with-golden-tasks-per-character-scored-nightly"
source: "plan/specs/bucket-3.json (round-1 canonical spec JSON)"
---

# PAP-110: Create an eval harness with golden tasks per character, scored nightly, regressions flagged in Linear

**Goal**

Measure the agents themselves: a harness runs golden tasks for every character nightly, scores the outputs against rubrics and deterministic checks, tracks the trend, and opens or updates a Linear issue when a character regresses. Prompt, skill and model changes can then be judged by numbers instead of vibes.

**Scope**

In:
- Repo location `packages/agents/evals/` with `tasks/<character>/<task-id>/` folders containing `task.yaml` (prompt, fixtures path, allowed tools, max turns, budget), `expected/` (files, JSON or rubric), and `grade.ts` (deterministic checks) or `rubric.md` (LLM-judged).
- Golden tasks, at least 3 per lead and 1 per sub (about 55 total): Atlas decomposes a mini brief into contract-valid issues; Forge adds a Drizzle table with migration and RLS; Iris builds a component with stories that pass axe; Quill writes a page spec that validates; Sentinel reviews a seeded PR containing 5 planted bugs (recall and precision); Nova adds a column type to the grid; Ledger posts a balanced journal entry; Beacon drafts a campaign from a changelog for approval; Scout scores a library against the rubric; subs get one focused task each.
- Runner `pnpm evals run [--character] [--task] [--model]` launching sessions through the Agent SDK with the character's bundle from `agents/tool-scopes`, in a throwaway worktree, capturing transcript, cost and duration.
- Grading: deterministic checks first (tests pass, file exists, schema validates, footer present, no denied tool calls), then an LLM judge (Sentinel's Code Reviewer definition, `claude-fable-5-1`, effort `high`) scoring the rubric 0-5 per criterion with justification; final score is weighted; store both.
- Results table `orchestrator.eval_runs(run_id, character, task, model, score, checks_json, cost_usd, duration_ms, transcript_ref, git_sha)`; trend per character over 14 runs.
- Regression rule: score drops more than 15 percent from the 7-run median, or any deterministic check that passed 3 times fails: create or update Linear issue `Eval regression: <character>/<task>` (Type Review, Character Sentinel) with the diff of transcripts.
- Nightly cron 03:00 UTC; budget cap per run (default $60) enforced via `agents/cost-controls`.
- Report page `docs/agents/evals.md` regenerated nightly with a table and sparkline per character.

Out: evals of the product itself (Playwright suites in `quality/*`), evals of prompts for end-user features, benchmark comparisons against other vendors.

**Spec**

- Tasks are frozen: changing a task bumps its `version` and resets the trend; the harness never edits expected outputs automatically.
- Judge prompt receives the rubric, the transcript (tool calls summarised), and the diff; judge output is a strict JSON schema (`output_config.format`) to avoid parsing failures.
- Seeded bugs for the Sentinel task live in a fixture repo tarball with an answer key; score is F1 over findings matched by file and line range.
- Cheap mode `--model claude-sonnet-5 --effort low` for smoke checks on skill PRs (cost under $5).
- All runs are logged to the prompt-log store with `issueKey: EVAL`.

**Definition of done**

- 55 tasks committed with graders; `pnpm evals list` shows them.
- Full nightly run completes under 3 hours and under the budget cap; results table screenshot at 1280 px.
- Regression detection tested by deliberately breaking Iris's prompt on a branch and observing an eval regression issue created in Linear (screenshot).
- Judge agreement: 20 judged outputs spot-checked by Sentinel with agreement above 80 percent, recorded in the comment.
- Report page renders; changelog entry; Linear comment with the first baseline table.

**Edge cases**

- Flaky task (network-dependent fixture): mark `flaky: true`, run 3 times, take median; flaky tasks cannot trigger regressions alone.
- Model outage or refusal mid-run: run marked `incomplete`, no regression issue, retried next night.
- Task passes deterministic checks but the judge scores low: report both; regression uses the combined score but flags the disagreement.
- Budget cap hit halfway: remaining tasks marked `skipped-budget`, trend unaffected.
- Two regressions for the same character in one night: one issue with a table, not two.
- Fixture repo drifts from the template (new lint rule): fixtures pinned to a template SHA; a weekly job bumps and re-baselines.

**Dependencies**

- `agents/roster-v1` (characters, bundles) and `agents/skills-library` (skills exercised by tasks).
- Uses `agents/tool-scopes` bundles, `agents/cost-controls` caps, `pm-linear/credit-metering` for cost, Linear for regression issues.

**Agent**

Built by Sentinel (lead, this is its core responsibility) with Atlas for orchestration; reviewed by Atlas and Quill (task wording), and Code Reviewer for the runner.

**Size**

L: 55 tasks, a runner, a judge and nightly infrastructure.
