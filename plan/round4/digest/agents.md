# Round 4 digest: Agent Characters & Orgs (`agents`)

Benchmarks: Claude Code (agents, skills, hooks, plugins, MCP allowlists, worktrees, permission modes, SDK); CrewAI and AutoGen (roles, delegation); LangGraph (state graphs, handoffs); Devin and OpenHands (sandboxes, browser, secrets); LangSmith and Braintrust (tracing, datasets, prompt versioning, experiments); OpenAI Evals and Inspect (golden tasks, judges); OWASP LLM Top 10 (prompt injection, excessive agency); Vault and Teleport (short-lived credentials).

## Feature matrix (57 rows: 44 covered, 3 partial, 10 gap)

| Feature | Status | Covered by | Note |
|---|---|---|---|
| Character schema (roles, tools, MCP, scopes, skills, memory, budget, escalation, model) | covered | PAP-103 | effort enum needs alignment with labels; amendment |
| Roster YAML for nine leads and 28 subs | covered | PAP-284 |  |
| Lead system prompts with shared fragments and style lint | covered | PAP-285 |  |
| Sub-character prompts and delegation descriptions | covered | PAP-286 |  |
| `.claude/agents` generation, drift check, smoke | covered | PAP-287 |  |
| Per-character runtime bundles and enforce-scope hook | covered | PAP-106, r4/agents/character-bundles-and-enforce-scope-hook | split this round |
| Least-privilege probe suite and privilege matrix | covered | PAP-106, r4/agents/least-privilege-probe-suite-and-matrix | split this round |
| Destructive-action deny list: policy and hook | covered | PAP-298, r4/agents/deny-list-policy-file-and-hook | split this round |
| Approval path, MCP destructive interception, backstops | covered | PAP-298, r4/agents/request-approval-mcp-interception-and-backstops | split this round |
| Prompt-injection trust tiers, wrapping, scanner, actor verification, spec freeze | covered | PAP-299, r4/agents/trust-tiers-wrapper-scanner-and-actor-verification | split this round |
| Injection eval suite and canaries | covered | PAP-299, r4/agents/injection-eval-suite-and-canaries | split this round |
| Runtime sandbox: container, limits, network isolation | covered | PAP-280 |  |
| Credential broker and egress proxy | covered | PAP-300 | pm-linear project |
| Prompt and tool-call logging with redaction | covered | PAP-107 |  |
| Prompt-log store and browser (tracing UI) | covered | PAP-129, PAP-135 | collab project |
| Session observability: heartbeats, stuck detection, OTel spans | covered | PAP-288 |  |
| Handoff protocol and assignee switching | covered | PAP-108 | assignee switching depends on the identity decision |
| Persistent memory with curation and budgets | covered | PAP-109 |  |
| Context packs and cache-stable prompt order | gap | r4/agents/docs-context-pack-and-cache-friendly-prompts | 150 KB read-first list per cold session |
| Session-end guard hooks (footer, handoff lint, pushed branch) | gap | r4/agents/session-end-guard-hooks | compliance relied on the model remembering |
| Skills library first wave | covered | PAP-105 |  |
| Skills named by character sheets but unbuilt (decompose-brief, edge-case-plan, threat-model, flake-triage, plan-audit) | gap | r4/agents/skills-library-second-wave |  |
| Spec authoring skill | covered | PAP-118 | spec-builder project |
| Scout weekly scan routine | covered | PAP-218 | libraries project, deferred |
| Slash commands for approval and handoff | partial | r4/agents/request-approval-mcp-interception-and-backstops, PAP-108 | `/request-approval` in the deny-list child; `/handoff` via plugin commands |
| Claude Code plugin packaging and marketplace | gap | r4/agents/claude-code-plugin-packaging | schema lists plugins; nothing packages the org |
| MCP server catalog with scope classes | covered | PAP-210 | libraries project |
| Hooks library (PreToolUse, PostToolUse, Stop, SessionEnd, logging) | covered | PAP-106, PAP-107, PAP-299, r4/agents/session-end-guard-hooks |  |
| Eval harness: runner and graders | covered | PAP-308 |  |
| Golden task set with answer keys | covered | PAP-309 |  |
| LLM judge, trend, regression issues, nightly report | covered | PAP-310 |  |
| Prompt versioning, change gating and experiments | gap | r4/agents/prompt-change-control-and-experiments | LangSmith and Braintrust class; hash exists, gate does not |
| Capture real sessions as eval tasks | gap | r4/agents/session-to-eval-task-capture | deferred |
| Gate 2 reviewer calibration | covered | PAP-241 | quality project |
| Budgets, caps, kill switch | covered | PAP-111 | sub-agent fan-out cap; amendment |
| Credit metering per character | covered | PAP-98 | pm-linear |
| Vendor rate-limit governor across sessions | gap | r4/agents/anthropic-rate-limit-governor | cost doc names it as the binding limit |
| Model and effort routing per issue with fallback | covered | r4/pm-linear/session-model-and-effort-routing | pm-linear round 4 |
| Second runtime or vendor adapter behind the flag | gap | r4/agents/second-runtime-adapter-spike | deferred research |
| Agents as first-class principals with keys and attribution | covered | PAP-60 | identity project |
| Character identity in Linear (assignee, lead, comment author) | gap | r4/agents/character-linear-identity-and-attribution | no bot users exist; every consumer assumes them |
| Forge bot accounts and signing keys | covered | PAP-48 | forge project |
| Human-in-the-loop approvals and decision cards | covered | PAP-94, PAP-298 |  |
| Character handbook | covered | PAP-112 |  |
| Org chart UI with live status and controls | covered | PAP-113 |  |
| Agents as live participants in the product | covered | PAP-146 | realtime, soft |
| Onboarding and retirement of characters with approval | gap | r4/agents/character-onboarding-and-retirement-wizard | non-goal is autonomous hiring; nothing scaffolds approved hiring |
| Sub-agent delegation with own bundles and depth caps | partial | PAP-106, PAP-111 | depth and fan-out caps unspecified; amendment |
| Daily standup per character | partial | PAP-98, r4/pm-linear/always-on-operations-and-morning-report | morning report covers the org; per-character view is the org chart |
| Content and migration agent characters | covered | PAP-192, PAP-208 | growth and migration, deferred |
| Rules and skills browsable in-app | covered | PAP-134 | collab |
| Agent-to-agent messaging | covered | PAP-108, PAP-112 | Linear comments and mentions are the channel |
| Contract package, conformance and kernel wiring | covered | PAP-466, PAP-469, PAP-472 | module system |
| Red-team of the deny list (adversarial suite) | covered | r4/agents/deny-list-policy-file-and-hook |  |
| Memory write review gate against injected imperatives | covered | PAP-109, PAP-299 |  |
| Compaction awareness and recovery point | covered | PAP-92, PAP-107 | PreCompact logged; footer is the recovery point |
| Agent cost per task in evals | covered | PAP-308, PAP-98 |  |

