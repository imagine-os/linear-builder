---
key: "pm-linear/orchestrator/sessions"
title: "Orchestrator: worktree lifecycle and Claude session launch"
project: "pm-linear"
parent: "PAP-96"
phase: "P0"
type: "Build"
priority: null
size: "M"
surfaces: ["Agent"]
milestone: null
intendedState: "Backlog"
blockedBy: ["pm-linear/orchestrator/claims"]
blocks: ["pm-linear/orchestrator/deploy"]
source: "round2/agent2/new_pm.py"
linearDocument: "https://linear.app/paperos/document/round-2-pending-issues-pm-linear-9-d4829fc00859"
status: "pending"
---

# Orchestrator: worktree lifecycle and Claude session launch

**Goal**

Turn a claim into a running Claude Code session: create or reuse the git worktree, render the prompt, launch through the Agent SDK with the character's bundle, stream messages to storage, capture the footer and detect the PR so the parent can move the issue to `In Review`.

**Scope**

* In: `src/git/worktree.ts`, `src/session/{prompt,launch,stream}.ts`, prompt template `prompts/issue.md`, PR detection, retry handoff of the previous footer.
* Out: claiming (`pm-linear/orchestrator/claims`), HTTP and deploy (`pm-linear/orchestrator/deploy`), sandboxing (`agents/runtime-sandbox`, which wraps `launch`).

**Spec**

* Worktree: `git -C /srv/repos/<repo> fetch origin && git worktree add /srv/worktrees/<PAP-key> -b <branch> origin/main` with the PAP-46 branch name; `pnpm i --frozen-lockfile`; reuse when branch matches; dirty crash leftovers stashed to `crash/<timestamp>`.
* Prompt: issue body, playbook pointer, character, branch, memory block (PAP-109 when available), previous footer on retry, required footer instruction.
* Launch: `query()` from `@anthropic-ai/claude-agent-sdk` with `cwd`, `permissionMode`, `allowedTools`, `disallowedTools`, `mcpServers` from the PAP-106 bundle (default allowlist until it lands), `agents` from `.claude/agents`, `maxTurns` from PAP-111 (default 200), `model` from `roster.json`, `settingSources: ["project"]`, abort controller exposed.
* Stream: every message to `sessions/<id>.ndjson` and `events`; `result` forwarded to PAP-98; last assistant text parsed for the footer and stored in `sessions.footer_json`.
* Completion: `gh pr list --head <branch>` and Forgejo API; PR found calls `toInReview`; none found calls `retry` with the footer in the next prompt.

**Interface contract**

* Provides: `ensureWorktree(repo, key): Worktree`, `renderPrompt(claim, ctx): string`, `launchSession(claim, opts): { sessionId, abort, done: Promise<Footer> }`, `detectPr(branch): PrRef | null`, events `session.started`, `session.message`, `session.ended`.
* Consumers: PAP-98 (`result`), PAP-107 (NDJSON handoff), PAP-111 (`abort`, wrap-up injection through `opts.onProgress`), PAP-110 eval runner reuses `launchSession` with a throwaway worktree, `agents/session-observability` heartbeats from `session.message`.
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

Blocked by `pm-linear/orchestrator/claims`. Soft: PAP-106, PAP-109, `agents/runtime-sandbox`.

**Agent**

Built by Atlas (Dispatcher sub-agent); reviewed by Sentinel.

**Size**

M
