---
identifier: "PAP-108"
title: "Design the handoff protocol between characters: artifact contract, Linear comment format, escalation to Needs Justin"
project: "agents"
projectName: "Agent Characters & Orgs"
phase: "P1"
type: "Spec"
priority: 1
surfaces: ["Agent"]
milestone: "Sub-agents, skills and evals live"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-94", "PAP-104", "PAP-105", "PAP-287"]
blocks: []
key: "agents/handoffs"
url: "https://linear.app/paperos/issue/PAP-108/design-the-handoff-protocol-between-characters-artifact-contract"
source: "Linear snapshot 2026-09-17T13:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T13:05:19.840Z"
model: "claude-sonnet-5"
effort: "high"
---

# PAP-108: Design the handoff protocol between characters: artifact contract, Linear comment format, escalation to Needs Justin

**Goal**

Specify how work passes cleanly between characters and sessions: what a finishing session leaves behind, how it is announced in Linear, how the receiver picks it up, and when and how anything escalates to `Needs Justin`. Clean baton passes stop the two most expensive failures: re-deriving context and silently dropping work.

**Scope**

* In: `docs/agents/handoff-protocol.md`, Zod `HandoffSchema` in `packages/agents/src/handoff.ts`, the `HANDOFF.md` template, `pnpm handoff lint`, three worked examples, orchestrator assignee switching.
* Out: decision card format (PAP-94, referenced), memory writes (PAP-109), notification delivery (PAP-136).

**Spec**

* A handoff is (1) code on a pushed branch, (2) `HANDOFF.md` at the worktree root, (3) the Linear comment whose PAP-92 footer carries `handoff: { kind, to, reason, artifacts: [{ type: branch | pr | doc | spec | screenshot, ref }], nextSteps[], openQuestions: [{ q, default }], contextFiles[] }`.
* Kinds: `build-to-review`, `review-to-build` (findings with severity, must-fix list), `spec-to-build`, `research-to-decision`, `escalate` (renders a PAP-94 decision card), `split` (proposed issue titles, sizes, dependencies in contract format), `crashed` (synthesised by the orchestrator).
* `HANDOFF.md` sections: Status, What changed, Decisions made, Verified, Not done, Next steps, Open questions (each with a default), Context files.
* `pnpm handoff lint` fails on missing sections, unpushed branch, open question without default, artifact referencing CI-only storage.
* Orchestrator: on a valid handoff comment, set assignee to `to`'s bot user, state per kind (`In Review` for build-to-review, `In Progress` for review-to-build), and queue the receiver.

**Interface contract**

* Provides: `HandoffSchema`, type `Handoff`, `validateHandoff()`, `renderHandoffComment()`, `lintWorktree(path)`, the `handoff` `$ref` used by PAP-92's footer schema, mapping `kind -> state`.
* Consumers: PAP-105 `linear-update` refuses invalid handoffs; PAP-96 switches assignee and state; PAP-94 receives `escalate`; PAP-110 grades handoff quality in Sentinel and Atlas tasks; PAP-81 reviewers emit `review-to-build`.
* Requires: PAP-104 characters and labels, PAP-92 footer, PAP-94 card format, PAP-105 script.

**Definition of done**

* Fixture tests for valid and invalid handoffs of every kind.
* `pnpm handoff lint` catches the four failure classes.
* Dry run: Nova builds a toy component, hands to Sentinel, Sentinel returns findings, Nova fixes and re-hands; four comments parse and the orchestrator switches assignee automatically (recording).
* One `escalate` dry run lands in `Needs Justin` as a decision card and is approved with `approve`.
* Doc reviewed by Atlas and Sentinel; changelog; Linear comment with recording.

**Test plan**

* Unit: schema per kind, `kind -> state` table, lint rules, `split` proposals validate against PAP-93 `validateIssue`.
* Integration: orchestrator handler on recorded comment webhooks; access cross-check refuses Beacon handing Stripe work to Iris.
* e2e: the four-comment dry run on staging.
* Visual: handoff comment rendering in Linear at 375 px (mobile) since Justin reads escalations on his phone.

**Demo**

In a toy worktree run `pnpm handoff lint` (fails on a missing default), fix it, run `pnpm skill linear-update handoff --to sentinel`, then watch the issue's assignee flip and state move to `In Review`. Ninety seconds.

**Edge cases**

* Receiver paused or over budget: handoff queues; Atlas notified after four hours.
* Session dies before posting: `crashed` synthesised from the last footer and `git status`, routed to the same character.
* Third disagreement round on one finding: auto-escalate with both positions.
* Artifact expired in CI: lint requires Linear or MinIO upload.
* Two open questions without defaults: blocked; handoffs must be actionable without a reply.

**Dependencies**

Blocked by PAP-104. Uses PAP-92, PAP-94, PAP-105.

**Agent**

Built by Atlas (lead) with Quill writing the document; reviewed by Sentinel.

**Size**

M
