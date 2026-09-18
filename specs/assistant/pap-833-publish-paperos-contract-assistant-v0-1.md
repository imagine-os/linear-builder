---
identifier: "PAP-833"
title: "Publish @paperos/contract-assistant v0.1 with manifest"
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
blockedBy: ["PAP-264", "PAP-279", "PAP-302", "PAP-303", "PAP-305", "PAP-433", "PAP-556", "PAP-834"]
blocks: ["PAP-835", "PAP-836", "PAP-837", "PAP-838", "PAP-845", "PAP-846"]
key: "r4/assistant/contract-publish"
url: "https://linear.app/paperos/issue/PAP-833/publish-paperoscontract-assistant-v01-with-manifest"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:51:16.200Z"
model: "claude-opus-5"
effort: "high"
estimate: 3
dueDate: "2026-10-01"
cycle: null
---

# PAP-833: Publish @paperos/contract-assistant v0.1 with manifest

**Model / Effort:** Opus 5 (`claude-opus-5`) / high — Spec M

**Goal**

Publish `@paperos/contract-assistant` v0.1 and the `assistant` module manifest so every other module codes against a versioned package instead of `packages/assistant, apps/web/src/assistant` internals (`docs/module-system.md` sections 1 to 3). The contract holds only types, Zod schemas, event topics, route signatures, slot definitions and port interfaces; the implementation stays in the project's Build issues. Swap risk is declared `high` and kind `runtime`, which decides how much of the swap playbook a rewrite must follow. This is a new module: the contract is written before the implementation, so the Build issues in this project consume it from day one rather than being retrofitted.

**Scope**

In: `packages/contracts/assistant/` published as `@paperos/contract-assistant` (workspace-private, `0.1.0`): `src/index.ts`, `ports.ts`, `events.ts`, `routes.ts`, `slots.ts` as applicable, an empty `conformance/` (filled by the conformance issue) and `fixtures/`. `module.ts` via `defineModule()` (PAP-264 shape) extended with `provides: [{ contract: '@paperos/contract-assistant', version: '0.1.0' }]`, `requires`, `capabilities`, `slots`, `events`, `owner: { agent: 'Nova', project: 'assistant' }`, `swapRisk: 'high'`, `kind: 'runtime'`, plus the generated `module.manifest.json`. `ownership.json` `contracts` entry (PAP-305 file) and the generated `docs/platform/contracts/assistant.md` (a `typedoc` stub until the docs generator PAP-445 lands). A `## Module boundary` paragraph on this project's model or umbrella issue naming the contract version each Build issue implements.

Out: Runtime behaviour, React, Drizzle tables, network calls. The conformance suite and the kernel binding (own issues). Changing contract-zero types; anything missing there is filed against PAP-302, PAP-279 or PAP-303.

**Spec**

