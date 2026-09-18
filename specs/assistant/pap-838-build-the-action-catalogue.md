---
identifier: "PAP-838"
title: "Build the action catalogue: agentCallable commands and oRPC procedures as tools with scope classes, confirmation cards, preview diffs and undo"
project: "assistant"
projectName: "Tenant AI Assistant & Business Agents"
phase: "P2"
type: "Build"
priority: 4
surfaces: ["Staff"]
milestone: "Actions, copilots and portal assistant"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-38", "PAP-291", "PAP-334", "PAP-389", "PAP-833", "PAP-836"]
blocks: ["PAP-841", "PAP-842", "PAP-843", "PAP-846"]
key: "r4/assistant/action-catalogue"
url: "https://linear.app/paperos/issue/PAP-838/build-the-action-catalogue-agentcallable-commands-and-orpc-procedures"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:52.209Z"
model: "claude-opus-5"
effort: "high"
estimate: 3
dueDate: null
cycle: null
---

# PAP-838: Build the action catalogue: agentCallable commands and oRPC procedures as tools with scope classes, confirmation cards, preview diffs and undo

**Model / Effort:** Opus 5 (`claude-opus-5`) / high — Build M

**Goal**

Let the assistant do things, safely: one `ActionPort` that exposes `agentCallable` commands (PAP-291) and allow-listed oRPC procedures as model tools with the PAP-389 scope classes, renders a preview diff before any write, executes with the human's permissions and an idempotency key, and offers undo through the PAP-334 trash and history for record writes.

**Scope**

In: `packages/assistant/src/actions/`: `defineTool({ name, description, input: zod, scopeClass: 'read'|'write'|'send'|'money', preview?, execute, undo? })`; auto-generated tools from `commands.manifest.json` entries flagged `agentCallable` (PAP-291) and from oRPC procedures annotated `.meta({ assistantTool: { scopeClass } })`. Confirmation cards: input rendered from the Zod schema with the PAP-233 form adapters, preview (for record writes: before/after diff from a dry-run in a rolled-back transaction, PAP-348 pattern), Confirm, Edit, Deny; card state persisted on the ToolCall. Execution: `ActionPort.confirm(toolCallId)` runs with the human principal via `callAs` semantics, `Idempotency-Key = toolCallId`, audit reason `assistant:<conversationId>` (PAP-38); `undo` calls `records.undo` (PAP-333) or the tool's own `undo`. Tenant allow-list: `tenant_ai_settings.allowedTools[]` and per-audience overrides; `send` and `money` classes always produce approval items (workflows approvals framework when present, else a `pending_approval` row consumed by PAP-192-style queues).

Out: Autonomous multi-step plans (workflows project agent step). Tools for portal customers beyond `read` and `book|pay` handoffs (portal issue). New business logic; tools only call existing procedures.

**Spec**

* The model sees at most 24 tools per turn: the catalogue ranks by page context (commands scoped to the current route first) and tenant allow-list; a `search_tools` meta-tool exposes the rest
* Every tool description is generated from the command title, spec `purpose` and procedure Zod descriptions; a lint fails when a tool lacks a description or a scope class
* Preview is mandatory for `write` tools touching more than one row; bulk writes above 200 rows are refused with "use the bulk bar" (PAP-342)
* Denied tool calls are stored with the reason and never re-proposed in the same conversation for the same input hash
* Audit: `audit_event.actor_kind = agent`, `on_behalf_of = human`, `reason` carries the conversation id; the record activity timeline (PAP-333) shows "Assistant, confirmed by Bo"

**Interface contract**

Provides: `ActionPort` default adapter, `defineTool`, generated tool catalogue, confirmation card components, events `assistant.action.proposed|confirmed|undone`. Consumes: agent execution endpoint and `agentCallable` (PAP-291), scope classes and expression rendering (PAP-389), trash/undo and record history (PAP-334, PAP-333), audit (PAP-38), form adapters (PAP-233), dry-run transactions (PAP-348). Consumed by: PAP-841, PAP-842, workflows `agent` step, commerce order tools.

**Definition of done**

* At least 12 tools generated in the demo tenant (navigate, filter view, create record, update field, assign, comment, schedule reminder, export view, open record, search, create task, send draft → approval)
* Confirm → execute → undo round trip on a record update leaves the row and audit chain consistent; denied and expired paths tested
* Security review: no tool executes without the human principal in scope; fuzzed inputs never bypass Zod
* Every new page has a `page.spec.yaml` (PAP-114) that passes the validator, declared loading, empty, error and denied states, and Gate 3 screenshots at 375, 768, 1024 and 1920 in light and dark themes.
* Linear comment on the issue with the evidence links (PR, gate artefacts, recording or report) and the module docs page updated where the interface changed.

**Test plan**

* Unit: catalogue ranking and cap; description lint; scope class routing (read auto, write card, send/money approval).
* Integration: preview diff equals the real write diff for 20 fixture updates; idempotent confirm replay; undo restores field history.
* Adversarial: PAP-85 edge-case hunter fixtures: unicode, 10k-char inputs, tool names injected via records.
* Isolation: the PAP-34 cross-tenant harness auto-enrols every new table; one negative case per new oRPC procedure proves `NOT_FOUND` on a foreign tenant row.

**Demo**

Ask "move all of Acme's open deals to Negotiation and tell Sam"; see the preview (3 rows), confirm the write, watch the message to Sam land in the approval queue rather than being sent, then undo the write.

**Edge cases**

* Tool whose underlying command was removed by a deploy between propose and confirm: confirm fails with `TOOL_GONE` and the card explains
* Human loses permission between propose and confirm: `can()` is re-evaluated at confirm; denied with the PAP-227 explain output
* Module disabled for the tenant (PAP-266): routes return `MODULE_DISABLED` (409), slot fills unmount and the manifest declares the dependency so consumers fail closed rather than half-render.

**Dependencies**

PAP-836 (hard), PAP-291 and PAP-389 (hard), PAP-334, PAP-333, PAP-38 (hard), PAP-233 and PAP-348 (soft).

**Agent**

Builder: Nova. Reviewer: Sentinel (Security Auditor).

**Size**

M: one session.

*Round 4 critique fix (2026-09-18):* resolved 3 round-4 file keys in this description to Linear identifiers: `r4/assistant/business-characters` = PAP-842, `r4/assistant/conversation-runtime` = PAP-836, `r4/assistant/portal-assistant` = PAP-841.
