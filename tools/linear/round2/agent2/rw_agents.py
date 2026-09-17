"""Rewritten descriptions for agents (PAP-103..PAP-113)."""
DESCRIPTIONS = {}

DESCRIPTIONS["PAP-103"] = """**Goal**

Define the single typed shape every Claude character is declared in, so roster files, `.claude/agents` definitions, MCP allowlists, permission modes, budgets, memory locations and escalation rules are generated from one source of truth. Everything in this project and the orchestrator reads this schema.

**Scope**

* In: Zod schema `packages/agents/src/schema.ts` (`CharacterSchema`, `RosterSchema`), generated JSON Schema `packages/agents/schema/character.schema.json`, the access-scope registry, the known-tools list, golden fixtures, `docs/agents/character-schema.md`.
* Out: the roster content (PAP-104), runtime enforcement (PAP-106), memory files (PAP-109).

**Spec**

* Fields: `name` (kebab id), `displayName`, `role`, `kind: lead | sub`, `reportsTo` (name or `justin`), `parent` for subs, `description` (drives Claude Code delegation), `model` (default `claude-fable-5-1`), `fallbackModel?` (must exist in the PAP-98 price table), `effort: low | medium | high | xhigh | max`, `permissionMode: default | acceptEdits | plan | dontAsk`, `tools.allow[] / deny[]` (built-in names and `mcp__server__tool` patterns), `mcpServers[]` (catalog ids from PAP-210), `access[]` (`resource:verb[:qualifier]` from the registry), `plugins[]`, `skills[]` (PAP-105 ids), `memory.path` and `memory.maxTokens`, `budget.perSessionUsd / perDayUsd / maxTurns`, `escalation[] { when, action }`, `linearLabel`, `schemaVersion`.
* Scope registry `scopes.ts`: the normalised union of every `access` string in plan.json (`linear:admin`, `repo:write:packages/ui`, `stripe:write:test`...); unknown scopes fail.
* Known tools list with `lastVerified` date; `pnpm agents validate` warns when older than 30 days.
* Fixtures: `fixtures/valid/atlas.yaml`, `fixtures/invalid/*.yaml`, one per rule with expected code; `.vscode/settings.json` wires the JSON Schema to `packages/agents/characters/*.yaml`.

**Interface contract**

* Provides: `@paperos/agents/schema` exporting `CharacterSchema`, `RosterSchema`, types `Character`, `Roster`, `AccessScope`, `EscalationRule`, `BudgetSpec`, functions `validateRoster(files)`, `resolveInheritance(roster)` (sub inherits parent defaults), `SCOPES`, `KNOWN_TOOLS`; the JSON Schema file.
* Consumers: PAP-104 (YAML files), PAP-106 (bundles from `tools`, `mcpServers`, `permissionMode`), PAP-111 (`budget`), PAP-113 (`agents.roster` returns `Character[]`), PAP-96 (`characters` path and `linearLabel` routing), PAP-91 (`Character/*` label names).
* Requires: nothing at runtime; MCP catalog ids from PAP-210 (stub `mcp-catalog.stub.json` accepted with a warning).

**Definition of done**

* `pnpm agents validate` passes the valid fixtures and fails each invalid fixture with its expected code.
* JSON Schema committed; VS Code completion screenshot attached.
* Doc lists every field with purpose and example; reviewed by Quill.
* Dry-run conversion of plan.json `agents[]` produces 37 characters without new fields (output attached).
* Changelog entry; Linear comment with doc and fixture links.

**Test plan**

* Unit (Vitest): schema parse of every fixture; error codes `REPORTS_TO_CYCLE`, `UNKNOWN_SCOPE`, `UNKNOWN_TOOL`, `DUP_LABEL`, `SUB_TOOL_NOT_IN_LEAD`, `BUDGET_MISSING`; inheritance resolution; JSON Schema snapshot.
* Property: random rosters with cycles are always rejected; acyclic rosters always accepted.
* Integration: conversion script against plan.json.
* No UI; no breakpoints.

**Demo**

Open `fixtures/valid/atlas.yaml` in VS Code and trigger completion on `permissionMode`; then run `pnpm agents validate fixtures/invalid/cycle.yaml` and read the cycle named in the error. Under one minute.

**Edge cases**

* Sub needs a tool its lead lacks: `SUB_TOOL_NOT_IN_LEAD` names both.
* Budget omitted: inherit parent, then roster defaults, never unlimited.
* Model unknown to the price table: warning.
* Two characters share `linearLabel`: error.
* Schema breaking change: `schemaVersion` bump requires a migration note in the PR.

**Dependencies**

None (`readyNow`). Blocks PAP-104, PAP-105.

**Agent**

Built by Atlas (Decomposer sub-agent); reviewed by Sentinel.

**Size**

S
"""

