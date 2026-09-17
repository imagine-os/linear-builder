---
identifier: "PAP-91"
title: "Add pipeline states (Ready for Claude, In Review, Needs Justin), label groups and project templates to Linear team PAP"
project: "pm-linear"
projectName: "Project Management & Claude Pipeline"
phase: "P0"
type: "Infra"
priority: 1
surfaces: ["Agent"]
milestone: "Linear configured for the pipeline"
state: "Needs Justin"
parent: null
children: []
blockedBy: []
blocks: ["PAP-22", "PAP-93", "PAP-94", "PAP-95", "PAP-96"]
key: "pm-linear/configure-workspace"
url: "https://linear.app/paperos/issue/PAP-91/add-pipeline-states-ready-for-claude-in-review-needs-justin-label"
source: "plan/specs/bucket-3.json (round-1 canonical spec JSON)"
---

# PAP-91: Add pipeline states (Ready for Claude, In Review, Needs Justin), label groups and project templates to Linear team PAP

**Goal**

Turn Linear team PAP into the queue the whole plan assumes: the six pipeline states, four label groups, one issue template per issue type and a project template, created idempotently by a script so any future `paperos create <app>` project gets the identical setup. After this issue every other issue key in plan.json can be created with the right state, labels and template without manual clicking.

**Scope**

In:
- Workflow states on team PAP: keep `Backlog`, `Todo` (renamed to `Ready for Claude`, type unstarted, color #5E6AD2), `In Progress`, add `In Review` (started, #F2994A) and `Needs Justin` (started, #EB5757, description from plan.json `states`), keep `Done`, `Canceled`, `Duplicate`. Order: Backlog, Ready for Claude, In Progress, In Review, Needs Justin, Done, Canceled, Duplicate.
- Label groups (parent labels with children) exactly as plan.json `labels.groups`: Phase (P0/P1/P2), Type (Research/Spec/Build/Review/Infra/Docs), Surface (Customer/Staff/Developer/Agent), plus a fourth group `Character` with one child per lead in `agents[]` (Atlas, Forge, Iris, Quill, Sentinel, Nova, Ledger, Beacon, Scout) so the orchestrator can route by label.
- Issue templates via `templateCreate` (type `issue`): one per Type label, body pre-filled with the section headings the issue contract (`pm-linear/issue-contract`) will validate.
- A project template (`templateCreate` type `project`) with the three-milestone shape used across plan.json.
- Team settings: enable estimates (T-shirt: S/M/L mapped to 1/3/5), default issue state `Backlog`, auto-close parent when children done off, cycles disabled for now.
- Script `ops/linear/configure-workspace.ts` in repo `imagine-os/paperos-orchestrator` using `@linear/sdk`, run with `LINEAR_API_KEY`; idempotent (looks up by name before creating; updates color/description if drifted).
- Removing the three default labels (Bug, Feature, Improvement) only after confirming zero issues use them; otherwise archive.

Out: webhooks (`pm-linear/webhooks`), issue contract validation, PAP-5 changes, creating the ~200 plan issues (done by the Decomposer run that consumes plan.json).

**Spec**

- Use the GraphQL mutations `workflowStateCreate`/`workflowStateUpdate`, `issueLabelCreate` (with `parentId` for groups, `isGroup: true` on parents), `templateCreate`, `teamUpdate` (`issueEstimationType: "tShirt"`, `defaultIssueStateId`).
- Renaming `Todo` preserves the state id, so no issues need moving; PAP-5 stays in Backlog.
- Script exits non-zero and prints a diff table (name, field, before, after) when run with `--check`; applies with `--apply`.
- Output a `linear-workspace.json` snapshot (ids of every state, label, template) committed to the orchestrator repo; every later issue reads ids from this file rather than hard-coding.
- Document the resulting configuration in `docs/pm/linear-setup.md` with a screenshot of the workflow settings page.

**Definition of done**

- `pnpm linear:configure --check` reports no drift after `--apply` (idempotency proven by running twice).
- All six pipeline states exist in the listed order with the listed types and colors; verified via `team.states` query printed in CI log.
- Four label groups with all children exist; Bug/Feature/Improvement gone or archived.
- Issue templates appear in the Linear "New issue" template picker (screenshot attached at 1280 px and on the mobile web layout at 375 px).
- `linear-workspace.json` committed and referenced by `pm-linear/orchestrator` spec.
- `docs/pm/linear-setup.md` written; changelog entry added.
- Linear comment on this issue with the screenshot links and the snapshot file path.

**Edge cases**

- A state named `In Review` already exists with a different type: update in place, never create a duplicate.
- Label group parent exists but a child is missing: create only the child.
- Linear API rate limit (HTTP 429 or `RATELIMITED` error): back off with exponential retry up to 5 attempts.
- Renaming `Todo` fails because a Linear view filters on the name: log and continue; names in views are resolved by id.
- Running against the wrong team (key not `PAP`): refuse unless `--team` is passed explicitly.
- API key lacks admin scope: fail fast with a clear message before any mutation.

**Dependencies**

None; this is the first issue in the plan and `readyNow: true`. Consumers: `pm-linear/issue-contract`, `pm-linear/orchestrator`, `app-shell/create-cli` (reuses the script for new projects).

**Agent**

Built by Atlas (Dispatcher sub-agent); reviewed by Sentinel (Code Reviewer) for idempotency and by Justin only via the final screenshot comment.

**Size**

S: a single scripted API run against a well-documented GraphQL surface.
