---
identifier: "PAP-836"
title: "Build the conversation runtime: streaming turns over the push transport, prompt assembly with trust tiers, tool-call loop, prompt-log ingestion and redaction"
project: "assistant"
projectName: "Tenant AI Assistant & Business Agents"
phase: "P2"
type: "Build"
priority: 2
surfaces: ["Staff"]
milestone: "Assistant contract and grounded chat"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-129", "PAP-299", "PAP-304", "PAP-381", "PAP-558", "PAP-600", "PAP-714", "PAP-833", "PAP-834"]
blocks: ["PAP-837", "PAP-838", "PAP-840", "PAP-843", "PAP-844", "PAP-846"]
key: "r4/assistant/conversation-runtime"
url: "https://linear.app/paperos/issue/PAP-836/build-the-conversation-runtime-streaming-turns-over-the-push-transport"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:51:19.717Z"
model: "claude-opus-5"
effort: "high"
estimate: 3
dueDate: "2026-10-01"
cycle: null
---

# PAP-836: Build the conversation runtime: streaming turns over the push transport, prompt assembly with trust tiers, tool-call loop, prompt-log ingestion and redaction

**Model / Effort:** Opus 5 (`claude-opus-5`) / high — Build M

**Goal**

Turn the model document into a running service: `assistant.send` accepts a turn, assembles the prompt in the documented order with grounding wrapped as untrusted content, streams deltas to the client, loops on tool calls through the two-phase rule, stores every message, and ships the redacted transcript to the prompt-log store so the assistant is as observable as the builder agents.

**Scope**

In: `packages/assistant/src/runtime/`: oRPC `assistant.start|send|list|get|feedback|abort` with `Idempotency-Key` on `send` (PAP-304); `ConversationPort` adapter; `PromptAssembler` (block budgets from the model doc); `TurnLoop` (max 6 tool iterations, then a card asking the human to continue). Streaming: `publishLiveEvent('assistant.delta', { conversationId, seq, part })` over PAP-381; server persists partial text every 2 s so a reload resumes; `abort` cancels the provider stream. Trust tiers: grounding chunks, record fields and tool results are wrapped with PAP-299 tier-3 markers; instructions found inside them are logged as `injection.suspected` security events (PAP-356) and never followed (eval-tested). Prompt-log ingestion: each turn posts a session of kind `assistant` to PAP-129 with tenant, surface, character, tokens, cost, tool calls; redaction runs before ingest. Budget guard: per-tenant daily message and token limits from PAP-844 (stubbed constants until it lands); PAP-111 kill switch flag `assistant.enabled` honoured at every turn.

Out: UI (panel and widget issues). Tool definitions (action catalogue). Retrieval internals.

**Spec**

* A turn is one transaction for storage and at-least-once for streaming: the message row is written `status: streaming` first, deltas follow, the final row update carries tokens and latency; clients treat `seq` gaps as a reason to refetch
* Tool loop: model returns `tool_use` → runtime resolves the tool in the catalogue → `read` executes immediately with the human principal → others become a `proposed` ToolCall and the turn pauses until `assistant.confirm` (own procedure, also idempotent)
* Conversation window: last 20 messages or 6k tokens, older turns summarised by a cheap model call (Haiku 4.5 tier) into a stored `summary` part, once per 20 turns
* Every model call carries `metadata.user_id` as an opaque hash so provider-side abuse tooling works without PII
* Feedback: thumbs and free text per assistant message stored on the message; `assistant.feedback.given` event feeds the eval issue

**Interface contract**

Provides: `assistant.*` procedures, `ConversationPort` default adapter, `assistant.delta` live event kind, prompt-log session kind `assistant`, `TurnLoop` extension point for tools. Consumes: `ModelProviderPort` and schemas (model issue), push transport (PAP-381), prompt-log ingest (PAP-129), trust tiers (PAP-299), idempotency (PAP-304), security events (PAP-356), kill switch (PAP-111). Consumed by: PAP-837, PAP-841, PAP-838, PAP-839, PAP-840, workflows agent step.

**Definition of done**

* A grounded turn streams in the demo tenant end to end with the mock and the Anthropic adapter; reload mid-stream resumes; abort stops provider billing within 1 s
* Prompt-log browser (PAP-135) shows assistant sessions with redacted transcripts and tool calls
* Injection fixture set (10 poisoned records) produces zero followed instructions and 10 security events
* Every new page has a `page.spec.yaml` (PAP-114) that passes the validator, declared loading, empty, error and denied states, and Gate 3 screenshots at 375, 768, 1024 and 1920 in light and dark themes.
* Linear comment on the issue with the evidence links (PR, gate artefacts, recording or report) and the module docs page updated where the interface changed.

**Test plan**

* Unit: assembler budgets, window summarisation trigger, tool loop state machine (proposed → confirmed → executed, denied path), redaction before ingest.
* Integration: mock provider streaming with a forced disconnect at delta 5 resumes at 6; idempotent `send` replay returns the stored message; kill switch returns `ASSISTANT_DISABLED` (503) with copy from PAP-368.
* E2E: two browser contexts on one conversation see the same deltas (multi-window PAP-145).
* Isolation: the PAP-34 cross-tenant harness auto-enrols every new table; one negative case per new oRPC procedure proves `NOT_FOUND` on a foreign tenant row.

**Demo**

In `/demo/assistant`, ask "summarise Acme's open invoices"; watch tokens stream, a citation chip open the record, and the session appear in the prompt-log browser with tokens and cost.

**Edge cases**

* Model returns malformed tool input: the runtime replies to the model with the Zod error once, then surfaces a card "I could not complete that" after the second failure
* Human closes the tab with a `proposed` tool call: it expires after 15 minutes and the conversation records `denied: timeout`
* Conversation shared with a second staff member: permission checks use the sender of each turn, so a less-privileged colleague cannot piggyback on earlier grounding (grounding is recomputed per turn)
* Module disabled for the tenant (PAP-266): routes return `MODULE_DISABLED` (409), slot fills unmount and the manifest declares the dependency so consumers fail closed rather than half-render.

**Dependencies**

Model issue and PAP-833 (hard), PAP-381 (hard: streaming), PAP-129 (hard), PAP-299 and PAP-304 (hard), PAP-356 and PAP-111 (soft).

**Agent**

Builder: Nova. Reviewer: Sentinel (Security Auditor).

**Size**

M: one session.

*Round 4 critique fix (2026-09-18):* resolved 7 round-4 file keys in this description to Linear identifiers: `r4/assistant/action-catalogue` = PAP-838, `r4/assistant/contract-publish` = PAP-833, `r4/assistant/metering-limits` = PAP-844, `r4/assistant/nl-to-views` = PAP-839, `r4/assistant/portal-assistant` = PAP-841, `r4/assistant/staff-chat-panel` = PAP-837, `r4/assistant/summaries-and-drafting` = PAP-840.
