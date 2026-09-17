---
key: "agents/roster-v1/yaml"
title: "Roster: convert the plan.json roster to 37 validated character YAML files"
project: "agents"
parent: "PAP-104"
phase: "P0"
type: "Build"
priority: null
size: "S"
surfaces: ["Agent"]
milestone: null
intendedState: "Backlog"
blockedBy: []
blocks: ["agents/roster-v1/lead-prompts", "agents/roster-v1/sub-prompts", "agents/roster-v1/build"]
source: "round2/agent2/new_agents.py"
linearDocument: "https://linear.app/paperos/document/round-2-pending-issues-agents-9-85624b15630d"
status: "pending"
---

# Roster: convert the plan.json roster to 37 validated character YAML files

**Goal**

Produce the structured half of the roster: one validated YAML per character (nine leads, 28 subs) generated from plan.json `agents[]` and completed with model, effort, permission mode, budgets, skills, memory paths and escalation rules, plus `roster.yaml` defaults, so prompt writers and the build tool start from files that already pass `pnpm agents validate`.

**Scope**

* In: `scripts/plan-to-roster.ts` (one-time converter, kept for re-runs), `packages/agents/characters/<name>.yaml` for all 37, `packages/agents/roster.yaml` (defaults, budget shares, `fallbackModel`), `pnpm agents tree`.
* Out: prompt prose (sibling children), `.claude/agents` generation (`agents/roster-v1/build`), bundles (PAP-106).

**Spec**

* Names: kebab ids (`atlas`, `page-spec-writer`), `displayName` from the plan; `kind`, `reportsTo`, `parent`, `role`, `description` (one sentence with trigger phrases, refined by the sub-prompts child), `linearLabel: Character/<Lead>` for leads only.
* Defaults in `roster.yaml`: leads `claude-fable-5-1`, `xhigh`, `acceptEdits`; read-mostly subs Sonnet at `medium`; Sentinel subs `high`, `plan`, deny Write and Edit; `fallbackModel` chosen from the PAP-98 price table ids (no model named in prompts).
* Budgets: daily allowance split by area share (Sentinel tree 30 percent, Atlas 8, builders share the rest, research 5); `perSessionUsd` by role (lead 40, sub 15), `maxTurns` 200 lead, 80 sub.
* `access[]` normalised to the PAP-103 scope registry; `mcpServers[]` from PAP-210 stub names; `skills[]` from PAP-105 ids; `memory.path` per character; escalation rules shared plus Atlas's cycle rule.
* `pnpm agents tree` prints the org tree and diffs against plan.json structure.

**Interface contract**

* Provides: the 37 YAML files, `roster.yaml`, `pnpm agents tree [--check]`, `plan-to-roster.ts`.
* Consumers: `agents/roster-v1/lead-prompts` and `agents/roster-v1/sub-prompts` (fields to describe), `agents/roster-v1/build` (input), PAP-106, PAP-111 budgets, PAP-113 roster.
* Requires: PAP-103 schema and validator; plan.json.

**Definition of done**

* `pnpm agents validate` passes all 37; `pnpm agents tree --check` matches plan.json.
* Every `access` string resolves in the registry; every skill id exists in `skills.json` or is marked `planned`.
* Budget shares sum to 100 percent (test).
* Changelog; Linear comment with the tree output.

**Test plan**

* Unit: converter output snapshot; budget sum; label uniqueness; inheritance resolution for subs.
* Integration: validator run over the directory in CI.
* No UI.

**Demo**

Run `pnpm agents tree` and read the nine leads with their subs indented; open `characters/sentinel.yaml` and point at `permissionMode: plan` and the deny list. Under one minute.

**Edge cases**

* Plan sub name with spaces and punctuation ("Motion and Input Stylist"): id `motion-and-input-stylist`, display name intact.
* Two subs with the same role text across leads: allowed; descriptions differ.
* Missing access for a sub: inherits the lead's subset, never more.
* `fallbackModel` not in price table: validator warning blocks merge here.
* Plan changes later: re-run converter with `--merge` preserving hand edits.

**Dependencies**

Blocked by PAP-103 (through the parent). Blocks the three sibling children.

**Agent**

Built by Atlas (Decomposer sub-agent); reviewed by Sentinel.

**Size**

S
