---
identifier: "PAP-103"
title: "Define the character schema: name, role, reportsTo, tools, MCP servers, access scopes, plugins, skills, memory, escalation rules"
project: "agents"
projectName: "Agent Characters & Orgs"
phase: "P0"
type: "Spec"
priority: 1
surfaces: ["Agent"]
milestone: "Roster defined and installed"
state: "Ready for Claude"
parent: null
children: []
blockedBy: []
blocks: ["PAP-104", "PAP-105", "PAP-284"]
key: "agents/character-schema"
url: "https://linear.app/paperos/issue/PAP-103/define-the-character-schema-name-role-reportsto-tools-mcp-servers"
source: "Linear snapshot 2026-09-17T13:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T06:43:03.703Z"
model: "claude-fable-5-1"
effort: "high"
---

# PAP-103: Define the character schema: name, role, reportsTo, tools, MCP servers, access scopes, plugins, skills, memory, escalation rules

**Goal**

Define the single typed shape every Claude character is declared in, so roster files, `.claude/agents` definitions, MCP allowlists, permission modes, budgets, memory locations and escalation rules are generated from one source of truth. Everything in this project and the orchestrator reads this schema.

**Read first.** Read before coding: [Blueprint](<https://linear.app/paperos/document/paperos-core-platform-blueprint-0c2115fe48f1>) → [Interface & Data Contracts](<https://linear.app/paperos/document/paperos-interface-and-data-contracts-d40e6a4d227c>) → your project's `Contract` section (Linear project content) → your character sheet ([Roster](<https://linear.app/paperos/document/paperos-agent-roster-org-chart-and-character-index-fc7ea7f41ff3>)) → [Execution Schedule](<https://linear.app/paperos/document/paperos-execution-schedule-1fa3d38d6795>) for your start day and the branch-start rule. The Roster and the nine character sheets linked from it are the fixtures `validateRoster` must accept unchanged; Contracts §2 row "Agent principal" fixes the key metadata `{ character, issue?, session?, scopes[] }` and the session status shape your schema feeds.

**Scope**

* In: Zod schema `packages/agents/src/schema.ts` (`CharacterSchema`, `RosterSchema`), generated JSON Schema `packages/agents/schema/character.schema.json`, the access-scope registry, the known-tools list, golden fixtures, `docs/agents/character-schema.md`.
* Out: the roster content (PAP-104), runtime enforcement (PAP-106), memory files (PAP-109).

**Spec**

* Fields: `name` (kebab id), `displayName`, `role`, `kind: lead | sub`, `reportsTo` (name or `justin`), `parent` for subs, `description` (drives Claude Code delegation), `model` (default `claude-fable-5-1`), `fallbackModel?` (must exist in the PAP-98 price table), `effort: low | medium | high | xhigh | max`, `permissionMode: default | acceptEdits | plan | dontAsk`, `tools.allow[] / deny[]` (built-in names and `mcp__server__tool` patterns), `mcpServers[]` (catalog ids from PAP-210), `access[]` (`resource:verb[:qualifier]` from the registry), `plugins[]`, `skills[]` (PAP-105 ids), `memory.path` and `memory.maxTokens`, `budget.perSessionUsd / perDayUsd / maxTurns`, `escalation[] { when, action }`, `linearLabel`, `schemaVersion`.
* Scope registry `scopes.ts`: the normalised union of every `access` string in plan.json (`linear:admin`, `repo:write:packages/ui`, `stripe:write:test`...); unknown scopes fail.
* Known tools list with `lastVerified` date; `pnpm agents validate` warns when older than 30 days.
* Fixtures: `fixtures/valid/atlas.yaml`, `fixtures/invalid/*.yaml`, one per rule with expected code; `.vscode/settings.json` wires the JSON Schema to `packages/agents/characters/*.yaml`.

**Interface contract**

* Provides: `@paperos/agents/schema` exporting `CharacterSchema`, `RosterSchema`, types `Character`, `Roster`, `AccessScope`, `EscalationRule`, `BudgetSpec`, functions `validateRoster(files)`, `resolveInheritance(roster)` (sub inherits parent defaults), `SCOPES`, `KNOWN_TOOLS`; the JSON Schema file.
* Consumers: PAP-104 (YAML files), PAP-106 (bundles from `tools`, `mcpServers`, `permissionMode`), PAP-111 (`budget`), PAP-113 (`agents.roster` returns `Character[]`), PAP-96 (`characters` path and `linearLabel` routing), PAP-91 (`Character/*` label names).
* Requires: nothing at runtime; MCP catalog ids from PAP-210 (stub `mcp-catalog.stub.json` accepted with a warning).

**Definition of done**

* `pnpm agents validate` passes the valid fixtures and fails each invalid fixture with its expected code.
* JSON Schema committed; VS Code completion screenshot attached.
* Doc lists every field with purpose and example; reviewed by Quill.
* Dry-run conversion of plan.json `agents[]` produces 37 characters without new fields (output attached).
* Changelog entry; Linear comment with doc and fixture links.

**Test plan**

* Unit (Vitest): schema parse of every fixture; error codes `REPORTS_TO_CYCLE`, `UNKNOWN_SCOPE`, `UNKNOWN_TOOL`, `DUP_LABEL`, `SUB_TOOL_NOT_IN_LEAD`, `BUDGET_MISSING`; inheritance resolution; JSON Schema snapshot.
* Property: random rosters with cycles are always rejected; acyclic rosters always accepted.
* Integration: conversion script against plan.json.
* No UI; no breakpoints.

**Demo**

Open `fixtures/valid/atlas.yaml` in VS Code and trigger completion on `permissionMode`; then run `pnpm agents validate fixtures/invalid/cycle.yaml` and read the cycle named in the error. Under one minute.

**Edge cases**

* Sub needs a tool its lead lacks: `SUB_TOOL_NOT_IN_LEAD` names both.
* Budget omitted: inherit parent, then roster defaults, never unlimited.
* Model unknown to the price table: warning.
* Two characters share `linearLabel`: error.
* Schema breaking change: `schemaVersion` bump requires a migration note in the PR.

**Dependencies**

None (`readyNow`). Blocks PAP-104, PAP-105.

**Agent**

Built by Atlas (Decomposer sub-agent); reviewed by Sentinel.

**Size**

S
