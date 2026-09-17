---
identifier: "PAP-291"
title: "Agent execution endpoint, telemetry and default commands"
project: "input"
projectName: "Multi-Input Control & Accessibility"
phase: "P0"
type: "Build"
priority: 1
surfaces: ["Customer", "Staff"]
milestone: "Keyboard and command system"
state: "Backlog"
parent: "PAP-151"
children: []
blockedBy: ["PAP-290"]
blocks: ["PAP-153", "PAP-159", "PAP-165"]
key: "input/commands/agent-endpoint-defaults"
url: "https://linear.app/paperos/issue/PAP-291/agent-execution-endpoint-telemetry-and-default-commands"
source: "Linear snapshot 2026-09-17T13:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T13:05:22.997Z"
model: "claude-sonnet-5"
effort: "medium"
---

# PAP-291: Agent execution endpoint, telemetry and default commands

**Goal**

Complete PAP-151: agents run commands through an audited oRPC endpoint limited to `agentCallable` commands, every execution emits telemetry, and the default global commands ship so every app has navigation, layout and help commands from day one.

**Scope**

In:

* oRPC `commands.execute({ id, args })` for principals with scope `commands:execute`; checks `agentCallable`, `permission` via `can()`, validates `args` with `argsSchema`; audit row in PAP-38 `{ commandId, principal, args hash, result }`.
* Telemetry `command.executed { id, source: keyboard|palette|menu|voice|gamepad|api }` and `command.failed` to PAP-40; failures toast.
* Defaults: `nav.*` from spec-declared navigation, `ui.toggleSidebar|toggleInspector|toggleTheme`, `edit.undo|redo`, `help.shortcuts`, `search.open`.
* Docs page generated from the manifest.

Out: registry and palette (siblings).

**Spec**

* Server-side commands run in a headless registry with the agent's principal context; UI-only commands are marked `agentCallable: false` and rejected with `NOT_CALLABLE`.
* Rate limit per key from PAP-60 applies.

**Interface contract**

Exposes `commands.execute` contract `{ id, args } -> { ok, result | error: { code } }`, telemetry event types, default command IDs. Consumes registry (sibling 1), oRPC and `callAs` (PAP-267, PAP-268), audit writer (PAP-38), agent scopes (PAP-60), observability (PAP-40).

**Definition of done**

* Agent key executes an allowed command and is denied on a non-callable one with audit rows; defaults work in the template; docs page committed; Linear comment.

**Test plan**

* Vitest: allow and deny matrix (callable, permission, scope, schema), telemetry payloads.
* Integration: `callAs(agent)` executes `nav.goToInbox` and receives `NOT_CALLABLE` for `ui.toggleTheme`; audit rows present; `callAs(customer)` lacks scope → 403.
* Playwright: defaults toggle sidebar and theme from the palette.

**Demo**

Run `pnpm agent:cmd nav.goToInbox` with a test key and see `{ ok: true }` plus the audit row; try `ui.toggleTheme` and read `NOT_CALLABLE`. Under two minutes.

**Edge cases**

* Args fail schema: 400 with field errors.
* Command throws server-side: audited as failed, no retry.

**Dependencies**

Sibling 1, PAP-35 children (hard). PAP-38, PAP-60, PAP-40 (soft).

**Agent**

Built by Nova. Reviewed by Sentinel (Security Auditor).

**Size**

S: an endpoint, telemetry and a handful of commands.
