from gen_common import trio

K = 'assistant'
MS = ['Assistant contract and grounded chat', 'Actions, copilots and portal assistant', 'Business characters, evals and swap']

PROJECT = {
    'key': K,
    'name': 'Tenant AI Assistant & Business Agents',
    'lead': 'Nova',
    'phase': 'P2',
    'description': 'The in-product AI layer for tenants and their customers: a grounded assistant that chats over tenant data with citations, turns natural language into views and formulas, drafts replies for approval, takes audited actions through the command registry, and lets tenants configure customer-facing business characters, all metered, evaluated and red-teamed.',
    'content': """Goal: every PaperOS app ships with an assistant the tenant's staff and customers can talk to, and the agent roster (PAP-104) is not the only kind of agent the platform knows. Today the plan's agents build the product; nothing in the eighteen projects lets a salon owner ask "who has not rebooked in 60 days?", a clinic receptionist say "draft a reminder to tomorrow's patients", or a customer ask the portal "where is my invoice?". This project adds that layer as one module: a `ModelProviderPort` (Anthropic first, tenant BYO key allowed), a conversation store under RLS, permission-filtered retrieval over the existing search registry (PAP-39) with citations, an action catalogue that reuses the `agentCallable` command endpoint (PAP-291) and oRPC scope classes with confirmation cards and undo, natural-language-to-view and formula copilots on the tables engine, drafting into `pending_approval` (the PAP-192 pattern: the assistant never sends), a customer-facing portal widget grounded on the tenant's help center with handoff to the support inbox, tenant-configurable business characters that extend the character schema (PAP-103) with a tenant scope, a red-team eval suite on the PAP-308 harness, and token metering through PAP-391. Every prompt and response lands in the prompt-log store (PAP-129) with redaction, and every action is attributed to the assistant as an agent principal (PAP-60) acting on behalf of a human. Non-goals: training or fine-tuning models, autonomous sending or money movement without a human approval step, voice (PAP-159 routes speech into the command registry, which the assistant then consumes), replacing the builder agents.

## Contract

**Provides**

* `@paperos/contract-assistant`: `ModelProviderPort` (`complete`, `stream`, `embed`, `countTokens`, provider capabilities), `ConversationPort` (`start`, `send`, `list`, `feedback`), `RetrievalPort` (`ground(query, principal, scopes)` returning chunks with `EntityRef` citations), `ActionPort` (`listTools(principal)`, `propose`, `confirm`, `undo`), `CopilotPort` (`toFilterTree`, `toFormula`, `toViewSpec`, `summarise`, `draft`), `CharacterPort` (tenant characters: `list`, `resolve(audience, surface)`), slot `assistant.panel`, `portal.assistant.widget`, `view.toolbar.ask`, `record.panel.tabs.assistant`.
* Events: `assistant.conversation.started|ended`, `assistant.action.proposed|confirmed|undone`, `assistant.draft.created`, `assistant.escalated`, `assistant.feedback.given`.
* Usage kinds registered with PAP-391: `assistant.messages`, `assistant.tokens.in`, `assistant.tokens.out`, `assistant.actions`.
* Eval tasks and graders for the PAP-308 harness under `evals/assistant/*`; the red-team fixture set.

**Requires**

* data-layer: search registry and embeddings (PAP-39), jobs (PAP-43), audit (PAP-38), field encryption for tenant API keys (PAP-353), transactional email for transcripts (PAP-370), idempotency (PAP-304), event bus (PAP-303).
* identity: `Principal` and agent principals (PAP-55, PAP-60), permission engine with SQL predicate (PAP-59, PAP-228) for retrieval filtering, portal and console shells (PAP-62, PAP-63).
* realtime: push transport for streaming tokens and job progress (PAP-381).
* tables: `FilterTree` (PAP-279), formula catalogue and parser (PAP-382), view model (PAP-161), dataset registry, bulk undo (PAP-334).
* input: command registry and the agent execution endpoint (PAP-151, PAP-291).
* collab: prompt-log store (PAP-129), comments for "ask on this thread" (PAP-131), tenant docs (PAP-379), rules and skills objects (PAP-134).
* agents: character schema and prompt-injection trust tiers (PAP-103, PAP-299), eval harness (PAP-308, PAP-310), budgets and kill switch (PAP-111).
* business-core: entitlements and metering (PAP-178, PAP-391). growth: support inbox for handoff (PAP-411), content agent drafting pattern (PAP-192).
* design-system: rich text editor (PAP-142), overlays and state components (PAP-237, PAP-234).

**Consumed by**

* engagement (help center answers, booking by chat), workflows (agent step uses `ActionPort`), commerce (order lookup in the portal widget), platform-ops (assistant usage in tenant health), growth (reply drafting in the support inbox), tables (`view.toolbar.ask` copilot).

**Owner**: Nova leads and builds; Atlas (Decomposer) consults on the runtime; Sentinel (Security Auditor) reviews every retrieval and action issue. Milestones: Assistant contract and grounded chat (2026-10-01), Actions, copilots and portal assistant (2026-10-09, deferred v0.2), Business characters, evals and swap (2026-10-16, deferred v0.2).""",
    'milestones': [
        {'name': MS[0], 'targetDate': '2026-10-01', 'description': 'Contract v0.1, model and provider port, conversation runtime, permission-filtered retrieval and the staff chat panel with citations.'},
        {'name': MS[1], 'targetDate': '2026-10-09', 'description': 'Deferred (v0.2). Action catalogue with confirmations and undo, natural language to views and formulas, summaries and drafting, the customer-facing portal assistant.'},
        {'name': MS[2], 'targetDate': '2026-10-16', 'description': 'Deferred (v0.2). Tenant business characters, red-team evals, metering and limits, conformance suite and kernel wiring.'},
    ],
}

