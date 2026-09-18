---
identifier: "PAP-709"
title: "Least privilege: per-character runtime bundles (`settings.json`, `.mcp.json`, `hooks.json`), the `enforce-scope` PreToolUse hook and `loadBundle()`"
project: "agents"
projectName: "Agent Characters & Orgs"
phase: "P0"
type: "Build"
priority: 1
surfaces: ["Agent"]
milestone: "Roster defined and installed"
state: "Backlog"
parent: "PAP-106"
children: []
blockedBy: ["PAP-48", "PAP-104", "PAP-287", "PAP-521"]
blocks: ["PAP-298", "PAP-710", "PAP-711", "PAP-715", "PAP-717"]
key: "r4/agents/character-bundles-and-enforce-scope-hook"
url: "https://linear.app/paperos/issue/PAP-709/least-privilege-per-character-runtime-bundles-settingsjson-mcpjson"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:20:23.863Z"
model: "claude-sonnet-5"
effort: "high"
estimate: 3
dueDate: "2026-09-24"
cycle: null
---

# PAP-709: Least privilege: per-character runtime bundles (`settings.json`, `.mcp.json`, `hooks.json`), the `enforce-scope` PreToolUse hook and `loadBundle()`

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / high — Build M

**Goal**

First half of PAP-106: make the schema's `tools`, `mcpServers`, `permissionMode` and `access` real at launch time. `pnpm agents build` emits one bundle per character that the orchestrator hands to the Agent SDK, and a `PreToolUse` hook denies anything outside the bundle with a reason that names the schema field. The probe suite that proves it is the sibling child.

**Scope**

* In: `packages/agents/src/bundle.ts` extending the PAP-287 build with `dist/<name>/{settings.json,.mcp.json,hooks.json}`, `packages/agents/hooks/enforce-scope.ts`, `loadBundle(name)` consumed by PAP-282 `launchSession`, the always-deny set, sub-character bundle derivation (Task tool passes the sub's own bundle), stale-bundle refusal in the launcher, `docs/agents/bundles.md`.
* Out: secrets injection (`secretsFor`, moved to PAP-300 broker placeholders), the probe suite and privilege matrix (sibling), the full deny list (PAP-298 extends this hook), container isolation (PAP-280).

**Spec**

* `settings.json`: `permissions.allow` from `tools.allow[]`, `permissions.deny` = always-deny set (`Bash(git push*main*)`, `Bash(rm -rf*)`, `Bash(curl*|sh)`, `Write(.claude/settings.json)`, `Write(ops/secrets/**)`) plus `tools.deny[]`, `permissions.defaultMode` from `permissionMode`; `.mcp.json` lists only `mcpServers[]` from the PAP-210 catalog with env var names, never values; `hooks.json` wires `PreToolUse` to `enforce-scope.ts` and the PAP-107 logging hooks.
* `enforce-scope.ts` reads hook JSON from stdin, normalises Bash strings (quotes, whitespace, `$IFS`, `sh -c`) with `shell-quote`, matches path globs for file tools relative to the worktree, exact `mcp__server__tool` names with `mcp__server__*` allowed only for catalog servers marked `readOnly`; returns `permissionDecision: deny` with `reason: '<character> lacks <scope>; change tools.allow in characters/<name>.yaml'`; unknown tools fail closed; the decision is logged as `scope-denied` (PAP-107) in under 100 ms.
* Sub-characters: `Task` invocations receive the sub's bundle derived at build time (`SUB_TOOL_NOT_IN_LEAD` already prevents widening); the hook reads `PAPEROS_CHARACTER` to pick the policy.
* `loadBundle(name): { allowedTools, disallowedTools, permissionMode, mcpServers, hooks, envNames, bundleHash }`; the launcher refuses a bundle whose `bundleHash` differs from `roster.json.promptHash` inputs (stale build).
* Temporary scope: label `scope:+<name>` on the issue adds one scope for that session only and is logged.

**Interface contract**

* Provides: bundle layout, `loadBundle()`, hook event `scope-denied`, the always-deny set constant, `scope:+<name>` label contract.
* Consumes: PAP-287 build and `roster.json`, PAP-103 schema fields, PAP-210 catalog `readOnly` flags, PAP-107 log format, PAP-282 launcher (soft: default allowlist until wired).

**Definition of done**

* Bundles for 37 characters generated deterministically; `--check` in Gate 1.
* Hook fixtures: 40 obfuscated commands (`g''it push`, `sh -c 'rm -rf /'`, path traversal, MCP wildcard on a write server) denied with the right reason; 15 benign commands allowed; p95 under 100 ms.
* Recorded Beacon session asking to `git push origin main` denied with the schema-field reason; stale bundle refused by the launcher (test).
* Docs; changelog; Linear comment with the fixture table and recording.

**Test plan**

* Unit: matcher cases, bundle snapshot per kind, hash staleness, sub-bundle derivation.
* E2E: `claude -p` session with the bundle on a toy worktree; launcher integration with mocked SDK options.

**Demo**

Launch a Beacon session in a toy worktree and ask it to `git push origin main`; read the denial naming `repo:write` and the YAML file to change. Then `pnpm agents build --check`. Ninety seconds.

**Edge cases**

* Tool renamed in a Claude Code release: unknown tool fails closed; the `lastVerified` alert in the nightly probe (sibling) catches it.
* Hook script crashes: Claude Code blocks the tool on non-zero exit; `hook-error` logged.
* Character needs a one-off scope: `scope:+<name>` with a comment; expires with the session.
* Bundle used outside the orchestrator (`pnpm agents run`): same files, same hook; no orchestrator-only paths assumed.

**Dependencies**

Hard: PAP-287. Soft: PAP-210, PAP-107, PAP-282, PAP-103.

**Agent**

Builder: Forge (Ops Runner) with Atlas (Dispatcher) on the launcher. Reviewer: Sentinel (Security Auditor).

**Size**

M: one session.
