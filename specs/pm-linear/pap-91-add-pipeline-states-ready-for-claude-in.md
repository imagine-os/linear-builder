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
state: "Ready for Claude"
parent: null
children: []
blockedBy: []
blocks: ["PAP-22", "PAP-93", "PAP-94", "PAP-95", "PAP-96", "PAP-281", "PAP-503", "PAP-691", "PAP-692", "PAP-693", "PAP-694", "PAP-695", "PAP-696", "PAP-700", "PAP-701", "PAP-702", "PAP-722"]
key: "pm-linear/configure-workspace"
url: "https://linear.app/paperos/issue/PAP-91/add-pipeline-states-ready-for-claude-in-review-needs-justin-label"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T13:51:01.448Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 2
dueDate: "2026-09-20"
cycle: {"number": 1, "name": "C1 Foundation & core systems", "startsAt": "2026-09-18", "endsAt": "2026-09-25"}
---

# PAP-91: Add pipeline states (Ready for Claude, In Review, Needs Justin), label groups and project templates to Linear team PAP

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Infra S

**Needs Justin — NJ-1: upgrade the Linear workspace plan**

Upgrade the Linear workspace plan (Basic is enough) so \~165 specified issues can be created; until then the plan runs on the 275 that exist. Reply `/approve` on this issue.

**NJ-1 answered 2026-09-17: upgraded to Basic; 153 pending issues created (PAP-280..PAP-432; team PAP now has 428 issues;** `gap/data-layer/filter-grammar` **already existed as PAP-279; the four folded specs stay work packages). Create order from the NJ-1 section followed; relations and parent links added; this issue is back in Ready for Claude.**

* Why: every `issueCreate` since 2026-09-17 04:20Z returns `USAGE_LIMIT_EXCEEDED` (free-plan cap; team PAP holds 275 active issues). About 165 fully specified issues (Goal through Size) wait in the twelve "Round 2 pending issues" documents: children of PAP-96, PAP-101, PAP-104, PAP-110, PAP-119, PAP-120, PAP-124; 22 collab, realtime and input; 48 tables, business-core and growth; 29 migration and libraries; 14 app-shell, data-layer and forge gaps; 11 security; 4 contracts; 8 golden path; `agents/runtime-sandbox` and `agents/session-observability`. 49 live issues cite them as `[project/key]`.
* Nothing waits on the answer (Plan B, applied 2026-09-17 in round-2 FIX-5): the 12 hard dependencies on pending issues were folded into the citing issues as work packages. `migration/test-accounts` is now PAP-198 work package 2 (its sign-ups are a separate Needs Justin ask, NJ-13, filed from PAP-198); `gap/growth/consent-centre` is PAP-187 work package 0 (PAP-191 and PAP-193 depend on it there); `gap/business-core/recurring-dunning` is PAP-180 work package 4 (PAP-174 no longer cites it); `spec-builder/spec-versioning` is an explicit non-goal of PAP-114, which ships only a `migrate/` skeleton. No Dependencies section in a live issue names a pending key as a hard dependency any more.
* On `/approve` (plan upgraded): the session that reads the reply creates, in this order and nothing else first, (1) `agents/runtime-sandbox` (P0 safety) and (4) `agents/session-observability` via `round2/agent2/create_new.py`, (2) PAP-96's three children and (3) PAP-104's four children via the same script, then the rest by phase with `round2/agent3/create_issues.py`, `agent4/create_issues.py`, `agent5/create_issues.py`, `agent6/create_issues.py`, `apply_golden_path.py` and `create_contracts.py`, and adds the `blocks` relations each document lists. Run them only after round-2 FIX-6 (duplicate pending entries) is finished; every script is idempotent on title-in-project and the four folded keys above are skipped (`round2/folded-into-live-issues.json`). Then move this issue back to Ready for Claude.
* On `/reject <reason>`: the plan stays at 275 issues; the pending documents remain the spec of record for the uncreated work, and the builder of each parent builds its work packages on branches `<parent>/wp<n>-<slug>` as the documents describe. Move this issue back to Ready for Claude.

This issue sits in Needs Justin for NJ-1 only. The configuration work below has no human dependency and is claimable the moment the issue returns to Ready for Claude, so a `/approve` or `/reject` is all it needs.

**Goal**

Turn the Linear configuration of team PAP into code: one idempotent script that reads the live workspace, prints the diff against the plan and applies only what is missing, so every future `paperos create <app>` project gets the same states, labels and templates. The live team already has most of it from the round-1 import; this issue must never "fix" what exists.

