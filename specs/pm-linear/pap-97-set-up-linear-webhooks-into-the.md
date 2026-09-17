---
identifier: "PAP-97"
title: "Set up Linear webhooks into the orchestrator and PR status back to Linear as comments with screenshots and review verdicts"
project: "pm-linear"
projectName: "Project Management & Claude Pipeline"
phase: "P0"
type: "Build"
priority: 1
surfaces: ["Agent"]
milestone: "Orchestrator claims and ships issues"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-96", "PAP-283", "PAP-303"]
blocks: ["PAP-101", "PAP-299", "PAP-307", "PAP-356", "PAP-372"]
key: "pm-linear/webhooks"
url: "https://linear.app/paperos/issue/PAP-97/set-up-linear-webhooks-into-the-orchestrator-and-pr-status-back-to"
source: "Linear snapshot 2026-09-17T13:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T13:06:19.228Z"
model: "claude-opus-5"
effort: "medium"
---

# PAP-97: Set up Linear webhooks into the orchestrator and PR status back to Linear as comments with screenshots and review verdicts

**Goal**

Make Linear the only window Justin needs: Linear events reach the orchestrator instantly, and every PR event, gate result, screenshot set and reviewer verdict is written back to the issue as one structured, edited-in-place status comment with images. Nobody opens GitHub or Forgejo to know how an issue is doing.

**Scope**

* In: inbound receivers `POST /webhooks/linear`, `/webhooks/github`, `/webhooks/forgejo` in the orchestrator (Hono); the persisted event bus; outbound PR attachment and status comment; screenshot upload policy.
* Out: contract decisions (PAP-93), decision replies (PAP-94), the gate artifacts themselves (PAP-239 defines them).

**Spec**

* Linear: verify `Linear-Signature` (HMAC-SHA256 of raw body), reject `webhookTimestamp` older than 60 s, dedupe by `webhookId`, dispatch on `type` and `action` to handlers registered with `events.on("linear.issue.update")`.
* GitHub and Forgejo: `X-Hub-Signature-256`; events `pull_request`, `check_suite`, `workflow_run`, `pull_request_review`; map PR to issue by the key in the branch name (PAP-46) or `Closes PAP-123` in the body.
* Outbound: `attachmentCreate` once per PR; a single status comment (id in `sessions.status_comment_id`) rendered from `templates/pr-status.md` and edited with 5 s debounce; up to seven screenshots (one per breakpoint from PAP-82), each resized under 2 MB with `sharp`, plus a link to the full set; reviewer verdicts from `security.json` and the review JSON block (PAP-239).
* Every event persisted to `orchestrator.events` with `source`, `delivery_id`, `payload`; `pnpm events:replay --since` re-renders comments.

**Interface contract**

* Provides: `registerWebhookHandler(source, type, action, handler)`, `events` emitter, `postPrStatus(issueId, PrStatus)` with `PrStatus = { pr: { url, number, state }, gates: Record<"gate1" | "gate2" | "gate3" | "gate4", "pending" | "pass" | "fail" | "skipped">, screenshots: { width, url }[], verdicts: Finding[] }`, `verifySignature(source, headers, rawBody)`.
* Consumers: PAP-93 and PAP-94 register handlers; PAP-101 reuses the Linear receiver; PAP-112 `@character` mentions; PAP-307 listens to `Issue.create` and `Comment.create`.
* Requires: PAP-96 service, sessions table and `linearComment()`; artifact schemas from PAP-239 (`gate1.json`, `visual.json`, `security.json`); screenshot naming `screenshots/<page>/<width>.png` from PAP-82.
* Contract source: [Interface & Data Contracts](<https://linear.app/paperos/document/paperos-interface-and-data-contracts-d40e6a4d227c>) §3 (the orchestrator is both a bus consumer and the producer of `issue.needs_justin`, `review.gate_failed`, `review.ready` and `release.candidate`; inbound Linear and Forgejo webhooks are normalised into the §3 envelope with `actor.type='service'`; delivery is at-least-once and handlers are idempotent on `event.id`); `PrStatus.gates` and `verdicts` are read from the PAP-239 `GateReport` artifacts (§6 row "Gate artifacts"); §6 row "Domain event envelope" (provider: pending contracts issue B; the `events` emitter here uses the same envelope so the swap is one import).

**Definition of done**

* Signature tests for all three sources, including tampered body and stale timestamp.
* Replaying 200 recorded events yields byte-identical status comments (snapshot).
* Live: open a PR on a toy repo, see attachment and status comment with screenshots within 60 s of CI finishing; recording attached.
* Duplicate delivery test shows one comment.
* Runbook section on secret rotation; changelog entry; Linear comment with recording.

**Test plan**

* Unit: signature verification, PR-to-issue mapping, debounce collapsing five events into one edit, image resize.
* Integration: recorded fixtures for each event kind through the bus into a mocked Linear client; idempotency on redelivery.
* e2e: toy repo PR on staging with gate artifacts uploaded by a stub workflow.
* Visual: status comment rendered in Linear web at 1280 px and Linear mobile at 375 px, both screenshotted.

**Demo**

Push a commit to a toy PR whose branch carries the issue key; within a minute the Linear issue shows the PR attachment and a status comment with gate badges and seven thumbnails. Ninety seconds.

**Edge cases**

* PR opened before any claim: link it, set `In Review`, note "no session record".
* One PR closes several issues: status comment on each.
* Upload fails: post links only, retry uploads in the background.
* GitHub and Forgejo fire for the same mirrored commit: dedupe by SHA and event kind.
* Comment deleted by a human: create a new one and store the id.
* Secret rotation: accept the previous secret for 24 hours.

**Dependencies**

Blocked by PAP-96 (hard). PAP-239 soft: PAP-97 ships its own `orchestrator-event.json` schema and adopts `packages/contracts` when it lands; the `blocks` relation from PAP-239 was removed on 2026-09-17 (round-2 FIX-1; PAP-239's milestone is 09-25, this one's is 09-22). Blocks PAP-101, PAP-307.

**Agent**

Built by Atlas (Dispatcher sub-agent); reviewed by Sentinel.

**Size**

M