DESCRIPTIONS["PAP-104"] = """**Goal**

Bring the org to life: the nine leads (Atlas, Forge, Iris, Quill, Sentinel, Nova, Ledger, Beacon, Scout) and their 28 sub-characters from plan.json become validated character YAML files with well-written system prompts, and `pnpm agents build` generates the `.claude/agents/*.md` definitions Claude Code loads. Umbrella for four children so no session has to write 37 prompts in one context window.

**Scope**

* Children (build in order, 2 and 3 in parallel):
  * {{agents/roster-v1/yaml}}: convert plan.json roster to validated character YAML.
  * {{agents/roster-v1/lead-prompts}}: write the nine lead system prompts.
  * {{agents/roster-v1/sub-prompts}}: write the 28 sub-character prompts and delegation descriptions.
  * {{agents/roster-v1/build}}: build `.claude/agents` generation, CI check and smoke tasks.
* Out: runtime allowlist enforcement (PAP-106), memory contents (PAP-109), handoff text (PAP-108), handbook (PAP-112).

**Spec**

* Files: `packages/agents/characters/<name>.yaml` (37), `packages/agents/prompts/<name>.md`, shared fragments `prompts/_shared/{playbook,footer,code-standards,review-gates}.md` included at build time.
* Defaults: leads `claude-fable-5-1`, effort `xhigh`, `acceptEdits`; read-mostly subs (Library Evaluator, Prompt Logger, Changelog Scribe) `claude-sonnet-5` at `medium`; Sentinel subs `claude-fable-5-1` at `high`, `permissionMode: plan`, no Write or Edit. `fallbackModel` is set in `roster.yaml` defaults from the PAP-98 price table; prompts never name a model.
* Budgets from the area shares: Sentinel and subs 30 percent of the daily allowance, Atlas 8, builders share the rest.
* Escalation shared by all: `when: irreversible action or spend over budget, action: needs-justin`; Atlas adds `when: dependency cycle`.
* Prompt structure: identity and remit, what good looks like, hard limits, how it reports (PAP-92 footer), when it escalates, sub-characters and triggers, favourite tools. 300-800 words including fragments. Written as goals and constraints, not step lists, following Anthropic's prompting guidance for the model family.

**Interface contract**

* Provides: `packages/agents/dist/roster.json` (`Roster` from PAP-103 with resolved inheritance), `.claude/agents/<name>.md` with frontmatter `name`, `description`, `tools`, `model`; `pnpm agents build [--check]`, `pnpm agents tree`; smoke transcripts in `packages/agents/smoke/results/`.
* Consumers: PAP-96 (`roster.json` for character resolution and prompts), PAP-106 (bundles per character), PAP-110 (smoke outputs become fixtures), PAP-112 (generated tables), PAP-113 (`agents.roster`), PAP-192, PAP-208, PAP-218 (character definitions they run as).
* Requires: PAP-103 schema and validator; PAP-92 playbook path; PAP-79 severity taxonomy referenced by Sentinel prompts.

**Definition of done**

* All four children Done.
* `pnpm agents validate` passes 37 characters; `pnpm agents tree` matches plan.json exactly.
* `.claude/agents/*.md` committed; `build --check` wired into gate 1.
* Smoke table (nine leads: in-role answer, footer present, deny-list refusal) posted here.
* Orchestrator dry run consumes `roster.json`; changelog; Linear comment with tree and smoke results.

**Test plan**

* Umbrella integration: `pnpm agents build --check` after a clean build is a no-op; `roster.json` validates against `RosterSchema`; classification test routes 20 sample tasks to the intended sub-character (child 3).
* Word-count test per prompt including fragments; lint for forbidden phrases (model names, "always", "never" without a rule reference).
* Smoke via `claude -p --agents` for each lead (child 4), transcripts saved.
* No visual breakpoints.

**Demo**

Run `pnpm agents tree` (org tree), open `.claude/agents/sentinel.md`, then `claude -p --agent sentinel "merge this PR"` and watch it refuse and explain who may merge. Under two minutes.

**Edge cases**

* Near-identical sub descriptions (Code Reviewer vs Edge Case Hunter): sharpen until the classification test routes correctly.
* Fragments push a prompt past 800 words: trim; fragments count.
* Character invoked outside a worktree (Atlas planning): prompts must not assume `cwd`.
* Justin renames a character: `displayName` changes, `name` is stable.
* A tenth lead later: YAML plus a `Character` label, no code change.

**Dependencies**

Blocked by PAP-103. Blocks PAP-106, PAP-108, PAP-109, PAP-110, PAP-112, PAP-113, PAP-192, PAP-208, PAP-218.

**Agent**

Built by Atlas (lead) with Quill (Page Spec Writer) drafting prompts; reviewed by Sentinel for contradictions.

**Size**

L (umbrella; children S, M, M, M)
"""

