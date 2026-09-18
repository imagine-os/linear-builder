---
identifier: "PAP-834"
title: "Specify the assistant model: conversations, messages, grounding citations, tool calls and the ModelProviderPort (Anthropic first, tenant BYO key)"
project: "assistant"
projectName: "Tenant AI Assistant & Business Agents"
phase: "P2"
type: "Spec"
priority: 2
surfaces: ["Developer"]
milestone: "Assistant contract and grounded chat"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-60", "PAP-129", "PAP-299", "PAP-302", "PAP-303", "PAP-353", "PAP-556", "PAP-587", "PAP-714"]
blocks: ["PAP-833", "PAP-835", "PAP-836"]
key: "r4/assistant/model-and-provider-port"
url: "https://linear.app/paperos/issue/PAP-834/specify-the-assistant-model-conversations-messages-grounding-citations"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:51:41.818Z"
model: "claude-fable-5-1"
effort: "max"
estimate: 3
dueDate: "2026-10-01"
cycle: null
---

# PAP-834: Specify the assistant model: conversations, messages, grounding citations, tool calls and the ModelProviderPort (Anthropic first, tenant BYO key)

**Model / Effort:** Fable 5.1 (`claude-fable-5-1`) / max — Spec M

**Goal**

Decide once how the platform talks to a model and remembers what was said: the conversation and message tables, the citation and tool-call shapes every copilot reuses, the `ModelProviderPort` with Anthropic as the first adapter and a tenant-supplied key as the second, the prompt assembly order with PAP-299 trust tiers, and the attribution rule (the assistant is an agent principal acting on behalf of a human). Everything else in this project is an implementation of this document.

**Scope**

In: `docs/assistant/model.md` (ADR PAP-130 style) and Zod schemas in `packages/contracts/assistant/src/model.ts`: `Conversation` (`id uuidv7`, `tenant_id`, `owner_principal`, `surface: 'console'|'portal'|'view'|'record'|'api'`, `character_id?`, `anchor: EntityRef?`, `status`), `Message` (`role`, `parts: (text|citation|toolCall|toolResult|card)[]`, `tokens_in`, `tokens_out`, `model`, `latency_ms`, `redacted`), `Citation` (`entityRef`, `chunkId`, `quote`, `score`), `ToolCall` (`tool`, `input`, `scopeClass`, `status: proposed|confirmed|executed|undone|denied`). `ModelProviderPort`: `complete`, `stream` (async iterable of deltas over PAP-381), `embed` (delegating to the PAP-39 `EmbeddingProvider`), `countTokens`, `capabilities()`; adapters `anthropic` (Messages API with tool use, prompt caching for the system block) and `tenantKey` (same adapter, key read through PAP-353 `encrypted()` column on `tenant_ai_settings`); `mock` for tests. Prompt assembly order: platform system block (rules from PAP-134 objects) → character persona → tenant terminology (PAP-126) → grounding chunks wrapped as untrusted content with PAP-299 tier markers → conversation window → user turn; a token budget per block with truncation order documented. Attribution: the assistant runs as agent principal `assistant@<tenant>` (PAP-60) with `onBehalfOf: <human principal>`; every audit row (PAP-38) records both; permission checks always evaluate the human, never the agent. Retention and redaction: messages inherit PAP-355 rules; PII redaction before prompt-log ingestion (PAP-129) using the `pii` annotations; tenants can set `retainTranscripts: 0..365` days.

Out: Implementation of any adapter beyond the interface and the mock. Model choice per task (each copilot issue picks within the port). Fine-tuning, training, embeddings storage (PAP-39 owns).

**Spec**

* One model call never sees data the human could not read: retrieval is filtered by the PAP-228 SQL predicate for the human principal before ranking, and tool results pass through the same `can()` check; this rule is stated as an invariant with a conformance case id
* Tool calls are two-phase by default: the model proposes, the human confirms in a card, the platform executes through PAP-291 or an oRPC procedure with `Idempotency-Key`; `scopeClass: read` tools may auto-execute, `write` requires confirmation, `send` and `money` are never auto-executed and produce a `pending_approval` item instead
* Streaming: deltas travel over `useLiveEvents` (PAP-381) keyed by `conversation_id`; the client reconciles by `seq`; a dropped stream resumes from the stored partial message
* Cost: every message records tokens and model; `recordUsage('assistant.tokens.in|out')` is called by the runtime, not by adapters, so BYO keys are metered for limits even when not billed
* Provider failover: `anthropic` → retry with backoff (PAP-43 semantics) → degraded answer "The assistant is unavailable" with the search results still shown (the panel is useful without the model)
* A `tenant_ai_settings` table: provider, encrypted key, default model, `enabledSurfaces[]`, `allowedTools[]`, `retainTranscripts`, `portalEnabled`, data-sharing acknowledgement timestamp

**Interface contract**

Provides: `docs/assistant/model.md`, Zod schemas `Conversation`, `Message`, `Citation`, `ToolCall`, `ModelProviderPort`, `tenant_ai_settings` Drizzle schema, the prompt assembly order and the attribution invariant. Consumes: `Principal`/`ActorRef` and `Money` (PAP-302, PAP-55), event envelope (PAP-303), prompt-log ingest API (PAP-129), `encrypted()` (PAP-353), agent principals (PAP-60), trust tiers (PAP-299). Consumed by: every issue in this project; PAP-391 (usage kinds), PAP-129 (session kind `assistant`), PAP-113 (assistant appears on the org chart as a tenant-scoped node).

**Definition of done**

* Document merged with a reviewed ADR; schemas exported from the contract package; migration for `conversation`, `message`, `tenant_ai_settings` with RLS policies and the PAP-34 harness enrolment
* The invariant "model never sees unreadable data" and the two-phase tool rule appear as named conformance cases in the conformance issue
* Sentinel (Security Auditor) sign-off comment on the prompt assembly order and the redaction step
* Linear comment on the issue with the evidence links (PR, gate artefacts, recording or report) and the module docs page updated where the interface changed.

**Test plan**

* Unit: schema fixtures (valid and invalid conversation, message with every part kind, tool call in each status); prompt assembler truncation order under a 2k-token budget; redaction of a message containing an email and a card-shaped number.
* Integration: mock provider round trip stores tokens and model; a `tenantKey` row decrypts only under the tenant RLS context.
* Review: threat-model delta appended to PAP-219 (new trust boundary: model provider) with STRIDE rows.

**Demo**

Walk through `docs/assistant/model.md` with the sequence diagram of one grounded, tool-using turn, then run the mock provider test that shows the audit row carrying both the assistant principal and the human it acted for.

**Edge cases**

* Tenant key revoked mid-conversation: the next turn fails with `PROVIDER_AUTH` and the settings page shows the failure; no fallback to the platform key without an explicit tenant setting
* A message longer than the context window: the assembler summarises the oldest turns into a `summary` part (stored, cited as such) rather than silently dropping them
* Provider outage: the runtime answers with search results and a banner; no retries beyond the PAP-43 policy so a stuck provider cannot burn budget

**Dependencies**

PAP-302, PAP-303 (hard: types and envelope), PAP-129 (hard: ingest shape), PAP-353 (hard: key storage), PAP-60 and PAP-299 (soft: principals and tiers exist as specs).

**Agent**

Builder: Nova. Reviewer: Sentinel (Security Auditor).

**Size**

M: one session.
