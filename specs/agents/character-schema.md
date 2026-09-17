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
blocks: ["PAP-104", "PAP-105"]
key: "agents/character-schema"
url: "https://linear.app/paperos/issue/PAP-103/define-the-character-schema-name-role-reportsto-tools-mcp-servers"
source: "plan/specs/bucket-3.json (round-1 canonical spec JSON)"
---

# PAP-103: Define the character schema: name, role, reportsTo, tools, MCP servers, access scopes, plugins, skills, memory, escalation rules

**Goal**

Define the single typed shape every Claude character is declared in, so that roster files, `.claude/agents` definitions, MCP allowlists, permission modes, budgets, memory locations and escalation rules are all generated from one source of truth instead of hand-maintained in five places. Everything in the agents project and the orchestrator reads this schema.

**Scope**

In:
- Zod schema `packages/agents/src/schema.ts` in paperos-template exporting `CharacterSchema` and `RosterSchema`, plus a generated JSON Schema `packages/agents/schema/character.schema.json` for editor validation of YAML files.
- Fields: `name` (kebab id and display name), `role` (one sentence), `reportsTo` (character name or `justin`), `kind` (`lead` | `sub`), `parent` for subs, `description` (used as the `.claude/agents` description that drives automatic delegation), `model` (`claude-fable-5-1` default; `claude-sonnet-5` allowed for subs), `effort` (`low`..`max`), `permissionMode` (`default` | `acceptEdits` | `plan` | `dontAsk`), `tools.allow[]` / `tools.deny[]` (Claude Code tool names and `mcp__server__tool` patterns), `mcpServers[]` (names resolved against `libraries/mcp-servers` catalog), `access[]` (scope strings matching plan.json, validated against a registry), `plugins[]`, `skills[]` (names from `agents/skills-library`), `memory` (`path`, `maxTokens`), `budget` (`perSessionUsd`, `perDayUsd`, `maxTurns`), `escalation` (`rules[]` of `{when, action: needs-justin|handoff|stop, to?}`), `linear` (`labelName`, `botUser`), `forge` (`botAccount`), `prompt` (`systemPromptPath`).
- Roster file `packages/agents/roster.yaml` listing character file paths; each character in `packages/agents/characters/<name>.yaml`.
- Validation rules: sub-character `access` and `tools.allow` must be a subset of the parent lead's; `reportsTo` graph must be a tree rooted at `justin`; `mcpServers` must exist in the catalog; budgets of subs cannot exceed the parent's.
- CLI `pnpm agents validate` and `pnpm agents build` (build stubbed here; implemented in `agents/roster-v1` and `agents/tool-scopes`): emits `.claude/agents/<name>.md`, `.claude/settings.json` fragments and `.mcp.json` per character.
- `docs/agents/character-schema.md` with the field table, examples for a lead and a sub, and the reasoning for each constraint.

Out: writing the nine actual characters (`agents/roster-v1`), enforcement at runtime (`agents/tool-scopes`), UI.

**Spec**

- Access scope registry `packages/agents/src/scopes.ts`: the union of every `access` string used in plan.json `agents[]` (`linear:admin`, `repo:write (all)`, `stripe:test-mode write`...), normalised to `resource:verb[:qualifier]` and documented; unknown scopes fail validation.
- Tool names validated against a committed list of Claude Code built-ins (Read, Write, Edit, Bash, Glob, Grep, WebFetch, WebSearch, Task, TodoWrite...) plus MCP patterns; the list has a `lastVerified` date so it is refreshed.
- Generated JSON Schema wired into `.vscode/settings.json` `yaml.schemas` for authoring help.
- Golden fixtures: `fixtures/valid/atlas.yaml`, `fixtures/invalid/*.yaml` each violating one rule with the expected error code.
- Semantic versioning of the schema (`schemaVersion` field); a migration note is required for breaking changes.

**Definition of done**

- `pnpm agents validate` passes on the fixtures and fails on each invalid fixture with the expected code (Vitest).
- JSON Schema generated and checked in; editing a YAML in VS Code shows completions (screenshot).
- Doc reviewed by Quill; every field has a one-line purpose and an example.
- The nine leads and their subs from plan.json can be expressed without adding fields (dry-run conversion script output attached).
- Changelog entry; Linear comment linking doc and fixtures.

**Edge cases**

- A character needs a tool its lead lacks (Sentinel's Visual Inspector needs a vision MCP): the lead must be granted it too; the validator says so explicitly.
- Circular `reportsTo`: detected, error names the cycle.
- MCP catalog not yet published (`libraries/mcp-servers` pending): validator accepts names listed in a local `mcp-catalog.stub.json` and warns.
- Two characters share a Linear label: error; labels are unique.
- Budget omitted: inherit from parent, then from roster defaults; never unlimited.
- Model string unknown to the price table in `pm-linear/credit-metering`: warning, not error.

**Dependencies**

None (`readyNow: true`). Consumed by `agents/roster-v1`, `agents/tool-scopes`, `agents/cost-controls`, `agents/org-chart-ui`, `pm-linear/orchestrator`.

**Agent**

Built by Atlas (Decomposer sub-agent); reviewed by Sentinel (Security Auditor) because the schema defines the privilege boundary, and Quill for docs.

**Size**

S: a schema, validator and doc with fixtures.
