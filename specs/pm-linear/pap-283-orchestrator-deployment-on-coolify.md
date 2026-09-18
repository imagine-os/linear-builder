---
identifier: "PAP-283"
title: "Orchestrator: deployment on Coolify, `/status` endpoint and runbook"
project: "pm-linear"
projectName: "Project Management & Claude Pipeline"
phase: "P0"
type: "Infra"
priority: 1
surfaces: ["Agent"]
milestone: "Orchestrator claims and ships issues"
state: "Backlog"
parent: "PAP-96"
children: []
blockedBy: ["PAP-25", "PAP-281", "PAP-282"]
blocks: ["PAP-97", "PAP-98", "PAP-99", "PAP-706"]
key: "pm-linear/orchestrator/deploy"
url: "https://linear.app/paperos/issue/PAP-283/orchestrator-deployment-on-coolify-status-endpoint-and-runbook"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:21:26.629Z"
model: "claude-opus-5"
effort: "high"
estimate: 2
dueDate: "2026-09-22"
cycle: null
---

# PAP-283: Orchestrator: deployment on Coolify, `/status` endpoint and runbook

**Model / Effort:** Opus 5 (`claude-opus-5`) / high — child of PAP-96 orchestrator (named exception applied to children)

**Goal**

Run the orchestrator as a service: a Docker image deployed through Coolify on the VPS with the repos cloned, `/healthz` and `/status`, structured logs, graceful shutdown and restart semantics that never lose a claim, plus the runbook a human or Atlas follows to start, stop, drain and inspect.

**Scope**

* In: `Dockerfile`, Coolify service definition, `src/http.ts` (Hono) with `/healthz` and `/status`, pino logs, shutdown handling, `README.md` runbook, secrets wiring through sops (PAP-17 conventions).
* Out: webhooks routes (PAP-97 adds them to the same Hono app), sandbox containers (PAP-280), the org chart (PAP-113 reads `/status`).

**Spec**

* Image: Node 22 slim with git, gh CLI, pnpm; volumes `/srv/repos`, `/srv/worktrees`, `/srv/sessions`; env from Coolify secrets; non-root user.
* `/status` JSON: `{ version, uptime, slots: { max, used }, queueDepth, sessions: SessionStatus[], scheduler?, limits?, paused }` where `SessionStatus` is the PAP-288 shape (interim fields `issue`, `character`, `state`, `startedAt`, `lastMessageAt` until it lands).
* Shutdown on SIGTERM: stop claiming, wait up to `drainSeconds` (default 600) for sessions, then mark remaining `interrupted`, release claims and exit; on start, `interrupted` sessions re-queue their issues with the last footer.
* `pnpm orchestrator drain | resume | inspect <sessionId>` CLI over the HTTP API with an admin token.
* Logs: JSON lines with `sessionId`, `issue`, `character`; log level from env.

**Interface contract**

* Provides: `GET /healthz`, `GET /status`, `POST /admin/drain`, `POST /admin/resume` (admin token), the Coolify service `paperos-orchestrator`, the runbook sections Start, Stop, Drain, Inspect, Rotate secrets, Recover from crash.
* Consumers: PAP-113 (`/status`), PAP-111 (`paused` flag and `/kill` mounted here), PAP-97 (mounts webhook routes), PAP-99 (`scheduler` block), Coolify health checks.
* Requires: PAP-25 VPS and Coolify, the two sibling children, PAP-17 secrets conventions.

**Definition of done**

* Coolify deploy green; `/healthz` returns 200; `/status` screenshot at 1280 px.
* Restart mid-session marks it `interrupted` and re-queues the issue (recording).
* Drain test: no new claims after `drain`, running session finishes, process exits 0.
* Runbook reviewed by Forge; changelog; Linear comment with screenshot and recording.

**Test plan**

* Unit: `/status` serializer snapshot; shutdown state machine with fake timers.
* Integration: container build and smoke run in CI (`docker run` then `curl /healthz`).
* e2e: staging restart and drain.
* Visual: `/status` JSON viewed at 1280 px only.

**Demo**

Open `/status` on staging, run `pnpm orchestrator drain`, watch `slots.used` fall to zero and `paused: true`, then `resume` and see claims restart. One minute.

**Edge cases**

* Volume missing on first boot: clone repos from config, log duration.
* Coolify health check during drain: `/healthz` stays 200 with `draining: true`.
* Two replicas by accident: claims stay safe (SKIP LOCKED); `/status` shows `replica` id.
* Disk full from worktrees: alert in logs; `pnpm orchestrator gc` removes worktrees of `Done` issues.
* Secrets rotated: restart picks new env; runbook step.

**Dependencies**

Blocked by PAP-281, PAP-282, PAP-25.

**Agent**

Built by Forge (Ops Runner sub-agent); reviewed by Sentinel (Security Auditor).

**Size**

S