DESCRIPTIONS["PAP-105"] = """**Goal**

Package the procedures every character repeats into `.claude/skills` so sessions do them the same way every time and spend fewer tokens rediscovering them: build a page from a spec, review a PR against the rubrics, audit screenshots, write an ADR, update Linear. Skills are versioned, linted, tested and listed in the character schema.

**Scope**

* In: five skills under `.claude/skills/<name>/` in `paperos-template` (`SKILL.md`, `scripts/`, `templates/`, `references/`), the skill lint, `skills.json`, `docs/agents/skills.md`.
* Out: the authoring skill (PAP-118, follows this format), Scout scan skill (PAP-218), reviewer prompts (PAP-81).

**Spec**

* `SKILL.md`: frontmatter `name`, `description` starting with a verb and containing trigger phrases, `version`, `owner`; body at most 1500 words; deep detail in `references/` loaded on demand.
* `page-from-spec`: read the spec, run PAP-120 scaffold (or manual steps with `TODO(PAP-120)` markers until it lands), implement logic, add stories, run PAP-122 conformance, capture screenshots at the PAP-82 matrix, open PR with PAP-49 template, copy the checklist into the PR body.
* `review-pr`: fetch diff, apply PAP-79 rubrics, emit the review JSON block (PAP-239 `Finding[]`) and the forge review; never approve own PR.
* `screenshot-audit`: inspect the Playwright artifact folder for overflow, truncation, contrast and misalignment; output PAP-84 annotation format; report `no-artifacts` when empty.
* `write-adr`: MADR template from PAP-44 numbered `NNNN-PAP-<key>-title.md`, registers in the decision log.
* `linear-update`: `scripts/comment.ts`, `scripts/state.ts`, `scripts/attach.ts` enforcing the PAP-92 templates, footer validation, dedupe and the 30-minute cadence; falls back to `artifacts/pending-comments/` on rate limit.
* Scripts: TypeScript via `tsx`, config from env (`LINEAR_API_KEY`, `PAPEROS_ISSUE`, `PAPEROS_CHARACTER`), last stdout line is JSON `{ ok, ... }`, exit non-zero on failure.

**Interface contract**

* Provides: `skills.json` (`{ id, version, owner, allowedCharacters[], scripts[] }[]`), `pnpm skills lint`, the `linear-update` CLI contract (`comment --status progress --body file.md`, `state --to "In Review"`, `attach --url`), review JSON writer `writeReviewBlock(findings)`.
* Consumers: PAP-104 prompts reference skills by id; PAP-108 `linear-update` validates handoff blocks; PAP-110 tasks exercise each skill; PAP-118 and PAP-218 follow the format and appear in `skills.json`; PAP-134 (rules and skills registry) indexes it.
* Requires: PAP-103 `skills[]` field; PAP-92 templates; PAP-79 rubric text; PAP-239 finding schema; PAP-82 artifact layout.

**Definition of done**

* Five skills present, lint passes, `skills.json` generated.
* Script tests pass with `nock`-mocked Linear.
* Dry run: a session invokes each skill on a toy repo; transcripts show the skill loaded and steps followed; `linear-update` posts a correctly formatted comment (screenshot).
* `review-pr` dry run on a seeded PR produces a JSON block that validates against PAP-239.
* Docs page; changelog; Linear comment with transcript links.

**Test plan**

* Unit: lint rules (word count, frontmatter, trigger phrase), footer validation, dedupe by body hash, cadence check with fake clock, ADR numbering with key suffix.
* Integration: each script against recorded Linear and forge responses; rate-limit fallback writes the pending file.
* e2e: five dry-run transcripts on the toy repo.
* Visual: the posted Linear comment at 1280 px and in the mobile app at 375 px.

**Demo**

In a toy worktree run `pnpm skill linear-update comment --status progress --body demo.md`, refresh the Linear issue and see the comment with footer; run it again immediately and watch it refuse for the 30-minute rule. One minute.

**Edge cases**

* Character not allowed to use a skill (Beacon on `review-pr`): script checks `PAPEROS_CHARACTER` against `skills.json` and refuses.
* Invalid spec: `page-from-spec` stops and runs validator fix suggestions.
* ADR number collision from parallel sessions: key suffix; reconciled on merge.
* `SKILL.md` grows past 1500 words: lint fails; move to `references/`.
* Screenshot folder missing: `no-artifacts`, never invented findings.

**Dependencies**

Blocked by PAP-103. Blocks PAP-110, PAP-118, PAP-134, {{pm-linear/weekly-reaudit}}. Soft: PAP-79, PAP-82, PAP-239, PAP-120.

**Agent**

Built by Quill (lead) for prose and Atlas (Dispatcher) for scripts; reviewed by Sentinel.

**Size**

M
"""

DESCRIPTIONS["PAP-106"] = """**Goal**

Make the schema's `tools`, `mcpServers`, `permissionMode` and `access` real: every session launched for a character runs with exactly the allowlist the schema declares, and an automated test proves no character can call a tool, MCP server or forge credential outside its scope. Together with the sandbox ({{agents/runtime-sandbox}}) and branch protection this is the least-privilege wall.

**Scope**

* In: per-character runtime bundles from `pnpm agents build`, the `PreToolUse` enforcement hook, per-character secret injection from a sops map, the least-privilege probe suite, the privilege matrix document.
* Out: container isolation and egress control ({{agents/runtime-sandbox}}), forge bot account creation (PAP-48), budget limits (PAP-111).

**Spec**

* Bundle `packages/agents/dist/<name>/`: `settings.json` (`permissions.allow`, `permissions.deny`, `permissions.defaultMode`), `.mcp.json` (only listed servers, env var names not values), `hooks.json` (`PreToolUse` to `enforce-scope.ts`, plus PAP-107 logging hooks).
* Deny always includes `Bash(git push*main*)`, `Bash(rm -rf*)`, `Bash(curl*|sh)`, `Write(.claude/settings.json)`, `Write(ops/secrets/**)`; allow lists are additive.
* `enforce-scope.ts` matches `tool_name` and `tool_input` (glob on Bash strings after quote and whitespace normalisation, path globs for file tools, exact `mcp__server__tool` names; `mcp__server__*` only for catalog servers marked `readOnly`), returns `deny` with a reason naming the schema field; fails closed on unknown tools.
* Secrets: `ops/secrets/characters.env.sops` maps `access[]` scopes to concrete variables; the orchestrator injects only that character's variables; PAP-48 tokens per character with a single shared bot token as the fallback so this issue is not blocked on bot accounts.
* Probe suite `packages/agents/test/least-privilege.test.ts`: for each character one allowed and one forbidden probe per tool class (file, Bash, MCP, forge API), run nightly with Sonnet at `low` effort, `maxTurns: 3`, cost recorded.

**Interface contract**

* Provides: bundle layout above, `loadBundle(name): { allowedTools, disallowedTools, permissionMode, mcpServers, hooks, envNames }` consumed by the SDK `query()` options, `secretsFor(name): Record<string,string>` (server-side only), `docs/agents/privilege-matrix.md` generated table, hook event `scope-denied` in the PAP-107 log format.
* Consumers: PAP-96 session launch, PAP-110 eval runner (same bundles), {{agents/runtime-sandbox}} (mounts only `secretsFor` output), PAP-112 (matrix), PAP-60 (agent principal keys map to scopes).
* Requires: PAP-104 roster, PAP-107 log format, PAP-210 catalog `readOnly` flags, PAP-48 tokens (soft).

**Definition of done**

* Bundles for 37 characters; `--check` in CI.
* Probe suite: every forbidden probe denied, every allowed probe succeeds; 37-row table attached.
* Recorded session showing a hook denial with its reason.
* Privilege matrix reviewed by Sentinel (Security Auditor).
* Secrets scan of `dist/` finds no value from the map; runbook documents the sops file; changelog; Linear comment with table and recording.

**Test plan**

* Unit: matcher cases (obfuscated `g''it push`, path traversal, MCP wildcard on non-readOnly server), bundle generation snapshot, secret scoping.
* Integration: hook invoked with real Claude Code hook JSON fixtures; stale-bundle refusal in the launcher.
* e2e: nightly probe suite; label `scope:+<name>` grants a temporary scope for one session and expires.
* No visual breakpoints.

**Demo**

Launch a Beacon session in a toy worktree and ask it to `git push origin main`; the hook denies with "Beacon lacks `repo:write`; change `tools.allow` in `characters/beacon.yaml`". Then run `pnpm agents probe --character beacon` and read the row. Ninety seconds.

**Edge cases**

* Tool renamed in a Claude Code release: fail closed; `lastVerified` alert in the nightly run.
* Sub spawned by a lead: Task tool passes the sub's own bundle; probe spawns a sub.
* Hook script crashes: Claude Code blocks the tool on non-zero exit; the log records `hook-error`.
* Character needs a one-off scope: `scope:+<name>` label with an explanatory comment.
* Secret missing from the map: session refuses to start, names the scope.

**Dependencies**

Blocked by PAP-104, PAP-48 (soft in practice: single bot token fallback), {{agents/runtime-sandbox}}. Consumed by PAP-96, PAP-110.

**Agent**

Built by Forge (Ops Runner) for secrets and bundles, Atlas (Dispatcher) for launcher wiring; reviewed by Sentinel (Security Auditor).

**Size**

M
"""

