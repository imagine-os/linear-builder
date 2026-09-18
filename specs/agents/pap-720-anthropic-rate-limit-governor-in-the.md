---
identifier: "PAP-720"
title: "Anthropic rate-limit governor in the runtime: shared output-tokens-per-minute and concurrent-session budget across sessions, 429 and 529 backoff coordination, reviewer priority and a saturation signal to the scheduler"
project: "agents"
projectName: "Agent Characters & Orgs"
phase: "P1"
type: "Build"
priority: 2
surfaces: ["Agent"]
milestone: "Sub-agents, skills and evals live"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-98", "PAP-282"]
blocks: []
key: "r4/agents/anthropic-rate-limit-governor"
url: "https://linear.app/paperos/issue/PAP-720/anthropic-rate-limit-governor-in-the-runtime-shared-output-tokens-per"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:31.357Z"
model: "claude-opus-5"
effort: "medium"
estimate: 2
dueDate: "2026-09-25"
cycle: null
---

# PAP-720: Anthropic rate-limit governor in the runtime: shared output-tokens-per-minute and concurrent-session budget across sessions, 429 and 529 backoff coordination, reviewer priority and a saturation signal to the scheduler

**Model / Effort:** Opus 5 (`claude-opus-5`) / medium — Build S

**Goal**

The cost estimate names the binding limits: the organisation's concurrent-session cap and output tokens per minute (16 builders generate 30k to 35k output tokens per minute), not Linear's API. Each session today backs off alone, so a burst of 429s at 20 sessions turns into twenty uncoordinated retry storms and idle reviewers. A governor inside the runtime meters the shared budget, admits sessions by priority and tells PAP-99 when to stop claiming.

**Scope**

* In: `src/runtime/governor.ts` in the orchestrator (token bucket for output tokens per minute and a semaphore for concurrent sessions from `orchestrator.config.yaml` `anthropic.limits`), `admit(role)` before `launchSession`, shared backoff on 429 and 529 (all sessions pause new turns for the `retry-after` window; one probe resumes), reviewer and QA priority over builders, `/status.governor` block and `agent.quota.saturated` event consumed by PAP-99 (`eligible()` returns nothing while saturated), metrics into PAP-98, `docs/pm/rate-limits.md`.
* Out: per-character budgets (PAP-111), model fallback (pm-linear routing issue handles model choice; the governor only signals), Linear rate limits (PAP-281, PAP-373).

**Spec**

* Limits come from config with headroom: `outputTokensPerMinute` (default 80 percent of the org limit read from the Console, entered by Justin once as NJ-4 follow-up), `maxConcurrentSessions`, per-model buckets when the Console shows separate limits; usage is measured from streamed `usage` deltas (PAP-282 stream handler).
* Admission: `admit('reviewer' | 'qa' | 'builder' | 'eval')` reserves a slot and a token allowance estimated from the size median; reviewers and QA are admitted first, evals last; a session that cannot be admitted waits in `governor_queue` and PAP-99 sees `saturated: true`.
* Backoff coordination: on any 429 or 529, the governor sets `pauseUntil` from `retry-after` (or exponential from 5 s), all sessions defer their next SDK call through a shared gate, one probe request resumes; the routing issue's model fallback is invoked only after the governor's three coordinated attempts.
* Telemetry: `governor.tokensPerMinute`, `governor.paused`, `governor.queueDepth` in `/status.governor` and PAP-98's report line; `agent.quota.saturated` and `agent.quota.recovered` on the bus.
* Safety: the governor never kills a session; PAP-111 does; saturation for more than 30 minutes opens one Plan audit comment for Atlas.

**Interface contract**

* Provides: `admit()`, `release()`, shared gate for SDK calls, `/status.governor`, events `agent.quota.saturated|recovered`, config schema `anthropic.limits`.
* Consumes: PAP-282 stream `usage` and launch path, PAP-98 metering, PAP-99 `eligible()`, PAP-111 (kill remains its job), the pm-linear model-routing fallback.

**Definition of done**

* Simulation with a fake SDK: 20 sessions against a 30k tokens-per-minute bucket never exceed it and reviewers are admitted first (property test).
* Mocked 529 storm: all sessions pause, one probe resumes, no retry storm (test with fake timers); saturation flips PAP-99 eligibility off and on (test).
* Live soak on staging with eight sessions for one hour: zero uncoordinated 429s in logs; `/status.governor` screenshot; docs; changelog.

**Test plan**

* Unit: token bucket arithmetic, admission ordering, pause and probe state machine, config validation.
* E2E: staging soak; simulation snapshot committed.

**Demo**

Open `/status.governor` during a soak: tokens per minute against the limit, queue depth zero; inject a mocked 529 and watch `paused: true` then recovery. Under two minutes.

**Edge cases**

* Console limit changes: config edit and restart; the governor logs the new limit; no code change.
* Long tool call (Playwright) produces no tokens: the slot stays reserved; the allowance is not consumed.
* Governor process restarts: buckets reset conservatively (start at zero allowance for one minute); running sessions continue.
* Multiple orchestrator replicas: bucket state in Postgres with `SKIP LOCKED` reservations, same pattern as claims.

**Dependencies**

Hard: PAP-282, PAP-98. Soft: PAP-99, PAP-111, PAP-704.

* Soft dependency (round 4): PAP-99 is a soft dependency, not a `blocks` relation, because this issue's milestone (2026-09-25) is later than PAP-99's (2026-09-22); build against its interface and reconcile when it lands.
  **Agent**

Builder: Atlas (Dispatcher). Reviewer: Sentinel (Code Reviewer).

**Size**

S: half a session.

*Round 4 critique fix (2026-09-18):* resolved 1 round-4 file key in this description to Linear identifiers: `r4/pm-linear/session-model-and-effort-routing` = PAP-704.