## New issues (16: 6 children, 10 gaps, 2 deferred to v0.2)

| Key | Title | Parent | Type / Phase | Prio | Size (est.) | Model / effort | Milestone (due) | Blocked by |
|---|---|---|---|---|---|---|---|---|
| `r4/agents/character-bundles-and-enforce-scope-hook` | Least privilege: per-character runtime bundles (`settings.json`, `.mcp.json`, `hooks.json`), the `enforce-scope` PreToolUse hook and `loadBundle()` | PAP-106 | Build P0 | 1 | M (3) | Sonnet 5 / high | Roster defined and installed (2026-09-24) | PAP-287 |
| `r4/agents/least-privilege-probe-suite-and-matrix` | Least privilege: nightly probe suite (one allowed and one forbidden probe per tool class per character) and the generated privilege matrix | PAP-106 | Build P0 | 1 | S (2) | Sonnet 5 / medium | Roster defined and installed (2026-09-24) | r4/agents/character-bundles-and-enforce-scope-hook |
| `r4/agents/deny-list-policy-file-and-hook` | Deny list: `ops/security/agent-deny.yaml` with 45+ rules across eleven areas, the `packages/agent-policy` matcher and explain CLI, and the PreToolUse hook extension | PAP-298 | Build P0 | 1 | M (3) | Opus 5 / high | Roster defined and installed (2026-09-24) | r4/agents/character-bundles-and-enforce-scope-hook, PAP-210 |
| `r4/agents/request-approval-mcp-interception-and-backstops` | Deny list: the `/request-approval` skill filing a Needs Justin card, MCP destructive-scope interception per character and the backstop matrix with `pnpm policy:backstops` | PAP-298 | Build P0 | 1 | S (2) | Opus 5 / high | Roster defined and installed (2026-09-24) | r4/agents/deny-list-policy-file-and-hook, PAP-94 |
| `r4/agents/trust-tiers-wrapper-scanner-and-actor-verification` | Prompt injection: trust-tier classifier, `<untrusted>` wrapping in the prompt renderer, injection scanner, T1 actor verification for the reply grammar and the spec-freeze hash | PAP-299 | Build P0 | 1 | M (3) | Opus 5 / high | Roster defined and installed (2026-09-24) | PAP-92, PAP-97 |
| `r4/agents/injection-eval-suite-and-canaries` | Prompt injection: canary tokens in fixtures and secret maps with proxy and log alerts, and the 60-attack injection eval suite run nightly through the eval harness | PAP-299 | Build P0 | 1 | S (2) | Opus 5 / high | Roster defined and installed (2026-09-24) | r4/agents/trust-tiers-wrapper-scanner-and-actor-verification, PAP-308 |
| `r4/agents/claude-code-plugin-packaging` | Package the PaperOS agent org as a Claude Code plugin: agents, skills, hooks, rules and MCP allowlists installable into any repo with one command and versioned with the roster | - | Build P1 | 2 | M (3) | Sonnet 5 / high | Sub-agents, skills and evals live (2026-09-25) | PAP-287, PAP-105, r4/agents/character-bundles-and-enforce-scope-hook |
| `r4/agents/docs-context-pack-and-cache-friendly-prompts` | Context packs: generate a token-budgeted, cache-stable read-first bundle per project from the Blueprint, Contracts, Module System, roster and project Contract sections, loaded ahead of the issue body | - | Build P0 | 2 | S (2) | Sonnet 5 / medium | Roster defined and installed (2026-09-24) | PAP-92, PAP-287 |
| `r4/agents/session-end-guard-hooks` | Session-end guard: `Stop` and `SessionEnd` hooks that validate the footer, run `handoff lint`, require a pushed branch or `wip:` commit and post the memory block before a session may end | - | Build P0 | 2 | S (2) | Sonnet 5 / medium | Roster defined and installed (2026-09-24) | PAP-92, PAP-108, r4/agents/character-bundles-and-enforce-scope-hook |
| `r4/agents/skills-library-second-wave` | Skills library second wave: `decompose-brief`, `edge-case-plan`, `threat-model`, `flake-triage`, `context-pack`, `evidence-attach` and `plan-audit` as `.claude/skills` with lint, tests and `skills.json` entries | - | Build P1 | 2 | M (3) | Sonnet 5 / high | Sub-agents, skills and evals live (2026-09-25) | PAP-105, PAP-79 |
| `r4/agents/prompt-change-control-and-experiments` | Prompt change control: a PR that changes a character prompt, skill or rule runs that character's eval tasks in cheap mode, posts the score delta, records the prompt version in sessions and offers one-command rollback | - | Build P1 | 3 | S (2) | Sonnet 5 / medium | Sub-agents, skills and evals live (2026-09-25) | PAP-287, PAP-310 |
| `r4/agents/anthropic-rate-limit-governor` | Anthropic rate-limit governor in the runtime: shared output-tokens-per-minute and concurrent-session budget across sessions, 429 and 529 backoff coordination, reviewer priority and a saturation signal to the scheduler | - | Build P1 | 2 | S (2) | Opus 5 / medium | Sub-agents, skills and evals live (2026-09-25) | PAP-282, PAP-98 |
| `r4/agents/character-onboarding-and-retirement-wizard` | Character onboarding and retirement: `pnpm agents new <name> --lead <lead>` scaffolds YAML, prompt, smoke tasks, eval task, label and bundle and files the Needs Justin hiring card; `pnpm agents retire <name>` archives with an ADR | - | Build P1 | 3 | S (2) | Sonnet 5 / medium | Sub-agents, skills and evals live (2026-09-25) | PAP-287, PAP-94 |
| `r4/agents/character-linear-identity-and-attribution` | Character identity in Linear: decide and configure how characters appear as assignees, commenters and project leads (per-character seats versus one OAuth actor with `Character:` attribution), with the Needs Justin cost card | - | Infra P0 | 2 | S (2) | Sonnet 5 / medium | Roster defined and installed (2026-09-24) | PAP-91, PAP-48 |
| `r4/agents/session-to-eval-task-capture` | Capture real sessions as eval tasks: `pnpm evals capture --session <id>` turns a logged session or an escaped defect into a golden task with fixtures and graders | - | Build P2 | 4 deferred | S (2) | Sonnet 5 / medium | Sub-agents, skills and evals live (2026-09-25) | PAP-308, PAP-107 |
| `r4/agents/second-runtime-adapter-spike` | Research spike: a second `AgentRuntimePort` adapter (OpenHands or a hosted sandbox) behind `module.agents.impl`, scored against the conformance suite, with an ADR on when a second runtime is worth it | - | Research P2 | 4 deferred | S (2) | Sonnet 5 / medium | Agent org visible in app (2026-09-30) | PAP-469, PAP-280 |

