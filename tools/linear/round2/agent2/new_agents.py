"""New issues for agents: 2 gap issues and 7 children (PAP-104, PAP-110)."""
P = "agents"
GAPS = []
CHILDREN = {}

GAPS.append({
"key": "agents/runtime-sandbox",
"title": "Build the agent runtime sandbox: per-session container, worktree mount, CPU/RAM/time limits and network isolation with the credential broker's egress proxy as the only route",
"phase": "P0", "type": "Infra", "priority": 1, "surfaces": ["Agent", "Developer"],
"milestone": "Roster defined and installed", "state": "Backlog",
"blockedBy": ["PAP-25", "security/credential-broker", "security/agent-deny-list"], "blocks": [],
"description": """**Goal**

Give every Claude session a wall it cannot talk its way through: each session runs in a per-session container that mounts only its worktree, has bounded CPU, memory, pids and wall clock, and has no network route except the egress proxy owned by {{security/credential-broker}}. This issue owns the container, the worktree mount and the resource limits. The proxy, the per-character allowlist and credential injection belong to {{security/credential-broker}}; the hook policy the image ships belongs to {{security/agent-deny-list}}. PAP-106 admits its hook is best-effort; this is the isolation it defers to. Split on 2026-09-17 (FIX-6) from a trio that each defined the egress allowlist and the no-secrets rule.

**Scope**

* In: `ops/sandbox/` image and runner (`Dockerfile.session`, `run-session.sh`), `runInSandbox()` in the orchestrator launcher (`launchSession` gains `sandbox: true`), the internal Docker network with the broker proxy as its only route, resource limits by Size, worktree bind mount, orphan sweep, escape probes for filesystem, network route and limits, `docs/agents/sandbox.md`.
* Out: egress proxy container, allowlist generation and credential injection ({{security/credential-broker}}); deny rules and the PreToolUse hook ({{security/agent-deny-list}}, PAP-106); forge branch protection (PAP-46); VPS provisioning (PAP-25).

**Spec**

* Runtime: rootless Docker (or Podman) on the VPS; image Node 22, git, pnpm, gh, Playwright deps, the PAP-106 hooks and the compiled `agent-deny.json` from {{security/agent-deny-list}} (the launcher refuses to start a container whose policy digest is stale); read-only root filesystem except `/work` (the worktree bind mount), `/tmp` and the pnpm store cache; `--cap-drop ALL`, `--security-opt no-new-privileges`, seccomp default profile, `--pids-limit 512`, CPU 2, RAM 4 GB, session wall clock 3 h (configurable per Size).
* Network: containers attach to the internal `sandbox` network that has no default route; the only reachable host is the broker egress proxy (`PAPEROS_PROXY=http://egress:3128`, {{security/credential-broker}}); the sandbox proves the route property (a direct `curl https://example.com` fails at the network layer, not at the proxy). Which hosts the proxy allows per character and which credentials it injects is the broker's concern.
* Environment: the container receives only `broker:*` placeholders and non-secret configuration; the orchestrator's own keys, Postgres superuser, Coolify and sops keys never enter; a probe script asserts on every start that `env` contains no value matching `ghp_|lin_api_|sk-ant-|sk_test_|sk_live_`.
* Worktree: bind-mounted from `/srv/worktrees/<key>`; git pushes go through the proxy, which injects the character's forge token (PAP-48 or default bot, minted by the broker).
* Cleanup: container removed on session end; orphan sweep every 10 minutes; `SandboxHandle.kill` is what PAP-111 `kill` calls.

**Interface contract**

* Provides: `runInSandbox(spec: { worktree, character, env, limits }): SandboxHandle` with `exec`, `kill`, `stats`; image tag `paperos/session:<sha>`; network `sandbox`; events `sandbox.started`, `sandbox.killed`, `sandbox.limit_hit`.
* Consumers: {{pm-linear/orchestrator/sessions}} (`launchSession` wraps `query()` execution in the container), PAP-106 (hooks run inside), PAP-110 runner (`sandbox: true`), PAP-111 (`kill`), {{agents/session-observability}} (`stats`).
* Requires: PAP-25 VPS with Docker; {{security/credential-broker}} proxy image, network name and placeholder contract; {{security/agent-deny-list}} compiled policy; PAP-104 roster (character to Size and limits).

**Definition of done**

* Probe suite inside a running sandbox: cannot read `/srv/repos` of other issues, cannot reach `postgres:5432`, `coolify` or any host except the proxy, can reach Linear and the forge through the proxy; results table attached.
* No production credential present: `env` dump diffed against the placeholder set in CI.
* Limits enforced: a fork bomb and a 6 GB allocation are killed; timing recorded; a stale policy digest refuses to start (test).
* Orchestrator launches a real session in the sandbox and opens a PR (recording).
* Docs; changelog; Linear comment with table and recording.

**Test plan**

* Unit: limit computation by Size; policy digest check; network spec generation.
* Integration: `ops/sandbox/test/probes.sh` run in CI on a self-hosted runner (PAP-50) against a stub proxy; env-diff assertion.
* e2e: staging session through the sandbox and the real broker proxy.
* No UI.

**Demo**

Run `pnpm sandbox probe --character beacon`: watch a direct `curl https://example.com` fail with no route, a `curl` through the proxy to `api.linear.app` succeed, and `env | grep -c -E 'ghp_|lin_api_|sk-ant-'` print 0. One minute.

**Edge cases**

* Playwright needs Chromium: included in the image; `--shm-size 1g`.
* Session needs a host not on the allowlist: the proxy denies and logs `egress-denied`; the fix is the character's `access[]` in the broker rules, never a sandbox change.
* Docker daemon restart: orphan sweep reattaches or kills; claims released by the orchestrator.
* Disk pressure from images: nightly prune keeps two tags.
* Rootless Docker unavailable: fall back to a dedicated `sandbox` user with cgroups v2 limits and nftables rules that allow only the proxy; documented as degraded; the broker's degraded mode (short-lived tokens in env) applies.
* Broker not yet merged when this starts: build against a stub proxy that allows everything and injects nothing (branch-start rule); the DoD probe that needs real injection waits for the broker.

**Dependencies**

Blocked by PAP-25, {{security/credential-broker}} (proxy, allowlist, injection) and {{security/agent-deny-list}} (hook policy shipped in the image). Blocks nothing hard: PAP-106 runs its hooks inside the sandbox once it exists (soft), PAP-96 and {{pm-linear/orchestrator/sessions}} enable `sandbox: true` when it merges (soft). Soft: PAP-48, PAP-50, PAP-104.

**Agent**

Built by Forge (Ops Runner sub-agent); reviewed by Sentinel (Security Auditor).

**Size**

M (proxy and allowlist moved to the broker)""",
})
# FIX-6 (2026-09-17): rewritten; egress proxy, allowlist and secret injection moved to security/credential-broker, hook policy to security/agent-deny-list.

