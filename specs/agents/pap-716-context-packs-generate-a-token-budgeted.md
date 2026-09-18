---
identifier: "PAP-716"
title: "Context packs: generate a token-budgeted, cache-stable read-first bundle per project from the Blueprint, Contracts, Module System, roster and project Contract sections, loaded ahead of the issue body"
project: "agents"
projectName: "Agent Characters & Orgs"
phase: "P0"
type: "Build"
priority: 2
surfaces: ["Agent"]
milestone: "Roster defined and installed"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-92", "PAP-287"]
blocks: ["PAP-109"]
key: "r4/agents/docs-context-pack-and-cache-friendly-prompts"
url: "https://linear.app/paperos/issue/PAP-716/context-packs-generate-a-token-budgeted-cache-stable-read-first-bundle"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:20:23.956Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 2
dueDate: "2026-09-24"
cycle: null
---

# PAP-716: Context packs: generate a token-budgeted, cache-stable read-first bundle per project from the Blueprint, Contracts, Module System, roster and project Contract sections, loaded ahead of the issue body

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Build S

**Goal**

The read-first list (CLAUDE.md, PAP-92) is eight documents totalling about 150 KB, read cold by every one of the 300-plus sessions: at 16 builders that is the single largest avoidable token cost in the plan and it pushes the issue body to the end of the context. A generated context pack per project distils those documents into a stable, ordered prefix under 8k tokens so prompt caching hits, and links the full documents for the sections a session actually needs.

**Scope**

* In: `packages/agents/src/context/pack.ts` (`buildContextPack(projectKey): { markdown, tokens, sources[] }`), generated `docs/.generated/context-packs/<project>.md` committed and drift-checked, a Haiku 4.5 summarisation step with a fixed prompt and citation validation (every paragraph cites its source section), the prompt order in PAP-282 `renderPrompt` (system, character prompt, memory, context pack, then issue and untrusted blocks), `pnpm context:pack --project quality --check`, `docs/agents/context-packs.md`.
* Out: rewriting the source documents (Quill owns them), the memory files (PAP-109 sits after the pack), per-issue retrieval (PAP-138 search later).

**Spec**

* Sources in order: Blueprint key decisions and phases, Contracts sections 1, 3 and 4 and the project's rows of section 6, Module System sections 1 to 3 and the project's row of table 1.1, the project's Linear `Contract` section, the roster routing row and shared rules, the Execution Schedule rules section, the Threat Model deny list and tiers summary; each source section is quoted or summarised to a budget in `packs.yaml` (total 8k tokens, per section caps).
* Determinism: the summariser runs only when a source hash changed; output is committed; `--check` fails Gate 1 when sources changed and the pack did not; paragraphs carry `[src: contracts §3]` citations and a validator drops uncited sentences.
* Prompt order for cache stability: everything before the issue body is identical for all sessions of one character on one project, so the Anthropic prompt cache prefix covers system prompt, character prompt, pack and memory; PAP-282 asserts the order in a snapshot test; PAP-98 reports cache-read ratio per session to prove the effect.
* Pack carries a "Read in full when" table: which document to open for which kind of change (contract shape, RLS, UI slot, gate artefact), so sessions read one full document instead of eight.
* Umbrella and child issues share the project pack; the orchestrator adds the umbrella's Module boundary paragraph after the pack.

**Interface contract**

* Provides: `buildContextPack()`, generated packs, `packs.yaml` budgets, the prompt-order contract in `renderPrompt`, cache-read ratio metric in the burn report.
* Consumes: the source documents in `docs/`, PAP-92 read-first list, PAP-282 renderer, PAP-98 usage fields, Haiku 4.5 for summarisation, PAP-128 docs engine (soft) for rendering the packs.

**Definition of done**

* Eighteen packs generated under 8k tokens each with citations validated; `--check` in Gate 1.
* Renderer snapshot proves the order; on ten staging sessions the cache-read ratio rises above 70 percent versus the pre-pack baseline (numbers in the comment).
* Sentinel spot-checks three packs for lost rules (none of the deny list, umbrella, promotion or deferred rules may be dropped); docs; changelog.

**Test plan**

* Unit: budget trimming order, citation validator, hash-triggered regeneration, prompt order snapshot.
* E2E: ten staging sessions with `usage_events.cache_read_tokens` compared before and after.

**Demo**

Run `pnpm context:pack --project quality` and read the 8k-token pack with its citations; open a session's `Session started` footer and see `cacheReadRatio: 0.74`. Under one minute.

**Edge cases**

* A source document is rewritten heavily (round 5): regeneration runs; Sentinel's spot-check list is re-run as part of the PR.
* Pack accidentally drops a rule: the validator requires the presence of fixed sentences (deny list, umbrella, promotion, deferred, model rule) verbatim.
* Character-specific needs (Ledger needs PCI notes): `packs.yaml` allows per-character appendices under 1k tokens.
* Docs engine renders packs to customers by mistake: packs live under `docs/.generated/` and are excluded from public routes.

**Dependencies**

Hard: PAP-92, PAP-287. Soft: PAP-282, PAP-98, PAP-128, PAP-109.

**Agent**

Builder: Quill (Prompt Logger) with Atlas (Dispatcher) on the renderer. Reviewer: Sentinel (Code Reviewer).

**Size**

S: half a session.
