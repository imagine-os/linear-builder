---
identifier: "PAP-93"
title: "Define the issue contract (spec link, acceptance criteria, surfaces, definition of done) enforced by a Linear webhook validator"
project: "pm-linear"
projectName: "Project Management & Claude Pipeline"
phase: "P0"
type: "Spec"
priority: 1
surfaces: ["Agent"]
milestone: "Linear configured for the pipeline"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-91"]
blocks: ["PAP-306", "PAP-307", "PAP-465"]
key: "pm-linear/issue-contract"
url: "https://linear.app/paperos/issue/PAP-93/define-the-issue-contract-spec-link-acceptance-criteria-surfaces"
source: "Linear snapshot 2026-09-17T15:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T13:41:16.934Z"
model: "claude-fable-5-1"
effort: "high"
---

# PAP-93: Define the issue contract (spec link, acceptance criteria, surfaces, definition of done) enforced by a Linear webhook validator

**Model / Effort:** Fable 5.1 (`claude-fable-5-1`) / high — keystone spec: issue contract

**Goal**

Define what an issue must contain before a machine may build it, and enforce it with a webhook validator that bounces non-conforming issues out of `Ready for Claude` with a comment listing exactly what is missing. The rules must match the live workspace, so the 206 issues already in the queue pass unchanged.

**Scope**

* In: `docs/pm/issue-contract.md`; pure validator `src/contract/validate.ts` in the orchestrator repo; webhook handler; fixtures; `pnpm contract:audit` over the whole team.
* Out: workspace configuration (PAP-91), bulk fixes of existing issues (none planned: PAP-91 treats the live workspace as correct), drafting help for humans (PAP-307).

**Spec**

* Required sections, bold headings or `##`, any order (order mismatch warns): Goal, Scope, Spec, Definition of done, Edge cases, Dependencies, Agent, Size. Recommended, warn if absent: Interface contract, Test plan, Demo. Optional `Files:` glob lines in Scope for PAP-99.
* Metadata rules aligned with reality: exactly one `Phase/*`, exactly one `Type/*`, at least one surface label from `Customer | Staff | Developer | Agent`, `Character/*` optional until PAP-91 lands then warning, Size read from the description (`S | M | L`), Linear estimate not required, project required. Spec link (`specs/**/*.spec.yaml` or a Linear document) required only for `Type/Build` issues whose Scope names a route; warning until 2026-09-22, error after (`--strict` date in config).
* `validateIssue(issue): ContractResult = { ok, violations: [{ code, severity: "error" | "warn", message, fix }] }`. Codes: `MISSING_SECTION`, `EMPTY_SECTION`, `BAD_SIZE`, `LABEL_PHASE`, `LABEL_TYPE`, `LABEL_SURFACE`, `NO_PROJECT`, `NO_SPEC_LINK`, `BLOCKED_BY_OPEN` (error), `READY_BUT_BLOCKED` (error), `UMBRELLA_NOT_CLAIMABLE` (error), `DESCRIPTION_TOO_LONG`.
* `BLOCKED_BY_OPEN` (error): at least one inbound `blocks` relation comes from an **open** issue. An inbound blocker is open exactly when it is in `Backlog`, `Todo`, `Ready for Claude`, `In Progress` or `Needs Justin`, or in `In Review` without an open PR (no PR attachment and no `gh pr list --head <branch>` hit); it is closed when it is `Done`, `Canceled`, or `In Review` with a PR (the branch-start rule, Execution Schedule §1). The check applies to an issue in any state and is the predicate PAP-96 promotion (`promote()`, `pnpm linear:promote`) evaluates on every Backlog candidate: an issue with a `BLOCKED_BY_OPEN` error is not promoted. `fix` text lists each open blocker with its state and PR status and the two remedies: wait for the blocker to reach In Review with a PR (or Done), or soften the dependency (delete the relation and write the soft dependency with its fallback into Dependencies). On the webhook path (issue moved to Ready) the error bounces the issue to `Backlog` like any other; on the promotion path it only keeps the issue in Backlog and posts nothing; `pnpm contract:audit --state Backlog` reports it per issue, and the Backlog issues with zero errors are exactly the ones PAP-96 promotes on its next cycle. Was an undefined warning; made an error and defined 2026-09-17 (FIX-8).
* `READY_BUT_BLOCKED` (error): the issue is in `Ready for Claude` and `BLOCKED_BY_OPEN` holds (same definition of open: Backlog, Todo, Ready for Claude, In Progress, Needs Justin, or In Review without an open PR). Kept as a separate code so the bounce comment and the audit table distinguish "never promoted" (`BLOCKED_BY_OPEN` on a Backlog issue) from "promoted or hand-moved, then blocked again" (`READY_BUT_BLOCKED`). Invariant: the Ready set contains only unblocked issues. The `fix` text lists each blocker with its state and offers the two remedies: finish the blocker, or soften it (delete the relation and write the soft dependency with its branch-import fallback into the Dependencies section, as PAP-161 does for PAP-279). On the webhook path the issue is moved back to `Backlog` like any other error; `pnpm contract:audit` reports every violation across the team. Added 2026-09-17 (FIX-2), when PAP-279 and PAP-161 were the two offenders.
* Handler on `Issue.update` to `Ready for Claude`: errors move the issue to `Backlog`, add label `needs-contract`, post the violations comment; warnings comment only. If the last actor is Justin, comment but never move.
* Results stored in `contract_checks(issue_id, checked_at, ok, violations_json)`.
* `UMBRELLA_NOT_CLAIMABLE` (error): the issue has at least one sub-issue (`children.nodes.length > 0`) and is in `Ready for Claude`, `In Progress` or is the target of a claim. **Umbrella rule.** An issue with sub-issues is an umbrella. It is never moved to Ready for Claude and never claimed; the orchestrator skips it and the validator returns error `UMBRELLA_NOT_CLAIMABLE`. Children are claimed like any issue. When all children are Done, the session that finishes the last child runs the umbrella's integration test, attaches the evidence to the umbrella and moves it to In Review. The `fix` text lists the children with their states and names the first child in build order (the child with no sibling blocker) as the thing to claim instead. On the webhook path the umbrella is moved back to `Backlog` like any other error, without a `needs-contract` label (the issue is well-formed, only unclaimable). Added 2026-09-17 (FIX-3); the 16 split parents PAP-19, 20, 21, 28, 35, 36, 45, 54, 57, 59, 65, 67, 81, 82, 85, 88 are the current umbrellas.