GAPS.append({
"key": "agents/session-observability",
"title": "Add agent session observability: heartbeats, stuck-session detection, per-session OTel spans and a `/status` contract shared by the org chart, board cards and cost controls",
"phase": "P1", "type": "Build", "priority": 2, "surfaces": ["Agent", "Staff"],
"milestone": "Sub-agents, skills and evals live", "state": "Backlog",
"blockedBy": ["PAP-96", "PAP-40"], "blocks": ["PAP-113", "PAP-102"],
"description": """**Goal**

Define and implement the one status contract everyone assumes: a `SessionStatus` shape, a heartbeat every 60 seconds, `stuck` after 15 minutes without progress, per-session OpenTelemetry spans tagged with issue and character, and the `/status` payload that the org chart, board cards, cost controls and the weekly audit all read.

**Scope**

* In: `packages/agents/src/status.ts` (Zod `SessionStatus`), heartbeat writer in the orchestrator stream handler, stuck detector, OTel instrumentation of `launchSession` and tool calls, `/status.sessions`, alert events, `docs/agents/observability.md`.
* Out: the org chart rendering (PAP-113), the collector and dashboards (PAP-40), budget arithmetic (PAP-111).

**Spec**

* `SessionStatus = { sessionId, issue, character, model, state: "starting" | "working" | "waiting-tool" | "reviewing" | "paused" | "stuck" | "ending" | "ended" | "killed", startedAt, lastHeartbeat, lastProgressAt, turns, costUsd, worktree, branch, pr?, sandbox?: { cpuPct, memMb }, reason? }`.
* Heartbeat: the stream handler updates `lastHeartbeat` on every SDK message and `lastProgressAt` on assistant text or tool result; a 60 s ticker persists to `sessions.status_json` even when idle; hook-based sessions send `PAPEROS_HEARTBEAT` via PAP-107 `tool.post` events.
* Stuck: `now - lastProgressAt > 15 min` while `state = working` flips to `stuck`, emits `session.stuck`, posts one comment, and after 30 minutes PAP-111 may abort with `reason: stuck`.
* OTel: span `agent.session` with attributes `paperos.issue`, `paperos.character`, `paperos.model`; child spans per tool call (`agent.tool`, name, duration, denied flag) exported to the PAP-40 collector; trace id stored in `SessionStatus` for deep links.
* `/status.sessions: SessionStatus[]` plus `summary { working, stuck, paused }`.

**Interface contract**

* Provides: `SessionStatusSchema`, type `SessionStatus`, `statusOf(sessionId)`, `allStatus()`, events `session.heartbeat`, `session.stuck`, `session.recovered`, OTel attribute names under `paperos.*`, `/status.sessions`.
* Consumers: PAP-113 badges, PAP-102 character badge (15 minute staleness), PAP-111 (`stuck` abort), {{pm-linear/weekly-reaudit}} (`STALE_SESSION`), PAP-98 (turns and cost cross-check), PAP-146 pushes the same shape over realtime later.
* Requires: PAP-96 stream handler and `/status` route, PAP-40 collector endpoint, PAP-107 event format for hook sessions, {{agents/runtime-sandbox}} `stats` (soft).

**Definition of done**

* Schema and ticker implemented; `/status.sessions` validates against the schema in a test.
* Stuck detection proven with a session stalled by a mocked never-resolving tool; comment posted once; recovery flips back.
* Spans visible in the PAP-40 dashboard for a real session (screenshot at 1280 px).
* Docs; changelog; Linear comment with screenshot.

**Test plan**

* Unit: state machine transitions with fake clock; heartbeat persistence cadence; schema snapshot.
* Integration: mocked SDK stream producing heartbeats and a stall; OTel exporter captured in-memory and asserted for attributes.
* e2e: staging session traced end to end.
* Visual: dashboard screenshot only.

**Demo**

Start a rehearsal session, poll `/status.sessions` and watch `lastHeartbeat` advance every minute; freeze the mocked tool and after 15 minutes (fake clock in dev) see `stuck` and the Linear comment. Two minutes.

**Edge cases**

* Long legitimate tool call (Playwright run 20 min): tool spans count as progress; `waiting-tool` state suppresses `stuck` until 45 min.
* Orchestrator restart: statuses reloaded from `status_json`; `interrupted` sessions appear as `ended` with reason.
* Clock skew between hosts: heartbeats use orchestrator time only.
* Collector down: spans buffered and dropped after 5 minutes; status unaffected.
* Hundreds of ended sessions: `/status.sessions` returns active plus last 24 h; older via `?since`.

**Dependencies**

Blocked by PAP-96, PAP-40. Blocks PAP-113, PAP-102. Soft: PAP-107, {{agents/runtime-sandbox}}.

**Agent**

Built by Forge (Ops Runner) with Atlas (Dispatcher) on the state machine; reviewed by Sentinel.

**Size**

M
"""})

