---
identifier: "PAP-547"
title: "Kernel instrumentation: one OpenTelemetry span per port call tagged with module, implementation and contract version, per-module latency and error dashboards, and cost attribution hooks"
project: "module-system"
projectName: "Module System & Swap Tooling"
phase: "P1"
type: "Build"
priority: 2
surfaces: ["Developer"]
milestone: "Shell swap drill passes"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-40", "PAP-434", "PAP-537"]
blocks: []
key: "r4/module-system/kernel-otel"
url: "https://linear.app/paperos/issue/PAP-547/kernel-instrumentation-one-opentelemetry-span-per-port-call-tagged"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:20:52.327Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 2
dueDate: "2026-10-01"
cycle: null
---

# PAP-547: Kernel instrumentation: one OpenTelemetry span per port call tagged with module, implementation and contract version, per-module latency and error dashboards, and cost attribution hooks

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Build S

**Goal**

PAP-40 traces HTTP and SQL; the kernel sits between them and knows which module and which implementation served each call. Without kernel spans, a shadow run or canary (PAP-435) cannot be compared on latency per port, and a slow module hides inside a slow request. This is the observability the swap playbook's step 4 performance gate assumes.

**Scope**

In:

* `packages/kernel/otel.ts`: a resolve wrapper that starts a span `port <contract>.<port>.<method>` with attributes `paperos.module`, `paperos.impl`, `paperos.contract_version`, `paperos.tenant_id` (hashed), `paperos.shadow` and records exceptions; opt-out per port for hot paths via `describePort({ trace: "sampled" })`.
* Metrics: histogram `paperos_port_latency_ms{module, impl, port}` and counter `paperos_port_errors_total`; exported through the PAP-40 collector.
* Dashboards `ops/observability/modules.json`: per-module p50 and p95 latency, error rate, calls per minute, impl split during a canary; alert when a non-default impl has 2x the p95 of default for 10 minutes (feeds the PAP-442 shadow gate).
* Cost hook: `kernel.on("port:call", cb)` used by PAP-391 usage metering to attribute API calls to modules.

Out: the collector and base dashboards (PAP-40), HTTP and SQL spans (PAP-40), business metrics.

**Spec**

* Overhead under 20 microseconds per call when sampled out, under 0.1 ms when recorded (benchmark in PAP-434 suite).
* Sampling follows the PAP-40 head sampler; shadow calls are always recorded at 1 percent (PAP-435 sample) with `paperos.shadow=true`.
* No payloads or identifiers in attributes; tenant id hashed with the PAP-40 salt.

**Interface contract**

Provides: resolve wrapper, metrics, dashboard and alert, `port:call` hook; consumed by PAP-435 (latency columns in `swap_shadow_diff`), PAP-442 (step 4 gate), PAP-242 (per-procedure budgets now per module), PAP-391, PAP-446 drill numbers.

Consumes: kernel resolve path (PAP-434), collector, Grafana and salt (PAP-40), shadow binding (PAP-435, soft).

**Definition of done**

* A request through the gateway shows nested port spans with module and impl attributes in Tempo (screenshot); dashboard renders for the compose stack under load from the PAP-242 k6 smoke.
* Overhead benchmark green; alert rule tested with a slowed `bad` sample impl; `docs/platform/observability.md` modules section; Linear comment.

**Test plan**

* Unit: attribute set per call; opt-out and sampling; exception recording; hook invocation.
* E2E: compose stack: k6 smoke then Grafana query asserts per-module histograms exist.

**Demo**

Reviewer opens Tempo for one `views.list` request and expands `port @paperos/contract-tables.ViewQueryPort.query` with `impl=compiler-v2`, then the modules dashboard showing both impls side by side. Under a minute.

**Edge cases**

* Port resolved inside a Yjs callback (system scope): span parented to the system trace, tenant attribute absent.
* Recursive port calls (a port calling another): nested spans, depth capped at 10 with a warning.
* Collector down: spans dropped, no latency added (PAP-40 exporter behaviour).

**Dependencies**

Hard: PAP-434, PAP-40. Soft: PAP-435, PAP-242, PAP-391.

**Agent**

Builder: Forge (Platform Engineer). Reviewer: Sentinel (Code Reviewer).

**Size**

S: half a session.
