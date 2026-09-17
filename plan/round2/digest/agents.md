# agents — Agent Characters & Orgs
PHASE P0 prio 1 dependsOn ['pm-linear']
SUMMARY: The character roster: lead agents with sub-characters, each with explicit tools, access, plugins, skills, memory, budgets and handoff rules, visible as an org chart in-app.
DESC: Goal: the people building PaperOS are Claude characters, and they must be as legible as human staff. A character schema defines name, role, reportsTo, tools, MCP servers, access scopes, plugins, skills, memory and escalation rules. Nine leads and their sub-characters are installed as .claude/agents definitions with a shared skills library. Per-character MCP allowlists and permission modes are verified for least privilege. Persistent memory, a handoff protocol, an eval harness with golden tasks, budgets with a kill switch and prompt logging make the org safe to run unattended. An org chart UI shows who is doing what with which access. Non-goal: autonomous hiring of new characters without a Needs Justin approval.
MILESTONES: ['Roster defined and installed 2026-09-20: Schema, nine leads with sub-characters, skills library, tool scopes, logging hook', 'Sub-agents, skills and evals live 2026-09-25: Memory, handoffs, eval harness, cost controls, handbook', 'Agent org visible in app 2026-09-30: Org chart UI with live tasks and access']


## PAP-103 [P0 Spec S prio1 Ready for Claude] Define the character schema: name, role, reportsTo, tools, MCP servers, access scopes, plugins, skills, memory, escalation rules
key=agents/character-schema milestone=Roster defined and installed agent=Built by Atlas (Decomposer sub-agent); reviewed by Sentinel 
blockedBy=[] blocks=['PAP-105', 'PAP-104']
GOAL: Define the single typed shape every Claude character is declared in, so that roster files, `.claude/agents` definitions, MCP allowlists, permission modes, budgets, memory locations and escalation rules are all generated from one source of truth instead of hand-maintained in five places. Everything in the agents project and the orchestrator reads this schema.
SCOPE: In:

