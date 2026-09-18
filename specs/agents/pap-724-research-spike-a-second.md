---
identifier: "PAP-724"
title: "Research spike: a second `AgentRuntimePort` adapter (OpenHands or a hosted sandbox) behind `module.agents.impl`, scored against the conformance suite, with an ADR on when a second runtime is worth it"
project: "agents"
projectName: "Agent Characters & Orgs"
phase: "P2"
type: "Research"
priority: 4
surfaces: ["Agent"]
milestone: "Agent org visible in app"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-280", "PAP-469"]
blocks: []
key: "r4/agents/second-runtime-adapter-spike"
url: "https://linear.app/paperos/issue/PAP-724/research-spike-a-second-agentruntimeport-adapter-openhands-or-a-hosted"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:20:20.335Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 2
dueDate: null
cycle: null
---

# PAP-724: Research spike: a second `AgentRuntimePort` adapter (OpenHands or a hosted sandbox) behind `module.agents.impl`, scored against the conformance suite, with an ADR on when a second runtime is worth it

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Research S

**Goal**

Deferred to v0.2 by round 4 (not claimable before 2026-10-01; NJ-14 can reinstate). The module contract says a different harness, a hosted sandbox or a second model vendor is just another `AgentRuntimePort` adapter behind `module.agents.impl` that must pass the conformance suite. Nobody has tried. A time-boxed spike builds the thinnest possible second adapter, runs the suite and PAP-472's flag flip against it, and writes the ADR that says whether and when a second runtime is worth having.

**Scope**

* In: `packages/agents-runtime-openhands/` (or a hosted sandbox adapter) implementing `spawn`, `heartbeat`, `kill`, `status` from `@paperos/contract-agents` with the PAP-106 bundle translated to the runtime's permission model, conformance run (`paperos module conformance agents --impl sandbox,openhands`), a shadow-run of one golden task through both, `docs/adr/00xx-second-agent-runtime.md`, time box one session and $30.
* Out: production use, a second model vendor's prompt compatibility, replacing Claude Code as the default.

**Spec**

* Adapter maps `spawn(spec)` to the runtime's session API with the worktree mounted and the deny list translated where possible; unsupported capabilities reported as `unsupported` in `conformance.json`, never faked.
* Run the PAP-469 suite against both adapters; record pass, fail, pending, unsupported per case id; flip `module.agents.impl` for a staging tenant to the spike adapter for one golden task and back (PAP-472 mechanism).
* ADR criteria: conformance coverage, cost per task, isolation guarantees versus PAP-280, prompt-injection surface (PAP-299 hooks availability), operational burden; recommendation with a trigger condition (vendor outage, price change, capability gap).
* Everything is behind the flag and off by default; the package is marked `experimental`.

**Interface contract**

* Provides: the spike adapter package, `conformance.json` for both implementations, the ADR.
* Consumes: PAP-469 suite and case ids, PAP-472 flag mechanism, PAP-280 sandbox as the reference, PAP-106 bundle semantics, PAP-130 ADR template.

**Definition of done**

* Conformance table for both adapters attached; one golden task shadow-run recorded; ADR merged with a clear recommendation and trigger conditions; changelog.

**Test plan**

* Unit: none beyond the conformance suite.
* E2E: flag flip on staging for one task.

**Demo**

Run `paperos module conformance agents --impl sandbox,openhands` and read the two columns; open the ADR's recommendation. Under one minute.

**Edge cases**

* Runtime cannot mount a worktree: `spawn` reported `unsupported`; the ADR notes it as disqualifying for builders, possibly acceptable for reviewers.
* Time box exceeded: stop, record partial results, recommend `do not pursue now`.
* Runtime needs credentials the broker cannot inject: refused; documented.

**Dependencies**

Hard: PAP-469, PAP-280. Soft: PAP-472, PAP-106, PAP-299, PAP-130.

**Agent**

Builder: Scout (Library Evaluator) with Atlas. Reviewer: Sentinel (Security Auditor).

**Size**

S: half a session.
