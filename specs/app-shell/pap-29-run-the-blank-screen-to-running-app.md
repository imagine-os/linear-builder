---
identifier: "PAP-29"
title: "Run the blank-screen-to-running-app drill: time `paperos create` through first spec'd page, deploy and desktop build; record it; answer PAP-5 with numbers"
project: "app-shell"
projectName: "Universal App Shell & Repo Template"
phase: "P2"
type: "Review"
priority: 1
surfaces: ["Developer"]
milestone: "Multi-monitor and PWA polish"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-22", "PAP-26", "PAP-28", "PAP-120", "PAP-266", "PAP-316", "PAP-429"]
blocks: []
key: "app-shell/new-app-drill"
url: "https://linear.app/paperos/issue/PAP-29/run-the-blank-screen-to-running-app-drill-time-paperos-create-through"
source: "Linear snapshot 2026-09-17T13:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T13:05:26.414Z"
model: "claude-opus-5"
effort: "high"
---

# PAP-29: Run the blank-screen-to-running-app drill: time `paperos create` through first spec'd page, deploy and desktop build; record it; answer PAP-5 with numbers

**Goal**

PAP-5 asks a measurable question: how fast from a blank screen to a running app. This drill creates a new app from the template with agents using only documented tools and stamps wall-clock time and credit cost at five checkpoints. PAP-5 stays open as the standing scoreboard; PAP-95 must not close it (the two specs now agree). Findings become issues; the drill repeats weekly.

**Scope**

In:

* Protocol `docs/drills/new-app.md`: fixed scenario (clinic booking, two audiences, one table, one comment thread), fixed starting state, roles (Atlas dispatches, Forge builds, Quill writes two specs, Sentinel reviews), and what may not be done by hand.
* Timer harness `pnpm drill:new-app` reading `paperos create --json` step timings, PR merge events and deploy webhooks into `reports/drills/new-app-<date>.json` with spend from PAP-99.
* Video at 375 and 1280 (PAP-84) plus `asciinema` terminal; a 3-minute cut in the docs.
* Report with checkpoint table, cost, top five frictions by minutes lost, issues filed.

Out: fixing the frictions (they become issues).

**Spec**

* Checkpoints and first-run targets: C1 repo, mirror, CI, Linear project under 10 min; C2 two spec'd pages render locally under 60 min; C3 staging with auth and a seeded tenant under 90 min; C4 Linux and macOS desktop builds launch under 150 min; C5 release-candidate digest in Needs Justin under 240 min; credits under 150 USD.
* Everything through `paperos create`, the spec skill, the orchestrator (PAP-96) and gates 1-4; manual steps logged as frictions.
* Throwaway repo `drill-<date>` removed by PAP-51 after archiving the report.
* Scenario rotates clinic, agency, retail after the second run.

**Interface contract**

Provides:

* `reports/drills/new-app-<date>.json` schema `{ scenario, startedAt, checkpoints: [{ id, at, ms, status: 'ok'|'blocked' }], creditsUsd: { firstAttempt, retries }, frictions: [{ minutes, issue }] }` rendered by the docs and PAP-88's digest.
* Comment format on PAP-5: checkpoint table plus report link; PAP-95 links here instead of closing PAP-5.
* Recurring Linear issue template "Weekly new-app drill".

Consumes: `paperos create --json` (PAP-22), deploy status (PAP-26), release-candidate flow (PAP-88), codegen (PAP-120), modules (PAP-28), credit metering (PAP-99), video replays (PAP-84).

**Definition of done**

* First drill completed with all five checkpoints stamped; report and video in the docs; five or more friction issues filed and linked.
* PAP-5 comment with the table and link; no Needs Justin item.
* Weekly recurrence configured via PAP-88 and the issue template.
* CHANGELOG; Linear comment with the numbers.

**Test plan**

* Unit: harness parses fixture events into checkpoints; blocked-checkpoint handling; cost split first-attempt versus retries.
* Integration: dry drill against the sandbox repo with fake timings validates the JSON against its schema.
* Review: Sentinel (Edge Case Hunter) checks every manual intervention appears as a friction with minutes.
* Visual: report page at 375 and 1280; 3-minute video plays in the docs engine.

**Demo**

Reviewer opens the report page, reads the five-row checkpoint table with times and cost, plays the 3-minute cut, then opens PAP-5 and sees the same table as the latest comment. Under 2 minutes.

**Edge cases**

* Missing feature stalls the drill: stamp `blocked`, file the issue, continue with a documented manual step.
* Retry storms inflate cost: report separates first-attempt from retry cost.
* No Apple credentials: unsigned macOS build counts for C4 with signing status noted.
* Orchestrator concurrency delays: scheduling wait recorded separately from build time.
* Agents memorise the scenario: rotation after run two.

**Dependencies**

PAP-22, PAP-26, PAP-28, PAP-120 (hard). Soft: PAP-88 (the first run does not need the release train; weekly runs adopt it once it exists; the `blocks` relation from PAP-88 was removed on 2026-09-17, round-2 FIX-1), PAP-19, PAP-84, PAP-96, PAP-99, PAP-51. Feeds PAP-95 and every project through friction issues.

**Agent**

Run by Atlas (Dispatcher) with Forge, Quill and Sentinel in their roles.

**Size**

M: a protocol, a harness and one long run.
