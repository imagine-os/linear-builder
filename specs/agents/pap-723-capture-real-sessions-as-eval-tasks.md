---
identifier: "PAP-723"
title: "Capture real sessions as eval tasks: `pnpm evals capture --session <id>` turns a logged session or an escaped defect into a golden task with fixtures and graders"
project: "agents"
projectName: "Agent Characters & Orgs"
phase: "P2"
type: "Build"
priority: 4
surfaces: ["Agent"]
milestone: "Sub-agents, skills and evals live"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-107", "PAP-308"]
blocks: []
key: "r4/agents/session-to-eval-task-capture"
url: "https://linear.app/paperos/issue/PAP-723/capture-real-sessions-as-eval-tasks-pnpm-evals-capture-session-id"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:20:22.133Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 2
dueDate: null
cycle: null
---

# PAP-723: Capture real sessions as eval tasks: `pnpm evals capture --session <id>` turns a logged session or an escaped defect into a golden task with fixtures and graders

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Build S

**Goal**

Deferred to v0.2 by round 4 (not claimable before 2026-10-01; NJ-14 can reinstate). Golden tasks (PAP-309) are hand-written; the richest source of hard tasks is production: sessions that bounced twice, escaped defects PAP-241 attributes, disputed findings. LangSmith-style dataset capture turns a logged session into a reproducible task so the eval set grows from real failures instead of guesses.

**Scope**

* In: `packages/agents/evals/src/capture.ts`: read a session from the prompt-log store (PAP-129) or spool (PAP-107), extract the issue text, the worktree base SHA and touched files, produce `tasks/<character>/captured-<id>/task.yaml` with a fixture tarball of the base commit, deterministic graders from the issue's Definition of done (tests named, files expected) and, for escaped defects, the fixing PR's tests as the oracle; redaction pass; `pnpm evals capture --session <id> | --defect <sha>`; docs section.
* Out: judging captured tasks (PAP-310), storing large fixtures (MinIO reference as in PAP-309), capturing customer data (never; only PAP fixtures).

**Spec**

* Extraction: `issueKey`, `character`, base SHA from the `Session started` footer, files touched from the PR diff, DoD bullets parsed into `command` graders where they name a command or test file.
* Escaped defect mode: given the fix commit with `Introduced-By:` (PAP-241), the task is the original issue at the base SHA and the grader is the fix PR's added tests, so the task measures whether the character now avoids the defect.
* Fixture tarball from the base SHA of the template or repo, capped at 50 MB with MinIO reference otherwise; `version: 1`, `flaky: false`, `captured: { sessionId, at }` in `task.yaml`.
* Redaction through PAP-107 `redact()`; prompts containing untrusted T3 blocks are wrapped as in production.

**Interface contract**

* Provides: `pnpm evals capture`, task folder convention `captured-<id>`, `captured` metadata in `TaskSchema`.
* Consumes: PAP-308 task format, PAP-107 spool and `redact()`, PAP-129 store, PAP-241 `Introduced-By:` trailers, PAP-309 fixture rules.

**Definition of done**

* Three captured tasks (one bounce, one escaped defect, one disputed finding) run in cheap mode and grade; the escaped-defect task fails at the base SHA and passes with the fix applied (test).
* Docs section; changelog.

**Test plan**

* Unit: DoD-to-grader parsing on fixtures, base SHA extraction, redaction pass.
* E2E: capture from a staging session and run the task.

**Demo**

Run `pnpm evals capture --defect <sha>` for a seeded escaped defect, then `pnpm evals run --task sentinel/captured-<id>` and watch the grader fail on the base and pass on the fix. Two minutes.

**Edge cases**

* Session spans several worktrees (fix rounds): the last base SHA before the fix is used.
* DoD has no parsable checks: task created with a rubric stub for PAP-310's judge and flagged `needs-graders`.
* Fixture over cap: MinIO reference; CI fetches through the broker.

**Dependencies**

Hard: PAP-308, PAP-107. Soft: PAP-129, PAP-241, PAP-309.

**Agent**

Builder: Sentinel (Edge Case Hunter). Reviewer: Sentinel (Code Reviewer).

**Size**

S: half a session.
