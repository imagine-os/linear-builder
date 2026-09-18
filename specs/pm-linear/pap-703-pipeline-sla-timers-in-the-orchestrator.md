---
identifier: "PAP-703"
title: "Pipeline SLA timers in the orchestrator: Needs Justin default deadline, In Review without gate results, Ready but unclaimed, Triage undrafted and stuck sessions, each with an escalation and a label"
project: "pm-linear"
projectName: "Project Management & Claude Pipeline"
phase: "P1"
type: "Build"
priority: 3
surfaces: ["Agent"]
milestone: "PM module syncs both ways"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-94", "PAP-281", "PAP-288"]
blocks: ["PAP-306"]
key: "r4/pm-linear/pipeline-sla-timers"
url: "https://linear.app/paperos/issue/PAP-703/pipeline-sla-timers-in-the-orchestrator-needs-justin-default-deadline"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:28.971Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 2
dueDate: "2026-09-30"
cycle: null
---

# PAP-703: Pipeline SLA timers in the orchestrator: Needs Justin default deadline, In Review without gate results, Ready but unclaimed, Triage undrafted and stuck sessions, each with an escalation and a label

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Build S

**Goal**

Linear SLAs are a Business-plan feature and the workspace is on Basic, while PAP-94 (48 h default), PAP-288 (15 min stuck) and PAP-306 (weekly stale checks) each keep their own clock. One timer service in the orchestrator evaluates every open issue against a small SLA table every minute, sets a label, comments once and escalates, so the pipeline's promises are enforced in real time and visible in the views.

**Scope**

* In: `src/sla/{rules,evaluate,escalate}.ts` with `ops/pm/sla.yaml`, table `sla_breaches(issue_id, rule, breached_at, resolved_at, escalated_to)`, labels `sla:<rule>` created by the views issue script, comment template `templates/sla-breach.md` (edited in place), `/status.sla` block, PAP-306 `SLA_BREACHES` section, docs `docs/pm/sla.md`.
* Out: Linear's paid SLA feature, moving states (timers only label, comment and escalate), the budget timers (PAP-111 owns spend), heartbeat detection itself (PAP-288 provides `stuck`).

**Spec**

* Rules: `needs-justin-default` (open in Needs Justin longer than the card's `defaultTimeoutHours`, default 48 h: apply the default per PAP-94 unless `hard-block`, then label `sla:justin-overdue` and add to the daily digest); `in-review-no-gates` (In Review for 2 h with no gate status: label `gates-pending`, comment once, alert Sentinel after 4 h); `ready-unclaimed` (Ready for Claude longer than three poll cycles while slots are free: label `sla:unclaimed`, Atlas notified; usually a routing or budget hold); `triage-undrafted` (Triage for 10 min without `triaged`: retry PAP-307 once, then Atlas); `stuck-session` (PAP-288 `stuck` for 30 min: PAP-111 abort with `reason: stuck`); `in-progress-no-pr` (In Progress for twice the Size allowance in hours with no PR: comment, Atlas).
* Evaluator runs every minute over the orchestrator's cached issue set (refreshed by webhooks and the poll), never calling Linear per issue; a breach writes one row, sets the label and posts one comment edited in place with the elapsed time; resolution clears the label and marks the row.
* Escalation targets: Atlas (comment on the Plan audit issue), Sentinel (comment on `PAP-SECURITY-ALERTS` only for security-related rules), Justin (never directly; only through the PAP-94 default mechanism).
* `/status.sla` lists open breaches for PAP-113 badges; PAP-306's weekly report counts breaches per rule.

**Interface contract**

* Provides: `sla.yaml` schema, `evaluateSla()`, table `sla_breaches`, labels `sla:*` and `gates-pending`, `/status.sla`, comment template.
* Consumes: PAP-281 issue cache and `linearComment`, PAP-288 `SessionStatus`, PAP-94 default application, PAP-111 abort, PAP-97 gate events, the views issue's labels.

**Definition of done**

* Each rule proven with a fake clock on fixtures; live: a rehearsal issue left In Review without gates gets `gates-pending` after two hours and the comment once (recording).
* Resolution clears the label within one minute of the condition ending (test); `/status.sla` validates; docs; changelog; Linear comment with the recording.

**Test plan**

* Unit: rule windows and thresholds, single-comment idempotency, resolution path, escalation routing table.
* E2E: staging soak of four hours with induced breaches.

**Demo**

Open `/status.sla` and the `Pipeline: In Review awaiting gates` view during a rehearsal: one issue with `gates-pending`, the comment showing elapsed time, then the label vanishing when Gate 1 posts. Under two minutes.

**Edge cases**

* Orchestrator restart: breaches recomputed from state, rows reconciled, no duplicate comments (dedupe by hash).
* Issue moved by Justin mid-breach: resolution recorded with `resolvedBy: human`.
* Gate genuinely takes over two hours (nightly-heavy contention): `gates-pending` is informational; the 4 h alert names the runner queue time from the gate metrics table.
* Hundreds of issues Ready during a capacity dip: `ready-unclaimed` fires once with a count, not per issue.

**Dependencies**

Hard: PAP-281, PAP-288, PAP-94. Soft: PAP-111, PAP-97, PAP-306, PAP-701.

**Agent**

Builder: Atlas (Dispatcher). Reviewer: Sentinel (Code Reviewer).

**Size**

S: half a session.

*Round 4 critique fix (2026-09-18):* resolved 1 round-4 file key in this description to Linear identifiers: `r4/pm-linear/pipeline-views-as-code` = PAP-701.
