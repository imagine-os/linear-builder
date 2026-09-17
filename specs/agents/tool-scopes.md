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
blockedBy: ["PAP-104", "PAP-48"]
blocks: []
key: "agents/tool-scopes"
url: "https://linear.app/paperos/issue/PAP-106/implement-per-character-mcp-allowlists-and-permission-modes-and-verify"
source: "plan/specs/bucket-3.json (round-1 canonical spec JSON)"
---

# PAP-106: Implement per-character MCP allowlists and permission modes and verify least privilege with an automated test

**Goal**

Make the character schema's `tools`, `mcpServers`, `permissionMode` and `access` real: every session launched for a character runs with exactly the allowlist the schema declares, and an automated test proves no character can call a tool, MCP server or forge credential outside its scope. This is the least-privilege guarantee that lets the org run unattended.

**Scope**

In:
- `pnpm agents build` emits per-character runtime bundles in `packages/agents/dist/<name>/`: `settings.json` (`permissions.allow`, `permissions.deny`, `permissions.defaultMode`), `.mcp.json` (only the servers listed, with env var names not values), and `hooks.json` (a `PreToolUse` hook that re-checks the allowlist as defence in depth).
- Orchestrator integration: `pm-linear/orchestrator` passes `allowedTools`, `disallowedTools`, `permissionMode`, `mcpServers` from the bundle to the Agent SDK `query()` options and sets `settingSources` so project settings are merged; a session cannot start if the bundle is stale (`build --check`).
- Credential scoping: forge tokens from `forge/bot-accounts` and Linear/Stripe/Webflow keys are injected per character from a secrets map (`ops/secrets/characters.env.sops`) so Beacon never sees a repo-admin token; `access[]` strings map to concrete secret names in `packages/agents/src/access-map.ts`.
- Least-privilege test suite `packages/agents/tests/least-privilege.test.ts`: for each character, launch a short `claude -p` session (or SDK query) with a prompt that tries a forbidden action (write a file for a reviewer, call `mcp__stripe__*` for Iris, `Bash(git push origin main)` for everyone) and assert the tool call is denied in the transcript; also positive checks that allowed tools work.
- Static cross-check: `access[]` versus actually mounted secrets versus MCP servers; any secret present without a matching scope fails the build.
- Report `docs/agents/privilege-matrix.md` generated: characters as rows, tools/servers/secrets as columns.

Out: OS-level sandboxing (Docker per session is handled by the orchestrator deploy), Forgejo permission configuration (`forge/bot-accounts`), production access reviews.

**Spec**

- Deny always includes: `Bash(git push*main*)`, `Bash(rm -rf*)`, `Bash(curl*|sh)`, `Write(.claude/settings.json)`, `Write(ops/secrets/**)`; allow lists are additive per character.
- `PreToolUse` hook script `packages/agents/hooks/enforce-scope.ts` reads the bundle, matches `tool_name` and `tool_input` against allow/deny (glob on Bash command strings, path globs for file tools, `mcp__server__tool` for MCP), returns permission decision `deny` with a reason that names the schema field to change.
- Hook logs every denial to the prompt log (`agents/prompt-logging-hook`) with `event: "scope-denied"`.
- Test runs in CI nightly and on any change to `packages/agents/**` or `.claude/**`; per-run cost capped (Sonnet 5 at `low` effort, `maxTurns: 3`) and recorded by metering.
- Secrets never appear in bundles or logs; a scan asserts no value from the secrets map appears in `dist/`.

**Definition of done**

- Bundles generated for all 37 characters; `--check` in CI.
- Least-privilege suite passes: every forbidden probe denied, every allowed probe succeeds; results table attached (37 rows).
- Hook denial demonstrated in a recorded session with the reason text visible.
- Privilege matrix doc generated and reviewed by Sentinel (Security Auditor).
- Secrets scan passes; sops-encrypted file documented in the runbook.
- Changelog entry; Linear comment with the results table and recording.

**Edge cases**

- Tool renamed in a Claude Code release: hook fails closed (unknown tool denied) and the known-tools list has a `lastVerified` alert in the nightly run.
- MCP server exposes a new dangerous tool: allowlists use explicit `mcp__server__tool` names, not `mcp__server__*`, except for read-only servers marked `readOnly: true` in the catalog.
- Bash command obfuscation (`g''it push`): hook normalises quotes and whitespace; still flagged by the Security Auditor as best-effort, hence Docker isolation and branch protection remain the real wall.
- Sub-agent spawned by a lead inherits a wider scope: the Task tool passes the sub's own bundle; test spawns a sub and probes.
- Character needs a temporary extra scope for one issue: issue label `scope:+<name>` grants it for that session only and posts a comment; expires with the session.
- Hook script itself fails (syntax error): Claude Code treats a hook error as blocking; CI lints hooks.

**Dependencies**

- `agents/roster-v1` (characters to build bundles for).
- `forge/bot-accounts` (per-character forge tokens).
- Integrates with `pm-linear/orchestrator` launch options and `libraries/mcp-servers` catalog.

**Agent**

Built by Forge (Ops Runner) for secrets and bundles, Atlas (Dispatcher) for orchestrator wiring; reviewed by Sentinel (Security Auditor, mandatory) and Code Reviewer.

**Size**

M: generation is simple; the probe suite and secrets plumbing take the time.