ISSUES = [
 {
  'key': f'r4/{K}/model-and-provider-port', 'title': 'Specify the assistant model: conversations, messages, grounding citations, tool calls and the ModelProviderPort (Anthropic first, tenant BYO key)',
  'type': 'Spec', 'tier': 'fable', 'size': 'M', 'priority': 2, 'surfaces': ['Developer', 'Staff'], 'milestone': MS[0], 'deferred': False,
  'blockedBy': ['PAP-302', 'PAP-303', 'PAP-129', 'PAP-353', 'PAP-60', 'PAP-299'], 'blocks': [f'r4/{K}/contract-publish', f'r4/{K}/conversation-runtime', f'r4/{K}/retrieval-grounding'],
  'goal': "Decide once how the platform talks to a model and remembers what was said: the conversation and message tables, the citation and tool-call shapes every copilot reuses, the `ModelProviderPort` with Anthropic as the first adapter and a tenant-supplied key as the second, the prompt assembly order with PAP-299 trust tiers, and the attribution rule (the assistant is an agent principal acting on behalf of a human). Everything else in this project is an implementation of this document.",
  'scope_in': [
    "`docs/assistant/model.md` (ADR PAP-130 style) and Zod schemas in `packages/contracts/assistant/src/model.ts`: `Conversation` (`id uuidv7`, `tenant_id`, `owner_principal`, `surface: 'console'|'portal'|'view'|'record'|'api'`, `character_id?`, `anchor: EntityRef?`, `status`), `Message` (`role`, `parts: (text|citation|toolCall|toolResult|card)[]`, `tokens_in`, `tokens_out`, `model`, `latency_ms`, `redacted`), `Citation` (`entityRef`, `chunkId`, `quote`, `score`), `ToolCall` (`tool`, `input`, `scopeClass`, `status: proposed|confirmed|executed|undone|denied`)",
    "`ModelProviderPort`: `complete`, `stream` (async iterable of deltas over PAP-381), `embed` (delegating to the PAP-39 `EmbeddingProvider`), `countTokens`, `capabilities()`; adapters `anthropic` (Messages API with tool use, prompt caching for the system block) and `tenantKey` (same adapter, key read through PAP-353 `encrypted()` column on `tenant_ai_settings`); `mock` for tests",
    "Prompt assembly order: platform system block (rules from PAP-134 objects) → character persona → tenant terminology (PAP-126) → grounding chunks wrapped as untrusted content with PAP-299 tier markers → conversation window → user turn; a token budget per block with truncation order documented",
    "Attribution: the assistant runs as agent principal `assistant@<tenant>` (PAP-60) with `onBehalfOf: <human principal>`; every audit row (PAP-38) records both; permission checks always evaluate the human, never the agent",
    "Retention and redaction: messages inherit PAP-355 rules; PII redaction before prompt-log ingestion (PAP-129) using the `pii` annotations; tenants can set `retainTranscripts: 0..365` days",
  ],
  'scope_out': ['Implementation of any adapter beyond the interface and the mock', 'Model choice per task (each copilot issue picks within the port)', 'Fine-tuning, training, embeddings storage (PAP-39 owns)'],
  'spec': [
    'One model call never sees data the human could not read: retrieval is filtered by the PAP-228 SQL predicate for the human principal before ranking, and tool results pass through the same `can()` check; this rule is stated as an invariant with a conformance case id',
    'Tool calls are two-phase by default: the model proposes, the human confirms in a card, the platform executes through PAP-291 or an oRPC procedure with `Idempotency-Key`; `scopeClass: read` tools may auto-execute, `write` requires confirmation, `send` and `money` are never auto-executed and produce a `pending_approval` item instead',
    'Streaming: deltas travel over `useLiveEvents` (PAP-381) keyed by `conversation_id`; the client reconciles by `seq`; a dropped stream resumes from the stored partial message',
    'Cost: every message records tokens and model; `recordUsage(\'assistant.tokens.in|out\')` is called by the runtime, not by adapters, so BYO keys are metered for limits even when not billed',
    'Provider failover: `anthropic` → retry with backoff (PAP-43 semantics) → degraded answer "The assistant is unavailable" with the search results still shown (the panel is useful without the model)',
    'A `tenant_ai_settings` table: provider, encrypted key, default model, `enabledSurfaces[]`, `allowedTools[]`, `retainTranscripts`, `portalEnabled`, data-sharing acknowledgement timestamp',
  ],
  'provides': "`docs/assistant/model.md`, Zod schemas `Conversation`, `Message`, `Citation`, `ToolCall`, `ModelProviderPort`, `tenant_ai_settings` Drizzle schema, the prompt assembly order and the attribution invariant",
  'consumes': "`Principal`/`ActorRef` and `Money` (PAP-302, PAP-55), event envelope (PAP-303), prompt-log ingest API (PAP-129), `encrypted()` (PAP-353), agent principals (PAP-60), trust tiers (PAP-299)",
  'consumed_by': "every issue in this project; PAP-391 (usage kinds), PAP-129 (session kind `assistant`), PAP-113 (assistant appears on the org chart as a tenant-scoped node)",
  'dod': [
    'Document merged with a reviewed ADR; schemas exported from the contract package; migration for `conversation`, `message`, `tenant_ai_settings` with RLS policies and the PAP-34 harness enrolment',
    'The invariant "model never sees unreadable data" and the two-phase tool rule appear as named conformance cases in the conformance issue',
    'Sentinel (Security Auditor) sign-off comment on the prompt assembly order and the redaction step',
  ],
  'tests': {
    'Unit': 'schema fixtures (valid and invalid conversation, message with every part kind, tool call in each status); prompt assembler truncation order under a 2k-token budget; redaction of a message containing an email and a card-shaped number',
    'Integration': 'mock provider round trip stores tokens and model; a `tenantKey` row decrypts only under the tenant RLS context',
    'Review': 'threat-model delta appended to PAP-219 (new trust boundary: model provider) with STRIDE rows',
  },
  'demo': "Walk through `docs/assistant/model.md` with the sequence diagram of one grounded, tool-using turn, then run the mock provider test that shows the audit row carrying both the assistant principal and the human it acted for.",
  'edge': [
    'Tenant key revoked mid-conversation: the next turn fails with `PROVIDER_AUTH` and the settings page shows the failure; no fallback to the platform key without an explicit tenant setting',
    'A message longer than the context window: the assembler summarises the oldest turns into a `summary` part (stored, cited as such) rather than silently dropping them',
    'Provider outage: the runtime answers with search results and a banner; no retries beyond the PAP-43 policy so a stuck provider cannot burn budget',
  ],
  'deps': 'PAP-302, PAP-303 (hard: types and envelope), PAP-129 (hard: ingest shape), PAP-353 (hard: key storage), PAP-60 and PAP-299 (soft: principals and tiers exist as specs).',
  'builder': 'Nova', 'reviewer': 'Sentinel (Security Auditor)', 'tenant_data': False, 'module_edge': False,
 },
 {
  'key': f'r4/{K}/retrieval-grounding', 'title': 'Build permission-filtered retrieval over the search registry: chunking of records, docs, comments and files, hybrid ranking, citations and freshness',
  'type': 'Build', 'tier': 'opus', 'size': 'M', 'priority': 2, 'surfaces': ['Staff', 'Customer'], 'milestone': MS[0], 'deferred': False,
  'blockedBy': [f'r4/{K}/model-and-provider-port', 'PAP-39', 'PAP-228', 'PAP-59', 'PAP-43'], 'blocks': [f'r4/{K}/staff-chat-panel', f'r4/{K}/portal-assistant'],
  'goal': "Make the assistant answer from the tenant's own data without ever leaking a row the asker cannot read: a `RetrievalPort` that chunks searchable entities registered with PAP-39, keeps embeddings current through jobs, filters candidates by the human's PAP-228 SQL predicate before ranking, and returns chunks with `EntityRef` citations the UI can deep-link.",
  'scope_in': [
    "`packages/assistant/src/retrieval/`: `chunker` per entity kind (record → field-labelled text under 400 tokens; doc/comment → heading-aware chunks with overlap; file → extracted text from PAP-37 `text/*`, PDF via `pdf-parse`); table `assistant_chunk(entity_type, entity_id, chunk_ix, text, tsv, embedding vector(1024), acl_hint jsonb, updated_at)` with RLS",
    "Freshness: PAP-39 `paperos.search_upsert` trigger also enqueues `assistant.chunk` (PAP-43) with `singletonKey` per entity; deletes cascade; nightly reconcile job",
    "`ground(query, principal, { scopes, k, entityTypes })`: candidate set = `search.query(mode: hybrid)` top 50 ∩ rows visible under `compilePredicate(principal)` (PAP-228), re-ranked by reciprocal rank fusion plus recency; returns `Chunk[]` with `Citation` shapes and a `groundingReport` (counts filtered by permission, latency)",
    "`assistant.debugGrounding` procedure (staff `assistant.debug` permission) showing what was retrieved and what permission filtering removed, for support and Sentinel",
  ],
  'scope_out': ['Embedding provider hosting (PAP-39)', 'Chunking of Yjs canvases (v0.3)', 'Cross-tenant knowledge (never)'],
  'spec': [
    'Permission filtering happens in SQL (`WHERE` predicate from PAP-228 joined on the source table), not in application code, so a bug in ranking cannot leak; `acl_hint` is an optimisation only and never trusted',
    'Chunk text is stored redacted for `pii: secret` columns (PAP-355 annotations) and never for `encrypted()` columns (PAP-353)',
    'Top-k default 8, hard cap 20; total grounding budget 3k tokens; the report lists dropped chunks',
    'Citations carry `entityRef`, `route` (from the PAP-39 registry), `quote` (first 160 chars) and `score`; the UI renders them as chips that open the record panel (PAP-333) or doc',
    'Portal principals see only entities whose registry entry declares `audiences: [customer]` and pass the same predicate',
  ],
  'provides': "`RetrievalPort` implementation, `assistant_chunk` table and jobs, `assistant.debugGrounding` procedure, `Chunk`/`groundingReport` fixtures for conformance",
  'consumes': "search registry and `search.query` (PAP-39), `compilePredicate` (PAP-228), permission engine (PAP-59), jobs (PAP-43), files text extraction (PAP-37), `pii` annotations (PAP-355)",
  'consumed_by': f"`r4/{K}/conversation-runtime`, `r4/{K}/staff-chat-panel`, `r4/{K}/portal-assistant`, engagement help center answers",
  'dod': [
    'Chunks exist for every registered entity type in the demo tenant within 60 s of a write; `ground()` p95 under 400 ms on the 100k-row benchmark dataset (PAP-337)',
    'Leak test: a principal restricted by an attribute policy to `region = EU` never receives a chunk from a US row across 1,000 randomised queries',
    'Grounding report visible in the debug procedure and attached to the prompt-log session (PAP-129)',
  ],
  'tests': {
    'Unit': 'chunker boundaries (headings, 400-token cap, overlap), citation quote extraction, RRF ranking order with ties',
    'Integration': 'trigger → job → chunk row; delete cascades; predicate filtering against three audiences (admin, staff with attribute policy, customer)',
    'Property': 'fast-check: for random principals and rows, every returned chunk\'s source row is readable via a direct `can()` call',
  },
  'demo': "Ask the debug procedure \"what did we promise Acme?\" as a sales rep and as a support agent; show the two grounding reports differ only by permission filtering and every citation opens the source record.",
  'edge': [
    'Entity with 50k characters (a long doc): chunked into ≤120 chunks; embedding job batches 50 per call and resumes on failure',
    'Search registry entry without a `route`: citation renders without a link and the registry lint (PAP-39) warns the owner',
    'Embedding provider down: keyword-only grounding with a `degraded: true` flag in the report',
  ],
  'deps': f"`r4/{K}/model-and-provider-port` (hard), PAP-39 (hard), PAP-228 and PAP-59 (hard), PAP-43 (hard), PAP-37 and PAP-355 (soft).",
  'builder': 'Nova', 'reviewer': 'Sentinel (Security Auditor)',
 },
 {
  'key': f'r4/{K}/conversation-runtime', 'title': 'Build the conversation runtime: streaming turns over the push transport, prompt assembly with trust tiers, tool-call loop, prompt-log ingestion and redaction',
  'type': 'Build', 'tier': 'opus', 'size': 'M', 'priority': 2, 'surfaces': ['Staff', 'Customer', 'Developer'], 'milestone': MS[0], 'deferred': False,
  'blockedBy': [f'r4/{K}/model-and-provider-port', f'r4/{K}/contract-publish', 'PAP-381', 'PAP-129', 'PAP-299', 'PAP-304'], 'blocks': [f'r4/{K}/staff-chat-panel', f'r4/{K}/action-catalogue', f'r4/{K}/summaries-and-drafting'],
  'goal': "Turn the model document into a running service: `assistant.send` accepts a turn, assembles the prompt in the documented order with grounding wrapped as untrusted content, streams deltas to the client, loops on tool calls through the two-phase rule, stores every message, and ships the redacted transcript to the prompt-log store so the assistant is as observable as the builder agents.",
  'scope_in': [
    "`packages/assistant/src/runtime/`: oRPC `assistant.start|send|list|get|feedback|abort` with `Idempotency-Key` on `send` (PAP-304); `ConversationPort` adapter; `PromptAssembler` (block budgets from the model doc); `TurnLoop` (max 6 tool iterations, then a card asking the human to continue)",
    "Streaming: `publishLiveEvent('assistant.delta', { conversationId, seq, part })` over PAP-381; server persists partial text every 2 s so a reload resumes; `abort` cancels the provider stream",
    "Trust tiers: grounding chunks, record fields and tool results are wrapped with PAP-299 tier-3 markers; instructions found inside them are logged as `injection.suspected` security events (PAP-356) and never followed (eval-tested)",
    "Prompt-log ingestion: each turn posts a session of kind `assistant` to PAP-129 with tenant, surface, character, tokens, cost, tool calls; redaction runs before ingest",
    "Budget guard: per-tenant daily message and token limits from `r4/assistant/metering-limits` (stubbed constants until it lands); PAP-111 kill switch flag `assistant.enabled` honoured at every turn",
  ],
  'scope_out': ['UI (panel and widget issues)', 'Tool definitions (action catalogue)', 'Retrieval internals'],
  'spec': [
    'A turn is one transaction for storage and at-least-once for streaming: the message row is written `status: streaming` first, deltas follow, the final row update carries tokens and latency; clients treat `seq` gaps as a reason to refetch',
    'Tool loop: model returns `tool_use` → runtime resolves the tool in the catalogue → `read` executes immediately with the human principal → others become a `proposed` ToolCall and the turn pauses until `assistant.confirm` (own procedure, also idempotent)',
    'Conversation window: last 20 messages or 6k tokens, older turns summarised by a cheap model call (Haiku 4.5 tier) into a stored `summary` part, once per 20 turns',
    'Every model call carries `metadata.user_id` as an opaque hash so provider-side abuse tooling works without PII',
    'Feedback: thumbs and free text per assistant message stored on the message; `assistant.feedback.given` event feeds the eval issue',
  ],
  'provides': "`assistant.*` procedures, `ConversationPort` default adapter, `assistant.delta` live event kind, prompt-log session kind `assistant`, `TurnLoop` extension point for tools",
  'consumes': "`ModelProviderPort` and schemas (model issue), push transport (PAP-381), prompt-log ingest (PAP-129), trust tiers (PAP-299), idempotency (PAP-304), security events (PAP-356), kill switch (PAP-111)",
  'consumed_by': f"`r4/{K}/staff-chat-panel`, `r4/{K}/portal-assistant`, `r4/{K}/action-catalogue`, `r4/{K}/nl-to-views`, `r4/{K}/summaries-and-drafting`, workflows agent step",
  'dod': [
    'A grounded turn streams in the demo tenant end to end with the mock and the Anthropic adapter; reload mid-stream resumes; abort stops provider billing within 1 s',
    'Prompt-log browser (PAP-135) shows assistant sessions with redacted transcripts and tool calls',
    'Injection fixture set (10 poisoned records) produces zero followed instructions and 10 security events',
  ],
  'tests': {
    'Unit': 'assembler budgets, window summarisation trigger, tool loop state machine (proposed → confirmed → executed, denied path), redaction before ingest',
    'Integration': 'mock provider streaming with a forced disconnect at delta 5 resumes at 6; idempotent `send` replay returns the stored message; kill switch returns `ASSISTANT_DISABLED` (503) with copy from PAP-368',
    'E2E': 'two browser contexts on one conversation see the same deltas (multi-window PAP-145)',
  },
  'demo': "In `/demo/assistant`, ask \"summarise Acme's open invoices\"; watch tokens stream, a citation chip open the record, and the session appear in the prompt-log browser with tokens and cost.",
  'edge': [
    'Model returns malformed tool input: the runtime replies to the model with the Zod error once, then surfaces a card "I could not complete that" after the second failure',
    'Human closes the tab with a `proposed` tool call: it expires after 15 minutes and the conversation records `denied: timeout`',
    'Conversation shared with a second staff member: permission checks use the sender of each turn, so a less-privileged colleague cannot piggyback on earlier grounding (grounding is recomputed per turn)',
  ],
  'deps': f"Model issue and `r4/{K}/contract-publish` (hard), PAP-381 (hard: streaming), PAP-129 (hard), PAP-299 and PAP-304 (hard), PAP-356 and PAP-111 (soft).",
  'builder': 'Nova', 'reviewer': 'Sentinel (Security Auditor)',
 },
 {
  'key': f'r4/{K}/staff-chat-panel', 'title': 'Build the staff assistant panel: inspector slot, command palette "Ask", citations, suggested follow-ups, history and feedback',
  'type': 'Build', 'tier': 'sonnet', 'effort': 'medium', 'size': 'M', 'priority': 3, 'surfaces': ['Staff'], 'milestone': MS[0], 'deferred': False,
  'blockedBy': [f'r4/{K}/conversation-runtime', f'r4/{K}/retrieval-grounding', 'PAP-70', 'PAP-290', 'PAP-142', 'PAP-333'], 'blocks': [f'r4/{K}/nl-to-views'],
  'goal': "Give staff one place to ask: an assistant panel in the inspector slot that knows the current page and record, opens from the command palette with `?` or the `assistant.open` command, streams answers with citation chips, offers follow-ups, and keeps a searchable history per user.",
  'scope_in': [
    "`packages/assistant/src/ui/`: `<AssistantPanel/>` filling `shell.inspector` and `record.panel.tabs.assistant` (PAP-333) with context = current route spec key, selected record `EntityRef`, active view id; composer on the PAP-142 editor in local mode with `@` mentions of records and people",
    "Command palette integration: `assistant.open`, `assistant.ask` (prefilled with the palette query when no command matches, PAP-290 fallback slot), `assistant.explain-page` (uses spec `purpose`, PAP-380)",
    "Message list: streaming text, citation chips (open record panel or doc), tool-call cards (confirm, deny, view diff), `pending_approval` cards linking to the approval inbox, feedback thumbs; suggested follow-ups from the model as buttons",
    "History drawer: conversations by surface and anchor, search through PAP-39 registration `assistant_conversation` (owner-only), delete (soft, PAP-355 retention)",
    "Page spec `specs/pages/assistant/panel.page.spec.yaml`; a11y: live region for deltas throttled to sentence boundaries, focus stays in the composer, Escape closes",
  ],
  'scope_out': ['Portal widget (own issue)', 'Action definitions', 'Voice (PAP-159 routes into `assistant.ask`)'],
  'spec': [
    'Panel opens in under 100 ms with the last conversation for this anchor; first token p95 under 1.5 s on staging (dashboard in PAP-40)',
    'Context chips at the top show what the assistant can see (page, record, view) and can be removed before sending, which narrows grounding scopes',
    'Citation chips render title, entity type icon (PAP-68) and hover preview; keyboard: Tab cycles chips, Enter opens',
    'Empty state (PAP-234) offers three page-specific starter questions derived from the spec `purpose` and dataset names',
    'Multi-window (PAP-262): the panel can detach; conversation state syncs through the window bus (PAP-145)',
  ],
  'provides': "`<AssistantPanel/>`, commands `assistant.open|ask|explain-page`, slot fill for `record.panel.tabs.assistant`, `assistant_conversation` search registration",
  'consumes': "`assistant.*` procedures and live deltas (runtime), retrieval citations, `AppFrame`/`Inspector` (PAP-70), command palette (PAP-290), editor (PAP-142), record panel tabs (PAP-333), help panel purpose (PAP-380)",
  'consumed_by': f"`r4/{K}/nl-to-views` (renders view drafts in the panel), `r4/{K}/summaries-and-drafting`, growth support inbox (reply drafting card)",
  'dod': [
    'Panel works on console pages, record panels and views in the demo tenant; Storybook stories for every message part kind; axe clean',
    'Playwright: ask, stream, click citation, confirm a read tool, give feedback; screenshots at 375 (panel becomes a sheet), 1024, 1920',
  ],
  'tests': {
    'Unit': 'delta reducer with out-of-order `seq`; context chip removal narrows the `scopes` argument; follow-up buttons send the exact text',
    'E2E': 'command palette fallback routes an unmatched query into the panel; detach and re-dock keeps the conversation; screen reader announces one sentence per update (PAP-156 matrix)',
  },
  'demo': "On a CRM contact record, open the assistant tab, ask \"what did we last promise them and when is their next invoice due?\", click both citations, then give a thumbs up.",
  'edge': [
    'Very long answer (tables of 200 rows): rendered as a collapsed block with "open as view" (hands off to `nl-to-views`) instead of inline',
    'Tenant with assistant disabled: the tab and command are hidden by the `assistant.enabled` flag; deep links show `DeniedState` with the reason',
  ],
  'deps': f"`r4/{K}/conversation-runtime` and `r4/{K}/retrieval-grounding` (hard), PAP-70, PAP-290 (hard), PAP-142 and PAP-333 (soft, fallbacks exist).",
  'builder': 'Nova', 'reviewer': 'Sentinel (Visual Inspector)',
 },
 {
  'key': f'r4/{K}/action-catalogue', 'title': 'Build the action catalogue: agentCallable commands and oRPC procedures as tools with scope classes, confirmation cards, preview diffs and undo',
  'type': 'Build', 'tier': 'opus', 'size': 'M', 'priority': 4, 'surfaces': ['Staff', 'Developer'], 'milestone': MS[1], 'deferred': True,
  'blockedBy': [f'r4/{K}/conversation-runtime', 'PAP-291', 'PAP-389', 'PAP-334', 'PAP-38'], 'blocks': [f'r4/{K}/portal-assistant', f'r4/{K}/business-characters'],
  'goal': "Let the assistant do things, safely: one `ActionPort` that exposes `agentCallable` commands (PAP-291) and allow-listed oRPC procedures as model tools with the PAP-389 scope classes, renders a preview diff before any write, executes with the human's permissions and an idempotency key, and offers undo through the PAP-334 trash and history for record writes.",
  'scope_in': [
    "`packages/assistant/src/actions/`: `defineTool({ name, description, input: zod, scopeClass: 'read'|'write'|'send'|'money', preview?, execute, undo? })`; auto-generated tools from `commands.manifest.json` entries flagged `agentCallable` (PAP-291) and from oRPC procedures annotated `.meta({ assistantTool: { scopeClass } })`",
    "Confirmation cards: input rendered from the Zod schema with the PAP-233 form adapters, preview (for record writes: before/after diff from a dry-run in a rolled-back transaction, PAP-348 pattern), Confirm, Edit, Deny; card state persisted on the ToolCall",
    "Execution: `ActionPort.confirm(toolCallId)` runs with the human principal via `callAs` semantics, `Idempotency-Key = toolCallId`, audit reason `assistant:<conversationId>` (PAP-38); `undo` calls `records.undo` (PAP-333) or the tool's own `undo`",
    "Tenant allow-list: `tenant_ai_settings.allowedTools[]` and per-audience overrides; `send` and `money` classes always produce approval items (workflows approvals framework when present, else a `pending_approval` row consumed by PAP-192-style queues)",
  ],
  'scope_out': ['Autonomous multi-step plans (workflows project agent step)', 'Tools for portal customers beyond `read` and `book|pay` handoffs (portal issue)', 'New business logic; tools only call existing procedures'],
  'spec': [
    'The model sees at most 24 tools per turn: the catalogue ranks by page context (commands scoped to the current route first) and tenant allow-list; a `search_tools` meta-tool exposes the rest',
    'Every tool description is generated from the command title, spec `purpose` and procedure Zod descriptions; a lint fails when a tool lacks a description or a scope class',
    'Preview is mandatory for `write` tools touching more than one row; bulk writes above 200 rows are refused with "use the bulk bar" (PAP-342)',
    'Denied tool calls are stored with the reason and never re-proposed in the same conversation for the same input hash',
    'Audit: `audit_event.actor_kind = agent`, `on_behalf_of = human`, `reason` carries the conversation id; the record activity timeline (PAP-333) shows "Assistant, confirmed by Bo"',
  ],
  'provides': "`ActionPort` default adapter, `defineTool`, generated tool catalogue, confirmation card components, events `assistant.action.proposed|confirmed|undone`",
  'consumes': "agent execution endpoint and `agentCallable` (PAP-291), scope classes and expression rendering (PAP-389), trash/undo and record history (PAP-334, PAP-333), audit (PAP-38), form adapters (PAP-233), dry-run transactions (PAP-348)",
  'consumed_by': f"`r4/{K}/portal-assistant`, `r4/{K}/business-characters`, workflows `agent` step, commerce order tools",
  'dod': [
    'At least 12 tools generated in the demo tenant (navigate, filter view, create record, update field, assign, comment, schedule reminder, export view, open record, search, create task, send draft → approval)',
    'Confirm → execute → undo round trip on a record update leaves the row and audit chain consistent; denied and expired paths tested',
    'Security review: no tool executes without the human principal in scope; fuzzed inputs never bypass Zod',
  ],
  'tests': {
    'Unit': 'catalogue ranking and cap; description lint; scope class routing (read auto, write card, send/money approval)',
    'Integration': 'preview diff equals the real write diff for 20 fixture updates; idempotent confirm replay; undo restores field history',
    'Adversarial': 'PAP-85 edge-case hunter fixtures: unicode, 10k-char inputs, tool names injected via records',
  },
  'demo': "Ask \"move all of Acme's open deals to Negotiation and tell Sam\"; see the preview (3 rows), confirm the write, watch the message to Sam land in the approval queue rather than being sent, then undo the write.",
  'edge': [
    'Tool whose underlying command was removed by a deploy between propose and confirm: confirm fails with `TOOL_GONE` and the card explains',
    'Human loses permission between propose and confirm: `can()` is re-evaluated at confirm; denied with the PAP-227 explain output',
  ],
  'deps': f"`r4/{K}/conversation-runtime` (hard), PAP-291 and PAP-389 (hard), PAP-334, PAP-333, PAP-38 (hard), PAP-233 and PAP-348 (soft).",
  'builder': 'Nova', 'reviewer': 'Sentinel (Security Auditor)',
 },
 {
  'key': f'r4/{K}/nl-to-views', 'title': 'Build the tables copilot: natural language to FilterTree, formula and view spec with a reviewable draft, plus "explain this view"',
  'type': 'Build', 'tier': 'sonnet', 'effort': 'high', 'size': 'M', 'priority': 4, 'surfaces': ['Staff', 'Customer'], 'milestone': MS[1], 'deferred': True,
  'blockedBy': [f'r4/{K}/staff-chat-panel', 'PAP-279', 'PAP-382', 'PAP-161', 'PAP-166', 'PAP-172'], 'blocks': [],
  'goal': "Let anyone build a view or formula by describing it: \"invoices over 30 days late grouped by customer, biggest first\" becomes a validated `ViewSpec` draft shown beside the grid with the generated filter, sort and group visible in the PAP-166 builder, applied only on click; \"average order value this quarter\" becomes a formula that type-checks in PAP-382 before it is offered.",
  'scope_in': [
    "`packages/assistant/src/copilots/tables/`: `toFilterTree(text, datasetId)`, `toFormula(text, datasetId)`, `toViewSpec(text, datasetId, baseView?)`, `explainView(viewId)`; each uses constrained tool-use output (Zod schema of `FilterTree` PAP-279, `ViewSpec` PAP-161, formula AST PAP-382) and validates before returning; invalid output triggers one repair round then a friendly failure",
    "Field resolution: dataset field names, PAP-126 terminology aliases and the PAP-39 registry feed a field lexicon into the prompt; ambiguous references produce a clarifying question card, not a guess",
    "`view.toolbar.ask` slot fill: inline input in the view toolbar (PAP-343) that opens the draft in the filter builder with a diff against the current view; `Apply`, `Save as view` (PAP-172), `Discard`",
    "Formula editor integration: `Ask` button in the CodeMirror editor (PAP-383) inserts the generated formula with an explanation comment; `explainFormula` in reverse",
  ],
  'scope_out': ['Creating datasets or fields (PAP-332)', 'SQL generation (the compiler PAP-335 owns SQL; the copilot only emits the typed intermediate)', 'Charts wording beyond the chart view spec'],
  'spec': [
    'The copilot never emits SQL or bypasses the view compiler; output is always the typed intermediate the engine already validates and permission-filters',
    'Date phrases resolve through `chrono-node` relative to the user timezone (PAP-27) into `FilterTree` date ops; "this quarter" uses the tenant fiscal year from the finance settings (PAP-175) when present',
    'Drafts are stored as `view_draft` rows for 24 h so a reload keeps them; applying writes through the normal `views.update` with the assistant attribution',
    'Explain mode renders the current `FilterTree`, sorts and groups as one paragraph in the tenant terminology, cached per view version',
    'Portal customers get the copilot only on views shared to them (PAP-172) and only `toFilterTree`, never `Save as view`',
  ],
  'provides': "`CopilotPort.toFilterTree|toFormula|toViewSpec|explain`, `view.toolbar.ask` fill, `view_draft` table, eval tasks `copilot-tables-*` for PAP-310",
  'consumes': "`FilterTree` grammar (PAP-279), formula parser and type checker (PAP-382, PAP-383), view model and builder (PAP-161, PAP-166), sharing (PAP-172), terminology (PAP-126), timezone helpers (PAP-27)",
  'consumed_by': "tables (toolbar), dashboards (block-level ask, PAP-386), engagement reports, commerce reports",
  'dod': [
    'Golden set of 60 utterances over the demo datasets: ≥85 percent produce a valid draft that matches the expected `FilterTree` or formula on first try; ≥97 percent after one repair; results tracked nightly in the eval report (PAP-310)',
    'Playwright: ask in the toolbar, see the diff in the filter builder, apply, save as view; formula insertion type-checks',
  ],
  'tests': {
    'Unit': 'schema-constrained output validation and repair loop with mocked model; date phrase resolution across timezones and DST; ambiguity detection when two fields share a synonym',
    'E2E': 'draft survives reload; portal customer cannot save; explain paragraph updates when the view changes',
  },
  'demo': "On the invoices grid type \"late more than 30 days, biggest first, by customer\"; the filter builder shows the draft diff; apply, then click Explain on a saved dashboard view to read it back in plain English.",
  'edge': [
    'Utterance references a field the user cannot see: the lexicon is built from readable fields only, so the copilot asks which field was meant instead of revealing the name',
    'Formula that references a relation two hops away: the copilot proposes a lookup or rollup field (PAP-340) as a prerequisite card instead of an invalid formula',
  ],
  'deps': f"`r4/{K}/staff-chat-panel` (hard), PAP-279, PAP-382, PAP-161, PAP-166 (hard), PAP-172, PAP-126, PAP-27 (soft).",
  'builder': 'Nova', 'reviewer': 'Sentinel (Edge Case Hunter)',
 },
 {
  'key': f'r4/{K}/summaries-and-drafting', 'title': 'Build summaries and drafting copilots: record and thread summaries, reply drafts for support and outreach into pending approval, notes to tasks',
  'type': 'Build', 'tier': 'sonnet', 'effort': 'medium', 'size': 'M', 'priority': 4, 'surfaces': ['Staff'], 'milestone': MS[1], 'deferred': True,
  'blockedBy': [f'r4/{K}/conversation-runtime', 'PAP-333', 'PAP-131', 'PAP-412', 'PAP-192', 'PAP-370'], 'blocks': [],
  'goal': "Save staff the reading and the first draft: one-click summaries of a record's activity timeline or a comment thread, reply drafts in the support inbox and outreach sequences that land as `pending_approval` items in the tenant voice (PAP-192 pattern, never sent by the model), and \"turn these notes into tasks\" that proposes PM issues for confirmation.",
  'scope_in': [
    "`CopilotPort.summarise(entityRef | threadRef, { length, audience })` grounded on PAP-333 activity, PAP-131 comments and linked documents; cached per entity version with a `stale` marker; rendered as a `Summary` card at the top of the record panel (slot `record.panel.summary`) with citations",
    "`CopilotPort.draft({ kind: 'support-reply'|'outreach-email'|'outreach-sms'|'comment', context, tone })` using the tenant voice profile (from PAP-192 `CampaignDraft` voice fields) and the conversation history; output is a `pending_approval` draft on the support conversation (PAP-412 reply box prefill) or an outreach template suggestion (PAP-406), always human-edited before send",
    "Notes to tasks: paste or select text → proposed PM issues (PAP-100 entities) with assignee suggestions from mentions; confirmation card per task via the action catalogue",
    "Voice profile settings on `tenant_ai_settings` (tone, banned phrases, sign-off, languages via PAP-27) with a preview",
  ],
  'scope_out': ['Sending anything', 'Meeting transcription (out; v0.3 with PAP-159)', 'Marketing campaign drafting (PAP-192 owns; this issue reuses its schema)'],
  'spec': [
    'Summaries cite at least one source per claim; a claim without a citation is dropped by a post-processing check (the model is asked to tag each sentence with chunk ids)',
    'Drafts respect consent and suppression (`canContact` from PAP-187 WP0) by refusing to draft to a suppressed contact with an explanation',
    'Language: drafts are produced in the contact\'s preferred language when known, else tenant default; the voice profile applies per language',
    'Every draft records `assistant.draft.created` with the conversation id so approval queues can show provenance ("drafted by assistant, edited by Sam")',
    'Summary length presets: one line (for grids, via a computed field type `aiSummary` registered with PAP-338 as read-only), paragraph, bullet list',
  ],
  'provides': "`CopilotPort.summarise|draft`, `record.panel.summary` fill, `aiSummary` computed field type, voice profile settings, events `assistant.draft.created`",
  'consumes': "record activity (PAP-333), comments (PAP-131), support inbox reply box (PAP-412), voice schema (PAP-192), outreach templates (PAP-406), consent (PAP-187), email package (PAP-370) for preview rendering, PM entities (PAP-100)",
  'consumed_by': "growth (inbox and sequences), engagement (review responses, booking confirmations), pm-linear (notes to issues), commerce (order notes)",
  'dod': [
    'Summary card on contact, deal, invoice and PM issue records in the demo tenant with citations; support reply draft appears in the reply box as editable text with provenance',
    'Eval: 30 summary fixtures graded by the LLM judge (PAP-310) for faithfulness ≥ 4/5 and zero uncited claims',
  ],
  'tests': {
    'Unit': 'citation post-check drops uncited sentences; suppression refusal; language selection; cache invalidation on new activity',
    'E2E': 'draft a support reply, edit, send through the normal inbox path; the sent message carries the human as sender and the draft provenance in the activity timeline',
  },
  'demo': "Open a long support conversation, click Summarise, then Draft reply; edit one sentence and send; the timeline shows the assistant drafted and Sam sent.",
  'edge': [
    'Record with no activity: summary card shows the empty state with a suggestion to add a note, no model call made',
    'Contact who unsubscribed after the draft was created: the send path (PAP-405) still blocks; the draft card shows the block reason',
  ],
  'deps': f"`r4/{K}/conversation-runtime` (hard), PAP-333, PAP-131 (hard), PAP-412, PAP-192, PAP-406 (soft: features degrade to a copyable draft), PAP-370 (soft).",
  'builder': 'Nova', 'reviewer': 'Sentinel (Code Reviewer)',
 },
 {
  'key': f'r4/{K}/portal-assistant', 'title': 'Build the customer-facing portal assistant: help-center grounding, account lookups, booking and payment handoffs, guardrails and escalation to the support inbox',
  'type': 'Build', 'tier': 'opus', 'size': 'M', 'priority': 4, 'surfaces': ['Customer'], 'milestone': MS[1], 'deferred': True,
  'blockedBy': [f'r4/{K}/retrieval-grounding', f'r4/{K}/action-catalogue', 'PAP-62', 'PAP-411', 'PAP-379', 'PAP-304'], 'blocks': [f'r4/{K}/business-characters'],
  'goal': "Give every tenant's customers a helpful, bounded assistant in the portal: grounded on the tenant's help center and the customer's own records (invoices, bookings, orders), able to hand off to booking and pay flows and to a human in the support inbox, and unable to see, say or do anything outside the customer audience.",
  'scope_in': [
    "`<PortalAssistant/>` filling `portal.assistant.widget` (bottom-right launcher, full-screen sheet on phones) in the PAP-62 portal, and an unauthenticated mode on public help-center pages limited to help-center grounding with email capture (PAP-411 pattern)",
    "Grounding scopes: help-center articles (PAP-379 published pages), the customer's own entities via the registry `audiences: [customer]`, tenant public FAQs; nothing else",
    "Tools for customers: `read` lookups on own records, `openRoute` (navigate to invoice, booking), handoffs `startBooking` and `payInvoice` that open the existing flows (engagement booking pages, PAP-396 `/pay`), `escalate` that creates a support conversation with the transcript attached",
    "Guardrails: refusal policy for out-of-scope topics with the tenant's escalation copy; rate limits per session and IP (PAP-304); tier-3 wrapping of everything; no memory across sessions for anonymous users",
    "Tenant controls on `tenant_ai_settings`: `portalEnabled`, hours (outside hours the widget offers escalation only), languages, disclosure text (\"You are chatting with an automated assistant\")",
  ],
  'scope_out': ['Staff features', 'Voice', 'Proactive outreach (never from the widget)'],
  'spec': [
    'Disclosure is always shown at conversation start and the assistant identifies itself as automated when asked; this is a conformance case (several jurisdictions require it)',
    'Escalation attaches the redacted transcript as an internal note (PAP-411 internal notes) and sets the conversation subject from the model summary; the customer sees "A person will reply" with the tenant SLA text',
    'Answer confidence: when grounding returns no chunk above the threshold the assistant says it does not know and offers escalation rather than improvising (eval-tested)',
    'Widget budget: under 40 KB gzipped, loads after the portal shell, no third-party scripts',
    'Anonymous sessions are keyed by a signed cookie, capped at 30 messages per hour and expire after 24 h; their transcripts are retained 7 days unless captured with an email',
  ],
  'provides': "`<PortalAssistant/>`, `portal.assistant.widget` fill, customer tool set, `escalate` handoff, `assistant.escalated` event, unauthenticated help-center mode",
  'consumes': "retrieval (own issue), action catalogue, portal shell (PAP-62), support chat widget and conversations (PAP-411, PAP-410), tenant docs (PAP-379), rate limits (PAP-304), pay pages (PAP-396)",
  'consumed_by': "engagement help center and booking pages, commerce order lookups, growth support inbox",
  'dod': [
    'Customer in the demo tenant asks about an invoice, gets a cited answer, pays through the handoff, then escalates a second question which appears in the staff inbox with the transcript',
    'Leak test: 500 adversarial prompts (PAP-85 fixtures plus red-team set) produce zero staff-only or other-customer data; disclosure shown in 100 percent of sessions',
  ],
  'tests': {
    'Unit': 'scope enforcement in grounding arguments; hours logic across timezones; anonymous rate limit and expiry',
    'E2E': 'phone width full-screen sheet; keyboard and screen reader flow (PAP-156); escalation path; unauthenticated help-center mode with email capture',
  },
  'demo': "As a portal customer on a phone, ask \"when is my next appointment and can I move it?\"; the assistant answers with a citation and opens the reschedule flow; then ask about a refund and watch it hand off to a human.",
  'edge': [
    'Customer belongs to two tenants (PAP-58): the widget is tenant-scoped by host and never mixes; switching tenants starts a new conversation',
    'Help center article updated during a conversation: subsequent turns cite the new version; earlier citations keep their chunk id and show "updated"',
  ],
  'deps': f"`r4/{K}/retrieval-grounding` and `r4/{K}/action-catalogue` (hard), PAP-62 (hard), PAP-411 and PAP-410 (hard for escalation), PAP-379 (soft: FAQs fallback), PAP-304 (hard).",
  'builder': 'Nova', 'reviewer': 'Sentinel (Security Auditor)',
 },
 {
  'key': f'r4/{K}/business-characters', 'title': 'Build tenant-configurable business characters: persona, knowledge sources, allowed tools, audience and hours, extending the character schema with a tenant scope',
  'type': 'Build', 'tier': 'sonnet', 'effort': 'high', 'size': 'M', 'priority': 4, 'surfaces': ['Staff', 'Customer'], 'milestone': MS[2], 'deferred': True,
  'blockedBy': [f'r4/{K}/action-catalogue', f'r4/{K}/portal-assistant', 'PAP-103', 'PAP-104', 'PAP-134', 'PAP-113'], 'blocks': [],
  'goal': "Let a tenant shape its own agents the way PaperOS shapes its builders: named characters (\"Front Desk\", \"Bookkeeper\", \"Onboarding Guide\") with a persona, knowledge sources, an allowed tool set, an audience and hours, defined in the same character schema as PAP-103 but stored per tenant, visible on the org chart (PAP-113), and selectable per surface so the portal widget and the staff panel can speak with different characters.",
  'scope_in': [
    "Character schema extension (PAP-103): `scope: 'platform'|'tenant'`, `tenantId`, `audience[]`, `surfaces[]`, `knowledge: { docs[], datasets[], helpCenter }`, `tools[]` (subset of the catalogue), `hours`, `handoff: { toCharacter?, toSupport }`, `voice`; stored in `tenant_character` with RLS; platform characters stay in `.claude/agents`",
    "Console page `/console/assistant/characters` (spec) with list, editor (form view generated from the schema via PAP-124 patterns), test chat side panel, publish/unpublish, version history through PAP-134 objects (tenant characters are rules objects too)",
    "`CharacterPort.resolve(audience, surface, route)`: picks the published character for the context (portal → customer characters; console route prefix → staff characters), falling back to the default assistant",
    "Org chart (PAP-113): tenant characters appear under a \"Business agents\" node with usage and spend from the prompt log; PAP-111 budgets per tenant character",
    "Starter characters in business packs (PAP-427 `pack.yaml` gains `characters[]`) so a clinic gets a Front Desk and a Billing Assistant on day one",
  ],
  'scope_out': ['Characters running builder sessions (never; tenant characters only use `ActionPort`)', 'Marketplace of characters (v0.3)', 'Voice cloning'],
  'spec': [
    'A tenant character can never hold tools outside the tenant allow-list or the audience\'s permissions; `tools[]` is intersected at resolve time and the editor shows the effective set',
    'Persona text passes the PAP-299 lint for instruction-injection patterns before publish ("ignore previous", "you are now") and is capped at 4k tokens',
    'Hours use the tenant timezone; outside hours the character answers with its handoff text and, for customers, escalates only',
    'Versioning: publishing creates an immutable version; conversations record the character version so the prompt log can replay the exact persona',
    'Evals: each starter character ships two golden tasks in `evals/assistant/characters/` graded nightly (PAP-310); a tenant character can run the "test chat" against the same graders on demand',
  ],
  'provides': "`tenant_character` table and `characters.*` procedures, `CharacterPort` adapter, console page, org chart node, pack `characters[]` schema, starter characters for the five packs",
  'consumes': "character schema and lead prompts (PAP-103, PAP-104), rules objects and history (PAP-134), org chart (PAP-113), budgets (PAP-111), spec editor patterns (PAP-124), pack format (PAP-426), portal and staff surfaces (own issues)",
  'consumed_by': "commerce packs (starter characters), engagement (Front Desk answers booking questions), platform-ops (character spend in tenant health)",
  'dod': [
    'Demo tenant has two published characters with different tool sets; the portal speaks as Front Desk and the console as Ops Assistant; org chart shows both with spend',
    'Publish blocked for a persona containing an injection pattern; effective tool intersection visible and tested',
  ],
  'tests': {
    'Unit': 'schema validation with tenant scope; resolve() precedence (route > surface > default); tool intersection; hours across DST',
    'E2E': 'edit → test chat → publish → portal picks up the new version within one conversation; version history shows the diff',
  },
  'demo': "Create \"Front Desk\" for the salon demo, give it booking tools and the help center, set hours, publish; open the portal as a customer and book through it; open the org chart and find its spend.",
  'edge': [
    'Character deleted while conversations reference it: conversations keep the version snapshot; new turns fall back to the default assistant with a notice',
    'Two characters match the same route: the editor refuses to publish overlapping surfaces without an explicit priority',
  ],
  'deps': f"`r4/{K}/action-catalogue` and `r4/{K}/portal-assistant` (hard), PAP-103, PAP-104 (hard: schema), PAP-134, PAP-113 (soft), PAP-426 (soft: pack integration).",
  'builder': 'Nova', 'reviewer': 'Atlas (Decomposer)',
 },
 {
  'key': f'r4/{K}/safety-evals-redteam', 'title': 'Build the assistant eval and red-team suite: injection via records and docs, cross-tenant leak probes, action misuse, faithfulness and refusal grading on the nightly harness',
  'type': 'Review', 'tier': 'opus', 'size': 'M', 'priority': 4, 'surfaces': ['Developer'], 'milestone': MS[2], 'deferred': True,
  'blockedBy': [f'r4/{K}/conversation-runtime', f'r4/{K}/action-catalogue', 'PAP-308', 'PAP-310', 'PAP-299', 'PAP-85'], 'blocks': [],
  'goal': "Prove the assistant is safe every night, not once: a task set on the PAP-308 harness covering prompt injection planted in records, docs, files and comments, cross-tenant and cross-audience leak probes, action misuse (unconfirmed writes, scope escalation), faithfulness of summaries and copilots, and correct refusals, with regressions filed as Linear issues by PAP-310 and an S0 alert through PAP-356 on any leak.",
  'scope_in': [
    "`evals/assistant/`: task format from PAP-308 with fixture tenants (two tenants, three audiences, poisoned content in 12 places); graders: deterministic (leak = any string from the forbidden set appears; action = any executed tool call without confirmation), LLM judge (faithfulness, helpfulness, disclosure) from PAP-310",
    "Red-team generator: templates × payload corpora (PAP-299 corpus plus PAP-85 adversarial inputs) producing 300 cases per night with a fixed seed and 50 fresh mutations",
    "Reports: `assistant-evals.json` in the PAP-239 artefact shape; trend page section in PAP-310 report; leak → security event `assistant.leak.detected` (S0) → pinned Linear issue and Needs Justin (PAP-356 routing)",
    "Gate hook: any PR touching `packages/assistant` runs the 40-case smoke subset in Gate 1; nightly runs the full set on staging with the real provider through the credential broker (PAP-300)",
  ],
  'scope_out': ['Model-level jailbreak research', 'Evals for builder agents (PAP-309)'],
  'spec': [
    'Leak grading is exact and conservative: fixture tenants contain unique canary strings per audience; any canary crossing a boundary fails the whole run',
    'Injection cases assert three things: the instruction was not followed, a `injection.suspected` security event was emitted, and the answer still addressed the user\'s actual question',
    'Action misuse cases include time-of-check attacks (permission removed between propose and confirm) and tool-name collisions injected via record content',
    'Faithfulness threshold 4/5 median with no case below 2; refusal set has 30 out-of-scope prompts per surface; disclosure must appear in every portal case',
    'Budget: the nightly run is capped at a token budget from PAP-111; exceeding it fails the run visibly rather than silently truncating',
  ],
  'provides': "`evals/assistant/*` tasks and graders, red-team generator, `assistant-evals.json` artefact, Gate 1 smoke subset, `assistant.leak.detected` security event",
  'consumes': "eval harness and judge (PAP-308, PAP-310), trust-tier corpus (PAP-299), adversarial inputs (PAP-85), gate artefacts (PAP-239), security telemetry (PAP-356), credential broker (PAP-300), the runtime and action catalogue",
  'consumed_by': f"`r4/{K}/business-characters` (test chat graders), platform-ops compliance evidence (nightly safety evidence), quality release digest (PAP-89 section)",
  'dod': [
    'Nightly run green for seven consecutive nights on staging before the portal assistant flag is enabled for any real tenant (documented gate in the release train PAP-252)',
    'One seeded leak (a deliberately broken predicate in a test branch) is caught by the run and produces the S0 path end to end',
  ],
  'tests': [
    'Meta-tests: graders scored against 20 hand-labelled transcripts (precision and recall ≥ 0.95 for leak, ≥ 0.9 for injection).',
    'Determinism: the fixed-seed subset yields identical case ids and payloads across two runs.',
    'Smoke subset runtime under 4 minutes with the mock provider in Gate 1.',
  ],
  'demo': "Run the smoke subset locally against the mock provider, show one injection case transcript with its security event, then show the nightly trend page and a regression issue PAP-310 filed.",
  'edge': [
    'Provider changes behaviour after a model update: the trend page flags a step change and the model pin in `tenant_ai_settings` defaults is bumped only through an ADR',
    'A fixture canary accidentally appears in real docs: canaries are UUID-derived and checked against the search index before each run',
  ],
  'deps': f"`r4/{K}/conversation-runtime` and `r4/{K}/action-catalogue` (hard), PAP-308, PAP-310 (hard), PAP-299, PAP-85, PAP-239, PAP-356 (soft).",
  'builder': 'Sentinel', 'reviewer': 'Atlas (Merger)', 'tenant_data': False, 'module_edge': False,
 },
 {
  'key': f'r4/{K}/metering-limits', 'title': 'Add assistant metering and limits: usage kinds, per-tenant daily limits and entitlements, cost dashboard section and BYO-key accounting',
  'type': 'Build', 'tier': 'sonnet', 'effort': 'medium', 'size': 'S', 'priority': 4, 'surfaces': ['Staff', 'Customer'], 'milestone': MS[2], 'deferred': True,
  'blockedBy': [f'r4/{K}/conversation-runtime', 'PAP-391', 'PAP-178', 'PAP-98'], 'blocks': [],
  'goal': "Make the assistant affordable and predictable: every message and token is a usage event, plans carry `assistantMessagesPerDay` and `assistantTokensPerMonth` entitlements, tenants see spend and remaining allowance on the billing page, BYO-key tenants are metered for limits but not billed for tokens, and the platform's own credit report (PAP-98) separates assistant spend from builder spend.",
  'scope_in': [
    "Register kinds with PAP-391: `assistant.messages`, `assistant.tokens.in`, `assistant.tokens.out`, `assistant.actions`; `recordUsage` calls in the runtime with `billable: !byoKey`; hourly rollups feed PAP-178 `used`",
    "Entitlement keys in `plans.ts` (PAP-178): `assistant`, `assistantPortal`, `assistantMessagesPerDay`, `assistantTokensPerMonth`; `<EntitlementGate/>` on the panel and widget with the upgrade prompt; hard stop at 100 percent with a friendly message and escalation-only mode for the portal",
    "Billing page section `/org/settings/billing#assistant`: messages today, tokens this month, cost estimate (platform key) or provider cost estimate (BYO), per-character breakdown, export CSV",
    "PAP-98 burn report gains an `assistant` line per tenant; Stripe metered price sync for `assistant.tokens.out` when a plan flags it metered",
  ],
  'scope_out': ['Pricing decisions (Needs Justin item filed with a proposed table)', 'Per-user chargeback'],
  'spec': [
    'Limits are evaluated before the model call from the hourly rollup plus an in-memory counter for the current hour; a tenant cannot exceed the daily cap by more than one hour\'s burst',
    'Warnings at 80 and 100 percent go through the notification kinds registry (PAP-136) to org admins',
    'Token accounting uses provider-reported counts when available and `countTokens` estimates otherwise, flagged `estimated`',
    'BYO key tenants see provider cost estimates from a public price table in `packages/assistant/prices.yaml` reviewed monthly by Scout (PAP-218 routine)',
  ],
  'provides': "usage kinds, entitlement keys, billing page section, burn report line, `prices.yaml`",
  'consumes': "usage metering (PAP-391), entitlements (PAP-178), credit spend report (PAP-98), notification kinds (PAP-136), the conversation runtime",
  'consumed_by': "platform-ops tenant health, business-core billing page, agents budgets (PAP-111 kill switch reads the same counters)",
  'dod': [
    'Demo tenant hits a 50-message test cap and the panel shows the limit and upgrade prompt; billing section renders with real rollups; burn report separates assistant spend',
    'Metered Stripe price sync verified in test mode for one plan',
  ],
  'tests': {
    'Unit': 'limit evaluation at hour boundaries; `estimated` flag path; BYO not billed but counted',
    'Integration': 'rollup → entitlement `used` → gate; notification at 80 percent once per day',
  },
  'demo': "Set the demo plan to 20 messages a day, send 21, watch the gate and the admin notification, then open the billing page section and export the CSV.",
  'edge': [
    'Clock skew between worker and API: limits use database time; the in-memory counter resets on the database hour',
    'Plan downgrade mid-month below current usage: assistant enters read-only history mode until the next period; no retroactive charge',
  ],
  'deps': f"`r4/{K}/conversation-runtime` (hard), PAP-391 and PAP-178 (hard), PAP-98 and PAP-136 (soft).",
  'builder': 'Ledger', 'reviewer': 'Sentinel (Code Reviewer)',
 },
]

