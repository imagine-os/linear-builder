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
blockedBy: ["PAP-104", "PAP-105", "PAP-94"]
blocks: []
key: "agents/handoffs"
url: "https://linear.app/paperos/issue/PAP-108/design-the-handoff-protocol-between-characters-artifact-contract"
source: "plan/specs/bucket-3.json (round-1 canonical spec JSON)"
---

# PAP-108: Design the handoff protocol between characters: artifact contract, Linear comment format, escalation to Needs Justin

**Goal**

Specify how work passes cleanly between characters and sessions: what a finishing session must leave behind (the artifact contract), how it is announced in Linear, how the receiving character picks it up, and when and how anything escalates to `Needs Justin`. Clean baton passes stop the two most expensive failure modes: re-deriving context and silently dropping work.

**Scope**

In:
- `docs/agents/handoff-protocol.md` and the machine-readable `packages/agents/src/handoff.ts` (Zod schema for the handoff block).
- Artifact contract: a handoff consists of (1) code on a pushed branch, (2) a `HANDOFF.md` at the worktree root describing state, decisions, open questions, and next steps, (3) the Linear comment with the `paperos-session` footer extended by a `handoff` object: `{to: character, reason, artifacts: [{type: branch|pr|doc|spec|screenshot, ref}], nextSteps: [...], openQuestions: [...], contextFiles: [...]}`.
- Handoff kinds: `build-to-review` (builder to Sentinel: PR link, what to look at, known gaps), `review-to-build` (Sentinel to builder: findings with severity, must-fix list), `spec-to-build` (Quill to a builder: validated spec path, decisions made), `research-to-decision` (Scout to Atlas or Justin: ADR draft, recommendation), `escalate` (any character to Justin: decision card per `pm-linear/justin-queue`), `split` (any character to Atlas: proposed sub-issues when scope proves too large).
- Receiving rules: the orchestrator reads the `handoff.to` field, sets the Character label and assignee, and the next session's prompt includes `HANDOFF.md` and the handoff comment verbatim; the receiver's first comment acknowledges with `handoff.accepted: true` or rejects with a reason (goes to Atlas).
- Escalation criteria (shared list): irreversible or external-facing action, spend over cap, contradictory requirements between two issues, security finding of severity high or above, third failed attempt on the same issue, any request to change permissions or budgets.
- Timeouts: a handoff not accepted within 4 hours is re-posted to Atlas; a review handoff older than 24 hours raises priority.

Out: implementation of state changes (the orchestrator already handles them), notifications, cross-repo handoffs (single repo per issue by convention).

**Spec**

- `HANDOFF.md` template with sections: Status (one line), What changed, Decisions made (link ADRs), Verified (tests, screenshots), Not done, Next steps (ordered), Open questions (each with a proposed default), Context files (paths worth reading first).
- Footer `handoff` object validated by the `linear-update` skill before posting; invalid handoffs are refused so nothing half-formed lands.
- `split` handoffs must include proposed issue titles, sizes and dependencies in the contract format so the Decomposer can create them without re-reading the code.
- The protocol doc includes three worked examples (build-to-review, review-to-build with a blocking finding, escalate).
- Add a `pnpm handoff lint` command that checks a worktree's `HANDOFF.md` and the last comment before a session ends; the playbook's end checklist calls it.

**Definition of done**

- Schema tests: valid and invalid handoff fixtures for each kind.
- `pnpm handoff lint` catches a missing section, an unpushed branch and an unanswered open question without a default.
- Dry run: Nova builds a toy component, hands to Sentinel, Sentinel returns findings, Nova fixes and re-hands; all four comments parse and the orchestrator switches assignee automatically (recording attached).
- One escalation dry run lands in `Needs Justin` as a decision card and is approved with a single `approve` comment.
- Doc reviewed by Atlas and Sentinel; changelog entry; Linear comment with recording.

**Edge cases**

- Receiver character is over budget or paused (`agents/cost-controls`): handoff queues; Atlas is notified if it waits over 4 hours.
- Handoff to a character that cannot access the required tool (Beacon handing Stripe work to Iris): validator cross-checks `access` and refuses with the right target suggested.
- Session dies before posting the handoff: orchestrator synthesises a `handoff.kind: "crashed"` from the last footer and `git status`, routed to the same character for a retry.
- Two open questions with no defaults: linter blocks; a handoff must be actionable without a reply.
- Reviewer and builder disagree twice on the same finding: third round auto-escalates with both positions.
- Handoff references a screenshot artifact that expired in CI: artifacts referenced must be uploaded to Linear or MinIO, not left in CI.

**Dependencies**

- `agents/roster-v1` (characters and labels).
- Uses `pm-linear/session-playbook` footer, `pm-linear/justin-queue` decision card, `agents/skills-library` (`linear-update` validation).

**Agent**

Built by Atlas (lead) with Quill writing the document; reviewed by Sentinel (Code Reviewer) and Nova as a representative receiving builder.

**Size**

M: a spec with schema, linter and a multi-session dry run.
