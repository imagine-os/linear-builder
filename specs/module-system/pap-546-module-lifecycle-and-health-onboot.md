---
identifier: "PAP-546"
title: "Module lifecycle and health: `onBoot`, `onReady`, `onStop` hooks in `bind`, ordered graceful shutdown, per-module health checks aggregated into `/healthz` and a boot timing report"
project: "module-system"
projectName: "Module System & Swap Tooling"
phase: "P1"
type: "Build"
priority: 2
surfaces: ["Developer"]
milestone: "Contracts and conformance wired"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-269", "PAP-434", "PAP-537"]
blocks: []
key: "r4/module-system/lifecycle-and-health"
url: "https://linear.app/paperos/issue/PAP-546/module-lifecycle-and-health-onboot-onready-onstop-hooks-in-bind"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:05.179Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 3
dueDate: "2026-09-27"
cycle: null
---

# PAP-546: Module lifecycle and health: `onBoot`, `onReady`, `onStop` hooks in `bind`, ordered graceful shutdown, per-module health checks aggregated into `/healthz` and a boot timing report

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Build M

**Goal**

OSGi bundles have a lifecycle; PaperOS modules have `bind`. Without start and stop hooks, a module that needs a warm cache, a Stripe client handshake or a Hocuspocus connection does it lazily on the first request, and shutdown loses in-flight jobs. `/healthz` (PAP-269) answers for the process, not for the modules inside it, so a broken payments adapter looks healthy. This issue gives modules a lifecycle and the health endpoint a module view.

**Scope**

In:

* Manifest `lifecycle` block (minor bump of PAP-433 schema): `{ startupBudgetMs, healthIntervalMs, drainTimeoutMs }`; `bind(kernel)` may return `{ onBoot?, onReady?, onStop?, health? }`.
* Kernel: `kernel.start()` runs `onBoot` in topological order with per-module budgets (over budget is a warning, throw aborts boot naming the module), then `onReady` once every module booted; `kernel.stop(signal)` runs `onStop` in reverse order with `drainTimeoutMs`, after the Hono server stops accepting and pg-boss (PAP-43) pauses; SIGTERM handled in the three hosts.
* Health: `health()` returns `{ status: ok|degraded|down, details }`; the kernel polls per `healthIntervalMs` and caches; `/healthz` (PAP-269) gains `modules: { <id>: status }` and returns 503 only when a `requires[].optional=false` provider is `down`; `/readyz` answers 200 only after `onReady`.
* Boot report: `kernel.describe().boot` with per-module timings, printed by `pnpm modules:list --boot` and exported as an OTel span tree (PAP-547).

Out: process supervision (Coolify), the health endpoint route itself (PAP-269), per-port resilience (PAP-548).

**Spec**

* Total boot budget for the template under 3 s on the compose stack; the report fails a Gate 1 benchmark when exceeded.
* `onStop` must be idempotent; a second SIGTERM forces exit after `drainTimeoutMs`.
* A `degraded` module keeps serving; the status is visible on `/settings/modules` (PAP-538) and in `/healthz`.
* Disabled modules (PAP-266) are skipped entirely and reported `disabled`.

**Interface contract**

Provides: `lifecycle` manifest block, `onBoot|onReady|onStop|health` hook shapes, `kernel.start|stop`, `/healthz.modules`, `/readyz`, boot report; consumed by every `Wire <module>` issue (adapters with connections), PAP-26 (deploy waits on `/readyz`), PAP-40 (health metrics), PAP-283 (orchestrator `/status`), PAP-88.

Consumes: kernel and topological order (PAP-434), health endpoints (PAP-269), jobs pause (PAP-43, soft), Hono server (PAP-267).

**Definition of done**

* Template boots with the report showing every module under budget; SIGTERM on the API drains an in-flight request and stops modules in reverse order (log).
* A double reporting `down` flips `/healthz` to 503 and `degraded` keeps 200 (tests); `docs/platform/kernel.md` lifecycle section; Linear comment.

**Test plan**

* Unit: hook ordering on chains and diamonds; budget warnings and aborts; reverse-order stop; health aggregation matrix; idempotent stop.
* E2E: compose stack: boot report, `/readyz` timing, SIGTERM drain with a 2 s handler.

**Demo**

Reviewer runs `pnpm modules:list --boot` and reads eighteen modules with timings, then `curl /healthz` showing `modules`, then kills the API with SIGTERM during a slow request and sees the request complete before exit. Under 2 minutes.

**Edge cases**

* Module `onBoot` depends on a port whose provider boots later: topological order guarantees providers first; a cycle is already a manifest error.
* Health check itself hangs: bounded by a 2 s timeout, reported `down` with `timeout`.
* Vite dev HMR: `onStop` and `onBoot` rerun for the replaced module only.

**Dependencies**

Hard: PAP-434, PAP-269. Soft: PAP-43, PAP-267, PAP-266. Feeds PAP-26, PAP-283.

**Agent**

Builder: Forge (Platform Engineer). Reviewer: Sentinel (Edge Case Hunter).

**Size**

M: one session.

*Round 4 critique fix (2026-09-18):* resolved 3 round-4 file keys in this description to Linear identifiers: `r4/module-system/kernel-otel` = PAP-547, `r4/module-system/modules-settings-page` = PAP-538, `r4/module-system/port-resilience` = PAP-548.
