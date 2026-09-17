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
children: ["PAP-281", "PAP-282", "PAP-283"]
blockedBy: ["PAP-25", "PAP-46", "PAP-91", "PAP-92", "PAP-298"]
blocks: ["PAP-97", "PAP-98", "PAP-99", "PAP-288", "PAP-300", "PAP-354"]
key: "pm-linear/orchestrator"
url: "https://linear.app/paperos/issue/PAP-96/build-the-orchestrator-that-polls-ready-for-claude-spawns-one-claude"
source: "Linear snapshot 2026-09-17T13:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T13:06:19.348Z"
model: null
effort: null
---

# PAP-96: Build the orchestrator that polls Ready for Claude, spawns one Claude Code session per issue in a git worktree and moves states

**Goal**

Build the engine that turns Linear into running agents: a long-lived service that polls `Ready for Claude`, claims one issue per free slot, creates a git worktree, launches a Claude Code session configured for the issue's character, streams progress and moves the issue to `In Review` when a PR exists. This is the umbrella; the work is split into three children so cold sessions can finish each in one context window. The claim loop also owns **promotion**: it is the only thing that moves a Backlog issue to `Ready for Claude` once every blocker is Done, Canceled or In Review with a PR (the branch-start rule), so the queue refills after the 26 Ready issues drain without Atlas promoting by hand.

