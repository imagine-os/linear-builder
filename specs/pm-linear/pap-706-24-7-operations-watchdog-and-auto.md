---
identifier: "PAP-706"
title: "24/7 operations: watchdog and auto-restart for the orchestrator, capacity curve by time of day and phase, night mode for Needs Justin escalations, and a 07:00 morning report of what ran overnight"
project: "pm-linear"
projectName: "Project Management & Claude Pipeline"
phase: "P1"
type: "Build"
priority: 2
surfaces: ["Staff"]
milestone: "Orchestrator claims and ships issues"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-98", "PAP-283"]
blocks: []
key: "r4/pm-linear/always-on-operations-and-morning-report"
url: "https://linear.app/paperos/issue/PAP-706/247-operations-watchdog-and-auto-restart-for-the-orchestrator-capacity"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:29.494Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 2
dueDate: "2026-09-22"
cycle: null
---

# PAP-706: 24/7 operations: watchdog and auto-restart for the orchestrator, capacity curve by time of day and phase, night mode for Needs Justin escalations, and a 07:00 morning report of what ran overnight

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Build S

**Goal**

Justin asked for the AI to run 24/7. PAP-283 deploys the orchestrator with restart semantics and PAP-99 caps parallelism, but nothing schedules capacity through the night, keeps the process alive without a human, or tells Justin at breakfast what happened while he slept. This issue adds the watchdog, a capacity curve that follows the Execution Schedule's peaks, night handling for escalations and one morning comment.

**Scope**

* In: `ops/orchestrator/watchdog.sh` and a Coolify health check with auto-restart and a crash-loop breaker (three restarts in 15 min pauses claiming and pages Atlas), `ops/orchestrator/capacity.yaml` (target `maxParallel` per hour and phase, from Execution Schedule section 2's peak curve), night mode (00:00 to 07:00 Justin local: Needs Justin cards queue silently, `page` security alerts still fire, no new P2 claims in the last hour before the daily cap), morning report job at 07:00 local on the burn report issue from `templates/morning-report.md`, `/status.capacity`, docs `docs/pm/operations.md`.
* Out: the scheduler algorithm (PAP-99), budgets (PAP-111), the burn numbers (PAP-98), notification transport beyond Linear comments (PAP-136).

**Spec**

* Watchdog: `/healthz` polled every 30 s by Coolify; two failures restart the container; `interrupted` sessions re-queue per PAP-283; a crash loop opens one Plan audit comment with the last 50 log lines and pauses claiming until Atlas resumes.
* Capacity curve: `capacity.yaml` maps `(date range, hour range) -> maxParallel` with the schedule's 8, 12, 16, 20 peaks and the 09-27 to 09-30 taper; the loop reads it every cycle; a manual override `POST /admin/capacity { maxParallel, until }` with an admin token; reviewers stay outside the cap.
* Night mode: decision cards created at night are held with `queued-for-justin` until 07:00 unless `Urgent` or security `page`; the PAP-94 48 h default clock still runs; no session is started in the final hour before `globalPerDayUsd` would be reached (PAP-111 pre-flight consults the curve).
* Morning report under 2500 characters: sessions started, landed, bounced, killed overnight; PRs merged; gates red now; Needs Justin cards waiting with one-line asks; spend overnight and chunk line; stuck or interrupted sessions; the day's planned claims from the promotion dry run.
* `/status.capacity` exposes the current target, override and night-mode flag for PAP-113.

**Interface contract**

* Provides: watchdog and crash-loop breaker, `capacity.yaml` schema, `POST /admin/capacity`, night-mode rules, morning report template and job, `/status.capacity`.
* Consumes: PAP-283 deployment and `/healthz`, PAP-98 spend, PAP-288 statuses, PAP-94 governor, PAP-111 pre-flight, PAP-97 merge events, the promotion dry run.

**Definition of done**

* Kill the container on staging: it restarts within a minute and re-queues the interrupted session (recording); a forced crash loop pauses claiming and posts the log excerpt.
* Capacity follows the curve across a simulated day with a fake clock (test); override honoured and expires.
* Three morning reports posted on staging (screenshots at 375 px); night-mode holds a rehearsal card until 07:00 (recording); docs; changelog.

**Test plan**

* Unit: curve lookup with boundaries, night-mode decision table, report renderer snapshot, crash-loop counter.
* E2E: staging kill and crash-loop drills; overnight soak with the morning report.

**Demo**

Open the burn report issue at 07:05 and read the morning report; open `/status.capacity` and see today's target and the night-mode flag off. Under one minute.

**Edge cases**

* Justin's timezone changes (travel): `operator.timezone` in config; night mode follows it.
* Coolify itself down: the VPS cron `watchdog.sh` restarts Docker services; documented in the runbook.
* Capacity file invalid: loop keeps the last good curve and logs loudly.
* Nothing ran overnight (queue empty): the report says so and lists why (blocked chains from the slack table).

**Dependencies**

Hard: PAP-283, PAP-98, PAP-288. Soft: PAP-94, PAP-111, PAP-97, PAP-99, PAP-691.

* Soft dependency (round 4): PAP-288 is a soft dependency, not a `blocks` relation, because its milestone (2026-09-25) is later than this issue's (2026-09-22); build against its interface and reconcile when it lands.
  **Agent**

Builder: Atlas (Dispatcher) with Forge (Ops Runner). Reviewer: Sentinel (Code Reviewer).

**Size**

S: half a session.

*Round 4 critique fix (2026-09-18):* resolved 1 round-4 file key in this description to Linear identifiers: `r4/pm-linear/orchestrator-promotion-pass` = PAP-691.
*Round 4 critique fix (2026-09-18):* PAP-288 appears in the Hard list above and in a round-4 soft note; it is soft (no `blocks` relation). Read the Hard list without it.
