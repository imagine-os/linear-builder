---
identifier: "PAP-95"
title: "Decompose PAP-5 (startup procedure inefficiency) into this master plan's projects and close it with a summary comment"
project: "pm-linear"
projectName: "Project Management & Claude Pipeline"
phase: "P0"
type: "Docs"
priority: 2
surfaces: ["Agent"]
milestone: "Linear configured for the pipeline"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-91"]
blocks: []
key: "pm-linear/pap5-decompose"
url: "https://linear.app/paperos/issue/PAP-95/decompose-pap-5-startup-procedure-inefficiency-into-this-master-plans"
source: "plan/specs/bucket-3.json (round-1 canonical spec JSON)"
---

# PAP-95: Decompose PAP-5 (startup procedure inefficiency) into this master plan's projects and close it with a summary comment

**Goal**

Close the loop on the issue that started everything. PAP-5 ("the startup procedure for creating new apps on the fly is inefficient... how quickly do we get from blank screen to electrons") is restated as a measurable goal, linked to the projects and issues in this plan that answer it, and closed with a summary comment so the origin of the whole programme is traceable from Linear.

**Scope**

In:
- Rewrite the PAP-5 description (keep the original title text quoted at the top) into the contract format: Goal restated as "time from `paperos create <app>` to a running, reviewed page on web and desktop under 4 hours of wall-clock and under $150 of credits"; Scope pointing to the 17 projects.
- A "Decomposition" section: a table with one row per project (name, Linear project link, phase, what it contributes to the startup time), generated from plan.json by a script so it matches the created projects exactly.
- Linear relations: PAP-5 `related` to each of the 17 projects' first milestone issue; PAP-5 becomes the parent of a new tracking issue `Startup benchmark` (Type Review, P2) that measures the time-to-first-page metric at the end of P2.
- Close PAP-5 as `Done` with a final comment: the metric, where the plan lives (plan.json path in the orchestrator repo and the Linear projects view), and how to reopen (new issue, not reopen).
- Labels: P0, Docs, Agent, Character Atlas; estimate S.

Out: any changes to other issues' content; building the benchmark itself (the new tracking issue owns that).

**Spec**

- Script `ops/linear/decompose-pap5.ts` in `imagine-os/paperos-orchestrator` reads `plan.json`, resolves project ids via `projects(filter: {name: {eq}})`, writes the description with `issueUpdate`, creates relations with `issueRelationCreate` (type `related`), creates the benchmark child with `issueCreate` (`parentId`), then `issueUpdate` state to Done using ids from `linear-workspace.json`.
- Description under 4000 characters so it renders fully in the Linear mobile app; the full table lives in `docs/pm/pap5-decomposition.md` and is linked.
- The benchmark issue's Definition of done: run `paperos create bench-app` on a clean machine, time each stage (clone, install, first page from spec, PR opened, gates green, demo URL), record in `docs/pm/startup-benchmark.md`, target under 4 hours.
- Idempotent: re-running updates rather than duplicates (relations checked before creation).

**Definition of done**

- PAP-5 description matches the contract validator (`pnpm contract:check PAP-5` passes) while keeping the original title quoted.
- 17 `related` relations exist (verified by `issue.relations` query output pasted in the comment).
- Benchmark child issue exists in Backlog with a complete contract.
- PAP-5 is `Done`; closing comment includes the metric and links; screenshot of the closed issue at 1280 px attached.
- `docs/pm/pap5-decomposition.md` committed; changelog entry.
- Justin receives no `Needs Justin` item for this; it is informational (he can reopen by creating a new issue).

**Edge cases**

- A project from plan.json does not yet exist in Linear (Decomposer run incomplete): script lists missing ones and exits non-zero without partial updates.
- PAP-5 has been edited by Justin since planning: preserve any text he added under a `Original notes` section rather than overwriting.
- Linear rejects a relation because it already exists: treat as success.
- Closing an issue with an open child is allowed in Linear; confirm the team setting from `pm-linear/configure-workspace` does not auto-reopen it.
- Title exceeds Linear's limit if we append: do not touch the title.

**Dependencies**

- `pm-linear/configure-workspace` (states, labels, ids).
- The Decomposer run that creates projects from plan.json must have completed (tracked under `pm-linear/orchestrator` prerequisites).

**Agent**

Built by Quill (Changelog Scribe sub-agent), reviewed by Atlas.

**Size**

S: one script and two documents.