* Zod schema `packages/agents/src/schema.ts` in paperos-template exporting `CharacterSchema` and `RosterSchema`, plus a generated JSON Schema `packages/agents/schema/character.schema.json` for editor validation of YAML files.
* Fields: `name` (kebab id and display name), `role` (one sentence), `reportsTo` (character name or `justin`), `kind` (`lead` | `sub`), `parent` for subs, `description` (used as the `.claude/agents` description that drives automatic delegation), `model` (`claude-fable-5-1` default; `claude-sonnet-5` allowed for subs), `effort` (`low`..`max`), `permissionMode` (`default` | `acceptEdits` | `plan` | `dontAsk`), `tools.allow[]` / `tools.deny[]` (Claude Code tool names and `mcp__server__tool` patterns), `mcpServers[]` (names resolved against `libraries/mcp-servers` catalog), `access[]` (scope strings matching plan.json, validated against a registry), `plugins[]`, `s
SPEC(first 1200): * Access scope registry `packages/agents/src/scopes.ts`: the union of every `access` string used in plan.json `agents[]` (`linear:admin`, `repo:write (all)`, `stripe:test-mode write`...), normalised to `resource:verb[:qualifier]` and documented; unknown scopes fail validation.
* Tool names validated against a committed list of Claude Code built-ins (Read, Write, Edit, Bash, Glob, Grep, WebFetch, WebSearch, Task, TodoWrite...) plus MCP patterns; the list has a `lastVerified` date so it is refreshed.
* Generated JSON Schema wired into `.vscode/settings.json` `yaml.schemas` for authoring help.
* Golden fixtures: `fixtures/valid/atlas.yaml`, `fixtures/invalid/*.yaml` each violating one rule with the expected error code.
* Semantic versioning of the schema (`schemaVersion` field); a migration note is required for breaking changes.
DOD:
* `pnpm agents validate` passes on the fixtures and fails on each invalid fixture with the expected code (Vitest).
* JSON Schema generated and checked in; editing a YAML in VS Code shows completions (screenshot).
* Doc reviewed by Quill; every field has a one-line purpose and an example.
* The nine leads and their subs from plan.json can be expressed without adding fields (dry-run conversion script output attached).
* Changelog entry; Linear comment linking doc and fixtures.
EDGE:
* A character needs a tool its lead lacks (Sentinel's Visual Inspector needs a vision MCP): the lead must be granted it too; the validator says so explicitly.
* Circular `reportsTo`: detected, error names the cycle.
* MCP catalog not yet published (`libraries/mcp-servers` pending): validator accepts names listed in a local `mcp-catalog.stub.json` and warns.
* Two characters share a Linear label: error; labels are unique.
* Budget omitted: inherit from parent, then from roster defaults; never unlimited.
* Model string unknown to the price table in `pm-linear/credit-metering`: warning, not error.
DEPS: None (`readyNow: true`). Consumed by `agents/roster-v1`, `agents/tool-scopes`, `agents/cost-controls`, `agents/org-chart-ui`, `pm-linear/orchestrator`.


## PAP-104 [P0 Build L prio1 Backlog] Write the nine lead characters and their sub-characters as .claude/agents definitions with system prompts
key=agents/roster-v1 milestone=Roster defined and installed agent=Built by Atlas (lead) with Quill (Page Spec Writer) drafting
blockedBy=['PAP-103'] blocks=['PAP-218', 'PAP-208', 'PAP-192', 'PAP-113', 'PAP-112', 'PAP-110', 'PAP-109', 'PAP-108', 'PAP-106']
GOAL: Bring the org to life: write the nine lead characters (Atlas, Forge, Iris, Quill, Sentinel, Nova, Ledger, Beacon, Scout) and their 28 sub-characters from plan.json as validated character YAML files with carefully written system prompts, and generate the `.claude/agents/*.md` definitions that Claude Code loads, so the orchestrator can spawn any of them by name.
SCOPE: In:

* `packages/agents/characters/*.yaml` for all 37 characters, fields filled from plan.json `agents[]` (role, reportsTo, tools, access, plugins, subAgents) and completed with model, effort, permission mode, budgets, skills, memory path and escalation rules.
* System prompts in `packages/agents/prompts/<name>.md`, 300-800 words each, structured as: identity and remit, what good looks like, hard limits (what it may never do), how it reports (playbook footer), when it escalates, its sub-characters and when to delegate, its favourite tools. Prompts follow the Fable 5.1 guidance: state goals and constraints, avoid over-prescriptive step lists, ask for progress notes on long tasks.
* Shared prompt fragments `packages/agents/prompts/_shared/` (playbook pointer, comment footer, code standards, review gates) included by reference at build time to avoid drift.
* `pnpm agents build` implementati
SPEC(first 1200): * Defaults: leads `claude-fable-5-1`, effort `xhigh`, `acceptEdits`; subs that mostly read (Library Evaluator, Prompt Logger, Changelog Scribe) `claude-sonnet-5` at `medium`; reviewers (Sentinel subs) `claude-fable-5-1` at `high` with `permissionMode: plan` and no Write/Edit tools.
* Budgets seeded from the plan's area shares: Sentinel and its subs get 30 percent of daily allowance; Atlas 8; builders share the rest; exact numbers in `roster.yaml` defaults.
* Escalation rule shared by all: `when: "irreversible action or spend over budget" action: needs-justin`; Atlas additionally `when: "cycle in dependencies" action: needs-justin`.
* Sentinel prompts include the severity taxonomy from `quality/review-rubrics` by reference and explicitly forbid merging.
* Build is deterministic; CI fails if `.claude/agents` is out of date with the YAML (`pnpm agents build --check`).
DOD:
* `pnpm agents validate` passes for all 37 characters; tree renders (`pnpm agents tree`) and matches plan.json.
* `.claude/agents/*.md` generated and committed; `--check` wired into CI gate 1.
* Smoke tasks executed for each lead; transcripts show in-role behaviour, correct footer and a refusal when asked to do something outside the deny list; summary table posted as a Linear comment.
* Prompts reviewed by Sentinel for contradictory instructions and by Quill for clarity; each prompt under 800 words (word-count test).
* `roster.json` consumed successfully by `pm-linear/orchestrator` in a dry run.
* Changelog entry; Linear comment with the tree and smoke results.
EDGE:
* Two subs with near-identical descriptions (Code Reviewer vs Edge Case Hunter): sharpen descriptions until a classification test of 20 sample tasks routes each correctly.
* A lead's prompt exceeds the budget when shared fragments are included: fragments count toward the limit; trim.
* Character invoked outside a repo checkout (Atlas planning session): prompts must not assume `cwd` is a worktree.
* Model unavailable (refusal fallback or outage): orchestrator substitutes the roster's `fallbackModel` (default `claude-opus-5`); prompts must not name the model.
* Justin renames a character: `name` is the id; `displayName` changes freely.
* Plan.json adds a tenth lead later: no code change, only YAML plus a Character label in Linear.
DEPS: * `agents/character-schema` (schema, validator, build stub).
* Soft: `pm-linear/session-playbook` (referenced by prompts), `quality/review-rubrics` (referenced by Sentinel prompts).


## PAP-105 [P0 Build M prio1 Backlog] Build the shared skills library (page-from-spec, review-pr, screenshot-audit, write-adr, linear-update) as .claude/skills
key=agents/skills-library milestone=Roster defined and installed agent=Built by Quill (lead) for prose and Atlas (Dispatcher) for s
blockedBy=['PAP-103'] blocks=['PAP-134', 'PAP-118', 'PAP-110']
GOAL: Package the procedures every character repeats into `.claude/skills` so sessions do them the same way every time and spend fewer tokens rediscovering them: build a page from a spec, review a PR against the rubrics, audit screenshots, write an ADR, and update Linear. Skills are versioned, tested and listed in the character schema.
SCOPE: In:

* Skills under `.claude/skills/<name>/SKILL.md` in paperos-template, each with frontmatter (`name`, `description` phrased as when-to-use triggers) and a body of at most 1500 words, plus `scripts/` and `templates/` folders where a deterministic script beats prose:
  * `page-from-spec`: read `specs/<page>.spec.yaml`, run `spec-builder/layout-codegen` scaffold, implement logic, add stories, run conformance tests, capture screenshots at the breakpoint matrix, open PR with `forge/pr-templates`.
  * `review-pr`: fetch diff, apply `quality/review-rubrics`, produce the structured review JSON block and GitHub review; never approve own PR; severity taxonomy embedded by reference.
  * `screenshot-audit`: load the Playwright artifact folder, inspect each image for overflow, truncation, contrast and misalignment, output the annotated findings format expected by `quality/screenshot-annotation`.
 
SPEC(first 1200): * Frontmatter `description` must start with a verb and include trigger phrases ("Use when reviewing a PR..."); a lint script checks length and presence.
* Scripts are TypeScript run with `tsx`, read config from env (`LINEAR_API_KEY`, `PAPEROS_ISSUE`), exit non-zero on failure and print machine-readable JSON on the last line.
* `linear-update` enforces comment dedupe and the max-one-comment-per-30-minutes rule from the playbook by checking the last comment timestamp.
* `page-from-spec` includes a checklist file the session copies into the PR body; steps referencing tools not yet built (codegen) degrade to manual instructions with a `TODO(spec-builder/layout-codegen)` marker.
* Each SKILL.md has `version` and `changelog` sections; skill changes require a PR reviewed by the owning character's lead.
DOD:
* Five skills present, lint passes, `skills.json` generated.
* Script tests pass in Vitest with fixtures (mocked Linear via `nock`).
* Dry run: a Claude Code session invokes each skill on a toy repo; transcripts show the skill loaded and steps followed; the `linear-update` skill posts a correctly formatted comment (screenshot).
* `review-pr` dry run on a seeded PR produces a review whose JSON block validates against the schema shared with `quality/review-agents`.
* Docs `docs/agents/skills.md` listing skills, triggers and owners; changelog entry; Linear comment with transcript links.
EDGE:
* Skill invoked by a character not allowed to use it (Beacon running `review-pr`): the script checks `PAPEROS_CHARACTER` against `skills.json` and refuses.
* Linear rate limit inside `linear-update`: retry with backoff, then write the comment to `artifacts/pending-comments/` for the orchestrator to flush.
* Screenshot folder missing or empty: `screenshot-audit` reports `no-artifacts` rather than hallucinating findings.
* ADR number collision from parallel sessions: numbering script uses the issue key as suffix (`0042-PAP-123-title.md`) and reconciles on merge.
* Spec file invalid: `page-from-spec` stops and runs the validator's fix suggestions first.
* SKILL.md grows past 1500 words: lint fails; move detail into `references/` files loaded on demand.
DEPS: * `agents/character-schema` (skills field, build).
* Interfaces: `quality/review-rubrics` (review JSON schema), `quality/playwright-matrix` (artifact layout), `forge/pr-templates`, `spec-builder/layout-codegen` (optional).


## PAP-106 [P0 Build M prio1 Backlog] Implement per-character MCP allowlists and permission modes and verify least privilege with an automated test
key=agents/tool-scopes milestone=Roster defined and installed agent=Built by Forge (Ops Runner) for secrets and bundles, Atlas (
blockedBy=['PAP-48', 'PAP-104'] blocks=[]
GOAL: Make the character schema's `tools`, `mcpServers`, `permissionMode` and `access` real: every session launched for a character runs with exactly the allowlist the schema declares, and an automated test proves no character can call a tool, MCP server or forge credential outside its scope. This is the least-privilege guarantee that lets the org run unattended.
SCOPE: In:

* `pnpm agents build` emits per-character runtime bundles in `packages/agents/dist/<name>/`: `settings.json` (`permissions.allow`, `permissions.deny`, `permissions.defaultMode`), `.mcp.json` (only the servers listed, with env var names not values), and `hooks.json` (a `PreToolUse` hook that re-checks the allowlist as defence in depth).
* Orchestrator integration: `pm-linear/orchestrator` passes `allowedTools`, `disallowedTools`, `permissionMode`, `mcpServers` from the bundle to the Agent SDK `query()` options and sets `settingSources` so project settings are merged; a session cannot start if the bundle is stale (`build --check`).
* Credential scoping: forge tokens from `forge/bot-accounts` and Linear/Stripe/Webflow keys are injected per character from a secrets map (`ops/secrets/characters.env.sops`) so Beacon never sees a repo-admin token; `access[]` strings map to concrete secret 
SPEC(first 1200): * Deny always includes: `Bash(git push*main*)`, `Bash(rm -rf*)`, `Bash(curl*|sh)`, `Write(.claude/settings.json)`, `Write(ops/secrets/**)`; allow lists are additive per character.
* `PreToolUse` hook script `packages/agents/hooks/enforce-scope.ts` reads the bundle, matches `tool_name` and `tool_input` against allow/deny (glob on Bash command strings, path globs for file tools, `mcp__server__tool` for MCP), returns permission decision `deny` with a reason that names the schema field to change.
* Hook logs every denial to the prompt log (`agents/prompt-logging-hook`) with `event: "scope-denied"`.
* Test runs in CI nightly and on any change to `packages/agents/**` or `.claude/**`; per-run cost capped (Sonnet 5 at `low` effort, `maxTurns: 3`) and recorded by metering.
* Secrets never appear in bundles or logs; a scan asserts no value from the secrets map appears in `dist/`.
DOD:
* Bundles generated for all 37 characters; `--check` in CI.
* Least-privilege suite passes: every forbidden probe denied, every allowed probe succeeds; results table attached (37 rows).
* Hook denial demonstrated in a recorded session with the reason text visible.
* Privilege matrix doc generated and reviewed by Sentinel (Security Auditor).
* Secrets scan passes; sops-encrypted file documented in the runbook.
* Changelog entry; Linear comment with the results table and recording.
EDGE:
* Tool renamed in a Claude Code release: hook fails closed (unknown tool denied) and the known-tools list has a `lastVerified` alert in the nightly run.
* MCP server exposes a new dangerous tool: allowlists use explicit `mcp__server__tool` names, not `mcp__server__*`, except for read-only servers marked `readOnly: true` in the catalog.
* Bash command obfuscation (`g''it push`): hook normalises quotes and whitespace; still flagged by the Security Auditor as best-effort, hence Docker isolation and branch protection remain the real wall.
* Sub-agent spawned by a lead inherits a wider scope: the Task tool passes the sub's own bundle; test spawns a sub and probes.
* Character needs a temporary extra scope for one issue: issue label `scope:+<name>` grants it for that session only and posts a comment; expires with the session.
* Hook script itself fails (syntax error): Claude Code treats a hook
DEPS: * `agents/roster-v1` (characters to build bundles for).
* `forge/bot-accounts` (per-character forge tokens).
* Integrates with `pm-linear/orchestrator` launch options and `libraries/mcp-servers` catalog.


## PAP-107 [P0 Build M prio1 Backlog] Hook every session's prompts, responses and tool calls into the prompt-log store
key=agents/prompt-logging-hook milestone=Roster defined and installed agent=Built by Forge (Ops Runner) with Quill (Prompt Logger) defin
blockedBy=['PAP-129'] blocks=[]
GOAL: Record how the product was built: every prompt, response, tool call and tool result from every character session, with session, character, issue, tokens and cost, flows into the prompt-log store with secrets redacted before they leave the machine. This is the audit trail, the training set for evals and the memory source for characters.
SCOPE: In:

* Claude Code hooks in the generated character bundles (`agents/tool-scopes`): `SessionStart`, `UserPromptSubmit`, `PreToolUse`, `PostToolUse`, `SubagentStop`, `Stop`, `SessionEnd`, each running `packages/agents/hooks/log-event.ts` which reads the hook JSON from stdin (`session_id`, `transcript_path`, `cwd`, `hook_event_name`, `tool_name`, `tool_input`, `tool_response`) and appends a normalised event to a local spool `~/.paperos/spool/<session_id>.ndjson`.
* Transcript ingestion on `Stop`/`SessionEnd`: parse the JSONL at `transcript_path` for assistant messages and their `usage` (input, output, cache read, cache creation tokens) so token counts are exact even when hooks miss a turn.
* Orchestrator path: sessions launched through the Agent SDK also stream messages directly; `pm-linear/orchestrator` writes the same event shape, so the store sees one format regardless of launch method.
SPEC(first 1200): * Hook scripts must finish under 500 ms so they do not slow the session; heavy work (transcript parsing, shipping) happens in `Stop`/`SessionEnd` or in a detached shipper process.
* Sequence numbers are monotonic per session from a local counter file; `seq` gaps are reported by the store.
* Issue key and character come from env (`PAPEROS_ISSUE`, `PAPEROS_CHARACTER`) set by the orchestrator, or from the worktree branch name as a fallback.
* Tool outputs above 64 KB are stored as a blob in `data-layer/file-storage` (MinIO) with a URL in the event when available; otherwise truncated.
* A `--dry-run` mode prints events to stderr for local debugging; hook failures never block the session (exit 0 with stderr note) except for the scope hook which is separate.
DOD:
* Unit tests for redaction (30 secret-like fixtures, zero false negatives on the fixture set, false positives listed), schema validation, transcript parsing on three real transcripts.
* Integration: a 20-turn test session produces a complete, ordered event set in the store; token totals match the SDK `result` message within 1 percent.
* Hook latency measured under 500 ms p95 (numbers in the comment).
* Secrets scan of a shipped spool shows no raw key material.
* `docs/agents/prompt-logging.md` (what is logged, retention, how to inspect a session locally); changelog entry; Linear comment with the integration results.
EDGE:
* Store unreachable for hours: spool grows; shipper caps at 500 MB per host and pages the orchestrator log; oldest sessions ship first.
* Session killed by the kill switch (`agents/cost-controls`): `SessionEnd` may not fire; the orchestrator writes a synthetic `session.killed` event.
* Sub-agent transcripts (Task tool): captured via `SubagentStop`, linked by `parentSessionId`.
* Binary tool output (screenshots read via Read): store a hash and size, not bytes.
* Redaction removes something needed for debugging (a URL with a token): keep the host and path, redact only the credential segment.
* Two sessions share one `transcript_path` after a resume: `seq` continues from the stored max for that session id.
* Compaction rewrites history: log the `PreCompact` event so replays show where context was summarised.
DEPS: * `collab/prompt-log-store` (ingest endpoint, dedupe, storage).
* Integrates with `agents/tool-scopes` bundles and `pm-linear/orchestrator` SDK stream.


## PAP-108 [P1 Spec M prio1 Backlog] Design the handoff protocol between characters: artifact contract, Linear comment format, escalation to Needs Justin
key=agents/handoffs milestone=Sub-agents, skills and evals live agent=Built by Atlas (lead) with Quill writing the document; revie
blockedBy=['PAP-104'] blocks=[]
GOAL: Specify how work passes cleanly between characters and sessions: what a finishing session must leave behind (the artifact contract), how it is announced in Linear, how the receiving character picks it up, and when and how anything escalates to `Needs Justin`. Clean baton passes stop the two most expensive failure modes: re-deriving context and silently dropping work.
SCOPE: In:

* `docs/agents/handoff-protocol.md` and the machine-readable `packages/agents/src/handoff.ts` (Zod schema for the handoff block).
* Artifact contract: a handoff consists of (1) code on a pushed branch, (2) a `HANDOFF.md` at the worktree root describing state, decisions, open questions, and next steps, (3) the Linear comment with the `paperos-session` footer extended by a `handoff` object: `{to: character, reason, artifacts: [{type: branch|pr|doc|spec|screenshot, ref}], nextSteps: [...], openQuestions: [...], contextFiles: [...]}`.
* Handoff kinds: `build-to-review` (builder to Sentinel: PR link, what to look at, known gaps), `review-to-build` (Sentinel to builder: findings with severity, must-fix list), `spec-to-build` (Quill to a builder: validated spec path, decisions made), `research-to-decision` (Scout to Atlas or Justin: ADR draft, recommendation), `escalate` (any character to 
SPEC(first 1200): * `HANDOFF.md` template with sections: Status (one line), What changed, Decisions made (link ADRs), Verified (tests, screenshots), Not done, Next steps (ordered), Open questions (each with a proposed default), Context files (paths worth reading first).
* Footer `handoff` object validated by the `linear-update` skill before posting; invalid handoffs are refused so nothing half-formed lands.
* `split` handoffs must include proposed issue titles, sizes and dependencies in the contract format so the Decomposer can create them without re-reading the code.
* The protocol doc includes three worked examples (build-to-review, review-to-build with a blocking finding, escalate).
* Add a `pnpm handoff lint` command that checks a worktree's `HANDOFF.md` and the last comment before a session ends; the playbook's end checklist calls it.
DOD:
* Schema tests: valid and invalid handoff fixtures for each kind.
* `pnpm handoff lint` catches a missing section, an unpushed branch and an unanswered open question without a default.
* Dry run: Nova builds a toy component, hands to Sentinel, Sentinel returns findings, Nova fixes and re-hands; all four comments parse and the orchestrator switches assignee automatically (recording attached).
* One escalation dry run lands in `Needs Justin` as a decision card and is approved with a single `approve` comment.
* Doc reviewed by Atlas and Sentinel; changelog entry; Linear comment with recording.
EDGE:
* Receiver character is over budget or paused (`agents/cost-controls`): handoff queues; Atlas is notified if it waits over 4 hours.
* Handoff to a character that cannot access the required tool (Beacon handing Stripe work to Iris): validator cross-checks `access` and refuses with the right target suggested.
* Session dies before posting the handoff: orchestrator synthesises a `handoff.kind: "crashed"` from the last footer and `git status`, routed to the same character for a retry.
* Two open questions with no defaults: linter blocks; a handoff must be actionable without a reply.
* Reviewer and builder disagree twice on the same finding: third round auto-escalates with both positions.
* Handoff references a screenshot artifact that expired in CI: artifacts referenced must be uploaded to Linear or MinIO, not left in CI.
DEPS: * `agents/roster-v1` (characters and labels).
* Uses `pm-linear/session-playbook` footer, `pm-linear/justin-queue` decision card, `agents/skills-library` (`linear-update` validation).


## PAP-109 [P1 Build M prio2 Backlog] Give characters persistent memory (project notes, decisions, gotchas) stored in the docs system and loaded at session start
key=agents/memory milestone=Sub-agents, skills and evals live agent=Built by Quill (Prompt Logger sub-agent) with Atlas wiring t
blockedBy=['PAP-128', 'PAP-104'] blocks=[]
GOAL: Stop characters from repeating mistakes: each character (and each project) keeps a curated memory of notes, decisions and gotchas in the docs system, loaded into the session prompt at start and appended to at session end, with size limits and review so it stays useful rather than becoming a landfill of transcripts.
SCOPE: In:

* Memory files as MDX in the docs engine: `docs/memory/characters/<name>.md` (one per character, lead and sub), `docs/memory/projects/<project-key>.md` (one per Linear project), and `docs/memory/global.md` (org-wide gotchas), each with frontmatter (`owner`, `maxTokens`, `updated`).
* Structure inside each file: `## Working notes` (rolling, pruned), `## Decisions` (links to ADRs from `collab/decision-log`, one line each), `## Gotchas` (repo, tool and API traps with the fix), `## Do not` (explicit prohibitions learned the hard way), `## Open threads`.
* Loader `packages/agents/src/memory/load.ts`: given character and issue (project key from Linear), assembles global, project and character memory in that order, trims to the character's `memory.maxTokens` (default 6000; measured with the token-count endpoint or a cached estimate) by dropping oldest working notes first, and returns markd
SPEC(first 1200): * Entry format is one bullet per item, max 300 characters, with a trailing `(PAP-123, 2026-09-21)` provenance; the loader strips provenance when trimming to save tokens but keeps it in the file.
* Token budget split default: global 1000, project 2000, character 3000; configurable per character in the schema (`memory.maxTokens`).
* Loader output is deterministic for a given file state so prompt caching (`pm-linear/orchestrator`) benefits: memory goes after the stable system prompt and before the issue body.
* Frontmatter `pinned: true` entries are never trimmed.
* All writes attributed to the character principal in git author (`Forge (agent) <forge@paperos.bot>`).
DOD:
* Loader tests: trimming order, pinned preservation, missing files, token estimate within 10 percent of `count_tokens` on 5 samples.
* Writer tests: apply add/remove blocks, reject entries over 300 characters or without provenance, auto-merge threshold.
* Live run: two consecutive sessions of Forge on related issues; the second session's transcript shows it used a gotcha recorded by the first (transcript excerpt in the comment).
* Memory pages render in the docs engine with a "last updated by" line; screenshot at 375 and 1280 px.
* `docs/agents/memory.md` explains structure, budgets, pruning; changelog entry; Linear comment with the excerpt and screenshots.
EDGE:
* Two sessions update the same memory file concurrently: memory branches rebase; on conflict the later one appends rather than fails (entries are order-independent bullets).
* A session proposes a memory entry containing a secret: the redaction from `agents/prompt-logging-hook` runs on the block; redacted entries are dropped with a note.
* Gotcha becomes wrong after a refactor: pruning job flags entries whose referenced paths no longer exist; Quill confirms removal.
* Character has no memory file yet: loader creates an empty template on first write; no failure on read.
* Memory grows past budget with only pinned entries: loader warns in `/status`; Quill must curate.
* Project key changes (project renamed): memory keyed by Linear project id in frontmatter, filename is a slug.
DEPS: * `agents/roster-v1` (character list and `memory` schema field).
* `collab/docs-engine` (MDX storage, rendering, versioning); `collab/decision-log` for decision links; `data-layer/search` optional.


## PAP-110 [P1 Review L prio1 Backlog] Create an eval harness with golden tasks per character, scored nightly, regressions flagged in Linear
key=agents/eval-harness milestone=Sub-agents, skills and evals live agent=Built by Sentinel (lead, this is its core responsibility) wi
blockedBy=['PAP-105', 'PAP-104'] blocks=[]
GOAL: Measure the agents themselves: a harness runs golden tasks for every character nightly, scores the outputs against rubrics and deterministic checks, tracks the trend, and opens or updates a Linear issue when a character regresses. Prompt, skill and model changes can then be judged by numbers instead of vibes.
SCOPE: In:

* Repo location `packages/agents/evals/` with `tasks/<character>/<task-id>/` folders containing `task.yaml` (prompt, fixtures path, allowed tools, max turns, budget), `expected/` (files, JSON or rubric), and `grade.ts` (deterministic checks) or `rubric.md` (LLM-judged).
* Golden tasks, at least 3 per lead and 1 per sub (about 55 total): Atlas decomposes a mini brief into contract-valid issues; Forge adds a Drizzle table with migration and RLS; Iris builds a component with stories that pass axe; Quill writes a page spec that validates; Sentinel reviews a seeded PR containing 5 planted bugs (recall and precision); Nova adds a column type to the grid; Ledger posts a balanced journal entry; Beacon drafts a campaign from a changelog for approval; Scout scores a library against the rubric; subs get one focused task each.
* Runner `pnpm evals run [--character] [--task] [--model]` launching
SPEC(first 1200): * Tasks are frozen: changing a task bumps its `version` and resets the trend; the harness never edits expected outputs automatically.
* Judge prompt receives the rubric, the transcript (tool calls summarised), and the diff; judge output is a strict JSON schema (`output_config.format`) to avoid parsing failures.
* Seeded bugs for the Sentinel task live in a fixture repo tarball with an answer key; score is F1 over findings matched by file and line range.
* Cheap mode `--model claude-sonnet-5 --effort low` for smoke checks on skill PRs (cost under $5).
* All runs are logged to the prompt-log store with `issueKey: EVAL`.
DOD:
* 55 tasks committed with graders; `pnpm evals list` shows them.
* Full nightly run completes under 3 hours and under the budget cap; results table screenshot at 1280 px.
* Regression detection tested by deliberately breaking Iris's prompt on a branch and observing an eval regression issue created in Linear (screenshot).
* Judge agreement: 20 judged outputs spot-checked by Sentinel with agreement above 80 percent, recorded in the comment.
* Report page renders; changelog entry; Linear comment with the first baseline table.
EDGE:
* Flaky task (network-dependent fixture): mark `flaky: true`, run 3 times, take median; flaky tasks cannot trigger regressions alone.
* Model outage or refusal mid-run: run marked `incomplete`, no regression issue, retried next night.
* Task passes deterministic checks but the judge scores low: report both; regression uses the combined score but flags the disagreement.
* Budget cap hit halfway: remaining tasks marked `skipped-budget`, trend unaffected.
* Two regressions for the same character in one night: one issue with a table, not two.
* Fixture repo drifts from the template (new lint rule): fixtures pinned to a template SHA; a weekly job bumps and re-baselines.
DEPS: * `agents/roster-v1` (characters, bundles) and `agents/skills-library` (skills exercised by tasks).
* Uses `agents/tool-scopes` bundles, `agents/cost-controls` caps, `pm-linear/credit-metering` for cost, Linear for regression issues.


## PAP-111 [P1 Build M prio2 Backlog] Add per-character budgets, max-turn limits and a kill switch
key=agents/cost-controls milestone=Sub-agents, skills and evals live agent=Built by Atlas (Dispatcher sub-agent); reviewed by Sentinel 
blockedBy=['PAP-98'] blocks=[]
GOAL: Bound spend at every level so no runaway session or over-eager character can burn the budget: per-session and per-day caps per character, max-turn limits, per-issue caps derived from size, and a kill switch that stops one session, one character or everything within seconds and leaves a clean record.
SCOPE: In:

* Limits from the character schema `budget` (`perSessionUsd`, `perDayUsd`, `maxTurns`) plus orchestrator config `limits` (`perIssueUsd` by estimate S 60 / M 180 / L 450, `globalPerDayUsd`, `reserveUsd` kept untouchable for release week).
* Pre-flight check in `pm-linear/orchestrator` before spawning: character daily remaining, issue remaining (across attempts), global remaining; if any is below the expected session cost (median of the character's last 10 sessions, default $25), do not spawn; comment on the issue with the reason and label `budget-hold`.
* In-flight enforcement: the SDK stream is metered live (`pm-linear/credit-metering` running total); at 80 percent of the session cap the orchestrator injects a warning via the next user turn asking the session to wrap up and post its handoff; at 100 percent it aborts the query, commits `wip:`, pushes, posts the footer with `status: "
SPEC(first 1200): * Module `src/limits/` in the orchestrator: `preflight.ts`, `inflight.ts`, `kill.ts`, `reset.ts`; state in `orchestrator.budgets` and `orchestrator.kill_state`.
* Abort uses the SDK query's abort controller; a grace period of 20 seconds lets the current tool call finish unless scope is `all` with `hard: true`.
* All limit decisions are logged as events with the numbers used, for the eval harness and post-mortems.
* Reviewers (Sentinel subs) have separate daily pools so a builder spending spree cannot starve review, matching the 30 percent review share.
* Character caps default from `roster.yaml`; per-issue override via label `budget:<usd>` (max 2x default without approval).
DOD:
* Unit tests for pre-flight decisions, 80/100 percent thresholds, reset, and cap arithmetic with fake clocks and fake meters.
* Integration: a session on a toy issue with `perSessionUsd: 2` is warned and then aborted; `wip:` commit pushed; footer posted (recording).
* Kill switch: `KILL ALL` comment from Justin stops 3 running sessions within 5 seconds; `/status` shows paused; resume works (recording).
* Alerts observed at thresholds in a simulated day.
* Runbook `docs/pm/cost-controls.md` including "what to do if the budget is gone"; changelog entry; Linear comment with recordings.
EDGE:
* Metering lag means the cap is discovered late: compare with the SDK `result` cost afterwards and charge the overrun to the next session's allowance.
* Kill during a git push: let the push finish (grace), never leave a half-written worktree without a `wip:` commit.
* Justin's `KILL` comment arrives while Linear webhooks are down: the poll loop also scans the burn-report issue comments every 30 seconds.
* Character has no sessions yet (no median): use the default expected cost.
* Reserve breached in the final days: only Justin can release it through `Needs Justin`.
* Clock at daily reset while sessions are running: sessions keep their original day's allowance; new spend counts to the new day.
* Sub-agent spawns inside a session inherit the parent's session cap; the SDK cost includes them.
DEPS: * `pm-linear/credit-metering` (live totals, price table, budgets table).
* Integrates with `pm-linear/orchestrator` launch path and `agents/character-schema` budget fields.


## PAP-112 [P1 Docs M prio2 Backlog] Publish the character handbook: who does what, how to summon them, what they may not do
key=agents/character-docs milestone=Sub-agents, skills and evals live agent=Built by Quill (lead); reviewed by Sentinel (accuracy) and A
blockedBy=['PAP-104'] blocks=[]
GOAL: Publish the handbook a human opens to understand the agent org: who each character is, what it owns, how to summon it from Linear or the CLI, what it may never do, and how to change it. Written for Justin first and future staff second, generated where possible from the roster so it never drifts from reality.
SCOPE: In:

* `docs/agents/handbook/` in the docs engine: `index.md` (org chart as mermaid, the one-paragraph story of how work flows), one page per lead `atlas.md`...`scout.md` with sub-character sections, `summoning.md`, `limits.md`, `changing-the-org.md`, `glossary.md`.
* Per-character page content: role and remit, reports to, sub-characters with triggers, tools and MCP servers (generated table), access scopes (generated), skills, budgets, escalation rules, example tasks it excels at, tasks to route elsewhere, three real example issues it completed (linked), and its memory file link.
* Summoning: assign the Character label in Linear and move to `Ready for Claude`; `pnpm agents run <name> --issue PAP-123` for local; `@character` mention convention in Linear comments picked up by the orchestrator to request a specific character's opinion as a comment (implemented here as a small handler using 
SPEC(first 1200): * Reading level: plain language, no internal jargon without a glossary entry; each page under 1200 words; the index under 600.
* Every "may not" statement links to the enforcing mechanism (deny list, hook, branch protection) so claims are verifiable.
* Pages carry frontmatter `generatedFrom` and `lastVerified`; CI fails if `roster.json` changed and docs were not regenerated.
* The `@character` handler: on a Comment `create` webhook containing `@atlas`...`@scout` from a human, spawn a short read-only session (plan mode, `maxTurns` 8, Sonnet 5 unless the question is architectural) that replies in a comment with the footer; cost capped at $3 per mention.
* Screenshots of two handbook pages on phone width are required because Justin reads on mobile.
DOD:
* All pages present and rendering in the docs engine (or the repo, if the engine is not yet live) with generated tables matching `roster.json`.
* `pnpm agents docs --check` in CI.
* `@sentinel` mention on a test issue produces a relevant reply comment within 2 minutes (screenshot).
* Read-through by Sentinel for accuracy against the privilege matrix and by Quill for clarity; every "may not" has a link.
* Screenshots at 375 and 1280 px; changelog entry; Linear comment with links and screenshots.
EDGE:
* Character retired: page moves to `handbook/retired/` with the retirement ADR; mentions of it reply with a redirect.
* Mention by an agent (not human): ignored to prevent loops.
* Mention asks for an action, not an opinion: the reply explains that actions come from issues and offers to draft one (creates a Backlog issue in contract format on `yes`).
* Roster and prose disagree (prose claims a tool the YAML denies): CI lint flags tool names in prose that are not in the generated table.
* Docs engine down: pages still readable on the forge as markdown; links are relative.
* Very long generated access tables (Atlas): collapse into a details block.
DEPS: * `agents/roster-v1` (roster.json, prompts) and, through it, `agents/tool-scopes` for the privilege matrix.
* Uses `collab/docs-engine` when available and `pm-linear/webhooks` for the mention handler.


## PAP-113 [P2 Build M prio2 Backlog] Build the agent org chart UI showing characters, sub-agents, current tasks, tools and access
key=agents/org-chart-ui milestone=Agent org visible in app agent=Built by Nova (Canvas Cartographer sub-agent) with Iris (Com
blockedBy=['PAP-132', 'PAP-104'] blocks=[]
GOAL: Make the agent org a first-class page in the product: an interactive org chart of characters and sub-characters showing who reports to whom, what each is doing right now, what tools and access it holds, and how much it has spent, drawn on the canvas engine so it can be rearranged, annotated and commented on like any other PaperOS canvas.
SCOPE: In:

* Route `/agents` with page spec `specs/agents/org-chart.spec.yaml` (staff and agent audiences; read-only for agents) and `specs/agents/character.spec.yaml` for the detail drawer.
* Canvas built on `collab/canvas-view`: nodes for Justin, nine leads and 28 subs from `roster.json` (fetched via oRPC `agents.roster`), tree layout (dagre or ELK auto-layout with manual nudges persisted per user), edges for `reportsTo`, badge overlays for state: idle, working (with issue key), reviewing, paused, over budget, killed.
* Live data: `agents.status` oRPC procedure proxying the orchestrator `/status` (active sessions, current issue, elapsed time) and `pm-linear/credit-metering` (`spentTodayUsd`, `dailyCapUsd`), polled every 10 seconds or pushed over the realtime layer when `realtime/agent-presence` lands.
* Detail drawer on click: role, prompt excerpt, tools and MCP servers, access scopes (from 
SPEC(first 1200): * Node component in `packages/ui` (`CharacterNode`: name, role line, state badge, budget ring) with stories for every state; distinct visual identity for agents (dashed border, bot glyph) consistent with `realtime/agent-presence`.
* Layout persisted in a `canvas_layout` record per user; "reset layout" action.
* Data contracts: `agents.roster` returns the schema type from `agents/character-schema`; `agents.status` returns `{character, state, issueKey?, sessionId?, startedAt?, spentTodayUsd, dailyCapUsd, lastHeartbeat}`.
* Responsive: under 768 px the canvas becomes a collapsible tree list with the same badges; the drawer becomes a full-screen sheet.
* Accessibility: nodes are focusable in tree order, arrow keys move between siblings and levels (`input/focus-management`), state announced via `aria-label`.
DOD:
* Page spec validates; conformance tests pass.
* Storybook stories for `CharacterNode` in all six states, light and dark; axe passes.
* Playwright screenshots at 320, 375, 768, 1024, 1280, 1920 and 2560 px in both themes attached.
* Live demo on staging: start a session via Linear and watch the node switch to working within 10 seconds; pause from the drawer stops it (recording).
* Keyboard navigation and screen-reader labels verified.
* GitHub Pages demo with mocked status; changelog entry; Linear comment with demo, screenshots and recording.
EDGE:
* Orchestrator unreachable: nodes show "status unknown" with the last-known time, no spinner forever.
* 100+ sub-characters in future: collapse subs under a lead by default when more than 6.
* Character present in status but missing from roster (stale build): render as an orphan node with a warning.
* Two sessions for one character concurrently (perCharacter 3): badge shows count; drawer lists all.
* Budget cap zero (paused character): ring shows paused, not 0/0 error.
* User without permission clicks pause: button disabled with tooltip; permission from the page spec access section.
* Canvas library not chosen yet (`collab/collab-research` pending): the tree list mode ships first and the canvas mode follows.
DEPS: * `agents/roster-v1` (roster.json, states).
* `collab/canvas-view` (canvas engine) and through it `spec-builder/schema`; also `pm-linear/credit-metering` and `agents/cost-controls` endpoints, `realtime/agent-presence` optional.
