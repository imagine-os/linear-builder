---
identifier: "PAP-99"
title: "Implement concurrency controls: max parallel sessions, file-lock hints and dependency-aware scheduling from dependsOn"
project: "pm-linear"
projectName: "Project Management & Claude Pipeline"
phase: "P1"
type: "Build"
priority: 1
surfaces: ["Agent"]
milestone: "Orchestrator claims and ships issues"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-96"]
blocks: []
key: "pm-linear/concurrency"
url: "https://linear.app/paperos/issue/PAP-99/implement-concurrency-controls-max-parallel-sessions-file-lock-hints"
source: "plan/specs/bucket-3.json (round-1 canonical spec JSON)"
---

# PAP-99: Implement concurrency controls: max parallel sessions, file-lock hints and dependency-aware scheduling from dependsOn

**Goal**

Let twenty sessions run at once without merge storms or blocked work: the orchestrator schedules issues by dependency readiness, keeps sessions that touch the same files apart, and caps parallelism globally, per repo and per character. Throughput goes up while conflict rate stays near zero.

**Scope**

In:
- Dependency-aware scheduling: an issue is eligible only when every Linear `blockedBy` relation is `Done` (or the blocker is `In Review` and the issue is labelled `can-start-on-review`); build a DAG from relations each poll and detect cycles.
- File-lock hints: issues declare `Files:` glob lines in the `Scope` section (for example `packages/ui/**`); the scheduler will not start two sessions whose globs intersect on the same repo; hints are also learned by recording the paths each session's PR touched and warning when a new issue's globs miss them.
- Limits from `orchestrator.config.yaml`: `maxParallel` (global, default 12), `perRepo` (default 6), `perCharacter` (default 3, Sentinel 6 because review is cheap to parallelise), `perProject` optional.
- Priority scoring: `score = priorityWeight + ageHours*0.1 + unblocksCount*2 + phaseWeight`, where `unblocksCount` is the number of issues waiting on this one; highest score claimed first.
- Merge queue awareness: when more than `mergeQueueMax` (default 5) PRs are `In Review` for one repo, pause new claims for that repo and let Sentinel and Merger sub-agent catch up.
- `pnpm schedule:explain PAP-123` prints why an issue is or is not eligible; `/status` shows the eligible list with scores and the reason for each blocked issue.

Out: automatic rebasing and conflict resolution (Atlas's Merger sub-agent, tracked under forge), Linear relation creation (Decomposer), per-character budgets (`agents/cost-controls`).

**Spec**

- Module `src/scheduler/` with pure functions: `buildGraph(issues, relations)`, `eligible(graph, running, config)`, `score(issue, graph)`, `conflicts(globsA, globsB)` using `picomatch`; the loop from `pm-linear/orchestrator` calls `scheduler.next()` instead of taking the first issue.
- Globs parsed from the issue description by the contract parser (`pm-linear/issue-contract` adds an optional `Files` line; missing globs mean "unknown", which conflicts with nothing but is flagged in `/status` as a risk).
- Learned paths stored in `orchestrator.issue_paths(issue_id, path)` from `git diff --name-only origin/main...HEAD` at PR open.
- Cycle detection reports the cycle to `Needs Justin` once (deduped by cycle hash).
- Fairness: no project starves; if a project has had zero sessions in 6 hours while eligible, add a starvation bonus.

**Definition of done**

- Property-based tests (fast-check) that `eligible()` never returns two issues with intersecting globs on one repo and never returns an issue with an open blocker.
- Simulation test: 200 synthetic issues from plan.json with its `dependsOn` edges scheduled with `maxParallel` 12 completes with zero conflicts and total makespan printed; result table attached.
- Live soak: 8 real issues in parallel on staging for 4 hours with conflict rate (PRs needing manual rebase) below 10 percent; report in comment.
- `/status` screenshot at 1280 px showing eligibility reasons.
- Docs section in the orchestrator README; changelog entry; Linear comment with the simulation and soak results.

**Edge cases**

- Blocker is `Canceled` or `Duplicate`: treat as satisfied but comment on the dependent issue so a human can confirm.
- Globs like `**` on one issue: it conflicts with everything; warn in `/status` and require it to run alone.
- Relations changed mid-run (Justin adds a blocker to an `In Progress` issue): do not kill the session; note it in the status comment.
- Two repos share a package via git submodule: treat globs as repo-scoped only; document the limitation.
- Priority `Urgent` set by Justin: bypass `perProject` and merge-queue pause but not global `maxParallel`.
- Scheduler exception: fall back to the simple FIFO from the orchestrator and log loudly rather than stall the queue.

**Dependencies**

- `pm-linear/orchestrator` (loop, claims, config).
- Uses relation data created by the Decomposer and validated by `pm-linear/issue-contract`.

**Agent**

Built by Atlas (Dispatcher sub-agent); reviewed by Sentinel (Code Reviewer, Edge Case Hunter for the simulation).

**Size**

M: pure-logic scheduler with property tests and one soak run.
