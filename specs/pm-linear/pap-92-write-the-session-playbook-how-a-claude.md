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
blocks: ["PAP-96", "PAP-281", "PAP-299", "PAP-691", "PAP-713", "PAP-716", "PAP-717"]
key: "pm-linear/session-playbook"
url: "https://linear.app/paperos/issue/PAP-92/write-the-session-playbook-how-a-claude-session-picks-up-an-issue-what"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:52:36.409Z"
model: "claude-fable-5-1"
effort: "high"
estimate: 2
dueDate: "2026-09-20"
cycle: {"number": 1, "name": "C1 Foundation & core systems", "startsAt": "2026-09-18", "endsAt": "2026-09-25"}
---

# PAP-92: Write the session playbook: how a Claude session picks up an issue, what it must read, how it reports and ends

**Model / Effort:** Fable 5.1 (`claude-fable-5-1`) / high — keystone spec: session playbook

**Goal**

Write the one document every Claude Code session reads first: how an issue is claimed, what must be read before code is written, how progress is reported to Linear, how the PR is opened and how the session ends. It is the human-readable contract that PAP-96 automates and PAP-104 embeds in every character's prompt.

**Read first.** Read before coding: [Blueprint](<https://linear.app/paperos/document/paperos-core-platform-blueprint-0c2115fe48f1>) → [Interface & Data Contracts](<https://linear.app/paperos/document/paperos-interface-and-data-contracts-d40e6a4d227c>) → your project's `Contract` section (Linear project content) → your character sheet ([Roster](<https://linear.app/paperos/document/paperos-agent-roster-org-chart-and-character-index-fc7ea7f41ff3>)) → [Execution Schedule](<https://linear.app/paperos/document/paperos-execution-schedule-1fa3d38d6795>) for your start day and the branch-start rule. Also the [Security & Threat Model](<https://linear.app/paperos/document/paperos-security-and-threat-model-51fd5fd8929c>) (§4 deny list, §6 prompt tiers) and the [Golden Path](<https://linear.app/paperos/document/new-app-in-ten-minutes-the-golden-path-0f49429f566e>). The playbook you write carries this exact reading order and links every document in the Blueprint section "Documents (read in this order)".

**Scope**

* In: `docs/pm/session-playbook.md`, mirrored to `.claude/rules/session-playbook.md` in `paperos-template`; the comment templates; the footer JSON schema `packages/agents/src/session-footer.schema.json`; a worked example transcript.
* Out: branch and commit rules (PAP-46, linked), handoff semantics (PAP-108), character prompts (PAP-104).

**Spec**

* Structure: Purpose; lifecycle diagram (mermaid, states mirror Linear, including the Backlog → Ready for Claude promotion edge); How your issue got to Ready; steps claim, orient, plan, build, verify, report, hand off, end with exact commands (`git worktree add`, `pnpm i --frozen-lockfile`, `pnpm check`, `gh pr create --template`); comment templates; stop conditions; FAQ. 1500-2500 words, under ten minutes of reading.
* Required reading order: (1) the documents in the Blueprint section "Documents (read in this order)": [Blueprint](<https://linear.app/paperos/document/paperos-core-platform-blueprint-0c2115fe48f1>), [Interface & Data Contracts](<https://linear.app/paperos/document/paperos-interface-and-data-contracts-d40e6a4d227c>), the project's `Contract` section, [Roster](<https://linear.app/paperos/document/paperos-agent-roster-org-chart-and-character-index-fc7ea7f41ff3>) and the session's character sheet, [Security & Threat Model](<https://linear.app/paperos/document/paperos-security-and-threat-model-51fd5fd8929c>), [Execution Schedule](<https://linear.app/paperos/document/paperos-execution-schedule-1fa3d38d6795>), [Golden Path](<https://linear.app/paperos/document/new-app-in-ten-minutes-the-golden-path-0f49429f566e>) when relevant; (2) the issue body sections, linked `specs/**` files, `CLAUDE.md`, character memory (PAP-109), the last two Linear comments, the ADRs touched. The playbook links each document and says in one line what to take from it.
* Reporting: one `Session started` comment (worktree, branch, character, model), progress comments at most every 30 minutes, one `Session ended` comment (PR, gates, cost). Every comment ends with a fenced ```` ```paperos-session ```` JSON block.
* Footer schema: `{ playbookVersion: 1, sessionId, character, issue, status: "started" | "progress" | "ended" | "partial" | "contract-failed" | "handoff", costUsd, turns, pr?, branch, baseBranches?, handoff? }`. `handoff` is defined by PAP-108 and referenced by `$ref`; `baseBranches` echoes the `BASE_BRANCHES` prompt variable set by PAP-96 promotion (omitted when empty).
* Stop conditions: no linked spec (comment `needs-spec`), claimed by another session, budget warning from PAP-111, Justin comment (acknowledge first).
* **Umbrella rule.** An issue with sub-issues is an umbrella. It is never moved to Ready for Claude and never claimed; the orchestrator skips it and the validator returns error `UMBRELLA_NOT_CLAIMABLE`. Children are claimed like any issue. When all children are Done, the session that finishes the last child runs the umbrella's integration test, attaches the evidence to the umbrella and moves it to In Review. The playbook carries this paragraph verbatim in its claim step and in the FAQ ("Why can I not claim PAP-67?"). Relations: every child carries the external `blocks` relations it needs (added 2026-09-17, FIX-3), so a child in Ready for Claude is genuinely unblocked; the last child in build order also blocks whatever the umbrella blocks, so downstream readiness follows the real work.
* **How your issue got to Ready.** Nobody hand-picks issues for you. An issue reaches `Ready for Claude` in exactly one of two ways: Justin moved it (rare, and PAP-93 validates it anyway), or the orchestrator's promotion pass (PAP-96, Spec "Promotion") moved it because all four checks held: no `Deferred` label and no deferral note; no sub-issues (umbrellas are never promoted); every inbound `blocks` issue is `Done`, `Canceled`, or `In Review` with an open PR (the **branch-start rule**, Execution Schedule §1: a dependent may start once every blocker is In Review with a PR open and works against the PR branch); and the issue contract (PAP-93) passes with no errors, `BLOCKED_BY_OPEN` included (`BLOCKED_BY_OPEN` = an inbound blocker in Backlog, Todo, Ready for Claude, In Progress or Needs Justin, or In Review without a PR). The promotion comment on your issue reads `promoted: blockers PAP-x (Done), PAP-y (In Review, branch feat/PAP-y)` and your prompt carries `BASE_BRANCHES=feat/PAP-y,...` for every blocker that is still In Review. **Orient step therefore adds:** read the `promoted:` comment; for each branch in `BASE_BRANCHES` run `git merge --no-ff origin/<branch>` into your worktree before writing code (conflict → stop with `status: "ended", reason: "base-branch-conflict"`, comment, and the orchestrator routes to Needs Justin); list the base branches in your `Session started` footer (`baseBranches`); when a base PR merges before you open yours, rebase onto `main` (you own the rebase); when a base PR is closed without merge, PAP-93 bounces your issue and you stop with `status: "partial"`. **Manual fallback 09-17..09-20 (before PAP-96 is live, scheduled 09-20 pm):** Atlas runs `pnpm linear:promote --dry-run` from the orchestrator repo (`imagine-os/paperos-orchestrator`, script `src/cli/promote.ts` specified in the PAP-96 promotion package) at each half-day boundary (03:30Z and 15:30Z), reads the candidate table, and applies it by hand: move each listed issue to `Ready for Claude`, post the `promoted:` comment verbatim from the table, and put the table's `BASE_BRANCHES` line into the session prompt when launching. Until the orchestrator repo exists (PAP-96 is claimed 09-19), Atlas produces the same table by hand from the Linear `blocks` graph with the four checks above and records it as a comment on PAP-96 (`manual promotion 09-17 pm: PAP-16 (PAP-13 In Review, branch feat/PAP-13), ...`). The playbook carries this paragraph verbatim and the FAQ entry "My issue is in Backlog and its blockers are done, why is it not Ready?" (answers: Deferred label, sub-issues, an In Review blocker without a PR, or a contract error; check the `pnpm contract:audit --state Backlog` row).

**Interface contract**

* Provides: `session-footer.schema.json` and type `SessionFooter` (`packages/agents/src/session-footer.ts`), the comment templates `templates/session-{started,progress,ended}.md`, `playbookVersion` constant.
* Consumers: PAP-96 parses the footer to set state; PAP-97 and PAP-98 read `status` and `costUsd`; PAP-105 `linear-update` renders the templates; PAP-104 prompts point at `.claude/rules/session-playbook.md`; PAP-93 validator accepts `status: "contract-failed"`.
* Requires: nothing at runtime.

**Definition of done**

* Both copies identical (CI diff check in gate 1).
* A `claude -p` dry run given only the playbook and a toy issue produces three comments whose footers validate against the schema.
* Every "must" sentence has a check named beside it (Sentinel review).
* Linked from the repo README until the docs engine (PAP-128) renders it; changelog entry; Linear comment with the transcript.
* The playbook states the Umbrella rule verbatim (never claim an umbrella; last child's session runs the integration test and moves the umbrella to In Review).
* The playbook links every document in the Blueprint section "Documents (read in this order)" (Blueprint, Contracts, Threat Model, Roster and the nine character sheets, Execution Schedule, Golden Path, the pending-issue documents) and states the umbrella, promotion and deferred rules verbatim: umbrella (above); promotion (how a Backlog issue reaches Ready for Claude when its blockers are Done or In Review with a PR, the branch-start rule, PAP-96 promotion package and PAP-93 `BLOCKED_BY_OPEN`); deferred (an issue with the `Deferred` label or a "deferred" note in its body is never claimed and never promoted until Justin removes the deferral).
* The section "How your issue got to Ready" states the four promotion checks, the branch-start rule, the `BASE_BRANCHES` merge procedure in the orient step and the manual fallback for 09-17..09-20 (Atlas runs `pnpm linear:promote --dry-run` and applies the list by hand); Sentinel checks that its wording matches PAP-96 Spec "Promotion" and PAP-93 `BLOCKED_BY_OPEN` word for word where they define the same thing.

**Test plan**

* Unit: `ajv` validation of the schema against 10 valid and 10 invalid footers (including two with `baseBranches`); word-count test 1500-2500 (the promotion section counts; trim the FAQ before trimming it).
* Integration: script `scripts/playbook-dryrun.ts` runs the toy session and asserts three comments parse.
* Docs lint: every relative link resolves; mermaid renders in Storybook docs page.
* No visual breakpoints; the document is read in Linear and the repo.

**Demo**

Open the playbook, run `pnpm playbook:dryrun`, watch three comments appear on the toy issue and `pnpm footer:validate` print `ok` for each. Under two minutes.

**Edge cases**

* Context compacted mid-task: the last footer is the recovery point; playbook says re-read it.
* Two sessions claim one issue: check assignee and last `Session started`; later session exits with `status: "ended", reason: "duplicate-claim"`.
* Crashed worktree exists: reuse if branch matches, else suffix `-2`.
* Budget cap with uncommitted work: commit `wip:`, push, comment `partial`, stop.
* Justin comments mid-session: highest priority, acknowledged in the next comment.
* Prompt carries `BASE_BRANCHES` but a branch no longer exists on origin (PR merged and branch deleted): skip the merge, note it in the `Session started` comment, continue on `main`.

**Dependencies**

None (`readyNow`). Blocks PAP-96. Consumed by PAP-104, PAP-105, PAP-108.

*Round 4 critique fix (2026-09-18):* An umbrella's dependents are also blocked by its last child in build order: for every `P blocks D` the last child carries `Clast blocks D` (skipped only where it would create a cycle, a milestone inversion or a deferred -> scheduled edge), so the promotion pass gates D on the real work; the umbrella itself reaches In Review when that last child does.

**Agent**

Built by Quill (lead); reviewed by Atlas for operational fit.

**Size**

S
