---
identifier: "PAP-96"
title: "Build the orchestrator that polls Ready for Claude, spawns one Claude Code session per issue in a git worktree and moves states"
project: "pm-linear"
projectName: "Project Management & Claude Pipeline"
phase: "P0"
type: "Build"
priority: 1
surfaces: ["Agent"]
milestone: "Orchestrator claims and ships issues"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-25", "PAP-46", "PAP-91", "PAP-92"]
blocks: ["PAP-97", "PAP-98", "PAP-99"]
key: "pm-linear/orchestrator"
url: "https://linear.app/paperos/issue/PAP-96/build-the-orchestrator-that-polls-ready-for-claude-spawns-one-claude"
source: "plan/specs/bucket-3.json (round-1 canonical spec JSON)"
---

# PAP-96: Build the orchestrator that polls Ready for Claude, spawns one Claude Code session per issue in a git worktree and moves states

**Goal**

Build the engine that turns Linear into running agents: a long-lived service that polls `Ready for Claude`, claims one issue at a time per slot, creates a git worktree, launches a Claude Code session configured for the issue's character, streams its progress, and moves the issue through `In Progress` to `In Review` when a PR exists. Everything else in the pipeline (webhooks, metering, concurrency) plugs into this service.

**Scope**

In:
- Repo `imagine-os/paperos-orchestrator` (pre-provisioned): TypeScript, Node 22, pnpm, Biome, Vitest; deployed as a Docker service on the VPS via Coolify with the target repos cloned under `/srv/repos/<repo>` and worktrees under `/srv/worktrees/<PAP-key>`.
- Poll loop (every 30 s, also triggered by webhook) using `@linear/sdk`: `issues(filter: {team: {key: {eq: "PAP"}}, state: {name: {eq: "Ready for Claude"}}, assignee: {null: true}})` ordered by priority then `createdAt`.
- Claim: `issueUpdate` set assignee to the character's bot user (from `forge/bot-accounts` mapping) and state `In Progress`, atomically guarded by re-reading the issue and checking `updatedAt` matches.
- Worktree: `git -C /srv/repos/<repo> fetch origin && git worktree add /srv/worktrees/PAP-123 -b <branch> origin/main` with branch name from `forge/branch-policy`; `pnpm i --frozen-lockfile`.
- Session launch through `@anthropic-ai/claude-agent-sdk` `query()` with options: `cwd` worktree, `permissionMode` from the character schema (default `acceptEdits`), `allowedTools`/`disallowedTools` and `mcpServers` from `agents/tool-scopes`, `agents` loaded from `.claude/agents`, `maxTurns` from `agents/cost-controls` (default 200), `model` `claude-fable-5-1`, `settingSources: ["project"]`. Prompt is the rendered `prompts/issue.md` template: issue body, playbook pointer, character name, branch, and the required footer JSON.
- Stream handling: persist every SDK message to `sessions/<id>.ndjson` (handoff to `agents/prompt-logging-hook`), forward `result` message (`total_cost_usd`, `num_turns`, `duration_ms`) to metering.
- Completion: detect a PR on the branch via `gh pr list --head <branch>` (GitHub) and Forgejo API; set `In Review`, add attachment (`attachmentCreate`) with the PR URL; on no PR after the session ends, post the footer and return the issue to `Ready for Claude` with label `retry-1`, max 2 retries then `Needs Justin`.
- Storage: Postgres (the platform instance from `data-layer/postgres-provision`, schema `orchestrator`) tables `sessions`, `claims`, `events`; Drizzle migrations.
- Ops: `GET /healthz`, `GET /status` JSON (slots, active sessions, queue depth), structured logs (pino), graceful shutdown that lets sessions finish or marks them `interrupted`.

Out: webhook receiver (`pm-linear/webhooks`), burn reports (`pm-linear/credit-metering`), scheduling beyond a fixed `maxParallel` (`pm-linear/concurrency`), the Linear PM data model.

**Spec**

- Package layout: `src/linear/` (client, queries, state ids from `linear-workspace.json`), `src/git/worktree.ts`, `src/session/launch.ts`, `src/session/prompt.ts`, `src/loop.ts`, `src/db/`, `src/http.ts`. Config via `orchestrator.config.yaml` validated with Zod: `maxParallel` (default 4), `pollIntervalMs`, `repos[]` (name, path, defaultBranch, linearProjectKeys[]), `characters` path.
- Character resolution: Character label on the issue; fallback to the project's default character; fail to `Needs Justin` if none.
- Session prompt must instruct the model to follow `.claude/rules/session-playbook.md` and end with the footer block; the orchestrator parses the last assistant text for it and stores `status`.
- Retries reuse the existing worktree; a new session gets the previous session's footer in its prompt.
- Everything the orchestrator posts to Linear goes through one `linearComment()` helper that adds the footer and dedupes by `(issueId, sha256(body))`.

**Definition of done**

- Unit tests for claim atomicity (simulated concurrent poll), prompt rendering (snapshot), worktree lifecycle (temp git repo), footer parsing.
- Integration test with a mocked Agent SDK stream that emits assistant, tool_use and result messages.
- Live run: a real `Ready for Claude` issue on a toy repo produces a worktree, a session, a PR, `In Review` state and a PR attachment; recording attached.
- `/status` endpoint screenshot; Coolify deploy green; restart mid-session marks the session `interrupted` and re-queues the issue.
- README with runbook (start, stop, drain, inspect a session); changelog entry; Linear comment with the recording and PR link.

**Edge cases**

- Two orchestrator replicas: claims use `SELECT ... FOR UPDATE SKIP LOCKED` on `claims`; only one wins.
- Worktree directory exists but is dirty from a crash: stash to `crash/<timestamp>` branch, recreate.
- Session ends with `stop_reason` `max_turns` or budget exhaustion: commit `wip:`, push, comment, mark `partial`.
- Linear API down: keep running sessions, pause claiming, exponential backoff, alert in logs.
- Issue moved out of `Ready for Claude` between poll and claim: `updatedAt` guard fails, skip.
- Branch already exists on origin from a previous attempt: check out and rebase onto `main` instead of failing.
- Agent SDK throws a `refusal` stop: record `stop_details.category`, post to `Needs Justin` with the category, do not retry.

**Dependencies**

- `pm-linear/configure-workspace` (states, labels, snapshot ids).
- `forge/branch-policy` (branch names, commit rules, worktree conventions).
- `pm-linear/session-playbook` (the prompt points sessions at it).
- Soft: `forge/bot-accounts` for per-character assignees (falls back to one bot user), `data-layer/postgres-provision` (falls back to SQLite via `better-sqlite3` in dev).

**Agent**

Built by Atlas (Dispatcher sub-agent) with Forge (Ops Runner) for the Coolify deploy; reviewed by Sentinel (Code Reviewer and Security Auditor, since this service holds every credential).

**Size**

L: the central service of the plan, with git, Linear, Agent SDK and Postgres integration and a live soak.