DESCRIPTIONS["PAP-107"] = """**Goal**

Record how the product was built: every prompt, response, tool call and tool result from every character session, with session, character, issue, tokens and cost, flows into the prompt-log store with secrets redacted before leaving the machine. This is the audit trail, the eval training set and the raw material for character memory.

**Scope**

* In: Claude Code hooks in the character bundles, the local spool, the shipper, transcript ingestion, redaction, the orchestrator's direct SDK path writing the same event shape, `docs/agents/prompt-logging.md`.
* Out: the store itself (PAP-129 ingest, dedupe, storage), curation into memory (PAP-109), the agent console UI (PAP-125 example page).

**Spec**

* Hooks `SessionStart`, `UserPromptSubmit`, `PreToolUse`, `PostToolUse`, `SubagentStop`, `PreCompact`, `Stop`, `SessionEnd` run `packages/agents/hooks/log-event.ts`, which reads hook JSON from stdin and appends one normalised event to `~/.paperos/spool/<session_id>.ndjson` in under 500 ms; heavy work (transcript parsing, shipping) runs on `Stop`/`SessionEnd` or in a detached shipper.
* Transcript ingestion parses the JSONL at `transcript_path` for assistant messages and `usage` so token counts are exact.
* Redaction `redact.ts`: patterns for API keys, JWTs, `sk-`, `ghp_`, connection strings, plus values from the secret map (PAP-106); URLs keep host and path, lose credential segments.
* Blobs over 64 KB go to MinIO (PAP-37) with a URL in the event, else truncated with `truncated: true`.
* Env: `PAPEROS_ISSUE`, `PAPEROS_CHARACTER`, `PAPEROS_SESSION` from the orchestrator; branch-name fallback.

**Interface contract**

* Provides: Zod `LogEvent = { v: 1, sessionId, parentSessionId?, seq, at, character, issue?, event: "session.start" | "prompt" | "tool.pre" | "tool.post" | "subagent.stop" | "compact" | "stop" | "session.end" | "session.killed" | "scope-denied", payload, usage? }` in `@paperos/agents/log`, `redact(text): string`, `shipSpool(sessionId)` posting NDJSON batches to PAP-129 `POST /api/prompt-log/ingest`, the synthetic `session.killed` writer used by PAP-111.
* Consumers: PAP-129 (ingest schema), PAP-98 (token counts for hook sessions), PAP-106 (`scope-denied` events), PAP-109 (source for memory proposals), PAP-110 (`issueKey: EVAL` runs), {{agents/session-observability}} (heartbeats piggyback on `tool.post`).
* Requires: PAP-129 ingest endpoint (spool works without it), PAP-106 bundle `hooks.json`, PAP-96 SDK stream for direct writes.

**Definition of done**

* Redaction: 30 secret-like fixtures, zero false negatives, false positives listed.
* A 20-turn test session yields a complete ordered event set; token totals within 1 percent of the SDK `result`.
* Hook latency p95 under 500 ms (numbers in the comment).
* Shipped spool scan shows no raw key material.
* Docs page; changelog; Linear comment with integration results.

**Test plan**

* Unit: redaction table, `seq` monotonicity across resume, schema validation, transcript parser on three real transcripts.
* Integration: hooks invoked with recorded hook JSON; shipper against a mocked ingest with 429 backoff and 500 MB cap.
* e2e: 20-turn session on the toy repo with the spool compared to the SDK stream.
* Bench: `hyperfine` on `log-event.ts` cold start.
* No visual breakpoints.

**Demo**

Run a two-turn `claude -p` session with the bundle, `cat ~/.paperos/spool/<id>.ndjson | jq .event` to see the ordered events, then `pnpm log:ship <id>` and open the session in the prompt-log store. One minute.

**Edge cases**

* Store unreachable for hours: spool grows to 500 MB cap; oldest ships first.
* Killed by PAP-111: `SessionEnd` may not fire; orchestrator writes `session.killed`.
* Binary tool output: hash and size only.
* Resume shares a `transcript_path`: `seq` continues from stored max.
* Compaction: `PreCompact` logged so replays show the summary point.

**Dependencies**

Blocked by PAP-129 (ingest; may land up to 2026-09-21, spool-only until then). Integrates with PAP-106, PAP-96.

**Agent**

Built by Forge (Ops Runner) with Quill (Prompt Logger) defining the schema; reviewed by Sentinel (Security Auditor).

**Size**

M
"""