## Amendments to existing specs (8)

* **PAP-103** (Spec): * Effort and model precedence (round 4, aligns with CLAUDE.md): `effort` enum is `low | medium | high | max`; `xhigh` in existing sheets maps to `high` (documen…
* **PAP-284** (Spec): * Defaults (round 4): `roster.yaml` lead defaults follow the plan's per-issue rule rather than a flat Fable 5.1: leads default to `claude-opus-5` / `high` as th…
* **PAP-106** (Scope): * Round 4: this issue is split into two children, `Least privilege: per-character runtime bundles and the enforce-scope hook` (`r4/agents/character-bundles-and-…
* **PAP-298** (Scope): * Round 4: split into two children, `Deny list: policy file, matcher and hook extension` (`r4/agents/deny-list-policy-file-and-hook`, M) and `Deny list: request…
* **PAP-299** (Scope): * Round 4: split into two children, `Prompt injection: trust tiers, wrapper, scanner, actor verification and spec freeze` (`r4/agents/trust-tiers-wrapper-scanne…
* **PAP-111** (Spec): * Sub-agent limits (round 4): a session may spawn at most six concurrent sub-agents and nest at most two levels; the parent's cap covers them (SDK cost already…
* **PAP-282** (Spec): * Prompt order and context pack (round 4): `renderPrompt` places, in this order, the system prompt, the character prompt, the memory block (PAP-109), the projec…
* **PAP-108** (Spec): * Assignee switching (round 4): `to` resolves through `botUser(character)` from the character identity decision (`r4/agents/character-linear-identity-and-attrib…

## Cross-project suggestions (5)

* **libraries**: MCP catalog: `scope` classes (`readOnly`, `write`, `destructive`), `lastVerified` and a Claude Code plugin manifest per connector
* **collab**: Prompt log browser filter by `promptVersion` and `modelServed` with a per-version cost and score column
* **pm-linear**: `loop.registerPass()` plug-in point in PAP-281 for the promotion pass, SLA evaluator and rate-limit governor
* **identity**: Agent principal per sub-character (`pos_agent_` keys carry `character/sub`) so audit rows attribute to the sub that acted
* **forge**: Forge bot display names and avatars matching the Linear character identity decision

## What was missing and why it matters

1. Three P0 security issues (PAP-106 least privilege, PAP-298 deny list, PAP-299 prompt injection) each carried two sessions of work in one M; all three are split into children with their own blockers so the safety wall lands before the roster runs unattended.
2. Every consumer assumed per-character Linear bot users that do not exist (one human member, two OAuth apps); an identity decision issue files the one Needs Justin card and adapts PAP-281, PAP-108 and PAP-113 to either path.
3. Every cold session reads about 150 KB of documents; project context packs under 8k tokens with a cache-stable prompt order cut the largest avoidable token cost in the plan.
4. The org was built into one repo although the schema lists plugins and every generated app needs it: packaging agents, skills, hooks and rules as a Claude Code plugin makes the org installable in one command, which is what plug and play means here.
5. Compliance at session end relied on the model remembering; Stop hooks now refuse to end a session without a valid footer, linted handoff and pushed branch, and the skills the character sheets promise (decompose-brief, edge-case-plan, threat-model, flake-triage, plan-audit) are finally built.
