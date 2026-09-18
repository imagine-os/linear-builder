---
identifier: "PAP-284"
title: "Roster: convert the plan.json roster to 37 validated character YAML files"
project: "agents"
projectName: "Agent Characters & Orgs"
phase: "P0"
type: "Build"
priority: 1
surfaces: ["Agent"]
milestone: "Roster defined and installed"
state: "Backlog"
parent: "PAP-104"
children: []
blockedBy: ["PAP-103"]
blocks: ["PAP-285", "PAP-286", "PAP-287"]
key: "agents/roster-v1/yaml"
url: "https://linear.app/paperos/issue/PAP-284/roster-convert-the-planjson-roster-to-37-validated-character-yaml"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T13:56:11.675Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 2
dueDate: "2026-09-24"
cycle: null
---

# PAP-284: Roster: convert the plan.json roster to 37 validated character YAML files

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Build S

**Goal**

Produce the structured half of the roster: one validated YAML per character (nine leads, 28 subs) generated from plan.json `agents[]` and completed with model, effort, permission mode, budgets, skills, memory paths and escalation rules, plus `roster.yaml` defaults, so prompt writers and the build tool start from files that already pass `pnpm agents validate`.

**Scope**

* In: `scripts/plan-to-roster.ts` (one-time converter, kept for re-runs), `packages/agents/characters/<name>.yaml` for all 37, `packages/agents/roster.yaml` (defaults, budget shares, `fallbackModel`), `pnpm agents tree`.
* Out: prompt prose (sibling children), `.claude/agents` generation (PAP-287), bundles (PAP-106).

**Spec**

* Names: kebab ids (`atlas`, `page-spec-writer`), `displayName` from the plan; `kind`, `reportsTo`, `parent`, `role`, `description` (one sentence with trigger phrases, refined by the sub-prompts child), `linearLabel: Character/<Lead>` for leads only.
* Defaults in `roster.yaml`: leads `claude-fable-5-1`, `xhigh`, `acceptEdits`; read-mostly subs Sonnet at `medium`; Sentinel subs `high`, `plan`, deny Write and Edit; `fallbackModel` chosen from the PAP-98 price table ids (no model named in prompts).
* Budgets: daily allowance split by area share (Sentinel tree 30 percent, Atlas 8, builders share the rest, research 5); `perSessionUsd` by role (lead 40, sub 15), `maxTurns` 200 lead, 80 sub.
* `access[]` normalised to the PAP-103 scope registry; `mcpServers[]` from PAP-210 stub names; `skills[]` from PAP-105 ids; `memory.path` per character; escalation rules shared plus Atlas's cycle rule.
* `pnpm agents tree` prints the org tree and diffs against plan.json structure.

*Round 4 amendment (2026-09-18):*

* Defaults (round 4): `roster.yaml` lead defaults follow the plan's per-issue rule rather than a flat Fable 5.1: leads default to `claude-opus-5` / `high` as the fallback when an issue carries no Model label, Sentinel reviewer subs to `claude-opus-5` / `high` in `plan` mode (Sonnet 5 / high when the builder was Sonnet, decided per review by `resolveModel`), read-mostly subs to `claude-sonnet-5` / `medium`; Fable 5.1 is reserved for the eight keystone specs and the four release-candidate reviews as labelled in Linear.

**Interface contract**

* Provides: the 37 YAML files, `roster.yaml`, `pnpm agents tree [--check]`, `plan-to-roster.ts`.
* Consumers: PAP-285 and PAP-286 (fields to describe), PAP-287 (input), PAP-106, PAP-111 budgets, PAP-113 roster.
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