* Ports and schemas exported at v0.1: `ModelProviderPort` (`complete`, `stream`, `embed`, `countTokens`, `capabilities`); `ConversationPort` (`start`, `send`, `list`, `get`, `feedback`, `abort`); `RetrievalPort` (`ground`) with `Chunk` and `Citation` schemas; `ActionPort` (`listTools`, `propose`, `confirm`, `deny`, `undo`) with `ToolDefinition` and `ScopeClass`; `CopilotPort` (`toFilterTree`, `toFormula`, `toViewSpec`, `explain`, `summarise`, `draft`); `CharacterPort` (`list`, `resolve`) with `TenantCharacter` schema; slots `assistant.panel`, `portal.assistant.widget`, `view.toolbar.ask`, `record.panel.tabs.assistant`, `record.panel.summary`
* Events declared with `defineTopic()` (payload schemas, version 1): `assistant.conversation.started`, `assistant.conversation.ended`, `assistant.action.proposed`, `assistant.action.confirmed`, `assistant.action.undone`, `assistant.draft.created`, `assistant.escalated`, `assistant.feedback.given`
* Requires (manifest `requires[]`): `@paperos/contract-identity` ^0.1 (`Principal`, `can`, SQL predicate); `@paperos/contract-data-layer` ^0.1 (search registry, jobs, audit, email, idempotency); `@paperos/contract-realtime` ^0.1 (push transport); `@paperos/contract-tables` ^0.1 (`ViewSpec`, `FieldDef`, formula AST; optional for copilots); `@paperos/contract-input` ^0.1 (command registry, `agentCallable`); `@paperos/contract-collab` ^0.1 (prompt-log sink, comments, docs); `@paperos/contract-agents` ^0.1 (character schema, trust tiers)
* Rules: Zod 4 only, JSON Schema generated and committed; no `z.bigint()` on wire schemas (PAP-302 `Money` codec); one sentence of doc and one fixture per port method; `size-limit` under 50 KB minified; lint R9 passes; manifest `dependsOn` is derived from `requires`, never hand-written
* Every port method that mutates money, sends a message or signs a document carries `Idempotency-Key` semantics from PAP-304 in its signature (`{ idempotencyKey }` option) so adapters cannot forget it
* Error codes reuse the contracts document catalogue (`NOT_FOUND`, `FORBIDDEN`, `CONFLICT`, `MODULE_DISABLED`, `RATE_LIMITED`); module-specific codes are listed in `errors.ts` with user-facing copy keys (PAP-368)

**Interface contract**

Provides: `@paperos/contract-assistant@0.1.0` with the exports above; `module.manifest.json` valid against `manifest.schema.json`; `ownership.json` `contracts.assistant`. Consumes: the manifest schema and validator (PAP-433), contract-zero (`@paperos/core/types|filter|events`, PAP-302, PAP-279, PAP-303), the base manifest shape (PAP-264) and the ownership map (PAP-305). Consumed by: engagement (help center answers, booking by chat), workflows (`agent` step), commerce (portal order lookups), growth (support reply drafting), tables (`view.toolbar.ask`), platform-ops (usage in tenant health), and this module's conformance and wire issues.

**Definition of done**

* Package merged, `0.1.0` in the workspace changeset; manifest validates; `pnpm modules:validate` and `pnpm gen:dep-map` green with the new module present
* Generated JSON Schema, `typedoc` stub and ownership entry committed; `compat-matrix.json` (PAP-440) shows every `requires` resolving
* Sentinel confirms no implementation leaked into the package (no React, no Drizzle, no fetch)
* Linear comment on the issue with the evidence links (PR, gate artefacts, recording or report) and the module docs page updated where the interface changed.

**Test plan**

* Static: lint rules R7 to R9; generated JSON Schema committed and unchanged; `size-limit`; `tsc --noEmit` with `exactOptionalPropertyTypes`.
* Unit: every schema accepts its valid fixture and rejects its invalid one (four conversations (console, portal, view, record), twelve message part fixtures, six tool calls across the status machine, eight grounding results with citations, three tenant characters, two provider capability sets); `defineTopic` registrations resolve at import; the manifest validates and its `requires` resolve against the other manifests.
* Review: Sentinel reads the package top to bottom against `docs/module-system.md` section 2 and the contracts document; every port method has a fixture.

**Demo**

`pnpm modules:validate` prints the `assistant` manifest with its provides and requires, `pnpm gen:dep-map` shows the new node with only declared edges, and `docs/platform/contracts/assistant.md` renders the port list.

**Edge cases**

* A port needed by a Build issue but missing at v0.1 is added as a minor bump (`0.2.0`) with a fixture, never as a direct import of the implementation
* A type that two contracts both want (for example a scheduling `TimeRange`) goes to contract-zero via PAP-302, not into this package, to avoid a dependency between contracts

**Dependencies**

PAP-433 manifest schema (hard), contract-zero PAP-302, PAP-279, PAP-303 (hard), PAP-264 and PAP-305 (soft, shape only). Unblocks every other issue in this project.

**Agent**

Builder: Nova. Reviewer: Sentinel (Code Reviewer).

**Size**

M: one session.