DESCRIPTIONS["PAP-108"] = """**Goal**

Specify how work passes cleanly between characters and sessions: what a finishing session leaves behind, how it is announced in Linear, how the receiver picks it up, and when and how anything escalates to `Needs Justin`. Clean baton passes stop the two most expensive failures: re-deriving context and silently dropping work.

**Scope**

* In: `docs/agents/handoff-protocol.md`, Zod `HandoffSchema` in `packages/agents/src/handoff.ts`, the `HANDOFF.md` template, `pnpm handoff lint`, three worked examples, orchestrator assignee switching.
* Out: decision card format (PAP-94, referenced), memory writes (PAP-109), notification delivery (PAP-136).

**Spec**

* A handoff is (1) code on a pushed branch, (2) `HANDOFF.md` at the worktree root, (3) the Linear comment whose PAP-92 footer carries `handoff: { kind, to, reason, artifacts: [{ type: branch | pr | doc | spec | screenshot, ref }], nextSteps[], openQuestions: [{ q, default }], contextFiles[] }`.
* Kinds: `build-to-review`, `review-to-build` (findings with severity, must-fix list), `spec-to-build`, `research-to-decision`, `escalate` (renders a PAP-94 decision card), `split` (proposed issue titles, sizes, dependencies in contract format), `crashed` (synthesised by the orchestrator).
* `HANDOFF.md` sections: Status, What changed, Decisions made, Verified, Not done, Next steps, Open questions (each with a default), Context files.
* `pnpm handoff lint` fails on missing sections, unpushed branch, open question without default, artifact referencing CI-only storage.
* Orchestrator: on a valid handoff comment, set assignee to `to`'s bot user, state per kind (`In Review` for build-to-review, `In Progress` for review-to-build), and queue the receiver.

**Interface contract**

* Provides: `HandoffSchema`, type `Handoff`, `validateHandoff()`, `renderHandoffComment()`, `lintWorktree(path)`, the `handoff` `$ref` used by PAP-92's footer schema, mapping `kind -> state`.
* Consumers: PAP-105 `linear-update` refuses invalid handoffs; PAP-96 switches assignee and state; PAP-94 receives `escalate`; PAP-110 grades handoff quality in Sentinel and Atlas tasks; PAP-81 reviewers emit `review-to-build`.
* Requires: PAP-104 characters and labels, PAP-92 footer, PAP-94 card format, PAP-105 script.

**Definition of done**

* Fixture tests for valid and invalid handoffs of every kind.
* `pnpm handoff lint` catches the four failure classes.
* Dry run: Nova builds a toy component, hands to Sentinel, Sentinel returns findings, Nova fixes and re-hands; four comments parse and the orchestrator switches assignee automatically (recording).
* One `escalate` dry run lands in `Needs Justin` as a decision card and is approved with `approve`.
* Doc reviewed by Atlas and Sentinel; changelog; Linear comment with recording.

**Test plan**

* Unit: schema per kind, `kind -> state` table, lint rules, `split` proposals validate against PAP-93 `validateIssue`.
* Integration: orchestrator handler on recorded comment webhooks; access cross-check refuses Beacon handing Stripe work to Iris.
* e2e: the four-comment dry run on staging.
* Visual: handoff comment rendering in Linear at 375 px (mobile) since Justin reads escalations on his phone.

**Demo**

In a toy worktree run `pnpm handoff lint` (fails on a missing default), fix it, run `pnpm skill linear-update handoff --to sentinel`, then watch the issue's assignee flip and state move to `In Review`. Ninety seconds.

**Edge cases**

* Receiver paused or over budget: handoff queues; Atlas notified after four hours.
* Session dies before posting: `crashed` synthesised from the last footer and `git status`, routed to the same character.
* Third disagreement round on one finding: auto-escalate with both positions.
* Artifact expired in CI: lint requires Linear or MinIO upload.
* Two open questions without defaults: blocked; handoffs must be actionable without a reply.

**Dependencies**

Blocked by PAP-104. Uses PAP-92, PAP-94, PAP-105.

**Agent**

Built by Atlas (lead) with Quill writing the document; reviewed by Sentinel.

**Size**

M
"""

DESCRIPTIONS["PAP-109"] = """**Goal**

Stop characters repeating mistakes: each character and each project keeps a curated memory of notes, decisions and gotchas in the docs system, loaded into the prompt at session start and appended at session end, with token budgets and review so it stays useful instead of becoming a landfill.

**Scope**

* In: memory MDX files, the loader, the writer with auto-merge rules, pruning job, `docs/agents/memory.md`.
* Out: raw transcripts (PAP-107), decision records themselves (PAP-130), search (PAP-138 optional).

**Spec**

* Files: `docs/memory/characters/<name>.md`, `docs/memory/projects/<key>.md`, `docs/memory/global.md`; frontmatter `owner`, `linearProjectId`, `maxTokens`, `updated`, `pinned[]`.
* Sections: `## Working notes` (rolling), `## Decisions` (one line each linking ADRs), `## Gotchas`, `## Do not`, `## Open threads`. One bullet per item, max 300 characters, trailing provenance `(PAP-123, 2026-09-21)`.
* Loader `packages/agents/src/memory/load.ts`: assembles global, project, character in that order; trims to `memory.maxTokens` (default 6000, split 1000/2000/3000) dropping oldest working notes first, never pinned; deterministic output placed after the system prompt and before the issue body so prompt caching holds.
* Writer `write.ts`: a session ends with a fenced ```` ```paperos-memory ```` block of `add:` and `remove:` entries in its final comment; the orchestrator applies it on a `memory/<session>` branch; entries pass PAP-107 redaction; auto-merge when under five entries and lint passes, else a PR to Quill.
* Pruning weekly: entries whose referenced paths no longer exist are flagged for Quill.

**Interface contract**

* Provides: `loadMemory({ character, projectKey, maxTokens }): { markdown, tokens, dropped[] }`, `applyMemoryBlock(sessionId, block)`, Zod `MemoryEntry`, the `paperos-memory` block grammar, git author convention `Forge (agent) <forge@paperos.bot>`.
* Consumers: PAP-96 prompt rendering calls `loadMemory`; PAP-105 `linear-update` validates the memory block; PAP-112 links memory files per character; PAP-110 checks that a second session used a recorded gotcha; PAP-128 renders the pages.
* Requires: PAP-104 `memory` field, PAP-128 docs engine (repo markdown fallback), PAP-130 for decision links, PAP-107 `redact`.

**Definition of done**

* Loader tests: trimming order, pinned preservation, missing files, token estimate within 10 percent of `count_tokens` on five samples.
* Writer tests: apply add and remove, reject over-long or provenance-less entries, auto-merge threshold.
* Live: two consecutive Forge sessions; the second's transcript uses a gotcha from the first (excerpt in comment).
* Memory pages render with "last updated by"; screenshots at 375 and 1280 px.
* Docs page; changelog; Linear comment with excerpt and screenshots.

**Test plan**

* Unit: loader determinism (same files, same bytes), split budgets, provenance parsing, redaction pass-through.
* Integration: writer against a temp git repo with concurrent branches rebasing (order-independent bullets).
* e2e: two-session live run on staging.
* Visual: docs engine memory page at 375 and 1280 px.

**Demo**

Run `pnpm memory load --character forge --project data-layer` and read the assembled block with token count; append a gotcha through `pnpm memory apply fixtures/block.md`, re-run load and see it first. One minute.

**Edge cases**

* Concurrent updates: later branch appends rather than fails.
* Entry containing a secret: redacted entries dropped with a note.
* No memory file yet: empty template created on first write.
* Only pinned entries exceed budget: warn in `/status`; Quill curates.
* Project renamed: keyed by Linear project id in frontmatter.

**Dependencies**

Blocked by PAP-104, PAP-128. Soft: PAP-130, PAP-138.

**Agent**

Built by Quill (Prompt Logger sub-agent) with Atlas wiring the loader; reviewed by Sentinel.

**Size**

M
"""

