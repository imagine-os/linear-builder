---
key: "agents/eval-harness/runner"
title: "Eval harness: task format, SDK runner, deterministic graders and results table"
project: "agents"
parent: "PAP-110"
phase: "P1"
type: "Build"
priority: null
size: "M"
surfaces: ["Agent"]
milestone: null
intendedState: "Backlog"
blockedBy: []
blocks: ["agents/eval-harness/tasks", "agents/eval-harness/judge"]
source: "round2/agent2/new_agents.py"
linearDocument: "https://linear.app/paperos/document/round-2-pending-issues-agents-9-85624b15630d"
identifier: "PAP-308"
status: "created"
createdAt: "2026-09-17"
---

# Eval harness: task format, SDK runner, deterministic graders and results table

**Goal**

Build the machinery of the eval harness: the frozen task format, a runner that launches a character on a task in a throwaway worktree through the Agent SDK with its PAP-106 bundle, deterministic graders (tests pass, files exist, schema valid, footer present, no denied tool calls) and the `eval_runs` table, so tasks and the judge can be added on top.

**Scope**

* In: `packages/agents/evals/src/{task,run,grade,store}.ts`, `task.yaml` schema, `pnpm evals run | list`, `orchestrator.eval_runs` migration, fixture repo tarball handling, cheap mode flags.
* Out: the task set (`agents/eval-harness/tasks`), the LLM judge, trend and regression issues (`agents/eval-harness/judge`).

**Spec**

* `task.yaml`: `{ id, character, version, prompt, fixtures: { repo: tarball | template@sha, files? }, allowedTools?, maxTurns, budgetUsd, flaky, graders: [{ kind: tests | fileExists | schema | footer | noDenied | command, args }] }`; Zod-validated; changing content without bumping `version` fails `evals list`.
* Runner: unpack fixtures into `/srv/evals/<run>/<task>`, call `launchSession` from `pm-linear/orchestrator/sessions` with `sandbox: true` when `agents/runtime-sandbox` exists, `model` and `effort` overrides, capture transcript, cost (PAP-98 `result`), duration and denied-tool events (PAP-107).
* Graders return `{ id, pass, detail }`; `command` grader runs inside the fixture with a timeout; `tests` runs `pnpm vitest run` in the fixture.
* Store: `eval_runs(run_id, character, task, task_version, model, effort, score, checks_json, judge_json, cost_usd, duration_ms, transcript_ref, git_sha, at)`; `score` for this child is the deterministic pass ratio; judge fills `judge_json` later.
* Cheap mode `--model claude-sonnet-5 --effort low` for smoke.

**Interface contract**

* Provides: `TaskSchema`, `runTask(task, opts): EvalResult`, `grade(task, workspace): Check[]`, `pnpm evals run [--character] [--task] [--model] [--effort] [--cap]`, `pnpm evals list`, table `eval_runs`, `EvalResult` Zod type.
* Consumers: sibling children; PAP-104 build child (smoke outputs convertible to tasks); PAP-105 skill PRs (cheap mode gate); PAP-241 (F1 scorer helper lives in `grade.ts`).
* Requires: `pm-linear/orchestrator/sessions` `launchSession`, PAP-106 bundles, PAP-98 cost, PAP-111 cap, PAP-107 events.

**Definition of done**

* Two seed tasks (Quill spec validates, Forge migration applies) run end to end and store rows.
* Graders unit-tested with pass and fail fixtures; frozen-version check tested.
* Cheap mode run under $5 for the two tasks; numbers in comment.
* Changelog; Linear comment.

**Test plan**

* Unit: task schema, version freeze, each grader, score arithmetic.
* Integration: runner with a mocked SDK producing files; fixture unpack and cleanup.
* e2e: two real tasks in staging.
* No UI.

**Demo**

Run `pnpm evals run --task quill/page-spec-invoices --model claude-sonnet-5 --effort low` and watch checks print pass or fail with the transcript path; `pnpm evals list` shows versions. Ninety seconds.

**Edge cases**

* Fixture tarball missing: fail fast before spending tokens.
* Session exceeds `budgetUsd`: aborted via PAP-111, run stored with `aborted: true`.
* Grader command hangs: timeout 5 minutes, check fails with `timeout`.
* Worktree reuse between tasks: never; fresh directory per run.
* Same task run twice in one night: both stored; trend uses the latest.

**Dependencies**

Blocked by PAP-104, PAP-105 (through the parent). Uses `pm-linear/orchestrator/sessions`, PAP-106, PAP-98, PAP-111.

**Agent**

Built by Sentinel (lead) with Atlas on the runner; reviewed by Forge.

**Size**

M
