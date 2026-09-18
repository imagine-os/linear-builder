---
identifier: "PAP-691"
title: "Orchestrator: Backlog to Ready for Claude promotion pass under the branch-start rule, `promotions` table, `BASE_BRANCHES` and `pnpm linear:promote`"
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
blockedBy: ["PAP-25", "PAP-46", "PAP-91", "PAP-92", "PAP-93", "PAP-281"]
blocks: ["PAP-97", "PAP-98", "PAP-99", "PAP-288", "PAP-300", "PAP-354", "PAP-471", "PAP-562"]
key: "r4/pm-linear/orchestrator-promotion-pass"
url: "https://linear.app/paperos/issue/PAP-691/orchestrator-backlog-to-ready-for-claude-promotion-pass-under-the"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:20:25.790Z"
model: "claude-opus-5"
effort: "high"
estimate: 3
dueDate: "2026-09-22"
cycle: null
---

# PAP-691: Orchestrator: Backlog to Ready for Claude promotion pass under the branch-start rule, `promotions` table, `BASE_BRANCHES` and `pnpm linear:promote`

**Model / Effort:** Opus 5 (`claude-opus-5`) / high — Build M

**Goal**

PAP-96 folds the promotion work package into PAP-281 "in the same session as the poll loop", which makes PAP-281 a two-session issue on the zero-slack orchestrator chain. This child lifts the package out: every poll cycle `promote()` moves Backlog issues whose blockers are Done, Canceled or In Review with an open PR into Ready for Claude, records the decision, tells the claiming session which branches to merge first, and gives Atlas the `--dry-run` table used by hand before the loop is live.

**Scope**

* In: `src/promote/{promote,checks,report}.ts` and `src/cli/promote.ts` in `imagine-os/paperos-orchestrator`, migration `promotions`, comment template `templates/promoted.md`, `BASE_BRANCHES` injection point in `renderPrompt` (PAP-282), `issue.promoted` event, README section "Promotion".
* Out: the poll and claim loop (PAP-281), scheduler ordering beyond the interim rule (PAP-99), the validator itself (PAP-93), umbrella closing (PAP-281 `UMBRELLA_CLOSE`).

**Spec**

* `promote({ dryRun, limit = 20, issue? })` scans team PAP `Backlog` paged 100 at a time and applies the four checks from PAP-96 Spec verbatim: no `Deferred` label or deferral note; no sub-issues; every inbound `blocks` issue is `Done`, `Canceled` or `In Review` with an open PR (attachment or `gh pr list --head <branch>`); `validateIssue()` (PAP-93) has no `error`, with `isOpen()` imported from PAP-93 so the two predicates cannot disagree (`promotion.validator_mismatch` logged otherwise).
* Per promoted issue: collect `BASE_BRANCHES` from In Review blockers in identifier order; insert `promotions(issue_id, promoted_at, blockers_json, base_branches_json, dry_run)` unique per open promotion; `issueUpdate` to Ready for Claude under the `updatedAt` guard; one `linearComment` `promoted: blockers PAP-x (Done), PAP-y (In Review, branch feat/PAP-y)` with footer `status: "promoted"`; emit `issue.promoted`.
* Ordering: least slack first when PAP-99 `scheduler.next()` exists, else milestone target date, priority, `createdAt`; never re-promote an issue PAP-93 bounced after its blockers last changed; never promote when the promotion would exceed `limit`.
* CLI `pnpm linear:promote [--dry-run|--apply] [--limit n] [--issue PAP-n] [--record]` prints the candidate table (issue, milestone, blockers with state and PR, validator, `BASE_BRANCHES`, verdict, reason); exit 0 ran, 2 Linear unreachable.
* Base-branch lifecycle: PAP-97 `pr.closed` without merge triggers re-validation of dependents promoted with that branch and bounces them; a merged base PR is dropped from `BASE_BRANCHES` at claim time.

**Interface contract**

* Provides: `promote()`, `PromotionReport`, table `promotions`, CLI `pnpm linear:promote`, event `issue.promoted`, prompt variable `BASE_BRANCHES`, template `promoted.md`.
* Consumes: PAP-281 Linear client, `linearComment`, ids and tables; PAP-93 `validateIssue` and `isOpen`; PAP-282 `renderPrompt`; PAP-97 `pr.closed`; PAP-99 `next()` (soft).

**Definition of done**

* Fixture graph `test/fixtures/promotion-graph.json` (chains A and B, Deferred `PAP-e`, umbrella `PAP-f`, In Progress blocker `PAP-g`, In Review without PR `PAP-h`, validator failure `PAP-i`): one pass promotes exactly `PAP-b` and `PAP-d` with the specified comments and `BASE_BRANCHES`; a second pass is a no-op; moving `PAP-c` back bounces `PAP-d`.
* `--dry-run` on the live team prints the table and changes nothing (recording); `--apply` on a rehearsal pair promotes within one cycle.
* Live: a Backlog issue whose only blocker moves to Done is Ready within two poll cycles; the claiming session's prompt shows `BASE_BRANCHES`.
* README section; changelog; Linear comment with the recording and the fixture table.

**Test plan**

* Unit: four checks individually, `isOpen` agreement test importing PAP-93, ordering rule, limit, `BASE_BRANCHES` order and pruning, comment template snapshot.
* E2E: mocked Linear graph end to end; live rehearsal pair on team PAP.

**Demo**

Run `pnpm linear:promote --dry-run`, read the candidate table, then `--apply --issue PAP-<rehearsal>` and watch the issue move to Ready for Claude with the `promoted:` comment. Under one minute.

**Edge cases**

* Justin moves an issue to Ready by hand while `promote()` runs: the `updatedAt` guard fails, his move stands, PAP-93 validates it.
* Blocker in Needs Justin: counts as open; the dry-run table names the card so Atlas sees what holds the chain.
* Linear rate limit mid-pass: stop the pass, resume next cycle from the cursor; promotions already written are not repeated.
* Validator unavailable (PAP-93 not merged): checks 1-3 plus local `parseSections`; report marked `validator: unavailable`.

**Dependencies**

Hard: PAP-281, PAP-93. Soft: PAP-282, PAP-97, PAP-99.

**Agent**

Builder: Atlas (Dispatcher). Reviewer: Sentinel (Code Reviewer).

**Size**

M: one session.
