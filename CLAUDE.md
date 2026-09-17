# PaperOS Core Platform: brief for a Claude Code session

You are one of the nine PaperOS agent characters picking up an issue from Linear team **PAP** (https://linear.app/paperos). This repository holds the plan; the code lives in the repositories the issue names (`imagine-os/paperos-template`, `imagine-os/paperos-orchestrator`, ...). Justin Massion is the only human; he approves `Needs Justin` cards and nothing else.

**Linear is the system of record.** The files here are snapshots of Linear content. If a spec here and the issue in Linear disagree, the issue wins; note the drift in a comment on the issue.

## Read first, in this order

1. `docs/blueprint.md` (Blueprint: vision, decisions, phases, budget, project index)
2. `docs/interface-and-data-contracts.md` (the shapes every project codes against; changing one needs an ADR, PAP-130)
3. Your project's `Contract` section: the project content in Linear (project list: `plan/plan.json` `projects[]`)
4. `docs/agent-roster.md`, then your character sheet in `docs/characters/` (routing, tools, access, refusal rules)
5. `docs/security-and-threat-model.md` (§4 is the Linear deny list: never archive or delete anything, never move to Done or Canceled, never touch PAP-1..PAP-12 or views)
6. `docs/execution-schedule.md` (your start day, milestone dates, the branch-start rule, the Needs Justin table)
7. `docs/new-app-in-ten-minutes.md` (the golden path the whole platform serves)

Then read your issue in Linear end to end, including its Dependencies section and every issue it links.

## Where specs live

* `specs/<project-key>/<slug>.md`: one file per canonical PAP issue with frontmatter (identifier, project, phase, type, priority, state, blockedBy, blocks, URL). Index: `specs/README.md`. Every spec has the eight contract sections: Goal, Scope, Spec, Interface contract, Definition of done, Test plan, Demo, Dependencies (plus Size).
* `docs/pending/<project-key>/<slug>.md`: historical spec text of the 156 round-2 pending issues. All of them were created in Linear on 2026-09-17 as PAP-280..PAP-432 (153 issues; the other 3 stayed folded into live issues as work packages) and are normal issues now, claimable like any other. The live Linear description (mirrored in `specs/`) wins over the pending file; `docs/pending/README.md` maps each `[project/key]` citation to its identifier. Team PAP holds 428 issues, 28 of them in Ready for Claude. For a folded work package, build it on a branch `<parent>/wp<n>-<slug>`.
* `plan/round2/changes/`: every Linear mutation made while planning, one log per agent and per fix. Use them to understand why a relation or paragraph exists.

## Pipeline states

| State | Meaning |
|---|---|
| `Backlog` | Specified, waiting on blockers. The orchestrator's promotion pass moves it forward; you do not. |
| `Ready for Claude` | Spec-complete and unblocked. The only state you may claim from. |
| `In Progress` | Claimed by exactly one session, working in a git worktree on branch `feat/PAP-n-<slug>`. |
| `In Review` | A PR exists; Sentinel's gates and reviewers run. Dependents may start against the PR branch (branch-start rule). |
| `Needs Justin` | A human decision is required; the card says what and offers `/approve` or `/reject`. Nothing else waits on it unless the card says so. |
| `Done` | Merged and verified. Only the merge flow moves issues here, never a session by hand. |

`Todo` exists as human parking and is never polled. Move your issue only along `Ready for Claude → In Progress → In Review`; anything else goes through a comment.

## Rules every session obeys

* **Umbrella rule.** An issue with sub-issues is an umbrella. Never claim it and never move it to Ready for Claude (validator error `UMBRELLA_NOT_CLAIMABLE`). Claim its children like any issue; every child carries the external `blocks` relations it needs. The session that finishes the last child runs the umbrella's integration test, attaches the evidence and moves the umbrella to In Review.
* **Deferred rule.** An issue carrying the `Deferred` label (the Execution Schedule v0.2 set, 28 issues) or a "deferred" note under Goal is never claimed and never promoted until Justin removes the deferral (NJ-14). If you find one in Ready for Claude, leave one comment `not claimable: labelled Deferred` and move on.
* **Model and effort rule.** A builder session runs on the model named by the issue's `Model` label (`Model: Fable 5.1`, `Model: Opus 5`, `Model: Sonnet 5`, `Model: Haiku 4.5`) at the reasoning effort named by its `Effort` label (`Effort: low|medium|high|max`, group `Reasoning effort`); the same values sit in the `**Model / Effort:**` line of the description and in the spec frontmatter (`model:`, `effort:`). If either label is missing, fall back to Sonnet 5 / medium. Reviewers and the QA gate follow the rule in `docs/cost-and-duration-estimate.md` section 4b (Opus 5 / high after an Opus or Fable builder, Sonnet 5 / high after a Sonnet builder; QA gate Haiku 4.5 / low). Umbrellas carry no Model or Effort label; their children do.
* **Promotion rule (how an issue reaches Ready).** Nobody hand-picks issues. The orchestrator (PAP-96) promotes a Backlog issue to Ready for Claude only when all four checks hold: no `Deferred` label or note; no sub-issues; every inbound `blocks` issue is `Done`, `Canceled`, or `In Review` with an open PR (the branch-start rule); and the issue contract (PAP-93) passes with no errors, `BLOCKED_BY_OPEN` included. The promotion comment lists the blockers and, for In Review blockers, the `BASE_BRANCHES` you merge into your worktree before starting. Until the orchestrator runs, Atlas applies `pnpm linear:promote --dry-run` by hand.
* **Claim exactly one issue**, from `Ready for Claude`, that routes to your character (roster routing rules). Re-check state and labels immediately before claiming; if someone else got it, pick the next.
* **Never** delete, archive, rename or re-state anything in Linear beyond your own issue's `In Progress → In Review` move and comments. Never touch PAP-1..PAP-12, views, labels or documents.
* Work in a worktree on the named branch; open the PR with the issue identifier in the title; attach the Definition-of-done evidence the spec asks for (recordings, gate artifacts); post one comment on the issue when you move it to In Review.
* Anything that needs a human (a paid account, a secret, a policy decision) becomes a `Needs Justin` card in the form the Execution Schedule table uses; it never blocks your own issue unless the spec says so.

## Tooling in this repository

`tools/linear/` holds the Python scripts that built the plan (GraphQL to `https://api.linear.app/graphql`, key from `LINEAR_API_KEY`, idempotent, never destructive). `tools/blueprint/` builds `site/index.html`. You will rarely need either while building an issue.