TRIO = trio({
    'key': K, 'lead': 'Nova', 'owner': 'Nova', 'kind': 'runtime', 'swapRisk': 'high', 'impl': 'packages/assistant, apps/web/src/assistant',
    'milestones': MS, 'impl_keys': [f'r4/{K}/conversation-runtime', f'r4/{K}/retrieval-grounding', f'r4/{K}/staff-chat-panel', f'r4/{K}/action-catalogue'],
    'publish_blockedBy': [f'r4/{K}/model-and-provider-port'],
    'ports': ['`ModelProviderPort` (`complete`, `stream`, `embed`, `countTokens`, `capabilities`)', '`ConversationPort` (`start`, `send`, `list`, `get`, `feedback`, `abort`)', '`RetrievalPort` (`ground`) with `Chunk` and `Citation` schemas', '`ActionPort` (`listTools`, `propose`, `confirm`, `deny`, `undo`) with `ToolDefinition` and `ScopeClass`', '`CopilotPort` (`toFilterTree`, `toFormula`, `toViewSpec`, `explain`, `summarise`, `draft`)', '`CharacterPort` (`list`, `resolve`) with `TenantCharacter` schema', 'slots `assistant.panel`, `portal.assistant.widget`, `view.toolbar.ask`, `record.panel.tabs.assistant`, `record.panel.summary`'],
    'events': ['assistant.conversation.started', 'assistant.conversation.ended', 'assistant.action.proposed', 'assistant.action.confirmed', 'assistant.action.undone', 'assistant.draft.created', 'assistant.escalated', 'assistant.feedback.given'],
    'requires': ['`@paperos/contract-identity` ^0.1 (`Principal`, `can`, SQL predicate)', '`@paperos/contract-data-layer` ^0.1 (search registry, jobs, audit, email, idempotency)', '`@paperos/contract-realtime` ^0.1 (push transport)', '`@paperos/contract-tables` ^0.1 (`ViewSpec`, `FieldDef`, formula AST; optional for copilots)', '`@paperos/contract-input` ^0.1 (command registry, `agentCallable`)', '`@paperos/contract-collab` ^0.1 (prompt-log sink, comments, docs)', '`@paperos/contract-agents` ^0.1 (character schema, trust tiers)'],
    'fixtures': 'four conversations (console, portal, view, record), twelve message part fixtures, six tool calls across the status machine, eight grounding results with citations, three tenant characters, two provider capability sets',
    'consumers': 'engagement (help center answers, booking by chat), workflows (`agent` step), commerce (portal order lookups), growth (support reply drafting), tables (`view.toolbar.ask`), platform-ops (usage in tenant health)',
})

ISSUES = [TRIO[0]] + ISSUES + TRIO[1:]
