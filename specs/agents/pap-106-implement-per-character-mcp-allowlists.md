---
identifier: "PAP-106"
title: "Implement per-character MCP allowlists and permission modes and verify least privilege with an automated test"
project: "agents"
projectName: "Agent Characters & Orgs"
phase: "P0"
type: "Build"
priority: 1
surfaces: ["Agent"]
milestone: "Roster defined and installed"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-48", "PAP-104", "PAP-287"]
blocks: ["PAP-298"]
key: "agents/tool-scopes"
url: "https://linear.app/paperos/issue/PAP-106/implement-per-character-mcp-allowlists-and-permission-modes-and-verify"
source: "Linear snapshot 2026-09-17T13:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T13:06:17.918Z"
---

# PAP-106: Implement per-character MCP allowlists and permission modes and verify least privilege with an automated test

**Goal**

Make the schema's `tools`, `mcpServers`, `permissionMode` and `access` real: every session launched for a character runs with exactly the allowlist the schema declares, and an automated test proves no character can call a tool, MCP server or forge credential outside its scope. Together with the sandbox (PAP-280) and branch protection this is the least-privilege wall.

**Scope**

* In: per-character runtime bundles from `pnpm agents build`, the `PreToolUse` enforcement hook, per-character secret injection from a sops map, the least-privilege probe suite, the privilege matrix document.
* Out: container isolation and egress control (PAP-280), forge bot account creation (PAP-48), budget limits (PAP-111).

**Spec**

* Bundle `packages/agents/dist/<name>/`: `settings.json` (`permissions.allow`, `permissions.deny`, `permissions.defaultMode`), `.mcp.json` (only listed servers, env var names not values), `hooks.json` (`PreToolUse` to `enforce-scope.ts`, plus PAP-107 logging hooks).
* Deny always includes `Bash(git push*main*)`, `Bash(rm -rf*)`, `Bash(curl*|sh)`, `Write(.claude/settings.json)`, `Write(ops/secrets/**)`; allow lists are additive.
* `enforce-scope.ts` matches `tool_name` and `tool_input` (glob on Bash strings after quote and whitespace normalisation, path globs for file tools, exact `mcp__server__tool` names; `mcp__server__*` only for catalog servers marked `readOnly`), returns `deny` with a reason naming the schema field; fails closed on unknown tools.
* Secrets: `ops/secrets/characters.env.sops` maps `access[]` scopes to concrete variables; the orchestrator injects only that character's variables; PAP-48 tokens per character with a single shared bot token as the fallback so this issue is not blocked on bot accounts.
* Probe suite `packages/agents/test/least-privilege.test.ts`: for each character one allowed and one forbidden probe per tool class (file, Bash, MCP, forge API), run nightly with Sonnet at `low` effort, `maxTurns: 3`, cost recorded.

**Interface contract**

* Provides: bundle layout above, `loadBundle(name): { allowedTools, disallowedTools, permissionMode, mcpServers, hooks, envNames }` consumed by the SDK `query()` options, `secretsFor(name): Record<string,string>` (server-side only), `docs/agents/privilege-matrix.md` generated table, hook event `scope-denied` in the PAP-107 log format.
* Consumers: PAP-96 session launch, PAP-110 eval runner (same bundles), PAP-280 (mounts only `secretsFor` output), PAP-112 (matrix), PAP-60 (agent principal keys map to scopes).
* Requires: PAP-104 roster, PAP-107 log format, PAP-210 catalog `readOnly` flags, PAP-48 tokens (soft).
* Contract source: [Interface & Data Contracts](<https://linear.app/paperos/document/paperos-interface-and-data-contracts-d40e6a4d227c>) §2 row "Agent principal" (`user` rows with `kind='agent'`, API-key metadata `{ character, issue?, session?, scopes[] }`, prefix `pos_agent_`) and §5 (`.claude/` is owned by agents; `packages/agents` holds the bundles). Threat Model source: [PaperOS Security & Threat Model](https://linear.app/paperos/document/paperos-security-and-threat-model-51fd5fd8929c) §4 (the deny list in `ops/security/agent-deny.yaml` is enforced by this issue's PreToolUse hook and by removing `destructive`-scoped MCP tools from every character except Atlas, with a server-side backstop for every S0 rule) and §5 (per-agent scoped tokens, `broker:*` placeholders injected by the egress proxy, `secretsFor` is the only path a secret reaches a session).

**Definition of done**

* Bundles for 37 characters; `--check` in CI.
* Probe suite: every forbidden probe denied, every allowed probe succeeds; 37-row table attached.
* Recorded session showing a hook denial with its reason.
* Privilege matrix reviewed by Sentinel (Security Auditor).
* Secrets scan of `dist/` finds no value from the map; runbook documents the sops file; changelog; Linear comment with table and recording.

**Test plan**

* Unit: matcher cases (obfuscated `g''it push`, path traversal, MCP wildcard on non-readOnly server), bundle generation snapshot, secret scoping.
* Integration: hook invoked with real Claude Code hook JSON fixtures; stale-bundle refusal in the launcher.
* e2e: nightly probe suite; label `scope:+<name>` grants a temporary scope for one session and expires.
* No visual breakpoints.

**Demo**

Launch a Beacon session in a toy worktree and ask it to `git push origin main`; the hook denies with "Beacon lacks `repo:write`; change `tools.allow` in `characters/beacon.yaml`". Then run `pnpm agents probe --character beacon` and read the row. Ninety seconds.

**Edge cases**

* Tool renamed in a Claude Code release: fail closed; `lastVerified` alert in the nightly run.
* Sub spawned by a lead: Task tool passes the sub's own bundle; probe spawns a sub.
* Hook script crashes: Claude Code blocks the tool on non-zero exit; the log records `hook-error`.
* Character needs a one-off scope: `scope:+<name>` label with an explanatory comment.
* Secret missing from the map: session refuses to start, names the scope.

**Dependencies**

Blocked by PAP-104, PAP-48 (soft in practice: single bot token fallback), PAP-280. Consumed by PAP-96, PAP-110.

**Agent**

Built by Forge (Ops Runner) for secrets and bundles, Atlas (Dispatcher) for launcher wiring; reviewed by Sentinel (Security Auditor).

**Size**

M
