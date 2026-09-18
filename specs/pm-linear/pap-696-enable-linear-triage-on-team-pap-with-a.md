---
identifier: "PAP-696"
title: "Enable Linear Triage on team PAP with a `Triage` state, make PAP-307 draft from the triage inbox, and define accept, decline, merge-as-duplicate and snooze outcomes with a ten-minute drafting SLA"
project: "pm-linear"
projectName: "Project Management & Claude Pipeline"
phase: "P1"
type: "Infra"
priority: 2
surfaces: ["Staff"]
milestone: "PM module syncs both ways"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-91", "PAP-307"]
blocks: ["PAP-697"]
key: "r4/pm-linear/linear-triage-enable-and-intake-state-machine"
url: "https://linear.app/paperos/issue/PAP-696/enable-linear-triage-on-team-pap-with-a-triage-state-make-pap-307"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:28.203Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 2
dueDate: "2026-09-30"
cycle: null
---

# PAP-696: Enable Linear Triage on team PAP with a `Triage` state, make PAP-307 draft from the triage inbox, and define accept, decline, merge-as-duplicate and snooze outcomes with a ten-minute drafting SLA

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Infra S

**Goal**

`triageEnabled` is false; PAP-307 listens for issues created in Todo or Backlog and the only triage today is a saved view. Linear's Triage feature gives an inbox state, accept and decline actions, duplicate merging and intake from integrations (Slack, email, API). Enabling it and pointing the Decomposer at it turns Justin's one-liners and voice memos into one queue with a measurable drafting SLA.

**Scope**

* In: `teamUpdate({ triageEnabled: true })` and the `Triage` workflow state (type `triage`) in `configure-workspace.ts` (PAP-91), `triageIssueState` wiring, PAP-307 trigger change (issue created in `Triage` or comment `triage:`), outcome handlers in the orchestrator (`accept` moves to Backlog with the drafted contract; `decline` cancels with a reason comment, only Justin or Atlas; `duplicate` uses `markedAsDuplicateWorkflowState`; `snooze` sets a `snoozedUntil`), SLA timer `triage.drafted_within_10m`, docs `docs/pm/triage.md` update.
* Out: the Decomposer prompt itself (PAP-307), Slack voice-memo intake (own issue), Linear's paid SLA feature (Business plan; emulated by the pipeline SLA issue).

**Spec**

* State: `Triage` created with type `triage`, position before Backlog, description "Inbox for humans and integrations; the Decomposer drafts within ten minutes"; `team.triageIssueState` set; default state for API creates by integrations stays `Triage`, for the orchestrator's own creates `Backlog`.
* PAP-307 handler: trigger on `Issue.create` with state `Triage` (any author) and on `triage:` comments; after drafting it leaves the issue in `Triage` with label `triaged` and the one comment; Justin's `accept` (Linear action or reply `accept`) moves it to Backlog where promotion (round-4 child) picks it up when unblocked; `decline` moves to Canceled with the reason; `duplicate` links and marks Duplicate; `snooze <n>d` hides it from the view until the date.
* Outcome grammar reuses PAP-94 `parseReply` verbs plus `accept | decline: <reason> | duplicate PAP-n | snooze <n>d`; agent authors cannot accept.
* SLA: `triage_sla(issue_id, created_at, drafted_at, accepted_at)`; drafting over ten minutes emits `pipeline.sla_breached` (pipeline SLA issue) and shows in the Plan audit (PAP-306).
* Views-as-code issue adds `Pipeline: triage inbox` (state Triage, oldest first).

**Interface contract**

* Provides: `Triage` state id in `linear-workspace.json`, outcome grammar and handlers, `triage_sla` table, event `triage.drafted`, the intake contract for integrations (create in `Triage` with the source in the description footer).
* Consumes: PAP-91 configure script, PAP-307 Decomposer handler, PAP-94 grammar, PAP-97 webhooks, PAP-306 audit, Linear `teamUpdate` and workflow state APIs.

**Definition of done**

* Triage enabled with the state; a one-line issue created in Triage is drafted within ten minutes and accepted with `accept` to Backlog (recording); `decline` and `duplicate` paths tested on rehearsal issues.
* SLA table populated for five rehearsal issues; `--check` clean; docs; changelog; Linear comment with the recording.

**Test plan**

* Unit: outcome grammar table, actor checks, SLA arithmetic with a fake clock.
* E2E: five rehearsal issues through create, draft and each outcome on team PAP.

**Demo**

Create an issue in Triage titled "invoices need a paid stamp", watch the draft appear, reply `accept` and see it land in Backlog with the contract sections. Under two minutes.

**Edge cases**

* Issue created directly in Backlog by Justin (old habit): PAP-307's Backlog trigger stays for a month and comments "next time use Triage".
* Integration floods Triage (Slack bot loop): drafting paused above 20 new issues per hour; Atlas notified.
* Snoozed issue passes its date: reappears in the view; no state change.
* `decline` by a non-Justin human (none exist today): honoured for Justin only; others get "only Justin can decline".

**Dependencies**

Hard: PAP-91, PAP-307. Soft: PAP-94, PAP-97, PAP-306, PAP-691.

**Agent**

Builder: Atlas (Decomposer). Reviewer: Sentinel (Code Reviewer).

**Size**

S: half a session.

*Round 4 critique fix (2026-09-18):* resolved 1 round-4 file key in this description to Linear identifiers: `r4/pm-linear/orchestrator-promotion-pass` = PAP-691.