DESCRIPTIONS["PAP-110"] = """**Goal**

Measure the agents themselves: a harness runs golden tasks for every character nightly, scores outputs with deterministic checks and an LLM judge, tracks the trend and opens a Linear issue when a character regresses. Prompt, skill and model changes get judged by numbers. Umbrella for three children; relabelled `Type/Build` because it builds a harness.

**Scope**

* Children (build in order, 2 can start after 1's task format is fixed):
  * {{agents/eval-harness/runner}}: task format, runner, deterministic graders and results table.
  * {{agents/eval-harness/tasks}}: the golden task set (three per lead, one per sub, about 55) with fixture repos.
  * {{agents/eval-harness/judge}}: LLM judge, trend, regression issues, nightly schedule and report page.
* Out: product e2e (quality project), end-user feature prompts, vendor benchmarks.

**Spec**

* Layout `packages/agents/evals/tasks/<character>/<task-id>/{task.yaml, expected/, grade.ts | rubric.md}`; `task.yaml`: `prompt`, `fixtures`, `allowedTools`, `maxTurns`, `budgetUsd`, `version`, `flaky`.
* Runner `pnpm evals run [--character] [--task] [--model] [--effort]` launches through the Agent SDK with the PAP-106 bundle in a throwaway worktree; cheap mode Sonnet `low` for skill PRs under $5.
* Grading: deterministic first (tests pass, files exist, schema valid, footer present, no `scope-denied` events), then judge (Sentinel Code Reviewer definition, strict JSON output) 0-5 per rubric criterion; weighted final score; both stored.
* Table `orchestrator.eval_runs(run_id, character, task, task_version, model, score, checks_json, judge_json, cost_usd, duration_ms, transcript_ref, git_sha, at)`.
* Regression: score drops more than 15 percent from the seven-run median, or a check that passed three times fails: create or update `Eval regression: <character>/<task>` (Type Review, Character Sentinel). Nightly 03:00 UTC, cap $60 via PAP-111, all runs logged with `issueKey: EVAL`.

**Interface contract**

* Provides: `pnpm evals {run,list,report}`, `eval_runs` table, `EvalResult` Zod type, `docs/agents/evals.md` regenerated nightly, the regression issue template, judge schema `judge.schema.json`.
* Consumers: PAP-104 prompt PRs (smoke gate), PAP-105 skill PRs (cheap mode), PAP-111 (cap), PAP-113 (score per character optional), PAP-241 (Gate 2 calibration reuses the seeded-bug fixture and F1 scorer), {{pm-linear/weekly-reaudit}} (eval trend section).
* Requires: PAP-104 roster and smoke transcripts as fixtures, PAP-105 skills, PAP-106 bundles, PAP-98 cost, PAP-111 caps, Linear ids from PAP-91.

**Definition of done**

* All three children Done.
* Full nightly run under three hours and under cap; results table screenshot at 1280 px.
* Regression detection proven by breaking Iris's prompt on a branch and observing the Linear issue (screenshot).
* Judge agreement above 80 percent on 20 spot-checked outputs.
* Report page renders; changelog; Linear comment with first baseline.

**Test plan**

* Umbrella integration: `pnpm evals run --all --model claude-sonnet-5 --effort low` on CI produces a table for all characters; determinism check on graders.
* Regression rule tested with synthetic run histories (fake clock).
* Visual: report page at 1280 px only.

**Demo**

Run `pnpm evals run --character quill --task page-spec-invoices` and watch the deterministic checks and judge score print with a transcript link; then `pnpm evals report` to see the trend table. Two minutes.

**Edge cases**

* Flaky task: run three times, median; cannot trigger regressions alone.
* Model outage: run `incomplete`, retried next night.
* Checks pass but judge low: report both, flag disagreement.
* Budget cap mid-run: remaining `skipped-budget`.
* Fixture repo drifts: pinned to a template SHA; weekly bump job re-baselines.

**Dependencies**

Blocked by PAP-104, PAP-105. Uses PAP-106, PAP-111, PAP-98.

**Agent**

Built by Sentinel (lead) with Atlas on the runner; reviewed by Quill for task clarity.

**Size**

L (umbrella; children M, M, M)
"""