**Interface contract**

* Provides: `validateIssue`, `parseSections(markdown): Record<Section, string>`, `parseFilesGlobs(scope): string[]`, type `ContractResult`, the `needs-contract` label id, comment template `templates/violations.md` with footer `status: "contract-failed"`.
* Consumers: PAP-96 re-validates before claiming and calls `validateIssue` on every Backlog promotion candidate (promotion requires zero errors, `BLOCKED_BY_OPEN` included; the two implementations of "open" must agree, PAP-96 logs `promotion.validator_mismatch` otherwise); PAP-99 uses `parseFilesGlobs`; PAP-118 and PAP-307 call `validateIssue` before creating issues; PAP-306 runs `contract:audit`.
* Requires: state and label ids from `linear-workspace.json` (PAP-91), webhook receiver from PAP-97 (minimal receiver shipped here if PAP-97 is later).

**Definition of done**

* Fixture suite of 12 good and 20 bad issues passes; `validate.ts` coverage above 95 percent.
* `BLOCKED_BY_OPEN` fixtures pass (six cases in the Test plan) and `pnpm contract:audit --state Backlog` prints the pre-promotion list: every Backlog issue with its error codes, so the zero-error rows are the ones PAP-96 will promote next cycle; the table for the live team is posted here.
* `pnpm contract:audit` on all live PAP issues reports zero errors (warnings allowed) and the table is posted here.
* Live bounce of a deliberately bad issue within 10 seconds, recording attached; a good issue is untouched.
* Contract doc published; `PaperOS Spec` template matches the section names.
* Changelog entry; Linear comment with the audit table and recording.

**Test plan**

* Unit: each violation code has a pass and fail fixture; heading normalisation (`**Goal**` vs `## Goal`); 50 k character truncation. `READY_BUT_BLOCKED`: a Ready issue with a Backlog blocker fails; the same issue passes once the blocker is Done or the relation is removed; a blocker In Review with an open PR passes (branch-start rule).
* `BLOCKED_BY_OPEN`: a Backlog issue with a Todo blocker fails (error); with a Needs Justin blocker fails; with an In Progress blocker fails; with an In Review blocker without a PR fails; with an In Review blocker with a PR passes; with every blocker Done or Canceled passes; with no inbound blockers passes; an outbound `blocks` relation never triggers it. `isOpen(blocker)` is exported and PAP-96's promotion test imports it so the two agree by construction.
* Integration: replay of 30 recorded webhook payloads including duplicate deliveries yields one comment each.
* e2e: live bounce on a `contract-test` labelled issue, then cleanup by moving it back.
* No visual breakpoints; comment rendering checked in Linear web and mobile app screenshots.
* `UMBRELLA_NOT_CLAIMABLE`: an issue with two Backlog children moved to Ready fails and is bounced to Backlog; the same issue with all children Done and an integration-test attachment moved to In Review passes; a leaf issue never triggers the code.

**Demo**

Move a fixture issue with a missing Definition of done to `Ready for Claude`; within ten seconds it returns to `Backlog` with a comment naming `MISSING_SECTION` and the fix. Then add the section and move it again: silence. One minute.

**Edge cases**

* Validator's own bot moves an issue: ignore by `actor.id`.
* Sub-issue whose parent has a spec link: inherits `NO_SPEC_LINK` satisfaction.
* Sections in a foreign heading style (`Goal:` plain): `MISSING_SECTION` with a fix pointing to the template.
* Size given as `Small`: normalise to `S`.
* Webhook delivered twice: idempotent by `webhookId`.
* Blocker moves to Done while the dependent sits in Ready: nothing to do; blocker moves back from Done to In Progress: re-validate every Ready dependent and bounce with `READY_BUT_BLOCKED`.
* Blocker moves to Done or In Review-with-PR while the dependent sits in Backlog: nothing to do here; PAP-96 promotion picks the dependent up on its next cycle (or Atlas via `pnpm linear:promote --dry-run` before 09-20).
* Blocker is In Review and its PR is closed without merge: it becomes open again; PAP-97's `pr.closed` event triggers re-validation of the dependents and `READY_BUT_BLOCKED` bounces the promoted ones.

**Dependencies**

Blocked by PAP-91. Soft: PAP-97. Consumed by PAP-96 (claim re-validation and promotion check 4), PAP-99, PAP-118.

**Agent**

Built by Atlas (Decomposer sub-agent); reviewed by Sentinel.

**Size**

M
