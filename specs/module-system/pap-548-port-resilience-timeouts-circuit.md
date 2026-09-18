---
identifier: "PAP-548"
title: "Port resilience: timeouts, circuit breaker and degraded fallbacks for optional ports in kernel resolve wrappers, `MODULE_DEGRADED` telemetry and the chaos toggle for staging"
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
blockedBy: ["PAP-368", "PAP-434", "PAP-502", "PAP-537"]
blocks: []
key: "r4/module-system/port-resilience"
url: "https://linear.app/paperos/issue/PAP-548/port-resilience-timeouts-circuit-breaker-and-degraded-fallbacks-for"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:05.295Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 3
dueDate: "2026-10-01"
cycle: null
---

# PAP-548: Port resilience: timeouts, circuit breaker and degraded fallbacks for optional ports in kernel resolve wrappers, `MODULE_DEGRADED` telemetry and the chaos toggle for staging

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Build M

**Goal**

Plug and play also means unplug safely: when the growth module's social adapter hangs or the forge port times out, the shell and tables must keep working. PAP-438 wraps slot fills in error boundaries; ports have nothing. Backstage and OSGi treat a failing plugin as isolated; this issue gives the kernel the same containment for `optional` dependencies and clear failure for required ones.

**Scope**

In:

* `describePort({ timeoutMs, breaker: { failures, windowMs, halfOpenAfterMs }, fallback })` in the contract; kernel resolve wrapper applying a timeout, a circuit breaker per `(port, impl, tenant)` and, for `requires[].optional=true` consumers, a declared fallback (`unavailable` result object or a memory double) instead of a throw.
* Required ports: on breaker open the call fails fast with `MODULE_UNAVAILABLE` (503 at the gateway with `Retry-After`), never hangs; error copy from `errors.yaml` (PAP-368).
* Telemetry: `module.degraded|recovered` topics (kernel-owned, PAP-436 registry), `paperos_breaker_state` metric (PAP-547), status `degraded` in the health view (PAP-546) and a banner slot in `/settings/modules`.
* Chaos toggle for staging only: flag `platform.chaos` with rules `{ port, mode: latency|error|timeout, rate }` used by the PAP-253 nightly to prove containment; refused when `PUBLIC_ENV=production`.

Out: HTTP client retries inside adapters (each module), rate limiting (PAP-304), UI error boundaries (PAP-438, PAP-368).

**Spec**

* Defaults: timeout 5 s, breaker opens after 5 failures in 30 s, half-open after 15 s; overridable per port, never disabled for `service`-kind providers.
* Breaker state is per process; a tenant-scoped override lets one tenant's failing integration not trip others.
* Fallback doubles are the contract's memory doubles in read-only mode where declared safe; writes are never faked.
* Every breaker transition writes an audit event with the module and reason (PAP-38).

**Interface contract**

Provides: `describePort` resilience options, wrapper behaviour, `MODULE_UNAVAILABLE` and `MODULE_DEGRADED`, topics, chaos flag; consumed by every `Wire <module>` issue (declares budgets), PAP-437 (503 mapping), PAP-253 (nightly chaos run), PAP-85 (edge-case hunter network failures), PAP-446.

Consumes: kernel resolve (PAP-434), error catalogue (PAP-368), event registry (PAP-436, soft), flags (PAP-366, soft), audit (PAP-38).

**Definition of done**

* Sample `bad` impl configured to hang: consumers with `optional` get the fallback within the timeout; required consumers get `MODULE_UNAVAILABLE` fast; breaker opens and recovers (test with fake timers and one compose run).
* Chaos run on staging: shell and tables keep passing Gate 3 while growth ports fail at 50 percent (contact sheet); `docs/platform/resilience.md`; Linear comment.

**Test plan**

* Unit: timeout, breaker state machine, half-open probe, per-tenant isolation, fallback selection, production refusal of chaos.
* E2E: compose stack with the sample `bad` impl and the chaos flag; gateway returns 503 with `Retry-After`.

**Demo**

Reviewer enables `platform.chaos` for `contract-forge.ForgePort` at 100 percent timeout on staging, opens the dashboard: everything renders, the repo widget shows "unavailable", `/healthz` says `forge: degraded`; disables it and the widget recovers within 15 s. Under 2 minutes.

**Edge cases**

* Breaker open during a shadow run: shadow secondary skipped and recorded as `skipped`, never counted as a diff.
* Port with streaming results: timeout applies to first byte only.
* Fallback double returns stale-looking data: results carry `degraded: true` so UI can badge them (PAP-234 `IntegrationUnavailable`).

**Dependencies**

Hard: PAP-434, PAP-368. Soft: PAP-436, PAP-366, PAP-38, PAP-437, PAP-547, PAP-546.

**Agent**

Builder: Forge (Platform Engineer). Reviewer: Sentinel (Edge Case Hunter).

**Size**

M: one session.

*Round 4 critique fix (2026-09-18):* resolved 2 round-4 file keys in this description to Linear identifiers: `r4/module-system/kernel-otel` = PAP-547, `r4/module-system/lifecycle-and-health` = PAP-546.
