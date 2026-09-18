---
identifier: "PAP-466"
title: "Publish @paperos/contract-agents v0.1 with manifest"
project: "agents"
projectName: "Agent Characters & Orgs"
phase: "P0"
type: "Spec"
priority: 1
surfaces: ["Developer"]
milestone: "Roster defined and installed"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-103", "PAP-433"]
blocks: ["PAP-111", "PAP-113", "PAP-288", "PAP-469", "PAP-472"]
key: "module/agents/contract"
url: "https://linear.app/paperos/issue/PAP-466/publish-paperoscontract-agents-v01-with-manifest"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:21:04.187Z"
model: "claude-opus-5"
effort: "high"
estimate: 2
dueDate: "2026-09-24"
cycle: null
---

# PAP-466: Publish @paperos/contract-agents v0.1 with manifest

**Model / Effort:** Opus 5 / high

**Goal**

Publish `@paperos/contract-agents` v0.1 and the `agents` module manifest so every other module codes against a versioned package instead of `.claude/agents, .claude/skills, packages/agents, paperos-orchestrator (runtime)` internals (`docs/module-system.md` sections 1 to 3). The contract holds only types, Zod schemas, event topics, route signatures, slot definitions and port interfaces; the implementation stays where the existing issues put it. Swap risk is declared `medium`, which decides how much of the swap playbook a rewrite must follow.

**Scope**

In:

* `packages/contracts/agents/` published as `@paperos/contract-agents` (workspace-private, `0.1.0`): `src/index.ts`, `ports.ts`, `events.ts`, `routes.ts`, `slots.ts` as applicable, an empty `conformance/` (filled by the conformance issue) and `fixtures/`.
* `module.ts` via `defineModule()` (PAP-264 shape) extended with `provides: [{ contract: '@paperos/contract-agents', version: '0.1.0' }]`, `requires`, `capabilities`, `slots`, `events`, `owner: { agent: 'Atlas', project: 'agents' }`, `swapRisk: 'medium'`, `kind: 'tooling'`, plus the generated `module.manifest.json`.
* `ownership.json` `contracts` entry (PAP-305 file) and the generated `docs/platform/contracts/agents.md` (a `typedoc` stub until the docs generator lands).

Out: runtime behaviour, React, Drizzle tables, network calls; the conformance suite and the kernel binding (own issues). Nothing already fixed by PAP-103 is redesigned; it is packaged.

**Spec**

Ports and schemas exported at v0.1:

* `CharacterSchema` (PAP-103): name, role, reportsTo, tools, MCP servers, access scopes, plugins, skills, memory, escalation, model, effort
* `HandoffArtifact` (PAP-108) and `SessionStatus` (`character`, `state`, `issueKey`, `sessionId`, `spentTodayUsd`, `dailyCapUsd`, `lastHeartbeat`; PAP-113, PAP-288)
* `AgentRuntimePort`: `spawn`, `heartbeat`, `kill`, `status` (PAP-280, PAP-282) and `BudgetPort` (`spend`, `remaining`, `killSwitch`; PAP-111)
* `PromptLogSink` interface the runtime writes to (implemented by collab's store, PAP-107, PAP-129)
* `SkillManifest` and `McpAllowlist` schemas (PAP-105, PAP-106), `DenyListPolicy` (PAP-298)

Events declared with `defineTopic()` (payload schemas, version 1): `agent.session.started|finished|blocked`, `agent.quota.exceeded`, `agent.handoff.posted`.

Requires (manifest `requires[]`): \* `@paperos/contract-identity` ^0.1 (agent principals and keys)

* `@paperos/contract-pm-linear` ^0.1 (issue refs)
* `@paperos/contract-collab` ^0.1 (prompt log store)

Rules: Zod 4 only, JSON Schema generated; no `z.bigint()` on wire schemas (PAP-302 codec); one sentence and one fixture per port method; `size-limit` under 50 KB minified; lint R9 passes; manifest `dependsOn` is derived from `requires`.

**Interface contract**

Provides: `@paperos/contract-agents@0.1.0` with the exports above; `module.manifest.json` valid against `manifest.schema.json`; `ownership.json` `contracts.agents`. Consumes: the manifest schema and validator (`module-system/manifest-schema`), contract-zero (`@paperos/core/types|filter|events`), the decisions in PAP-103 (Define the character schema: name, role, reportsTo, tools, M). Consumed by: PAP-111 (budgets and kill switch), PAP-113 (org chart UI), PAP-288 (session observability), PAP-109 (memory), PAP-192 and PAP-208 (content and migration agents), and the module's conformance and wire issues.

**Test plan**

* Static: lint rules R7 to R9; generated JSON Schema committed and unchanged; `size-limit`; `tsc --noEmit` with `exactOptionalPropertyTypes`.
* Unit: every schema accepts its valid fixture and rejects its invalid one (the nine lead and 28 sub-character YAML files as valid samples, three invalid ones (unknown tool, cycle in reportsTo, missing budget), two handoff artefacts, one session status timeline); `defineTopic` registrations resolve at import; the manifest validates and its `requires` resolve against the other manifests.
* Review: Sentinel confirms no implementation leaked into the package.

**Definition of done**

* Package merged, `0.1.0` in the workspace changeset; manifest validates; compatibility matrix shows every `requires` as `ok` or a named pending provider.
* `docs/platform/contracts/agents.md` generated; short ADR `docs/adr/00xx-contract-agents.md` recording what was pinned.
* Comments on PAP-111, PAP-113, PAP-288 that their Interface contract sections now import from `@paperos/contract-agents`; Linear comment here with the docs link.

**Edge cases**

* A port the implementation has not built yet: declared `@experimental` with a fixture; conformance marks it `pending`, never `passed`.
* A type two modules want (for example `Money`) belongs to contract-zero; the validator rejects a schema whose `$id` collides with a core one.
* Implementation disagrees with the contract after merge: the contract wins; the implementation issue gets a comment and a fix child.

**Dependencies**

Blocked by `module-system/manifest-schema` and PAP-103. Blocks PAP-111, PAP-113, PAP-288, `module/agents/conformance` and `module/agents/wire`. Soft: docs generator, compatibility matrix job.

**Agent**

Specified by Atlas (Agent Characters & Orgs owner). Reviewed by Sentinel and Atlas (contract ownership).

**Size**

S

**Demo**

Reviewer runs `pnpm contract:show agents` and validates the 37 roster files against `CharacterSchema`; introduces a `reportsTo` cycle and the validator names both characters. Under a minute.
