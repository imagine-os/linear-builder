---
identifier: "PAP-717"
title: "Session-end guard: `Stop` and `SessionEnd` hooks that validate the footer, run `handoff lint`, require a pushed branch or `wip:` commit and post the memory block before a session may end"
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
blockedBy: ["PAP-92", "PAP-709"]
blocks: ["PAP-109"]
key: "r4/agents/session-end-guard-hooks"
url: "https://linear.app/paperos/issue/PAP-717/session-end-guard-stop-and-sessionend-hooks-that-validate-the-footer"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:31.147Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 2
dueDate: "2026-09-24"
cycle: null
---

# PAP-717: Session-end guard: `Stop` and `SessionEnd` hooks that validate the footer, run `handoff lint`, require a pushed branch or `wip:` commit and post the memory block before a session may end

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Build S

**Goal**

The playbook (PAP-92), handoff protocol (PAP-108) and memory writer (PAP-109) all rely on the session doing the right thing in its last turn: a valid footer, a linted `HANDOFF.md`, pushed code, a memory block. Claude Code `Stop` hooks can block a stop and tell the model what is missing. This issue turns the end-of-session checklist into a hook that refuses to let a session end wrong, so the orchestrator never has to synthesise a `crashed` handoff for a session that simply forgot.

**Scope**

* In: `packages/agents/hooks/session-end-guard.ts` wired as `Stop` (blocking, with the missing items as the reason) and `SessionEnd` (final audit, non-blocking) in `hooks.json` (PAP-106 bundle), checks (footer parses against `session-footer.schema.json`, `HANDOFF.md` passes `pnpm handoff lint` when `status` is `handoff` or `partial`, worktree clean or committed as `wip:` and pushed, memory block present or `memory: none` declared, no `TODO(PAP-` markers without a follow-up issue reference), retry cap, `docs/agents/session-end.md`.
* Out: the footer schema (PAP-92), lint rules (PAP-108), memory semantics (PAP-109), budget aborts (PAP-111 bypasses the guard with `hard: true`).

**Spec**

* `Stop` hook reads the transcript path from the hook JSON, extracts the last assistant message, and runs the checks; on failure it returns `decision: block` with `reason` listing the missing items and the exact fix (```` Add a ```paperos-session footer with status ended ````, `Run pnpm handoff lint`, `git push -u origin <branch>`); Claude Code feeds the reason back and the session continues; after three blocked stops the hook allows the stop and logs `session-end.forced` so a runaway loop cannot spend the budget.
* `SessionEnd` writes `session-end.audit` to the spool (PAP-107) with the check results so PAP-96 can synthesise `crashed` only when the audit is missing.
* Checks are pure functions in `packages/agents/src/session-end/checks.ts` shared with the orchestrator's footer parser (PAP-282) and PAP-105 `linear-update`, so the three agree.
* Kill and budget aborts (PAP-111) set `PAPEROS_FORCE_STOP=1`; the guard then only records the audit.
* Latency under 2 s; `pnpm handoff lint` runs only when a `HANDOFF.md` exists or the footer says `handoff`.

**Interface contract**

* Provides: `session-end-guard.ts`, `checks.ts`, spool event `session-end.audit`, `session-end.forced`, env `PAPEROS_FORCE_STOP`.
* Consumes: PAP-92 footer schema and templates, PAP-108 lint, PAP-109 block grammar, PAP-106 `hooks.json`, PAP-107 spool, PAP-111 force stop, PAP-282 footer parser.

**Definition of done**

* Fixture transcripts (missing footer, unpushed branch, handoff without defaults, valid) produce the expected block or allow decisions; a session that ignores three blocks is allowed with `forced` logged (tests).
* Live: a toy session that tries to end without a footer is told what is missing and ends correctly on the next turn (recording).
* PAP-96 `crashed` synthesis test now checks for a missing audit; docs; changelog; Linear comment with the recording.

**Test plan**

* Unit: each check on fixtures, retry cap, force-stop bypass, shared parser agreement test with PAP-282.
* E2E: toy sessions on the sandbox repo with and without a footer; a kill during a session.

**Demo**

Run a two-turn `claude -p` session with the bundle and no footer: watch the stop blocked with the reason, the model add the footer, and the session end; `cat` the spool audit. Under one minute.

**Edge cases**

* Session ends because of context exhaustion: the hook still runs; a missing footer is `forced` and PAP-96 retries with the last progress footer.
* Reviewer sessions (plan mode, no code): the pushed-branch check is `n/a` when the character has no write scope.
* Very large `HANDOFF.md`: lint time-boxed to 20 s; timeout allows the stop and logs it.
* Hook disabled in a repo without the plugin: the orchestrator's footer parser still validates and posts `contract-failed`.

**Dependencies**

Hard: PAP-92, PAP-108, PAP-709. Soft: PAP-109, PAP-107, PAP-111, PAP-282, PAP-105.

* Soft dependency (round 4): PAP-108 is a soft dependency, not a `blocks` relation, because its milestone (2026-09-25) is later than this issue's (2026-09-24); build against its interface and reconcile when it lands.
  **Agent**

Builder: Atlas (Dispatcher) with Quill on the check wording. Reviewer: Sentinel (Code Reviewer).

**Size**

S: half a session.

*Round 4 critique fix (2026-09-18):* resolved 1 round-4 file key in this description to Linear identifiers: `r4/agents/character-bundles-and-enforce-scope-hook` = PAP-709.
*Round 4 critique fix (2026-09-18):* PAP-108 appears in the Hard list above and in a round-4 soft note; it is soft (no `blocks` relation). Read the Hard list without it.