**Read first.** Read before coding: [Blueprint](<https://linear.app/paperos/document/paperos-core-platform-blueprint-0c2115fe48f1>) → [Interface & Data Contracts](<https://linear.app/paperos/document/paperos-interface-and-data-contracts-d40e6a4d227c>) → your project's `Contract` section (Linear project content) → your character sheet ([Roster](<https://linear.app/paperos/document/paperos-agent-roster-org-chart-and-character-index-fc7ea7f41ff3>)) → [Execution Schedule](<https://linear.app/paperos/document/paperos-execution-schedule-1fa3d38d6795>) for your start day and the branch-start rule. Also [Security & Threat Model](<https://linear.app/paperos/document/paperos-security-and-threat-model-51fd5fd8929c>) §4 (Linear deny list: never archive or delete anything, never move to Done or Canceled, never touch PAP-1..PAP-12 or views) and the Execution Schedule's Needs Justin table (NJ-1 is this issue).

**Scope**

* In: `ops/linear/configure-workspace.ts` in `imagine-os/paperos-orchestrator` (`@linear/sdk`, `--check` and `--apply`), the committed snapshot `linear-workspace.json`, a `Character` label group with nine children (Atlas, Forge, Iris, Quill, Sentinel, Nova, Ledger, Beacon, Scout), the `PaperOS Spec` issue template updated to the contract sections of PAP-93, a project template with three milestones, `docs/pm/linear-setup.md`.
* Out: reconciling issue bodies and estimates (not needed: this issue treats the live workspace as correct; the former `pm-linear/workspace-reconcile` is merged here), the contract validator (PAP-93), deleting or renaming anything.

**Spec**

* Live facts the script treats as correct: states `Backlog`, `Todo`, `Ready for Claude` (unstarted), `In Progress`, `In Review`, `Needs Justin` (started), `Done`, `Canceled`, `Duplicate`; groups `Phase` (P0/P1/P2) and `Type` (Research/Spec/Build/Review/Infra/Docs); ungrouped `Customer`, `Staff`, `Developer`, `Agent` because Linear allows one label per group and 53 issues carry several surfaces; the empty `Surface` group label; `issueEstimationType: notUsed`. `Todo` stays and is documented as "human parking, never polled".
* Desired additions: `Character` group via `issueLabelCreate` with `parentId`; template body from `docs/pm/issue-contract.md`; `workflowStateUpdate` only for description and color, never name or type.
* `--check` exits 1 with a table `(kind, name, field, live, wanted)`; `--apply` creates or updates, then re-runs `--check` and must print no drift. Refuses to run unless `team.key === "PAP"` or `--team` is explicit.
* Writes `linear-workspace.json` with ids of every state, label, template and project; later scripts import ids from it.

*Round 4 amendment (2026-09-18):*

* Round 4 additions managed by the same `--check|--apply` script and recorded in `linear-workspace.json`: team settings `issueEstimationType: fibonacci`, `cyclesEnabled: true` (one-week cycles), `triageEnabled: true` with a `Triage` state; initiative ids, template ids per Type, `Pipeline:` view ids and the labels `gates-pending`, `stuck`, `slack-risk`, `critical-path`, `sla:*`, `source:slack`, `triaged`. Team-setting drift is reported as `manual` and only changed with `--apply`. `--check` runs nightly in the orchestrator and posts drift to the Plan audit issue.

**Interface contract**

* Provides: `linear-workspace.json` (`{ states: Record<StateName, id>, labels: Record<"Phase/P0" | ... | "Character/Atlas", id>, templates, projects }`), TypeScript type `WorkspaceIds` exported from `src/linear/workspace.ts`; `pnpm linear:configure --check|--apply`.
* Consumers: PAP-93 (label and state ids), PAP-96 (state ids for claims), PAP-99 (Character routing), PAP-22 (`paperos create` reuses the script).
* Requires: Linear API key with admin scope (already configured through the proxy).

**Definition of done**

* `--check` on the live team reports only the `Character` group and template drift before `--apply`, nothing after; two consecutive `--apply` runs are no-ops.
* Nine `Character` labels exist under one group; no existing label, state or issue changed name, type or state.
* `linear-workspace.json` committed and imported by the orchestrator repo's `src/linear/`.
* `docs/pm/linear-setup.md` documents the live configuration including why `Todo` and ungrouped surfaces stay; screenshot of the workflow settings at 1280 px.
* Changelog entry and a Linear comment with the diff table before and after.
* NJ-1 answered on this issue: workspace plan upgraded (and the create order above started) or Justin declined.

**Test plan**

* Unit (Vitest): diff engine against fixtures of the live snapshot (`round2/linear-snapshot.json` reduced), asserting zero destructive operations are ever planned; name matching is case-insensitive.
* Integration: mocked SDK proving `--apply` issues only `issueLabelCreate`, `templateUpdate`, `workflowStateUpdate({description,color})`.
* Live: `--check` output pasted in the issue before and after.
* No visual checks beyond the settings screenshot.

**Demo**

Run `pnpm linear:configure --check` (drift table), `--apply`, `--check` again (empty), then open Linear labels and show the `Character` group. Ninety seconds.

**Edge cases**

* A `Character` child already exists ungrouped: move it under the group with `issueLabelUpdate({parentId})`, do not create a duplicate.
* Label with the same name in another team: filter by `team.id`.
* Rate limit (`RATELIMITED` or 429): sleep 60 s and retry up to five times.
* Someone renamed a state since the snapshot: report as drift with `manual` marker, never rename back.
* API key without admin scope: fail before the first mutation.

**Dependencies**

None (`readyNow`). Blocks PAP-93, PAP-94, PAP-95, PAP-96, PAP-22.

**Agent**

Built by Atlas (Dispatcher sub-agent); reviewed by Sentinel (Code Reviewer).

**Size**

S