DESCRIPTIONS["PAP-111"] = """**Goal**

Bound spend at every level so no runaway session or over-eager character can burn the budget: per-session and per-day caps per character, max-turn limits, per-issue caps by size, a release-week reserve and a kill switch that stops one session, one character or everything within seconds and leaves a clean record.

**Scope**

* In: `src/limits/{preflight,inflight,kill,reset}.ts` in the orchestrator, tables `budgets` extension and `kill_state`, the `budget-hold` label flow, the `KILL` comment grammar, `docs/pm/cost-controls.md`.
* Out: metering itself (PAP-98), eval caps content (PAP-110 passes its cap in).

**Spec**

* Limits: schema `budget` (`perSessionUsd`, `perDayUsd`, `maxTurns`) plus config `limits.perIssueUsd` by Size (S 60, M 180, L 450), `globalPerDayUsd`, `reserveUsd`; label override `budget:<usd>` up to twice the default.
* Pre-flight before spawn: character daily remaining, issue remaining across attempts, global remaining, reserve untouched; expected cost is the character's median of the last ten sessions (default $25); failure comments and labels `budget-hold`.
* In-flight: `liveTotal(sessionId)` from PAP-98; at 80 percent inject a wrap-up user turn asking for the handoff (PAP-108); at 100 percent abort through the SDK abort controller with a 20 s grace, commit `wip:`, push, post footer `status: "partial"`.
* Kill switch: comment `KILL <PAP-key> | KILL <character> | KILL ALL [hard]` by Justin on any issue or the burn report; also `POST /kill` with an admin token; `/status` shows `paused`; `RESUME` reverses. The poll loop scans the burn-report comments every 30 s as a webhook fallback.
* Reviewers (Sentinel subs) have a separate daily pool matching the 30 percent review share.

**Interface contract**

* Provides: `preflight(issue, character): Allow | Hold`, `attachInflight(session, abortController)`, `kill(scope, hard?)`, `resume(scope)`, `limitsFor(character)`, events `limit.warned`, `limit.aborted`, `kill.requested`, `kill.completed` on the PAP-96 bus, `/status.limits` block.
* Consumers: PAP-96 (spawn path and abort), PAP-99 (`budget-hold` exclusion), PAP-110 (`--cap` per run), PAP-113 (paused ring, pause button calls `kill(character)`), PAP-108 (over-budget receivers queue).
* Requires: PAP-98 `liveTotal`, `spent`, `budgets`; PAP-103 `budget` fields; PAP-94 for reserve release decisions; PAP-107 `session.killed` writer.

**Definition of done**

* Unit tests for pre-flight decisions, 80 and 100 percent thresholds, reset at day boundary, cap arithmetic.
* Integration: a toy session with `perSessionUsd: 2` is warned then aborted; `wip:` pushed; footer posted (recording).
* `KILL ALL` from Justin stops three running sessions within five seconds; `/status` paused; `RESUME` works (recording).
* Runbook including "what to do if the budget is gone"; changelog; Linear comment with recordings.

**Test plan**

* Unit: decision table, median cost with fewer than ten sessions, label override cap, reviewer pool isolation.
* Integration: fake meter and fake clock driving in-flight thresholds; grace period lets a mocked `git push` finish.
* e2e: kill and resume on staging with three sessions.
* Visual: `/status` limits block at 1280 px.

**Demo**

Start a toy session with `perSessionUsd: 1`, watch `/status` show the running total, see the wrap-up warning appear in the transcript at 80 percent and the abort with a `wip:` commit at 100 percent. Then post `KILL ALL` and watch every slot pause. Two minutes.

**Edge cases**

* Metering lag: reconcile with the SDK `result` and charge overrun to the next allowance.
* Kill during push: grace lets it finish; never a worktree without a `wip:` commit.
* Webhooks down when `KILL` is posted: poll scan catches it within 30 s.
* Reserve breached in the final days: only Justin releases it via PAP-94.
* Sub-agents inside a session: parent cap applies; SDK cost includes them.

**Dependencies**

Blocked by PAP-98. Integrates with PAP-96, PAP-103, PAP-94.

**Agent**

Built by Atlas (Dispatcher sub-agent); reviewed by Sentinel.

**Size**

M
"""

DESCRIPTIONS["PAP-112"] = """**Goal**

Publish the handbook a human opens to understand the agent org: who each character is, what it owns, how to summon it from Linear or the CLI, what it may never do and how to change it. Written for Justin first, generated from the roster wherever possible so it never drifts from reality.

**Scope**

* In: `docs/agents/handbook/` (index with org chart, one page per lead with sub sections, `summoning.md`, `limits.md`, `changing-the-org.md`, `glossary.md`), `pnpm agents docs [--check]`, the `@character` mention handler.
* Out: the org chart UI (PAP-113), prompt content (PAP-104), the privilege matrix generation (PAP-106).

**Spec**

* Per-character page: role and remit, reports to, subs with triggers, generated tables for tools, MCP servers and access scopes from `roster.json` and the PAP-106 matrix, skills, budgets, escalation rules, example tasks it excels at, tasks to route elsewhere, three completed issues (linked), memory file link. Under 1200 words; index under 600; plain language with glossary links.
* Every "may not" statement links to the enforcing mechanism (deny list line, hook, branch protection rule).
* Frontmatter `generatedFrom`, `lastVerified`; CI fails if `roster.json` changed and docs were not regenerated.
* Mention handler: on `Comment.create` from a human containing `@atlas`..`@scout`, spawn a read-only session (`plan` mode, `maxTurns` 8, Sonnet unless the question is architectural), reply in a comment with the PAP-92 footer, cost capped at $3 through PAP-111; agent-authored mentions ignored.

**Interface contract**

* Provides: handbook pages in the PAP-128 docs engine (repo markdown fallback), `pnpm agents docs --check`, the mention handler registered via PAP-97 `registerWebhookHandler("linear", "Comment", "create")`, a `summon` contract: assign `Character/<name>` and move to `Ready for Claude`, or `pnpm agents run <name> --issue PAP-123`.
* Consumers: Justin and future staff; PAP-95 (links the origin story); PAP-113 drawer "Open handbook page" links `docs/agents/handbook/<name>`; PAP-134 registry indexes the pages.
* Requires: PAP-104 `roster.json`, PAP-106 matrix, PAP-97 webhooks, PAP-111 cap, PAP-128 rendering.

**Definition of done**

* All pages render with generated tables matching `roster.json`; `--check` in CI.
* `@sentinel` mention on a test issue gets a relevant reply within two minutes (screenshot).
* Read-through by Sentinel for accuracy against the privilege matrix and by Quill for clarity; every "may not" links.
* Screenshots at 375 and 1280 px; changelog; Linear comment with links and screenshots.

**Test plan**

* Unit: table generation snapshot from a roster fixture; prose lint flagging tool names absent from the generated table; word counts.
* Integration: mention handler on recorded comment webhooks, agent-author ignore, cost cap enforcement with a fake meter.
* e2e: live mention on staging.
* Visual: two handbook pages at 375 px (phone) and 1280 px in light and dark through the docs engine.

**Demo**

Open the handbook index on a phone, tap Sentinel, read its "may not merge" line and follow the link to the branch protection rule; then post `@sentinel is RLS on pm_issue correct?` on a test issue and read the reply. Two minutes.

**Edge cases**

* Retired character: page moves to `handbook/retired/` with the ADR; mentions redirect.
* Mention asking for an action: reply explains actions come from issues and offers to draft one (PAP-93 contract) on `yes`.
* Roster and prose disagree: CI lint fails.
* Docs engine down: markdown readable on the forge; relative links.
* Long access tables (Atlas): collapsed details block.

**Dependencies**

Blocked by PAP-104. Uses PAP-106, PAP-97, PAP-128, PAP-111.

**Agent**

Built by Quill (lead); reviewed by Sentinel (accuracy) and Atlas (org fit).

**Size**

M
"""