CHILDREN["PAP-104"] = [
{
"key": "agents/roster-v1/yaml", "title": "Roster: convert the plan.json roster to 37 validated character YAML files", "type": "Build", "size": "S",
"blockedBy": [], "blocks": ["agents/roster-v1/lead-prompts", "agents/roster-v1/sub-prompts", "agents/roster-v1/build"],
"description": """**Goal**

Produce the structured half of the roster: one validated YAML per character (nine leads, 28 subs) generated from plan.json `agents[]` and completed with model, effort, permission mode, budgets, skills, memory paths and escalation rules, plus `roster.yaml` defaults, so prompt writers and the build tool start from files that already pass `pnpm agents validate`.

**Scope**

* In: `scripts/plan-to-roster.ts` (one-time converter, kept for re-runs), `packages/agents/characters/<name>.yaml` for all 37, `packages/agents/roster.yaml` (defaults, budget shares, `fallbackModel`), `pnpm agents tree`.
* Out: prompt prose (sibling children), `.claude/agents` generation ({{agents/roster-v1/build}}), bundles (PAP-106).

**Spec**

* Names: kebab ids (`atlas`, `page-spec-writer`), `displayName` from the plan; `kind`, `reportsTo`, `parent`, `role`, `description` (one sentence with trigger phrases, refined by the sub-prompts child), `linearLabel: Character/<Lead>` for leads only.
* Defaults in `roster.yaml`: leads `claude-fable-5-1`, `xhigh`, `acceptEdits`; read-mostly subs Sonnet at `medium`; Sentinel subs `high`, `plan`, deny Write and Edit; `fallbackModel` chosen from the PAP-98 price table ids (no model named in prompts).
* Budgets: daily allowance split by area share (Sentinel tree 30 percent, Atlas 8, builders share the rest, research 5); `perSessionUsd` by role (lead 40, sub 15), `maxTurns` 200 lead, 80 sub.
* `access[]` normalised to the PAP-103 scope registry; `mcpServers[]` from PAP-210 stub names; `skills[]` from PAP-105 ids; `memory.path` per character; escalation rules shared plus Atlas's cycle rule.
* `pnpm agents tree` prints the org tree and diffs against plan.json structure.

**Interface contract**

* Provides: the 37 YAML files, `roster.yaml`, `pnpm agents tree [--check]`, `plan-to-roster.ts`.
* Consumers: {{agents/roster-v1/lead-prompts}} and {{agents/roster-v1/sub-prompts}} (fields to describe), {{agents/roster-v1/build}} (input), PAP-106, PAP-111 budgets, PAP-113 roster.
* Requires: PAP-103 schema and validator; plan.json.

**Definition of done**

* `pnpm agents validate` passes all 37; `pnpm agents tree --check` matches plan.json.
* Every `access` string resolves in the registry; every skill id exists in `skills.json` or is marked `planned`.
* Budget shares sum to 100 percent (test).
* Changelog; Linear comment with the tree output.

**Test plan**

* Unit: converter output snapshot; budget sum; label uniqueness; inheritance resolution for subs.
* Integration: validator run over the directory in CI.
* No UI.

**Demo**

Run `pnpm agents tree` and read the nine leads with their subs indented; open `characters/sentinel.yaml` and point at `permissionMode: plan` and the deny list. Under one minute.

**Edge cases**

* Plan sub name with spaces and punctuation ("Motion and Input Stylist"): id `motion-and-input-stylist`, display name intact.
* Two subs with the same role text across leads: allowed; descriptions differ.
* Missing access for a sub: inherits the lead's subset, never more.
* `fallbackModel` not in price table: validator warning blocks merge here.
* Plan changes later: re-run converter with `--merge` preserving hand edits.

**Dependencies**

Blocked by PAP-103 (through the parent). Blocks the three sibling children.

**Agent**

Built by Atlas (Decomposer sub-agent); reviewed by Sentinel.

**Size**

S
"""},
{
"key": "agents/roster-v1/lead-prompts", "title": "Roster: write the nine lead system prompts with shared fragments", "type": "Build", "size": "M",
"blockedBy": ["agents/roster-v1/yaml"], "blocks": ["agents/roster-v1/build"],
"description": """**Goal**

Write the nine lead prompts (Atlas, Forge, Iris, Quill, Sentinel, Nova, Ledger, Beacon, Scout): 300-800 words each including shared fragments, structured the same way, stating goals and constraints rather than step lists, so each lead behaves in role, reports through the playbook footer, escalates correctly and delegates to its subs.

**Scope**

* In: `packages/agents/prompts/<lead>.md` (nine), `prompts/_shared/{playbook,footer,code-standards,review-gates,escalation}.md`, a prompt lint, `docs/agents/prompt-style.md`.
* Out: sub prompts ({{agents/roster-v1/sub-prompts}}), YAML fields ({{agents/roster-v1/yaml}}), build and smoke ({{agents/roster-v1/build}}).

**Spec**

* Structure per prompt: Identity and remit; What good looks like (three measurable statements); Hard limits (each linked to an enforcing mechanism from PAP-106 or PAP-46); How you report (`{{include _shared/footer}}`); When you escalate (`{{include _shared/escalation}}` plus role-specific triggers); Your sub-characters and when to delegate (one line each); Tools you prefer; Context you read first (PAP-92 order, memory from PAP-109).
* Style rules from `prompt-style.md`: second person, present tense, no model names, no "always" or "never" without a mechanism, no numbered procedures longer than five steps, explicit permission to ask for progress notes on long tasks, calibrated language about uncertainty.
* Sentinel: severity taxonomy by reference to PAP-79, forbidden from merging and from approving its own PRs; Atlas: budget and dependency guardianship, `Needs Justin` admission rules from PAP-94; Ledger: double-entry invariants, Stripe test mode only; Beacon: sandbox email until approved; Scout: rubric and license policy references.
* Includes resolved at build time; word budget counts included text.

**Interface contract**

* Provides: nine prompt files and five fragments, `pnpm agents lint-prompts` (word count, forbidden phrases, include resolution, mechanism links present), `prompt-style.md` used by the sub-prompts child and PAP-118.
* Consumers: {{agents/roster-v1/build}} renders them into `.claude/agents`; PAP-110 smoke fixtures; PAP-112 quotes remit paragraphs; PAP-126 adds a terminology fragment later.
* Requires: {{agents/roster-v1/yaml}} fields, PAP-92 footer text, PAP-79 taxonomy text (reference only), PAP-94 admission rules.

**Definition of done**

* Nine prompts pass lint; each 300-800 words with includes.
* Sentinel review finds no contradictory instructions (checklist attached); Quill review for clarity.
* Three sample tasks per lead answered in role in a `claude -p` dry run using the raw prompt (transcripts saved for the build child's smoke step).
* Changelog; Linear comment with transcripts.

**Test plan**

* Unit: lint rules on fixtures (over length, model name, missing include, dangling mechanism link).
* Integration: include resolution snapshot for one prompt.
* e2e: 27 dry-run transcripts saved; a reviewer rubric scores in-role behaviour.
* No UI.

**Demo**

Open `prompts/atlas.md`, then run `claude -p --system-prompt-file dist/prompts/atlas.md "Should we let Beacon push to main?"` and read a refusal that cites branch protection and offers a `Needs Justin` card. One minute.

**Edge cases**

* A lead's remit overlaps another's (Nova and Iris on components): each prompt names the boundary and who owns which package.
* Fragment change alters nine prompts: lint re-checks lengths; CI fails on overflow.
* Prompt asked to act outside a worktree: no `cwd` assumptions.
* Model refuses a task category: prompt says to record the refusal category in the footer, not to retry.
* Justin's name and role: referred to as the single human reviewer, never as a tool.

**Dependencies**

Blocked by {{agents/roster-v1/yaml}}. Blocks {{agents/roster-v1/build}}.

**Agent**

Built by Quill (lead) drafting with Atlas; reviewed by Sentinel.

**Size**

M
"""},
{
"key": "agents/roster-v1/sub-prompts", "title": "Roster: write the 28 sub-character prompts and delegation descriptions", "type": "Build", "size": "M",
"blockedBy": ["agents/roster-v1/yaml"], "blocks": ["agents/roster-v1/build"],
"description": """**Goal**

Write the 28 sub-character prompts and the one-sentence `description` fields that drive Claude Code's automatic delegation, sharp enough that a classification test routes twenty sample tasks to the intended sub every time (Code Reviewer versus Edge Case Hunter, Dispatcher versus Decomposer, Views Engineer versus Canvas Cartographer).

**Scope**

* In: `packages/agents/prompts/<sub>.md` (28, 150-500 words with includes), refined `description` fields written back into the YAML, `packages/agents/test/delegation.test.ts` with 20 labelled tasks, `prompts/_shared/sub-footer.md`.
* Out: lead prompts ({{agents/roster-v1/lead-prompts}}), build ({{agents/roster-v1/build}}).

**Spec**

* Structure: Who you are and who you report to; The one job (two sentences); Inputs you expect (artifact types from PAP-108 handoffs); Output contract (exact artifact: review JSON, migration files, stories, spec file); Limits (tools denied in YAML restated with the mechanism); When to hand back to your lead.
* `description` grammar: "Use when <trigger phrases>; not for <nearest sibling's job>." Under 200 characters.
* Reviewer subs (Sentinel's four): read-only wording, output the PAP-239 `Finding[]` block, severity from PAP-79, never approve or merge.
* Read-mostly subs on Sonnet: shorter prompts, explicit instruction to summarise rather than paraphrase transcripts (Prompt Logger), to preserve provenance (Changelog Scribe), to score with the rubric only (Library Evaluator).
* Classification test: 20 tasks with an expected sub; a cheap model call picks a sub from the 28 descriptions; pass threshold 20 of 20, allowed to fix descriptions until it passes.

**Interface contract**

* Provides: 28 prompt files, updated `description` fields, the delegation test and its task fixture (reused by PAP-110 as an Atlas golden task), `sub-footer.md`.
* Consumers: {{agents/roster-v1/build}}, PAP-110, PAP-112 sub sections, PAP-108 (artifact expectations align with handoff kinds).
* Requires: {{agents/roster-v1/yaml}}, `prompt-style.md` from the lead-prompts child (may start from its draft), PAP-108 kinds (draft acceptable).

**Definition of done**

* 28 prompts pass lint; descriptions under 200 characters.
* Delegation test 20 of 20 on two consecutive runs.
* Sentinel review of reviewer subs for read-only consistency; Quill review for clarity.
* Changelog; Linear comment with the classification table.

**Test plan**

* Unit: lint, description grammar regex, word counts.
* Integration: delegation test in CI (cheap mode, cost under $1).
* e2e: one dry run per Sentinel sub on a seeded PR fixture producing a valid `Finding[]` block.
* No UI.

**Demo**

Run `pnpm agents delegation-test` and watch twenty tasks route correctly; then feed "find the empty-state bug on the invoices page" and see `edge-case-hunter` chosen over `code-reviewer`. One minute.

**Edge cases**

* Two subs legitimately fit a task: the test fixture names a primary and an acceptable alternate.
* Sub prompt refers to a tool the YAML denies: lint fails via the PAP-112 prose rule reused here.
* Description too generic ("helps with code"): grammar regex rejects.
* Sub invoked directly by Justin: prompt says to report to the lead in the footer anyway.
* Plan adds a sub: template file plus a fixture task.

**Dependencies**

Blocked by {{agents/roster-v1/yaml}}. Blocks {{agents/roster-v1/build}}. Soft: PAP-108, PAP-239.

**Agent**

Built by Quill (Page Spec Writer) with Sentinel on reviewer subs; reviewed by Atlas.

**Size**

M
"""},
{
"key": "agents/roster-v1/build", "title": "Roster: build `.claude/agents` generation, CI drift check and smoke tasks per lead", "type": "Build", "size": "M",
"blockedBy": ["agents/roster-v1/yaml", "agents/roster-v1/lead-prompts", "agents/roster-v1/sub-prompts"], "blocks": [],
"description": """**Goal**

Make the roster executable: `pnpm agents build` deterministically renders `.claude/agents/<name>.md` with frontmatter and resolved prompts plus `dist/roster.json`, `--check` fails CI when outputs drift from the YAML and prompts, and three smoke tasks per lead prove each character answers in role, respects its deny list and produces the footer.

**Scope**

* In: `packages/agents/src/build.ts`, `.claude/agents/*.md` (37, committed), `dist/roster.json`, gate 1 job `agents-drift`, `packages/agents/smoke/<lead>/task-{1,2,3}.md` with `run-smoke.ts`, results table.
* Out: runtime bundles (PAP-106 extends `build`), evals (PAP-110 reuses smoke outputs as fixtures).

**Spec**

* Frontmatter per agent file: `name`, `description`, `tools` (allow list rendered as Claude Code expects), `model`; body is the prompt with includes resolved and a trailing generated banner with the source hash.
* `roster.json`: `RosterSchema` output with inheritance resolved, `linearLabel`, `budget`, `memory`, `skills`, `escalation`, `promptHash`.
* Determinism: sorted keys, LF endings, no timestamps; `build --check` rebuilds in memory and diffs; exit 1 on drift with file names.
* Smoke: `claude -p --agent <lead>` on three tasks (in-role question, a forbidden action such as pushing to `main` or approving own PR, a task requiring the footer) with `maxTurns 6`, Sonnet cheap mode allowed; outputs graded by regex checks (footer present, refusal phrase, no denied tool call) and saved as `smoke/results/<lead>/<task>.json` for PAP-110.
* Gate 1 wiring through PAP-78 job slot `agents-drift`.

**Interface contract**

* Provides: `pnpm agents build [--check]`, `.claude/agents/*.md`, `dist/roster.json`, `pnpm agents smoke [--lead]`, `smoke/results/**` fixture format `{ lead, task, footerOk, refusalOk, deniedCalls, transcriptRef }`.
* Consumers: PAP-96 (`roster.json`), PAP-106 (extends build with bundles), PAP-110 (fixtures), PAP-112 (`roster.json` tables), PAP-113 (`agents.roster`), PAP-78 (job).
* Requires: the three sibling children; PAP-78 job slot; PAP-92 footer schema for grading.

**Definition of done**

* 37 agent files and `roster.json` committed; two builds byte-identical; `--check` red on a deliberate YAML edit in a seeded PR.
* Smoke table for nine leads posted: 27 tasks, footer and refusal columns all green.
* `roster.json` consumed by an orchestrator dry run (parent DoD).
* Changelog; Linear comment with table and transcript links.

**Test plan**

* Unit: renderer snapshot for one lead and one sub; frontmatter tool list formatting; hash banner.
* Integration: `--check` drift detection; CI job on both forges.
* e2e: smoke run in CI nightly (cheap mode) and once on Fable for the baseline.
* No UI.

**Demo**

Edit one word in `characters/nova.yaml`, run `pnpm agents build --check` and see it fail naming `.claude/agents/nova.md`; run `pnpm agents build` then `pnpm agents smoke --lead sentinel` and read three green checks. Ninety seconds.

**Edge cases**

* Prompt include missing: build fails with the include path.
* Tool name unknown to Claude Code: build warns; PAP-106 hook fails closed at runtime.
* Smoke model outage: results marked `incomplete`, not red.
* Windows checkout with CRLF: build normalises; `.gitattributes` enforces LF.
* Forty-plus characters later: build time under 2 s (bench).

**Dependencies**

Blocked by {{agents/roster-v1/yaml}}, {{agents/roster-v1/lead-prompts}}, {{agents/roster-v1/sub-prompts}}. Uses PAP-78, PAP-92.

**Agent**

Built by Atlas (Dispatcher sub-agent); reviewed by Sentinel.

**Size**

M
"""},
]

