---
identifier: "PAP-94"
title: "Design the Needs Justin queue: batched decisions, one-click approve/reject comments, max five open items rule"
project: "pm-linear"
projectName: "Project Management & Claude Pipeline"
phase: "P0"
type: "Spec"
priority: 1
surfaces: ["Staff"]
milestone: "Linear configured for the pipeline"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-91"]
blocks: ["PAP-88", "PAP-108", "PAP-252", "PAP-254"]
key: "pm-linear/justin-queue"
url: "https://linear.app/paperos/issue/PAP-94/design-the-needs-justin-queue-batched-decisions-one-click"
source: "Linear snapshot 2026-09-17T15:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T13:41:17.097Z"
model: "claude-opus-5"
effort: "high"
---

# PAP-94: Design the Needs Justin queue: batched decisions, one-click approve/reject comments, max five open items rule

**Model / Effort:** Opus 5 (`claude-opus-5`) / high — Spec P0

**Goal**

Keep the only human reviewer's queue small and fast: `Needs Justin` holds at most five open items, each is a pre-digested decision card with one-word replies, defaults apply when he is silent, and anything a machine can decide is refused entry. This is what makes the rest of the plan safe to run unattended.

**Scope**

* In: `docs/pm/justin-queue.md` (admission rules), the decision card format, the reply grammar, the queue governor and daily digest in the orchestrator, the `queued-for-justin` overflow label.
* Out: the notification transport (PAP-136 delivers the digest later; until then the digest is a Linear comment), release-train specifics (PAP-88 consumes the grammar).

**Spec**

* Admission: release-candidate approval, irreversible actions (production deploy, data deletion), spend above `justinQueue.spendThresholdUsd` (default 500), external communication, credential grants, new characters. Refused: code review, test failures, library choices under the rubric.
* Decision card (issue description or comment): `Decision needed`, `Recommendation` (one sentence), `Options` (max 3 with cost and risk), `Deadline`, `Default if no answer` (applied after `defaultTimeoutHours: 48` unless `hard-block`), `Context links`.
* Reply grammar (first line of a comment by Justin): `approve`, `reject`, `option <n>`, `defer <n>d`, `ask: <question>`, multiple `PAP-123: approve` pairs. Regex first, LLM classification only on regex miss and only to ask a clarifying question, never to act.
* Governor in `src/justin/governor.ts`: counts open `Needs Justin`; the sixth item gets `queued-for-justin` and stays in its previous state; freeing a slot admits by priority then age. Digest `src/justin/digest.ts` at 14:00 UTC posted to a pinned `Justin digest` issue, under 3000 characters.
* Config in `orchestrator.config.yaml`: `justinQueue.maxOpen: 5`, `defaultTimeoutHours`, `digestCronUtc`, `spendThresholdUsd`.

**Interface contract**

* Provides: `requestDecision(card: DecisionCard): Promise<DecisionHandle>` and `onDecision(handle, cb)` from `src/justin/index.ts`; type `DecisionCard`, `Decision = { verb: "approve" | "reject" | "option" | "defer" | "ask", option?, days?, question? }`; `parseReply(text): Decision[]`; footer statuses `decision-requested | decision-applied`.
* Consumers: PAP-88 release approval, PAP-108 `escalate` handoffs, PAP-111 reserve release, PAP-96 refusal stops, PAP-307 single-question asks.
* Requires: comment webhooks from PAP-97 (poll fallback every 30 s reads comments on open `Needs Justin` issues), state ids from PAP-91.

**Definition of done**

* Doc published and linked from the playbook (PAP-92).
* Governor bounces the sixth item and admits on free slot within one poll (test with mocked SDK).
* Grammar fixture suite of 30 replies including typos (`aprove`) passes.
* Default application with fake clock tested; `hard-block` never auto-applies.
* Digest posted three consecutive days in staging; screenshots at 375 px (Linear mobile) and 1280 px.
* Changelog entry; Linear comment with screenshots.

**Test plan**

* Unit: `parseReply` table test (30 cases), governor slot arithmetic, deadline computed from the card comment's `createdAt`.
* Integration: end-to-end with `nock`-recorded Linear responses: request, reply, state transition, acknowledgement comment.
* e2e: one real decision card on a `rehearsal` issue answered by Justin; timing recorded.
* Visual: digest rendering in Linear mobile at 375 px and web at 1280 px.

**Demo**

`pnpm justin:request fixtures/deploy-decision.yaml` creates a card in `Needs Justin`; reply `option 2` in Linear; within 30 seconds the issue moves to `In Progress` with an acknowledgement naming option 2. Ninety seconds.

**Edge cases**

* Prose that matches nothing: reply with one `ask:` clarifying question, do not guess.
* `Urgent` item arriving at a full queue: bump the oldest non-urgent item to `queued-for-justin` with a comment.
* Justin edits the issue state instead of commenting: treat the state change as approval of the recommendation.
* Two cards for the same subject: dedupe by `card.key`.
* Reply on a closed card: acknowledge and ignore.

**Dependencies**

Blocked by PAP-91. Soft: PAP-97. Blocks PAP-88 (grammar).

**Agent**

Built by Atlas (lead); reviewed by Sentinel (Code Reviewer).

**Size**

M
