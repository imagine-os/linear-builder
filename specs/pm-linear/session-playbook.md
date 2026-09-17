---
identifier: "PAP-92"
title: "Write the session playbook: how a Claude session picks up an issue, what it must read, how it reports and ends"
project: "pm-linear"
projectName: "Project Management & Claude Pipeline"
phase: "P0"
type: "Docs"
priority: 1
surfaces: ["Agent"]
milestone: "Linear configured for the pipeline"
state: "Ready for Claude"
parent: null
children: []
blockedBy: []
blocks: ["PAP-96"]
key: "pm-linear/session-playbook"
url: "https://linear.app/paperos/issue/PAP-92/write-the-session-playbook-how-a-claude-session-picks-up-an-issue-what"
source: "plan/specs/bucket-3.json (round-1 canonical spec JSON)"
---

# PAP-92: Write the session playbook: how a Claude session picks up an issue, what it must read, how it reports and ends

**Goal**

Write the one document every Claude Code session reads first: how an issue is picked up, what must be read before code is written, how progress is reported to Linear, how the PR is opened, and how the session ends cleanly. It is the human-readable contract that `pm-linear/orchestrator` automates and `agents/roster-v1` embeds into every character's system prompt.

**Scope**

In:
- `docs/pm/session-playbook.md` (also copied into `.claude/rules/session-playbook.md` in `paperos-template` so it is loaded automatically) covering: claim, orient, plan, build, verify, report, hand off, end.
- Required reading order: the Linear issue body (contract sections), linked page specs under `specs/`, `CLAUDE.md`, the character's memory file (`agents/memory`), the two most recent Linear comments on the issue, and the project's ADRs in `docs/adr/` touched by the issue.
- Reporting cadence: a Linear comment at start (`Session started` with worktree, branch, character, model), at every meaningful milestone (max one per 30 minutes), and at end (`Session ended` with PR link, gates status, cost).
- Comment format: a fixed markdown template with a machine-readable footer block (` ```paperos-session ` fenced JSON with `sessionId`, `character`, `costUsd`, `turns`, `pr`, `status`) that `pm-linear/credit-metering` and `agents/handoffs` parse.
- End conditions: PR opened and `In Review` set; blocked (moves to `Needs Justin` with a single question); out of budget (posts partial state and stops); dependency missing (comments and returns to `Backlog`).
- Rules: never push to `main`; one issue per worktree; do not edit files outside the paths named in the issue's `Scope` without adding a comment explaining why; run `pnpm check` before opening a PR; attach screenshots at the breakpoints the issue lists.
- A 20-line quick reference at the top and a checklist the session pastes into its final comment.

Out: automation of these steps (orchestrator), the handoff protocol details between characters (`agents/handoffs`), review rubrics (`quality/review-rubrics`).

**Spec**

- Document structure: Purpose, Lifecycle diagram (mermaid, states mirror Linear), Step-by-step with the exact commands (`git worktree add`, `pnpm i`, `pnpm check`, `gh pr create --template`), Comment templates, Stop conditions, FAQ.
- Reference the branch naming and commit conventions from `forge/branch-policy` by link rather than restating them.
- Include a worked example transcript for a small issue (adding a Storybook story) showing the three comments verbatim.
- Word budget 1500-2500; reading time under 10 minutes because every session pays the tokens to read it.
- Versioned: a `playbookVersion` field in the footer JSON so the orchestrator can flag sessions running an outdated playbook.

**Definition of done**

- `docs/pm/session-playbook.md` and `.claude/rules/session-playbook.md` are identical (CI check compares them).
- A dry-run session (Claude Code, `-p` mode) given only the playbook and a toy issue produces the three comments in the correct format, verified by parsing the footer JSON with the schema committed at `packages/agents/src/session-footer.schema.json`.
- Reviewed by Sentinel for ambiguity: every "must" has a verifiable check.
- Rendered in the docs engine once `collab/docs-engine` exists; until then linked from the repo README.
- Changelog entry; Linear comment on this issue linking the document and the dry-run transcript.

**Edge cases**

- Issue has no linked spec: playbook says stop and comment `needs-spec` rather than inventing one.
- Two sessions claim the same issue (orchestrator race): playbook says check the assignee and the last `Session started` comment; the later session exits.
- Session context is compacted mid-task: the footer JSON of the last comment is the recovery point; playbook says re-read it.
- Worktree already exists from a crashed session: reuse if branch matches, else create `-2` suffix and note it.
- Justin comments mid-session: treat as highest priority instruction, acknowledge in the next comment.
- Budget cap hit with uncommitted work: commit as `wip:` on the branch, push, comment, stop.

**Dependencies**

None to start (`readyNow: true`). Consumed by `pm-linear/orchestrator`, `agents/roster-v1`, `agents/handoffs`, `agents/skills-library` (the `linear-update` skill implements the comment templates).

**Agent**

Built by Quill (lead); reviewed by Atlas for operational fit and by Sentinel for testability.

**Size**

S: pure writing, but it is load-bearing so it gets a dry-run test.
