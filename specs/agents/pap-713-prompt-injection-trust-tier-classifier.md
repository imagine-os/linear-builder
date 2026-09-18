---
identifier: "PAP-713"
title: "Prompt injection: trust-tier classifier, `<untrusted>` wrapping in the prompt renderer, injection scanner, T1 actor verification for the reply grammar and the spec-freeze hash"
project: "agents"
projectName: "Agent Characters & Orgs"
phase: "P0"
type: "Build"
priority: 1
surfaces: ["Agent"]
milestone: "Roster defined and installed"
state: "Backlog"
parent: "PAP-299"
children: []
blockedBy: ["PAP-92", "PAP-97"]
blocks: ["PAP-81", "PAP-109", "PAP-677", "PAP-714"]
key: "r4/agents/trust-tiers-wrapper-scanner-and-actor-verification"
url: "https://linear.app/paperos/issue/PAP-713/prompt-injection-trust-tier-classifier-untrusted-wrapping-in-the"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:20:22.675Z"
model: "claude-opus-5"
effort: "high"
estimate: 3
dueDate: "2026-09-24"
cycle: null
---

# PAP-713: Prompt injection: trust-tier classifier, `<untrusted>` wrapping in the prompt renderer, injection scanner, T1 actor verification for the reply grammar and the spec-freeze hash

**Model / Effort:** Opus 5 (`claude-opus-5`) / high — Build M

**Goal**

First half of PAP-299: the mechanism. Text a session reads is classified into a trust tier at ingestion, anything below the operator tier is wrapped as data, a scanner strips and reports injection patterns, only Justin's Linear user id can trigger the reply grammar, and a spec-freeze hash bounces issues edited after promotion. The attack suite and canaries are the sibling child.

**Scope**

* In: `packages/agents/src/trust/{classify,wrap,scan}.ts`, PAP-96 `renderPrompt` changes (instruction section never interpolates untrusted text), PAP-97 handler changes (`isOperator(actorId)` gate for PAP-94 verbs and `KILL`), `claims.spec_hash` and label `spec-changed`, PAP-243 input hardening flags (`mcpServers: []` on fork PRs, URL-in-finding filter), PostToolUse hook wrapping tool results as T3, `docs/security/prompt-injection.md` sections "Tiers" to "Freeze".
* Out: canary tokens and the 60-attack eval suite (sibling), the memory gate wording beyond the hook (PAP-109 consumes `classify`), model-level safety, the deny list (PAP-298).

**Spec**

* Tiers: `T0 system` (orchestrator prompt, `.claude/rules`, character prompt, reviewed memory), `T1 operator` (comments whose Linear `user.id` is in `operatorUserIds`, verified from the webhook payload), `T2 internal` (bot-authored issue bodies and comments, PR bodies from `imagine-os` branches), `T3 external` (fork PRs, imported documents, web fetches, third-party responses, customer data, Renovate changelogs), `T4 hostile` (scanner-flagged).
* Wrapping: `<untrusted source="linear:comment:<id>" author="<id>" tier="T3">…</untrusted>` with the fixed preamble; nested tags escaped; a unit test asserts no untrusted string reaches the instruction section; blocks over 30k tokens are truncated with a link.
* Scanner `scan(text): Finding[]`: instruction overrides, agent-directed imperatives, hidden content (HTML comments, zero-width and bidi characters, base64 over 200 chars, data URIs), tool-call lookalikes and secret-shaped strings; hits downgrade the block to T4, strip it and post `Possible prompt injection removed (<rule>)`; precision target 0.9 on a 200-sample corpus.
* Actor verification: PAP-97 resolves `webhook.actor.id`; `approve`, `reject`, `option n`, `KILL*`, `accept`, `decline`, `trust:` are honoured only for T1; others get "Only Justin can decide this" and a `security.injection_flagged` event when the text matched the grammar.
* Spec freeze: entering Ready for Claude records `sha256(description)` in `claims.spec_hash`; a non-T1 edit before claim returns the issue to Backlog with `spec-changed` and a comment; T1 edits update the hash; `trust: <comment id>` from Justin promotes one block to T1 for that issue.

**Interface contract**

* Provides: `classify()`, `wrap()`, `scan()`, `isOperator()`, event `security.injection_flagged`, `claims.spec_hash`, label `spec-changed`, the `trust:` grammar, PostToolUse wrapper hook.
* Consumes: PAP-92 playbook rule text, PAP-97 actor data and handlers, PAP-96 renderer, PAP-243 assembler, PAP-107 logging, `operatorUserIds` config.

**Definition of done**

* Classifier on 30 sources and wrapper escaping tests green; renderer assertion test proves untrusted text never enters the instruction section.
* Scanner precision at least 0.9 and recall at least 0.9 on the 100 positive and 100 negative samples (numbers in the PR).
* A non-Justin `approve` on a rehearsal card is ignored and answered; a bot edit to a Ready issue bounces it with `spec-changed` (recordings).
* Docs sections; changelog under "Security"; Linear comment with the numbers and recordings.

**Test plan**

* Unit: tier table, escaping, scanner corpus, `isOperator` with spoofed display names, hash freeze transitions.
* E2E: renderer snapshot with mixed tiers; webhook fixtures through PAP-97 handlers; live rehearsal card and bounce.

**Demo**

Post `approve` from the bot account on a rehearsal Needs Justin card and read the reply; edit a Ready issue from the bot account and watch it bounce with `spec-changed`; run `pnpm trust:scan fixtures/hidden-comment.md` and read the stripped block. Two minutes.

**Edge cases**

* Legitimate spec text that reads like an instruction ("the agent must call `billing.sync`"): imperatives directed at the reader score higher than domain descriptions; T2 planning content is flagged for the reviewer, not stripped.
* Justin edits from the mobile app: identity is `user.id`, unaffected.
* Scanner false positive removes needed content: the comment names the block; `trust: <comment id>` restores it for that issue.
* Attack via tool output (web page fetched by Scout): wrapped T3 by the PostToolUse hook, not the renderer.

**Dependencies**

Hard: PAP-92, PAP-97. Soft: PAP-96, PAP-243, PAP-107, PAP-94, PAP-109.

**Agent**

Builder: Sentinel (Security Auditor) with Atlas (Dispatcher) for renderer and webhook changes. Reviewer: Sentinel (Code Reviewer).

**Size**

M: one session.
