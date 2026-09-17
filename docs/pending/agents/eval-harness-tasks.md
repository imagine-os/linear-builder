---
key: "agents/eval-harness/tasks"
title: "Eval harness: golden task set (three per lead, one per sub) with fixture repos and answer keys"
project: "agents"
parent: "PAP-110"
phase: "P1"
type: "Build"
priority: null
size: "M"
surfaces: ["Agent"]
milestone: null
intendedState: "Backlog"
blockedBy: ["agents/eval-harness/runner"]
blocks: ["agents/eval-harness/judge"]
source: "round2/agent2/new_agents.py"
linearDocument: "https://linear.app/paperos/document/round-2-pending-issues-agents-9-85624b15630d"
identifier: "PAP-309"
status: "created"
createdAt: "2026-09-17"
---

# Eval harness: golden task set (three per lead, one per sub) with fixture repos and answer keys

**Goal**

Write the golden tasks that define what good looks like for every character: at least three per lead and one per sub (about 55), each with a frozen prompt, a fixture repo pinned to a template SHA, deterministic graders and, where judgement is needed, a rubric, including the seeded-bug PR for Sentinel with an answer key and F1 scoring.

**Scope**

* In: `packages/agents/evals/tasks/<character>/<task-id>/` for all characters, fixture tarballs under `packages/agents/evals/fixtures/`, `answer-key.json` for seeded bugs, rubric files, a weekly fixture bump job.
* Out: runner and graders (`agents/eval-harness/runner`), judge and trend (`agents/eval-harness/judge`).

**Spec**

* Lead tasks: Atlas decomposes a mini brief into three contract-valid issues (grader: PAP-93 `validateIssue` on each), schedules a toy graph, writes a decision card; Forge adds a Drizzle table with migration and RLS (grader: migration applies, RLS test passes), fixes a failing CI job, writes a compose service; Iris builds a component with stories passing axe, fixes a contrast bug, adds a token; Quill writes a page spec that validates, an ADR, a changelog from PRs; Sentinel reviews a PR with five planted bugs (F1 over findings by file and line range), reviews a spec-conformance drift, triages screenshots; Nova adds a grid column type, a kanban swimlane, a canvas node; Ledger posts a balanced journal entry (grader: debits equal credits), reconciles a Stripe fixture, computes a payroll adapter mapping; Beacon drafts a campaign from a changelog for approval (rubric), a landing form spec, a CRM segment; Scout scores a library against the rubric (grader: all criteria present), drafts an ADR, runs a license check.
* Sub tasks: one focused task each matching its `description` trigger.
* Fixtures pinned to `paperos-template@<sha>`; seeded bugs documented in `answer-key.json` with `file`, `lines`, `severity`, `category`.
* Rubrics: 0-5 per criterion with anchors; at most five criteria per task.

**Interface contract**

* Provides: about 55 task folders validating against `TaskSchema`, fixture tarballs, `answer-key.json` format `{ bugs: [{ id, file, lines: [a, b], severity, category }] }`, `scoreF1(findings, key)` in `grade.ts`.
* Consumers: `agents/eval-harness/judge` (rubrics), PAP-241 (seeded-bug fixture and F1 for Gate 2 calibration), PAP-81 (same fixture for reviewer calibration), PAP-104 (smoke outputs cross-checked).
* Requires: runner child; PAP-93, PAP-115, PAP-79 for graders and rubric anchors; template SHA.

**Definition of done**

* `pnpm evals list` shows all tasks; every task runs once in cheap mode without infrastructure errors (table attached).
* Seeded-bug PR: a deliberately perfect answer scores F1 1.0 and an empty answer 0.0 (tests).
* Fixture bump job opens a PR when the template SHA moves.
* Changelog; Linear comment with the task table.

**Test plan**

* Unit: `scoreF1` cases, answer-key schema, task schema for every folder.
* Integration: cheap-mode run of all tasks once.
* No UI.

**Demo**

Open `tasks/sentinel/seeded-bugs-1/answer-key.json`, run `pnpm evals run --task sentinel/seeded-bugs-1 --model claude-sonnet-5 --effort low` and read the F1 score with matched and missed bug ids. Two minutes.

**Edge cases**

* Task depends on a package not yet merged (dashboard blocks): fixture pins a branch tarball; task marked `pending-dependency` and excluded from trend.
* Two tasks share a fixture: one tarball, referenced twice.
* Sentinel finds an unplanted real bug: counts as a true positive if a reviewer confirms; answer key updated with a version bump.
* Rubric criterion ambiguous: anchors rewritten; version bump resets trend.
* Fixture over 50 MB: stored in MinIO (PAP-37) with a hash reference.

**Dependencies**

Blocked by `agents/eval-harness/runner`. Uses PAP-93, PAP-115, PAP-79.

**Agent**

Built by Sentinel (Edge Case Hunter) with each lead contributing its own tasks; reviewed by Quill.

**Size**

M
