---
identifier: "PAP-288"
title: "Add agent session observability: heartbeats, stuck-session detection, per-session OTel spans and a `/status` contract shared by the org chart, board cards and cost controls"
project: "agents"
projectName: "Agent Characters & Orgs"
phase: "P1"
type: "Build"
priority: 2
surfaces: ["Agent", "Staff"]
milestone: "Sub-agents, skills and evals live"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-96"]
blocks: ["PAP-102", "PAP-113"]
key: "agents/session-observability"
url: "https://linear.app/paperos/issue/PAP-288/add-agent-session-observability-heartbeats-stuck-session-detection-per"
source: "Linear snapshot 2026-09-17T13:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T13:06:09.833Z"
---

# PAP-288: Add agent session observability: heartbeats, stuck-session detection, per-session OTel spans and a `/status` contract shared by the org chart, board cards and cost controls

**Goal**

Define and implement the one status contract everyone assumes: a `SessionStatus` shape, a heartbeat every 60 seconds, `stuck` after 15 minutes without progress, per-session OpenTelemetry spans tagged with issue and character, and the `/status` payload that the org chart, board cards, cost controls and the weekly audit all read.

**Scope**

* In: `packages/agents/src/status.ts` (Zod `SessionStatus`), heartbeat writer in the orchestrator stream handler, stuck detector, OTel instrumentation of `launchSession` and tool calls, `/status.sessions`, alert events, `docs/agents/observability.md`.
* Out: the org chart rendering (PAP-113), the collector and dashboards (PAP-40), budget arithmetic (PAP-111).

**Spec**

* `SessionStatus = { sessionId, issue, character, model, state: "starting" | "working" | "waiting-tool" | "reviewing" | "paused" | "stuck" | "ending" | "ended" | "killed", startedAt, lastHeartbeat, lastProgressAt, turns, costUsd, worktree, branch, pr?, sandbox?: { cpuPct, memMb }, reason? }`.
* Heartbeat: the stream handler updates `lastHeartbeat` on every SDK message and `lastProgressAt` on assistant text or tool result; a 60 s ticker persists to `sessions.status_json` even when idle; hook-based sessions send `PAPEROS_HEARTBEAT` via PAP-107 `tool.post` events.
* Stuck: `now - lastProgressAt > 15 min` while `state = working` flips to `stuck`, emits `session.stuck`, posts one comment, and after 30 minutes PAP-111 may abort with `reason: stuck`.
* OTel: span `agent.session` with attributes `paperos.issue`, `paperos.character`, `paperos.model`; child spans per tool call (`agent.tool`, name, duration, denied flag) exported to the PAP-40 collector; trace id stored in `SessionStatus` for deep links.
* `/status.sessions: SessionStatus[]` plus `summary { working, stuck, paused }`.

**Interface contract**

* Provides: `SessionStatusSchema`, type `SessionStatus`, `statusOf(sessionId)`, `allStatus()`, events `session.heartbeat`, `session.stuck`, `session.recovered`, OTel attribute names under `paperos.*`, `/status.sessions`.
* Consumers: PAP-113 badges, PAP-102 character badge (15 minute staleness), PAP-111 (`stuck` abort), PAP-306 (`STALE_SESSION`), PAP-98 (turns and cost cross-check), PAP-146 pushes the same shape over realtime later.
* Requires: PAP-96 stream handler and `/status` route, PAP-40 collector endpoint, PAP-107 event format for hook sessions, PAP-280 `stats` (soft).

**Definition of done**

* Schema and ticker implemented; `/status.sessions` validates against the schema in a test.
* Stuck detection proven with a session stalled by a mocked never-resolving tool; comment posted once; recovery flips back.
* Spans visible in the PAP-40 dashboard for a real session (screenshot at 1280 px).
* Docs; changelog; Linear comment with screenshot.

**Test plan**

* Unit: state machine transitions with fake clock; heartbeat persistence cadence; schema snapshot.
* Integration: mocked SDK stream producing heartbeats and a stall; OTel exporter captured in-memory and asserted for attributes.
* e2e: staging session traced end to end.
* Visual: dashboard screenshot only.

**Demo**

Start a rehearsal session, poll `/status.sessions` and watch `lastHeartbeat` advance every minute; freeze the mocked tool and after 15 minutes (fake clock in dev) see `stuck` and the Linear comment. Two minutes.

**Edge cases**

* Long legitimate tool call (Playwright run 20 min): tool spans count as progress; `waiting-tool` state suppresses `stuck` until 45 min.
* Orchestrator restart: statuses reloaded from `status_json`; `interrupted` sessions appear as `ended` with reason.
* Clock skew between hosts: heartbeats use orchestrator time only.
* Collector down: spans buffered and dropped after 5 minutes; status unaffected.
* Hundreds of ended sessions: `/status.sessions` returns active plus last 24 h; older via `?since`.

**Dependencies**

Blocked by PAP-96, PAP-40. Blocks PAP-113, PAP-102. Soft: PAP-107, PAP-280.

**Agent**

Built by Forge (Ops Runner) with Atlas (Dispatcher) on the state machine; reviewed by Sentinel.

**Size**

M
