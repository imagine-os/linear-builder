---
identifier: "PAP-851"
title: "Build the durable workflow run engine on pg-boss: step executor, suspend and resume, timers, retries, compensation, run log and replay"
project: "workflows"
projectName: "Workflows, Approvals, Forms, Documents & E-Signature"
phase: "P2"
type: "Build"
priority: 4
surfaces: ["Developer"]
milestone: "Forms builder and document templates"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-43", "PAP-303", "PAP-304", "PAP-388", "PAP-556", "PAP-558", "PAP-565", "PAP-847", "PAP-848", "PAP-849"]
blocks: ["PAP-852", "PAP-853", "PAP-861"]
key: "r4/workflows/run-engine"
url: "https://linear.app/paperos/issue/PAP-851/build-the-durable-workflow-run-engine-on-pg-boss-step-executor-suspend"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:51:46.522Z"
model: "claude-opus-5"
effort: "high"
estimate: 5
dueDate: null
cycle: null
---

# PAP-851: Build the durable workflow run engine on pg-boss: step executor, suspend and resume, timers, retries, compensation, run log and replay

**Model / Effort:** Opus 5 (`claude-opus-5`) / high — Build L

**Goal**

Run the model durably: an engine that consumes trigger events from the outbox, executes steps as pg-boss jobs, suspends on human tasks, approvals, waits and signatures without holding a worker, resumes from signals, retries and compensates per the definition, and records a replayable run log, sharing the PAP-388 limits, loop guard and circuit breaker so a runaway workflow cannot exhaust a tenant.

**Scope**

In: `packages/workflows/src/engine/`: `Scheduler` (outbox consumer per trigger topic, PAP-303) creating runs idempotently; `StepRunner` job `workflow.step` with `singletonKey = runId` so one step per run executes at a time; `Resumer` for `signal(runId, stepId, payload)`; `Timer` using pg-boss `startAfter` for waits and timeouts; `Compensator`. Run log: `run_step` attempts with input/output hashes, durations and errors; `workflows.runs.replay(runId, fromStep)` re-executes in a dry-run transaction (PAP-348 pattern) for debugging; live progress via PAP-381 `job.progress`. Guards from PAP-388 reused: daily run limit per tenant, loop guard (a run cannot trigger itself more than 3 deep through events), circuit breaker per definition after 20 consecutive failures with a notification. Admin page `/console/workflows/runs` (grid view) with status filters, timeline drawer, cancel, retry step, and the `X-PaperOS-Impl` shown for shadow runs.

Out: Step kinds beyond `noop`, `wait`, `branch` used for tests (step catalogue). Editor.

**Spec**

* Exactly-once step effects: every step execution carries `Idempotency-Key = <runId>:<stepId>:<attempt>` into the actions it calls (PAP-304); a retried step that already produced its effect returns the stored result
* Suspension writes the resume token and releases the worker within 50 ms; resume is a new job; a suspended run costs nothing while waiting
* Concurrency: 8 step workers per API replica, fair-shared across tenants by pg-boss priority derived from tenant plan and recent usage
* Timeouts: per step `timeout` then `onError`; whole-run `maxDuration` default 90 days for suspended runs, after which the run expires with a notification
* Compensation runs in reverse order of completed steps with their own retry policy; a failed compensation lands in the DLQ (PAP-43) and pings `workflows.manage`

**Interface contract**

Provides: `WorkflowPort` default adapter (`start`, `signal`, `cancel`, `listRuns`, `replay`), `workflow.step` job, run log tables, `/console/workflows/runs` page, `workflow.run.*` events. Consumes: jobs and DLQ (PAP-43), outbox and topics (PAP-303), idempotency (PAP-304), automation guards (PAP-388), dry-run transactions (PAP-348), live progress (PAP-381), grid view (PAP-165). Consumed by: PAP-852, PAP-853, forms (`form` trigger), signatures (`signature.completed` resume), commerce and engagement processes, migration packs.

**Definition of done**

* The three model examples run end to end on the compose stack with a forced worker crash mid-run and recover; 1,000 concurrent suspended runs cost zero worker time (measured)
* k6 scenario (PAP-242): 200 runs per minute with p95 step latency under 500 ms; loop guard and circuit breaker demonstrated
* Every new page has a `page.spec.yaml` (PAP-114) that passes the validator, declared loading, empty, error and denied states, and Gate 3 screenshots at 375, 768, 1024 and 1920 in light and dark themes.
* Linear comment on the issue with the evidence links (PR, gate artefacts, recording or report) and the module docs page updated where the interface changed.

**Test plan**

* Unit: state machine transitions; idempotency key derivation; compensation order; timer scheduling across DST.
* Integration: crash between effect and log write is recovered by the idempotent replay; signal for an unknown token is rejected; run expiry.
* Chaos: kill the worker container during a 20-step run three times; the run completes with exactly one effect per step.
* Isolation: the PAP-34 cross-tenant harness auto-enrols every new table; one negative case per new oRPC procedure proves `NOT_FOUND` on a foreign tenant row.

**Demo**

Start 50 expense-approval runs, kill the worker, restart it, and show every run completing with one ledger posting each; open one run's timeline and replay it in dry-run.

**Edge cases**

* Tenant module disabled while runs are suspended: runs pause with status `blocked:module_disabled` and resume when re-enabled; nothing is lost
* Event storm (10k events in a minute): the scheduler batches run creation and the fair-share priority keeps other tenants' steps flowing
* Module disabled for the tenant (PAP-266): routes return `MODULE_DISABLED` (409), slot fills unmount and the manifest declares the dependency so consumers fail closed rather than half-render.

**Dependencies**

PAP-848 and PAP-849 (hard), PAP-43, PAP-303, PAP-304 (hard), PAP-388 (hard: shared guards), PAP-348, PAP-381 (soft).

**Agent**

Builder: Nova. Reviewer: Sentinel (Edge Case Hunter).

**Size**

L: two sessions; split at the first natural seam if the first session does not reach the integration test.

*Round 4 critique fix (2026-09-18):* resolved 4 round-4 file keys in this description to Linear identifiers: `r4/workflows/approvals-framework` = PAP-849, `r4/workflows/canvas-editor` = PAP-853, `r4/workflows/step-catalogue` = PAP-852, `r4/workflows/workflow-model` = PAP-848.