**Read first.** Read before coding: [Blueprint](<https://linear.app/paperos/document/paperos-core-platform-blueprint-0c2115fe48f1>) → [Interface & Data Contracts](<https://linear.app/paperos/document/paperos-interface-and-data-contracts-d40e6a4d227c>) → your project's `Contract` section (Linear project content) → your character sheet ([Roster](<https://linear.app/paperos/document/paperos-agent-roster-org-chart-and-character-index-fc7ea7f41ff3>)) → [Execution Schedule](<https://linear.app/paperos/document/paperos-execution-schedule-1fa3d38d6795>) for your start day and the branch-start rule. Also Contracts §3 (topics `agent.session.started|finished|blocked`, `agent.quota.exceeded`, `issue.needs_justin`, `review.*`) and §2 row "Agent principal"; [Security & Threat Model](<https://linear.app/paperos/document/paperos-security-and-threat-model-51fd5fd8929c>) §4 (deny list), §5 (broker placeholders, Linear key never leaves the orchestrator), §6 (only T0 rendered prompts and T1 Justin comments instruct an agent); Roster section "Routing: who picks up an issue"; Execution Schedule §1 for the branch-start rule the orchestrator must implement.

**Scope**

* Children (build in order):
  * PAP-281: Linear polling, atomic claim and state transitions.
  * PAP-282: worktree lifecycle and Claude session launch.
  * PAP-283: deployment, `/status` endpoint and runbook.
  * Promotion work package (lives inside PAP-281 and is built in the same session as the poll loop; if that child exists, claim the child): Backlog → Ready for Claude promotion under the branch-start rule, the `promotions` table, the `promoted:` comment, the `BASE_BRANCHES` prompt variable and the `pnpm linear:promote` CLI. Spec below under "Promotion".
* Out: webhook receiver (PAP-97), metering (PAP-98), scheduling beyond fixed `maxParallel` (PAP-99), the PM data model (PAP-100), sandboxing (PAP-280).

**Spec**

* Repo `imagine-os/paperos-orchestrator`: TypeScript, Node 22, pnpm, Biome, Vitest; Postgres schema `orchestrator` (SQLite via `better-sqlite3` in dev); config `orchestrator.config.yaml` validated with Zod (`maxParallel` default 4, `pollIntervalMs` 30000, `repos[]`, `characters` path).
* Package layout: `src/linear/`, `src/git/worktree.ts`, `src/session/{launch,prompt}.ts`, `src/loop.ts`, `src/db/`, `src/http.ts`.
* Everything posted to Linear goes through `linearComment()` which appends the PAP-92 footer and dedupes by `(issueId, sha256(body))`.
* Character resolution: `Character/*` label, else project default from `roster.json`, else `Needs Justin`.
* Claim filter: never claim an issue labelled `Deferred` (the Execution Schedule's v0.2 set, 28 issues on 2026-09-17; NJ-14 on 09-27 can reinstate one by removing the label). `claimNext()` adds `labels: { none: { name: { eq: "Deferred" } } }` to the Linear filter and re-checks the fetched issue's labels before writing the claim; a `Deferred` issue found in `Ready for Claude` is skipped with a `linearComment` `not claimable: labelled Deferred (Execution Schedule v0.2)` once per issue and left for PAP-93 to bounce. The same exclusion applies to promotion and to any stretch-pool claim until the label is gone.
* **Promotion (Backlog → Ready for Claude).** Every poll cycle, after the claim pass, `promote()` scans team PAP issues in `Backlog` (`state: { name: { eq: "Backlog" } }`, `first: 100`, paged) and moves a candidate to `Ready for Claude` only when all four checks hold:
  1. no `Deferred` label (label id from `linear-workspace.json`; the Execution Schedule v0.2 set) and no `deferred` note under Goal (PAP-92 deferred rule);
  2. no sub-issues (`children.nodes.length === 0`; an umbrella is never promoted, Umbrella rule above);
  3. every inbound `blocks` relation (`inverseRelations` filtered to `type: "blocks"`) comes from an issue that is `Done`, `Canceled`, or `In Review` **with an open PR** (a PR attachment on the blocker, or a `gh pr list --head <branch>` hit for its branch). This is the branch-start rule from Execution Schedule §1. An `In Review` blocker without a PR counts as open. Zero inbound blockers satisfies the check, so a `readyNow` Backlog issue is promoted on the first cycle;
  4. `validateIssue(issue)` (PAP-93) returns no `severity: "error"` violation; `BLOCKED_BY_OPEN` (error in PAP-93) is the same predicate as check 3 and must agree with it (a disagreement is logged as `promotion.validator_mismatch` and the issue is skipped). Until PAP-93 lands, `promote()` runs checks 1-3 plus a local `parseSections` requiring the eight PAP-93 sections and marks the report `validator: unavailable`.
     For each promoted issue the orchestrator: (a) collects the branch name of every `In Review` blocker into `BASE_BRANCHES` (comma-separated, deterministic order by identifier; empty when every blocker is Done or Canceled) and stores it with the `promotions(issue_id, promoted_at, blockers_json, base_branches_json, dry_run)` row (unique on `issue_id` while the issue stays promoted; a PAP-93 bounce clears it so re-promotion is allowed after a blocker changes state); (b) sets `stateId` to `Ready for Claude` under the same `updatedAt` guard as claiming; (c) posts exactly one `linearComment` in the form `promoted: blockers PAP-x (Done), PAP-y (In Review, branch feat/PAP-y)` or `promoted: no blockers`, footer `status: "promoted"`; (d) emits `issue.promoted`. At claim time `launchSession` injects `BASE_BRANCHES=<list>` into the session prompt; the session (PAP-92 orient step) creates its worktree from `main`, merges each base branch (`git merge --no-ff origin/<branch>`; a conflict stops the session with `status: "ended", reason: "base-branch-conflict"` and `Needs Justin`), and owns the rebase when the base PRs merge. Ordering and limits: at most 20 promotions per cycle, least slack first (PAP-99 `scheduler.next()` when present; before that milestone target date, then priority, then `createdAt`). Never re-promote an issue that PAP-93 bounced (`contract_checks` row with `ok: false` newer than the last blocker state change). `Deferred` issues are also excluded from any stretch-pool promotion until the label is gone.
* `pnpm linear:promote [--dry-run | --apply] [--limit n] [--issue PAP-n]` (`src/cli/promote.ts`) runs one promotion pass outside the loop. `--dry-run` is the default: it prints a table (issue, milestone, inbound blockers with state and PR/branch, validator result, `BASE_BRANCHES`, verdict) and writes nothing to Linear or the database (rows go to `promotions` with `dry_run: true` only when `--record` is passed). `--apply` performs (a)-(d) above. Atlas runs the dry run by hand each half-day 09-17..09-20 and applies the list manually (PAP-92 "How your issue got to Ready"); from 09-20 pm the loop runs `promote()` every cycle and the CLI stays as the operator tool. Exit code 0 when the pass ran, 2 when Linear was unreachable.
* Completion: PR detected on the branch sets `In Review` with an attachment; no PR after the session ends re-queues with `retry-<n>` up to two times, then `Needs Justin`.
* Claims: the poll never claims an issue that has sub-issues. **Umbrella rule.** An issue with sub-issues is an umbrella. It is never moved to Ready for Claude and never claimed; the orchestrator skips it and the validator returns error `UMBRELLA_NOT_CLAIMABLE`. Children are claimed like any issue. When all children are Done, the session that finishes the last child runs the umbrella's integration test, attaches the evidence to the umbrella and moves it to In Review. `pickNext()` filters `children.nodes.length === 0` before ordering; when the last child of an umbrella reaches Done, the orchestrator appends `UMBRELLA_CLOSE: <parent identifier>` to that session's prompt so the session runs the parent's integration test (the parent's Definition of done and Test plan), attaches the evidence to the parent and moves the parent to In Review; if the session ends without doing so, the orchestrator posts `umbrella-close pending` on the parent and re-queues one `umbrella-close` session against the parent (this is the only case in which a session is launched on an umbrella, and it must not change any child).

**Interface contract**

* Provides: tables `sessions(id, issue_id, character, model, worktree, branch, status, started_at, ended_at, footer_json)`, `claims(issue_id, session_id, claimed_at, updated_at_seen)`, `events(id, session_id, kind, payload, at)`; module API `claimNext()`, `launchSession(claim)`, `linearComment(issueId, body, footer)`; HTTP `GET /healthz`, `GET /status` returning `SessionStatus[]` as defined by PAP-288; typed event emitter `events.on("session.started" | "session.ended" | "issue.claimed" | "pr.detected")`.
* Promotion provides: `promote(opts: { dryRun: boolean; limit?: number; issue?: string }): PromotionReport` (`{ candidates: [{ issue, blockers: [{ identifier, state, pr?, branch? }], validator, baseBranches, verdict: "promoted" | "skipped" , reason? }] }`), table `promotions`, CLI `pnpm linear:promote`, event `issue.promoted`, prompt variable `BASE_BRANCHES` (read by PAP-92 orient step and PAP-104 prompt templates), comment template `templates/promoted.md`.
* Consumers: PAP-97 (event bus, sessions table), PAP-98 (`result` messages), PAP-99 (`scheduler.next()` replaces FIFO), PAP-111 (abort controller and pre-flight hook), PAP-113 (`/status`).
* Requires: PAP-91 ids, PAP-92 playbook path, PAP-46 branch policy, PAP-25 VPS, bundles from PAP-106 (falls back to default allowlist), bot users from PAP-48 (falls back to one bot user), `validateIssue` from PAP-93 for promotion check 4 (fallback: local `parseSections` and `validator: unavailable` in the report until PAP-93 lands).

**Definition of done**

* All three children Done and their DoDs met.
* Promotion package: on a fixture team, Backlog issues whose inbound blockers are all Done, Canceled or In Review with a PR are moved to `Ready for Claude` with the `promoted:` comment and a `promotions` row; an issue labelled `Deferred`, an umbrella with sub-issues, an issue with an In Progress blocker and an issue with an In Review blocker without a PR are left in Backlog with no comment; the promoted issue whose blocker is In Review receives `BASE_BRANCHES` in its session prompt. `pnpm linear:promote --dry-run` on the live team prints the candidate table and changes nothing (recording attached). Live: one Backlog issue on the team whose only blocker is moved to Done is in `Ready for Claude` within two poll cycles.
* Integration test across children: a `Ready for Claude` issue on a toy repo produces a worktree, a session, a PR, `In Review` and an attachment; restart mid-session marks `interrupted` and re-queues; recording attached.
* `roster.json` dry run consumes PAP-104 output.
* README runbook; changelog entry; Linear comment with recording and PR link.

**Test plan**

* Umbrella integration test `test/e2e/orchestrator.e2e.ts` with a mocked Agent SDK stream and a temp git remote: claim, launch, PR, state transitions, restart recovery. Runs in CI nightly.
* Live soak: two issues in parallel on staging for one hour, zero duplicate claims.
* `/status` visual check at 1280 px.
* Umbrella rule: fixture with an umbrella in Ready for Claude and two leaf children (one Ready, one Backlog) — `pickNext()` returns the Ready leaf and never the umbrella; marking the second child Done triggers exactly one `UMBRELLA_CLOSE` prompt and, if that session ends without moving the parent, exactly one re-queued `umbrella-close` session.
* Promotion fixture graph `test/fixtures/promotion-graph.json` (mocked Linear): chain A `PAP-a` Done → `PAP-b` Backlog; chain B `PAP-c` In Review with PR on `feat/PAP-c` → `PAP-d` Backlog; `PAP-e` Backlog labelled `Deferred` with every blocker Done; umbrella `PAP-f` Backlog with two Backlog children and every blocker Done; `PAP-g` Backlog with one blocker In Progress; `PAP-h` Backlog with an In Review blocker that has no PR; `PAP-i` Backlog with no blockers but a missing Definition of done (validator error). One `promote()` pass promotes exactly `PAP-b` and `PAP-d` and nothing else; the comment on `PAP-b` is `promoted: blockers PAP-a (Done)` and on `PAP-d` `promoted: blockers PAP-c (In Review, branch feat/PAP-c)`; `PAP-d`'s prompt carries `BASE_BRANCHES=feat/PAP-c` and `PAP-b`'s is empty; a second pass promotes nothing (idempotent); moving `PAP-c` back to In Progress then running PAP-93 bounces `PAP-d` and a third pass leaves it in Backlog; `--dry-run` on the same fixture lists the same two verdicts and every state and comment count is unchanged. Also: the umbrella's children are promoted when their own blockers are Done, the umbrella never.

**Demo**

Move a toy issue to `Ready for Claude`; within a minute `/status` shows a session, a branch appears on the forge, and after the session ends the issue is `In Review` with a PR attachment. Two minutes.

**Edge cases**

* Linear API down: keep running sessions, pause claiming, back off exponentially.
* Issue leaves `Ready for Claude` between poll and claim: `updatedAt` guard fails, skip.
* SDK refusal stop: record category, route to `Needs Justin`, do not retry.
* Two replicas: `SELECT ... FOR UPDATE SKIP LOCKED` on `claims`.
* Branch exists on origin: check out and rebase rather than fail.
* Label added after fetch: an issue labelled `Deferred` between poll and claim is caught by the pre-claim re-check, not by the `updatedAt` guard alone.
* Base PR closed without merge: PAP-97's `pr.closed` event triggers PAP-93 re-validation of every dependent promoted with that branch in `BASE_BRANCHES`; they are bounced to Backlog and promotion waits for the blocker to reach In Review again.
* Justin moves a Backlog issue to Ready for Claude by hand while `promote()` is running: the `updatedAt` guard fails, the promotion row is not written and Justin's move stands (PAP-93 will still validate it).
* Blocker in `Needs Justin`: counts as open; the candidate stays in Backlog and the dry-run table names the Needs Justin card so Atlas can see what is holding the chain.

**Dependencies**

Blocked by PAP-91, PAP-92, PAP-46, PAP-25. Soft: PAP-93 (`validateIssue` for promotion check 4; fallback in the Interface contract). Blocks PAP-97, PAP-98, PAP-99, PAP-288.

**Agent**

Built by Atlas (Dispatcher sub-agent) with Forge (Ops Runner) for deployment; reviewed by Sentinel.

**Size**

L (umbrella; children are M, M, S)