CHILDREN["PAP-110"] = [
{
"key": "agents/eval-harness/runner", "title": "Eval harness: task format, SDK runner, deterministic graders and results table", "type": "Build", "size": "M",
"blockedBy": [], "blocks": ["agents/eval-harness/tasks", "agents/eval-harness/judge"],
"description": """**Goal**

Build the machinery of the eval harness: the frozen task format, a runner that launches a character on a task in a throwaway worktree through the Agent SDK with its PAP-106 bundle, deterministic graders (tests pass, files exist, schema valid, footer present, no denied tool calls) and the `eval_runs` table, so tasks and the judge can be added on top.

**Scope**

* In: `packages/agents/evals/src/{task,run,grade,store}.ts`, `task.yaml` schema, `pnpm evals run | list`, `orchestrator.eval_runs` migration, fixture repo tarball handling, cheap mode flags.
* Out: the task set ({{agents/eval-harness/tasks}}), the LLM judge, trend and regression issues ({{agents/eval-harness/judge}}).

**Spec**

* `task.yaml`: `{ id, character, version, prompt, fixtures: { repo: tarball | template@sha, files? }, allowedTools?, maxTurns, budgetUsd, flaky, graders: [{ kind: tests | fileExists | schema | footer | noDenied | command, args }] }`; Zod-validated; changing content without bumping `version` fails `evals list`.
* Runner: unpack fixtures into `/srv/evals/<run>/<task>`, call `launchSession` from {{pm-linear/orchestrator/sessions}} with `sandbox: true` when {{agents/runtime-sandbox}} exists, `model` and `effort` overrides, capture transcript, cost (PAP-98 `result`), duration and denied-tool events (PAP-107).
* Graders return `{ id, pass, detail }`; `command` grader runs inside the fixture with a timeout; `tests` runs `pnpm vitest run` in the fixture.
* Store: `eval_runs(run_id, character, task, task_version, model, effort, score, checks_json, judge_json, cost_usd, duration_ms, transcript_ref, git_sha, at)`; `score` for this child is the deterministic pass ratio; judge fills `judge_json` later.
* Cheap mode `--model claude-sonnet-5 --effort low` for smoke.

**Interface contract**

* Provides: `TaskSchema`, `runTask(task, opts): EvalResult`, `grade(task, workspace): Check[]`, `pnpm evals run [--character] [--task] [--model] [--effort] [--cap]`, `pnpm evals list`, table `eval_runs`, `EvalResult` Zod type.
* Consumers: sibling children; PAP-104 build child (smoke outputs convertible to tasks); PAP-105 skill PRs (cheap mode gate); PAP-241 (F1 scorer helper lives in `grade.ts`).
* Requires: {{pm-linear/orchestrator/sessions}} `launchSession`, PAP-106 bundles, PAP-98 cost, PAP-111 cap, PAP-107 events.

**Definition of done**

* Two seed tasks (Quill spec validates, Forge migration applies) run end to end and store rows.
* Graders unit-tested with pass and fail fixtures; frozen-version check tested.
* Cheap mode run under $5 for the two tasks; numbers in comment.
* Changelog; Linear comment.

**Test plan**

* Unit: task schema, version freeze, each grader, score arithmetic.
* Integration: runner with a mocked SDK producing files; fixture unpack and cleanup.
* e2e: two real tasks in staging.
* No UI.

**Demo**

Run `pnpm evals run --task quill/page-spec-invoices --model claude-sonnet-5 --effort low` and watch checks print pass or fail with the transcript path; `pnpm evals list` shows versions. Ninety seconds.

**Edge cases**

* Fixture tarball missing: fail fast before spending tokens.
* Session exceeds `budgetUsd`: aborted via PAP-111, run stored with `aborted: true`.
* Grader command hangs: timeout 5 minutes, check fails with `timeout`.
* Worktree reuse between tasks: never; fresh directory per run.
* Same task run twice in one night: both stored; trend uses the latest.

**Dependencies**

Blocked by PAP-104, PAP-105 (through the parent). Uses {{pm-linear/orchestrator/sessions}}, PAP-106, PAP-98, PAP-111.

**Agent**

Built by Sentinel (lead) with Atlas on the runner; reviewed by Forge.

**Size**

M
"""},
{
"key": "agents/eval-harness/tasks", "title": "Eval harness: golden task set (three per lead, one per sub) with fixture repos and answer keys", "type": "Build", "size": "M",
"blockedBy": ["agents/eval-harness/runner"], "blocks": ["agents/eval-harness/judge"],
"description": """**Goal**

Write the golden tasks that define what good looks like for every character: at least three per lead and one per sub (about 55), each with a frozen prompt, a fixture repo pinned to a template SHA, deterministic graders and, where judgement is needed, a rubric, including the seeded-bug PR for Sentinel with an answer key and F1 scoring.

**Scope**

* In: `packages/agents/evals/tasks/<character>/<task-id>/` for all characters, fixture tarballs under `packages/agents/evals/fixtures/`, `answer-key.json` for seeded bugs, rubric files, a weekly fixture bump job.
* Out: runner and graders ({{agents/eval-harness/runner}}), judge and trend ({{agents/eval-harness/judge}}).

**Spec**

* Lead tasks: Atlas decomposes a mini brief into three contract-valid issues (grader: PAP-93 `validateIssue` on each), schedules a toy graph, writes a decision card; Forge adds a Drizzle table with migration and RLS (grader: migration applies, RLS test passes), fixes a failing CI job, writes a compose service; Iris builds a component with stories passing axe, fixes a contrast bug, adds a token; Quill writes a page spec that validates, an ADR, a changelog from PRs; Sentinel reviews a PR with five planted bugs (F1 over findings by file and line range), reviews a spec-conformance drift, triages screenshots; Nova adds a grid column type, a kanban swimlane, a canvas node; Ledger posts a balanced journal entry (grader: debits equal credits), reconciles a Stripe fixture, computes a payroll adapter mapping; Beacon drafts a campaign from a changelog for approval (rubric), a landing form spec, a CRM segment; Scout scores a library against the rubric (grader: all criteria present), drafts an ADR, runs a license check.
* Sub tasks: one focused task each matching its `description` trigger.
* Fixtures pinned to `paperos-template@<sha>`; seeded bugs documented in `answer-key.json` with `file`, `lines`, `severity`, `category`.
* Rubrics: 0-5 per criterion with anchors; at most five criteria per task.

**Interface contract**

* Provides: about 55 task folders validating against `TaskSchema`, fixture tarballs, `answer-key.json` format `{ bugs: [{ id, file, lines: [a, b], severity, category }] }`, `scoreF1(findings, key)` in `grade.ts`.
* Consumers: {{agents/eval-harness/judge}} (rubrics), PAP-241 (seeded-bug fixture and F1 for Gate 2 calibration), PAP-81 (same fixture for reviewer calibration), PAP-104 (smoke outputs cross-checked).
* Requires: runner child; PAP-93, PAP-115, PAP-79 for graders and rubric anchors; template SHA.

**Definition of done**

* `pnpm evals list` shows all tasks; every task runs once in cheap mode without infrastructure errors (table attached).
* Seeded-bug PR: a deliberately perfect answer scores F1 1.0 and an empty answer 0.0 (tests).
* Fixture bump job opens a PR when the template SHA moves.
* Changelog; Linear comment with the task table.

**Test plan**

* Unit: `scoreF1` cases, answer-key schema, task schema for every folder.
* Integration: cheap-mode run of all tasks once.
* No UI.

**Demo**

Open `tasks/sentinel/seeded-bugs-1/answer-key.json`, run `pnpm evals run --task sentinel/seeded-bugs-1 --model claude-sonnet-5 --effort low` and read the F1 score with matched and missed bug ids. Two minutes.

**Edge cases**

* Task depends on a package not yet merged (dashboard blocks): fixture pins a branch tarball; task marked `pending-dependency` and excluded from trend.
* Two tasks share a fixture: one tarball, referenced twice.
* Sentinel finds an unplanted real bug: counts as a true positive if a reviewer confirms; answer key updated with a version bump.
* Rubric criterion ambiguous: anchors rewritten; version bump resets trend.
* Fixture over 50 MB: stored in MinIO (PAP-37) with a hash reference.

**Dependencies**

Blocked by {{agents/eval-harness/runner}}. Uses PAP-93, PAP-115, PAP-79.

**Agent**

Built by Sentinel (Edge Case Hunter) with each lead contributing its own tasks; reviewed by Quill.

**Size**

M
"""},
{
"key": "agents/eval-harness/judge", "title": "Eval harness: LLM judge, trend, regression issues, nightly schedule and report page", "type": "Build", "size": "M",
"blockedBy": ["agents/eval-harness/runner", "agents/eval-harness/tasks"], "blocks": [],
"description": """**Goal**

Close the loop: an LLM judge scores rubric tasks with strict JSON output, a combined score feeds a per-character trend, regressions open or update a Linear issue, a nightly run under a budget cap keeps the numbers current, and a report page shows the state of the org at a glance.

**Scope**

* In: `packages/agents/evals/src/{judge,trend,regress,report}.ts`, nightly workflow `.github/workflows/evals-nightly.yml` (03:00 UTC), `docs/agents/evals.md` regeneration, regression issue template, judge agreement check.
* Out: runner and tasks (sibling children), eval of reviewer misses on real PRs (PAP-241).

**Spec**

* Judge: Sentinel Code Reviewer definition on `claude-fable-5-1` at `high`, input rubric, summarised transcript and diff; output constrained to `judge.schema.json` `{ criteria: [{ id, score: 0-5, justification }], overall }`; stored in `judge_json`.
* Combined score: `0.6 * deterministicRatio + 0.4 * judgeNormalised` when both exist, else the one available; disagreement flag when deterministic passes and judge under 2.
* Trend: per character and task over the last 14 runs; regression when score drops more than 15 percent from the seven-run median or a check that passed three consecutive times fails; flaky tasks need two consecutive regressions.
* Regression issue `Eval regression: <character>/<task>` (Type Review, Character label Sentinel, project agents) created or updated with a table and transcript diff links; one issue per character per night.
* Nightly: all non-flaky tasks, cap $60 through PAP-111 `--cap`, remaining tasks `skipped-budget`; report regenerated with a table and 14-day sparkline per character; runs logged with `issueKey: EVAL`.

**Interface contract**

* Provides: `judge(task, result): Judgement`, `combinedScore()`, `detectRegressions(runs): Regression[]`, `pnpm evals report`, `docs/agents/evals.md`, the regression issue template, `judge.schema.json`.
* Consumers: PAP-112 links the report; PAP-113 optional score badge; {{pm-linear/weekly-reaudit}} eval section; PAP-241 reuses the judge agreement method.
* Requires: sibling children, PAP-111 cap, PAP-91 ids for issue creation, PAP-105 `linear-update` for posting.

**Definition of done**

* Judge agreement: 20 judged outputs spot-checked by Sentinel with agreement above 80 percent (recorded).
* Regression proven by breaking Iris's prompt on a branch and observing the issue (screenshot).
* Full nightly run completes under three hours and under cap; report screenshot at 1280 px.
* Changelog; Linear comment with the first baseline table.

**Test plan**

* Unit: combined score cases, regression rule with synthetic histories and fake clock, flaky handling, one-issue-per-character dedupe.
* Integration: judge with a recorded transcript against the schema; report renderer snapshot.
* e2e: nightly run in staging; the Iris break test.
* Visual: report page at 1280 px only.

**Demo**

Run `pnpm evals report` and read the trend table; then `pnpm evals regress --simulate iris` to see the regression issue draft printed with its table. One minute.

**Edge cases**

* Judge output fails schema: retry once, then `judge: null`, deterministic only.
* Model outage mid-run: run `incomplete`, no regressions filed.
* Two regressions for one character: one issue, table of both.
* Task version bumped: trend resets; no regression against old versions.
* Report exceeds Linear comment size: link to the docs page with a five-line summary.

**Dependencies**

Blocked by {{agents/eval-harness/runner}}, {{agents/eval-harness/tasks}}. Uses PAP-111, PAP-105.

**Agent**

Built by Sentinel (lead); reviewed by Atlas.

**Size**

M
"""},
]
