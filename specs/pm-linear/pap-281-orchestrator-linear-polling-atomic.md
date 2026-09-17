---
identifier: "PAP-281"
title: "Orchestrator: Linear polling, atomic claim and state transitions"
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
blockedBy: ["PAP-46", "PAP-91", "PAP-92"]
blocks: ["PAP-282", "PAP-283"]
key: "pm-linear/orchestrator/claims"
url: "https://linear.app/paperos/issue/PAP-281/orchestrator-linear-polling-atomic-claim-and-state-transitions"
source: "Linear snapshot 2026-09-17T13:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T13:06:08.801Z"
---

# PAP-281: Orchestrator: Linear polling, atomic claim and state transitions

**Goal**

Build the half of the orchestrator that talks to Linear: the poll loop that reads `Ready for Claude`, the atomic claim that assigns and moves an issue, the state transitions to `In Review`, `Ready for Claude` (retry) and `Needs Justin`, the `linearComment()` helper and the database tables everything else records into.

**Scope**

* In: repo skeleton `imagine-os/paperos-orchestrator` (Node 22, pnpm, Biome, Vitest, Drizzle), `src/linear/`, `src/db/` with migrations, `src/loop.ts` with a pluggable `pickNext()` (FIFO by priority then age until PAP-99), `linearComment()`, config loading.
* Out: worktrees and sessions (PAP-282), HTTP and deployment (PAP-283), webhooks (PAP-97).

**Spec**

* Poll every `pollIntervalMs` (30 s): `issues(filter: { team: { key: { eq: "PAP" } }, state: { name: { eq: "Ready for Claude" } }, assignee: { null: true } })` ordered by priority, then `createdAt`; also callable by `loop.wake()` from webhooks.
* Claim: insert `claims(issue_id, session_id, updated_at_seen)` inside `SELECT ... FOR UPDATE SKIP LOCKED`; then `issueUpdate({ assigneeId: botUser(character), stateId: IN_PROGRESS })`; re-read and compare `updatedAt` to `updated_at_seen`; on mismatch release the claim.
* Transitions: `toInReview(issue, prUrl)` adds the attachment; `retry(issue, n)` sets `Ready for Claude` and label `retry-<n>` (max two); `escalate(issue, reason)` sets `Needs Justin` with a PAP-94 card.
* Tables: `sessions`, `claims`, `events`; SQLite in dev, Postgres schema `orchestrator` in production; ids from `linear-workspace.json` (PAP-91).
* `linearComment(issueId, body, footer)` appends the PAP-92 footer, dedupes on `(issue_id, sha256(body))` in `comments_sent`, retries on `RATELIMITED` after 60 s.

**Interface contract**

* Provides: `claimNext(character?): Claim | null`, `release(claim)`, `toInReview`, `retry`, `escalate`, `linearComment`, `linear.ids` (typed `WorkspaceIds`), tables above, `events.emit("issue.claimed" | "issue.released")`.
* Consumers: PAP-282 (claims to launch), PAP-97 (`linearComment`, events), PAP-99 (replaces `pickNext`), PAP-108 (assignee switch), PAP-111 (`release` on hold).
* Requires: PAP-91 ids, PAP-92 footer schema, bot user ids (single default bot until PAP-48).

**Definition of done**

* Claim atomicity test: 20 concurrent `claimNext()` on one issue yields one winner.
* `updatedAt` guard test releases the claim when the issue moved.
* Transition tests against a mocked SDK; comment dedupe test; migrations apply on SQLite and Postgres.
* Live: an issue moved to `Ready for Claude` on the team is claimed within one poll and shows the bot assignee and `In Progress`; recording.
* Changelog; Linear comment.

**Test plan**

* Unit: query builder, priority ordering, footer append, dedupe hash, retry counter cap.
* Integration: Postgres via testcontainers for `SKIP LOCKED`; mocked SDK for transitions.
* e2e: live claim on a `rehearsal` issue, then release.
* No UI.

**Demo**

Run `pnpm dev`, move a rehearsal issue to `Ready for Claude`, watch the log print `claimed PAP-n` and Linear show `In Progress` with the bot assignee; stop the process and the claim row is released on restart. One minute.

**Edge cases**

* Linear down: pause claiming, exponential backoff, no crash.
* Issue reassigned by a human during claim: guard fails, skip.
* Two replicas: `SKIP LOCKED` ensures one winner.
* Comment body identical to a previous one: skipped silently, logged.
* Bot user missing: fall back to the default bot and warn.

**Dependencies**

Blocked by PAP-91, PAP-92 (through the parent). Blocks the two sibling children.

**Agent**

Built by Atlas (Dispatcher sub-agent); reviewed by Sentinel.

**Size**

M
