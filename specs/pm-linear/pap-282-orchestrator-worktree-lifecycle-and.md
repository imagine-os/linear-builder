---
identifier: "PAP-282"
title: "Orchestrator: worktree lifecycle and Claude session launch"
project: "pm-linear"
projectName: "Project Management & Claude Pipeline"
phase: "P0"
type: "Build"
priority: 1
surfaces: ["Agent"]
milestone: "Orchestrator claims and ships issues"
state: "Backlog"
parent: "PAP-96"
children: []
blockedBy: ["PAP-281"]
blocks: ["PAP-283", "PAP-704", "PAP-720"]
key: "pm-linear/orchestrator/sessions"
url: "https://linear.app/paperos/issue/PAP-282/orchestrator-worktree-lifecycle-and-claude-session-launch"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:28:49.251Z"
model: "claude-opus-5"
effort: "high"
estimate: 3
dueDate: "2026-09-22"
cycle: null
---

# PAP-282: Orchestrator: worktree lifecycle and Claude session launch

**Model / Effort:** Opus 5 (`claude-opus-5`) / high — child of PAP-96 orchestrator (named exception applied to children)

**Goal**

Turn a claim into a running Claude Code session: create or reuse the git worktree, render the prompt, launch through the Agent SDK with the character's bundle, stream messages to storage, capture the footer and detect the PR so the parent can move the issue to `In Review`.

**Scope**

* In: `src/git/worktree.ts`, `src/session/{prompt,launch,stream}.ts`, prompt template `prompts/issue.md`, PR detection, retry handoff of the previous footer.
* Out: claiming (PAP-281), HTTP and deploy (PAP-283), sandboxing (PAP-280, which wraps `launch`).

**Spec**

* Worktree: `git -C /srv/repos/<repo> fetch origin && git worktree add /srv/worktrees/<PAP-key> -b <branch> origin/main` with the PAP-46 branch name; `pnpm i --frozen-lockfile`; reuse when branch matches; dirty crash leftovers stashed to `crash/<timestamp>`.
* Prompt: issue body, playbook pointer, character, branch, memory block (PAP-109 when available), previous footer on retry, required footer instruction.
* Launch: `query()` from `@anthropic-ai/claude-agent-sdk` with `cwd`, `permissionMode`, `allowedTools`, `disallowedTools`, `mcpServers` from the PAP-106 bundle (default allowlist until it lands), `agents` from `.claude/agents`, `maxTurns` from PAP-111 (default 200), `model` from `roster.json`, `settingSources: ["project"]`, abort controller exposed.
* Stream: every message to `sessions/<id>.ndjson` and `events`; `result` forwarded to PAP-98; last assistant text parsed for the footer and stored in `sessions.footer_json`.
* Completion: `gh pr list --head <branch>` and Forgejo API; PR found calls `toInReview`; none found calls `retry` with the footer in the next prompt.

*Round 4 amendment (2026-09-18):*

* Model selection (round 4, aligns with CLAUDE.md): `launchSession` calls `resolveModel(issue, character, 'builder')` from `src/session/model-routing.ts`; precedence is the issue's `Model` and `Effort` labels, then the character's `model` and `effort` in `roster.json`, then Sonnet 5 / medium. The served model reported by the SDK is stored in `sessions.model_served` and the footer; on 529 or 429 storms the fallback chain Fable 5.1 to Opus 5 to Sonnet 5 applies after three attempts, never upward, and a refusal stop never falls back.

*Round 4 amendment (2026-09-18):*

* Prompt order and context pack (round 4): `renderPrompt` places, in this order, the system prompt, the character prompt, the memory block (PAP-109), the project context pack (PAP-716), the umbrella's Module boundary paragraph, then the issue body and untrusted blocks (PAP-299 wrapping), so the prefix is byte-identical across sessions of one character on one project and the prompt cache hits; a snapshot test asserts the order.

**Interface contract**

* Provides: `ensureWorktree(repo, key): Worktree`, `renderPrompt(claim, ctx): string`, `launchSession(claim, opts): { sessionId, abort, done: Promise<Footer> }`, `detectPr(branch): PrRef | null`, events `session.started`, `session.message`, `session.ended`.
* Consumers: PAP-98 (`result`), PAP-107 (NDJSON handoff), PAP-111 (`abort`, wrap-up injection through `opts.onProgress`), PAP-110 eval runner reuses `launchSession` with a throwaway worktree, PAP-288 heartbeats from `session.message`.
* Requires: sibling claims module, PAP-46 branch policy, PAP-92 footer, PAP-104 roster, PAP-106 bundles (soft).

**Definition of done**

* Worktree tests on a temp repo: create, reuse, crash recovery, existing remote branch rebase.
* Prompt snapshot test; footer parsing test on three transcripts.
* Integration with a mocked SDK stream (assistant, tool_use, result).
* Live: one rehearsal issue produces a worktree, a session, a PR; footer stored; recording.
* Changelog; Linear comment.

**Test plan**

* Unit: branch naming, prompt rendering with and without memory, footer regex, PR mapping.
* Integration: temp git remote plus mocked SDK; `max_turns` stop marks `partial` and pushes `wip:`.
* e2e: live toy issue on staging.
* No UI.

**Demo**

With claims running, watch `/srv/worktrees/PAP-n` appear, tail `sessions/<id>.ndjson` to see tool calls stream, and see the PR open on the forge when the session ends. Two minutes.

**Edge cases**

* `stop_reason: max_turns` or budget: commit `wip:`, push, footer `partial`.
* Refusal stop: record category, escalate, no retry.
* Worktree path exists but wrong branch: `-2` suffix.
* `pnpm i` fails (lockfile drift): comment and retry once after `git pull`.
* PR opened by the session under a different branch name: fallback to `Closes PAP-n` search.

**Dependencies**

Blocked by PAP-281. Soft: PAP-106, PAP-109, PAP-280.

**Agent**

Built by Atlas (Dispatcher sub-agent); reviewed by Sentinel.

**Size**

M

*Round 4 critique fix (2026-09-18):* resolved 1 round-4 file key in this description to Linear identifiers: `r4/agents/docs-context-pack-and-cache-friendly-prompts` = PAP-716.
