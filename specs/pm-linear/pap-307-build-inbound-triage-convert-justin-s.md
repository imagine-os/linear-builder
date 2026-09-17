---
identifier: "PAP-307"
title: "Build inbound triage: convert Justin's freeform issues and comments into contract-valid issues via the Decomposer sub-agent, wired to the Triage view"
project: "pm-linear"
projectName: "Project Management & Claude Pipeline"
phase: "P1"
type: "Build"
priority: 2
surfaces: ["Agent", "Staff"]
milestone: "Orchestrator claims and ships issues"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-93", "PAP-97", "PAP-118"]
blocks: []
key: "pm-linear/inbound-triage"
url: "https://linear.app/paperos/issue/PAP-307/build-inbound-triage-convert-justins-freeform-issues-and-comments-into"
source: "Linear snapshot 2026-09-17T13:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T13:06:07.130Z"
model: "claude-sonnet-5"
effort: "high"
---

# PAP-307: Build inbound triage: convert Justin's freeform issues and comments into contract-valid issues via the Decomposer sub-agent, wired to the Triage view

**Goal**

The contract (PAP-93) bounces non-conforming issues, but the only human should be able to type one line and get a buildable issue. When Justin creates an issue in `Todo` or `Backlog` without contract sections, or comments `triage:` on any issue, the Decomposer sub-agent drafts Goal, Scope, Spec, Definition of done, Edge cases, Dependencies, Agent and Size, links or requests a spec, asks at most one question and leaves the issue for him to move to `Ready for Claude`.

**Scope**

* In: webhook handler on `Issue.create` and `Comment.create` (human author, team PAP), the triage session prompt, the `triaged` label, a decision-free `ask:` flow, `docs/pm/triage.md`, and a saved filter definition documented for the existing `Triage` view (the view itself is not modified).
* Out: acting on the issue, moving it to `Ready for Claude`, changing states, creating projects.

**Spec**

* Trigger: issue created by a human with fewer than three contract sections, or a human comment whose first line is `triage:`; ignore agent authors and issues already labelled `triaged`.
* Session: Atlas (Decomposer) read-only plan mode, `maxTurns` 12, cost cap $4 (PAP-111); inputs are the issue text, the plan blueprint document, `linear-workspace.json`, the project list with descriptions and the twenty most similar issue titles (substring and label match).
* Output: `issueUpdate` with the full contract description (original text preserved under `Original request`), labels Phase, Type and surfaces inferred with confidence noted, a project and milestone proposal, `parentId` when it is clearly a sub-task, and one comment: either "Drafted, move to Ready for Claude when happy" or a single `ask:` question rendered as a PAP-94 card without occupying a `Needs Justin` slot.
* Spec requirement: if Type is Build and a route is named, call PAP-118 `author-spec open-issue` mode to draft the spec branch or add a `needs-spec` line.
* Every drafted issue passes `validateIssue` before the update is sent.

**Interface contract**

* Provides: handler registered through PAP-97 `registerWebhookHandler`, `triage(issueId): TriageResult = { ok, sectionsAdded[], labels[], project?, question? }`, label `triaged`, the `triage:` comment grammar, view filter `label = triaged AND state in (Backlog, Todo)`.
* Consumers: Justin; PAP-306 counts `triaged` issues waiting; PAP-112 handbook documents `triage:`.
* Requires: PAP-93 `validateIssue`, PAP-97 webhooks, PAP-118 scripts, PAP-104 Decomposer definition, PAP-111 cap.

**Definition of done**

* Five real one-line issues from Justin's style ("we need dark mode on the invoice page") triaged in staging; four of five pass the contract without edits; results table attached.
* Original text preserved in every case.
* `ask:` flow demonstrated once with a reply that completes the draft.
* No state changes performed by the handler (asserted in tests); docs; changelog; Linear comment.

**Test plan**

* Unit: trigger detection (sections count, author kind, grammar), label inference from fixture titles, `Original request` preservation, validator gate.
* Integration: recorded webhooks through the handler with a mocked SDK session returning a fixture draft.
* e2e: five staging issues.
* Visual: the drafted issue in Linear mobile at 375 px.

**Demo**

Create an issue titled "customers should get an SMS when an invoice is overdue" with no body; within two minutes it has all sections, labels, a proposed project and one comment; move it to `Ready for Claude` and watch PAP-93 stay silent. Two minutes.

**Edge cases**

* Request spans two projects: draft the smaller one and propose the second as a child list.
* Duplicate of an existing issue: comment with the match and label `possible-duplicate`, still draft.
* Justin edits during triage: session result is discarded if `updatedAt` moved; retry once.
* Cost cap hit: partial draft with a `TODO` marker, never silence.
* Non-English request: draft in English, keep the original.

**Dependencies**

Blocked by PAP-93, PAP-97, PAP-118. Uses PAP-111, PAP-104.

**Agent**

Built by Atlas (Decomposer sub-agent); reviewed by Quill for prose and Sentinel.

**Size**

M