DESCRIPTIONS["PAP-113"] = """**Goal**

Make the agent org a first-class page in the product: an interactive org chart of characters and subs showing who reports to whom, what each is doing right now, what tools and access it holds and how much it has spent, drawn on the canvas engine so it can be rearranged, annotated and commented on like any other PaperOS canvas.

**Scope**

* In: route `/agents` with `specs/agents/org-chart.spec.yaml` and `character.spec.yaml`, `CharacterNode` component, oRPC `agents.roster` and `agents.status`, detail drawer with pause action, tree-list fallback under 768 px.
* Out: the status contract itself ({{agents/session-observability}}), the canvas engine (PAP-132), presence styling (PAP-146, consumed).

**Spec**

* Canvas on PAP-132: nodes for Justin, nine leads, 28 subs from `agents.roster`; ELK layered layout with manual nudges persisted per user in `canvas_layout`; edges for `reportsTo`; badges `idle | working(issueKey) | reviewing | paused | over-budget | killed | stale`.
* Live data: `agents.status` proxies the orchestrator `/status` (`SessionStatus[]` from {{agents/session-observability}}) and PAP-98 (`spentTodayUsd`, `dailyCapUsd`), polled every 10 s until PAP-146 pushes it.
* Drawer: role, prompt excerpt, tools and MCP servers, access scopes (PAP-106 matrix), skills, current session with elapsed time and cost, last five issues, memory link (PAP-109), handbook link (PAP-112), `Pause` and `Resume` calling PAP-111 through `agents.control` (permission `agents.control` from the access section).
* Responsive: under 768 px a collapsible tree list with the same badges and a full-screen sheet for the drawer. Nodes focusable in tree order; arrow keys move between siblings and levels; state in `aria-label`.

**Interface contract**

* Provides: `CharacterNode` in `packages/ui` with stories for seven states, procedures `agents.roster(): Character[]`, `agents.status(): SessionStatus[]`, `agents.control({ character, action: "pause" | "resume" })`, page specs consumed by PAP-122, the graph-loader pattern reused from PAP-123.
* Consumers: Justin (staff audience), PAP-102 (shares the character badge renderer), PAP-146 (pushes status over the realtime layer later).
* Requires: PAP-104 `roster.json`, {{agents/session-observability}} `SessionStatus`, PAP-98 spend, PAP-111 control, PAP-132 canvas, PAP-106 matrix, PAP-152 focus management.

**Definition of done**

* Page specs validate; conformance tests pass.
* Storybook stories for all states, light and dark; axe passes.
* Screenshots at 320, 375, 768, 1024, 1280, 1920 and 2560 px in both themes.
* Live: start a session via Linear and watch the node switch to `working` within 10 s; pause from the drawer stops it (recording).
* Keyboard and screen-reader labels verified; Pages demo with mocked status; changelog; Linear comment.

**Test plan**

* Unit: badge derivation from `SessionStatus` (fake clock for `stale`), layout persistence, permission-gated pause button.
* Integration: `agents.status` against a mocked orchestrator including unreachable and orphan-character responses.
* e2e (Playwright): open, focus-navigate with arrows, open drawer, pause with a mocked control endpoint; run at 375 (tree list) and 1280 (canvas).
* Visual: seven-width matrix through gate 3; the 768 px switch asserted.

**Demo**

Open `/agents`, watch Forge's node turn `working` as a staging session starts, click it, read its current issue and spend, press `Pause` and see the badge flip and `/status` confirm. Two minutes.

**Edge cases**

* Orchestrator unreachable: "status unknown" with last-known time, no infinite spinner.
* More than six subs under a lead: collapsed by default.
* Character in status but not roster: orphan node with warning.
* Several concurrent sessions for one character: badge shows count; drawer lists all.
* Canvas library not chosen (PAP-132 pending): tree list ships first.

**Dependencies**

Blocked by PAP-104, PAP-132, {{agents/session-observability}}. Uses PAP-98, PAP-111, PAP-106. Soft: PAP-146.

**Agent**

Built by Nova (Canvas Cartographer sub-agent) with Iris (Component Crafter) on `CharacterNode`; reviewed by Sentinel (Visual Inspector).

**Size**

M
"""
